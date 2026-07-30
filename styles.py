"""CSS injection for Fluent Forest RPG — theme-driven via the shop_catalog CSS
dicts, with card styles, progress bars, animated XP pills, and confetti support."""

import streamlit as st
import shop_catalog as sc


def inject_css(theme_id: str, reduced_motion: bool = False):
    item = sc.get_item(theme_id) or sc.get_item("light")
    css_vars = item["css"]
    bg = css_vars.get("bg", "linear-gradient(135deg,#f8fafc,#e2e8f0)")
    text = css_vars.get("text", "#1a1a1a")
    accent = css_vars.get("accent", "#4f46e5")
    anim_transition = "none" if reduced_motion else "all .2s ease"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Nunito:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Nunito', -apple-system, sans-serif;
    }}
    .stApp {{
        background: {bg};
        background-attachment: fixed;
        color: {text};
    }}
    section[data-testid="stSidebar"] {{
        background: rgba(0,0,0,0.22);
        backdrop-filter: blur(16px);
    }}
    section[data-testid="stSidebar"] * {{ color: {text} !important; }}

    h1, h2, h3, h4 {{
        font-family: 'Baloo 2', cursive;
        color: {text};
    }}

    .rpg-card {{
        background: rgba(255,255,255,0.10);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 18px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.9rem;
        transition: {anim_transition};
    }}
    .rpg-card:hover {{ transform: {'none' if reduced_motion else 'translateY(-2px)'}; }}

    .rpg-xp-bar-outer {{
        width: 100%; height: 22px; border-radius: 999px;
        background: rgba(255,255,255,0.15); overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    .rpg-xp-bar-inner {{
        height: 100%; border-radius: 999px;
        background: linear-gradient(90deg, {accent}, #ffd166);
        transition: {'none' if reduced_motion else 'width 0.6s ease'};
    }}

    .rpg-pill {{
        display: inline-block; padding: 0.3rem 0.85rem; border-radius: 999px;
        background: linear-gradient(90deg, {accent}, #ffd166);
        color: #0b0b0f; font-weight: 800; font-size: 0.85rem; margin: 0.2rem;
    }}

    .rpg-badge {{
        display: inline-flex; flex-direction: column; align-items: center;
        width: 96px; padding: 0.8rem 0.4rem; border-radius: 16px;
        background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);
        margin: 0.3rem; text-align: center;
    }}
    .rpg-badge.locked {{ opacity: 0.32; filter: grayscale(1); }}
    .rpg-badge .emoji {{ font-size: 1.8rem; }}
    .rpg-badge .name {{ font-size: 0.65rem; font-weight: 700; }}

    .rarity-common {{ color: #9aa5b1; }}
    .rarity-uncommon {{ color: #3ecf8e; }}
    .rarity-rare {{ color: #3e8ef7; }}
    .rarity-legendary {{ color: #f7b32e; text-shadow: 0 0 8px rgba(247,179,46,0.6); }}

    div.stButton > button {{
        border-radius: 14px; border: 1px solid rgba(255,255,255,0.25);
        background: linear-gradient(90deg, {accent}, #ffd166);
        color: #0b0b0f; font-weight: 800;
        transition: {'none' if reduced_motion else 'transform .12s ease'};
    }}
    div.stButton > button:hover {{ transform: {'none' if reduced_motion else 'scale(1.03)'}; }}

    .pet-companion {{
        font-size: 2.4rem;
        display: inline-block;
        animation: {'none' if reduced_motion else 'bob 2.4s ease-in-out infinite'};
    }}
    @keyframes bob {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-6px); }}
    }}

    hr {{ border-color: rgba(255,255,255,0.15); }}
    </style>
    """, unsafe_allow_html=True)


def card_start():
    st.markdown('<div class="rpg-card">', unsafe_allow_html=True)


def card_end():
    st.markdown('</div>', unsafe_allow_html=True)


def xp_bar(pct: float, label: str = ""):
    pct_clamped = max(0.0, min(1.0, pct)) * 100
    st.markdown(f"""
    <div class="rpg-xp-bar-outer">
        <div class="rpg-xp-bar-inner" style="width:{pct_clamped}%;"></div>
    </div>
    {f'<div style="font-size:0.8rem;opacity:0.8;margin-top:0.2rem;">{label}</div>' if label else ''}
    """, unsafe_allow_html=True)


def rarity_span(rarity: str, text: str) -> str:
    return f'<span class="rarity-{rarity}">{text}</span>'
