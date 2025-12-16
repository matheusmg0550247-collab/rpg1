# -*- coding: utf-8 -*-
from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"

PHOTO_CANDIDATES = [
    ASSETS_DIR / "foto1.jpg",
    ASSETS_DIR / "foto1.jpeg",
    ASSETS_DIR / "foto1.png",
]

VIDEO_PATH = ASSETS_DIR / "video1.mp4"
MUSIC_PATH = ASSETS_DIR / "musica1.mp4"

INTRO_TEXT = """# 📜 Prólogo: A Sombra da Vitória

**Região:** A Fronteira Norte do Mar da Lua (The Moonsea)  
**Ano:** 1496 CV, O Ano do Guerreiro Desatento

O céu sobre o Mar da Lua está cinza há semanas, manchado pela fumaça das fogueiras de guerra. As notícias viajaram rápido: a Legião da Mão de Ferro, uma armada massiva de Hobgoblins vinda de além-mar, rompeu as defesas costeiras. Onde seus navios negros atracam, a terra morre.

O Reino convocou todos os estandartes. Mercenários, milícias e heróis estão marchando para a Praia da Desolação para formar a última linha de defesa contra a invasão. O barulho de aço e a lama das estradas são a única realidade conhecida por vocês nos últimos dias.

Vocês servem — ou são aliados — da Casa Aldric. O Lorde Aldric, conhecido como **"O Leão do Norte"**, é o comandante supremo dessas forças. Um herói vivo, famoso por expulsar os clãs goblins de Thar há trinta anos e tomar a impenetrável Cidadela de Ferro (Ironfang Keep), transformando um bastião de monstros em um símbolo de segurança humana.

Mas, enquanto todo o continente olha para a fumaça no leste, algo estranho acontece no oeste.

Ontem à noite, em vez de ordens de marcha para a frente de batalha, vocês receberam uma convocação urgente. Não veio pelos canais militares oficiais. Veio por um mensageiro encapuzado, trazendo um pergaminho selado não com o brasão de guerra do Leão, mas com o selo de cera pessoal de sua esposa, Lady Catelyn.

A mensagem era curta e perturbadora:

> "O Leão não ruge mais. O passado cobrou sua dívida.  
> A Cidadela de Ferro, nossa fortaleza mais segura na retaguarda, parou de responder.  
> Não marchem para a praia. Venham à minha tenda antes do amanhecer.  
> O verdadeiro inimigo não está vindo do mar. Ele já está entre nós."

Vocês estão a poucos metros da Tenda de Comando. O acampamento ao redor é barulhento e caótico, mas a tenda do Lorde está envolta em um silêncio sepulcral. Vocês sabem que, ao cruzarem aquela lona, a guerra lá fora deixará de ser o seu maior problema.

**Preparem seus espíritos.** O que quer que tenha silenciado a Cidadela de Ferro está esperando por vocês.
"""


def _find_photo() -> Path | None:
    for p in PHOTO_CANDIDATES:
        if p.exists():
            return p
    return None


def _audio_player_mp4_autoplay(file_path: Path) -> None:
    # Player sem título, só o controle
    data = file_path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    html = f"""
    <div style="border:1px solid #ff2b2b; border-radius:12px; padding:10px; background:#0f0f0f;">
      <audio controls autoplay style="width: 100%;">
        <source src="data:audio/mp4;base64,{b64}" type="audio/mp4">
      </audio>
    </div>
    """
    components.html(html, height=90)


def render() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    st.markdown(INTRO_TEXT)
    st.divider()

    col1, col2 = st.columns([0.62, 0.38], gap="large")

    with col1:
        photo = _find_photo()
        if photo:
            st.image(photo, use_container_width=True)

        if VIDEO_PATH.exists():
            st.video(VIDEO_PATH.read_bytes())

    with col2:
        if MUSIC_PATH.exists():
            _audio_player_mp4_autoplay(MUSIC_PATH)
