from __future__ import annotations

def ability_mod(score: int) -> int:
    return (int(score) - 10) // 2

def proficiency_bonus(level: int) -> int:
    level = max(1, int(level))
    return 2 + (level - 1) // 4
