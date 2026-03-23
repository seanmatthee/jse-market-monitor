"""
Configuration for the JSE Market Monitor web app.
Edit WATCHLIST to add/remove JSE tickers.
All JSE stocks use the .JO suffix on Yahoo Finance.
"""

from __future__ import annotations

# Display Name -> Yahoo Finance symbol
# JSE stocks use the .JO suffix on Yahoo Finance
WATCHLIST: dict[str, str] = {
    # ── Banking ─────────────────────────────────────────────────────────────
    "FirstRand": "FSR.JO",
    "Standard Bank": "SBK.JO",
    "ABSA Group": "ABG.JO",
    "Capitec": "CPI.JO",
    "Nedbank": "NED.JO",
    "Investec": "INL.JO",
    "Discovery": "DSY.JO",
    # ── Insurance ───────────────────────────────────────────────────────────
    "Sanlam": "SLM.JO",
    "Old Mutual": "OMU.JO",
    "Momentum Metropolitan": "MTM.JO",
    "Santam": "SNT.JO",
    "OUTsurance": "OUT.JO",
    "Liberty Holdings": "LBH.JO",
    # ── Mining & Resources ──────────────────────────────────────────────────
    "Anglo American": "AGL.JO",
    "BHP Group": "BHG.JO",
    "Gold Fields": "GFI.JO",
    "AngloGold Ashanti": "ANG.JO",
    "Sibanye Stillwater": "SSW.JO",
    "Impala Platinum": "IMP.JO",
    "Northam Platinum": "NHM.JO",
    "Exxaro": "EXX.JO",
    "Kumba Iron Ore": "KIO.JO",
    "African Rainbow Minerals": "ARI.JO",
    "Harmony Gold": "HAR.JO",
    "Pan African Resources": "PAN.JO",
    "Thungela Resources": "TGA.JO",
    "Royal Bafokeng Platinum": "RBP.JO",
    "South32": "S32.JO",
    "Glencore": "GLN.JO",
    # ── Energy ──────────────────────────────────────────────────────────────
    "Sasol": "SOL.JO",
    "TotalEnergies SA": "TTE.JO",
    # ── Tech & Media ────────────────────────────────────────────────────────
    "Naspers": "NPN.JO",
    "Prosus": "PRX.JO",
    "MTN Group": "MTN.JO",
    "Vodacom": "VOD.JO",
    "Telkom": "TKG.JO",
    "MultiChoice": "MCG.JO",
    "Datatec": "DTC.JO",
    "Altron": "AEL.JO",
    "Karooooo": "KRO.JO",
    "Bytes Technology": "BYI.JO",
    # ── Retail & Consumer ───────────────────────────────────────────────────
    "Shoprite": "SHP.JO",
    "Woolworths": "WHL.JO",
    "Clicks Group": "CLS.JO",
    "Pick n Pay": "PIK.JO",
    "Spar Group": "SPP.JO",
    "Mr Price": "MRP.JO",
    "Pepkor": "PPH.JO",
    "Truworths": "TRU.JO",
    "TFG (Foschini)": "TFG.JO",
    "Massmart": "MSM.JO",
    "Dis-Chem": "DCP.JO",
    "Tiger Brands": "TBS.JO",
    "AVI": "AVI.JO",
    "Pioneer Foods (PepsiCo)": "PFG.JO",
    "RCL Foods": "RCL.JO",
    "Astral Foods": "ARL.JO",
    "Oceana Group": "OCE.JO",
    "Famous Brands": "FBR.JO",
    "Bid Corp": "BID.JO",
    "Bidvest": "BVT.JO",
    # ── Property / REITs ────────────────────────────────────────────────────
    "Growthpoint": "GRT.JO",
    "Redefine": "RDF.JO",
    "Resilient REIT": "RES.JO",
    "NEPI Rockcastle": "NRP.JO",
    "Fortress REIT": "FFB.JO",
    "Hyprop": "HYP.JO",
    "Vukile": "VKE.JO",
    "Attacq": "ATT.JO",
    "SA Corporate": "SAC.JO",
    "Emira": "EMI.JO",
    "Sirius Real Estate": "SRE.JO",
    "Lighthouse Properties": "LTE.JO",
    # ── Industrials ─────────────────────────────────────────────────────────
    "Barloworld": "BAW.JO",
    "Reunert": "RLO.JO",
    "Nampak": "NPK.JO",
    "PPC": "PPC.JO",
    "Mpact": "MPT.JO",
    "Afrimat": "AFT.JO",
    "WBHO": "WBO.JO",
    "Aveng": "AEG.JO",
    "Murray & Roberts": "MUR.JO",
    "Grindrod": "GND.JO",
    "Trencor": "TRE.JO",
    "Super Group": "SPG.JO",
    "Motus Holdings": "MTH.JO",
    "Combined Motor": "CMH.JO",
    "Imperial Logistics": "IPL.JO",
    "KAP Industrial": "KAP.JO",
    "Hudaco": "HDC.JO",
    "Italtile": "ITE.JO",
    # ── Luxury ──────────────────────────────────────────────────────────────
    "Richemont": "CFR.JO",
    # ── Healthcare ──────────────────────────────────────────────────────────
    "Aspen Pharmacare": "APN.JO",
    "Mediclinic": "MEI.JO",
    "Netcare": "NTC.JO",
    "Life Healthcare": "LHC.JO",
    # ── Financial Services ──────────────────────────────────────────────────
    "PSG Group": "PSG.JO",
    "Coronation Fund": "CML.JO",
    "Ninety One": "N91.JO",
    "Transaction Capital": "TCP.JO",
    "Alexander Forbes": "AFH.JO",
    "Rand Merchant Investment": "RMI.JO",
    # ── Indices ──────────────────────────────────────────────────────────────
    "JSE Top 40": "^JN0U.JO",
    "JSE All Share": "^J203.JO",
    # ── Currency ─────────────────────────────────────────────────────────────
    "USD/ZAR": "ZAR=X",
    "EUR/ZAR": "EURZAR=X",
    "GBP/ZAR": "GBPZAR=X",
}

