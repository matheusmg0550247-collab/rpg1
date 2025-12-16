import streamlit as st
import uuid
from pathlib import Path

from rpg.storage import ensure_dirs, list_character_ids, load_character, save_character, PORTRAIT_DIR
from rpg.pdf_import import import_character_from_pdf
from rpg.utils import ability_mod, proficiency_bonus
from rpg.dice import roll_d20, roll_expr, critify, fmt_d20, fmt_expr

SKILLS = {
    "Athletics": "STR",
    "Acrobatics": "DEX",
    "Sleight of Hand": "DEX",
    "Stealth": "DEX",
    "Arcana": "INT",
    "History": "INT",
    "Investigation": "INT",
    "Nature": "INT",
    "Religion": "INT",
    "Animal Handling": "WIS",
    "Insight": "WIS",
    "Medicine": "Medicine",  # mantém label, mas atributo é WIS abaixo
    "Per
