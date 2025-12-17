# -*- coding: utf-8 -*-
import json
import uuid
import streamlit as st

from rpg.models import Monster, MonsterAction
from rpg.storage import (
    ensure_dirs,
    list_monster_ids,
    load_monster,
    save_monster,
    delete_monster,
)
from rpg.dice import roll_d20, roll_expr, critify, fmt_d20, fmt_expr

ensure_dirs()


def _require_password() -> bool:
    """
    Proteção simples por senha (não é criptografia, mas serve como gate no app).
    Configure MONSTER_PASSWORD em Streamlit Cloud -> Secrets.
    """
    if st.session_state.get("monsters_authed") is True:
        return True

    pwd = None
    try:
        pwd = st.secrets.get("MONSTER_PASSWORD")
    except Exception:
        pwd = None

    if not pwd:
        st.error("MONSTER_PASSWORD não configurado. Defina nos Secrets do Streamlit Cloud.")
        st.info('Em Streamlit Cloud: App → Settings → Secrets → MONSTER_PASSWORD="sua_senha"')
        return False

    st.markdown("## 🔒 Área Protegida — Monstros")
    typed = st.text_input("Senha", type="password")
    cols = st.columns([0.25, 0.75])
    if cols[0].button("Entrar", use_container_width=True):
        if typed == pwd:
            st.session_state["monsters_authed"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    return False


def _sample_monster() -> Monster:
    return Monster(
        id=uuid.uuid4().hex[:10],
        name="Hobgoblin da Mão de Ferro (Batedor)",
        size="Medium",
        creature_type="humanoid (hobgoblin)",
        alignment="lawful evil",
        ac=15,
        max_hp=22,
        current_hp=22,
        speed="30 ft.",
        str_score=13,
        dex_score=14,
        con_score=12,
        int_score=10,
        wis_score=11,
        cha_score=9,
        skills=["Perception +2", "Stealth +4"],
        senses="darkvision 60 ft.",
        languages="Common, Goblin",
        cr="1",
        traits_md="- **Disciplina de Legião:** enquanto estiver a 5 ft. de um aliado, ganha +1 AC.\n- **Tática de Emboscada:** na primeira rodada, tem vantagem no primeiro ataque se não foi visto.",
        actions=[
            MonsterAction(
                name="Espada Curta",
                to_hit=4,
                damage="1d6+2",
                damage_type="piercing",
                description="Ataque corpo a corpo. Se acertar, causa dano perfurante."
            ),
            MonsterAction(
                name="Arco Curto",
                to_hit=4,
                damage="1d6+2",
                damage_type="piercing",
                description="Ataque à distância."
            ),
        ],
        notes_md="Modelo homebrew para o seu cenário (sem copiar livro).",
    )


def render() -> None:
    if not _require_password():
        return

    # header + logout
    top = st.columns([0.8, 0.2])
    top[0].markdown("### 👹 Monstros (Protegido)")
    if top[1].button("Sair", use_container_width=True):
        st.session_state["monsters_authed"] = False
        st.rerun()

    if "m_log" not in st.session_state:
        st.session_state["m_log"] = []

    def mlog(line: str) -> None:
        st.session_state["m_log"].insert(0, line)

    # controles rápidos
    with st.expander("🎲 Controles de rolagem", expanded=False):
        adv = st.checkbox("Vantagem", value=False, key="m_adv")
        dis = st.checkbox("Desvantagem", value=False, key="m_dis")
        target_ac = st.number_input("AC do alvo (0 = ignorar)", 0, 40, value=0, step=1, key="m_ac")
        auto_damage = st.checkbox("Se acertar, rolar dano automático", value=True, key="m_autodmg")

    left, mid, right = st.columns([0.22, 0.50, 0.28], gap="large")

    # ===== LEFT: roster + import =====
    with left:
        st.markdown("### 📚 Bestiário")

        with st.expander("➕ Criar monstro de exemplo", expanded=False):
            st.caption("Cria um monstro modelo (homebrew).")
            if st.button("Criar exemplo", use_container_width=True):
                m = _sample_monster()
                save_monster(m)
                st.session_state["selected_monster_id"] = m.id
                st.success("Exemplo criado!")
                st.rerun()

        with st.expander("📥 Importar monstro via JSON", expanded=False):
            up = st.file_uploader("Enviar JSON", type=["json"], key="m_json_file")
            pasted = st.text_area("...ou cole o JSON aqui", height=140, key="m_json_paste")

            raw = None
            if up:
                raw = up.getvalue().decode("utf-8", errors="ignore")
            elif pasted.strip():
                raw = pasted.strip()

            if raw:
                try:
                    data = json.loads(raw)
                    # se vier sem id, cria
                    if isinstance(data, dict) and "id" not in data:
                        data["id"] = uuid.uuid4().hex[:10]
                    m = Monster.model_validate(data)
                    st.success(f"OK: {m.name}")
                    if st.button("✅ Salvar monstro", use_container_width=True):
                        save_monster(m)
                        st.session_state["selected_monster_id"] = m.id
                        st.rerun()
                except Exception as e:
                    st.error("JSON inválido para Monster.")
                    st.exception(e)

        st.divider()

        ids = list_monster_ids()
        if not ids:
            st.info("Sem monstros ainda. Crie o exemplo ou importe um JSON.")
        else:
            for mid_ in ids:
                m = load_monster(mid_)
                if not m:
                    continue

                confirm_key = f"confirm_del_mon_{mid_}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False

                with st.container(border=True):
                    st.markdown(f"**{m.name}**")
                    st.caption(f"CA {m.ac} • HP {m.current_hp}/{m.max_hp} • CR {m.cr}")

                    c1, c2 = st.columns([0.6, 0.4])
                    if c1.button("➡️ Abrir", key=f"open_mon_{mid_}", use_container_width=True):
                        st.session_state["selected_monster_id"] = mid_
                        st.rerun()

                    if not st.session_state[confirm_key]:
                        if c2.button("🗑️ Excluir", key=f"del_mon_{mid_}", use_container_width=True):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        x1, x2 = st.columns(2)
                        if x1.button("✅ Confirmar", key=f"del_mon_yes_{mid_}", use_container_width=True):
                            delete_monster(mid_)
                            if st.session_state.get("selected_monster_id") == mid_:
                                st.session_state["selected_monster_id"] = None
                            st.session_state[confirm_key] = False
                            st.rerun()
                        if x2.button("Cancelar", key=f"del_mon_no_{mid_}", use_container_width=True):
                            st.session_state[confirm_key] = False
                            st.rerun()

    # ===== MID: ficha do monstro =====
    with mid:
        mid_ = st.session_state.get("selected_monster_id")
        m = load_monster(mid_) if mid_ else None

        if not m:
            st.info("Selecione um monstro à esquerda.")
        else:
            st.markdown(f"## 👹 {m.name}")
            st.caption(f"{m.size} {m.creature_type} • {m.alignment}")

            cols = st.columns(4)
            cols[0].metric("CA", m.ac)
            cols[1].metric("HP", f"{m.current_hp}/{m.max_hp}")
            cols[2].metric("Desloc.", m.speed)
            cols[3].metric("CR", m.cr)

            st.markdown("### Atributos")
            a = st.columns(6)
            a[0].write(f"**STR** {m.str_score}")
            a[1].write(f"**DEX** {m.dex_score}")
            a[2].write(f"**CON** {m.con_score}")
            a[3].write(f"**INT** {m.int_score}")
            a[4].write(f"**WIS** {m.wis_score}")
            a[5].write(f"**CHA** {m.cha_score}")

            with st.expander("📌 Detalhes", expanded=False):
                if m.skills:
                    st.write("**Skills:** " + ", ".join(m.skills))
                if m.saves:
                    st.write("**Saves:** " + ", ".join(m.saves))
                if m.senses:
                    st.write("**Senses:** " + m.senses)
                if m.languages:
                    st.write("**Languages:** " + m.languages)

            if m.traits_md.strip():
                with st.expander("✨ Traits", expanded=False):
                    st.markdown(m.traits_md)

            with st.expander("⚔️ Ações (roláveis)", expanded=True):
                if not m.actions:
                    st.info("Sem ações cadastradas.")
                else:
                    # pega controles
                    adv = st.session_state.get("m_adv", False)
                    dis = st.session_state.get("m_dis", False)
                    target_ac = st.session_state.get("m_ac", 0)
                    auto_damage = st.session_state.get("m_autodmg", True)

                    for i, act in enumerate(m.actions):
                        r = st.columns([0.55, 0.18, 0.27])
                        label = act.name
                        if act.damage:
                            label += f" — {act.damage} {act.damage_type}".strip()
                        r[0].write(f"**{label}**")
                        if act.description:
                            r[0].caption(act.description)

                        # botão de ataque (d20)
                        if r[1].button("🎯 Ataque", key=f"m_atk_{m.id}_{i}", use_container_width=True):
                            to_hit = int(act.to_hit or 0)
                            rr = roll_d20(bonus=to_hit, advantage=adv, disadvantage=dis)
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

                            mlog(f"👹 **{m.name}** — {act.name}: {fmt_d20(rr)} → {outcome}")

                            if hit and auto_damage and act.damage:
                                dmg_expr = critify(act.damage) if crit else act.damage
                                dr = roll_expr(dmg_expr)
                                tag = " (CRIT dmg)" if crit else ""
                                mlog(f"💥 **{m.name}** — Dano {act.name}{tag}: {fmt_expr(dr)}")

                            st.rerun()

                        # botão de dano
                        if r[2].button("💥 Dano", key=f"m_dmg_{m.id}_{i}", use_container_width=True):
                            if not act.damage:
                                mlog(f"ℹ️ **{m.name}** — {act.name}: sem fórmula de dano.")
                            else:
                                dr = roll_expr(act.damage)
                                mlog(f"💥 **{m.name}** — Dano {act.name}: {fmt_expr(dr)}")
                            st.rerun()

            if m.notes_md.strip():
                with st.expander("🗒️ Notas", expanded=False):
                    st.markdown(m.notes_md)

    # ===== RIGHT: log =====
    with right:
        st.markdown("### 📜 Log (Monstros)")
        if st.button("Limpar log", use_container_width=True, key="m_clear"):
            st.session_state["m_log"] = []
            st.rerun()

        for line in st.session_state["m_log"][:250]:
            st.markdown(line)
