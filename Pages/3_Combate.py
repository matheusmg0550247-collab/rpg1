import streamlit as st
import uuid
import pandas as pd

from rpg.models import Encounter, Combatant
from rpg.storage import (
    list_character_ids, load_character,
    list_encounter_ids, load_encounter, save_encounter, delete_encounter
)
from rpg.initiative import roll_initiative, next_turn, prev_turn
from rpg.dice import roll_d20, roll_dice, format_roll

st.title("⚔️ Combate")

# Estado do encontro atual
if "encounter" not in st.session_state:
    st.session_state["encounter"] = None

top_left, top_right = st.columns([0.42, 0.58], gap="large")

with top_left:
    st.subheader("Encontros salvos")
    saved = list_encounter_ids()
    pick = st.selectbox("Abrir", ["(novo)"] + saved)

    if pick != "(novo)":
        enc = load_encounter(pick)
        if enc:
            st.session_state["encounter"] = enc
            st.success(f"Aberto: {enc.title}")
    else:
        if st.button("Criar encontro vazio", use_container_width=True):
            st.session_state["encounter"] = Encounter(id=uuid.uuid4().hex[:10], title="Encontro", combatants=[])
            st.rerun()

    enc = st.session_state.get("encounter")
    if enc and st.button("💾 Salvar encontro", use_container_width=True):
        save_encounter(enc)
        st.success("Salvo.")

    if enc and st.button("🗑️ Excluir encontro", use_container_width=True):
        delete_encounter(enc.id)
        st.session_state["encounter"] = None
        st.rerun()

with top_right:
    enc = st.session_state.get("encounter")
    if not enc:
        st.info("Crie ou abra um encontro para começar.")
    else:
        enc.title = st.text_input("Título do encontro", value=enc.title)

st.divider()
enc = st.session_state.get("encounter")
if not enc:
    st.stop()

# Adicionar combatentes
add_left, add_right = st.columns([0.55, 0.45], gap="large")

with add_left:
    st.subheader("Adicionar PCs da sua lista")
    char_ids = list_character_ids()
    if char_ids:
        chosen = st.multiselect("Selecionar PCs", char_ids)
        if st.button("Adicionar PCs", use_container_width=True):
            for cid in chosen:
                ch = load_character(cid)
                if not ch:
                    continue
                enc.combatants.append(Combatant(
                    name=ch.character_name,
                    kind="PC",
                    initiative_bonus=int(ch.initiative_bonus),
                    ac=int(ch.ac),
                    max_hp=int(ch.max_hp),
                    hp=int(ch.current_hp),
                ))
            st.success("PCs adicionados.")
            st.rerun()
    else:
        st.caption("Sem personagens ainda. Crie em **Fichas**.")

with add_right:
    st.subheader("Adicionar monstro/NPC")
    with st.form("add_monster"):
        name = st.text_input("Nome", value="Goblin")
        initb = st.number_input("Init bônus", -20, 20, value=2)
        ac = st.number_input("AC", 1, 40, value=15)
        hp = st.number_input("HP", 1, 999, value=7)
        add = st.form_submit_button("Adicionar", use_container_width=True)
    if add:
        enc.combatants.append(Combatant(name=name, kind="Monster", initiative_bonus=int(initb), ac=int(ac), max_hp=int(hp), hp=int(hp)))
        st.rerun()

st.divider()

# Iniciativa e turno
controls = st.columns([1, 1, 1, 1, 1], gap="small")
with controls[0]:
    if st.button("🎲 Rolar iniciativa", use_container_width=True):
        roll_initiative(enc.combatants)
        enc.turn_index = 0
        enc.round = 1
        st.session_state["log"].insert(0, "⚔️ Iniciativa rolada.")
        st.rerun()
with controls[1]:
    if st.button("⬅️ Turno anterior", use_container_width=True):
        enc.turn_index = prev_turn(enc.turn_index, len(enc.combatants))
        st.rerun()
