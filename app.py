import streamlit as st

st.set_page_config(
    page_title="RPG Panel",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("## 🎲 RPG Panel")
st.caption("Menu rápido no topo (você ainda pode usar o menu lateral se quiser).")

# --- MENU DO TOPO ---
c1, c2, c3, c4 = st.columns([1, 1, 1, 3])

with c1:
    st.page_link("app.py", label="🏠 Início")

with c2:
    st.page_link("pages/2_Fichas.py", label="🧾 Fichas")

with c3:
    st.page_link("pages/3_Combate.py", label="⚔️ Combate")

with c4:
    st.page_link("pages/4_Midia.py", label="🎵 Mídia")

st.divider()

st.info("Use o menu acima para ir direto em **Fichas** ou **Combate**.")
