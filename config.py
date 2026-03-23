"""
Configuration for the JSE Market Monitor web app.
Edit WATCHLIST to add/remove JSE tickers.
"""

from __future__ import annotations

# Display Name -> Yahoo Finance symbol
# JSE stocks use the .JO suffix on Yahoo Finance
WATCHLIST: dict[str, str] = {
    # ── JSE Top 40 / Blue Chips ──────────────────────────────────────────
    "Naspers": "NPN.JO",
    "Prosus": "PRX.JO",
    "Anglo American": "AGL.JO",
    "BHP Group": "BHG.JO",
    "Richemont": "CFR.JO",
    "FirstRand": "FSR.JO",
    "Standard Bank": "SBK.JO",
    "ABSA Group": "ABG.JO",
    "Capitec": "CPI.JO",
    "MTN Group": "MTN.JO",
    "Vodacom": "VOD.JO",
    "Shoprite": "SHP.JO",
    "Woolworths": "WHL.JO",
    "Sasol": "SOL.JO",
    "Gold Fields": "GFI.JO",
    "AngloGold Ashanti": "ANG.JO",
    "Sibanye Stillwater": "SSW.JO",
    "Discovery": "DSY.JO",
    "Nedbank": "NED.JO",
    "Clicks Group": "CLS.JO",
    # ── Indices ──────────────────────────────────────────────────────────
    "JSE Top 40": "^JN0U.JO",
    "JSE All Share": "^J203.JO",
    # ── Currency ─────────────────────────────────────────────────────────
    "USD/ZAR": "ZAR=X",
}

# Group tickers for confluence analysis
CONFLUENCE_GROUPS: dict[str, list[str]] = {
    "Banking": ["FSR.JO", "SBK.JO", "ABG.JO", "CPI.JO", "NED.JO"],
    "Mining & Resources": ["AGL.JO", "BHG.JO", "GFI.JO", "ANG.JO", "SSW.JO", "SOL.JO"],
    "Tech & Media": ["NPN.JO", "PRX.JO", "MTN.JO", "VOD.JO"],
    "Retail & Consumer": ["SHP.JO", "WHL.JO", "CLS.JO", "DSY.JO"],
    "Luxury": ["CFR.JO"],
    "Indices": ["^JN0U.JO", "^J203.JO"],
}

# How often to re-scan (seconds)
SCAN_INTERVAL_SECONDS = 300

# Historical data period for indicators
DATA_PERIOD = "6mo"

# Signal thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
