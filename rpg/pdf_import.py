from __future__ import annotations
import io, re
from typing import Dict, Tuple, List
from pypdf import PdfReader

from rpg.models import Character, Weapon

SKILL_PT_TO_EN = {
    "Atletismo": "Athletics",
    "Acrobacia": "Acrobatics",
    "Prestidigitação": "Sleight of Hand",
    "Furtividade": "Stealth",
    "Arcanismo": "Arcana",
    "História": "History",
    "Investigação": "Investigation",
    "Natureza": "Nature",
    "Religião": "Religion",
    "Adestrar Animais": "Animal Handling",
    "Intuição": "Insight",
    "Medicina": "Medicine",
    "Percepção": "Perception",
    "Sobrevivência": "Survival",
    "Enganação": "Deception",
    "Intimidação": "Intimidation",
    "Atuação": "Performance",
    "Persuasão": "Persuasion",
}

SAVE_PT_TO_AB = {
    "Força": "STR",
    "Destreza": "DEX",
    "Constituição": "CON",
    "Inteligência": "INT",
    "Sabedoria": "WIS",
    "Carisma": "CHA",
}

def _to_int(s: str | None, default: int = 0) -> int:
    if not s:
        return default
    s = str(s).strip().replace(" ", "")
    s = s.replace(".", "").replace(",", ".")
    m = re.search(r"[+-]?\d+", s)
    return int(m.group(0)) if m else default

def _parse_level(class_level: str) -> int:
    # pega o último número (ex.: "Bárbaro NVL 7" -> 7)
    nums = re.findall(r"\d+", class_level or "")
    return int(nums[-1]) if nums else 1

def _parse_speed(speed_raw: str) -> int:
    if not speed_raw:
        return 30
    s = speed_raw.strip().lower().replace(" ", "").replace(",", ".")
    # se vier em metros (ex.: 13.5m), converte aprox para pés arredondado pra múltiplos de 5
    if "m" in s:
        m = re.search(r"(\d+(\.\d+)?)", s)
        if m:
            meters = float(m.group(1))
            feet = meters * 3.28084
            return int(round(feet / 5) * 5)
    # se já vier em número, assume pés
    return _to_int(s, 30)

def extract_pdf_fields(pdf_bytes: bytes) -> Tuple[Dict[str, str], List[str], List[str]]:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields() or {}
    values: Dict[str, str] = {}

    checked_skills: List[str] = []
    checked_saves: List[str] = []

    for name, f in fields.items():
        v = f.get("/V")
        if name.startswith("Check Box"):
            if v not in (None, "/Off"):
                # skills
                m = re.search(r"Perícia\s*-\s*(.+)$", name)
                if m:
                    pt = m.group(1).strip()
                    en = SKILL_PT_TO_EN.get(pt)
                    if en:
                        checked_skills.append(en)

                # saves
                m2 = re.search(r"Teste de Resistência\s*-\s*(.+)$", name)
                if m2:
                    pt = m2.group(1).strip()
                    ab = SAVE_PT_TO_AB.get(pt)
                    if ab:
                        checked_saves.append(ab)
            continue

        if v is not None:
            values[name] = str(v).strip()

    return values, checked_skills, checked_saves

def import_character_from_pdf(pdf_bytes: bytes, *, char_id: str) -> Character:
    values, skills, saves = extract_pdf_fields(pdf_bytes)

    name = values.get("Nome do Personagem", "").strip() or "Sem Nome"
    class_level = values.get("Classe & Nível", "")
    level = _parse_level(class_level)

    weapons: List[Weapon] = []
    for i in (1, 2, 3):
        wname = values.get(f"Arma {i}", "").strip()
        if not wname:
            continue
        atk = _to_int(values.get(f"Bônus de Ataque {i}", "0"), 0)
        dmg = (values.get(f"Dano / Tipo {i}", "") or "").strip()

        # tentativa simples de extrair tipo (se vier "1d8+3 cortante")
        dmg_expr = dmg
        dmg_type = ""
        m = re.match(r"^([0-9dD+\-\s]+)\s*(.*)$", dmg)
        if m:
            dmg_expr = m.group(1).replace(" ", "")
            dmg_type = m.group(2).strip()

        weapons.append(Weapon(
            name=wname,
            attack_bonus=atk,
            damage=dmg_expr or "1d6+0",
            damage_type=dmg_type or "—",
        ))

    equip_raw = values.get("Equipamento", "") or ""
    equipment = [x.strip() for x in re.split(r"[\n,;]+", equip_raw) if x.strip()]

    max_hp = _to_int(values.get("Pontos de Vida Máximo"), 10)
    cur_hp = _to_int(values.get("Pontos de Vida Atual"), max_hp) or max_hp

    ch = Character(
        id=char_id,
        character_name=name,
        player_name=values.get("Nome do Jogador", ""),
        species=values.get("Raça", ""),
        class_and_level=class_level,
        background=values.get("Antecedentes", ""),
        level=level,

        str_score=_to_int(values.get("Força"), 10),
        dex_score=_to_int(values.get("Destreza"), 10),
        con_score=_to_int(values.get("Constituição"), 10),
        int_score=_to_int(values.get("Inteligência"), 10),
        wis_score=_to_int(values.get("Sabedoria"), 10),
        cha_score=_to_int(values.get("Carisma"), 10),

        ac=_to_int(values.get("Classe de Armadura"), 10),
        speed=_parse_speed(values.get("Deslocamento", "")),
        max_hp=max_hp,
        current_hp=cur_hp,
        temp_hp=_to_int(values.get("Pontos de Vida Temporário"), 0),
        initiative_bonus=_to_int(values.get("Iniciativa"), 0),

        skill_proficiencies=sorted(set(skills)),
        save_proficiencies=sorted(set(saves)),
        weapons=weapons,
        equipment=equipment,
    )
    return ch
