#!/usr/bin/env python3
"""Direct SAT threshold test for the fixed-five branch of the #719 probe."""

from __future__ import annotations

import argparse
import itertools
import json
import threading
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--anchor-k4", action="store_true")
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()

    started = time.monotonic()
    n = 9
    edges = list(itertools.combinations(range(n), 3))
    edge_id = {edge: i + 1 for i, edge in enumerate(edges)}
    fixed_five = set(range(5))
    solver = Solver(name=args.solver)
    forbidden = 0
    for vertices in itertools.combinations(range(n), 4):
        if set(vertices).issubset(fixed_five):
            continue
        solver.add_clause(
            [-edge_id[edge] for edge in itertools.combinations(vertices, 3)]
        )
        forbidden += 1
    if args.anchor_k4:
        # Any solution above ex_3(9)=54 has a K_4^3.  All allowed copies lie
        # in the fixed five-set, whose S_5 symmetry moves one to 0123.
        for edge in itertools.combinations(range(4), 3):
            solver.add_clause([edge_id[edge]])
    cardinality = CardEnc.atleast(
        lits=list(range(1, len(edges) + 1)),
        bound=args.threshold,
        top_id=len(edges),
        encoding=EncType.totalizer,
    )
    solver.append_formula(cardinality.clauses)
    timer = threading.Timer(args.timeout_seconds, solver.interrupt)
    timer.start()
    try:
        status = solver.solve_limited(expect_interrupt=True)
    finally:
        timer.cancel()
    payload = {
        "schema": "erdos719-n9-k1-fixed5-threshold-v1",
        "n": n,
        "r": 3,
        "solver": args.solver,
        "edge_threshold": args.threshold,
        "forbidden_four_set_clauses": forbidden,
        "anchor_k4_0123": args.anchor_k4,
        "cardinality_clauses": len(cardinality.clauses),
        "status": "sat" if status is True else "unsat" if status is False else "unknown",
        "seconds": time.monotonic() - started,
        "edges": [],
    }
    if status is True:
        model = set(solver.get_model())
        payload["edges"] = [list(edge) for edge in edges if edge_id[edge] in model]
    solver.delete()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
