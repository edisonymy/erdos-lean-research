#!/usr/bin/env python3
"""Exact SAT search for finite counterexamples to Erdos problem 128.

A counterexample on n vertices is a triangle-free graph in which every
floor(n/2)-vertex set spans at least floor(n^2/50)+1 edges.  It is enough to
check sets of exactly floor(n/2) vertices, since adding vertices never removes
edges.

This script uses Z3 pseudo-Boolean constraints.  No floating-point arithmetic
is used.  A SAT model is written as a plain edge list that can be checked by
the separate checker.py program.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import z3


def edge_key(i: int, j: int) -> tuple[int, int]:
    return (i, j) if i < j else (j, i)


def build(n: int, timeout_ms: int, alpha_upper: int | None) -> tuple[z3.Solver, dict[tuple[int, int], z3.BoolRef]]:
    k = n // 2
    threshold = n * n // 50 + 1
    edges = {
        (i, j): z3.Bool(f"e_{i}_{j}")
        for i in range(n)
        for j in range(i + 1, n)
    }
    solver = z3.Solver()
    if timeout_ms:
        solver.set(timeout=timeout_ms)

    # Triangle-free.
    for i, j, l in itertools.combinations(range(n), 3):
        solver.add(z3.Or(z3.Not(edges[i, j]), z3.Not(edges[i, l]), z3.Not(edges[j, l])))

    if alpha_upper is not None:
        for subset in itertools.combinations(range(n), alpha_upper + 1):
            solver.add(z3.Or([edges[edge_key(i, j)] for i, j in itertools.combinations(subset, 2)]))

    # Exact half-set constraints.  These also imply the condition for larger sets.
    for subset in itertools.combinations(range(n), k):
        inside = [edges[edge_key(i, j)] for i, j in itertools.combinations(subset, 2)]
        solver.add(z3.PbGe([(x, 1) for x in inside], threshold))

    return solver, edges


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    parser.add_argument("--timeout-ms", type=int, default=0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--alpha-upper", type=int)
    args = parser.parse_args()

    n = args.n
    if n < 4:
        raise SystemExit("n must be at least 4")
    k = n // 2
    threshold = n * n // 50 + 1
    print(json.dumps({"n": n, "half_size": k, "threshold": threshold,
                      "half_sets": __import__('math').comb(n, k)}), flush=True)
    start = time.monotonic()
    solver, edges = build(n, args.timeout_ms, args.alpha_upper)
    built = time.monotonic()
    result = solver.check()
    ended = time.monotonic()
    print(json.dumps({"result": str(result), "build_seconds": built - start,
                      "solve_seconds": ended - built, "reason_unknown": solver.reason_unknown()}),
          flush=True)

    if result == z3.sat:
        model = solver.model()
        selected = [[i, j] for (i, j), x in edges.items() if z3.is_true(model.eval(x))]
        payload = {"n": n, "edges": selected}
        output = args.output or Path(f"counterexample_n{n}.json")
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {output} with {len(selected)} edges")
    return 0 if result != z3.unknown else 2


if __name__ == "__main__":
    raise SystemExit(main())
