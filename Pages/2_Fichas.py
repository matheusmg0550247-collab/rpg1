import streamlit as st
import uuid
import pandas as pd
from rpg.models import Character, Weapon
from rpg.storage import list_character_ids, load_character, save_character, delete_character
from rpg.utils import ability_mod, proficiency_bonus

st.title("🧾 Fichas")

ids = list_character_ids()

left, right = st.columns([0.42, 0.58], gap="large")

with left:
    st.subheader("Personagens")
    options = ["(novo)"] + ids
    pick = st.selectbox("Selecione", options)

    if pick != "(novo)":
        ch = load_character(pick)
        if ch is None:
            st.error("Não consegui carregar esse personagem.")
        else:
            st.success(f"Carregado: {ch.character_name}")
            if st.button("🗑️ Excluir personagem", use_container_width=True):
                delete_character(ch.id)
                st.rerun()
    else:
        ch = None

with right:
    st.subheader("Editar / Criar")
    with st.form("char_form", clear_on_submit=False):
        character_name = st.text_input("Character Name", value=(ch.character_name if ch else ""))
        player_name = st.text_input("Player Name", value=(ch.player_name if ch else ""))
        species = st.text_input("Species", value=(ch.species if ch else ""))
        class_and_level = st.text_input("Class & Level", value=(ch.class_and_level if ch else ""))
        background = st.text_input("Background", value=(ch.background if ch else ""))
        level = st.number_input("Level", min_value=1, max_value=20, value=(ch.level if ch else 1), step=1)

        c1, c2, c3 = st.columns(3)
        with c1:
            str_score = st.number_input("STR", 1, 30, value=(ch.str_score if ch else 10))
            dex_score = st.number_input("DEX", 1, 30, value=(ch.dex_score if ch else 10))
        with c2:
            con_score = st.number_input("CON", 1, 30, value=(ch.con_score if ch else 10))
            int_score = st.number_input("INT", 1, 30, value=(ch.int_score if ch else 10))
        with c3:
            wis_score = st.number_input("WIS", 1, 30, value=(ch.wis_score if ch else 10))
            cha_score = st.number_input("CHA", 1, 30, value=(ch.cha_score if ch else 10))

        c4, c5, c6, c7 = st.columns(4)
        with c4:
            ac = st.number_input("AC", 1, 40, value=(ch.ac if ch else 10))
        with c5:
            speed = st.number_input("Speed", 0, 120, value=(ch.speed if ch else 30))
        with c6:
            max_hp = st.number_input("Max HP", 1, 999, value=(ch.max_hp if ch else 10))
        with c7:
            initiative_bonus = st.number_input("Init Bonus", -20, 20, value=(ch.initiative_bonus if ch else 0))

        # Weapons (bem simples)
        st.markdown("### ⚔️ Armas (simples)")
        wname = st.text_input("Nome da arma", value=(ch.weapons[0].name if ch and ch.weapons else "Longsword"))
        wbonus = st.number_input("Bônus de ataque", -20, 20, value=(ch.weapons[0].attack_bonus if ch and ch.weapons else 0))
        wdamage = st.text_input("Dano (ex.: 1d8+3)", value=(ch.weapons[0].damage if ch and ch.weapons else "1d8+0"))
        wtype = st.text_input("Tipo de dano", value=(ch.weapons[0].damage_type if ch and ch.weapons else "slashing"))

        submitted = st.form_submit_button("💾 Salvar", use_container_width=True)

    if submitted:
        char_id = ch.id if ch else uuid.uuid4().hex[:10]
        weapons = [Weapon(name=wname, attack_bonus=int(wbonus), damage=wdamage, damage_type=wtype)]
        new_ch = Character(
            id=char_id,
            character_name=character_name,
            player_name=player_name,
            species=species,
            class_and_level=class_and_level,
            background=background,
            level=int(level),
            str_score=int(str_score),
            dex_score=int(dex_score),
            con_score=int(con_score),
            int_score=int(int_score),
            wis_score=int(wis_score),
            cha_score=int(cha_score),
            ac=int(ac),
            speed=int(speed),
            max_hp=int(max_hp),
            current_hp=int(max_hp),
            initiative_bonus=int(initiative_bonus),
            weapons=weapons,
        )
        save_character(new_ch)
        st.success("Salvo!")
        st.rerun()

    # Preview
    if ch:
        st.divider()
        st.subheader("📌 Resumo")
        pb = proficiency_bonus(ch.level)
        st.write(f"**PB:** +{pb}  |  **AC:** {ch.ac}  |  **Speed:** {ch.speed}  |  **HP:** {ch.current_hp}/{ch.max_hp}")

        mods = {
            "STR": ability_mod(ch.str_score),
            "DEX": ability_mod(ch.dex_score),
            "CON": ability_mod(ch.con_score),
            "INT": ability_mod(ch.int_score),
            "WIS": ability_mod(ch.wis_score),
            "CHA": ability_mod(ch.cha_score),
        }
        df = pd.DataFrame([{"Ability": k, "Score": getattr(ch, f"{k.lower()}_score"), "Mod": f"{v:+d}"} for k, v in mods.items()])
        st.dataframe(df, use_container_width=True, hide_index=True)

        if ch.weapons:
            w = ch.weapons[0]
            st.markdown(f"**Arma:** {w.name}  |  **Ataque:** +{w.attack_bonus}  |  **Dano:** {w.damage} ({w.damage_type})")
