import streamlit as st

st.set_page_config(page_title="RPG Panel", page_icon="🎲", layout="wide", initial_sidebar_state="collapsed")

st.markdown("## 🎲 RPG Panel")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🧾 Fichas", use_container_width=True):
        st.switch_page("pages/2_Fichas.py")

with c2:
    if st.button("⚔️ Combate", use_container_width=True):
        st.switch_page("pages/3_Combate.py")

with c3:
    if st.button("🎵 Mídia", use_container_width=True):
        st.switch_page("pages/4_Midia.py")
