# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from rpg.storage import ensure_dirs
from rpg.intro_view import render as render_intro
from rpg.ficha_view import render as render_ficha
from rpg.combate_view import render as render_combate
from rpg.monsters_view import render as render_monsters


def apply_black_red_css() -> None:
    st.markdown(
        """
<style>
/* ===== FUNDO PRINCIPAL ===== */
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at top left, #2a0000 0%, #070707 55%, #000000 100%) !important;
}

/* ===== TEXTO BRANCO ===== */
html, body, [data-testid="stAppViewContainer"] * { color: #ffffff !important; }
[data-testid="stMarkdownContainer"] * { color: #ffffff !important; }

/* ===== SIDEBAR PRETO ===== */
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
  background-color: #0a0a0a !important;
  border-right: 1px solid #1f1f1f !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; }

/* ===== LINKS ===== */
a, a * { color: #ff2b2b !important; }

/* ===== BOTÕES ===== */
div.stButton > button {
  background: #b30000 !important;
  color: #ffffff !important;
  border: 1px solid #ff2b2b !important;
  border-radius: 10px !important;
}
div.stButton > button:hover {
  background: #ff2b2b !important;
  color: #0a0a0a !important;
}

/* ===== INPUTS (GERAL) ===== */
div[data-baseweb="base-input"] {
  background-color: #0f0f0f !important;
  border: 1px solid #2b2b2b !important;
  border-radius: 10px !important;
}
div[data-baseweb="base-input"] input,
div[data-baseweb="base-input"] textarea {
  background-color: transparent !important;
  color: #ffffff !important;
}

/* ===== NUMBER INPUT (AC etc) ===== */
[data-testid="stNumberInput"] div[data-baseweb="base-input"] {
  background-color: #0f0f0f !important;
  border: 1px solid #ff2b2b !important;
  border-radius: 10px !important;
}
[data-testid="stNumberInput"] input { background: transparent !important; color: #ffffff !important; }
[data-testid="stNumberInput"] button {
  background: #0f0f0f !important;
  color: #ffffff !important;
  border-left: 1px solid #2b2b2b !important;
}
[data-testid="stNumberInput"] button:hover { background: #1a1a1a !important; }

/* ===== ALERTS ===== */
div[data-testid="stAlert"] {
  background: #0f0f0f !important;
  border: 1px solid #2b2b2b !important;
  border-left: 4px solid #ff2b2b !important;
  border-radius: 12px !important;
}
div[data-testid="stAlert"] * { color: #ffffff !important; }

/* ===== EXPANDER ===== */
div[data-testid="stExpander"] details > summary {
  background: #0f0f0f !important;
  border: 1px solid #2b2b2b !important;
  border-left: 4px solid #ff2b2b !important;
  border-radius: 12px !important;
  padding: 10px 12px !important;
}
div[data-testid="stExpander"] div[role="region"] {
  background: rgba(15,15,15,0.85) !important;
  border: 1px solid #1f1f1f !important;
  border-top: none !important;
  border-radius: 0 0 12px 12px !important;
  padding: 12px !important;
}

/* ===== FILE UPLOADER (tirar branco) ===== */
div[data-testid="stFileUploaderDropzone"],
section[data-testid="stFileUploaderDropzone"],
div[data-testid="stFileUploaderDropzone"] > div,
section[data-testid="stFileUploaderDropzone"] > div {
  background: #0f0f0f !important;
  border: 1px dashed #ff2b2b !important;
  border-radius: 12px !important;
}
div[data-testid="stFileUploaderDropzone"] *,
section[data-testid="stFileUploaderDropzone"] * {
  color: #ffffff !important;
}

/* ===== CODE BLOCK ===== */
[data-testid="stCodeBlock"], pre, code {
  background: #0f0f0f !important;
  color: #ffffff !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="RPG Panel",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()
apply_black_red_css()

with st.sidebar:
    st.markdown("## 🎲 RPG Panel")
    page = st.radio(
        "Navegação",
        ["📜 Introdução", "🧾 Ficha", "⚔️ Combate", "👹 Monstros (🔒)"],
        index=0,
        label_visibility="collapsed",
    )

if page == "📜 Introdução":
    render_intro()
elif page == "🧾 Ficha":
    render_ficha()
elif page == "⚔️ Combate":
    render_combate()
elif page == "👹 Monstros (🔒)":
    render_monsters()