# Group tickers for confluence analysis (sector-level signals)
CONFLUENCE_GROUPS: dict[str, list[str]] = {
    "Banking": [
        "FSR.JO", "SBK.JO", "ABG.JO", "CPI.JO", "NED.JO", "INL.JO",
        "DSY.JO",
    ],
    "Insurance": [
        "SLM.JO", "OMU.JO", "MTM.JO", "SNT.JO", "OUT.JO", "LBH.JO",
    ],
    "Mining & Resources": [
        "AGL.JO", "BHG.JO", "GFI.JO", "ANG.JO", "SSW.JO", "IMP.JO",
        "NHM.JO", "EXX.JO", "KIO.JO", "ARI.JO", "HAR.JO", "PAN.JO",
        "TGA.JO", "RBP.JO", "S32.JO", "GLN.JO",
    ],
    "Energy": [
        "SOL.JO", "TTE.JO",
    ],
    "Tech & Media": [
        "NPN.JO", "PRX.JO", "MTN.JO", "VOD.JO", "TKG.JO", "MCG.JO",
        "DTC.JO", "AEL.JO", "KRO.JO", "BYI.JO",
    ],
    "Retail & Consumer": [
        "SHP.JO", "WHL.JO", "CLS.JO", "PIK.JO", "SPP.JO", "MRP.JO",
        "PPH.JO", "TRU.JO", "TFG.JO", "MSM.JO", "DCP.JO", "TBS.JO",
        "AVI.JO", "PFG.JO", "RCL.JO", "ARL.JO", "OCE.JO", "FBR.JO",
        "BID.JO", "BVT.JO",
    ],
    "Property / REITs": [
        "GRT.JO", "RDF.JO", "RES.JO", "NRP.JO", "FFB.JO", "HYP.JO",
        "VKE.JO", "ATT.JO", "SAC.JO", "EMI.JO", "SRE.JO", "LTE.JO",
    ],
    "Industrials": [
        "BAW.JO", "RLO.JO", "NPK.JO", "PPC.JO", "MPT.JO", "AFT.JO",
        "WBO.JO", "AEG.JO", "MUR.JO", "GND.JO", "TRE.JO", "SPG.JO",
        "MTH.JO", "CMH.JO", "IPL.JO", "KAP.JO", "HDC.JO", "ITE.JO",
    ],
    "Luxury": [
        "CFR.JO",
    ],
    "Healthcare": [
        "APN.JO", "MEI.JO", "NTC.JO", "LHC.JO",
    ],
    "Financial Services": [
        "PSG.JO", "CML.JO", "N91.JO", "TCP.JO", "AFH.JO", "RMI.JO",
    ],
    "Indices": [
        "^JN0U.JO", "^J203.JO",
    ],
    "Currency": [
        "ZAR=X", "EURZAR=X", "GBPZAR=X",
    ],
}

# How often to re-scan (seconds)
SCAN_INTERVAL_SECONDS = 300

# Historical data period for indicators
DATA_PERIOD = "6mo"

# Signal thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# How many tickers to fetch in one yfinance batch
BATCH_SIZE = 10
