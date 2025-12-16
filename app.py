import streamlit as st
from rpg.storage import ensure_dirs

st.set_page_config(
    page_title="RPG Panel (D&D Helper)",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_dirs()

st.title("🎲 RPG Panel (Starter)")
st.write("Use as páginas no menu lateral: **Dados**, **Fichas**, **Combate**, **Mídia**, **Config**.")

# Estado global básico
if "log" not in st.session_state:
    st.session_state["log"] = []
if "media" not in st.session_state:
    st.session_state["media"] = {"audio": None, "video": None}

st.info("Dica: comece criando uma ficha em **Fichas** e depois abra **Combate**.")
