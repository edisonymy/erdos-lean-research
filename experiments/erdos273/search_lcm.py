#!/usr/bin/env python3
"""Rank smooth candidate periods for Erdos problem 273.

For a proposed period L, every usable modulus d must divide L and d + 1 must
be prime.  A covering system needs sum(1/d) >= 1, so this script first ranks
periods by that necessary density before any SAT search is attempted.
"""

from __future__ import annotations

import argparse
import itertools
import math
from fractions import Fraction


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def divisors_from_factorization(factors: list[tuple[int, int]]) -> list[int]:
    result = [1]
    for p, exponent in factors:
        powers = [p**e for e in range(exponent + 1)]
        result = [d * q for d in result for q in powers]
    return sorted(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=10**9)
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument(
        "--sort", choices=("density", "period"), default="density"
    )
    args = parser.parse_args()

    # Broad enough for smooth periods below the default bound.  Exponent zero
    # is permitted except for 2, since every p-1 here is even.
    prime_caps = [(2, 12), (3, 8), (5, 5), (7, 4), (11, 3), (13, 3)]
    ranked: list[tuple[Fraction, int, list[int], list[tuple[int, int]]]] = []
    exponent_ranges = [range(1, prime_caps[0][1] + 1)] + [
        range(cap + 1) for _, cap in prime_caps[1:]
    ]
    for exponents in itertools.product(*exponent_ranges):
        L = math.prod(p**e for (p, _), e in zip(prime_caps, exponents))
        if L > args.bound:
            continue
        factors = [(p, e) for (p, _), e in zip(prime_caps, exponents) if e]
        moduli = [
            d
            for d in divisors_from_factorization(factors)
            if d >= 4 and is_prime(d + 1)
        ]
        density = sum((Fraction(1, d) for d in moduli), Fraction())
        ranked.append((density, L, moduli, factors))

    if args.sort == "density":
        ranked.sort(key=lambda row: (row[0], -row[1]), reverse=True)
    else:
        ranked = [row for row in ranked if row[0] >= 1]
        ranked.sort(key=lambda row: (row[1], -row[0]))
    for density, L, moduli, factors in ranked[: args.top]:
        print(
            f"L={L} factors={factors} count={len(moduli)} "
            f"density={density} ({float(density):.12f})"
        )
        print("moduli=" + ",".join(map(str, moduli)))


if __name__ == "__main__":
    main()
