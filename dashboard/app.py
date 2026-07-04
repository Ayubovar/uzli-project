"""
UZLI Dashboard — Uzbekistan Liquidity Index
Enterprise-quality Streamlit + Plotly dashboard for MBA portfolio project.

Data source : data/processed/uzli_final.csv  (read-only, never modified)
Run         : streamlit run dashboard/app.py
"""

import base64
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

# ── Page config — must be the very first Streamlit call ──────────────────────
st.set_page_config(
    page_title="UZLI Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "uzli_final.csv"
LOGO_PATH = Path(__file__).resolve().parent / "imrs_logo.jpg"

# ── Design tokens ─────────────────────────────────────────────────────────────
C = {
    "navy":          "#0B2545",
    "amber":         "#F4B400",
    "bg":            "#F5F7FA",
    "low":           "#E63946",
    "moderate":      "#F4A261",
    "high":          "#2A9D8F",
    "text":          "#1E293B",
    "muted":         "#64748B",
    "border":        "#E5E7EB",
    "volume_norm":   "#264653",
    "breadth_norm":  "#2A9D8F",
    "turnover_norm": "#E9C46A",
    "amihud_norm":   "#F4A261",
    "spread_norm":   "#E76F51",
}

# ── Metric weights (display reference only — no calculations here) ─────────
WEIGHTS = {
    "volume_norm":   0.25,
    "breadth_norm":  0.20,
    "turnover_norm": 0.25,
    "amihud_norm":   0.20,
    "spread_norm":   0.10,
}
NORM_COLS    = list(WEIGHTS.keys())
CONTRIB_COLS = [f"{m}_contrib" for m in NORM_COLS]

# ── Bilingual string table ────────────────────────────────────────────────────
STRINGS = {
    "en": {
        # Hero
        "page_title":    "Uzbekistan Liquidity Index (UZLI)",
        "subtitle":      "Composite Liquidity Benchmark for the Tashkent Stock Exchange",
        "eyebrow":       "Market Intelligence",
        "badge_years":   "2016 – 2026",
        "badge_days":    "2,373 Trading Days",
        "badge_sec":     "290 Listed Securities",
        # KPI cards
        "current_uzli":  "Current UZLI",
        "liq_level":     "Liquidity Level",
        "avg_30d":       "30-Day Average",
        "vs_prior":      "vs. prior 30 days",
        # Charts & table
        "chart_title":   "UZLI — Full History",
        "contrib_title": "Metric Contributions (Monthly Average)",
        "contrib_note":  "Each bar shows the weighted contribution of each metric to the monthly average UZLI score.",
        "table_title":   "Latest 30 Trading Days",
        # Sidebar
        "date_range":    "Date Range",
        "reset":         "Reset Filters",
        "about":         "About Project",
        "about_text": (
            "The Uzbekistan Liquidity Index (UZLI) is a composite indicator built from five "
            "Min-Max normalized metrics — volume, breadth, turnover, Amihud illiquidity, and "
            "bid-ask spread — each weighted and combined to produce a daily score on a 0–100 scale. "
            "Data covers the Tashkent Stock Exchange from November 2016 to June 2026."
        ),
        "download":      "Download CSV",
        # Labels
        "low":           "Low Liquidity",
        "moderate":      "Moderate Liquidity",
        "high":          "High Liquidity",
        # Empty state
        "empty_title":   "No Data Available",
        "empty_text":    "No trading days found in the selected period. Please adjust the date range.",
        # Chart annotations
        "ann_mod":       "Moderate",
        "ann_high":      "High",
        # Table columns
        "col_date":      "Date",
        "col_score":     "UZLI Score",
        "col_label":     "Liquidity Label",
        "col_vol":       "Volume",
        "col_breadth":   "Breadth",
        "col_turnover":  "Turnover",
        "col_amihud":    "Amihud",
        "col_spread":    "Spread",
        # Footer (kept for compatibility)
        "footer_source": "Data Source: Tashkent Stock Exchange",
        "footer_cover":  "Coverage: 2016 – 2026",
        "footer_author": "Created by: Project Author",
    },
    "uz": {
        # Hero
        "page_title":    "O'zbekiston Likvidlik Indeksi (UZLI)",
        "subtitle":      "Toshkent Fond Birjasi uchun Kompozit Likvidlik Ko'rsatkichi",
        "eyebrow":       "Bozor Tahlili",
        "badge_years":   "2016 – 2026",
        "badge_days":    "2 373 Savdo Kuni",
        "badge_sec":     "290 Qimmatli Qog'oz",
        # KPI cards
        "current_uzli":  "Joriy UZLI",
        "liq_level":     "Likvidlik Darajasi",
        "avg_30d":       "30 Kunlik O'rtacha",
        "vs_prior":      "oldingi 30 kun bilan",
        # Charts & table
        "chart_title":   "UZLI — To'liq Tarix",
        "contrib_title": "Metrik Hissalar (Oylik O'rtacha)",
        "contrib_note":  "Har bir ustun har bir metrikning oylik o'rtacha UZLI balliga tortilgan hissasini ko'rsatadi.",
        "table_title":   "Oxirgi 30 Ta Savdo Kuni",
        # Sidebar
        "date_range":    "Sana Oralig'i",
        "reset":         "Filtrlarni Tiklash",
        "about":         "Loyiha Haqida",
        "about_text": (
            "O'zbekiston Likvidlik Indeksi (UZLI) — beshta Min-Max normalangan metrikdan iborat "
            "kompozit ko'rsatkich: hajm, kenglik, aylanma, Amihud nolikvidligi va bid-ask spread. "
            "Har bir metrik tortilgan va birlashtiriladi, natijada kunlik 0–100 ball hosil bo'ladi. "
            "Ma'lumotlar 2016-yil noyabridan 2026-yil iyunigacha bo'lgan davrni qamrab oladi."
        ),
        "download":      "CSV Yuklab Olish",
        # Labels
        "low":           "Past Likvidlik",
        "moderate":      "O'rtacha Likvidlik",
        "high":          "Yuqori Likvidlik",
        # Empty state
        "empty_title":   "Ma'lumot Topilmadi",
        "empty_text":    "Tanlangan davr uchun savdo kunlari topilmadi. Iltimos, sana oralig'ini o'zgartiring.",
        # Chart annotations
        "ann_mod":       "O'rtacha",
        "ann_high":      "Yuqori",
        # Table columns
        "col_date":      "Sana",
        "col_score":     "UZLI Ball",
        "col_label":     "Likvidlik Yorlig'i",
        "col_vol":       "Hajm",
        "col_breadth":   "Kenglik",
        "col_turnover":  "Aylanma",
        "col_amihud":    "Amihud",
        "col_spread":    "Spread",
        # Footer (kept for compatibility)
        "footer_source": "Ma'lumot Manbai: Toshkent Fond Birjasi",
        "footer_cover":  "Qamrov: 2016 – 2026",
        "footer_author": "Yaratuvchi: Loyiha Muallifi",
    },
}

METRIC_DISPLAY = {
    "en": dict(zip(NORM_COLS, ["Volume", "Breadth", "Turnover", "Amihud", "Spread"])),
    "uz": dict(zip(NORM_COLS, ["Hajm", "Kenglik", "Aylanma", "Amihud", "Spread"])),
}


# ── Utilities ─────────────────────────────────────────────────────────────────

def label_color(label: str) -> str:
    lo = label.lower()
    if "low" in lo or "past" in lo:
        return C["low"]
    if "moderate" in lo or "o'rtacha" in lo:
        return C["moderate"]
    if "high" in lo or "yuqori" in lo:
        return C["high"]
    return C["navy"]


def translate_label(label: str, lang: str) -> str:
    s = STRINGS[lang]
    return {"Low Liquidity": s["low"], "Moderate Liquidity": s["moderate"],
            "High Liquidity": s["high"]}.get(label, label)


def load_logo_b64(path: Path) -> str | None:
    """
    Reads the logo file from disk at runtime and returns a base64 data URI.
    Returns None if the file does not exist or cannot be read.
    This is dynamic loading — the file is read from the filesystem each run,
    not hardcoded into the source.
    """
    if not path.exists():
        return None
    try:
        suffix = path.suffix.lower()
        mime   = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png"
        with open(path, "rb") as fh:
            encoded = base64.b64encode(fh.read()).decode()
        return f"data:{mime};base64,{encoded}"
    except Exception:
        return None


def sec_hdr(title: str) -> str:
    """Premium section header: amber accent bar + title + full-width rule."""
    return (
        '<div class="sec-header">'
        '  <span class="sec-accent"></span>'
        f' <span class="sec-title-text">{title}</span>'
        '  <div class="sec-rule"></div>'
        '</div>'
    )


# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    for col, w in WEIGHTS.items():
        df[f"{col}_contrib"] = df[col] * w
    return df


# ── CSS ───────────────────────────────────────────────────────────────────────

def apply_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Design system tokens ── */
    :root {
        --bg:         #F5F7FA;
        --navy:       #0B2545;
        --amber:      #F4B400;
        --positive:   #2A9D8F;
        --negative:   #E63946;
        --text:       #1E293B;
        --muted:      #64748B;
        --border:     #E5E7EB;
        --card:       #FFFFFF;
        --shadow-sm:  0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.06);
        --shadow-md:  0 4px 6px -1px rgba(15,23,42,0.07), 0 2px 4px -1px rgba(15,23,42,0.04);
        --shadow-lg:  0 10px 15px -3px rgba(15,23,42,0.08), 0 4px 6px -2px rgba(15,23,42,0.04);
        --font:       'Inter', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        --radius-sm:  8px;
        --radius:     12px;
        --radius-lg:  16px;
    }

    /* ── Base ── */
    html, body, [class*="css"] { font-family: var(--font) !important; }
    #MainMenu, footer { visibility: hidden; }
    header            { display: none !important; }
    .stApp                      { background-color: var(--bg); }
    .block-container {
        padding-top:    0.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1360px;
    }

    /* ─────────────────────────── SIDEBAR ─────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: var(--navy) !important;
        min-width: 240px !important;
        max-width: 260px !important;
    }
    [data-testid="stSidebar"] * {
        font-family: var(--font) !important;
        /* color intentionally omitted here: applying color:#fff !important on the *
           wildcard overrides the color:transparent that Streamlit uses to hide
           internal accessibility/utility nodes, making them render as visible white
           text on top of the real label and producing the "arrbo…tProject" overlap */
    }
    /* Restrict white-text override to known visible text containers only */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }

    /* Language radio — pill style */
    [data-testid="stSidebar"] .stRadio > div  { flex-direction: row; gap: 6px; }
    [data-testid="stSidebar"] .stRadio label  {
        background: rgba(255,255,255,0.07);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.77rem !important;
        font-weight: 500 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.14);
        transition: all 0.18s ease;
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(244,180,0,0.13);
        border-color: var(--amber);
    }

    /* Reset button */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: 1.5px solid rgba(244,180,0,0.65);
        color: var(--amber) !important;
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-size: 0.77rem;
        width: 100%;
        padding: 8px 12px;
        transition: all 0.18s ease;
        letter-spacing: 0.01em;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--amber);
        color: var(--navy) !important;
        border-color: var(--amber);
        transform: translateY(-1px);
    }

    /* Download button */
    [data-testid="stSidebar"] .stDownloadButton > button {
        background: rgba(255,255,255,0.05);
        border: 1.5px solid rgba(255,255,255,0.18);
        color: rgba(255,255,255,0.82) !important;
        border-radius: var(--radius-sm);
        font-size: 0.77rem;
        font-weight: 500;
        width: 100%;
        padding: 8px 12px;
        transition: all 0.18s ease;
    }
    [data-testid="stSidebar"] .stDownloadButton > button:hover {
        background: rgba(255,255,255,0.11);
        border-color: rgba(255,255,255,0.36);
    }

    /* Date input */
    [data-testid="stSidebar"] .stDateInput input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #fff !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.77rem !important;
        font-family: var(--font) !important;
    }

    /* Expander — use data-testid (stable) instead of .stExpander class name */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        border: 1px solid rgba(255,255,255,0.11) !important;
        border-radius: var(--radius-sm) !important;
        background: rgba(255,255,255,0.03) !important;
    }
    /* Apply font properties to summary only — no color here, because cascading
       color:#fff to span children overrides the color:transparent Streamlit sets
       on its hidden accessibility nodes, revealing them and causing label overlap. */
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        font-size: 0.79rem !important;
        font-weight: 500 !important;
    }
    /* Target only the visible <p> label — color is safe here. */
    [data-testid="stSidebar"] [data-testid="stExpander"] summary p {
        color: #FFFFFF !important;
    }

    /* Sidebar helpers */
    .sb-label {
        font-size: 0.59rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.36) !important;
        display: block;
        margin-bottom: 9px;
    }
    .sb-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.07);
        margin: 18px 0;
    }

    /* ─────────────────────────── HERO ────────────────────────────────────── */
    .hero {
        padding: 4px 0 16px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 20px;
    }
    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--amber);
        margin-bottom: 16px;
    }
    .hero-eyebrow::before {
        content: '';
        display: inline-block;
        width: 26px;
        height: 3px;
        background: var(--amber);
        border-radius: 2px;
        flex-shrink: 0;
    }
    .hero-title {
        font-size: 2.55rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.03em;
        margin: 0 0 10px 0;
        line-height: 1.06;
    }
    .hero-subtitle {
        font-size: 1.02rem;
        font-weight: 400;
        color: var(--muted);
        max-width: 640px;
        line-height: 1.55;
        margin: 0 0 22px 0;
    }
    .hero-badges { display: flex; flex-wrap: wrap; gap: 8px; }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: #EEF2F7;
        color: var(--text);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        transition: opacity 0.18s ease;
    }
    .hero-badge:hover { opacity: 0.7; }

    /* ─────────────────────────── KPI CARDS ───────────────────────────────── */
    .kpi-card {
        background: var(--card);
        border-radius: var(--radius);
        padding: 26px 24px 20px 24px;
        box-shadow: var(--shadow-md);
        border-left: 4px solid var(--amber);
        position: relative;
        transition: transform 0.22s ease, box-shadow 0.22s ease;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
    }
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 10px;
    }
    .kpi-label {
        font-size: 0.62rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--muted);
        line-height: 1.2;
    }
    .kpi-icon {
        font-size: 1.15rem;
        opacity: 0.3;
        line-height: 1;
        flex-shrink: 0;
    }
    .kpi-value {
        font-size: 2.15rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.03em;
        line-height: 1;
    }
    .kpi-sub  { font-size: 0.71rem; color: var(--muted); margin-top: 8px; }
    .kpi-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.69rem;
        font-weight: 700;
        margin-top: 10px;
        letter-spacing: 0.04em;
    }
    .delta-up { color: #2A9D8F; font-size: 0.73rem; font-weight: 600; margin-top: 8px; }
    .delta-dn { color: #E63946; font-size: 0.73rem; font-weight: 600; margin-top: 8px; }

    /* ─────────────────────── SECTION HEADERS ─────────────────────────────── */
    .sec-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 20px 0 12px 0;
    }
    .sec-accent {
        display: inline-block;
        width: 3px;
        height: 20px;
        background: var(--amber);
        border-radius: 2px;
        flex-shrink: 0;
    }
    .sec-title-text {
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--text);
        white-space: nowrap;
        letter-spacing: -0.01em;
    }
    .sec-rule { flex: 1; height: 1px; background: var(--border); }

    /* ─────────────────────── CHART CONTAINERS ────────────────────────────── */
    [data-testid="stPlotlyChart"] {
        background: var(--card);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
        padding: 4px;
        margin-bottom: 4px;
        overflow: hidden;
    }

    /* ────────────────────────── DATA TABLE ───────────────────────────────── */
    [data-testid="stDataFrame"] {
        border-radius: var(--radius);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border);
        overflow: hidden;
        background: var(--card);
    }

    /* ────────────────────────── EMPTY STATE ──────────────────────────────── */
    .empty-state {
        background: var(--card);
        border-radius: var(--radius-lg);
        padding: 72px 32px;
        text-align: center;
        border: 1.5px dashed #CBD5E0;
        margin: 32px 0;
    }
    .empty-icon  { font-size: 3rem; margin-bottom: 16px; opacity: 0.45; }
    .empty-title { font-size: 1.1rem; font-weight: 700; color: var(--text); margin-bottom: 8px; }
    .empty-text  { color: var(--muted); font-size: 0.86rem; }

    /* ───────────────────────── AUTHOR CARD ───────────────────────────────── */
    .author-card {
        display: flex;
        align-items: center;
        gap: 28px;
        background: var(--card);
        border-radius: var(--radius-lg);
        padding: 28px 32px;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border);
        border-left: 4px solid var(--navy);
        margin-top: 52px;
        margin-bottom: 32px;
        flex-wrap: wrap;
        transition: box-shadow 0.22s ease, transform 0.22s ease;
    }
    .author-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    .author-logo-wrap {
        flex-shrink: 0;
        width: 96px;
        height: 96px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #F8FAFC;
        border-radius: var(--radius);
        overflow: hidden;
        border: 1px solid var(--border);
    }
    .author-logo-wrap img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 6px;
        display: block;
    }
    .author-logo-placeholder {
        font-size: 2.4rem;
        opacity: 0.4;
    }
    .author-info { flex: 1; min-width: 220px; }
    .author-name {
        font-size: 1.08rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.015em;
        margin: 0 0 3px 0;
    }
    .author-role {
        font-size: 0.68rem;
        font-weight: 700;
        color: var(--amber);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0 0 8px 0;
    }
    .author-org {
        font-size: 0.79rem;
        color: var(--muted);
        line-height: 1.55;
        margin: 0 0 12px 0;
        max-width: 400px;
    }
    .author-email {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.79rem;
        font-weight: 500;
        color: var(--navy);
        text-decoration: none;
        border-bottom: 1px solid transparent;
        padding-bottom: 1px;
        transition: border-color 0.18s ease;
    }
    .author-email:hover { border-bottom-color: var(--navy); }
    .author-divider {
        width: 1px;
        height: 76px;
        background: var(--border);
        flex-shrink: 0;
    }
    .author-meta { flex-shrink: 0; text-align: right; min-width: 170px; }
    .meta-label {
        font-size: 0.58rem;
        font-weight: 700;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        color: var(--muted);
        margin: 0 0 2px 0;
    }
    .meta-value {
        font-size: 0.79rem;
        font-weight: 600;
        color: var(--text);
        margin: 0 0 14px 0;
    }

    /* ──────────────────── RESPONSIVE BREAKPOINTS ─────────────────────────── */
    @media (max-width: 1024px) {
        .hero-title   { font-size: 2rem; }
        .kpi-value    { font-size: 1.75rem; }
        .block-container {
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }
        .author-divider { display: none; }
        .author-meta    { text-align: left; }
    }

    @media (max-width: 768px) {
        .hero         { padding: 4px 0 20px 0; }
        .hero-title   { font-size: 1.5rem; }
        .hero-subtitle { font-size: 0.88rem; }
        .hero-eyebrow { font-size: 0.56rem; }
        .kpi-card     { min-height: auto; padding: 18px 18px 14px 18px; }
        .kpi-value    { font-size: 1.5rem; }
        .kpi-label    { font-size: 0.57rem; }
        .sec-title-text { font-size: 0.84rem; }
        .author-card  { flex-direction: column; align-items: flex-start; padding: 20px 22px; }
        .author-meta  { text-align: left; }
    }

    @media (max-width: 480px) {
        .hero-title    { font-size: 1.2rem; }
        .hero-subtitle { font-size: 0.82rem; }
        .kpi-value     { font-size: 1.3rem; }
        .kpi-card      { padding: 14px 14px 12px 14px; }
        .author-logo-wrap { width: 64px; height: 64px; }
    }
    </style>
    """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar(df: pd.DataFrame):
    """Render sidebar controls. Returns (filtered_df, lang)."""
    with st.sidebar:

        # Brand mark
        st.markdown("""
        <div style="padding:30px 4px 22px 4px;text-align:center;
                    border-bottom:1px solid rgba(255,255,255,0.07);
                    margin-bottom:2px;">
            <div style="font-size:0.56rem;letter-spacing:0.2em;text-transform:uppercase;
                        color:rgba(255,255,255,0.3);margin-bottom:6px;">
                Market Research
            </div>
            <div style="font-size:1.55rem;font-weight:800;color:#fff;
                        letter-spacing:-0.02em;display:inline-block;
                        border-bottom:2.5px solid #F4B400;padding-bottom:3px;
                        line-height:1.2;">
                UZLI
            </div>
            <div style="font-size:0.56rem;color:rgba(255,255,255,0.28);
                        letter-spacing:0.13em;text-transform:uppercase;
                        margin-top:7px;">
                Dashboard &nbsp;·&nbsp; TSE Analytics
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Language
        st.markdown(
            '<div style="padding-top:18px"><span class="sb-label">🌐 &nbsp;Language / Til</span></div>',
            unsafe_allow_html=True,
        )
        lang_choice = st.radio(
            "", ["English", "O'zbek"],
            horizontal=True,
            label_visibility="collapsed",
        )
        lang = "en" if lang_choice == "English" else "uz"
        s = STRINGS[lang]

        st.markdown('<hr class="sb-divider"/>', unsafe_allow_html=True)

        # Date range
        st.markdown(
            f'<span class="sb-label">📅 &nbsp;{s["date_range"]}</span>',
            unsafe_allow_html=True,
        )
        min_d = df["date"].min().date()
        max_d = df["date"].max().date()

        if "reset_n" not in st.session_state:
            st.session_state.reset_n = 0

        date_sel = st.date_input(
            label="",
            value=(min_d, max_d),
            min_value=min_d,
            max_value=max_d,
            label_visibility="collapsed",
            key=f"dr_{st.session_state.reset_n}",
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button(f"↺  {s['reset']}", use_container_width=True):
            st.session_state.reset_n += 1
            st.rerun()

        st.markdown('<hr class="sb-divider"/>', unsafe_allow_html=True)

        # About
        with st.expander(f"ℹ  {s['about']}"):
            st.markdown(
                f'<span style="font-size:0.78rem;color:rgba(255,255,255,0.7);'
                f'line-height:1.65;display:block;">{s["about_text"]}</span>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="sb-divider"/>', unsafe_allow_html=True)

        # Resolve date range
        if isinstance(date_sel, (list, tuple)) and len(date_sel) == 2:
            d_start, d_end = date_sel
        elif isinstance(date_sel, (list, tuple)) and len(date_sel) == 1:
            d_start = d_end = date_sel[0]
        else:
            d_start = d_end = date_sel

        filtered = df[
            (df["date"].dt.date >= d_start) &
            (df["date"].dt.date <= d_end)
        ].copy().reset_index(drop=True)

        # Download
        st.markdown(
            f'<span class="sb-label">⬇ &nbsp;{s["download"]}</span>',
            unsafe_allow_html=True,
        )
        export_cols = ["date"] + NORM_COLS + ["uzli_score", "liquidity_label"]
        csv_bytes   = filtered[export_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"⬇  {s['download']}",
            data=csv_bytes,
            file_name="uzli_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )

    return filtered, lang


# ── Hero ──────────────────────────────────────────────────────────────────────

def render_hero(lang: str):
    s = STRINGS[lang]
    st.markdown(f"""
    <div class="hero">
        <div class="hero-eyebrow">{s["eyebrow"]}</div>
        <h1 class="hero-title">{s["page_title"]}</h1>
        <p class="hero-subtitle">{s["subtitle"]}</p>
        <div class="hero-badges">
            <span class="hero-badge">📅 {s["badge_years"]}</span>
            <span class="hero-badge">📊 {s["badge_days"]}</span>
            <span class="hero-badge">🏛 {s["badge_sec"]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Empty state ───────────────────────────────────────────────────────────────

def render_empty_state(lang: str):
    s = STRINGS[lang]
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-title">{s["empty_title"]}</div>
        <div class="empty-text">{s["empty_text"]}</div>
    </div>
    """, unsafe_allow_html=True)


# ── KPI Cards ─────────────────────────────────────────────────────────────────

def render_kpi_cards(df: pd.DataFrame, lang: str):
    s    = STRINGS[lang]
    last = df.iloc[-1]
    lc   = label_color(last["liquidity_label"])
    tl   = translate_label(last["liquidity_label"], lang)

    avg_30   = df["uzli_score"].tail(30).mean()
    prior_30 = df["uzli_score"].iloc[-60:-30]

    if len(prior_30) > 0:
        delta = avg_30 - prior_30.mean()
        arrow = "▲" if delta >= 0 else "▼"
        cls   = "delta-up" if delta >= 0 else "delta-dn"
        delta_html = (
            f'<div class="{cls}">{arrow} {abs(delta):.2f} '
            f'<span style="font-weight:400;color:var(--muted);">{s["vs_prior"]}</span></div>'
        )
    else:
        delta_html = f'<div class="kpi-sub">{s["vs_prior"]}</div>'

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{C['amber']}">
            <div class="kpi-header">
                <span class="kpi-label">{s['current_uzli']}</span>
                <span class="kpi-icon">📊</span>
            </div>
            <div class="kpi-value" style="color:{lc}">{last['uzli_score']:.2f}</div>
            <div class="kpi-sub">{last['date'].strftime('%d %b %Y')}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{lc}">
            <div class="kpi-header">
                <span class="kpi-label">{s['liq_level']}</span>
                <span class="kpi-icon">🔵</span>
            </div>
            <div class="kpi-value" style="font-size:1.25rem;letter-spacing:-0.01em;color:{lc}">{tl}</div>
            <span class="kpi-badge" style="background:{lc}18;color:{lc}">{tl}</span>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color:{C['navy']}">
            <div class="kpi-header">
                <span class="kpi-label">{s['avg_30d']}</span>
                <span class="kpi-icon">📈</span>
            </div>
            <div class="kpi-value">{avg_30:.2f}</div>
            {delta_html}
        </div>""", unsafe_allow_html=True)


# ── Executive Summary card ────────────────────────────────────────────────────

def render_exec_summary(df: pd.DataFrame, lang: str):
    labels = METRIC_DISPLAY[lang]
    last   = df.iloc[-1]
    lc     = label_color(last["liquidity_label"])
    tl     = translate_label(last["liquidity_label"], lang)

    avg_30   = df["uzli_score"].tail(30).mean()
    prior_30 = df["uzli_score"].iloc[-60:-30]

    if len(prior_30) > 0:
        delta     = avg_30 - prior_30.mean()
        arrow     = "▲" if delta >= 0 else "▼"
        delta_clr = C["high"] if delta >= 0 else C["low"]
        delta_html = (
            f'<span style="color:{delta_clr};font-weight:600;">'
            f'{arrow} {abs(delta):.2f} pts</span>'
        )
    else:
        delta_html = '<span style="color:#64748B;">—</span>'

    contrib_means = df[CONTRIB_COLS].mean()
    top_col    = contrib_means.idxmax()
    top_metric = top_col.replace("_contrib", "")
    top_name   = labels[top_metric]
    top_val    = contrib_means[top_col]

    date_str  = last["date"].strftime("%d %b %Y")
    score_str = f"{last['uzli_score']:.2f}"
    avg_str   = f"{avg_30:.2f}"

    lbl_as_of = {"en": f"As of {date_str}", "uz": f"{date_str} holatiga"}[lang]
    lbl_30d   = {"en": "30-Day Average",    "uz": "30 Kunlik O'rtacha"}[lang]
    lbl_dom   = {"en": "Dominant Metric",   "uz": "Yetakchi Metrik"}[lang]

    lbl_s  = "font-size:0.58rem;font-weight:700;letter-spacing:0.13em;text-transform:uppercase;color:#64748B;margin-bottom:5px;"
    val_s  = "font-size:0.93rem;font-weight:600;color:#1E293B;line-height:1.35;"
    cell_s = "flex:1;min-width:190px;padding:0 20px;"
    div_s  = "border-left:1px solid #E5E7EB;"

    st.markdown(f"""
    <div style="background:#FFFFFF;border-radius:12px;padding:16px 0 16px 20px;
                box-shadow:0 1px 2px rgba(15,23,42,.04),0 1px 3px rgba(15,23,42,.06);
                border:1px solid #E5E7EB;border-left:4px solid {C['amber']};
                display:flex;gap:0;align-items:center;flex-wrap:wrap;margin-bottom:8px;">
        <div style="{cell_s}padding-left:4px;">
            <div style="{lbl_s}">{lbl_as_of}</div>
            <div style="{val_s}">UZLI&nbsp;<span style="color:{lc}">{score_str}</span>&nbsp;&mdash;&nbsp;<span style="color:{lc}">{tl}</span></div>
        </div>
        <div style="{cell_s}{div_s}">
            <div style="{lbl_s}">{lbl_30d}</div>
            <div style="{val_s}">{avg_str} pts &nbsp;&nbsp; {delta_html}</div>
        </div>
        <div style="{cell_s}{div_s}">
            <div style="{lbl_s}">{lbl_dom}</div>
            <div style="{val_s}">{top_name}&nbsp;<span style="color:#64748B;font-weight:400;">({top_val:.2f} pts)</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Main UZLI chart ───────────────────────────────────────────────────────────

def build_uzli_chart(df: pd.DataFrame, lang: str) -> go.Figure:
    s     = STRINGS[lang]
    y_max = max(df["uzli_score"].max() * 1.1, 85)

    fig = go.Figure()

    for y0, y1, color in [(0, 40, C["low"]), (40, 70, C["moderate"]), (70, 100, C["high"])]:
        fig.add_hrect(y0=y0, y1=y1, fillcolor=color, opacity=0.04, line_width=0)

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["uzli_score"],
        mode="lines",
        line=dict(color=C["navy"], width=1.7),
        fill="tozeroy",
        fillcolor="rgba(11,37,69,0.07)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>UZLI: <b>%{y:.2f}</b><extra></extra>",
        name="UZLI",
    ))

    for y_val, color, label in [
        (40, C["moderate"], f"  {s['ann_mod']} ≥40"),
        (70, C["high"],     f"  {s['ann_high']} ≥70"),
    ]:
        fig.add_hline(
            y=y_val,
            line_dash="dash",
            line_color=color,
            line_width=1.2,
            annotation_text=label,
            annotation_position="top right",
            annotation_font_size=10,
            annotation_font_color=color,
        )

    fig.update_layout(
        template="plotly_white",
        title=dict(
            text=s["chart_title"],
            font=dict(size=13, color=C["text"], family="Inter"),
            x=0.01, xanchor="left",
        ),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=10, color=C["muted"]),
            tickformat="%Y",
            dtick="M12",
            showline=True,
            linecolor=C["border"],
            tickangle=0,
        ),
        yaxis=dict(
            range=[0, y_max],
            tickfont=dict(size=10, color=C["muted"]),
            gridcolor="#F0F4F8",
            title=dict(text="UZLI Score", font=dict(size=10, color=C["muted"])),
            zeroline=False,
        ),
        margin=dict(l=48, r=96, t=48, b=32),
        hovermode="x unified",
        showlegend=False,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=440,
    )
    return fig


