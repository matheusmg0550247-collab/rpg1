from __future__ import annotations

import random
import re
from typing import Dict, List


def roll_d20(bonus: int = 0, advantage: bool = False, disadvantage: bool = False) -> Dict:
    rolls = [random.randint(1, 20)]
    if advantage or disadvantage:
        rolls.append(random.randint(1, 20))
        chosen = max(rolls) if advantage and not disadvantage else min(rolls)
    else:
        chosen = rolls[0]
    total = chosen + int(bonus)
    return {"type": "d20", "rolls": rolls, "chosen": chosen, "bonus": int(bonus), "total": total}


def _roll_term(n: int, sides: int) -> List[int]:
    return [random.randint(1, sides) for _ in range(n)]


def roll_expr(expr: str) -> Dict:
    expr = (expr or "").strip().lower().replace(" ", "")
    if not expr:
        return {"type": "expr", "expr": "", "terms": [], "total": 0}

    tokens = re.findall(r"[+\-]?\d*d?\d+|[+\-]?\d+", expr)
    terms = []
    total = 0

    for tok in tokens:
        sign = 1
        t = tok
        if t.startswith("+"):
            t = t[1:]
        elif t.startswith("-"):
            sign = -1
            t = t[1:]

        if "d" in t:
            n_s, s_s = t.split("d", 1)
            n = int(n_s) if n_s else 1
            sides = int(s_s)
            rolls = _roll_term(n, sides)
            subtotal = sum(rolls) * sign
            total += subtotal
            terms.append({"kind": "dice", "n": n, "sides": sides, "rolls": rolls, "sign": sign, "subtotal": subtotal})
        else:
            val = int(t) * sign
            total += val
            terms.append({"kind": "flat", "value": val})

    return {"type": "expr", "expr": expr, "terms": terms, "total": total}


def roll_dice(expr: str) -> Dict:
    return roll_expr(expr)


def critify(expr: str) -> str:
    # dobra apenas os dados: 2d6+3 -> 4d6+3
    expr = (expr or "").strip().lower().replace(" ", "")
    if not expr:
        return expr
    parts = re.split(r"(?=[+\-])", expr)
    out = []
    for p in parts:
        if not p:
            continue
        sign = ""
        t = p
        if t[0] in "+-":
            sign = t[0]
            t = t[1:]
        if "d" in t:
            n_s, s_s = t.split("d", 1)
            n = int(n_s) if n_s else 1
            out.append(f"{sign}{2*n}d{s_s}")
        else:
            out.append(f"{sign}{t}")
    return "".join(out)


def fmt_d20(rr: Dict) -> str:
    rolls = rr.get("rolls", [])
    chosen = rr.get("chosen", 0)
    bonus = rr.get("bonus", 0)
    total = rr.get("total", 0)
    if len(rolls) == 2:
        return f"[{rolls[0]}, {rolls[1]}] → {chosen} {bonus:+d} = **{total}**"
    return f"{chosen} {bonus:+d} = **{total}**"


def fmt_expr(dr: Dict) -> str:
    expr = dr.get("expr", "")
    total = dr.get("total", 0)
    return f"`{expr}` = **{total}**"


def format_roll(x: Dict) -> str:
    if x.get("type") == "d20":
        return fmt_d20(x)
    return fmt_expr(x)
