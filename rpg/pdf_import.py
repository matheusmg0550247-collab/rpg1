from __future__ import annotations

import re
import uuid
from io import BytesIO
from typing import Any, Dict, Optional

# tenta pypdf primeiro; se não tiver, tenta PyPDF2
try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    from PyPDF2 import PdfReader  # type: ignore

from .models import Character, Weapon


def _to_str(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    try:
        return str(v)
    except Exception:
        return ""


def _parse_int(s: str, default: int = 0) -> int:
    s = _to_str(s).strip()
    if not s:
        return default
    s = s.replace(".", "").replace(",", ".")  # "23.000" -> "23000", "10,5" -> "10.5"
    m = re.search(r"-?\d+", s)
    if not m:
        return default
    try:
        return int(m.group(0))
    except Exception:
        return default


def _parse_bonus(s: str, default: int = 0) -> int:
    s = _to_str(s).strip()
    if not s:
        return default
    m = re.search(r"[-+]\s*\d+", s)
    if not m:
        # às vezes vem "5" sem sinal
        m2 = re.search(r"-?\d+", s)
        return int(m2.group(0)) if m2 else default
    return int(m.group(0).replace(" ", ""))


def _normalize_damage(expr: str) -> str:
    """
    Converte coisas tipo:
      "1d8(V10)" -> "1d8"
      "2d6 + 3"  -> "2d6+3"
    Mantém apenas 0-9 d + -
    """
    s = _to_str(expr).strip()
    if not s:
        return ""
    s = re.sub(r"\(.*?\)", "", s)  # remove "(V10)" etc
    s = s.replace(" ", "")
    s = re.sub(r"[^0-9dD+\-]", "", s)
    s = s.lower()
    # precisa ter pelo menos um "d"
    return s if "d" in s else ""


def _extract_form_fields(pdf_bytes: bytes) -> Dict[str, str]:
    reader = PdfReader(BytesIO(pdf_bytes))
    raw = reader.get_fields() or {}

    out: Dict[str, str] = {}
    for k, f in raw.items():
        key = _to_str(k).strip()
        if not key:
            continue

        # valor geralmente em /V
        v = ""
        if isinstance(f, dict):
            v = _to_str(f.get("/V"))
        else:
            try:
                v = _to_str(getattr(f, "value", ""))
            except Exception:
                v = ""

        out[key] = v.strip()
    return out


def _pick(fields: Dict[str, str], *names: str) -> str:
    """
    Busca por chaves exatas e também tentando variantes com/sem espaços.
    """
    for name in names:
        n = name.strip()
        if n in fields and fields[n]:
            return fields[n]
        # tenta achar por case-insensitive
        for k, v in fields.items():
            if k.strip().lower() == n.lower() and v:
                return v
    return ""


def import_character_from_pdf(pdf_bytes: bytes, char_id: Optional[str] = None) -> Character:
    """
    Importa ficha a partir de PDF FORM (AcroForm).
    Se o PDF não tiver campos, retorna ficha básica.
    """
    if not char_id:
        char_id = uuid.uuid4().hex[:10]

    fields = _extract_form_fields(pdf_bytes)

    # Se não vier nada útil (PDF só com labels), cai num personagem mínimo
    if not fields or all((not _to_str(v).strip()) for v in fields.values()):
        return Character(
            id=char_id,
            character_name="Novo Personagem",
            player_name="",
            species="",
            class_and_level="",
            background="",
            level=1,
        )

    character_name = _pick(fields, "CharacterName", "NOME DO PERSONAGEM")
    player_name = _pick(fields, "PlayerName", "NOME DO JOGADOR")
    species = _pick(fields, "Race", "Race ", "RAÇA")
    class_and_level = _pick(fields, "ClassLevel", "CLASSE E NÍVEL")
    background = _pick(fields, "Background", "ANTECEDENTE")

    # tenta extrair nível do texto (último número)
    lvl = 1
    m = re.search(r"(\d+)\s*$", class_and_level.strip())
    if m:
        lvl = int(m.group(1))

    # Atenção: em MUITAS fichas PDF, o campo "STRmod" guarda o SCORE (14),
    # e o campo "STR" guarda o MOD (+2). Então pegamos o SCORE pelos "*mod".
    str_score = _parse_int(_pick(fields, "STRmod", "StrengthScore", "STR SCORE"), 10)
    dex_score = _parse_int(_pick(fields, "DEXmod", "DEXmod ", "DexterityScore", "DEX SCORE"), 10)
    con_score = _parse_int(_pick(fields, "CONmod", "ConstitutionScore", "CON SCORE"), 10)
    int_score = _parse_int(_pick(fields, "INTmod", "IntelligenceScore", "INT SCORE"), 10)
    wis_score = _parse_int(_pick(fields, "WISmod", "WisdomScore", "WIS SCORE"), 10)
    cha_score = _parse_int(_pick(fields, "CHamod", "CHAmod", "CharismaScore", "CHA SCORE"), 10)

    ac = _parse_int(_pick(fields, "AC", "ARMD"), 10)
    initiative_bonus = _parse_int(_pick(fields, "Initiative", "INICIATIVA"), 0)
    speed = _parse_int(_pick(fields, "Speed", "DESLOC."), 30)

    max_hp = _parse_int(_pick(fields, "HPMax", "PV Totais"), 10)
    current_hp = _parse_int(_pick(fields, "HPCurrent", "PONTOS DE VIDA ATUAIS"), max_hp)
    temp_hp = _parse_int(_pick(fields, "HPTemp", "PONTOS DE VIDA TEMPORÁRIOS"), 0)

    # Equipamentos (campo multiline)
    equipment_raw = _pick(fields, "Equipment", "EQUIPAMENTO")
    equipment = [ln.strip() for ln in equipment_raw.splitlines() if ln.strip()]

    # Traits / Features (viram Markdown)
    race_traits = _pick(fields, "Feat+Traits", "Racial Traits")
    class_features = _pick(fields, "Features and Traits", "Class Features")
    prof_lang = _pick(fields, "ProficienciesLang", "IDIOMAS E OUTRAS PROFICIÊNCIAS")

    # Armas (3 slots comuns)
    weapons: list[Weapon] = []
    slots = [
        ("Wpn Name", "Wpn1 AtkBonus", "Wpn1 Damage"),
        ("Wpn Name 2", "Wpn2 AtkBonus", "Wpn2 Damage"),
        ("Wpn Name 3", "Wpn3 AtkBonus", "Wpn3 Damage"),
    ]
    for name_k, atk_k, dmg_k in slots:
        wname = _pick(fields, name_k)
        if not wname:
            continue
        atk = _parse_bonus(_pick(fields, atk_k), 0)
        dmg = _normalize_damage(_pick(fields, dmg_k))
        if not dmg:
            dmg = "1d4+0"
        weapons.append(
            Weapon(
                name=wname.strip(),
                attack_bonus=atk,
                damage=dmg,
                damage_type="",
                notes="",
            )
        )

    # evita campos vazios demais
    if not character_name:
        character_name = "Personagem Importado"

    ch = Character(
        id=char_id,
        character_name=character_name.strip(),
        player_name=player_name.strip(),
        species=species.strip(),
        class_and_level=class_and_level.strip(),
        background=background.strip(),
        level=int(lvl),

        str_score=str_score,
        dex_score=dex_score,
        con_score=con_score,
        int_score=int_score,
        wis_score=wis_score,
        cha_score=cha_score,

        ac=ac,
        speed=speed,
        max_hp=max_hp,
        current_hp=current_hp,
        temp_hp=temp_hp,
        initiative_bonus=initiative_bonus,

        weapons=weapons,
        equipment=equipment,

        race_notes_md=race_traits.strip(),
        background_notes_md=prof_lang.strip() if prof_lang else "",
        class_notes_md=class_features.strip(),
    )
    return ch
