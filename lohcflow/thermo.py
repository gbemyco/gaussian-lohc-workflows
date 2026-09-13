from __future__ import annotations

import re

HARTREE_TO_KJ_MOL = 2625.499639
ATOMIC_MASS = {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "S": 32.06}


def dehydrogenation_energy(initial: float, final: float, h2: float, released_h2: int) -> tuple[float, float]:
    if released_h2 <= 0:
        raise ValueError("released_h2 must be positive")
    total = (final + released_h2 * h2 - initial) * HARTREE_TO_KJ_MOL
    return total, total / released_h2


def molecular_mass(formula: str) -> float:
    tokens = re.findall(r"([A-Z][a-z]?)(\d*)", formula)
    if not tokens or "".join(element + count for element, count in tokens) != formula:
        raise ValueError(f"unsupported molecular formula: {formula}")
    return sum(ATOMIC_MASS[element] * (int(count) if count else 1) for element, count in tokens)


def hydrogen_capacity(hydrogenated_formula: str, stored_h_atoms: int) -> float:
    return 100.0 * stored_h_atoms * ATOMIC_MASS["H"] / molecular_mass(hydrogenated_formula)
