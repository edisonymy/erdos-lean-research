#!/usr/bin/env python3
"""Independent exact Z3 attack on the remaining order-16 Erdos-128 case.

This encoding deliberately does not share PySAT's sequential-counter CNF
encoding.  It uses 120 Boolean edge variables and Z3 native pseudo-Boolean
constraints.  See Z3_CROSS_SEARCH.md for the sound reductions and symmetry.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import z3


N = 16
INDEPENDENT = range(6)
OUTSIDE = range(6, 16)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "cross_degree",
        type=int,
        choices=(1, 2, 3),
        help="minimum number of neighbours in the fixed independent six-set",
    )
    parser.add_argument("--model", type=Path)
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=0,
        help="Z3 timeout in milliseconds (zero means no timeout)",
    )
    parser.add_argument(
        "--solver",
        choices=("default", "qf_fd"),
        default="qf_fd",
        help="Z3 front-end; qf_fd sends the finite-domain formula to SAT",
    )
    args = parser.parse_args()

    started = time.monotonic()
    edges = {
        (i, j): z3.Bool(f"e_{i}_{j}")
        for i in range(N)
        for j in range(i + 1, N)
    }

    def edge(i: int, j: int) -> z3.BoolRef:
        if i == j:
            return z3.BoolVal(False)
        return edges[tuple(sorted((i, j)))]

    solver = z3.SolverFor("QF_FD") if args.solver == "qf_fd" else z3.Solver()
    if args.timeout_ms:
        solver.set(timeout=args.timeout_ms)

    groups: dict[str, int] = {}

    # Triangle-free.
    for i, j, k in itertools.combinations(range(N), 3):
        solver.add(z3.Or(z3.Not(edge(i, j)), z3.Not(edge(i, k)), z3.Not(edge(j, k))))
    groups["triangle_free"] = 560

    # The fixed maximum independent set I={0,...,5}.
    for i, j in itertools.combinations(INDEPENDENT, 2):
        solver.add(z3.Not(edge(i, j)))
    groups["fixed_independent_six"] = 15

    # alpha(G) <= 6: every seven-set contains an edge.
    for subset in itertools.combinations(range(N), 7):
        solver.add(z3.Or(*(edge(i, j) for i, j in itertools.combinations(subset, 2))))
    groups["alpha_at_most_six"] = 11440

    # Every eight-set spans at least 6 edges, the integral form of > 16^2/50.
    for subset in itertools.combinations(range(N), 8):
        solver.add(
            z3.PbGe(
                [(edge(i, j), 1) for i, j in itertools.combinations(subset, 2)],
                6,
            )
        )
    groups["dense_halves"] = 12870

    # It is lossless to extend a counterexample to a maximal triangle-free
    # graph.  For every pair uv, either uv is an edge or u,v have a common
    # neighbour (so adding uv would make a triangle).
    for i, j in itertools.combinations(range(N), 2):
        solver.add(
            z3.Or(
                edge(i, j),
                *(z3.And(edge(i, k), edge(j, k)) for k in range(N) if k not in (i, j)),
            )
        )
    groups["maximal_triangle_free"] = 120

    # Pick an outside vertex of minimum cross-degree, call it 6, and use S_6
    # on I to make its neighbourhood the prefix {0,...,d-1}.
    d = args.cross_degree
    for i in INDEPENDENT:
        solver.add(edge(i, 6) if i < d else z3.Not(edge(i, 6)))
    for v in OUTSIDE:
        solver.add(z3.PbGe([(edge(i, v), 1) for i in INDEPENDENT], d))
    groups["minimum_cross_degree_and_prefix"] = 16

    # Quotient the still-free S_9 action on vertices 7,...,15 by sorting their
    # six-bit I-neighbourhood codes.  This does not constrain vertex 6.
    def cross_code(v: int) -> z3.ArithRef:
        return z3.Sum(*(z3.If(edge(i, v), 1 << i, 0) for i in INDEPENDENT))

    for u, v in zip(range(7, 15), range(8, 16)):
        solver.add(cross_code(u) <= cross_code(v))
    groups["outside_neighbourhood_order"] = 8

    # This follows by averaging the 12,870 half inequalities, but exposing it
    # helps both backends propagate at the root.
    solver.add(z3.PbGe([(var, 1) for var in edges.values()], 26))
    groups["global_edge_lower_bound"] = 1

    encoded = time.monotonic()
    print(
        json.dumps(
            {
                "event": "encoded",
                "n": N,
                "cross_degree": d,
                "solver": args.solver,
                "z3_version": z3.get_version_string(),
                "edge_variables": len(edges),
                "constraint_groups": groups,
                "assertions": len(solver.assertions()),
                "encode_seconds": encoded - started,
            }
        ),
        flush=True,
    )

    result = solver.check()
    finished = time.monotonic()
    report = {
        "event": "result",
        "result": str(result),
        "cross_degree": d,
        "solver": args.solver,
        "solve_seconds": finished - encoded,
        "statistics": str(solver.statistics()),
    }
    if result == z3.unknown:
        report["reason_unknown"] = solver.reason_unknown()
    print(json.dumps(report), flush=True)

    if result == z3.sat:
        model = solver.model()
        selected = [
            [i, j]
            for (i, j), var in edges.items()
            if z3.is_true(model.eval(var, model_completion=True))
        ]
        output = args.model or Path(f"counterexample_n16_cross_d{d}.json")
        output.write_text(
            json.dumps({"n": N, "edges": selected}, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({"event": "model", "path": str(output), "edges": len(selected)}))
        return 10
    if result == z3.unsat:
        return 20
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
