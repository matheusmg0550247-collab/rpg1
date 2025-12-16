from __future__ import annotations
import random
import re
from dataclasses import dataclass
from typing import List, Optional, Dict

_DICE_RE = re.compile(r"^\s*(?P<n>\d*)\s*[dD]\s*(?P<sides>\d+)\s*(?P<mod>[+-]\s*\d+)?\s*$")

@dataclass
class RollResult:
    expression: str
    rolls: List[int]
    modifier: int
    total: int

def roll_dice(expr: str, *, rng: Optional[random.Random] = None) -> RollResult:
    """Rola expressão simples: XdY(+/-Z). Ex.: d20+5, 2d6-1"""
    rng = rng or random.Random()
    m = _DICE_RE.match(expr)
    if not m:
        raise ValueError(f"Expressão inválida: {expr}. Use formato tipo '2d6+3' ou 'd20'.")
    n = int(m.group("n") or "1")
    sides = int(m.group("sides"))
    mod_raw = m.group("mod") or "+0"
    mod = int(mod_raw.replace(" ", ""))
    rolls = [rng.randint(1, sides) for _ in range(n)]
    total = sum(rolls) + mod
    return RollResult(expression=f"{n}d{sides}{mod_raw.replace(' ','') if mod_raw else ''}", rolls=rolls, modifier=mod, total=total)

def roll_d20(*, bonus: int = 0, advantage: bool = False, disadvantage: bool = False, rng: Optional[random.Random] = None) -> Dict:
    """Rola d20 com bônus e (des)vantagem. Retorna detalhes."""
    rng = rng or random.Random()
    if advantage and disadvantage:
        advantage = disadvantage = False

    if advantage or disadvantage:
        a = rng.randint(1, 20)
        b = rng.randint(1, 20)
        chosen = max(a, b) if advantage else min(a, b)
        return {
            "type": "d20",
            "rolls": [a, b],
            "chosen": chosen,
            "bonus": bonus,
            "total": chosen + bonus,
            "advantage": advantage,
            "disadvantage": disadvantage,
        }
    r = rng.randint(1, 20)
    return {"type": "d20", "rolls": [r], "chosen": r, "bonus": bonus, "total": r + bonus, "advantage": False, "disadvantage": False}

def format_roll(result) -> str:
    """Formata resultados para log."""
    if isinstance(result, RollResult):
        rolls = ", ".join(map(str, result.rolls))
        mod = f"{result.modifier:+d}"
        return f"{result.expression} → [{rolls}] {mod} = **{result.total}**"
    # d20 dict
    rolls = ", ".join(map(str, result["rolls"]))
    if len(result["rolls"]) == 2:
        tag = "ADV" if result["advantage"] else "DIS"
        return f"2d20({tag}) → [{rolls}] escolhe {result['chosen']} {result['bonus']:+d} = **{result['total']}**"
    return f"d20 → [{rolls}] {result['bonus']:+d} = **{result['total']}**"
