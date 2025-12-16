import streamlit as st
import uuid
from pathlib import Path

from rpg.storage import ensure_dirs, list_character_ids, load_character, save_character, PORTRAIT_DIR
from rpg.pdf_import import import_character_from_pdf
from rpg.utils import ability_mod, proficiency_bonus
from rpg.dice import roll_d20, roll_expr, critify, fmt_d20, fmt_expr

SKILLS = {
    "Athletics": "STR",
    "Acrobatics": "DEX",
    "Sleight of Hand": "DEX",
    "Stealth": "DEX",
    "Arcana": "INT",
    "History": "INT",
    "Investigation": "INT",
    "Nature": "INT",
    "Religion": "INT",
    "Animal Handling": "WIS",
    "Insight": "WIS",
    "Medicine": "WIS",
    "Perception": "WIS",
    "Survival": "WIS",
    "Deception": "CHA",
    "Intimidation": "CHA",
    "Performance": "CHA",
    "Persuasion": "CHA",
}

ensure_dirs()

def _log(line: str) -> None:
    st.session_state["log"].insert(0, line)

def render():
    if "log" not in st.session_state:
        st.session_state["log"] = []
    if "selected_char_id" not in st.session_state:
        ids = list_character_ids()
        st.session_state["selected_char_id"] = ids[0] if ids else None

    with st.sidebar:
        st.markdown("### 🎲 Regras rápidas")
        adv = st.checkbox("Vantagem", value=False)
        dis = st.checkbox("Desvantagem", value=False)
        target_ac = st.number_input("AC do alvo (0 = ignorar)", 0, 40, value=0, step=1)
        auto_damage = st.checkbox("Se acertar, rolar dano automático", value=True)

    st.markdown("### 🧾 Ficha + Rolagens (clicáveis)")

    roster, sheet, logcol = st.columns([0.22, 0.48, 0.30], gap="large")

    # ROSTER + IMPORT
    with roster:
        st.markdown("### 👥 Jogadores")

        with st.expander("📥 Importar ficha por PDF", expanded=False):
            pdf = st.file_uploader("Envie o PDF da ficha", type=["pdf"])
            if pdf:
                new_id = uuid.uuid4().hex[:10]
                ch_new = import_character_from_pdf(pdf.getvalue(), new_id)
                st.success(f"Detectado: {ch_new.character_name} ({ch_new.class_and_level})")
                if st.button("✅ Salvar como nova ficha", use_container_width=True):
                    save_character(ch_new)
                    st.session_state["selected_char_id"] = ch_new.id
                    st.rerun()

        st.divider()

        ids = list_character_ids()
        if not ids:
            st.info("Sem fichas ainda. Importe um PDF acima.")
        else:
            for cid in ids:
                ch = load_character(cid)
                if not ch:
                    continue
                with st.container(border=True):
                    portrait = getattr(ch, "portrait_path", None)
                    if portrait and Path(portrait).exists():
                        st.image(portrait, use_container_width=True)
                    else:
                        st.caption("📷 Sem foto")

                    st.markdown(f"**{ch.character_name}**")
                    st.caption(ch.class_and_level)

                    if st.button("➡️ Abrir", key=f"open_{cid}", use_container_width=True):
                        st.session_state["selected_char_id"] = cid
                        st.rerun()

    # PERSONAGEM SELECIONADO
    cid = st.session_state.get("selected_char_id")
    ch = load_character(cid) if cid else None

    with sheet:
        if not ch:
            st.info("Selecione um jogador à esquerda.")
        else:
            pb = proficiency_bonus(ch.level)
            mods = {
                "STR": ability_mod(ch.str_score),
                "DEX": ability_mod(ch.dex_score),
                "CON": ability_mod(ch.con_score),
                "INT": ability_mod(ch.int_score),
                "WIS": ability_mod(ch.wis_score),
                "CHA": ability_mod(ch.cha_score),
            }

            st.markdown(f"## 🧾 {ch.character_name}")
            st.caption(f"{ch.species} • {ch.class_and_level} • Nível {ch.level} • PB +{pb}")

            with st.expander("➡️ 📷 Foto do jogador/personagem", expanded=False):
                img = st.file_uploader("Enviar imagem (png/jpg)", type=["png", "jpg", "jpeg"], key=f"img_{ch.id}")
                if img:
                    out = PORTRAIT_DIR / f"{ch.id}.png"
                    out.write_bytes(img.getvalue())
                    ch.portrait_path = str(out)
                    save_character(ch)
                    st.success("Foto salva!")
                    st.rerun()

            with st.expander("➡️ Atributos (clique para rolar)", expanded=True):
                cols = st.columns(6)
                for ab in ["STR","DEX","CON","INT","WIS","CHA"]:
                    with cols[["STR","DEX","CON","INT","WIS","CHA"].index(ab)]:
                        score = getattr(ch, f"{ab.lower()}_score")
                        mod = mods[ab]
                        st.markdown(f"**{ab}**  \n{score}")
                        if st.button(f"{mod:+d}", key=f"abil_{ab}_{ch.id}"):
                            rr = roll_d20(bonus=mod, advantage=adv, disadvantage=dis)
                            _log(f"🧠 **{ch.character_name}** — {ab} Check: {fmt_d20(rr)}")
                            st.rerun()

            with st.expander("➡️ Perícias (clique para rolar)", expanded=False):
                for skill, ab in SKILLS.items():
                    prof = skill in (ch.skill_proficiencies or [])
                    bonus = mods[ab] + (pb if prof else 0)
                    r = st.columns([0.55, 0.2, 0.25])
                    r[0].write(f"{skill} *( {ab} )*")
                    if r[1].button(f"{bonus:+d}", key=f"skill_{skill}_{ch.id}"):
                        rr = roll_d20(bonus=bonus, advantage=adv, disadvantage=dis)
                        tag = " (PROF)" if prof else ""
