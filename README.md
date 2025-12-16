# RPG Streamlit Starter (D&D helper)

Este projeto é um **painel** para:
- 🎲 rolagens (com log e modo "3D visual" simples)
- 🧾 fichas (salvas em JSON)
- ⚔️ combate (iniciativa + turno + ações rápidas)
- 🎵 mídia (música/vídeo de fundo)

## Rodar localmente
### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### Linux/Mac
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Publicar no Streamlit Community Cloud
1. Suba este repositório no GitHub
2. Vá em share.streamlit.io e conecte o repo
3. Aponte para `app.py`

> Observação: GitHub Pages não roda Streamlit (Pages é estático). Use Streamlit Cloud.

## Onde ficam os dados
- Personagens: `data/characters/*.json`
- Encontros salvos: `data/encounters/*.json`
- Mídia: `data/media/audio` e `data/media/video`

Licenças: use apenas arquivos de áudio/vídeo com permissão (ex.: Creative Commons).
