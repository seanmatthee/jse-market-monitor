"""
Signal generation engine for JSE stocks.

Computes technical indicators on OHLCV data and produces a list of
scored signals per ticker. Each signal votes bullish (+1), bearish (-1),
or neutral (0). An aggregate score and trade bias are derived.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import time

import numpy as np
import pandas as pd
import yfinance as yf

from config import (
    BATCH_SIZE,
    DATA_PERIOD,
    RSI_OVERBOUGHT,
    RSI_OVERSOLD,
)


# ── Data structures ──────────────────────────────────────────────────────────

@dataclass
class Signal:
    """A single scored indicator signal."""
    name: str
    vote: int           # +1 bullish, -1 bearish, 0 neutral
    detail: str

    @property
    def label(self) -> str:
        if self.vote > 0:
            return "BULLISH"
        if self.vote < 0:
            return "BEARISH"
        return "NEUTRAL"


@dataclass
class TickerAnalysis:
    """Full analysis result for one ticker."""
    name: str
    symbol: str
    price: float
    daily_change_pct: float
    signals: list[Signal] = field(default_factory=list)
    bullish: int = 0
    bearish: int = 0
    neutral: int = 0
    score: int = 0
    score_pct: float = 0.0
    bias: str = "NEUTRAL"
    rsi: float = 0.0
    macd: float = 0.0
    macd_signal: float = 0.0
    sma_50: float = 0.0
    sma_200: float = 0.0
    bb_upper: float = 0.0
    bb_lower: float = 0.0
    atr: float = 0.0
    suggested_entry: str = ""
    suggested_stop: str = ""
    suggested_target: str = ""
    price_history: list[float] = field(default_factory=list)
    error: str = ""


# ── Data fetching ────────────────────────────────────────────────────────────

def fetch_data(symbol: str, retries: int = 3) -> pd.DataFrame | None:
    """Download historical OHLCV data with retry logic for rate limits."""
    for attempt in range(retries):
        try:
            df = yf.download(symbol, period=DATA_PERIOD, progress=False)
            if df.empty:
                if attempt < retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
        except Exception:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                return None
    return None


# ── Indicator calculations ───────────────────────────────────────────────────

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add all technical indicator columns to the dataframe."""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # Moving averages
    df["SMA_20"] = close.rolling(20).mean()
    df["SMA_50"] = close.rolling(50).mean()
    df["SMA_200"] = close.rolling(200).mean() if len(df) >= 200 else np.nan
    df["EMA_9"] = close.ewm(span=9, adjust=False).mean()
    df["EMA_21"] = close.ewm(span=21, adjust=False).mean()

    # RSI (14)
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    # Bollinger Bands (20, 2)
    bb_std = close.rolling(20).std()
    df["BB_Upper"] = df["SMA_20"] + 2 * bb_std
    df["BB_Lower"] = df["SMA_20"] - 2 * bb_std
    df["BB_Pct"] = (close - df["BB_Lower"]) / (df["BB_Upper"] - df["BB_Lower"])

    # ATR (14) — for stop-loss / target suggestions
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    # Volume averages
    df["Vol_20"] = volume.rolling(20).mean()
    df["Vol_50"] = volume.rolling(50).mean()

    # Rate of change (20-day)
    df["ROC_20"] = close.pct_change(20) * 100

    return df


# ── Signal scoring ───────────────────────────────────────────────────────────

