import streamlit as st
from rpg.dice import roll_dice, roll_d20, format_roll
from rpg.dice3d import cube_html
import streamlit.components.v1 as components

st.title("🎲 Dados")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Rolagem rápida")
    mode = st.radio("Modo", ["Expressão (ex.: 2d6+3)", "d20 (ataques/testes)"], horizontal=True)

    if mode.startswith("Expressão"):
        expr = st.text_input("Expressão", value="1d20+0")
        times = st.number_input("Quantidade", min_value=1, max_value=50, value=1, step=1)
        if st.button("Rolar", use_container_width=True):
            for _ in range(int(times)):
                rr = roll_dice(expr)
                st.session_state["log"].insert(0, f"🎲 {format_roll(rr)}")
            st.rerun()

    else:
        bonus = st.number_input("Bônus", min_value=-50, max_value=50, value=0, step=1)
        adv = st.checkbox("Vantagem")
        dis = st.checkbox("Desvantagem")
        if st.button("Rolar d20", use_container_width=True):
            rr = roll_d20(bonus=int(bonus), advantage=adv, disadvantage=dis)
            st.session_state["log"].insert(0, f"🎲 {format_roll(rr)}")
            st.session_state["last_d20"] = rr
            st.rerun()

with col2:
    st.subheader("Visual 3D (simples)")
    st.caption("Animação 3D visual (o resultado é o que aparece no log).")
    last = st.session_state.get("last_d20")
    if last:
        components.html(cube_html(last["total"]), height=240)
    else:
        components.html(cube_html("🎲"), height=240)

st.divider()
st.subheader("📜 Log")
if st.button("Limpar log"):
    st.session_state["log"] = []
for line in st.session_state.get("log", [])[:200]:
    st.markdown(line)
