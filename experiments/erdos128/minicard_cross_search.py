#!/usr/bin/env python3
"""Second exact order-16 attack using MiniCard native cardinality constraints.

This is intentionally independent of z3_cross_search.py: it constructs a
CNFPlus formula directly, uses no Z3 expressions, uses MiniCard rather than
Z3's QF_FD backend, and omits the Z3 outside-neighbourhood sorting symmetry.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from pysat.formula import CNFPlus, IDPool
from pysat.solvers import Solver


N = 16
I = range(6)
O = range(6, 16)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cross_degree", type=int, choices=(1, 2, 3))
    parser.add_argument("--model", type=Path)
    args = parser.parse_args()

    started = time.monotonic()
    pool = IDPool()
    edge_vars = {
        (i, j): pool.id(("edge", i, j))
        for i in range(N)
        for j in range(i + 1, N)
    }

    def edge(i: int, j: int) -> int:
        return edge_vars[tuple(sorted((i, j)))]

    formula = CNFPlus()
    groups: dict[str, int] = {}

    for i, j, k in itertools.combinations(range(N), 3):
        formula.append([-edge(i, j), -edge(i, k), -edge(j, k)])
    groups["triangle_free_clauses"] = 560

    for i, j in itertools.combinations(I, 2):
        formula.append([-edge(i, j)])
    groups["fixed_independent_six_units"] = 15

    for subset in itertools.combinations(range(N), 7):
        formula.append([edge(i, j) for i, j in itertools.combinations(subset, 2)])
    groups["alpha_at_most_six_clauses"] = 11440

    # At least six edges among 28 is at most 22 negated edge literals.  These
    # remain native MiniCard constraints; there is no source-level counter CNF.
    for subset in itertools.combinations(range(N), 8):
        formula.append(
            [[-edge(i, j) for i, j in itertools.combinations(subset, 2)], 22],
            is_atmost=True,
        )
    groups["dense_half_native_atmost"] = 12870

    # Maximal triangle-free: if ij is absent, choose a common-neighbour
    # witness.  Only witness -> the two incident edges is needed, since the
    # long clause existentially chooses a witness whenever ij is false.
    maximality_clauses = 0
    for i, j in itertools.combinations(range(N), 2):
        witnesses = []
        for k in range(N):
            if k in (i, j):
                continue
            witness = pool.id(("common", i, j, k))
            witnesses.append(witness)
            formula.append([-witness, edge(i, k)])
            formula.append([-witness, edge(j, k)])
            maximality_clauses += 2
        formula.append([edge(i, j), *witnesses])
        maximality_clauses += 1
    groups["maximal_triangle_free_clauses"] = maximality_clauses

    d = args.cross_degree
    for i in I:
        formula.append([edge(i, 6) if i < d else -edge(i, 6)])
    groups["prefix_units"] = 6
    for v in O:
        formula.append(
            [[-edge(i, v) for i in I], 6 - d],
            is_atmost=True,
        )
    groups["minimum_cross_degree_native_atmost"] = 10

    # Averaged consequence of the half constraints: at least 26 of 120 edges.
    formula.append([[-var for var in edge_vars.values()], 94], is_atmost=True)
    groups["global_edge_native_atmost"] = 1

    encoded = time.monotonic()
    print(
        json.dumps(
            {
                "event": "encoded",
                "n": N,
                "cross_degree": d,
                "solver": "minicard",
                "edge_variables": len(edge_vars),
                "variables_with_witnesses": pool.top,
                "ordinary_clauses": len(formula.clauses),
                "native_atmost_constraints": len(formula.atmosts),
                "constraint_groups": groups,
                "encode_seconds": encoded - started,
                "z3_neighbourhood_order_symmetry": False,
            }
        ),
        flush=True,
    )

    with Solver(name="minicard", bootstrap_with=formula, use_timer=True) as solver:
        sat = solver.solve()
        finished = time.monotonic()
        print(
            json.dumps(
                {
                    "event": "result",
                    "result": "sat" if sat else "unsat",
                    "cross_degree": d,
                    "solve_seconds": finished - encoded,
                    "solver_time": solver.time(),
                    "statistics": solver.accum_stats(),
                }
            ),
            flush=True,
        )
        if sat:
            model = set(solver.get_model())
            selected = [
                [i, j]
                for (i, j), variable in edge_vars.items()
                if variable in model
            ]
            output = args.model or Path(f"counterexample_n16_minicard_d{d}.json")
            output.write_text(
                json.dumps({"n": N, "edges": selected}, indent=2) + "\n",
                encoding="utf-8",
            )
            print(json.dumps({"event": "model", "path": str(output), "edges": len(selected)}))
            return 10
    return 20


if __name__ == "__main__":
    raise SystemExit(main())
