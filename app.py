# -*- coding: utf-8 -*-

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from rpg.storage import ensure_dirs
from rpg.ficha_view import render as render_ficha
from rpg.combate_view import render as render_combate

st.set_page_config(
    page_title="RPG Panel",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ensure_dirs()

st.title("RPG Panel")

tab1, tab2 = st.tabs(["Ficha", "Combate"])
with tab1:
    render_ficha()
with tab2:
    render_combate()
