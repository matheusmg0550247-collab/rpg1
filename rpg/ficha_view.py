from __future__ import annotations

import base64
from typing import Optional, Dict, Any, List

import streamlit as st

from rpg.models import Character
from rpg.storage import (
    ensure_dirs,
    list_character_ids,
    load_character,
    save_character,
    delete_character,
)
from rpg.pdf_import import import_character_from_pdf
from rpg.dice import roll_d20, roll_expr, fmt_d20, fmt_expr


ensure_dirs()


def _ability_mod(score: int) -> int:
    return (score - 10) // 2


def _img_bytes_from_b64(b64: Optional[str]) -> Optional[bytes]:
    if not b64:
        return None
    try:
        return base64.b64decode(b64.encode("utf-8"))
    except Exception:
        return None


def render() -> None:
    st.markdown("## 🧾 Ficha + Rolagens (clicáveis)")

    if "log" not in st.session_state:
        st.session_state["log"] = []
    if "selected_char_id" not in st.session_state:
        st.session_state["selected_char_id"] = None

    def log(line: str) -> None:
        st.session_state["log"].insert(0, line)

    # coluna 1 = roster/import | coluna 2 = ficha | coluna 3 = log
    col_roster, col_sheet, col_log = st.columns([0.23, 0.52, 0.25], gap="large")

    # ====== ROSTER / IMPORT ======
    with col_roster:
        st.markdown("### 👥 Jogadores")

        with st.expander("📥 Importar ficha por PDF", expanded=False):
            up = st.file_uploader("Envie o PDF da ficha", type=["pdf"], key="pdf_upload")
            if up is not None:
                pdf_bytes = up.getvalue()
                ch = import_character_from_pdf(pdf_bytes)

                st.success(f"Detectado: **{ch.character_name}** ({ch.class_and_level})")
                if st.button("✅ Salvar como nova ficha", use_container_width=True):
                    save_character(ch)
                    st.session_state["selected_char_id"] = ch.id
                    log(f"📥 Importado PDF: **{ch.character_name}**")
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
                    img = _img_bytes_from_b64(getattr(ch, "portrait_b64", None))
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.caption("📷 Sem foto")

                    st.markdown(f"**{ch.character_name}**")
                    st.caption(ch.class_and_level or ch.species or "—")

                    b1, b2 = st.columns(2)
                    if b1.button("➡️ Abrir", key=f"open_{cid}", use_container_width=True):
                        st.session_state["selected_char_id"] = cid
                        st.rerun()
                    if b2.button("🗑️ Excluir", key=f"del_{cid}", use_container_width=True):
                        delete_character(cid)
                        if st.session_state.get("selected_char_id") == cid:
                            st.session_state["selected_char_id"] = None
                        st.rerun()

    # ====== FICHA ======
    with col_sheet:
        cid = st.session_state.get("selected_char_id")
        ch: Optional[Character] = load_character(cid) if cid else None

        if not ch:
            st.info("Selecione um jogador à esquerda.")
        else:
            st.markdown(f"## 📄 {ch.character_name}")
            sub = []
            if ch.species:
                sub.append(ch.species)
            if ch.class_and_level:
                sub.append(ch.class_and_level)
            if ch.alignment:
                sub.append(ch.alignment)
            if ch.prof_bonus:
                sub.append(f"PB +{ch.prof_bonus}")
            st.caption(" • ".join(sub) if sub else "—")

            # métricas
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("CA", ch.ac)
            m2.metric("HP", f"{ch.current_hp}/{ch.max_hp}")
            m3.metric("Desloc.", f"{ch.speed} ft" if isinstance(ch.speed, int) else str(ch.speed))
            m4.metric("Iniciativa", f"+{ch.initiative_bonus}" if ch.initiative_bonus >= 0 else str(ch.initiative_bonus))

            # FOTO
            with st.expander("🖼️ Foto do jogador/personagem", expanded=False):
                up_img = st.file_uploader("Enviar imagem (png/jpg)", type=["png", "jpg", "jpeg"], key=f"img_{ch.id}")
                if up_img is not None:
                    b = up_img.getvalue()
                    ch.portrait_b64 = base64.b64encode(b).decode("utf-8")
                    save_character(ch)
                    st.success("Foto salva na ficha.")
                    st.rerun()

                img = _img_bytes_from_b64(ch.portrait_b64)
                if img:
                    st.image(img, use_container_width=True)

            # PERSONALIDADE / BACKGROUND
            with st.expander("🧠 Personalidade / Ideais / Laços / Defeitos", expanded=False):
                if ch.personality_traits:
                    st.markdown(f"**Traços:** {ch.personality_traits}")
                if ch.ideals:
                    st.markdown(f"**Ideais:** {ch.ideals}")
                if ch.bonds:
                    st.markdown(f"**Laços:** {ch.bonds}")
                if ch.flaws:
                    st.markdown(f"**Defeitos:** {ch.flaws}")
                if not (ch.personality_traits or ch.ideals or ch.bonds or ch.flaws):
                    st.caption("—")

            # CARACTERÍSTICAS (MD)
            with st.expander("📚 Características (Raça / Antecedente / Classe)", expanded=False):
                ch.race_notes_md = st.text_area("Raça / Legado (Markdown)", value=ch.race_notes_md or "", height=140, key=f"race_md_{ch.id}")
                ch.background_notes_md = st.text_area("Antecedente / Proficiências (Markdown)", value=ch.background_notes_md or "", height=140, key=f"bg_md_{ch.id}")
                ch.class_notes_md = st.text_area("Classe / Features (Markdown)", value=ch.class_notes_md or "", height=180, key=f"class_md_{ch.id}")

                if st.button("💾 Salvar características", use_container_width=True, key=f"save_md_{ch.id}"):
                    save_character(ch)
                    st.success("Salvo.")
                    st.rerun()

            with st.expander("📖 Ver características (modo leitura)", expanded=False):
                if ch.race_notes_md.strip():
                    st.markdown("### Raça / Legado")
                    st.markdown(ch.race_notes_md)
                if ch.background_notes_md.strip():
                    st.markdown("### Antecedente")
                    st.markdown(ch.background_notes_md)
                if ch.class_notes_md.strip():
                    st.markdown("### Classe")
                    st.markdown(ch.class_notes_md)
                if not (ch.race_notes_md.strip() or ch.background_notes_md.strip() or ch.class_notes_md.strip()):
                    st.caption("—")

            # ATRIBUTOS (clicáveis)
            with st.expander("🧬 Atributos (clique para rolar)", expanded=True):
                abilities = [
                    ("STR", ch.str_score),
                    ("DEX", ch.dex_score),
                    ("CON", ch.con_score),
                    ("INT", ch.int_score),
                    ("WIS", ch.wis_score),
                    ("CHA", ch.cha_score),
                ]
                cols = st.columns(6)
                for i, (abv, score) in enumerate(abilities):
                    mod = _ability_mod(score)
                    cols[i].markdown(f"**{abv}**  \n{score}")
                    if cols[i].button(f"{mod:+d}", key=f"ab_{abv}_{ch.id}", use_container_width=True):
                        rr = roll_d20(bonus=mod)
                        log(f"🧬 **{ch.character_name}** — {abv} check: {fmt_d20(rr)}")
                        st.rerun()

            # SAVES (do PDF, prontos)
            with st.expander("🛡️ Testes de Resistência (do PDF)", expanded=False):
                if not ch.save_mods:
                    st.caption("Sem saves importados do PDF.")
                else:
                    c = st.columns(6)
                    for i, abv in enumerate(["STR", "DEX", "CON", "INT", "WIS", "CHA"]):
                        bonus = ch.save_mods.get(abv, 0)
                        if c[i].button(f"{abv} {bonus:+d}", key=f"save_{abv}_{ch.id}", use_container_width=True):
                            rr = roll_d20(bonus=bonus)
                            log(f"🛡️ **{ch.character_name}** — Save {abv}: {fmt_d20(rr)}")
                            st.rerun()

            # SKILLS (do PDF, prontos)
            with st.expander("🎯 Perícias (do PDF)", expanded=False):
                if not ch.skill_mods:
                    st.caption("Sem perícias importadas do PDF.")
                else:
                    items = sorted(ch.skill_mods.items(), key=lambda x: x[0].lower())
                    for skill, bonus in items:
                        if st.button(f"{skill} {bonus:+d}", key=f"skill_{skill}_{ch.id}", use_container_width=True):
                            rr = roll_d20(bonus=bonus)
                            log(f"🎯 **{ch.character_name}** — {skill}: {fmt_d20(rr)}")
                            st.rerun()

            # ATAQUES
            with st.expander("⚔️ Ataques (roláveis)", expanded=False):
                if not ch.weapons:
                    st.caption("Sem armas importadas.")
                for w in ch.weapons:
                    row = st.columns([0.52, 0.24, 0.24])
                    row[0].markdown(f"**{w.name}**  \nDano: `{w.damage}`")
                    if row[1].button(f"🎯 Ataque +{w.attack_bonus}", key=f"atk_{ch.id}_{w.name}", use_container_width=True):
                        rr = roll_d20(bonus=w.attack_bonus)
                        log(f"🎯 **{ch.character_name}** — {w.name}: {fmt_d20(rr)}")
                        st.rerun()
                    if row[2].button("💥 Dano", key=f"dmg_{ch.id}_{w.name}", use_container_width=True):
                        dr = roll_expr(w.damage)
                        log(f"💥 **{ch.character_name}** — Dano {w.name}: {fmt_expr(dr)}")
                        st.rerun()

            # EQUIPAMENTOS
            with st.expander("🎒 Equipamentos", expanded=False):
                if ch.equipment:
                    for it in ch.equipment:
                        st.write(f"• {it}")
                else:
                    st.caption("—")

            # MAGIAS
            with st.expander("✨ Magias (importadas do PDF)", expanded=False):
                meta = ch.spellcasting_meta or {}
                if meta:
                    st.markdown("**Spellcasting**")
                    for k, v in meta.items():
                        st.write(f"- {k}: {v}")

                if ch.spell_slots_total:
                    st.markdown("**Slots**")
                    # mostra em linha (1..9)
                    cols = st.columns(9)
                    for i in range(1, 10):
                        lvl = str(i)
                        t = ch.spell_slots_total.get(lvl, 0)
                        r = ch.spell_slots_remaining.get(lvl, 0)
                        txt = f"{r}/{t}" if r else f"{t}"
                        cols[i-1].metric(f"{i}º", txt)

                if ch.spells:
                    st.markdown(f"**Lista de magias ({len(ch.spells)})**")
                    for s in ch.spells:
                        st.write(f"• {s}")
                else:
                    st.caption("Sem magias preenchidas no PDF.")

            # DUMP COMPLETO DO PDF
            with st.expander("📄 Campos do PDF (100%) — busca", expanded=False):
                q = st.text_input("Filtrar por texto (campo ou valor)", value="", key=f"pdf_filter_{ch.id}")
                items = list(ch.raw_pdf_fields.items()) if ch.raw_pdf_fields else []
                if q.strip():
                    qq = q.strip().lower()
                    items = [(k, v) for (k, v) in items if qq in k.lower() or qq in (v or "").lower()]

                st.caption(f"Mostrando {len(items)} campos.")
                data = [{"campo": k, "valor": v} for k, v in items[:500]]
                st.dataframe(data, use_container_width=True, hide_index=True)

    # ====== LOG ======
    with col_log:
        st.markdown("### 📜 Log")
        if st.button("Limpar log", use_container_width=True):
            st.session_state["log"] = []
            st.rerun()

        for line in st.session_state["log"][:250]:
            st.markdown(line)
