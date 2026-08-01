#!/usr/bin/env python3
"""Semantic audit for the order-16 cross-case proof CNF helpers.

The audit is not an order-16 UNSAT proof.  It checks that the exact sequential
counter helper is existentially equivalent to native at-least constraints on
all small assignments, exercises the three target six-input bounds
exhaustively, samples both larger target counters, and exhaustively checks the
maximality-witness helper on all graphs through order five.
"""

from __future__ import annotations

import itertools
import json
import random

import pysat
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

from cross_proof_cnf import append_atleast, append_maximal_triangle_free


def audit_counter(
    width: int, bound: int, assignments: list[tuple[bool, ...]]
) -> int:
    pool = IDPool()
    variables = [pool.id(("input", i)) for i in range(width)]
    cnf = CNF()
    append_atleast(cnf, pool, variables, bound)
    assert cnf.nv == pool.top
    with Solver(name="cadical195", bootstrap_with=cnf.clauses) as solver:
        for assignment in assignments:
            assumptions = [
                variable if value else -variable
                for variable, value in zip(variables, assignment, strict=True)
            ]
            expected = sum(assignment) >= bound
            assert solver.solve(assumptions=assumptions) == expected
    return len(assignments)


def exhaustive_small_counters() -> int:
    checked = 0
    for width in range(1, 9):
        assignments = list(itertools.product((False, True), repeat=width))
        for bound in range(width + 1):
            checked += audit_counter(width, bound, assignments)
    return checked


def target_counter_assignments(width: int, seed: int) -> list[tuple[bool, ...]]:
    result: set[tuple[bool, ...]] = set()
    # Every Hamming weight gets a prefix, suffix, and deterministic rotation.
    for weight in range(width + 1):
        prefix = (True,) * weight + (False,) * (width - weight)
        result.add(prefix)
        result.add(tuple(reversed(prefix)))
        shift = (7 * weight + 3) % width
        result.add(prefix[shift:] + prefix[:shift])
    random_source = random.Random(seed)
    for _ in range(1029):
        result.add(tuple(bool(random_source.getrandbits(1)) for _ in range(width)))
    return sorted(result)


def target_counters() -> dict[str, int]:
    record: dict[str, int] = {}
    six_assignments = list(itertools.product((False, True), repeat=6))
    for bound in (1, 2, 3):
        record[f"width_6_bound_{bound}"] = audit_counter(6, bound, six_assignments)
    for width, bound, seed in ((28, 6, 1282806), (120, 26, 12812026)):
        assignments = target_counter_assignments(width, seed)
        record[f"width_{width}_bound_{bound}"] = audit_counter(
            width, bound, assignments
        )
    return record


def has_edge(edges: set[tuple[int, int]], i: int, j: int) -> bool:
    return tuple(sorted((i, j))) in edges


def audit_maximality_witness() -> int:
    checks = 0
    for n in range(2, 6):
        edge_list = list(itertools.combinations(range(n), 2))
        pool = IDPool()
        edge_variables = {
            edge: pool.id(("edge", *edge)) for edge in edge_list
        }
        cnf = CNF()
        append_maximal_triangle_free(cnf, pool, edge_variables, n)
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as solver:
            for mask in range(1 << len(edge_list)):
                edges = {
                    edge for bit, edge in enumerate(edge_list) if mask >> bit & 1
                }
                assumptions = [
                    edge_variables[edge]
                    if edge in edges
                    else -edge_variables[edge]
                    for edge in edge_list
                ]
                expected = all(
                    has_edge(edges, i, j)
                    or any(
                        has_edge(edges, i, k) and has_edge(edges, j, k)
                        for k in range(n)
                        if k not in (i, j)
                    )
                    for i, j in edge_list
                )
                assert solver.solve(assumptions=assumptions) == expected
                checks += 1
    return checks


def main() -> int:
    payload = {
        "status": "PASS",
        "python_sat": pysat.__version__,
        "exhaustive_small_cardinality_assignments": exhaustive_small_counters(),
        "target_cardinality_assignments": target_counters(),
        "maximality_graph_assignments": audit_maximality_witness(),
        "scope": (
            "semantic helper audit only; this does not establish order-16 UNSAT "
            "or verify a proof certificate"
        ),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
