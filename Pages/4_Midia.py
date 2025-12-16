import streamlit as st
from pathlib import Path

st.title("🎵 Mídia")

base = Path(__file__).resolve().parents[1] / "data" / "media"
audio_dir = base / "audio"
video_dir = base / "video"
audio_dir.mkdir(parents=True, exist_ok=True)
video_dir.mkdir(parents=True, exist_ok=True)

st.caption("Você pode usar arquivos locais no repo (data/media) ou colar um link do YouTube para vídeo.")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Áudio")
    audios = ["(nenhum)"] + sorted([p.name for p in audio_dir.glob("*") if p.is_file()])
    pick_audio = st.selectbox("Escolher áudio local", audios)
    audio_url = st.text_input("...ou URL de áudio (opcional)", value="")
    if st.button("Aplicar áudio", use_container_width=True):
        if audio_url.strip():
            st.session_state["media"]["audio"] = audio_url.strip()
        elif pick_audio != "(nenhum)":
            st.session_state["media"]["audio"] = str(audio_dir / pick_audio)
        else:
            st.session_state["media"]["audio"] = None
        st.success("Áudio aplicado.")

with col2:
    st.subheader("Vídeo")
    videos = ["(nenhum)"] + sorted([p.name for p in video_dir.glob("*") if p.is_file()])
    pick_video = st.selectbox("Escolher vídeo local", videos)
    video_url = st.text_input("...ou URL do YouTube (opcional)", value="")
    if st.button("Aplicar vídeo", use_container_width=True):
        if video_url.strip():
            st.session_state["media"]["video"] = video_url.strip()
        elif pick_video != "(nenhum)":
            st.session_state["media"]["video"] = str(video_dir / pick_video)
        else:
            st.session_state["media"]["video"] = None
        st.success("Vídeo aplicado.")

st.divider()
st.subheader("Preview")
media = st.session_state.get("media", {})
if media.get("video"):
    st.video(media["video"])
if media.get("audio"):
    st.audio(media["audio"])
