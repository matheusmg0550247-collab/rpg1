from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class Weapon(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = "Longsword"
    attack_bonus: int = 0              # bônus TOTAL do ataque (já pronto)
    damage: str = "1d8+0"              # suporta "2d6+1d4+3"
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

    alignment: str = ""
    xp: str = ""
    inspiration: str = ""

    personality_traits: str = ""
    ideals: str = ""
    bonds: str = ""
    flaws: str = ""

    prof_bonus: int = 0

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

    # Proficiencies (strings)
    save_proficiencies: List[str] = Field(default_factory=list)
    skill_proficiencies: List[str] = Field(default_factory=list)

    # Import “completo” do PDF: bônus prontos (como está na ficha)
    skill_mods: Dict[str, int] = Field(default_factory=dict)   # ex: {"Perception": 6}
    save_mods: Dict[str, int] = Field(default_factory=dict)    # ex: {"WIS": 6}

    weapons: List[Weapon] = Field(default_factory=list)

    # Foto + equipamentos
    portrait_path: Optional[str] = None
    portrait_b64: Optional[str] = None
    equipment: List[str] = Field(default_factory=list)

    # Markdown (raça/antecedente/classe)
    race_notes_md: str = ""
    background_notes_md: str = ""
    class_notes_md: str = ""

    # Magias
    spells: List[str] = Field(default_factory=list)  # lista completa dos campos Spells...
    spell_slots_total: Dict[str, int] = Field(default_factory=dict)       # {"1": 4, "2": 3, ...}
    spell_slots_remaining: Dict[str, int] = Field(default_factory=dict)   # {"1": 4, ...}
    spellcasting_meta: Dict[str, str] = Field(default_factory=dict)       # DC, atk bonus, ability, class...

    # ✅ Dump 100% dos campos do PDF (pra nada se perder)
    raw_pdf_fields: Dict[str, str] = Field(default_factory=dict)


class MonsterAction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = "Ataque"
    to_hit: Optional[int] = None
    damage: Optional[str] = None
    damage_type: str = ""
    description: str = ""


class Monster(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str

    size: str = "Medium"
    creature_type: str = "humanoid"
    alignment: str = "unaligned"

    ac: int = 12
    max_hp: int = 7
    current_hp: int = 7
    speed: str = "30 ft."

    str_score: int = Field(10, ge=1, le=30)
    dex_score: int = Field(10, ge=1, le=30)
    con_score: int = Field(10, ge=1, le=30)
    int_score: int = Field(10, ge=1, le=30)
    wis_score: int = Field(10, ge=1, le=30)
    cha_score: int = Field(10, ge=1, le=30)

    skills: List[str] = Field(default_factory=list)
    saves: List[str] = Field(default_factory=list)
    senses: str = ""
    languages: str = ""
    cr: str = "1/4"

    traits_md: str = ""
    actions: List[MonsterAction] = Field(default_factory=list)
    notes_md: str = ""
