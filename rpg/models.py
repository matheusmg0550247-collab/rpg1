from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class Weapon(BaseModel):
    name: str = "Longsword"
    attack_bonus: int = 0              # bônus TOTAL do ataque (já pronto)
    damage: str = "1d8+0"              # suporta "2d6+1d4+3"
    damage_type: str = "slashing"
    notes: str = ""


class Character(BaseModel):
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

    # Proficiencies (strings padrão)
    # saves: ["STR","DEX","CON","INT","WIS","CHA"]
    save_proficiencies: List[str] = Field(default_factory=list)

    # skills: ["Athletics","Stealth",...]
    skill_proficiencies: List[str] = Field(default_factory=list)

    weapons: List[Weapon] = Field(default_factory=list)

    # NOVO: foto + equipamentos
    portrait_path: Optional[str] = None
    equipment: List[str] = Field(default_factory=list)
    
