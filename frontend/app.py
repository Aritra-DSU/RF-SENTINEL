import streamlit as st
import streamlit.components.v1 as components
from backend import classify_signal, defense_action
import random
import time
import math
from datetime import datetime
import pandas as pd
import requests
import json

st.set_page_config(
    page_title="RF SENTINEL — SIGINT OPS",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Bebas+Neue&family=Exo+2:wght@300;400;600;700;900&display=swap');

:root {
    --bg-primary:    #04060b;
    --bg-secondary:  #070c14;
    --bg-card:       #080e19;
    --accent-teal:   #00e5cc;
    --accent-orange: #ff6d00;
    --accent-red:    #ff1744;
    --accent-green:  #00e676;
    --accent-amber:  #ffab00;
    --text-primary:  #d0dce8;
    --text-dim:      #3a5068;
    --text-muted:    #1e3040;
    --border-dim:    #0d1f30;
    --border-glow:   #00e5cc22;
    --grid-line:     rgba(0,229,204,0.05);
}

html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

.stApp {
    background:
        linear-gradient(rgba(0,229,204,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,229,204,0.025) 1px, transparent 1px),
        radial-gradient(ellipse at 15% 0%, #0a1a28 0%, var(--bg-primary) 55%, #100408 100%);
    background-size: 40px 40px, 40px 40px, 100% 100%;
    min-height: 100vh;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050a12 0%, #04060b 100%);
    border-right: 1px solid #0d1f30;
}
section[data-testid="stSidebar"] * { color: #6a8aaa !important; }
section[data-testid="stSidebar"] .stSlider { padding: 4px 0; }

/* ── HEADINGS ── */
h1 {
    font-family: 'Bebas Neue', sans-serif !important;
    color: var(--accent-teal) !important;
    letter-spacing: 6px;
    font-size: 2rem !important;
    text-shadow: 0 0 30px rgba(0,229,204,0.4), 0 0 60px rgba(0,229,204,0.15);
    margin: 0 !important;
}
h2, h3, h4 {
    font-family: 'Exo 2', sans-serif !important;
    color: #7aa8c8 !important;
    letter-spacing: 3px;
    font-weight: 700;
    text-transform: uppercase;
}

/* ── METRIC CARDS — 3D effect ── */
.metric-card {
    background: linear-gradient(145deg, #0c1828 0%, #080e18 50%, #060a14 100%);
    border: 1px solid #0d2035;
    border-top: 1px solid #1a3550;
    border-radius: 6px;
    padding: 18px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow:
        0 8px 32px rgba(0,0,0,0.6),
        0 2px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.04),
        inset 0 -1px 0 rgba(0,0,0,0.3);
    transition: all 0.3s ease;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-teal), transparent);
    opacity: 0.5;
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(0,229,204,0.04) 0%, transparent 70%);
    pointer-events: none;
}
.metric-card:hover {
    border-color: rgba(0,229,204,0.2);
    box-shadow:
        0 12px 40px rgba(0,0,0,0.7),
        0 0 20px rgba(0,229,204,0.08),
        inset 0 1px 0 rgba(255,255,255,0.06);
    transform: translateY(-2px);
}
.metric-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem;
    line-height: 1;
    letter-spacing: 2px;
}
.metric-lbl {
    font-size: .62rem;
    letter-spacing: 4px;
    color: var(--text-dim);
    margin-top: 6px;
    text-transform: uppercase;
    font-weight: 600;
}
.metric-sub {
    font-family: 'Space Mono', monospace;
    font-size: .65rem;
    color: var(--text-dim);
    margin-top: 3px;
}

/* ── THREAT BAR ── */
.threat-wrap {
    background: #060810;
    border: 1px solid #0d1f30;
    border-radius: 4px;
    height: 18px;
    overflow: hidden;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
}
.threat-fill {
    height: 100%;
    border-radius: 3px;
    transition: width .8s cubic-bezier(.4,0,.2,1), background .8s;
    position: relative;
    overflow: hidden;
}
.threat-fill::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255,255,255,0.12), transparent);
    border-radius: 3px 3px 0 0;
}

/* ── ANIMATIONS ── */
@keyframes blink       { 0%,100%{opacity:1} 50%{opacity:.1} }
@keyframes glowpulse   { 0%,100%{text-shadow:0 0 10px currentColor} 50%{text-shadow:0 0 40px currentColor,0 0 80px currentColor} }
@keyframes scan-line   { 0%{top:-5%} 100%{top:105%} }
@keyframes border-glow { 0%,100%{box-shadow:0 0 10px rgba(255,23,68,0.3)} 50%{box-shadow:0 0 40px rgba(255,23,68,0.8),0 0 80px rgba(255,23,68,0.3)} }
@keyframes slide-in    { from{opacity:0;transform:translateX(-12px)} to{opacity:1;transform:translateX(0)} }
@keyframes pulse-ring  { 0%{transform:scale(0.95);opacity:0.8} 50%{transform:scale(1.02);opacity:1} 100%{transform:scale(0.95);opacity:0.8} }
@keyframes ticker      { 0%{transform:translateX(100%)} 100%{transform:translateX(-100%)} }
@keyframes vignette-pulse { 0%,100%{opacity:0.3} 50%{opacity:0.7} }

.blink     { animation: blink 0.6s infinite; }
.glowpulse { animation: glowpulse 2s infinite; }
.slide-in  { animation: slide-in 0.4s ease forwards; }

/* ── RED ALERT OVERLAY ── */
#red-alert-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: 99998;
    pointer-events: none;
}
#red-alert-overlay.active { display: block; }
#red-alert-vignette {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at center, transparent 30%, rgba(255,23,68,0.25) 70%, rgba(255,23,68,0.5) 100%);
    animation: vignette-pulse 0.8s infinite;
}
#red-alert-border {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    border: 3px solid rgba(255,23,68,0.8);
    animation: border-glow 0.6s infinite;
}
#red-alert-scanline {
    position: absolute;
    left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, rgba(255,23,68,0.8), transparent);
    animation: scan-line 2s linear infinite;
    box-shadow: 0 0 20px rgba(255,23,68,0.6);
}
#red-alert-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%,-50%);
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem;
    color: rgba(255,23,68,0.15);
    letter-spacing: 20px;
    white-space: nowrap;
    animation: blink 0.8s infinite;
    text-shadow: 0 0 60px rgba(255,23,68,0.5);
    pointer-events: none;
}
#red-ticker {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    height: 28px;
    background: rgba(255,23,68,0.15);
    border-top: 1px solid rgba(255,23,68,0.5);
    z-index: 99999;
    display: none;
    overflow: hidden;
    pointer-events: none;
}
#red-ticker.active { display: block; }
#red-ticker-text {
    font-family: 'Space Mono', monospace;
    font-size: .68rem;
    color: #ff1744;
    letter-spacing: 3px;
    white-space: nowrap;
    animation: ticker 12s linear infinite;
    line-height: 28px;
    padding-top: 4px;
}

/* ── CORNER NOTCH CARDS ── */
.notch-card {
    position: relative;
    background: linear-gradient(145deg, #0c1828, #07101a);
    border: 1px solid #0d2035;
    padding: 16px 18px;
    clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px));
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.03);
}
.notch-card::before {
    content: '';
    position: absolute;
    top: 0; right: 14px;
    width: 1px; height: 14px;
    background: var(--accent-teal);
    transform: rotate(45deg) translateX(7px);
    opacity: 0.4;
}

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(145deg, #0c1828, #08111e);
    color: var(--accent-teal);
    border: 1px solid rgba(0,229,204,0.3);
    border-radius: 3px;
    font-family: 'Exo 2', sans-serif;
    font-size: .75rem;
    font-weight: 700;
    letter-spacing: 3px;
    padding: 11px 24px;
    width: 100%;
    transition: all .2s;
    text-transform: uppercase;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    clip-path: polygon(8px 0%, 100% 0%, calc(100% - 8px) 100%, 0% 100%);
}
.stButton > button:hover {
    background: linear-gradient(145deg, #102030, #0c1a28);
    border-color: var(--accent-teal);
    box-shadow: 0 0 24px rgba(0,229,204,0.25), 0 4px 20px rgba(0,0,0,0.5), inset 0 1px 0 rgba(0,229,204,0.1);
    color: #fff;
    transform: translateY(-1px);
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-primary);
    border-bottom: 1px solid #0d1f30;
    gap: 3px;
    padding: 0 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Exo 2', sans-serif;
    font-weight: 700;
    letter-spacing: 2.5px;
    color: #2a4a6a;
    padding: 9px 20px;
    border-radius: 3px 3px 0 0;
    font-size: .78rem;
    text-transform: uppercase;
    transition: all .2s;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,229,204,0.06) !important;
    color: var(--accent-teal) !important;
    border-bottom: 2px solid var(--accent-teal) !important;
    box-shadow: 0 -1px 10px rgba(0,229,204,0.1);
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: #1e3a52; border-radius: 4px; }

/* ── ALERTS ── */
.alert-hostile {
    background: linear-gradient(135deg, rgba(40,5,8,0.98), rgba(25,4,6,0.98));
    border: 1px solid rgba(255,23,68,0.4);
    border-left: 3px solid var(--accent-red);
    border-radius: 4px;
    padding: 14px 18px;
    box-shadow: 0 0 40px rgba(255,23,68,0.12), inset 0 0 30px rgba(255,23,68,0.04), 0 8px 24px rgba(0,0,0,0.5);
    font-family: 'Space Mono', monospace;
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
}
.alert-friendly {
    background: linear-gradient(135deg, rgba(4,22,14,0.98), rgba(3,18,10,0.98));
    border: 1px solid rgba(0,230,118,0.3);
    border-left: 3px solid var(--accent-green);
    border-radius: 4px;
    padding: 14px 18px;
    box-shadow: 0 0 20px rgba(0,230,118,0.08), 0 8px 24px rgba(0,0,0,0.5);
    font-family: 'Space Mono', monospace;
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
}
.alert-unknown {
    background: linear-gradient(135deg, rgba(22,16,4,0.98), rgba(18,14,3,0.98));
    border: 1px solid rgba(255,171,0,0.3);
    border-left: 3px solid var(--accent-amber);
    border-radius: 4px;
    padding: 14px 18px;
    box-shadow: 0 0 20px rgba(255,171,0,0.08), 0 8px 24px rgba(0,0,0,0.5);
    font-family: 'Space Mono', monospace;
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
}

/* ── AI SUMMARY ── */
.ai-summary {
    background: linear-gradient(135deg, rgba(5,14,28,0.98), rgba(6,4,18,0.98));
    border: 1px solid rgba(255,109,0,0.25);
    border-left: 3px solid var(--accent-orange);
    border-radius: 4px;
    padding: 18px 20px;
    font-family: 'Exo 2', sans-serif;
    font-size: .9rem;
    line-height: 1.7;
    box-shadow: 0 0 30px rgba(255,109,0,0.08), 0 8px 24px rgba(0,0,0,0.5);
    position: relative;
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
}
.ai-summary::before {
    content: '⬡ SENTINEL-AI ANALYSIS';
    position: absolute;
    top: -9px; left: 16px;
    background: var(--bg-primary);
    padding: 0 8px;
    font-size: .58rem;
    letter-spacing: 4px;
    color: var(--accent-orange);
    font-family: 'Exo 2', sans-serif;
    font-weight: 700;
}

/* ── LOG ROWS ── */
.log-container {
    border: 1px solid #0d1f30;
    border-radius: 4px;
    overflow: hidden;
    background: var(--bg-primary);
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.4);
}

