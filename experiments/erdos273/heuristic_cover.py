#!/usr/bin/env python3
"""Randomized coordinate descent for candidate covering systems.

This is only a witness finder.  Any zero-uncovered output must still pass
check_certificate.py; nonzero output has no mathematical force.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path

import numpy as np


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    return all(n % d for d in range(3, math.isqrt(n) + 1, 2))


def admissible_moduli(L: int) -> list[int]:
    return [d for d in range(4, L + 1, 2) if L % d == 0 and is_prime(d + 1)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("L", type=int)
    parser.add_argument("--seconds", type=float, default=600)
    parser.add_argument("--seed", type=int, default=273)
    parser.add_argument("--noise", type=float, default=0.02)
    parser.add_argument("--fixed-parity", action="store_true")
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    moduli = admissible_moduli(args.L)
    deadline = time.time() + args.seconds
    best_uncovered = args.L + 1
    best_residue: dict[int, int] | None = None
    restarts = 0
    sweeps = 0

    while time.time() < deadline and best_uncovered:
        restarts += 1
        side: dict[int, int] = {}
        if args.fixed_parity:
            # A class with even modulus lies wholly in one parity.  Reject
            # random partitions unless each parity has enough raw density.
            half = args.L // 2
            while True:
                side = {d: rng.randrange(2) for d in moduli}
                side[moduli[0]] = 0
                mass0 = sum(args.L // d for d in moduli if side[d] == 0)
                if half <= mass0 <= sum(args.L // d for d in moduli) - half:
                    break
            residue = {
                d: rng.randrange(side[d], d, 2)
                for d in moduli
            }
        else:
            residue = {d: rng.randrange(d) for d in moduli}
        residue[moduli[0]] = 0  # translation symmetry
        count = np.zeros(args.L, dtype=np.int16)
        for d in moduli:
            count[residue[d] :: d] += 1

        stagnant = 0
        local_best = args.L + 1
        while time.time() < deadline and stagnant < 30 and best_uncovered:
            sweeps += 1
            order = moduli[1:]
            rng.shuffle(order)
            for d in order:
                old = residue[d]
                count[old::d] -= 1
                zeros = np.flatnonzero(count == 0)
                score = np.bincount(zeros % d, minlength=d)
                allowed = (
                    np.arange(side[d], d, 2)
                    if args.fixed_parity
                    else np.arange(d)
                )
                maximum = int(score[allowed].max())
                choices = allowed[score[allowed] == maximum]
                if rng.random() < args.noise:
                    new = int(allowed[rng.randrange(len(allowed))])
                else:
                    new = int(choices[rng.randrange(len(choices))])
                residue[d] = new
                count[new::d] += 1

            uncovered = int(np.count_nonzero(count == 0))
            if uncovered < best_uncovered:
                best_uncovered = uncovered
                best_residue = residue.copy()
                print(
                    f"best_uncovered={best_uncovered} restarts={restarts} "
                    f"sweeps={sweeps} elapsed={args.seconds-(deadline-time.time()):.3f}s",
                    flush=True,
                )
            if uncovered < local_best:
                local_best = uncovered
                stagnant = 0
            else:
                stagnant += 1

    print(
        f"result={'SAT' if best_uncovered == 0 else 'NO_WITNESS'} "
        f"best_uncovered={best_uncovered} restarts={restarts} sweeps={sweeps}",
        flush=True,
    )
    if best_uncovered == 0 and best_residue is not None:
        payload = {
            "period": args.L,
            "classes": [
                {"modulus": d, "prime": d + 1, "residue": best_residue[d]}
                for d in moduli
            ],
        }
        print(json.dumps(payload, indent=2), flush=True)
        if args.certificate:
            args.certificate.write_text(json.dumps(payload, indent=2) + "\n")


if __name__ == "__main__":
    main()
