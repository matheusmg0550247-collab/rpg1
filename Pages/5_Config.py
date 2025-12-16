import streamlit as st

st.title("⚙️ Config")

st.markdown("### Preferências")
st.checkbox("Mostrar resultado em destaque (placeholder)", value=True)

st.markdown("### Sobre o 3D")
st.info("O 3D atual é um visual simples (CSS). Quando você quiser, a gente evolui para um componente real com Three.js + física.")