/* ── INPUT WIDGETS ── */
.stSlider > div > div { color: var(--accent-teal) !important; }
div[data-testid="stNumberInput"] input {
    background: var(--bg-secondary) !important;
    border-color: #0d2035 !important;
    color: var(--text-primary) !important;
    font-family: 'Space Mono', monospace !important;
}

/* ── SELECTBOX ── */
div[data-baseweb="select"] > div {
    background: var(--bg-secondary) !important;
    border-color: #0d2035 !important;
}

/* ── NOTIFICATION PANEL ── */
.notif-item {
    padding: 8px 12px;
    border-bottom: 1px solid #0a1a28;
    font-family: 'Space Mono', monospace;
    font-size: .68rem;
    display: flex;
    align-items: center;
    gap: 10px;
    animation: slide-in 0.3s ease forwards;
}
.notif-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
}

/* ── SECTION DIVIDER ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    margin-top: 4px;
}
.section-header-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,229,204,0.3), transparent);
}
.section-header-text {
    font-family: 'Exo 2', sans-serif;
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: 4px;
    color: var(--accent-teal);
    text-transform: uppercase;
    opacity: 0.7;
}

/* ── TOGGLE ── */
.stToggle { font-family: 'Exo 2', sans-serif !important; }

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: linear-gradient(145deg, #0c1828, #08111e) !important;
    color: var(--accent-teal) !important;
    border: 1px solid rgba(0,229,204,0.2) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: .72rem !important;
    letter-spacing: 2px !important;
    font-weight: 700 !important;
}
</style>

<!-- RED ALERT OVERLAY -->
<div id="red-alert-overlay">
  <div id="red-alert-vignette"></div>
  <div id="red-alert-border"></div>
  <div id="red-alert-scanline"></div>
  <div id="red-alert-text">⚠ THREAT DETECTED ⚠</div>
