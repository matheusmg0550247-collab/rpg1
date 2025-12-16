from __future__ import annotations
import math

def ability_mod(score: int) -> int:
    """Modificador padrão: (score - 10) // 2"""
    return (int(score) - 10) // 2

def proficiency_bonus(level: int) -> int:
    """PB padrão 5e: 2 + floor((level-1)/4)."""
    level = max(1, int(level))
    return 2 + (level - 1) // 4
