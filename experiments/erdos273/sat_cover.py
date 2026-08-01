#!/usr/bin/env python3
"""Search for a p-1 distinct covering system at a prescribed period.

The Z3 model has one integer r_d for each admissible modulus d | L.  The
value -1 means unused; otherwise r_d is its unique chosen residue.  Covering
one full period is equivalent to covering all integers.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from fractions import Fraction
from pathlib import Path

from z3 import Int, Or, Solver, sat, unknown, unsat


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
    parser.add_argument("--timeout-ms", type=int, default=600_000)
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()

    started = time.time()
    moduli = admissible_moduli(args.L)
    density = sum((Fraction(1, d) for d in moduli), Fraction())
    print(f"period={args.L}")
    print(f"moduli_count={len(moduli)}")
    print(f"density={density} ({float(density):.12f})")
    print("moduli=" + ",".join(map(str, moduli)))
    if density < 1:
        print("result=UNSAT_BY_DENSITY")
        return

    solver = Solver()
    solver.set(timeout=args.timeout_ms)
    residues = {d: Int(f"r_{d}") for d in moduli}
    for d in moduli:
        solver.add(residues[d] >= -1, residues[d] < d)

    # The smallest modulus is forced whenever removing its reciprocal makes
    # the total density < 1.  Translation invariance then fixes its residue.
    first = moduli[0]
    if density - Fraction(1, first) < 1:
        solver.add(residues[first] == 0)
        print(f"symmetry_break=r_{first}=0")

    for x in range(args.L):
        solver.add(Or(*(residues[d] == x % d for d in moduli)))
        if x and x % 10_000 == 0:
            print(f"constraints_built={x} elapsed={time.time()-started:.3f}s")

    print(f"constraints_built={args.L} elapsed={time.time()-started:.3f}s")
    result = solver.check()
    print(f"result={result} elapsed={time.time()-started:.3f}s")
    if result == sat:
        model = solver.model()
        classes = [
            {"modulus": d, "prime": d + 1, "residue": model[residues[d]].as_long()}
            for d in moduli
            if model[residues[d]].as_long() >= 0
        ]
        payload = {"period": args.L, "classes": classes}
        print(json.dumps(payload, indent=2))
        if args.certificate:
            args.certificate.write_text(json.dumps(payload, indent=2) + "\n")
    elif result == unknown:
        print(f"reason_unknown={solver.reason_unknown()}")
    elif result != unsat:
        raise RuntimeError(f"unexpected Z3 result: {result}")


if __name__ == "__main__":
    main()
