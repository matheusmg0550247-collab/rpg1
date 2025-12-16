from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional
from .models import Character, Encounter

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CHAR_DIR = DATA_DIR / "characters"
ENC_DIR = DATA_DIR / "encounters"

def ensure_dirs() -> None:
    CHAR_DIR.mkdir(parents=True, exist_ok=True)
    ENC_DIR.mkdir(parents=True, exist_ok=True)

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

def delete_character(char_id: str) -> None:
    ensure_dirs()
    path = CHAR_DIR / f"{char_id}.json"
    if path.exists():
        path.unlink()

def list_encounter_ids() -> List[str]:
    ensure_dirs()
    return sorted([p.stem for p in ENC_DIR.glob("*.json")])

def load_encounter(enc_id: str) -> Optional[Encounter]:
    ensure_dirs()
    path = ENC_DIR / f"{enc_id}.json"
    if not path.exists():
        return None
    return Encounter.model_validate_json(path.read_text(encoding="utf-8"))

def save_encounter(enc: Encounter) -> None:
    ensure_dirs()
    path = ENC_DIR / f"{enc.id}.json"
    path.write_text(enc.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")

def delete_encounter(enc_id: str) -> None:
    ensure_dirs()
    path = ENC_DIR / f"{enc_id}.json"
    if path.exists():
        path.unlink()
