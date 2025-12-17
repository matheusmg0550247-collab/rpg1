# -*- coding: utf-8 -*-
import base64
import streamlit as st
import uuid
from pathlib import Path

from rpg.storage import (
    ensure_dirs,
    list_character_ids,
    load_character,
    save_character,
    delete_character,
    PORTRAIT_DIR,
)
from rpg.pdf_import import import_character_from_pdf
from rpg.utils import ability_mod, proficiency_bonus
from rpg.dice import roll_d20, roll_expr, critify, fmt_d20, fmt_expr

ensure_dirs()

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


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def _b64decode(s: str) -> bytes:
    return base64.b64decode(s.encode("utf-8"))


def _log(line: str) -> None:
    st.session_state["log"].insert(0, line)


def _ensure_selected_id() -> None:
    ids = list_character_ids()
    if "selected_char_id" not in st.session_state:
        st.session_state["selected_char_id"] = ids[0] if ids else None
        return
    if st.session_state["selected_char_id"] is None and ids:
        st.session_state["selected_char_id"] = ids[0]
        return
    if st.session_state["selected_char_id"] is not None and st.session_state["selected_char_id"] not in ids:
        st.session_state["selected_char_id"] = ids[0] if ids else None


def _show_portrait(ch) -> None:
    # prioridade: b64 (persistente)
    if getattr(ch, "portrait_b64", None):
        try:
            st.image(_b64decode(ch.portrait_b64), use_container_width=True)
            return
        except Exception:
            pass
    # fallback: path
    p = getattr(ch, "portrait_path", None)
    if p and Path(p).exists():
        st.image(p, use_container_width=True)
    else:
        st.caption("📷 Sem foto")


