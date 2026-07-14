"""Mines multiplier math.

Payout multiplier after revealing `k` safe tiles on a `size`-tile grid with
`mines` bombs, with a house edge baked in. Equivalent to the inverse of the
probability of surviving k picks.
"""
from math import comb

HOUSE_EDGE = 0.03


def multiplier(size: int, mines: int, revealed: int) -> float:
    if revealed <= 0:
        return 1.0
    safe = size - mines
    if revealed > safe:
        revealed = safe
    # Probability of picking `revealed` safe tiles in a row.
    prob = comb(safe, revealed) / comb(size, revealed)
    fair = 1.0 / prob
    return round(fair * (1 - HOUSE_EDGE), 4)
