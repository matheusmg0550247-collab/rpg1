from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Weapon(BaseModel):
    name: str = "Longsword"
    attack_bonus: int = 0
    damage: str = "1d8+0"
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

    # Combat basics
    ac: int = 10
    speed: int = 30
    max_hp: int = 10
    current_hp: int = 10
    temp_hp: int = 0
    initiative_bonus: int = 0

    # Saves/skills (simples: marca se proficiente)
    save_proficiencies: List[str] = Field(default_factory=list)
    skill_proficiencies: List[str] = Field(default_factory=list)

    weapons: List[Weapon] = Field(default_factory=list)

class Combatant(BaseModel):
    name: str
    kind: str = "PC"   # PC / Monster / NPC
    initiative_bonus: int = 0
    ac: Optional[int] = None
    max_hp: Optional[int] = None
    hp: Optional[int] = None
    conditions: List[str] = Field(default_factory=list)

    initiative_roll: Optional[int] = None
    initiative_total: Optional[int] = None

class Encounter(BaseModel):
    id: str
    title: str = "Encontro"
    combatants: List[Combatant] = Field(default_factory=list)
    round: int = 1
    turn_index: int = 0
