import streamlit as st
from rpg.storage import list_character_ids, load_character, save_character
from rpg.utils import ability_mod, proficiency_bonus
from rpg.dice import roll_d20, roll_expr, critify, fmt_d20, fmt_expr
from rpg.models import Weapon

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

ABIL_FIELDS = {
    "STR": "str_score",
    "DEX": "dex_score",
    "CON": "con_score",
    "INT": "int_score",
    "WIS": "wis_score",
    "CHA": "cha_score",
}

def _log(line: str):
    st.session_state["log"].insert(0, line)

def render():
    st.subheader("🧾 Ficha (clicável) + Log")

    if "log" not in st.session_state:
        st.session_state["log"] = []

    left, right = st.columns([0.60, 0.40], gap="large")

    # ====== Sidebar (controles) ======
    with st.sidebar:
        st.subheader("Personagem")
        ids = list_character_ids()
        if not ids:
            st.warning("Sem fichas em data/characters/. Coloque um JSON lá.")
            return

        pick = st.selectbox("Selecione", ids)
        ch = load_character(pick)
        if not ch:
            st.error("Não consegui carregar a ficha.")
            return

        st.divider()
        st.subheader("Regras de rolagem")
        adv = st.checkbox("Vantagem", value=False)
        dis = st.checkbox("Desvantagem", value=False)
        target_ac = st.number_input("AC do alvo (0 = ignorar)", 0, 40, value=0, step=1)
        auto_damage = st.checkbox("Se acertar, rolar dano automático", value=True)

        st.divider()
        with st.expander("Editar rápido"):
            ch.character_name = st.text_input("Nome", value=ch.character_name)
            ch.level = st.number_input("Nível", 1, 20, value=int(ch.level))
            ch.ac = st.number_input("AC", 1, 40, value=int(ch.ac))
            ch.max_hp = st.number_input("Max HP", 1, 999, value=int(ch.max_hp))
            ch.current_hp = st.number_input("HP atual", 0, int(ch.max_hp), value=int(ch.current_hp))
            ch.initiative_bonus = st.number_input("Bônus iniciativa", -20, 20, value=int(ch.initiative_bonus))

            if not ch.weapons:
                ch.weapons = [Weapon(name="Longsword", attack_bonus=5, damage="1d8+3", damage_type="slashing")]

            w = ch.weapons[0]
            st.markdown("**Arma 1**")
            w.name = st.text_input("Nome arma", value=w.name)
            w.attack_bonus = st.number_input("Ataque (bônus total)", -20, 20, value=int(w.attack_bonus))
            w.damage = st.text_input("Dano", value=w.damage)
            w.damage_type = st.text_input("Tipo", value=w.damage_type)

            if st.button("💾 Salvar ficha"):
                save_character(ch)
                st.success("Salvo!")

    # ====== cálculos ======
    pb = proficiency_bonus(ch.level)
    mods = {k: ability_mod(getattr(ch, ABIL_FIELDS[k])) for k in ABIL_FIELDS}

    # ====== FICHA (esquerda) ======
    with left:
        st.markdown(f"## {ch.character_name}")
        st.caption(f"{ch.species} • {ch.class_and_level} • Nível {ch.level} • PB +{pb}")

        a, b, c, d = st.columns(4)
        a.metric("AC", ch.ac)
        b.metric("Speed", ch.speed)
        c.metric("HP", f"{ch.current_hp}/{ch.max_hp}")
        d.metric("Init", f"{ch.initiative_bonus:+d}")

        st.divider()
        st.markdown("### Atributos (clique para rolar)")
        cols = st.columns(6)
        for i, ab in enumerate(["STR","DEX","CON","INT","WIS","CHA"]):
            with cols[i]:
                score = getattr(ch, ABIL_FIELDS[ab])
                mod = mods[ab]
                st.markdown(f"**{ab}**  \n{score}")
                if st.button(f"{mod:+d}", key=f"abil_{ab}"):
                    rr = roll_d20(bonus=mod, advantage=adv, disadvantage=dis)
                    _log(f"🧠 **{ch.character_name}** — {ab} Check: {fmt_d20(rr)}")
                    st.rerun()

                save_prof = ab in (ch.save_proficiencies or [])
                save_bonus = mod + (pb if save_prof else 0)
                if st.button(f"Save {save_bonus:+d}", key=f"save_{ab}"):
                    rr = roll_d20(bonus=save_bonus, advantage=adv, disadvantage=dis)
                    tag = " (PROF)" if save_prof else ""
                    _log(f"🛡️ **{ch.character_name}** — {ab} Save{tag}: {fmt_d20(rr)}")
                    st.rerun()

        st.divider()
        st.markdown("### Perícias (clique para rolar)")
        for skill, ab in SKILLS.items():
            prof = skill in (ch.skill_proficiencies or [])
            bonus = mods[ab] + (pb if prof else 0)
            r = st.columns([0.55, 0.2, 0.25])
            r[0].write(f"{skill} *( {ab} )*")
            if r[1].button(f"{bonus:+d}", key=f"skill_{skill}"):
                rr = roll_d20(bonus=bonus, advantage=adv, disadvantage=dis)
                tag = " (PROF)" if prof else ""
                _log(f"🎯 **{ch.character_name}** — {skill}{tag}: {fmt_d20(rr)}")
                st.rerun()
            r[2].write("✅" if prof else "")

        st.divider()
        st.markdown("### Ataques (com regras)")
        for idx, w in enumerate(ch.weapons or []):
            r = st.columns([0.48, 0.18, 0.34])
            r[0].write(f"**{w.name}**  \n{w.damage} ({w.damage_type})")

            if r[1].button(f"{int(w.attack_bonus):+d}", key=f"atk_{idx}"):
                rr = roll_d20(bonus=int(w.attack_bonus), advantage=adv, disadvantage=dis)
                nat = rr["chosen"]
                total = rr["total"]

                # regras de acerto
                if nat == 1:
                    outcome = "❌ **MISS (nat 1)**"
                    hit = False
                    crit = False
                elif nat == 20:
                    outcome = "💥 **CRIT (nat 20)**"
                    hit = True
                    crit = True
                else:
                    if target_ac and total >= int(target_ac):
                        outcome = f"✅ **HIT** vs AC {int(target_ac)}"
                        hit = True
                        crit = False
                    elif target_ac:
                        outcome = f"❌ **MISS** vs AC {int(target_ac)}"
                        hit = False
                        crit = False
                    else:
                        outcome = "🎲 **Rolado (sem AC)**"
                        hit = True
                        crit = False

                _log(f"🗡️ **{ch.character_name}** — Attack ({w.name}): {fmt_d20(rr)} → {outcome}")

                if hit and auto_damage:
                    dmg_expr = critify(w.damage) if crit else w.damage
                    dr = roll_expr(dmg_expr)
                    tag = " (CRIT dmg)" if crit else ""
                    _log(f"💥 **{ch.character_name}** — Damage {w.name}{tag}: {fmt_expr(dr)}")

                st.rerun()

            if r[2].button("🎯 Dano", key=f"dmg_{idx}"):
                dr = roll_expr(w.damage)
                _log(f"💥 **{ch.character_name}** — Damage {w.name}: {fmt_expr(dr)}")
                st.rerun()

    # ====== LOG (direita) ======
    with right:
        st.markdown("### 📜 Log")
        if st.button("Limpar log", use_container_width=True):
            st.session_state["log"] = []
            st.rerun()

        for line in st.session_state["log"][:250]:
            st.markdown(line)