# ── Contribution chart ────────────────────────────────────────────────────────

def build_contribution_chart(df: pd.DataFrame, lang: str) -> go.Figure:
    """
    Stacked bar chart of weighted metric contributions.
    Date filter is already applied — monthly groupby runs on the filtered slice.
    """
    s      = STRINGS[lang]
    labels = METRIC_DISPLAY[lang]

    tmp = df.copy()
    tmp["month"] = tmp["date"].dt.to_period("M").dt.to_timestamp()
    monthly = tmp.groupby("month")[CONTRIB_COLS].mean().reset_index()
    monthly.rename(columns={"month": "date"}, inplace=True)

    fig = go.Figure()
    for contrib_col, metric in zip(CONTRIB_COLS, NORM_COLS):
        fig.add_trace(go.Bar(
            x=monthly["date"],
            y=monthly[contrib_col],
            name=labels[metric],
            marker_color=C[metric],
            hovertemplate=(
                f"<b>{labels[metric]}</b><br>"
                "%{x|%b %Y}: <b>%{y:.2f}</b><extra></extra>"
            ),
        ))

    fig.update_layout(
        template="plotly_white",
        barmode="stack",
        title=dict(
            text=s["contrib_title"],
            font=dict(size=13, color=C["text"], family="Inter"),
            x=0.01, xanchor="left",
        ),
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=10, color=C["muted"]),
            showline=True,
            linecolor=C["border"],
        ),
        yaxis=dict(
            tickfont=dict(size=10, color=C["muted"]),
            gridcolor="#F0F4F8",
            title=dict(text="Weighted Contribution", font=dict(size=10, color=C["muted"])),
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color=C["text"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=48, r=40, t=48, b=72),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=360,
    )
    return fig


