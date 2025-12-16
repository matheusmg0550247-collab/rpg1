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
html, body, [data]()