with controls[2]:
    if st.button("➡️ Próximo turno", use_container_width=True):
        old = enc.turn_index
        enc.turn_index = next_turn(enc.turn_index, len(enc.combatants))
        if enc.turn_index == 0 and len(enc.combatants) > 0 and old == len(enc.combatants) - 1:
            enc.round += 1
        st.rerun()
with controls[3]:
    if st.button("➕ Nova rodada", use_container_width=True):
        enc.round += 1
        enc.turn_index = 0
        st.rerun()
with controls[4]:
    if st.button("🧹 Limpar combate (mantém lista)", use_container_width=True):
        enc.round = 1
        enc.turn_index = 0
        for c in enc.combatants:
            c.initiative_roll = None
            c.initiative_total = None
            c.conditions = []
        st.rerun()

# Tabela de turnos
st.subheader(f"📌 Ordem de turno — Rodada {enc.round}")
rows = []
for idx, c in enumerate(enc.combatants):
    active = "➡️" if idx == enc.turn_index else ""
    rows.append({
        "": active,
        "Nome": c.name,
        "Tipo": c.kind,
        "Init": (c.initiative_total if c.initiative_total is not None else ""),
        "AC": (c.ac if c.ac is not None else ""),
        "HP": (c.hp if c.hp is not None else ""),
        "Condições": ", ".join(c.conditions) if c.conditions else "",
    })
df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)

# Painel do turno atual
if enc.combatants:
    current = enc.combatants[enc.turn_index]
    st.divider()
    st.subheader(f"🎯 Turno: {current.name} ({current.kind})")

    c1, c2, c3 = st.columns([0.34, 0.33, 0.33], gap="large")
    with c1:
        st.markdown("### Vida / Condições")
        if current.hp is not None and current.max_hp is not None:
            new_hp = st.number_input("HP atual", 0, int(current.max_hp), value=int(current.hp), key=f"hp_{enc.turn_index}")
            current.hp = int(new_hp)
        cond = st.text_input("Adicionar condição (ex.: Prone)", value="", key=f"cond_{enc.turn_index}")
        if st.button("Adicionar condição", key=f"addcond_{enc.turn_index}", use_container_width=True) and cond.strip():
            current.conditions.append(cond.strip())
            st.rerun()
        if current.conditions and st.button("Limpar condições", key=f"clearcond_{enc.turn_index}", use_container_width=True):
            current.conditions = []
            st.rerun()

    with c2:
        st.markdown("### Ações rápidas")
        bonus = st.number_input("Bônus d20", -50, 50, value=0, key="quick_bonus")
        adv = st.checkbox("Vantagem", key="quick_adv")
        dis = st.checkbox("Desvantagem", key="quick_dis")
        if st.button("Rolar d20", key="quick_d20", use_container_width=True):
            rr = roll_d20(bonus=int(bonus), advantage=adv, disadvantage=dis)
            st.session_state["log"].insert(0, f"🎲 {current.name}: {format_roll(rr)}")
            st.rerun()

        dmg_expr = st.text_input("Dano (ex.: 1d8+3)", value="1d6+0", key="quick_dmg")
        if st.button("Rolar dano", key="quick_dmg_btn", use_container_width=True):
            rr = roll_dice(dmg_expr)
            st.session_state["log"].insert(0, f"💥 {current.name}: {format_roll(rr)}")
            st.rerun()

    with c3:
        st.markdown("### Mídia (vinda da página Mídia)")
        media = st.session_state.get("media", {})
        if media.get("video"):
            st.video(media["video"])
        else:
            st.caption("Nenhum vídeo selecionado.")
        if media.get("audio"):
            st.audio(media["audio"])
        else:
            st.caption("Nenhum áudio selecionado.")

else:
    st.info("Adicione combatentes para aparecer o painel de turno.")

st.divider()
st.subheader("📜 Log")
for line in st.session_state.get("log", [])[:200]:
    st.markdown(line)
