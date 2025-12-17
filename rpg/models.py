from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Weapon(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = "Longsword"
    attack_bonus: int = 0
    damage: str = "1d8+0"
    damage_type: str = "slashing"
    notes: str = ""


class Character(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    character_name: str
    player_name: str = ""
    species: str = ""
    class_and_level: str = ""
    background: str = ""
    level: int = 1

    # Ability scores
    str_score: int = Field(10, ge=1, le=30)
    dex_score: int = Field(10, ge=1, le=30)
    con_score: int = Field(10, ge=1, le=30)
    int_score: int = Field(10, ge=1, le=30)
    wis_score: int = Field(10, ge=1, le=30)
    cha_score: int = Field(10, ge=1, le=30)

    # Combat
    ac: int = 10
    speed: int = 30
    max_hp: int = 10
    current_hp: int = 10
    temp_hp: int = 0
    initiative_bonus: int = 0

    # Proficiencies
    save_proficiencies: List[str] = Field(default_factory=list)
    skill_proficiencies: List[str] = Field(default_factory=list)

    weapons: List[Weapon] = Field(default_factory=list)

    # Foto + equipamentos
    portrait_path: Optional[str] = None

    # ✅ NOVO: salva a imagem no JSON (resolve Streamlit Cloud “não persiste”)
    portrait_b64: Optional[str] = None

    equipment: List[str] = Field(default_factory=list)

    # Notas (Markdown) – raça/antecedente/classe
    race_notes_md: str = ""
    background_notes_md: str = ""
    class_notes_md: str = ""


class MonsterAction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = "Ataque"
    to_hit: Optional[int] = None          # bônus total no ataque
    damage: Optional[str] = None          # ex: "1d6+2"
    damage_type: str = ""                 # ex: "slashing"
