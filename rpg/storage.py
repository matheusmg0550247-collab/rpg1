from __future__ import annotations
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CHAR_DIR = DATA_DIR / "characters"
ENC_DIR = DATA_DIR / "encounters"

def ensure_dirs() -> None:
    CHAR_DIR.mkdir(parents=True, exist_ok=True)
    ENC_DIR.mkdir(parents=True, exist_ok=True)
