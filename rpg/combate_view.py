import streamlit as st
import random

def render():
    st.header("Combate")

    if "combat" not in st.session_state:
        st.session_state["combat"] = {"round": 1, "turn": 0, "combatants": []}

    combat = st.session_state["combat"]

    with st.expander("Adicionar combatente", expanded=True):
        name = st.text_input("Nome", value="Goblin")
        initb = st.number_input("Bonus iniciativa", -20, 20, value=2)
        if st.button("Adicionar"):
            combat["combatants"].append({"name": name, "initb": int(initb), "init": None})
            st.rerun()

    cols = st.columns(3)
    if cols[0].button("Rolar iniciativa"):
        for c in combat["combatants"]:
            c["init"] = random.randint(1, 20) + c["initb"]
        combat["combatants"].sort(key=lambda x: x["init"] or 0, reverse=True)
        combat["turn"] = 0
        combat["round"] = 1
        st.rerun()

    if cols[1].button("Proximo turno") and combat["combatants"]:
        combat["turn"] = (combat["turn"] + 1) % len(combat["combatants"])
        if combat["turn"] == 0:
            combat["round"] += 1
        st.rerun()

    if cols[2].button("Limpar"):
        combat["combatants"] = []
        combat["turn"] = 0
        combat["round"] = 1
        st.rerun()

    st.write("Rodada:", combat["round"])

    if not combat["combatants"]:
        st.info("Adicione combatentes.")
        return

    for i, c in enumerate(combat["combatants"]):
        marker = "➡️ " if i == combat["turn"] else ""
        st.write(f"{marker}{c['name']} — Init: {c['init']}")
