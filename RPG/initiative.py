from __future__ import annotations
import random
from typing import List, Optional
from .models import Combatant

def roll_initiative(combatants: List[Combatant], *, rng: Optional[random.Random] = None) -> List[Combatant]:
    rng = rng or random.Random()
    for c in combatants:
        r = rng.randint(1, 20)
        c.initiative_roll = r
        c.initiative_total = r + int(c.initiative_bonus or 0)

    # Ordena por total desc; desempate por roll desc; depois nome
    combatants.sort(key=lambda x: (x.initiative_total or 0, x.initiative_roll or 0, x.name), reverse=True)
    return combatants

def next_turn(turn_index: int, n: int) -> int:
    if n <= 0:
        return 0
    return (turn_index + 1) % n

def prev_turn(turn_index: int, n: int) -> int:
    if n <= 0:
        return 0
    return (turn_index - 1) % n
