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

    json_path = CHAR_DIR / f"{char_id}.json"

    # tenta descobrir retrato salvo no JSON (para apagar também)
    portrait_to_remove: Optional[Path] = None
    if json_path.exists():
        try:
            ch = Character.model_validate_json(json_path.read_text(encoding="utf-8"))
            portrait_str = getattr(ch, "portrait_path", None)
            if portrait_str:
                p = Path(portrait_str)
                # só permite remover arquivos dentro de data/ por segurança
                try:
                    rp = p.resolve()
                    rd = DATA_DIR.resolve()
                    if rd in rp.parents and rp.exists():
                        portrait_to_remove = rp
                except Exception:
                    portrait_to_remove = None
        except Exception:
            portrait_to_remove = None

        json_path.unlink()
        removed = True

    # remove retrato referenciado no JSON (se aplicável)
    if portrait_to_remove and portrait_to_remove.exists():
        try:
            portrait_to_remove.unlink()
            removed = True
        except Exception:
            pass

    # remove retrato padrão data/portraits/<id>.png (fallback)
    portrait_default = PORTRAIT_DIR / f"{char_id}.png"
    if portrait_default.exists():
        try:
            portrait_default.unlink()
            removed = True
        except Exception:
            pass

    return removed
