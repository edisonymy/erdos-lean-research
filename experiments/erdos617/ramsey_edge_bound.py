#!/usr/bin/env python3
"""Exact SAT test for sparse (K6,K6)-Ramsey graphs on 26 vertices.

A counterexample coloring for Erdos 617 at r=5 would make each color class
a graph with neither a six-clique nor a six-independent set.  If no such
graph has at most 65 edges, summing over the five color classes proves the
r=5 case immediately.
"""

from __future__ import annotations

import argparse
import itertools
import json
import threading
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver


N = 26
EDGES = [(u, v) for u in range(N) for v in range(u + 1, N)]
EDGE_INDEX = {edge: i + 1 for i, edge in enumerate(EDGES)}


def solve_limited(solver: Solver, timeout: float) -> bool | None:
    timer = threading.Timer(timeout, solver.interrupt)
    timer.start()
    try:
        return solver.solve_limited(expect_interrupt=True)
    finally:
        timer.cancel()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=65)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    started = time.monotonic()
    cnf = CNF()
    six_sets = 0
    for vertices in itertools.combinations(range(N), 6):
        variables = [
            EDGE_INDEX[u, v]
            for u, v in itertools.combinations(vertices, 2)
        ]
        cnf.append(variables)
        cnf.append([-variable for variable in variables])
        six_sets += 1

    cardinality = CardEnc.atmost(
        list(range(1, len(EDGES) + 1)),
        bound=args.bound,
        top_id=len(EDGES),
        encoding=EncType.seqcounter,
    )
    cnf.extend(cardinality.clauses)
    print(
        f"vertices={N} edges={len(EDGES)} six_sets={six_sets} "
        f"edge_bound={args.bound} variables={cnf.nv} clauses={len(cnf.clauses)} "
        f"build_seconds={time.monotonic()-started:.3f}",
        flush=True,
    )

    with Solver(name=args.solver, bootstrap_with=cnf.clauses) as solver:
        result = solve_limited(solver, args.timeout)
        print(
            f"result={result} elapsed_seconds={time.monotonic()-started:.3f} "
            f"stats={solver.accum_stats()}",
            flush=True,
        )
        if result is not True:
            print("UNSAT" if result is False else "UNKNOWN", flush=True)
            return
        positive = {literal for literal in solver.get_model() if literal > 0}
        selected = [
            [u, v] for index, (u, v) in enumerate(EDGES, start=1)
            if index in positive
        ]
        payload = {"n": N, "edges": selected}
        print(f"SAT edge_count={len(selected)}", flush=True)
        if args.output:
            args.output.write_text(json.dumps(payload, indent=2) + "\n")


if __name__ == "__main__":
    main()
