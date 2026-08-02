#!/usr/bin/env python3
"""Independent Z3 encoding of the decisive fixed-five threshold."""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import z3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=58)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    edges = list(itertools.combinations(range(9), 3))
    edge_id = {edge: i for i, edge in enumerate(edges)}
    variables = [z3.Bool(f"edge_{i}") for i in range(len(edges))]
    solver = z3.Solver()
    solver.set(timeout=args.timeout_seconds * 1000)
    fixed_five = set(range(5))
    forbidden = 0
    for vertices in itertools.combinations(range(9), 4):
        if set(vertices).issubset(fixed_five):
            continue
        solver.add(
            z3.Or(
                [z3.Not(variables[edge_id[e]]) for e in itertools.combinations(vertices, 3)]
            )
        )
        forbidden += 1
    solver.add(z3.Sum([z3.If(v, 1, 0) for v in variables]) >= args.threshold)
    status = solver.check()
    payload = {
        "schema": "erdos719-n9-k1-fixed5-z3-threshold-v1",
        "n": 9,
        "r": 3,
        "edge_threshold": args.threshold,
        "forbidden_four_set_constraints": forbidden,
        "status": str(status),
        "seconds": time.monotonic() - started,
        "reason_unknown": solver.reason_unknown() if status == z3.unknown else None,
    }
    if status == z3.sat:
        model = solver.model()
        payload["edges"] = [
            list(edge) for edge, variable in zip(edges, variables)
            if z3.is_true(model.eval(variable, model_completion=True))
        ]
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
