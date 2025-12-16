import streamlit as st

st.set_page_config(
    page_title="RPG Panel",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("## 🎲 RPG Panel")

# Menu no topo (links)
m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.8])
m1.page_link("app.py", label="🏠 Início")
m2.page_link("pages/2_Fichas.py", label="🧾 Fichas")
m3.page_link("pages/3_Combate.py", label="⚔️ Combate")
m4.page_link("pages/4_Midia.py", label="🎵 Mídia")
m5.page_link("pages/5_Config.py", label="⚙️ Config")

st.divider()
st.info("Use o menu acima. Você pode colapsar a lateral e usar só essa barra.")