def score_signals(df: pd.DataFrame) -> list[Signal]:
    """Evaluate the latest data row and return scored signals."""
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    signals: list[Signal] = []

    close = latest["Close"]

    # 1. EMA crossover (9/21) — fast trend direction
    ema9 = latest["EMA_9"]
    ema21 = latest["EMA_21"]
    if ema9 > ema21:
        signals.append(Signal("EMA 9/21", +1, f"EMA-9 ({ema9:,.1f}) above EMA-21 ({ema21:,.1f})"))
    else:
        signals.append(Signal("EMA 9/21", -1, f"EMA-9 ({ema9:,.1f}) below EMA-21 ({ema21:,.1f})"))

    # 2. Price vs SMA-50
    sma50 = latest["SMA_50"]
    if not np.isnan(sma50):
        pct = (close - sma50) / sma50 * 100
        vote = +1 if close > sma50 else -1
        signals.append(Signal("Price vs SMA-50", vote,
            f"Price {pct:+.1f}% {'above' if vote > 0 else 'below'} SMA-50 ({sma50:,.1f})"))

    # 3. Price vs SMA-200
    sma200 = latest.get("SMA_200", np.nan)
    if not np.isnan(sma200):
        pct = (close - sma200) / sma200 * 100
        vote = +1 if close > sma200 else -1
        signals.append(Signal("Price vs SMA-200", vote,
            f"Price {pct:+.1f}% {'above' if vote > 0 else 'below'} SMA-200 ({sma200:,.1f})"))

    # 4. RSI
    rsi = latest["RSI"]
    if rsi > RSI_OVERBOUGHT:
        signals.append(Signal("RSI (14)", -1, f"RSI {rsi:.1f} — overbought (>{RSI_OVERBOUGHT})"))
    elif rsi < RSI_OVERSOLD:
        signals.append(Signal("RSI (14)", +1, f"RSI {rsi:.1f} — oversold (<{RSI_OVERSOLD})"))
    elif rsi >= 50:
        signals.append(Signal("RSI (14)", +1, f"RSI {rsi:.1f} — bullish momentum"))
    else:
        signals.append(Signal("RSI (14)", -1, f"RSI {rsi:.1f} — bearish momentum"))

    # 5. MACD crossover
    macd = latest["MACD"]
    macd_sig = latest["MACD_Signal"]
    if macd > macd_sig:
        signals.append(Signal("MACD", +1, f"MACD ({macd:,.1f}) above signal ({macd_sig:,.1f})"))
    else:
        signals.append(Signal("MACD", -1, f"MACD ({macd:,.1f}) below signal ({macd_sig:,.1f})"))

    # 6. MACD histogram direction
    hist_now = latest["MACD_Hist"]
    hist_prev = prev["MACD_Hist"]
    if hist_now > hist_prev:
        signals.append(Signal("MACD Histogram", +1, f"Expanding ({hist_prev:,.1f} -> {hist_now:,.1f})"))
    else:
        signals.append(Signal("MACD Histogram", -1, f"Contracting ({hist_prev:,.1f} -> {hist_now:,.1f})"))

    # 7. Bollinger Band position
    bb_pct = latest["BB_Pct"]
    if bb_pct > 1.0:
        signals.append(Signal("Bollinger Bands", -1, f"Above upper band — overextended"))
    elif bb_pct < 0.0:
        signals.append(Signal("Bollinger Bands", +1, f"Below lower band — oversold"))
    elif bb_pct > 0.5:
        signals.append(Signal("Bollinger Bands", +1, f"Upper half ({bb_pct:.0%})"))
    else:
        signals.append(Signal("Bollinger Bands", -1, f"Lower half ({bb_pct:.0%})"))

    # 8. Volume confirmation
    vol20 = latest["Vol_20"]
    vol50 = latest["Vol_50"]
    roc = latest["ROC_20"]
    if vol50 > 0:
        vol_ratio = vol20 / vol50
        if vol_ratio > 1.1 and roc > 0:
            signals.append(Signal("Volume", +1, f"Rising on expanding volume ({vol_ratio:.1f}x)"))
        elif vol_ratio > 1.1 and roc < 0:
            signals.append(Signal("Volume", -1, f"Falling on expanding volume ({vol_ratio:.1f}x)"))
        else:
            signals.append(Signal("Volume", 0, f"Volume near average ({vol_ratio:.1f}x)"))
    else:
        signals.append(Signal("Volume", 0, "Volume data unavailable"))

    # 9. Momentum (ROC-20)
    if roc > 3:
        signals.append(Signal("Momentum", +1, f"Strong upward: {roc:+.1f}%"))
    elif roc > 0:
        signals.append(Signal("Momentum", +1, f"Positive: {roc:+.1f}%"))
    elif roc > -3:
        signals.append(Signal("Momentum", -1, f"Negative: {roc:+.1f}%"))
    else:
        signals.append(Signal("Momentum", -1, f"Strong downward: {roc:+.1f}%"))

    # 10. EMA-9 slope (trend acceleration)
    ema9_now = latest["EMA_9"]
    ema9_prev = prev["EMA_9"]
    if ema9_now > ema9_prev:
        signals.append(Signal("Trend Accel.", +1, "EMA-9 rising"))
    else:
        signals.append(Signal("Trend Accel.", -1, "EMA-9 falling"))

    return signals


# ── Trade suggestion logic ───────────────────────────────────────────────────

def _suggest_trade(bias: str, close: float, atr: float) -> tuple[str, str, str]:
    """Generate entry / stop / target suggestions based on bias and ATR."""
    if np.isnan(atr) or atr <= 0:
        return ("—", "—", "—")

    if bias in ("BULLISH", "STRONGLY BULLISH"):
        entry = f"R{close:,.2f} (current)"
        stop = f"R{close - 1.5 * atr:,.2f} (1.5 ATR below)"
        target = f"R{close + 3.0 * atr:,.2f} (3 ATR above — 1:2 R:R)"
        return (entry, stop, target)

    if bias in ("BEARISH", "STRONGLY BEARISH"):
        entry = f"R{close:,.2f} (current)"
        stop = f"R{close + 1.5 * atr:,.2f} (1.5 ATR above)"
        target = f"R{close - 3.0 * atr:,.2f} (3 ATR below — 1:2 R:R)"
        return (entry, stop, target)

    return ("No clear setup", "—", "—")


