"""
JSE Market Monitor — Flask web app with background scanning.

This is the single entry point for the deployed web application.
A background scheduler re-scans the watchlist on an interval and
stores the latest results in memory. The dashboard reads from that
cache on every page load.
"""

from __future__ import annotations

import os
import threading
import urllib.request
from dataclasses import dataclass
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template

from config import SCAN_INTERVAL_SECONDS, WATCHLIST, CONFLUENCE_GROUPS
from signals import TickerAnalysis, analyse_all

# ── Shared state ─────────────────────────────────────────────────────────────

@dataclass
class ConfluenceGroup:
    """Order flow confluence for a group of related instruments."""
    name: str
    bullish_count: int
    bearish_count: int
    neutral_count: int
    total: int
    bias: str
    strength: float          # -100 to +100
    tickers: list[str]       # ticker names in this group
    volume_rising: int       # how many have expanding volume
    volume_total: int


@dataclass
class Confluence:
    """Overall market confluence across all groups."""
    groups: list[ConfluenceGroup]
    overall_bullish: int
    overall_bearish: int
    overall_neutral: int
    overall_total: int
    overall_bias: str
    overall_strength: float
    agreement_pct: float     # how aligned instruments are (0-100)


_lock = threading.Lock()
_latest_results: list[TickerAnalysis] = []
_latest_confluence: Confluence | None = None
_last_scan_time: str = "scanning..."


def _compute_confluence(results: list[TickerAnalysis]) -> Confluence:
    """Compute order flow confluence across instrument groups."""
    by_symbol = {r.symbol: r for r in results if not r.error}
    groups: list[ConfluenceGroup] = []

    overall_bull = 0
    overall_bear = 0
    overall_neut = 0

    for group_name, symbols in CONFLUENCE_GROUPS.items():
        bull = bear = neut = vol_rising = vol_total = 0
        ticker_names: list[str] = []

        for sym in symbols:
            a = by_symbol.get(sym)
            if not a:
                continue
            ticker_names.append(a.name)
            if "BULLISH" in a.bias:
                bull += 1
            elif "BEARISH" in a.bias:
                bear += 1
            else:
                neut += 1

            # Check volume trend from signals
            for s in a.signals:
                if s.name == "Volume":
                    vol_total += 1
                    if s.vote > 0:
                        vol_rising += 1
                    break

        total = bull + bear + neut
        net = bull - bear
        strength = (net / total * 100) if total > 0 else 0

        if strength >= 50:
            bias = "STRONGLY BULLISH"
        elif strength > 0:
            bias = "BULLISH"
        elif strength == 0:
            bias = "NEUTRAL"
        elif strength > -50:
            bias = "BEARISH"
        else:
            bias = "STRONGLY BEARISH"

        groups.append(ConfluenceGroup(
            name=group_name, bullish_count=bull, bearish_count=bear,
            neutral_count=neut, total=total, bias=bias, strength=strength,
            tickers=ticker_names, volume_rising=vol_rising, volume_total=vol_total,
        ))

        overall_bull += bull
        overall_bear += bear
        overall_neut += neut

    overall_total = overall_bull + overall_bear + overall_neut
    overall_net = overall_bull - overall_bear
    overall_strength = (overall_net / overall_total * 100) if overall_total > 0 else 0

    if overall_strength >= 50:
        overall_bias = "STRONGLY BULLISH"
    elif overall_strength > 0:
        overall_bias = "BULLISH"
    elif overall_strength == 0:
        overall_bias = "NEUTRAL"
    elif overall_strength > -50:
        overall_bias = "BEARISH"
    else:
        overall_bias = "STRONGLY BEARISH"

    # Agreement: what % of instruments agree with the majority direction
    majority = max(overall_bull, overall_bear, overall_neut)
    agreement = (majority / overall_total * 100) if overall_total > 0 else 0

    return Confluence(
        groups=groups,
        overall_bullish=overall_bull, overall_bearish=overall_bear,
        overall_neutral=overall_neut, overall_total=overall_total,
        overall_bias=overall_bias, overall_strength=overall_strength,
        agreement_pct=agreement,
    )


def _run_scan() -> None:
    """Execute one scan cycle and update the shared state."""
    global _latest_results, _latest_confluence, _last_scan_time
    results = analyse_all(WATCHLIST)
    confluence = _compute_confluence(results)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _lock:
        _latest_results = results
        _latest_confluence = confluence
        _last_scan_time = now
    print(f"[Scanner] Scan complete at {now} — {len(results)} tickers | Confluence: {confluence.overall_bias}")


def _get_latest() -> tuple[list[TickerAnalysis], Confluence | None, str]:
    with _lock:
        return list(_latest_results), _latest_confluence, _last_scan_time


# ── Flask app ────────────────────────────────────────────────────────────────

app = Flask(__name__)


@app.route("/health")
def health() -> str:
    """Health check endpoint for keep-alive pings."""
    return "ok"


@app.route("/")
def index() -> str:
    analyses, confluence, last_scan = _get_latest()
    return render_template(
        "dashboard.html",
        analyses=analyses,
        confluence=confluence,
        last_scan=last_scan,
        refresh_interval=60,
    )


# ── Keep-alive ping (prevents Render free tier from sleeping) ────────────────

def _keep_alive() -> None:
    """Ping our own URL to prevent the free instance from spinning down."""
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if url:
        try:
            urllib.request.urlopen(url, timeout=10)
            print(f"[Keep-alive] Pinged {url}")
        except Exception:
            pass


# ── Scheduler ────────────────────────────────────────────────────────────────

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(_run_scan, "interval", seconds=SCAN_INTERVAL_SECONDS, id="scan")
scheduler.add_job(_keep_alive, "interval", minutes=10, id="keepalive")
scheduler.start()

# Run first scan in a background thread so gunicorn boots immediately
threading.Thread(target=_run_scan, daemon=True).start()


# ── Local dev entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5501))
    app.run(host="0.0.0.0", port=port, debug=False)
