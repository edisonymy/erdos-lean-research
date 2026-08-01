#!/usr/bin/env python3
"""Deterministic semantic audit for the PySAT sequential counters used here."""

from __future__ import annotations

import json
import random

import pysat
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


EXPECTED_PYSAT = "1.9.dev7"


def encoded_result(width: int, bound: int, assignment: tuple[bool, ...]) -> bool:
    literals = list(range(1, width + 1))
    cnf = CardEnc.atleast(literals, bound=bound, top_id=width,
                          encoding=EncType.seqcounter)
    units = [index + 1 if value else -(index + 1)
             for index, value in enumerate(assignment)]
    with Solver(name="cadical195",
                bootstrap_with=cnf.clauses + [[unit] for unit in units]) as solver:
        return solver.solve()


def deterministic_assignments(width: int, count: int) -> list[tuple[bool, ...]]:
    assignments: set[tuple[bool, ...]] = set()
    # Include every weight and rotations around the decision boundary.
    for weight in range(width + 1):
        for offset in range(width):
            assignment = tuple(
                ((index - offset) % width) < weight for index in range(width)
            )
            assignments.add(assignment)
            if len(assignments) >= count:
                return sorted(assignments)[:count]
    rng = random.Random(1281606)
    while len(assignments) < count:
        assignments.add(tuple(bool(rng.getrandbits(1)) for _ in range(width)))
    return sorted(assignments)[:count]


def main() -> None:
    if pysat.__version__ != EXPECTED_PYSAT:
        raise SystemExit(
            f"expected python-sat {EXPECTED_PYSAT}, found {pysat.__version__}"
        )

    small = [
        tuple(bool(mask & (1 << index)) for index in range(6))
        for mask in range(1 << 6)
    ]
    large = deterministic_assignments(28, 1029)
    for width, bound, assignments in ((6, 2, small), (28, 6, large)):
        for assignment in assignments:
            observed = encoded_result(width, bound, assignment)
            expected = sum(assignment) >= bound
            if observed != expected:
                raise AssertionError(
                    f"counter mismatch width={width} bound={bound} assignment={assignment}"
                )

    print(json.dumps({
        "python_sat": pysat.__version__,
        "small_width": 6,
        "small_bound": 2,
        "small_assignments": len(small),
        "order16_width": 28,
        "order16_bound": 6,
        "order16_assignments": len(large),
        "status": "PASS",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