def render():
    if "log" not in st.session_state:
        st.session_state["log"] = []

    _ensure_selected_id()

    # Regras rápidas (fica aqui na página)
    st.markdown("### 🧾 Ficha + Rolagens (clicáveis)")

    adv = st.checkbox("Vantagem", value=False)
    dis = st.checkbox("Desvantagem", value=False)
    target_ac = st.number_input("AC do alvo (0 = ignorar)", 0, 40, value=0, step=1)
    auto_damage = st.checkbox("Se acertar, rolar dano automático", value=True)

    roster, sheet, logcol = st.columns([0.22, 0.48, 0.30], gap="large")

    # ===== ROSTER =====
    with roster:
        st.markdown("### 👥 Jogadores")

        with st.expander("📥 Importar ficha por PDF", expanded=False):
            pdf = st.file_uploader("Envie o PDF da ficha", type=["pdf"])
            if pdf:
                new_id = uuid.uuid4().hex[:10]
                ch_new = import_character_from_pdf(pdf.getvalue(), new_id)
                st.success("Detectado: %s (%s)" % (ch_new.character_name, ch_new.class_and_level))
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
                ch_item = load_character(cid)
                if not ch_item:
                    continue

                confirm_key = "confirm_delete_%s" % cid
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                with st.container(border=True):
                    _show_portrait(ch_item)
                    st.markdown("**%s**" % ch_item.character_name)
                    st.caption(ch_item.class_and_level)

                    colA, colB = st.columns([0.6, 0.4])

                    if colA.button("➡️ Abrir", key="open_%s" % cid, use_container_width=True):
                        st.session_state["selected_char_id"] = cid
                        st.rerun()

                    if not st.session_state[confirm_key]:
                        if colB.button("🗑️ Excluir", key="del_%s" % cid, use_container_width=True):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        c1, c2 = st.columns(2)
                        if c1.button("✅ Confirmar", key="del_yes_%s" % cid, use_container_width=True):
                            delete_character(cid)
                            if st.session_state.get("selected_char_id") == cid:
                                st.session_state["selected_char_id"] = None
                            st.session_state[confirm_key] = False
                            st.rerun()
                        if c2.button("Cancelar", key="del_no_%s" % cid, use_container_width=True):
                            st.session_state[confirm_key] = False
                            st.rerun()

    # ===== personagem selecionado =====
    cid = st.session_state.get("selected_char_id")
    ch = load_character(cid) if cid else None

    # ===== FICHA =====
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

            st.markdown("## 🧾 %s" % ch.character_name)
            st.caption("%s • %s • Nível %d • PB +%d" % (ch.species, ch.class_and_level, ch.level, pb))

            with st.expander("➡️ 📷 Foto do jogador/personagem", expanded=False):
                img = st.file_uploader("Enviar imagem (png/jpg)", type=["png", "jpg", "jpeg"], key="img_%s" % ch.id)
                if img:
                    img_bytes = img.getvalue()

                    # ✅ salva no JSON (persistente no Cloud)
                    ch.portrait_b64 = _b64encode(img_bytes)

                    # fallback: salva também em arquivo (útil local)
                    ext = "jpg"
                    if img.type == "image/png":
                        ext = "png"
                    out = PORTRAIT_DIR / f"{ch.id}.{ext}"
                    try:
                        out.write_bytes(img_bytes)
                        ch.portrait_path = str(out)
                    except Exception:
                        pass

                    save_character(ch)
                    st.success("Foto salva!")
                    st.rerun()

            with st.expander("➡️ Atributos (clique para rolar)", expanded=True):
                cols = st.columns(6)
                abs_ = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
                for i, ab in enumerate(abs_):
                    with cols[i]:
                        score = getattr(ch, "%s_score" % ab.lower())
                        mod = mods[ab]
                        st.markdown("**%s**  \n%s" % (ab, score))
                        if st.button("%+d" % mod, key="abil_%s_%s" % (ab, ch.id)):
                            rr = roll_d20(bonus=mod, advantage=adv, disadvantage=dis)
                            _log("🧠 **%s** — %s Check: %s" % (ch.character_name, ab, fmt_d20(rr)))
                            st.rerun()

            with st.expander("➡️ Ataques (com regras)", expanded=False):
                if not ch.weapons:
                    st.info("Sem armas cadastradas na ficha.")
                else:
                    for idx, w in enumerate(ch.weapons):
                        r = st.columns([0.50, 0.18, 0.32])
                        r[0].write("**%s** — %s (%s)" % (w.name, w.damage, w.damage_type))

                        if r[1].button("%+d" % int(w.attack_bonus), key="atk_%d_%s" % (idx, ch.id)):
                            rr = roll_d20(bonus=int(w.attack_bonus), advantage=adv, disadvantage=dis)
                            nat = rr["chosen"]
                            total = rr["total"]

                            if nat == 1:
                                outcome = "❌ MISS (nat 1)"
                                hit = False
                                crit = False
                            elif nat == 20:
                                outcome = "💥 CRIT (nat 20)"
                                hit = True
                                crit = True
                            else:
                                if target_ac and total >= int(target_ac):
                                    outcome = f"✅ HIT vs AC {int(target_ac)}"
                                    hit = True
                                    crit = False
                                elif target_ac:
                                    outcome = f"❌ MISS vs AC {int(target_ac)}"
                                    hit = False
                                    crit = False
                                else:
                                    outcome = "🎲 Rolado (sem AC)"
                                    hit = True
                                    crit = False

                            _log("🗡️ **%s** — Attack (%s): %s → %s" % (ch.character_name, w.name, fmt_d20(rr), outcome))

                            if hit and auto_damage:
                                dmg_expr = critify(w.damage) if crit else w.damage
                                dr = roll_expr(dmg_expr)
                                tag = " (CRIT dmg)" if crit else ""
                                _log("💥 **%s** — Damage %s%s: %s" % (ch.character_name, w.name, tag, fmt_expr(dr)))

                            st.rerun()

                        if r[2].button("🎯 Dano", key="dmg_%d_%s" % (idx, ch.id)):
                            dr = roll_expr(w.damage)
                            _log("💥 **%s** — Damage %s: %s" % (ch.character_name, w.name, fmt_expr(dr)))
                            st.rerun()

            with st.expander("➡️ Equipamentos", expanded=False):
                text = "\n".join(getattr(ch, "equipment", []) or [])
                new_text = st.text_area("Lista (1 item por linha)", value=text, height=220, key="equip_%s" % ch.id)
                if st.button("💾 Salvar equipamentos", key="save_equip_%s" % ch.id, use_container_width=True):
                    ch.equipment = [x.strip() for x in new_text.splitlines() if x.strip()]
                    save_character(ch)
                    st.success("Equipamentos salvos!")
                    st.rerun()

    # ===== LOG =====
    with logcol:
        st.markdown("### 📜 Log")
        if st.button("Limpar log", use_container_width=True):
            st.session_state["log"] = []
            st.rerun()
        for line in st.session_state["log"][:250]:
            st.markdown(line)
