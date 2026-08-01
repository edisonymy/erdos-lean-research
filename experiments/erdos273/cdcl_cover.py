#!/usr/bin/env python3
"""Native-CNF search for a p-1 distinct covering system."""

from __future__ import annotations

import argparse
import json
import math
import threading
import time
from fractions import Fraction
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    return all(n % d for d in range(3, math.isqrt(n) + 1, 2))


def admissible_moduli(L: int, allow_two: bool = False) -> list[int]:
    lower = 2 if allow_two else 4
    return [d for d in range(lower, L + 1, 2) if L % d == 0 and is_prime(d + 1)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("L", type=int)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--allow-two", action="store_true")
    args = parser.parse_args()
    started = time.time()

    moduli = admissible_moduli(args.L, args.allow_two)
    density = sum((Fraction(1, d) for d in moduli), Fraction())
    print(f"period={args.L}", flush=True)
    print(f"moduli_count={len(moduli)}", flush=True)
    print(f"density={density} ({float(density):.12f})", flush=True)
    print("moduli=" + ",".join(map(str, moduli)), flush=True)
    if density < 1:
        print("result=UNSAT_BY_DENSITY", flush=True)
        return

    variable: dict[tuple[int, int], int] = {}
    next_variable = 1
    for d in moduli:
        for r in range(d):
            variable[d, r] = next_variable
            next_variable += 1
    primary_variables = next_variable - 1

    cnf = CNF()
    top_id = primary_variables
    for d in moduli:
        encoded = CardEnc.atmost(
            [variable[d, r] for r in range(d)],
            bound=1,
            top_id=top_id,
            encoding=EncType.seqcounter,
        )
        cnf.extend(encoded.clauses)
        top_id = encoded.nv

    mandatory = [d for d in moduli if density - Fraction(1, d) < 1]
    for d in mandatory:
        cnf.append([variable[d, r] for r in range(d)])
    print("mandatory=" + ",".join(map(str, mandatory)), flush=True)

    # If two chosen classes intersect, their intersection has density
    # 1/lcm(d,e).  The total multiplicity excess is at most density-1, hence
    # an intersection larger than this is impossible in any cover.  Encode
    # all such pairwise incompatibilities explicitly.
    excess = density - 1
    structural_binary_clauses = 0
    for i, d in enumerate(moduli):
        for e in moduli[i + 1 :]:
            if Fraction(1, math.lcm(d, e)) <= excess:
                continue
            g = math.gcd(d, e)
            for rd in range(d):
                for re in range(rd % g, e, g):
                    cnf.append([-variable[d, rd], -variable[e, re]])
                    structural_binary_clauses += 1
    print(f"structural_binary_clauses={structural_binary_clauses}", flush=True)

    # The first modulus is forced by density and translations act transitively
    # on its residues, so select residue zero without loss of generality.
    first = moduli[0]
    if density - Fraction(1, first) < 1:
        cnf.append([variable[first, 0]])
        print(f"symmetry_break=r_{first}=0", flush=True)

    for x in range(args.L):
        cnf.append([variable[d, x % d] for d in moduli])
    print(
        f"cnf_primary_variables={primary_variables} cnf_variables={cnf.nv} "
        f"cnf_clauses={len(cnf.clauses)} build_elapsed={time.time()-started:.3f}s",
        flush=True,
    )

    with Solver(name=args.solver, bootstrap_with=cnf.clauses) as solver:
        timer = threading.Timer(args.timeout, solver.interrupt)
        timer.start()
        try:
            result = solver.solve_limited(expect_interrupt=True)
        finally:
            timer.cancel()
        print(
            f"result={result} elapsed={time.time()-started:.3f}s "
            f"stats={solver.accum_stats()}",
            flush=True,
        )
        if result is True:
            model = set(lit for lit in solver.get_model() if lit > 0)
            classes = [
                {"modulus": d, "prime": d + 1, "residue": r}
                for d in moduli
                for r in range(d)
                if variable[d, r] in model
            ]
            payload = {"period": args.L, "classes": classes}
            print(json.dumps(payload, indent=2), flush=True)
            if args.certificate:
                args.certificate.write_text(json.dumps(payload, indent=2) + "\n")


if __name__ == "__main__":
    main()
