from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .models import Character, Monster

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CHAR_DIR = DATA_DIR / "characters"
PORTRAIT_DIR = DATA_DIR / "portraits"
MONSTER_DIR = DATA_DIR / "monsters"


def ensure_dirs() -> None:
    CHAR_DIR.mkdir(parents=True, exist_ok=True)
    PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)
    MONSTER_DIR.mkdir(parents=True, exist_ok=True)


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
    ensure_dirs()
    removed = False
    json_path = CHAR_DIR / f"{char_id}.json"
    if json_path.exists():
        json_path.unlink()
        removed = True

    for p in PORTRAIT_DIR.glob(f"{char_id}.*"):
        try:
            p.unlink()
            removed = True
        except Exception:
            pass
    return removed


def list_monster_ids() -> List[str]:
    ensure_dirs()
    return sorted([p.stem for p in MONSTER_DIR.glob("*.json")])


def load_monster(monster_id: str) -> Optional[Monster]:
    ensure_dirs()
    path = MONSTER_DIR / f"{monster_id}.json"
    if not path.exists():
        return None
    return Monster.model_validate_json(path.read_text(encoding="utf-8"))


def save_monster(m: Monster) -> None:
    ensure_dirs()
    path = MONSTER_DIR / f"{m.id}.json"
    path.write_text(m.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")


def delete_monster(monster_id: str) -> bool:
    ensure_dirs()
    path = MONSTER_DIR / f"{monster_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False