# ── Shared analysis logic (works on a pre-fetched DataFrame) ─────────────────

def _build_result(name: str, symbol: str, df: pd.DataFrame) -> TickerAnalysis:
    """Compute indicators, score signals, and build a TickerAnalysis from a DataFrame."""
    result = TickerAnalysis(name=name, symbol=symbol, price=0.0, daily_change_pct=0.0)

    df = compute_indicators(df)
    latest = df.iloc[-1]
    prev_close = df.iloc[-2]["Close"]

    result.price = latest["Close"]
    result.daily_change_pct = (result.price - prev_close) / prev_close * 100
    result.rsi = latest["RSI"]
    result.macd = latest["MACD"]
    result.macd_signal = latest["MACD_Signal"]
    result.sma_50 = latest["SMA_50"]
    result.sma_200 = latest.get("SMA_200", 0.0)
    result.bb_upper = latest["BB_Upper"]
    result.bb_lower = latest["BB_Lower"]
    result.atr = latest["ATR"]

    # Last 30 closing prices for sparkline charts
    result.price_history = df["Close"].tail(30).tolist()

    # Score signals
    signals = score_signals(df)
    result.signals = signals

    for s in signals:
        if s.vote > 0:
            result.bullish += 1
        elif s.vote < 0:
            result.bearish += 1
        else:
            result.neutral += 1

    total = len(signals)
    result.score = result.bullish - result.bearish
    result.score_pct = result.score / total * 100 if total > 0 else 0

    if result.score_pct >= 60:
        result.bias = "STRONGLY BULLISH"
    elif result.score_pct >= 20:
        result.bias = "BULLISH"
    elif result.score_pct > -20:
        result.bias = "NEUTRAL"
    elif result.score_pct > -60:
        result.bias = "BEARISH"
    else:
        result.bias = "STRONGLY BEARISH"

    entry, stop, target = _suggest_trade(result.bias, result.price, result.atr)
    result.suggested_entry = entry
    result.suggested_stop = stop
    result.suggested_target = target

    return result


# ── Single-ticker analysis (fetches its own data) ───────────────────────────

def analyse_ticker(name: str, symbol: str) -> TickerAnalysis:
    """Run the full analysis pipeline for one ticker."""
    result = TickerAnalysis(name=name, symbol=symbol, price=0.0, daily_change_pct=0.0)

    df = fetch_data(symbol)
    if df is None or len(df) < 30:
        result.error = "Could not fetch sufficient data"
        return result

    return _build_result(name, symbol, df)


# ── Batch-optimized helper (uses pre-fetched DataFrame) ─────────────────────

def _analyse_from_df(name: str, symbol: str, df: pd.DataFrame) -> TickerAnalysis:
    """Run the full analysis pipeline using an already-fetched DataFrame."""
    return _build_result(name, symbol, df)


# ── Batch analysis of entire watchlist ───────────────────────────────────────

def analyse_all(watchlist: dict[str, str]) -> list[TickerAnalysis]:
    """Analyse every ticker in the watchlist using batch downloads for speed."""
    results: list[TickerAnalysis] = []
    items = list(watchlist.items())

    # Process in batches
    for batch_start in range(0, len(items), BATCH_SIZE):
        batch = items[batch_start:batch_start + BATCH_SIZE]
        symbols = [sym for _, sym in batch]

        if batch_start > 0:
            time.sleep(2)  # Rate limit between batches

        # Batch download
        try:
            batch_data = yf.download(symbols, period=DATA_PERIOD, progress=False, group_by="ticker")
        except Exception:
            batch_data = None

        for name, symbol in batch:
            try:
                if batch_data is not None and len(symbols) > 1:
                    if symbol in batch_data.columns.get_level_values(0):
                        df = batch_data[symbol].dropna(how="all")
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = df.columns.get_level_values(0)
                    else:
                        df = None
                elif batch_data is not None and len(symbols) == 1:
                    df = batch_data
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                else:
                    df = None

                if df is None or df.empty or len(df) < 30:
                    # Fallback to single fetch
                    result = analyse_ticker(name, symbol)
                else:
                    result = _analyse_from_df(name, symbol, df)

                results.append(result)
            except Exception:
                results.append(analyse_ticker(name, symbol))

    return results