</div>
<div id="red-ticker">
  <div id="red-ticker-text">
    ⚠ CRITICAL THREAT LEVEL DETECTED &nbsp;|&nbsp; ALL UNITS ALERT &nbsp;|&nbsp; HOSTILE SIGNALS INTERCEPTED &nbsp;|&nbsp;
    INITIATE COUNTERMEASURES &nbsp;|&nbsp; COMMAND NOTIFIED &nbsp;|&nbsp; SECTOR LOCKDOWN IN EFFECT &nbsp;|&nbsp;
    RF SENTINEL MAXIMUM ALERT &nbsp;|&nbsp; ⚠ CRITICAL THREAT LEVEL DETECTED &nbsp;|&nbsp; ALL UNITS ALERT
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────
defaults = {
    "history": [], "conf_series": [], "threat_level": 0,
    "total_scans": 0, "hostile_count": 0, "friendly_count": 0, "unknown_count": 0,
    "radar_blips": [], "last_label": "—", "last_conf": 0.0, "last_action": "—",
    "alert_active": False, "last_ai_summary": "", "waterfall_data": [],
    "geo_points": [], "pattern_log": [], "gemini_api_key": "",
    "notifications": [], "threat_timeline": [], "mute_alarm": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


FREQ_MIN, FREQ_MAX = 70_000_000, 160_000_000

def freq_to_mhz(f): return f / 1_000_000

def threat_color(t):
    if t < 30: return "#00e676"
    if t < 60: return "#ffab00"
    if t < 80: return "#ff6d00"
    return "#ff1744"

def label_color(lbl):
    return {"Friendly": "#00e676", "Hostile": "#ff1744"}.get(lbl, "#ffab00")

def log_row_html(cells, is_header=False):
    cols = len(cells)
    bg   = "rgba(0,229,204,0.04)" if is_header else "transparent"
    bb   = "border-bottom:1px solid #0a1622"
    spans = "".join(
        f"<span style='color:{c};font-weight:{'700' if is_header else '400'};letter-spacing:{'2px' if is_header else '0.5px'}'>{t}</span>"
        for t, c in cells
    )
    return (f"<div style='display:grid;grid-template-columns:repeat({cols},1fr);"
            f"gap:6px;padding:7px 14px;{bb};background:{bg};"
            f"font-family:Space Mono,monospace;font-size:.7rem;align-items:center'>"
            f"{spans}</div>")

def log_container(rows_html, max_height=300):
    return (f"<div class='log-container' style='max-height:{max_height}px;overflow-y:auto'>{rows_html}</div>")

FAKE_REGIONS = [
    {"name": "Sector Alpha",  "lat": 33.5 + random.uniform(-2, 2), "lon": 44.4 + random.uniform(-2, 2)},
    {"name": "Grid Bravo",    "lat": 35.7 + random.uniform(-2, 2), "lon": 36.7 + random.uniform(-2, 2)},
    {"name": "Zone Charlie",  "lat": 31.5 + random.uniform(-2, 2), "lon": 34.5 + random.uniform(-2, 2)},
    {"name": "Post Delta",    "lat": 36.2 + random.uniform(-2, 2), "lon": 37.2 + random.uniform(-2, 2)},
    {"name": "Outpost Echo",  "lat": 29.9 + random.uniform(-2, 2), "lon": 40.1 + random.uniform(-2, 2)},
]

def get_fake_geo(freq, label):
    idx = int((freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * (len(FAKE_REGIONS) - 1))
    base = FAKE_REGIONS[idx]
    return {
        "name":  base["name"],
        "lat":   base["lat"] + random.uniform(-0.5, 0.5),
        "lon":   base["lon"] + random.uniform(-0.5, 0.5),
        "label": label,
        "freq":  freq_to_mhz(freq),
        "time":  datetime.now().strftime("%H:%M:%S"),
    }

def get_band_name(freq):
    mhz = freq_to_mhz(freq)
    if   mhz < 88:  return "VHF-LOW"
    elif mhz < 108: return "FM-BAND"
    elif mhz < 137: return "VHF-HIGH"
    else:            return "MILITARY"

def detect_pattern(history):
    if len(history) < 5:
        return None
    recent = history[:8]
    labels = [r[4] for r in recent]
    hostiles = labels.count("Hostile")
    unknowns = labels.count("Unknown")
    freqs = [r[1] for r in recent]
    freq_spread = max(freqs) - min(freqs) if freqs else 0

    if hostiles >= 5:
        return ("[CRITICAL] COORDINATED ATTACK", "Multiple hostile signals detected in rapid succession. Coordinated RF attack pattern confirmed.", "#ff1744")
    elif hostiles >= 3 and unknowns >= 2:
        return ("[WARNING] PROBE & SCAN DETECTED", "Mixed hostile/unknown pattern. Reconnaissance sweep before main attack vector.", "#ff6d00")
    elif freq_spread > 40 and hostiles >= 2:
        return ("[ALERT] FREQUENCY HOPPING", f"Signals spread {freq_spread:.1f} MHz. Classic frequency-hopping evasion tactic.", "#ffab00")
    elif unknowns >= 5:
        return ("[NOTICE] GHOST SIGNALS", "High volume of unclassified signals. Possible stealth probe or sensor interference.", "#00b4d8")
    return None

def call_gemini(api_key, freq, strength, noise, label, conf, action, band):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    threat_ctx = {
        "Hostile": "This is a confirmed hostile signal requiring immediate action.",
        "Unknown": "This signal is unclassified and under surveillance.",
        "Friendly": "This signal is confirmed as a friendly/allied transmission.",
    }.get(label, "")

    prompt = f"""You are SENTINEL-AI, a military RF signal intelligence system. Analyze this intercepted signal and provide a 3-sentence tactical assessment.

Signal Data:
- Frequency: {freq:.2f} MHz ({band} band)
- Signal Strength: {strength:.2f} (0-1 scale)
- Noise Level: {noise:.2f}
- AI Classification: {label} ({conf:.1f}% confidence)
- Recommended Action: {action}
- {threat_ctx}

Respond in 3 sentences max. Use military brevity. Start with threat level. Be specific about the frequency band implications. End with a tactical recommendation."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 150, "temperature": 0.7}
    }
    try:
        r = requests.post(url, json=payload, timeout=8)
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        band_info = {
            "VHF-LOW":  "VHF Low-band comms, likely ground-to-ground",
            "FM-BAND":  "Civil FM band, possible spoofing operation",
            "VHF-HIGH": "Aviation/navigation band, high-value target",
            "MILITARY": "Military tactical band, priority intercept"
        }
        summaries = {
            "Hostile":  f"[THREAT CONFIRMED] {band_info.get(band,'Unknown band')} signal at {freq:.1f} MHz with {strength:.0%} power — matches hostile transmission profile. Signal characteristics indicate coordinated electronic warfare activity; immediate countermeasures advised. Recommend BLOCK and escalate to command — threat index elevated.",
            "Unknown":  f"[UNVERIFIED] {band_info.get(band,'Unknown band')} transmission at {freq:.1f} MHz requires further analysis. Pattern does not match allied IFF signatures; treat as potential threat until verified. Maintain monitoring posture and prepare defensive response.",
            "Friendly": f"[ALLIED] {band_info.get(band,'Unknown band')} signal at {freq:.1f} MHz confirmed friendly via IFF. Strength {strength:.0%}, within normal operational parameters. No action required — signal logged.",
        }
        return summaries.get(label, "Signal analysis unavailable.")

def add_notification(label, freq, conf):
    icons = {"Hostile": "⚠", "Unknown": "◆", "Friendly": "▲"}
    colors = {"Hostile": "#ff1744", "Unknown": "#ffab00", "Friendly": "#00e676"}
    st.session_state.notifications.insert(0, {
        "time":  datetime.now().strftime("%H:%M:%S"),
        "label": label,
        "freq":  freq,
        "conf":  conf,
        "icon":  icons.get(label, "◈"),
        "color": colors.get(label, "#00e5cc"),
    })
    st.session_state.notifications = st.session_state.notifications[:30]

def record_scan(freq, strength, noise, label, conf, action):
    ts = datetime.now().strftime("%H:%M:%S")
    band = get_band_name(freq)
    st.session_state.history.insert(0, (ts, freq_to_mhz(freq), strength, noise, label, conf, action, band))
    st.session_state.history     = st.session_state.history[:300]
    st.session_state.conf_series.append(conf)
    st.session_state.conf_series = st.session_state.conf_series[-100:]
    st.session_state.total_scans += 1
    add_notification(label, freq_to_mhz(freq), conf)

    if label == "Hostile":
        st.session_state.hostile_count  += 1
        st.session_state.alert_active    = True
    elif label == "Unknown":
        st.session_state.unknown_count  += 1
        st.session_state.alert_active    = False
    else:
        st.session_state.friendly_count += 1
        st.session_state.alert_active    = False

    recent = st.session_state.history[:20]
    if recent:
        total_w, threat_w = 0.0, 0.0
        for i, entry in enumerate(recent):
            recency = math.exp(-i * 0.12)
            sig_str = entry[2]
            lbl_w   = {"Hostile": 1.0, "Unknown": 0.35, "Friendly": 0.0}.get(entry[4], 0.0)
            w       = recency * (0.6 + 0.4 * sig_str)
            threat_w += lbl_w * w
            total_w  += w
        raw = (threat_w / total_w) if total_w > 0 else 0.0
        st.session_state.threat_level = round(min(100, raw * 100))

    st.session_state.last_label  = label
    st.session_state.last_conf   = conf
    st.session_state.last_action = action

    # Threat timeline
    st.session_state.threat_timeline.append({
        "time": ts,
        "threat": st.session_state.threat_level,
        "label": label,
    })
    st.session_state.threat_timeline = st.session_state.threat_timeline[-60:]

    # Geo
    geo = get_fake_geo(freq, label)
    st.session_state.geo_points.insert(0, geo)
    st.session_state.geo_points = st.session_state.geo_points[:50]

    # Waterfall
    row = []
    for i in range(64):
        bin_freq = FREQ_MIN + (FREQ_MAX - FREQ_MIN) * i / 64
        dist = abs(bin_freq - freq)
        power = strength * math.exp(-dist / (8_000_000)) + noise * random.uniform(0, 1) * 0.3
        row.append(min(1.0, power))
    st.session_state.waterfall_data.insert(0, {"row": row, "label": label, "time": ts})
    st.session_state.waterfall_data = st.session_state.waterfall_data[:40]

    # Radar blip
    angle = ((freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN)) * 2 * math.pi
    r     = 0.25 + strength * 0.65
    st.session_state.radar_blips.append({
        "label": label, "age": 0, "freq": freq, "strength": strength,
        "x": 0.5 + r * 0.5 * math.cos(angle),
        "y": 0.5 + r * 0.5 * math.sin(angle),
    })
    st.session_state.radar_blips = [b for b in st.session_state.radar_blips if b["age"] < 15]
    for b in st.session_state.radar_blips:
        b["age"] += 1


_tl_now = st.session_state.threat_level
# Auto-unmute when threat drops back below threshold so alarm re-arms next time
if _tl_now < 75 and st.session_state.mute_alarm:
    st.session_state.mute_alarm = False
components.html(f"""
<script>
(function() {{
  const TL = {_tl_now};
  const overlay  = window.parent.document.getElementById('red-alert-overlay');
  const ticker   = window.parent.document.getElementById('red-ticker');
  if (!overlay || !ticker) return;
  if (TL >= 75) {{
    overlay.classList.add('active');
    ticker.classList.add('active');
  }} else {{
    overlay.classList.remove('active');
    ticker.classList.remove('active');
  }}
}})();
</script>
""", height=0)


components.html(f"""
<script>
(function() {{
  const THREAT = {_tl_now};
  const MUTED  = {'true' if st.session_state.mute_alarm else 'false'};
  if (!window._rfAlarmCtx) {{
    window._rfAlarmCtx = null;
    window._rfAlarmNodes = [];
    window._rfAlarmRunning = false;
  }}
  function stopAlarm() {{
    window._rfAlarmRunning = false;
    window._rfAlarmNodes.forEach(n => {{ try {{ n.stop(); }} catch(e) {{}} }});
    window._rfAlarmNodes = [];
    if (window._rfAlarmCtx) {{ window._rfAlarmCtx.close(); window._rfAlarmCtx = null; }}
  }}
  function playMilitaryBuzzer() {{
    if (window._rfAlarmRunning) return;
    window._rfAlarmRunning = true;
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    window._rfAlarmCtx = ctx;
    let cycle = 0;
    function whoopCycle() {{
      if (!window._rfAlarmRunning || cycle >= 999) return;
      cycle++;
      const now = ctx.currentTime, DUR = 0.55;
      const osc1 = ctx.createOscillator(), gain1 = ctx.createGain();
      osc1.type = 'sawtooth';
      osc1.frequency.setValueAtTime(700, now);
      osc1.frequency.linearRampToValueAtTime(1300, now + DUR * 0.6);
      osc1.frequency.linearRampToValueAtTime(800, now + DUR);
      gain1.gain.setValueAtTime(0, now);
      gain1.gain.linearRampToValueAtTime(0.35, now + 0.04);
      gain1.gain.setValueAtTime(0.35, now + DUR - 0.05);
      gain1.gain.linearRampToValueAtTime(0, now + DUR);
      osc1.connect(gain1); gain1.connect(ctx.destination);
      osc1.start(now); osc1.stop(now + DUR);
      window._rfAlarmNodes.push(osc1);
      const osc2 = ctx.createOscillator(), gain2 = ctx.createGain();
      osc2.type = 'square';
      osc2.frequency.setValueAtTime(350, now);
      osc2.frequency.linearRampToValueAtTime(650, now + DUR * 0.6);
      gain2.gain.setValueAtTime(0, now); gain2.gain.linearRampToValueAtTime(0.12, now + 0.04);
      gain2.gain.setValueAtTime(0.12, now + DUR - 0.05); gain2.gain.linearRampToValueAtTime(0, now + DUR);
      osc2.connect(gain2); gain2.connect(ctx.destination);
      osc2.start(now); osc2.stop(now + DUR);
      window._rfAlarmNodes.push(osc2);
      setTimeout(whoopCycle, (DUR + 0.25) * 1000);
    }}
    whoopCycle();
  }}
  if (THREAT >= 75 && !MUTED) {{ playMilitaryBuzzer(); }} else {{ stopAlarm(); }}
}})();
</script>
""", height=0)


with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 24px'>
      <div style='font-family:Bebas Neue,sans-serif;font-size:1.6rem;color:#00e5cc;
                  letter-spacing:6px;text-shadow:0 0 20px rgba(0,229,204,0.5)'>RF SENTINEL</div>
      <div style='font-size:.6rem;color:#1e3a52;letter-spacing:6px;margin-top:3px;font-family:Exo 2,sans-serif;font-weight:700'>SIGINT OPS v3.1</div>
      <div style='margin:14px auto;width:70%;height:1px;background:linear-gradient(90deg,transparent,rgba(0,229,204,0.3),transparent)'></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:.62rem;letter-spacing:4px;color:#1e4a6a;font-family:Exo 2,sans-serif;font-weight:700;margin-bottom:8px'>SIGNAL PARAMETERS</div>", unsafe_allow_html=True)
    freq     = st.slider("Frequency (MHz)", 70.0, 160.0, 100.0, step=0.5) * 1_000_000
    strength = st.slider("Signal Strength",  0.0,   1.0,   0.6,  step=0.01)
    noise    = st.slider("Noise Level",      0.0,   0.5,   0.1,  step=0.01)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.62rem;letter-spacing:4px;color:#1e4a6a;font-family:Exo 2,sans-serif;font-weight:700;margin-bottom:6px'>GEMINI API KEY</div>", unsafe_allow_html=True)
    api_key_input = st.text_input("API Key", value=st.session_state.gemini_api_key, type="password", placeholder="AIza...", label_visibility="collapsed")
    if api_key_input:
        st.session_state.gemini_api_key = api_key_input
        st.markdown("<div style='font-size:.65rem;color:#00e676;font-family:Space Mono,monospace'>▲ KEY AUTHENTICATED</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:.65rem;color:#ffab00;font-family:Space Mono,monospace'>◆ OFFLINE MODE</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin:14px 0;height:1px;background:linear-gradient(90deg,rgba(0,229,204,0.15),transparent)'></div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size:.62rem;letter-spacing:4px;color:#1e4a6a;font-family:Exo 2,sans-serif;font-weight:700;margin-bottom:8px'>BAND REFERENCE</div>", unsafe_allow_html=True)
    for band, (rng, use, col) in {
        "VHF LOW":  ("70–88 MHz",  "Comms / Recon",   "#00e676"),
        "FM BAND":  ("88–108 MHz", "Civil / Spoof",   "#ffab00"),
        "VHF HIGH": ("108–137",    "Aviation / Nav",  "#00e5cc"),
        "MILITARY": ("137–160",    "Tactical / SAT",  "#ff6d00"),
    }.items():
        st.markdown(f"""<div style='font-size:.7rem;margin-bottom:8px;padding:6px 10px;
            background:rgba(0,0,0,0.3);border-left:2px solid {col}44;border-radius:2px'>
            <span style='color:{col};font-weight:700;font-family:Exo 2,sans-serif'>{band}</span>
            <span style='color:#1e3a52;font-size:.62rem;margin-left:6px'>{rng}</span>
            <div style='color:#3a5a7a;font-size:.62rem;margin-top:2px'>{use}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:14px 0;height:1px;background:linear-gradient(90deg,rgba(0,229,204,0.15),transparent)'></div>", unsafe_allow_html=True)

    hp2 = st.session_state.hostile_count / max(1, st.session_state.total_scans) * 100
    tc_s = threat_color(st.session_state.threat_level)
    st.markdown(f"""
    <div style='font-family:Space Mono,monospace;font-size:.68rem;line-height:2.4'>
      <div style='color:#1e3a52;letter-spacing:3px;font-size:.58rem;font-family:Exo 2,sans-serif;font-weight:700;margin-bottom:6px'>SESSION STATISTICS</div>
      <div style='display:flex;justify-content:space-between'>
        <span style='color:#2a4a6a'>SCANS</span>
        <b style='color:#00e5cc'>{st.session_state.total_scans}</b>
      </div>
      <div style='display:flex;justify-content:space-between'>
        <span style='color:#2a4a6a'>FRIENDLY</span>
        <b style='color:#00e676'>{st.session_state.friendly_count}</b>
      </div>
      <div style='display:flex;justify-content:space-between'>
        <span style='color:#2a4a6a'>UNKNOWN</span>
        <b style='color:#ffab00'>{st.session_state.unknown_count}</b>
      </div>
      <div style='display:flex;justify-content:space-between'>
        <span style='color:#2a4a6a'>HOSTILE</span>
        <b style='color:#ff1744'>{st.session_state.hostile_count}</b>
      </div>
      <div style='display:flex;justify-content:space-between;margin-top:4px;padding-top:4px;border-top:1px solid #0d1f30'>
        <span style='color:#2a4a6a'>THREAT</span>
        <b style='color:{tc_s}'>{st.session_state.threat_level}%</b>
      </div>
      <div style='display:flex;justify-content:space-between'>
        <span style='color:#2a4a6a'>HOSTILE%</span>
        <b style='color:#ff6d00'>{hp2:.1f}%</b>
      </div>
    </div>""", unsafe_allow_html=True)

    
    st.markdown("<div style='margin:14px 0;height:1px;background:linear-gradient(90deg,rgba(0,229,204,0.15),transparent)'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.62rem;letter-spacing:4px;color:#1e4a6a;font-family:Exo 2,sans-serif;font-weight:700;margin-bottom:8px'>RECENT ALERTS</div>", unsafe_allow_html=True)
    notifs = st.session_state.notifications[:8]
    if notifs:
        notif_html = "<div style='border:1px solid #0d1f30;border-radius:4px;overflow:hidden;background:#04060b'>"
        for n in notifs:
            notif_html += f"""<div class='notif-item'>
              <div class='notif-dot' style='background:{n["color"]};box-shadow:0 0 6px {n["color"]}88'></div>
              <span style='color:{n["color"]}'>{n["icon"]}</span>
              <span style='color:#3a5a7a'>{n["time"]}</span>
              <span style='color:#8aaccc'>{n["label"]}</span>
              <span style='color:#1e4a6a;margin-left:auto'>{n["freq"]:.1f}M</span>
            </div>"""
        notif_html += "</div>"
        st.markdown(notif_html, unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:.65rem;color:#1e3a52;font-family:Space Mono,monospace'>No alerts yet</div>", unsafe_allow_html=True)


h1, h2, h3, h4 = st.columns([3, 1, 1, 1])
with h1:
    st.markdown(f"""
    <h1>RF SENTINEL — SIGINT OPS</h1>
    <div style='font-family:Space Mono,monospace;font-size:.68rem;color:#1e3a52;margin-top:4px'>
      ◈ SYS: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC &nbsp;|&nbsp;
      BAND: 70–160 MHz &nbsp;|&nbsp; MODE: ACTIVE &nbsp;|&nbsp;
      SCANS: {st.session_state.total_scans} &nbsp;|&nbsp;
      NODE: SENTINEL-PRIMARY
    </div>
    """, unsafe_allow_html=True)

with h2:
    tl  = st.session_state.threat_level
    tc  = threat_color(tl)
    tlabel = ["LOW", "ELEVATED", "HIGH", "CRITICAL"][min(3, tl // 25)]
    anim = "animation:blink 0.5s infinite" if tl >= 75 else ("animation:glowpulse 2s infinite" if tl >= 50 else "")
    st.markdown(f"""
    <div style='background:linear-gradient(145deg,#0c0508,#080306);
        border:1px solid {tc}33;border-top:1px solid {tc}66;
        border-radius:4px;padding:14px;text-align:center;
        box-shadow:0 0 30px {tc}22,0 8px 24px rgba(0,0,0,0.6),inset 0 1px 0 rgba(255,255,255,0.03);
        clip-path:polygon(8px 0%,100% 0%,100% calc(100% - 8px),calc(100% - 8px) 100%,0% 100%,0% 8px)'>
      <div style='font-family:Bebas Neue,sans-serif;font-size:2.2rem;color:{tc};{anim};
          text-shadow:0 0 20px {tc}88;letter-spacing:2px'>{tl}%</div>
      <div style='font-size:.55rem;letter-spacing:4px;color:{tc};opacity:.7;
          font-family:Exo 2,sans-serif;font-weight:700;margin-top:2px'>{tlabel} THREAT</div>
    </div>""", unsafe_allow_html=True)

with h3:
    lbl_now = st.session_state.last_label
    lc_now  = label_color(lbl_now)
    st.markdown(f"""
    <div style='background:linear-gradient(145deg,#050a14,#040810);
        border:1px solid {lc_now}22;border-top:1px solid {lc_now}44;
        border-radius:4px;padding:14px;text-align:center;
        box-shadow:0 8px 24px rgba(0,0,0,0.5),inset 0 1px 0 rgba(255,255,255,0.03);
        clip-path:polygon(8px 0%,100% 0%,100% calc(100% - 8px),calc(100% - 8px) 100%,0% 100%,0% 8px)'>
      <div style='font-family:Bebas Neue,sans-serif;font-size:1.5rem;color:{lc_now};
          letter-spacing:3px;text-shadow:0 0 15px {lc_now}66'>{lbl_now}</div>
      <div style='font-size:.55rem;letter-spacing:4px;color:{lc_now};opacity:.55;
          font-family:Exo 2,sans-serif;font-weight:700;margin-top:2px'>LAST SIGNAL</div>
    </div>""", unsafe_allow_html=True)

with h4:
    is_muted = st.session_state.mute_alarm
    mute_label = "🔇  UNMUTE ALARM" if is_muted else "🔔  SILENCE ALARM"
    mute_color = "#ffab00" if is_muted else "#ff1744"
    mute_bg    = "rgba(30,18,4,0.95)" if is_muted else "rgba(30,4,8,0.95)"
    st.markdown(f"""
    <style>
    div[data-testid="stButton"][id="mute_btn_wrap"] > button {{
        border-color: {mute_color}66 !important;
        color: {mute_color} !important;
        background: {mute_bg} !important;
    }}
    div[data-testid="stButton"][id="mute_btn_wrap"] > button:hover {{
        border-color: {mute_color} !important;
        box-shadow: 0 0 20px {mute_color}44 !important;
    }}
    </style>""", unsafe_allow_html=True)
    if st.button(mute_label, key="btn_mute_alarm"):
        st.session_state.mute_alarm = not st.session_state.mute_alarm
        st.rerun()
    st.markdown(f"""
    <div style='text-align:center;font-family:Space Mono,monospace;font-size:.58rem;
        color:{mute_color};opacity:.6;margin-top:4px;letter-spacing:2px'>
        {"ALARM SILENCED" if is_muted else "ALARM ACTIVE" if st.session_state.threat_level >= 75 else "STANDBY"}
    </div>""", unsafe_allow_html=True)


k1, k2, k3, k4, k5 = st.columns(5)
def kpi(col, val, lbl, color, sub=""):
    col.markdown(f"""
    <div class='metric-card'>
      <div class='metric-val' style='color:{color}'>{val}</div>
      <div class='metric-lbl'>{lbl}</div>
      {f"<div class='metric-sub'>{sub}</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)

kpi(k1, st.session_state.total_scans,    "TOTAL SCANS",  "#00e5cc", f"AVG CONF: {sum(st.session_state.conf_series)/max(1,len(st.session_state.conf_series)):.1f}%" if st.session_state.conf_series else "")
kpi(k2, st.session_state.friendly_count, "FRIENDLY",     "#00e676", f"{st.session_state.friendly_count/max(1,st.session_state.total_scans)*100:.0f}% of total")
kpi(k3, st.session_state.unknown_count,  "UNKNOWN",      "#ffab00", f"{st.session_state.unknown_count/max(1,st.session_state.total_scans)*100:.0f}% of total")
kpi(k4, st.session_state.hostile_count,  "HOSTILE",      "#ff1744", f"{st.session_state.hostile_count/max(1,st.session_state.total_scans)*100:.0f}% of total")
hostile_rate = st.session_state.hostile_count / max(1, st.session_state.total_scans) * 100
kpi(k5, f"{hostile_rate:.0f}%",          "HOSTILE RATE", threat_color(hostile_rate), "last 20 signals")

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)


tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "SCANNER",
    "WATERFALL",
    "GEO MAP",
    "LIVE MONITOR",
    "THREAT TIMELINE",
    "ATTACK SIM",
    "EVENT LOG",
])

with tab1:
    col_rad, col_res = st.columns([1, 1], gap="large")

    with col_rad:
        st.markdown("""
        <div class='section-header'>
          <span class='section-header-text'>Tactical Radar</span>
          <div class='section-header-line'></div>
        </div>""", unsafe_allow_html=True)

        blips_js = "["
        for b in st.session_state.radar_blips:
            a_b  = ((b.get("freq", freq) - FREQ_MIN) / (FREQ_MAX - FREQ_MIN)) * 360
            r_b  = 0.22 + b.get("strength", 0.5) * 0.68
            bc   = {"Friendly": "#00e676", "Hostile": "#ff1744", "Unknown": "#ffab00"}.get(b["label"], "#00e5cc")
            fade = max(0.12, 1 - b["age"] / 15)
            blips_js += f'{{"a":{a_b:.1f},"r":{r_b:.2f},"c":"{bc}","alpha":{fade:.2f}}},'
        blips_js += "]"
        cur_a = ((freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN)) * 360
        cur_r = 0.22 + strength * 0.68
        threat_col_js = threat_color(st.session_state.threat_level).replace("#", "")

        radar_html = f"""<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#04060b;display:flex;flex-direction:column;align-items:center;padding:8px;font-family:'Exo 2',sans-serif}}
canvas{{border-radius:50%;display:block;
  box-shadow:0 0 60px rgba(0,229,204,0.1),0 0 120px rgba(0,229,204,0.04),0 20px 60px rgba(0,0,0,0.8)}}
.info{{font-family:monospace;font-size:10px;color:#1e4a6a;margin-top:10px;
  letter-spacing:2px;text-align:center;background:rgba(0,0,0,0.4);
  border:1px solid #0d1f30;padding:5px 14px;border-radius:3px}}
.info b{{color:#00e5cc}}
</style></head><body>
<canvas id="r" width="320" height="320"></canvas>
<div class="info">FREQ: <b>{freq_to_mhz(freq):.1f} MHz</b> &nbsp;|&nbsp; STR: <b>{strength:.2f}</b> &nbsp;|&nbsp; BAND: <b>{get_band_name(freq)}</b></div>
<script>
const cv=document.getElementById('r'),ctx=cv.getContext('2d');
const W=320,H=320,CX=160,CY=160,R=148;
const blips={blips_js},curA={cur_a:.1f},curR={cur_r:.2f};
let sweep=0,t=0;
const d2r=d=>d*Math.PI/180;
const p2xy=(a,r)=>{{const rad=d2r(a-90);return[CX+Math.cos(rad)*r*R,CY+Math.sin(rad)*r*R]}};
function draw(){{
  t++;
  ctx.clearRect(0,0,W,H);

  // Outer glow ring
  const og=ctx.createRadialGradient(CX,CY,R-4,CX,CY,R+8);
  og.addColorStop(0,'rgba(0,229,204,0.0)');
  og.addColorStop(0.5,'rgba(0,229,204,0.08)');
  og.addColorStop(1,'rgba(0,229,204,0.0)');
  ctx.beginPath();ctx.arc(CX,CY,R+4,0,Math.PI*2);ctx.fillStyle=og;ctx.fill();

  // Background gradient
  const bg=ctx.createRadialGradient(CX,CY,0,CX,CY,R);
  bg.addColorStop(0,'#0c1828');
  bg.addColorStop(0.5,'#070e1a');
  bg.addColorStop(1,'#040810');
  ctx.beginPath();ctx.arc(CX,CY,R,0,Math.PI*2);ctx.fillStyle=bg;ctx.fill();

  // Grid rings
  [0.2,0.4,0.6,0.8,1.0].forEach((rf,i)=>{{
    ctx.beginPath();ctx.arc(CX,CY,rf*R,0,Math.PI*2);
    if(i===4){{
      ctx.strokeStyle='rgba(0,229,204,0.2)';ctx.lineWidth=1.5;ctx.setLineDash([]);
    }} else {{
      ctx.strokeStyle='rgba(0,229,204,0.07)';ctx.lineWidth=0.8;ctx.setLineDash([3,6]);
    }}
    ctx.stroke();ctx.setLineDash([]);
  }});

  // Spokes
  for(let a=0;a<360;a+=30){{
    const[x1,y1]=p2xy(a,0.0),[x2,y2]=p2xy(a,1.0);
    ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);
    ctx.strokeStyle='rgba(0,229,204,0.05)';ctx.lineWidth=0.6;ctx.setLineDash([2,8]);ctx.stroke();ctx.setLineDash([]);
  }}

  // Sweep trail (multiple passes for glow effect)
  const sr=d2r(sweep-90);
  for(let i=0;i<12;i++){{
    const ta=sr-d2r(i*5);
    ctx.save();ctx.beginPath();ctx.moveTo(CX,CY);
    ctx.arc(CX,CY,R,ta-d2r(5),ta,false);ctx.closePath();
    const alpha=(0.15-i*0.012).toFixed(3);
    ctx.fillStyle=`rgba(0,229,204,${{Math.max(0,alpha)}})`;ctx.fill();ctx.restore();
  }}

  // Sweep line with glow
  const[sx,sy]=p2xy(sweep,1.0);
  ctx.save();
  ctx.shadowBlur=15;ctx.shadowColor='rgba(0,229,204,0.8)';
  ctx.beginPath();ctx.moveTo(CX,CY);ctx.lineTo(sx,sy);
  ctx.strokeStyle='rgba(0,229,204,0.95)';ctx.lineWidth=2;ctx.stroke();
  ctx.restore();

  // Blips
  blips.forEach(b=>{{
    const[bx,by]=p2xy(b.a,b.r);
    ctx.globalAlpha=b.alpha;
    ctx.save();ctx.shadowBlur=16;ctx.shadowColor=b.c;
    ctx.beginPath();ctx.arc(bx,by,5,0,Math.PI*2);ctx.fillStyle=b.c;ctx.fill();
    ctx.restore();
    // Ring
    ctx.beginPath();ctx.arc(bx,by,10,0,Math.PI*2);
    ctx.strokeStyle=b.c;ctx.lineWidth=1;ctx.stroke();
    // Cross-hair
    ctx.beginPath();ctx.moveTo(bx-14,by);ctx.lineTo(bx-7,by);
    ctx.moveTo(bx+7,by);ctx.lineTo(bx+14,by);
    ctx.moveTo(bx,by-14);ctx.lineTo(bx,by-7);
    ctx.moveTo(bx,by+7);ctx.lineTo(bx,by+14);
    ctx.strokeStyle=b.c;ctx.lineWidth=0.8;ctx.globalAlpha=b.alpha*0.6;ctx.stroke();
    ctx.globalAlpha=1;
  }});

  // Current signal — large pulsing marker
  const[px,py]=p2xy(curA,curR);
  // Pulse rings
  for(let i=0;i<4;i++){{
    const ph=((t*3+i*300)%1200)/1200;
    ctx.beginPath();ctx.arc(px,py,8+ph*30,0,Math.PI*2);
    ctx.strokeStyle='rgba(0,229,204,1)';ctx.lineWidth=1.5;ctx.globalAlpha=(1-ph)*0.5;ctx.stroke();
  }}
  ctx.globalAlpha=1;
  ctx.save();ctx.shadowBlur=25;ctx.shadowColor='rgba(0,229,204,1)';
  ctx.beginPath();ctx.arc(px,py,7,0,Math.PI*2);ctx.fillStyle='rgba(0,229,204,0.95)';ctx.fill();
  ctx.restore();
  // Core dot
  ctx.beginPath();ctx.arc(px,py,3,0,Math.PI*2);ctx.fillStyle='#fff';ctx.fill();

  // Outer ring
  ctx.beginPath();ctx.arc(CX,CY,R,0,Math.PI*2);
  ctx.strokeStyle='rgba(0,229,204,0.3)';ctx.lineWidth=2;ctx.stroke();

  // Corner decoration
  const corners=[[-1,-1],[1,-1],[1,1],[-1,1]];
  corners.forEach(([cx2,cy2])=>{{
    const ox=CX+cx2*(R-2),oy=CY+cy2*(R-2);
    ctx.beginPath();ctx.moveTo(ox,oy-cy2*12);ctx.lineTo(ox,oy);ctx.lineTo(ox-cx2*12,oy);
    ctx.strokeStyle='rgba(0,229,204,0.4)';ctx.lineWidth=1.5;ctx.stroke();
  }});

  // Compass labels
  ctx.fillStyle='rgba(0,229,204,0.35)';ctx.font='bold 9px monospace';ctx.textAlign='center';
  ctx.fillText('N',CX,CY-R+14);ctx.fillText('S',CX,CY+R-6);
  ctx.textAlign='left';ctx.fillText('E',CX+R-12,CY+4);
  ctx.textAlign='right';ctx.fillText('W',CX-R+12,CY+4);

  // Freq ring labels
  ctx.fillStyle='rgba(0,229,204,0.2)';ctx.font='7px monospace';ctx.textAlign='left';
  ctx.fillText('70M',CX+3,CY-0.18*R);ctx.fillText('93M',CX+3,CY-0.38*R);
  ctx.fillText('115M',CX+3,CY-0.58*R);ctx.fillText('137M',CX+3,CY-0.78*R);

  // Center dot
  ctx.save();ctx.shadowBlur=10;ctx.shadowColor='rgba(0,229,204,1)';
  ctx.beginPath();ctx.arc(CX,CY,3,0,Math.PI*2);ctx.fillStyle='rgba(0,229,204,0.8)';ctx.fill();
  ctx.restore();

  sweep=(sweep+1.6)%360;
  requestAnimationFrame(draw);
}}
draw();
</script></body></html>"""
        components.html(radar_html, height=400, scrolling=False)

  
    with col_res:
        st.markdown("""
        <div class='section-header'>
          <span class='section-header-text'>Signal Analysis</span>
          <div class='section-header-line'></div>
        </div>""", unsafe_allow_html=True)

        if st.button("⬡  ANALYZE SIGNAL", key="btn_analyze"):
            with st.spinner("Processing..."):
                label, conf = classify_signal(freq, strength, noise)
                action = defense_action(label)
                record_scan(freq, strength, noise, label, conf, action)
                band = get_band_name(freq)
                summary = call_gemini(st.session_state.gemini_api_key, freq_to_mhz(freq), strength, noise, label, conf, action, band)
                st.session_state.last_ai_summary = summary

        lbl = st.session_state.last_label
        lc  = label_color(lbl)
        conf_val = st.session_state.last_conf

        alert_cls = {"Hostile": "alert-hostile", "Friendly": "alert-friendly", "Unknown": "alert-unknown"}.get(lbl, "alert-unknown")
        icon_map  = {
            "Hostile":  "⚠  HOSTILE SIGNAL INTERCEPTED",
            "Friendly": "▲  FRIENDLY SIGNAL CONFIRMED",
            "Unknown":  "◆  UNIDENTIFIED SIGNAL DETECTED"
        }
        st.markdown(f"""
        <div class='{alert_cls}' style='margin-bottom:14px'>
          <div style='font-size:.88rem;font-weight:700;color:{lc};letter-spacing:2px;font-family:Exo 2,sans-serif'>
            {icon_map.get(lbl, "◈  AWAITING SCAN")}
          </div>
          <div style='margin-top:8px;display:flex;gap:20px;font-size:.72rem;font-family:Space Mono,monospace'>
            <span style='color:#3a5a7a'>CONF: <b style='color:{lc}'>{conf_val:.1f}%</b></span>
            <span style='color:#3a5a7a'>ACTION: <b style='color:{lc}'>{st.session_state.last_action}</b></span>
            <span style='color:#3a5a7a'>BAND: <b style='color:#00e5cc'>{get_band_name(freq)}</b></span>
          </div>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c1.markdown(f"""
        <div class='metric-card'>
          <div class='metric-val' style='color:{lc}'>{conf_val:.1f}%</div>
          <div class='metric-lbl'>CONFIDENCE</div>
        </div>""", unsafe_allow_html=True)
        c2.markdown(f"""
        <div class='metric-card'>
          <div class='metric-val' style='color:{threat_color(st.session_state.threat_level)};font-size:1.8rem'>
            {st.session_state.threat_level}%
          </div>
          <div class='metric-lbl'>THREAT INDEX</div>
        </div>""", unsafe_allow_html=True)

        tl = st.session_state.threat_level
        tc = threat_color(tl)
        tlabel = ["LOW", "ELEVATED", "HIGH", "CRITICAL"][min(3, tl // 25)]
        st.markdown(f"""
        <div style='margin:14px 0 5px;display:flex;justify-content:space-between;
            font-size:.62rem;letter-spacing:3px;font-family:Exo 2,sans-serif;font-weight:700'>
          <span style='color:#1e3a52'>THREAT LEVEL</span>
          <span style='color:{tc}'>{tlabel}</span>
        </div>
        <div class='threat-wrap'>
          <div class='threat-fill' style='width:{tl}%;background:linear-gradient(90deg,#0a2a50,{tc})'></div>
        </div>""", unsafe_allow_html=True)

        norm_pos   = (freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * 100
        band_color = "#00e676" if norm_pos < 22 else ("#00e5cc" if norm_pos < 52 else ("#ff6d00" if norm_pos < 80 else "#ff1744"))
        st.markdown(f"""
        <div style='margin:14px 0 5px;font-size:.62rem;letter-spacing:3px;color:#1e3a52;
            font-family:Exo 2,sans-serif;font-weight:700'>SPECTRUM POSITION</div>
        <div style='background:#04060b;border:1px solid #0d1f30;border-radius:3px;height:12px;overflow:hidden;position:relative;
            box-shadow:inset 0 2px 4px rgba(0,0,0,0.5)'>
          <div style='height:100%;width:{norm_pos:.1f}%;background:linear-gradient(90deg,#0a2050,{band_color});
              border-radius:2px;box-shadow:2px 0 12px {band_color}88;position:relative'>
            <div style='position:absolute;top:0;left:0;right:0;height:50%;
                background:linear-gradient(180deg,rgba(255,255,255,0.15),transparent);border-radius:2px 2px 0 0'></div>
          </div>
        </div>
        <div style='display:flex;justify-content:space-between;font-size:.6rem;color:#1e3a52;
            font-family:Space Mono,monospace;margin-top:3px'>
          <span>70</span>
          <span style='color:{band_color};font-weight:700'>{freq_to_mhz(freq):.1f} MHz</span>
          <span>160</span>
        </div>""", unsafe_allow_html=True)

        if st.session_state.total_scans > 0:
            fp = st.session_state.friendly_count / st.session_state.total_scans * 100
            hp = st.session_state.hostile_count  / st.session_state.total_scans * 100
            up = 100 - fp - hp
            st.markdown(f"""
            <div style='margin:14px 0 5px;font-size:.62rem;letter-spacing:3px;color:#1e3a52;
                font-family:Exo 2,sans-serif;font-weight:700'>SIGNAL DISTRIBUTION</div>
            <div style='display:flex;gap:1px;height:10px;border-radius:2px;overflow:hidden;
                border:1px solid #0d1f30;box-shadow:inset 0 2px 4px rgba(0,0,0,0.5)'>
              <div style='width:{fp:.1f}%;background:linear-gradient(180deg,#00ff94,#00e676);position:relative'>
                <div style='position:absolute;top:0;left:0;right:0;height:50%;background:rgba(255,255,255,0.15)'></div>
              </div>
              <div style='width:{up:.1f}%;background:linear-gradient(180deg,#ffc433,#ffab00)'></div>
              <div style='width:{hp:.1f}%;background:linear-gradient(180deg,#ff4060,#ff1744)'></div>
            </div>
            <div style='display:flex;justify-content:space-between;font-size:.6rem;
                font-family:Space Mono,monospace;margin-top:4px'>
              <span style='color:#00e676'>▮ {fp:.0f}% FRN</span>
              <span style='color:#ffab00'>▮ {up:.0f}% UNK</span>
              <span style='color:#ff1744'>▮ {hp:.0f}% HST</span>
            </div>""", unsafe_allow_html=True)

        if st.session_state.last_ai_summary:
            st.markdown(f"""
            <div class='ai-summary' style='margin-top:16px'>
              <div style='color:#c8dce8;line-height:1.75;font-size:.88rem'>
                {st.session_state.last_ai_summary}
              </div>
            </div>""", unsafe_allow_html=True)

        pattern = detect_pattern(st.session_state.history)
        if pattern:
            p_title, p_desc, p_color = pattern
            st.markdown(f"""
            <div style='margin-top:14px;background:linear-gradient(135deg,rgba(5,5,20,0.98),rgba(3,3,12,0.98));
                border:1px solid {p_color}33;border-left:3px solid {p_color};border-radius:3px;padding:12px 14px;
                box-shadow:0 0 20px {p_color}11,0 8px 24px rgba(0,0,0,0.5);
                clip-path:polygon(0 0,calc(100% - 8px) 0,100% 8px,100% 100%,8px 100%,0 calc(100% - 8px))'>
              <div style='font-family:Exo 2,sans-serif;font-size:.7rem;font-weight:700;
                  color:{p_color};letter-spacing:3px'>{p_title}</div>
              <div style='font-size:.78rem;color:#8aacc8;margin-top:5px;line-height:1.5'>{p_desc}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("⬡  RESET SESSION", key="btn_reset"):
            for k, v in defaults.items():
                st.session_state[k] = v if not isinstance(v, list) else []
            st.rerun()


with tab2:
    st.markdown("""
    <div class='section-header'>
      <span class='section-header-text'>Signal Waterfall / Spectrogram</span>
      <div class='section-header-line'></div>
    </div>
    <div style='font-family:Space Mono,monospace;font-size:.68rem;color:#1e4a6a;margin-bottom:12px'>
      Each row = one scan. Color intensity = signal power per frequency bin. Right stripe = classification.
    </div>""", unsafe_allow_html=True)

    wf_data = st.session_state.waterfall_data
    if not wf_data:
        st.info("No scans yet — run a scan or start Live Monitoring to populate the waterfall.")
    else:
        rows_js   = json.dumps([r["row"]   for r in wf_data])
        labels_js = json.dumps([r["label"] for r in wf_data])
        times_js  = json.dumps([r["time"]  for r in wf_data])

        wf_html = f"""<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#04060b;padding:12px;font-family:monospace}}
canvas{{border:1px solid #0d2035;border-radius:4px;width:100%;display:block;
  box-shadow:0 8px 32px rgba(0,0,0,0.6),0 0 0 1px rgba(0,229,204,0.05)}}
.axis{{display:flex;justify-content:space-between;font-size:9px;color:#1e4a6a;
  margin-top:5px;padding:0 2px;letter-spacing:1px}}
.legend{{display:flex;align-items:center;gap:10px;margin-top:10px;font-size:10px;color:#3a5a7a}}
.grad{{width:140px;height:10px;border-radius:2px;
  background:linear-gradient(90deg,#04060b,#0d1a3a,#003a8a,#00e5cc,#00ff88,#ffab00,#ff6d00,#ff1744);
  border:1px solid #0d2035}}
</style></head><body>
<canvas id="wf"></canvas>
<div class="axis"><span>70 MHz</span><span>93 MHz</span><span>115 MHz</span><span>138 MHz</span><span>160 MHz</span></div>
<div class="legend">
  <span style='color:#1e3a52'>POWER:</span>
  <span style='color:#0d1a3a'>LOW</span>
  <div class="grad"></div>
  <span style='color:#ff1744'>HIGH</span>
  &nbsp;&nbsp;
  <span style='background:#00e676;width:6px;height:10px;display:inline-block;border-radius:1px'></span><span style='margin-left:4px'>Friendly</span>
  <span style='background:#ffab00;width:6px;height:10px;display:inline-block;border-radius:1px;margin-left:8px'></span><span style='margin-left:4px'>Unknown</span>
  <span style='background:#ff1744;width:6px;height:10px;display:inline-block;border-radius:1px;margin-left:8px'></span><span style='margin-left:4px'>Hostile</span>
</div>
<script>
const cv=document.getElementById('wf');
const rows={rows_js};
const labels={labels_js};
const COLS=64,ROWS=rows.length;
const PW=Math.max(9,Math.floor(820/COLS));
const PH=Math.max(10,Math.min(20,Math.floor(420/Math.max(1,ROWS))));
cv.width=COLS*PW+6; cv.height=ROWS*PH;
const ctx=cv.getContext('2d');
function powerToColor(p){{
  // Deep space → teal → green → amber → red
  if(p < 0.15) {{
    const t=p/0.15;
    return `rgba(${{Math.floor(4+t*8)}},${{Math.floor(6+t*15)}},${{Math.floor(11+t*45)}},0.95)`;
  }} else if(p < 0.4) {{
    const t=(p-0.15)/0.25;
    const r=Math.floor(12+t*0);
    const g=Math.floor(21+t*209);
    const b=Math.floor(56+t*146);
    return `rgba(${{r}},${{g}},${{b}},0.95)`;
  }} else if(p < 0.65) {{
    const t=(p-0.4)/0.25;
    const r=Math.floor(0+t*255);
    const g=Math.floor(229-t*58);
    const b=Math.floor(204-t*204);
    return `rgba(${{r}},${{g}},${{b}},0.95)`;
  }} else if(p < 0.85) {{
    const t=(p-0.65)/0.2;
    return `rgba(255,${{Math.floor(171-t*62)}},0,0.95)`;
  }} else {{
    const t=(p-0.85)/0.15;
    return `rgba(255,${{Math.floor(109-t*86)}},${{Math.floor(0+t*68)}},0.95)`;
  }}
}}
ctx.clearRect(0,0,cv.width,cv.height);
for(let row=0;row<ROWS;row++){{
  for(let col=0;col<COLS;col++){{
    ctx.fillStyle=powerToColor(rows[row][col]);
    ctx.fillRect(col*PW,row*PH,PW-1,PH-1);
  }}
  // Classification stripe (3px)
  const lc={{"Friendly":"#00e676","Hostile":"#ff1744","Unknown":"#ffab00"}}[labels[row]]||"#00e5cc";
  ctx.fillStyle=lc;
  ctx.fillRect(COLS*PW+1,row*PH,4,PH-1);
  // Row glow for hostile
  if(labels[row]==="Hostile"){{
    ctx.fillStyle='rgba(255,23,68,0.06)';
    ctx.fillRect(0,row*PH,COLS*PW,PH);
  }}
}}
// Scan line
ctx.fillStyle='rgba(0,229,204,0.06)';ctx.fillRect(0,0,2,cv.height);
</script></body></html>"""
        components.html(wf_html, height=max(320, min(520, len(wf_data) * 20 + 100)), scrolling=True)


with tab3:
    st.markdown("""
    <div class='section-header'>
      <span class='section-header-text'>Signal Origin — Tactical Geo Map</span>
      <div class='section-header-line'></div>
    </div>
    <div style='font-family:Space Mono,monospace;font-size:.68rem;color:#1e4a6a;margin-bottom:12px'>
      Estimated signal origin locations. Fictional battlefield coordinates derived from frequency triangulation model.
    </div>""", unsafe_allow_html=True)

    geo = st.session_state.geo_points
    if not geo:
        st.info("No geo data yet — run scans to populate the map.")
    else:
        geo_js = json.dumps(geo)
        map_html = f"""<!DOCTYPE html><html><head>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{margin:0;padding:0}}
body{{background:#04060b}}
#map{{width:100%;height:480px;background:#04060b}}
.leaflet-tile{{filter:invert(1) hue-rotate(195deg) brightness(0.35) saturate(0.4) contrast(1.1)}}
.leaflet-container{{background:#04060b}}
.custom-tooltip{{
  background:rgba(4,6,11,0.97) !important;
  border:1px solid #0d2035 !important;
  color:#c0d8e8 !important;
  font-family:'Space Mono',monospace !important;
  font-size:11px !important;
  padding:7px 10px !important;
  border-radius:3px !important;
  box-shadow:0 4px 20px rgba(0,0,0,0.7) !important;
}}
.leaflet-popup-content-wrapper {{
  background:rgba(4,6,11,0.97) !important;
  border:1px solid #0d2035 !important;
  border-radius:4px !important;
  box-shadow:0 8px 32px rgba(0,0,0,0.8) !important;
}}
.leaflet-popup-tip {{ background:rgba(4,6,11,0.97) !important; }}
</style></head><body>
<div id="map"></div>
<script>
const geo={geo_js};
const map=L.map('map',{{zoomControl:true,attributionControl:false}}).setView([33,42],5);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
const colors={{"Friendly":"#00e676","Hostile":"#ff1744","Unknown":"#ffab00"}};

// Grid overlay
for(let lat=20;lat<=50;lat+=5){{
  L.polyline([[lat,-10],[lat,75]],{{color:'rgba(0,229,204,0.06)',weight:0.8,dashArray:'3,12'}}).addTo(map);
}}
for(let lon=20;lon<=75;lon+=5){{
  L.polyline([[15,lon],[55,lon]],{{color:'rgba(0,229,204,0.06)',weight:0.8,dashArray:'3,12'}}).addTo(map);
}}

geo.forEach((p,i)=>{{
  const c=colors[p.label]||"#00e5cc";
  const isLatest=i===0;
  const r=isLatest?11:7;
  const circle=L.circleMarker([p.lat,p.lon],{{
    radius:r, color:c, fillColor:c,
    fillOpacity:isLatest?0.85:0.35,
    weight:isLatest?2:1,
    opacity:isLatest?1:0.7,
  }}).addTo(map);
  circle.bindTooltip(
    `<b style="color:${{c}};letter-spacing:2px">${{p.label}}</b><br>
     <span style="color:#4a7a9a">${{p.freq.toFixed(1)}} MHz &nbsp;|&nbsp; ${{p.time}}</span><br>
     <span style="color:#3a5a7a">${{p.name}}</span>`,
    {{className:'custom-tooltip',permanent:false,direction:'top'}}
  );
  if(isLatest) circle.openTooltip();
  // Pulse ring for hostile
  if(p.label==="Hostile" && isLatest){{
    const pulse=L.circleMarker([p.lat,p.lon],{{
      radius:20,color:'#ff1744',fillOpacity:0,weight:1,opacity:0.4
    }}).addTo(map);
  }}
}});
</script></body></html>"""
        components.html(map_html, height=500, scrolling=False)

        head = log_row_html([("TIME", "#1e3a52"), ("LOCATION", "#1e3a52"), ("LAT/LON", "#1e3a52"), ("FREQ", "#1e3a52"), ("CLASS", "#1e3a52")], is_header=True)
        rows = head
        for p in geo[:15]:
            rows += log_row_html([
                (p["time"], "#2a4a6a"),
                (p["name"], "#7aaac8"),
                (f"{p['lat']:.3f}, {p['lon']:.3f}", "#3a5a7a"),
                (f"{p['freq']:.1f} MHz", "#00e5cc"),
                (p["label"], label_color(p["label"])),
            ])
        st.markdown(log_container(rows, 220), unsafe_allow_html=True)


with tab4:
    st.markdown("""
    <div class='section-header'>
      <span class='section-header-text'>Real-Time Spectrum Monitor</span>
      <div class='section-header-line'></div>
    </div>""", unsafe_allow_html=True)

    c_chart, c_live = st.columns([2, 1])
    with c_chart:
        conf_ph = st.empty()
    with c_live:
        status_ph = st.empty()
    feed_ph   = st.empty()
    pattern_ph = st.empty()


    spec_ph = st.empty()

    run_live = st.toggle("⬡  START LIVE MONITORING", key="live_toggle")

    if run_live:
        for _ in range(120):
            if not st.session_state.get("live_toggle", False):
                break
            lf  = random.uniform(FREQ_MIN, FREQ_MAX)
            ls  = random.uniform(0.3, 1.0)
            ln  = random.uniform(0.0, 0.4)
            ll, lc2 = classify_signal(lf, ls, ln)
            la  = defense_action(ll)
            record_scan(lf, ls, ln, ll, lc2, la)

           
            if len(st.session_state.conf_series) > 1:
                conf_ph.line_chart(
                    pd.DataFrame({"Confidence %": st.session_state.conf_series}),
                    height=200,
                    use_container_width=True,
                )

            live_row = []
            for i in range(64):
                bin_freq = FREQ_MIN + (FREQ_MAX - FREQ_MIN) * i / 64
                dist = abs(bin_freq - lf)
                power = ls * math.exp(-dist / 8_000_000) + ln * random.uniform(0, 1) * 0.3
                live_row.append(min(1.0, power))
            live_row_js = json.dumps(live_row)
            llc = label_color(ll)
            spec_ph.markdown(f"""
            <div style='background:#04060b;border:1px solid #0d2035;border-radius:4px;
                padding:12px;margin-bottom:10px;box-shadow:0 8px 24px rgba(0,0,0,0.5)'>
              <div style='font-size:.62rem;letter-spacing:3px;color:#1e4a6a;
                  font-family:Exo 2,sans-serif;font-weight:700;margin-bottom:8px'>
                LIVE SPECTRUM — {freq_to_mhz(lf):.1f} MHz
              </div>
              <div style='display:flex;align-items:flex-end;gap:1px;height:60px'>
                {''.join(f"<div style='flex:1;height:{int(live_row[i]*100)}%;background:linear-gradient(180deg,{llc},{llc}44);border-radius:1px 1px 0 0;min-height:2px;transition:height 0.3s'></div>" for i in range(64))}
              </div>
              <div style='display:flex;justify-content:space-between;font-size:.6rem;
                  color:#1e3a52;font-family:Space Mono,monospace;margin-top:4px'>
                <span>70 MHz</span><span style='color:{llc}'>{freq_to_mhz(lf):.1f} MHz</span><span>160 MHz</span>
              </div>
            </div>""", unsafe_allow_html=True)

            tc2 = threat_color(st.session_state.threat_level)
            status_ph.markdown(f"""
            <div class='metric-card'>
              <div class='metric-lbl'>LIVE SIGNAL</div>
              <div class='metric-val' style='color:{llc};font-size:1.4rem;margin:6px 0'>{ll}</div>
              <div style='font-family:Space Mono,monospace;font-size:.72rem;color:#00e5cc'>{lc2:.1f}%</div>
              <div style='font-family:Space Mono,monospace;font-size:.68rem;color:{tc2};margin-top:4px'>
                THREAT: {st.session_state.threat_level}%
              </div>
              <div style='font-family:Space Mono,monospace;font-size:.65rem;color:#1e4a6a;margin-top:3px'>
                {freq_to_mhz(lf):.1f} MHz
              </div>
            </div>""", unsafe_allow_html=True)

            head = log_row_html([("TIME", "#1e3a52"), ("FREQ", "#1e3a52"), ("STR", "#1e3a52"), ("CLASS", "#1e3a52"), ("CONF", "#1e3a52")], is_header=True)
            rows_h = head
            for entry in st.session_state.history[:12]:
                ts2, ef, es, en, el, ec, ea, eb = entry
                rows_h += log_row_html([
                    (ts2, "#2a4a6a"), (f"{ef:.2f} MHz", "#7aaac8"),
                    (f"{es:.2f}", "#3a5a7a"), (el, label_color(el)),
                    (f"{ec:.1f}%", "#00e5cc")
                ])
            feed_ph.markdown(log_container(rows_h, 260), unsafe_allow_html=True)

            pat = detect_pattern(st.session_state.history)
            if pat:
                p_t, p_d, p_c = pat
                pattern_ph.markdown(f"""
                <div style='background:rgba(5,5,20,0.98);border:1px solid {p_c}33;border-left:3px solid {p_c};
                    border-radius:3px;padding:10px 14px;margin-top:10px'>
                  <div style='font-family:Exo 2,sans-serif;font-size:.68rem;font-weight:700;
                      color:{p_c};letter-spacing:3px'>{p_t}</div>
                  <div style='font-size:.75rem;color:#8aacc8;margin-top:4px'>{p_d}</div>
                </div>""", unsafe_allow_html=True)
            time.sleep(1)


with tab5:
    st.markdown("""
    <div class='section-header'>
      <span class='section-header-text'>Threat Timeline & Heatmap</span>
      <div class='section-header-line'></div>
    </div>""", unsafe_allow_html=True)

    tl_data = st.session_state.threat_timeline
    hist_data = st.session_state.history

    if not tl_data:
        st.info("No data yet — run scans to build the threat timeline.")
    else:
        tl_js = json.dumps(tl_data)
        hist_js = json.dumps([
            {"freq": r[1], "strength": r[2], "label": r[4]}
            for r in hist_data[:80]
        ])

        timeline_html = f"""<!DOCTYPE html><html><head>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#04060b;padding:14px;font-family:monospace;color:#3a5a7a}}
.panel{{background:#070c14;border:1px solid #0d2035;border-radius:4px;
  padding:14px;margin-bottom:14px;box-shadow:0 8px 32px rgba(0,0,0,0.5)}}
.panel-title{{font-size:10px;letter-spacing:3px;color:#1e4a6a;margin-bottom:10px;
  font-family:'Exo 2',sans-serif;font-weight:700;text-transform:uppercase}}
canvas{{width:100%;display:block}}
</style></head><body>

<div class='panel'>
  <div class='panel-title'>Threat Index Over Time</div>
  <canvas id="tl" height="120"></canvas>
</div>

<div class='panel'>
  <div class='panel-title'>Frequency × Strength Heatmap (Signal Density)</div>
  <canvas id="hm" height="150"></canvas>
</div>

<div class='panel'>
  <div class='panel-title'>Signal Classification Timeline</div>
  <canvas id="cl" height="80"></canvas>
</div>

<script>
const tlData={tl_js};
const histData={hist_js};

function drawAll() {{
  // Use body width minus padding; fall back to 700 if layout not ready yet
  const W = Math.max(300, (document.body.clientWidth || document.documentElement.clientWidth || 740) - 28);

// ── THREAT LINE CHART ──
(function(){{
  const cv=document.getElementById('tl');
  cv.width=W; cv.height=120;
  const ctx=cv.getContext('2d');
  const n=tlData.length;
  if(n<2) return;
  const vals=tlData.map(d=>d.threat);
  const minV=0,maxV=100;
  const pad={{t:10,r:40,b:20,l:40}};
  const cw=W-pad.l-pad.r,ch=120-pad.t-pad.b;
  ctx.clearRect(0,0,W,120);

  // Grid
  [0,25,50,75,100].forEach(v=>{{
    const y=pad.t+ch-(v/maxV)*ch;
    ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(pad.l+cw,y);
    ctx.strokeStyle=v===75?'rgba(255,23,68,0.2)':'rgba(0,229,204,0.06)';ctx.lineWidth=1;ctx.stroke();
    ctx.fillStyle='rgba(0,229,204,0.25)';ctx.font='8px monospace';ctx.textAlign='right';
    ctx.fillText(v+'%',pad.l-4,y+3);
  }});

  // Fill gradient
  const grad=ctx.createLinearGradient(0,pad.t,0,pad.t+ch);
  grad.addColorStop(0,'rgba(255,23,68,0.3)');
  grad.addColorStop(0.4,'rgba(255,109,0,0.15)');
  grad.addColorStop(1,'rgba(0,229,204,0.02)');
  ctx.beginPath();
  ctx.moveTo(pad.l,pad.t+ch);
  vals.forEach((v,i)=>{{
    const x=pad.l+(i/(n-1))*cw;
    const y=pad.t+ch-((v-minV)/(maxV-minV))*ch;
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
  }});
  ctx.lineTo(pad.l+cw,pad.t+ch);ctx.closePath();
  ctx.fillStyle=grad;ctx.fill();

  // Line
  ctx.beginPath();
  vals.forEach((v,i)=>{{
    const x=pad.l+(i/(n-1))*cw;
    const y=pad.t+ch-((v-minV)/(maxV-minV))*ch;
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y);
  }});
  // Color based on latest value
  const latest=vals[vals.length-1];
  const lc=latest>=75?'#ff1744':latest>=50?'#ff6d00':latest>=30?'#ffab00':'#00e676';
  ctx.strokeStyle=lc;ctx.lineWidth=2;ctx.shadowBlur=6;ctx.shadowColor=lc;ctx.stroke();
  ctx.shadowBlur=0;

  // Danger zone line
  const dangerY=pad.t+ch-(75/100)*ch;
  ctx.beginPath();ctx.moveTo(pad.l,dangerY);ctx.lineTo(pad.l+cw,dangerY);
  ctx.strokeStyle='rgba(255,23,68,0.35)';ctx.lineWidth=1;ctx.setLineDash([4,6]);ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle='rgba(255,23,68,0.5)';ctx.font='8px monospace';ctx.textAlign='left';
  ctx.fillText('CRITICAL',pad.l+cw+2,dangerY+3);

  // Dots for label events
  tlData.forEach((d,i)=>{{
    if(d.label==="Hostile"){{
      const x=pad.l+(i/(n-1))*cw;
      const y=pad.t+ch-((d.threat/100))*ch;
      ctx.beginPath();ctx.arc(x,y,3,0,Math.PI*2);
      ctx.fillStyle='#ff1744';ctx.shadowBlur=8;ctx.shadowColor='#ff1744';ctx.fill();ctx.shadowBlur=0;
    }}
  }});
}})();

// ── HEATMAP ──
(function(){{
  const cv=document.getElementById('hm');
  cv.width=W; cv.height=150;
  const ctx=cv.getContext('2d');
  const FREQ_BINS=60, STR_BINS=20;
  const grid=Array(STR_BINS).fill(null).map(()=>Array(FREQ_BINS).fill(0));
  const lcount={{"Friendly":0,"Unknown":0,"Hostile":0}};
  histData.forEach(d=>{{
    const fx=Math.floor(((d.freq-70)/90)*FREQ_BINS);
    const sy=Math.floor(d.strength*STR_BINS);
    if(fx>=0&&fx<FREQ_BINS&&sy>=0&&sy<STR_BINS) grid[Math.min(STR_BINS-1,sy)][fx]++;
    if(lcount[d.label]!==undefined) lcount[d.label]++;
  }});
  const maxVal=Math.max(1,...grid.flat());
  const cellW=W/FREQ_BINS, cellH=150/STR_BINS;
  for(let sy=0;sy<STR_BINS;sy++){{
    for(let fx=0;fx<FREQ_BINS;fx++){{
      const v=grid[STR_BINS-1-sy][fx]/maxVal;
      if(v>0){{
        const r=Math.floor(v*255);
        const g=Math.floor((1-v)*100+v*23);
        const b=Math.floor((1-v)*204);
        ctx.fillStyle=`rgba(${{r}},${{g}},${{b}},${{0.1+v*0.9}})`;
        ctx.fillRect(fx*cellW,sy*cellH,cellW-1,cellH-1);
        if(v>0.5){{
          ctx.fillStyle=`rgba(255,255,255,${{(v-0.5)*0.3}})`;
          ctx.fillRect(fx*cellW,sy*cellH,cellW-1,cellH/2);
        }}
      }}
    }}
  }}
  // Axes
  ctx.fillStyle='rgba(0,229,204,0.3)';ctx.font='8px monospace';ctx.textAlign='center';
  ['70M','93M','115M','137M','160M'].forEach((l,i)=>{{
    ctx.fillText(l,i*(W/4),148);
  }});
  ctx.textAlign='left';
  ctx.fillText('1.0',2,10);ctx.fillText('0.5',2,80);ctx.fillText('0.0',2,148);

  // Band dividers
  [18/90,38/90,67/90].forEach(p=>{{
    ctx.beginPath();ctx.moveTo(p*W,0);ctx.lineTo(p*W,150);
    ctx.strokeStyle='rgba(0,229,204,0.12)';ctx.lineWidth=1;ctx.setLineDash([3,5]);ctx.stroke();
    ctx.setLineDash([]);
  }});
}})();

// ── CLASSIFICATION TIMELINE ──
(function(){{
  const cv=document.getElementById('cl');
  cv.width=W; cv.height=80;
  const ctx=cv.getContext('2d');
  const n=histData.length;
  if(!n) return;
  const bw=Math.max(2,W/n);
  histData.slice().reverse().forEach((d,i)=>{{
    const c={{"Friendly":"#00e676","Unknown":"#ffab00","Hostile":"#ff1744"}}[d.label]||"#00e5cc";
    const h=20+d.strength*50;
    ctx.fillStyle=c+'aa';
    ctx.fillRect(i*bw,80-h,bw-1,h);
    // Top glow
    ctx.fillStyle=c;
    ctx.fillRect(i*bw,80-h,bw-1,2);
  }});
  // Zero line
  ctx.beginPath();ctx.moveTo(0,79);ctx.lineTo(W,79);
  ctx.strokeStyle='rgba(0,229,204,0.15)';ctx.lineWidth=1;ctx.stroke();
}})();
}} // end drawAll

// Run immediately, then again after layout settles
drawAll();
setTimeout(drawAll, 100);
setTimeout(drawAll, 400);
window.addEventListener('load', drawAll);
</script></body></html>"""
        components.html(timeline_html, height=560, scrolling=False)

       
        if st.session_state.threat_timeline:
            avg_t = sum(d["threat"] for d in tl_data) / len(tl_data)
            max_t = max(d["threat"] for d in tl_data)
            h_spikes = sum(1 for d in tl_data if d["threat"] >= 75)
            c1, c2, c3, c4 = st.columns(4)
            for col, val, lbl, clr in [
                (c1, f"{avg_t:.0f}%", "AVG THREAT",    "#00e5cc"),
                (c2, f"{max_t:.0f}%", "PEAK THREAT",   threat_color(max_t)),
                (c3, h_spikes,        "CRITICAL SPIKES","#ff1744"),
                (c4, len(tl_data),    "DATA POINTS",    "#7aaac8"),
            ]:
                col.markdown(f"""
                <div class='metric-card' style='padding:12px'>
                  <div class='metric-val' style='color:{clr};font-size:1.4rem'>{val}</div>
                  <div class='metric-lbl'>{lbl}</div>
                </div>""", unsafe_allow_html=True)


with tab6:
    st.markdown("""
    <div class='section-header'>
      <span class='section-header-text'>Attack Scenario Simulator</span>
      <div class='section-header-line'></div>
    </div>""", unsafe_allow_html=True)

    c_s1, c_s2 = st.columns(2)
    with c_s1:
        scenario = st.selectbox("Attack Scenario", [
            "Coordinated Jamming (137–160 MHz)",
            "Frequency Hopping Burst",
            "Low & Slow Infiltration (70–108 MHz)",
            "Broadband Flood (Full Spectrum)",
            "IFF Spoofing Probe",
        ])
        intensity = st.select_slider("Intensity", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
    with c_s2:
        waves  = st.number_input("Signal Bursts", min_value=3, max_value=25, value=8)
        ai_sim = st.checkbox("Generate AI Threat Brief after sim", value=True)

    sim_ph2    = st.empty()
    chart_ph3  = st.empty()
    spec_sim_ph = st.empty()
    ai_ph      = st.empty()

    if st.button("⬡  LAUNCH SIMULATION", key="btn_sim"):
        st.session_state.threat_level = 0
        st.session_state.alert_active = False
        base_str = {"LOW": 0.35, "MEDIUM": 0.6, "HIGH": 0.82, "CRITICAL": 0.95}[intensity]
        ranges   = {
            "Coordinated Jamming (137–160 MHz)":    (137_000_000, 160_000_000),
            "Frequency Hopping Burst":              (70_000_000,  160_000_000),
            "Low & Slow Infiltration (70–108 MHz)": (70_000_000,  108_000_000),
            "Broadband Flood (Full Spectrum)":      (70_000_000,  160_000_000),
            "IFF Spoofing Probe":                   (108_000_000, 137_000_000),
        }
        fmin2, fmax2 = ranges[scenario]
        sim_log = []

        for wave in range(int(waves)):
            sf = random.uniform(fmin2, fmax2)
            ss = random.uniform(base_str, 1.0)
            sn = random.uniform(0.0, 0.2)
            sl, sc = classify_signal(sf, ss, sn)
            sa = defense_action(sl)
            record_scan(sf, ss, sn, sl, sc, sa)
            sim_log.insert(0, (wave + 1, freq_to_mhz(sf), ss, sl, sc, sa))

            head = log_row_html([
                ("WAVE", "#1e3a52"), ("FREQ", "#1e3a52"), ("STR", "#1e3a52"),
                ("CLASS", "#1e3a52"), ("CONF", "#1e3a52"), ("ACTION", "#1e3a52")
            ], is_header=True)
            rows3 = head
            for w, ef2, es2, el2, ec2, ea2 in sim_log:
                rows3 += log_row_html([
                    (f"W{w:02d}", "#2a4a6a"), (f"{ef2:.1f} MHz", "#7aaac8"),
                    (f"{es2:.2f}", "#3a5a7a"), (el2, label_color(el2)),
                    (f"{ec2:.1f}%", "#00e5cc"), (ea2, label_color(el2))
                ])
            sim_ph2.markdown(log_container(rows3, 340), unsafe_allow_html=True)

            # Mini spectrum
            sim_row = []
            for i in range(64):
                bin_freq = FREQ_MIN + (FREQ_MAX - FREQ_MIN) * i / 64
                dist = abs(bin_freq - sf)
                power = ss * math.exp(-dist / 8_000_000) + sn * random.uniform(0, 1) * 0.3
                sim_row.append(min(1.0, power))
            slc = label_color(sl)
            spec_sim_ph.markdown(f"""
            <div style='background:#04060b;border:1px solid #0d2035;border-radius:4px;
                padding:10px;margin-top:8px'>
              <div style='font-size:.6rem;letter-spacing:3px;color:#1e4a6a;
                  font-family:Exo 2,sans-serif;font-weight:700;margin-bottom:6px'>
                SIM WAVE {wave+1:02d} — {freq_to_mhz(sf):.1f} MHz — {sl.upper()} — THREAT: {st.session_state.threat_level}%
              </div>
              <div style='display:flex;align-items:flex-end;gap:1px;height:48px'>
                {''.join(f"<div style='flex:1;height:{int(sim_row[i]*100)}%;background:{slc}88;border-radius:1px 1px 0 0;min-height:2px'></div>" for i in range(64))}
              </div>
            </div>""", unsafe_allow_html=True)

            if len(st.session_state.conf_series) > 1:
                chart_ph3.line_chart(
                    pd.DataFrame({"Confidence %": st.session_state.conf_series}),
                    height=160,
                )
            time.sleep(0.35)

        if ai_sim:
            h_count  = sum(1 for _, _, _, l, _, _ in sim_log if l == "Hostile")
            top_freq = sim_log[0][1] if sim_log else 100.0
            brief    = call_gemini(
                st.session_state.gemini_api_key,
                top_freq, base_str, 0.1,
                "Hostile", 88.0, "BLOCK",
                get_band_name(top_freq * 1_000_000)
            )
            tl3 = st.session_state.threat_level
            tc3 = threat_color(tl3)
            ai_ph.markdown(f"""
            <div style='background:linear-gradient(135deg,rgba(18,4,6,0.98),rgba(12,3,4,0.98));
                border:2px solid {tc3}44;border-top:2px solid {tc3}88;
                border-radius:4px;padding:18px 20px;margin-top:14px;
                box-shadow:0 0 40px {tc3}15,0 12px 40px rgba(0,0,0,0.7);
                clip-path:polygon(0 0,calc(100% - 14px) 0,100% 14px,100% 100%,14px 100%,0 calc(100% - 14px))'>
              <div style='font-family:Exo 2,sans-serif;font-size:.8rem;font-weight:700;
                  color:{tc3};letter-spacing:3px;margin-bottom:12px'>
                ◈ SIMULATION COMPLETE — {int(waves)} BURSTS &nbsp;|&nbsp;
                {h_count} HOSTILE &nbsp;|&nbsp; THREAT INDEX: {tl3}%
              </div>
              <div class='ai-summary' style='border-color:{tc3}44;border-left-color:{tc3}'>
                <div style='color:#c8dce8'>{brief}</div>
              </div>
            </div>""", unsafe_allow_html=True)


with tab7:
    st.markdown("""
    <div class='section-header'>
      <span class='section-header-text'>Full Event Log</span>
      <div class='section-header-line'></div>
    </div>""", unsafe_allow_html=True)

    c_f1, c_f2, c_f3, c_f4 = st.columns(4)
    filter_label = c_f1.selectbox("Classification", ["ALL", "Friendly", "Unknown", "Hostile"])
    filter_band  = c_f2.selectbox("Band",           ["ALL", "VHF-LOW", "FM-BAND", "VHF-HIGH", "MILITARY"])
    sort_order   = c_f3.selectbox("Sort",           ["Newest First", "Oldest First"])
    max_rows     = c_f4.slider("Max Rows", 10, 300, 80)

    log_data = st.session_state.history
    if filter_label != "ALL": log_data = [r for r in log_data if r[4] == filter_label]
    if filter_band  != "ALL": log_data = [r for r in log_data if len(r) > 7 and r[7] == filter_band]
    if sort_order == "Oldest First": log_data = list(reversed(log_data))
    log_data = log_data[:max_rows]

    if st.session_state.history:
        total  = len(st.session_state.history)
        h_all  = sum(1 for r in st.session_state.history if r[4] == "Hostile")
        avg_c  = sum(r[5] for r in st.session_state.history) / total
        c1, c2, c3, c4 = st.columns(4)
        for col, val, lbl, clr in [
            (c1, total,        "TOTAL RECORDS", "#00e5cc"),
            (c2, h_all,        "HOSTILE EVENTS","#ff1744"),
            (c3, f"{avg_c:.1f}%", "AVG CONFIDENCE","#7aaac8"),
            (c4, len(log_data),"SHOWING",       "#ffab00"),
        ]:
            col.markdown(f"""
            <div class='metric-card' style='padding:12px;margin-bottom:12px'>
              <div class='metric-val' style='color:{clr};font-size:1.5rem'>{val}</div>
              <div class='metric-lbl'>{lbl}</div>
            </div>""", unsafe_allow_html=True)

    if log_data:
        head = log_row_html([
            ("TIME", "#1e3a52"), ("FREQ", "#1e3a52"), ("STR", "#1e3a52"),
            ("NOISE", "#1e3a52"), ("BAND", "#1e3a52"), ("CLASS", "#1e3a52"), ("CONF", "#1e3a52")
        ], is_header=True)
        rows_l = head
        for row in log_data:
            ts3, ef3, es3, en3, el3, ec3, ea3 = row[:7]
            eb3 = row[7] if len(row) > 7 else "—"
            rows_l += log_row_html([
                (ts3, "#2a4a6a"), (f"{ef3:.2f} MHz", "#7aaac8"),
                (f"{es3:.2f}", "#3a5a7a"), (f"{en3:.2f}", "#3a5a7a"),
                (eb3, "#00e5cc"), (el3, label_color(el3)),
                (f"{ec3:.1f}%", "#00e5cc")
            ])
        st.markdown(log_container(rows_l, 500), unsafe_allow_html=True)

        df_exp = pd.DataFrame(
            [r[:7] + (r[7] if len(r) > 7 else "—",) for r in log_data],
            columns=["Time", "Freq_MHz", "Strength", "Noise", "Label", "Confidence", "Action", "Band"]
        )
        c_dl1, c_dl2 = st.columns(2)
        c_dl1.download_button("⬡  EXPORT CSV",  df_exp.to_csv(index=False).encode(),  "rf_sentinel_log.csv",  "text/csv")
        c_dl2.download_button("⬡  EXPORT JSON", df_exp.to_json(orient="records").encode(), "rf_sentinel_log.json", "application/json")
    else:
        st.info("No events match current filters. Run scans or start Live Monitoring.")
