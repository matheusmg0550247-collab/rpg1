from __future__ import annotations
import random
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

_TERM_RE = re.compile(r"^(\d*)d(\d+)$")


@dataclass
class ExprRoll:
    expression: str
    detail: List[Dict]
    total: int


def _split_terms(expr: str) -> List[Tuple[int, str]]:
    s = expr.replace(" ", "")
    if not s:
        raise ValueError("Expressão vazia.")
    if s[0] not in "+-":
        s = "+" + s
    parts = re.findall(r"[+-][^+-]+", s)
    out: List[Tuple[int, str]] = []
    for p in parts:
        sign = 1 if p[0] == "+" else -1
        term = p[1:]
        out.append((sign, term))
    return out


def roll_expr(expr: str, *, rng: Optional[random.Random] = None) -> ExprRoll:
    rng = rng or random.Random()
    terms = _split_terms(expr)
    detail: List[Dict] = []
    total = 0

    for sign, term in terms:
        m = _TERM_RE.match(term.lower())
        if m:
            n = int(m.group(1) or "1")
            sides = int(m.group(2))
            rolls = [rng.randint(1, sides) for _ in range(n)]
            subtotal = sign * sum(rolls)
            detail.append({"type": "dice", "term": f"{n}d{sides}", "sign": sign, "rolls": rolls, "subtotal": subtotal})
            total += subtotal
        else:
            if not re.fullmatch(r"\d+", term):
                raise ValueError(f"Termo inválido: {term} (use ex.: 2d6+3 ou 2d6+1d4+3)")
            val = sign * int(term)
            detail.append({"type": "mod", "term": term, "sign": sign, "value": val})
            total += val

    return ExprRoll(expression=expr, detail=detail, total=total)


def roll_d20(*, bonus: int = 0, advantage: bool = False, disadvantage: bool = False,
             rng: Optional[random.Random] = None) -> Dict:
    rng = rng or random.Random()
    if advantage and disadvantage:
        advantage = disadvantage = False

    if advantage or disadvantage:
        a = rng.randint(1, 20)
        b = rng.randint(1, 20)
        chosen = max(a, b) if advantage else min(a, b)
        return {"rolls": [a, b], "chosen": chosen, "bonus": bonus, "total": chosen + bonus,
                "advantage": advantage, "disadvantage": disadvantage}

    r = rng.randint(1, 20)
    return {"rolls": [r], "chosen": r, "bonus": bonus, "total": r + bonus,
            "advantage": False, "disadvantage": False}


def critify(expr: str) -> str:
    # dobra apenas os termos NdS (ex.: 1d8+3 => 2d8+3)
    terms = _split_terms(expr)
    rebuilt = []
    for sign, term in terms:
        m = _TERM_RE.match(term.lower())
        if m:
            n = int(m.group(1) or "1")
            sides = int(m.group(2))
            term2 = f"{n * 2}d{sides}"
        else:
            term2 = term
        rebuilt.append(("+" if sign == 1 else "-") + term2)
    s = "".join(rebuilt)
    return s[1:] if s.startswith("+") else s


def fmt_expr(rr: ExprRoll) -> str:
    chunks = []
    for d in rr.detail:
        if d["type"] == "dice":
            sig = "+" if d["sign"] == 1 else "-"
            chunks.append(f"{sig}{d['term']}[{','.join(map(str, d['rolls']))}]")
        else:
            sig = "+" if d["sign"] == 1 else "-"
            chunks.append(f"{sig}{abs(d['value'])}")
    pretty = " ".join(chunks).lstrip("+")
    return f"{rr.expression} → {pretty} = **{rr.total}**"


def fmt_d20(r: Dict) -> str:
    if len(r["rolls"]) == 2:
        tag = "ADV" if r["advantage"] else "DIS"
        return f"2d20({tag}) → [{r['rolls'][0]},{r['rolls'][1]}] escolhe {r['chosen']} {r['bonus']:+d} = **{r['total']}**"
    return f"d20 → [{r['rolls'][0]}] {r['bonus']:+d} = **{r['total']}**"
