"""CSS injection for the premium, theme-aware look and feel."""

import streamlit as st
from content import THEMES


def inject_css(theme_name: str):
    theme = THEMES.get(theme_name, THEMES["Neon Megacity"])
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Fraunces:ital,wght@0,500;0,700;1,500&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background: {theme['gradient']};
        background-attachment: fixed;
        color: {theme['text']};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: rgba(0,0,0,0.28);
        backdrop-filter: blur(18px);
        border-right: 1px solid rgba(255,255,255,0.08);
    }}
    section[data-testid="stSidebar"] * {{
        color: {theme['text']} !important;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Fraunces', Georgia, serif;
        color: {theme['text']};
        letter-spacing: -0.01em;
    }}

    /* Glass cards */
    .ff-card {{
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 20px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    .ff-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.35);
    }}

    .ff-metric-label {{
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        opacity: 0.7;
        margin-bottom: 0.15rem;
    }}
    .ff-metric-value {{
        font-family: 'Fraunces', serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: {theme['accent2']};
        line-height: 1.1;
    }}

    .ff-pill {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        background: linear-gradient(90deg, {theme['accent']}, {theme['accent2']});
        color: #0b0b0f;
        font-weight: 700;
        font-size: 0.78rem;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }}

    .ff-badge {{
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100px;
        padding: 0.9rem 0.5rem;
        border-radius: 18px;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.15);
        margin: 0.35rem;
        text-align: center;
        transition: transform .2s ease;
    }}
    .ff-badge:hover {{ transform: scale(1.06); }}
    .ff-badge.locked {{ opacity: 0.35; filter: grayscale(1); }}
    .ff-badge .emoji {{ font-size: 1.9rem; margin-bottom: 0.25rem; }}
    .ff-badge .name {{ font-size: 0.68rem; font-weight: 700; }}

    .ff-hero {{
        border-radius: 26px;
        padding: 2.2rem 2rem;
        background: linear-gradient(120deg, rgba(255,255,255,0.10), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.14);
        backdrop-filter: blur(20px);
        margin-bottom: 1.4rem;
    }}

    .ff-quote {{
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 1.15rem;
        border-left: 3px solid {theme['accent']};
        padding-left: 1rem;
        opacity: 0.92;
    }}

    div.stButton > button {{
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.2);
        background: linear-gradient(90deg, {theme['accent']}, {theme['accent2']});
        color: #0b0b0f;
        font-weight: 700;
        padding: 0.5rem 1.1rem;
        transition: transform .15s ease;
    }}
    div.stButton > button:hover {{
        transform: translateY(-2px) scale(1.02);
    }}

    [data-testid="stMetricValue"] {{
        color: {theme['accent2']};
        font-family: 'Fraunces', serif;
    }}

    .streak-flame {{
        font-size: 2.6rem;
        animation: flicker 1.6s infinite alternate;
    }}
    @keyframes flicker {{
        0% {{ transform: scale(1) rotate(-2deg); opacity: 0.9; }}
        100% {{ transform: scale(1.08) rotate(2deg); opacity: 1; }}
    }}

    hr {{ border-color: rgba(255,255,255,0.15); }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def card_start():
    st.markdown('<div class="ff-card">', unsafe_allow_html=True)


def card_end():
    st.markdown('</div>', unsafe_allow_html=True)


def metric_html(label, value, suffix=""):
    return f"""
    <div class="ff-card">
        <div class="ff-metric-label">{label}</div>
        <div class="ff-metric-value">{value}{suffix}</div>
    </div>
    """
