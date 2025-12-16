from __future__ import annotations
from pathlib import Path
from typing import List, Optional
from .models import Character

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CHAR_DIR = DATA_DIR / "characters"
PORTRAIT_DIR = DATA_DIR / "portraits"


def ensure_dirs() -> None:
    CHAR_DIR.mkdir(parents=True, exist_ok=True)
    PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)


def list_character_ids() -> List[str]:
    ensure_dirs()
    return sorted([p.stem for p in CHAR_DIR.glob("*.json")])


def load_character(char_id: str) -> Optional[Character]:
    ensure_dirs()
    path = CHAR_DIR / f"{char_id}.json"
    if not path.exists():
        return None
    return Character.model_validate_json(path.read_text(encoding="utf-8"))


def save_character(ch: Character) -> None:
    ensure_dirs()
    path = CHAR_DIR / f"{ch.id}.json"
    path.write_text(ch.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")

def delete_character(char_id: str) -> bool:
    """
    Apaga a ficha (JSON) e a foto associada (se existir).
    Retorna True se removeu algo.
    """
    ensure_dirs()
    removed = False

    # remove JSON
    json_path = CHAR_DIR / f"{char_id}.json"
    if json_path.exists():
        json_path.unlink()
        removed = True

    # remove foto padrão (salva como data/portraits/<id>.png)
    portrait_path = PORTRAIT_DIR / f"{char_id}.png"
    if portrait_path.exists():
        portrait_path.unlink()
        removed = True

    return removed