# ── Data table ────────────────────────────────────────────────────────────────

def render_data_table(df: pd.DataFrame, lang: str):
    s = STRINGS[lang]

    display = df.tail(30).copy().iloc[::-1].reset_index(drop=True)
    display["liquidity_label"] = display["liquidity_label"].apply(
        lambda x: translate_label(x, lang)
    )
    display["date"] = display["date"].dt.strftime("%d %b %Y")

    col_map = {
        "date":            s["col_date"],
        "volume_norm":     s["col_vol"],
        "breadth_norm":    s["col_breadth"],
        "turnover_norm":   s["col_turnover"],
        "amihud_norm":     s["col_amihud"],
        "spread_norm":     s["col_spread"],
        "uzli_score":      s["col_score"],
        "liquidity_label": s["col_label"],
    }
    display = display[list(col_map.keys())].rename(columns=col_map)

    num_cfg = dict(format="%.2f")
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=260,
        column_config={
            s["col_score"]:    st.column_config.NumberColumn(**num_cfg),
            s["col_vol"]:      st.column_config.NumberColumn(**num_cfg),
            s["col_breadth"]:  st.column_config.NumberColumn(**num_cfg),
            s["col_turnover"]: st.column_config.NumberColumn(**num_cfg),
            s["col_amihud"]:   st.column_config.NumberColumn(**num_cfg),
            s["col_spread"]:   st.column_config.NumberColumn(**num_cfg),
        },
    )


