#!/usr/bin/env python3
"""Independent exact audit of the recorded #701 equality extremizer.

This checker consumes only the recorded family masks.  It reconstructs the
disjointness graph directly and maximizes an intersecting subfamily with RC2.
It does not import either discovery encoding.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import pysat
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.input.read_text(encoding="utf-8"))
    family = sorted(source["family_masks"])
    if not family or len(set(family)) != len(family):
        raise AssertionError("family masks must be nonempty and distinct")

    family_set = set(family)
    for member in family:
        subset = member
        while True:
            if subset not in family_set:
                raise AssertionError("family is not downward closed")
            if subset == 0:
                break
            subset = (subset - 1) & member

    n = 8
    stars = [sum(bool(member & (1 << x)) for member in family) for x in range(n)]
    formula = WCNF()
    for index in range(1, len(family) + 1):
        formula.append([index], weight=1)

    disjointness_constraints = 0
    for i, left in enumerate(family):
        for j in range(i + 1, len(family)):
            if left & family[j] == 0:
                formula.append([-(i + 1), -(j + 1)])
                disjointness_constraints += 1

    with RC2(formula, solver="cadical195") as solver:
        model = solver.compute()
        if model is None:
            raise AssertionError("RC2 unexpectedly returned no model")
        chosen = sorted(family[lit - 1] for lit in model if 1 <= lit <= len(family))
        cost = solver.cost

    for i, left in enumerate(chosen):
        for right in chosen[i + 1 :]:
            if left & right == 0:
                raise AssertionError("reported optimum is not intersecting")

    optimum = len(chosen)
    if optimum != len(family) - cost:
        raise AssertionError("RC2 objective accounting mismatch")
    result = {
        "schema": "erdos701-equality-extremizer-root-rc2-audit-v1",
        "status": "VERIFIED_EQUALITY" if optimum == max(stars) else "CHECK_FAILED",
        "input": {
            "path": str(args.input),
            "sha256": sha256(args.input),
            "family_size": len(family),
        },
        "ground_set_size": n,
        "downward_closed": True,
        "star_sizes": stars,
        "maximum_star_size": max(stars),
        "disjointness_constraints": disjointness_constraints,
        "maximum_intersecting_size": optimum,
        "minimum_counterexample_gap": optimum - max(stars),
        "maximum_intersecting_witness_masks": chosen,
        "backend": {
            "optimizer": "PySAT RC2",
            "sat_solver": "CaDiCaL 1.9.5",
            "python": platform.python_version(),
            "python_sat": pysat.__version__,
            "rc2_cost": cost,
        },
        "claim_boundary": (
            "This exactly audits one recorded downset. Equality is not a "
            "counterexample and says nothing exhaustive about all n=8 downsets."
        ),
    }
    if result["status"] != "VERIFIED_EQUALITY":
        raise AssertionError("recorded family is not an equality extremizer")
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "status", "maximum_intersecting_size", "maximum_star_size",
        "minimum_counterexample_gap", "disjointness_constraints"
    )}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
