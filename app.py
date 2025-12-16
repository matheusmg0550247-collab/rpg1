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
/* Fundo geral */
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at top left, #220000 0%, #0a0a0a 55%, #000000 100%);
}

/* Cabeçalho e textos */
h1, h2, h3, h4 { letter-spacing: 0.2px; }
a { color: #ff2b2b !important; }

/* Abas */
button[data-baseweb="tab"] {
  color: #f5f5f5 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  border-bottom: 2px solid #ff2b2b !important;
}

/* Botões */
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

/* Expander */
details summary {
  border-left: 4px solid #ff2b2b !important;
  padding-left: 10px !important;
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
    render_ficha()

with tab_combate:
    render_combate()