# ── Footer — author card ──────────────────────────────────────────────────────

def render_footer(lang: str):
    # Override st.container(border=True) default styling with the premium card design.
    # The only bordered container in this app is this footer card, so the selector
    # is unambiguous. Inline styles bypass any f-string / large-string issues with
    # st.markdown, and st.image() serves the logo natively without base64-in-HTML.
    # Scope selector to .block-container so the sidebar expander
    # (also a stVerticalBlockBorderWrapper) is never affected.
    st.markdown(
        "<style>"
        ".block-container [data-testid='stVerticalBlockBorderWrapper']{"
            "background:#FFFFFF !important;"
            "border-radius:16px !important;"
            "border:1px solid #E5E7EB !important;"
            "border-left:4px solid #0B2545 !important;"
            "box-shadow:0 4px 6px -1px rgba(15,23,42,.07),"
                       "0 2px 4px -1px rgba(15,23,42,.04) !important;"
            "transition:box-shadow .22s ease,transform .22s ease !important;"
            "padding:20px 28px !important;"
        "}"
        ".block-container [data-testid='stVerticalBlockBorderWrapper']:hover{"
            "box-shadow:0 10px 15px -3px rgba(15,23,42,.08),"
                       "0 4px 6px -2px rgba(15,23,42,.04) !important;"
            "transform:translateY(-2px);"
        "}"
        "</style>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:52px'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        col_logo, col_info, col_gap, col_meta = st.columns([1.3, 3.8, 0.15, 2.2])

        with col_logo:
            if LOGO_PATH.exists():
                st.image(str(LOGO_PATH), use_container_width=True)
            else:
                st.markdown(
                    "<div style='text-align:center;font-size:2.5rem;"
                    "opacity:0.4;padding:16px 0;'>&#127963;</div>",
                    unsafe_allow_html=True,
                )

        with col_info:
            st.markdown(
                "<p style='font-size:1.08rem;font-weight:700;color:#1E293B;"
                    "letter-spacing:-0.015em;margin:0 0 3px 0;'>"
                    "Ayubov Rakhmatullo</p>"
                "<p style='font-size:0.68rem;font-weight:700;color:#F4B400;"
                    "text-transform:uppercase;letter-spacing:0.1em;margin:0 0 8px 0;'>"
                    "Lead Specialist</p>"
                "<p style='font-size:0.79rem;color:#64748B;line-height:1.55;margin:0 0 12px 0;'>"
                    "Institute for Macroeconomic and Regional Studies<br/>"
                    "under the Cabinet of Ministers of the Republic of Uzbekistan</p>"
                "<a href='mailto:r.ayubov@imrs.uz' style='font-size:0.79rem;font-weight:500;"
                    "color:#0B2545;text-decoration:none;border-bottom:1px solid transparent;"
                    "padding-bottom:1px;transition:border-color .18s;'>"
                    "&#9993;&nbsp; r.ayubov@imrs.uz</a>",
                unsafe_allow_html=True,
            )

        with col_gap:
            st.markdown(
                "<div style='width:1px;height:76px;background:#E5E7EB;"
                "margin:auto;'></div>",
                unsafe_allow_html=True,
            )

        with col_meta:
            st.markdown(
                "<div style='text-align:right;'>"
                "<p style='font-size:0.58rem;font-weight:700;letter-spacing:0.13em;"
                    "text-transform:uppercase;color:#64748B;margin:0 0 2px 0;'>"
                    "Data Source</p>"
                "<p style='font-size:0.79rem;font-weight:600;color:#1E293B;margin:0 0 14px 0;'>"
                    "Tashkent Stock Exchange</p>"
                "<p style='font-size:0.58rem;font-weight:700;letter-spacing:0.13em;"
                    "text-transform:uppercase;color:#64748B;margin:0 0 2px 0;'>"
                    "Coverage</p>"
                "<p style='font-size:0.79rem;font-weight:600;color:#1E293B;margin:0;'>"
                    "November 2016 &ndash; June 2026</p>"
                "</div>",
                unsafe_allow_html=True,
            )


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    apply_css()

    df = load_data()

    filtered_df, lang = render_sidebar(df)
    s = STRINGS[lang]

    render_hero(lang)

    if filtered_df.empty:
        render_empty_state(lang)
        render_footer(lang)
        return

    render_kpi_cards(filtered_df, lang)
    render_exec_summary(filtered_df, lang)

    st.markdown(sec_hdr(s["chart_title"]), unsafe_allow_html=True)
    st.plotly_chart(
        build_uzli_chart(filtered_df, lang),
        use_container_width=True,
        config={"displaylogo": False, "modeBarButtonsToRemove": ["autoScale2d", "lasso2d", "select2d"]},
    )

    col_chart, col_tbl = st.columns([1.6, 1])
    with col_chart:
        st.markdown(sec_hdr(s["contrib_title"]), unsafe_allow_html=True)
        st.plotly_chart(
            build_contribution_chart(filtered_df, lang),
            use_container_width=True,
            config={"displaylogo": False},
        )
        st.markdown(
            f'<p style="font-size:0.71rem;color:var(--muted,#64748B);margin:-10px 0 20px 2px;">'
            f'{s["contrib_note"]}</p>',
            unsafe_allow_html=True,
        )
    with col_tbl:
        st.markdown(sec_hdr(s["table_title"]), unsafe_allow_html=True)
        render_data_table(filtered_df, lang)

    render_footer(lang)


if __name__ == "__main__":
    main()
