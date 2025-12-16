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


def apply_black_red_css() -> None:
    st.markdown(
        """
<style>
/* ===== FUNDO PRINCIPAL ===== */
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at top left, #2a0000 0%, #070707 55%, #000000 100%) !important;
}

/* ===== SIDEBAR PRETO ===== */
[data-testid="stSidebar"] {
  background-color: #0a0a0a !important;
  border-right: 1px solid #1f1f1f !important;
}
[data-testid="stSidebarContent"] {
  background-color: #0a0a0a !important;
}
[data-testid="stSidebar"] * {
  color: #ffffff !important;
}

/* ===== TEXTO BRANCO (GARANTIA) ===== */
html, body, [data-testid="stAppViewContainer"] * {
  color: #ffffff;
}
[data-testid="stMarkdownContainer"] * {
  color: #ffffff !important;
}

/* ===== LINKS ===== */
a, a * { color: #ff2b2b !important; }

/* ===== ABAS ===== */
button[data-baseweb="tab"] {
  color: #ffffff !important;
  font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  border-bottom: 2px solid #ff2b2b !important;
}

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

/* ===== EXPANDER ===== */
details summary {
  border-left: 4px solid #ff2b2b !important;
  padding-left: 10px !important;
}

/* ===== INPUTS / NUMBER INPUT / TEXTAREA (PRETO) ===== */
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

/* ===== SELECT ===== */
div[data-baseweb="select"] > div {
  background-color: #0f0f0f !important;
  border: 1px solid #2b2b2b !important;
}
div[data-baseweb="select"] * {
  color: #ffffff !important;
}

/* ===== CHECKBOX (melhor contraste) ===== */
[data-testid="stCheckbox"] label {
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

st.title("🎲 RPG Panel")

tab_intro, tab_ficha, tab_combate = st.tabs(["📜 Introdução", "🧾 Ficha", "⚔️ Combate"])

with tab_intro:
    render_intro()

with tab_ficha:
    try:
        render_ficha()
    except Exception as e:
        st.error("Erro ao renderizar a Ficha. Veja os logs do Streamlit Cloud.")
        st.exception(e)

with tab_combate:
    try:
        render_combate()
    except Exception as e:
        st.error("Erro ao renderizar o Combate. Veja os logs do Streamlit Cloud.")
        st.exception(e)
