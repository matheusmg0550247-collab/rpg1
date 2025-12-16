import streamlit as st
import random
import pandas as pd

def render():
    st.subheader("⚔️ Combate (MVP)")
    st.caption("Aqui vamos evoluir para iniciativa, turnos, condições, etc.")

    if "combat" not in st.session_state:
        st.session_state["combat"] = {"round": 1, "turn": 0, "combatants": []}

    combat = st.session_state["combat"]

    with st.expander("Adicionar combatente"):
        name = st.text_input("Nome", value="Goblin")
        initb = st.number_input("Bônus iniciativa", -20, 20, value=2)
        if st.button("Adicionar"):
            combat["combatants"].append({"name": name, "initb": int(initb), "roll": None, "init": None})
            st.rerun()

    cols = st.columns(4)
    if cols[0].button("🎲 Rolar iniciativa"):
        for c in combat["combatants"]:
            r = random.randint(1, 20)
            c["roll"] = r
            c["init"] = r + c["initb"]
        combat["combatants"].sort(key=lambda x: (x["init"] or 0, x["roll"] or 0), reverse=True)
        combat["turn"] = 0
        combat["round"] = 1
        st.rerun()

    if cols[1].button("➡️ Próximo turno") and combat["combatants"]:
        combat["turn"] = (combat["turn"] + 1) % len(combat["combatants"])
        if combat["turn"] == 0:
            combat["round"] += 1
        st.rerun()

    if cols[2].button("🧹 Limpar lista"):
        combat["combatants"] = []
        combat["turn"] = 0
        combat["round"] = 1
        st.rerun()

    st.markdown(f"**Rodada:** {combat['round']}")
    if combat["combatants"]:
        rows = []
        for i, c in enumerate(combat["combatants"]):
            rows.append({
                "": "➡️" if i == combat["turn"] else "",
                "Nome": c["name"],
                "Roll": c["roll"] if c["roll"] is not None else "",
                "Init": c["init"] if c["init"] is not None else "",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Adicione combatentes para começar.")
