#!/usr/bin/env python3
"""Exact density obstruction for all possible LCMs up to a bound.

For fixed L, all usable moduli divide L.  Since each class has density 1/d,
coverage requires sum_{d|L, d+1 prime, d>=4} 1/d >= 1.  Multiplication by L
turns this into the exact integer test sum L/d >= L.
"""

from __future__ import annotations

import argparse
import math

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bound", type=int)
    parser.add_argument("--hits", type=int, default=30)
    args = parser.parse_args()
    bound = args.bound

    prime = np.ones(bound + 2, dtype=bool)
    prime[:2] = False
    for p in range(2, math.isqrt(bound + 1) + 1):
        if prime[p]:
            prime[p * p : bound + 2 : p] = False

    mass = np.zeros(bound + 1, dtype=np.int64)
    moduli = [d for d in range(4, bound + 1, 2) if prime[d + 1]]
    for d in moduli:
        quotients = np.arange(1, bound // d + 1, dtype=np.int64)
        mass[d : bound + 1 : d] += quotients

    periods = np.arange(bound + 1, dtype=np.int64)
    hits = np.flatnonzero((periods > 0) & (mass >= periods))
    print(f"bound={bound}")
    print(f"admissible_moduli_sieved={len(moduli)}")
    if len(hits):
        print(f"first_density_feasible_period={int(hits[0])}")
        for L in hits[: args.hits]:
            print(f"hit L={int(L)} mass={int(mass[L])} excess={int(mass[L]-L)}")
    else:
        print("first_density_feasible_period=NONE_IN_RANGE")

    below = np.arange(1, int(hits[0]) if len(hits) else bound + 1)
    best = int(below[np.argmax(mass[below] / below)])
    print(
        f"best_strictly_below_first L={best} mass={int(mass[best])} "
        f"deficit={int(best-mass[best])}"
    )

    # If 60 | L and epsilon := total_density - 1 < 1/30, the moduli
    # 4, 6, 10 are mandatory.  Any same-parity pair intersects with density
    # at least 1/30 > epsilon, yet three classes cannot have pairwise distinct
    # parities.  This gives an elementary obstruction.
    triangle_eliminated = [
        int(L)
        for L in hits
        if L % 60 == 0 and 30 * (int(mass[L]) - int(L)) < int(L)
    ]
    triangle_set = set(triangle_eliminated)
    survivors = [int(L) for L in hits if int(L) not in triangle_set]
    print(f"density_feasible_count={len(hits)}")
    print(f"parity_triangle_eliminated_count={len(triangle_eliminated)}")
    print("parity_triangle_eliminated=" + ",".join(map(str, triangle_eliminated)))
    print(f"unresolved_period_count={len(survivors)}")
    print("unresolved_periods=" + ",".join(map(str, survivors)))


if __name__ == "__main__":
    main()
