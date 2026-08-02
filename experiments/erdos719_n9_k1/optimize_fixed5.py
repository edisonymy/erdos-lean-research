#!/usr/bin/env python3
"""Exact MaxSAT probe for the n=9, r=3, packing-number-one lane of #719.

For a 3-graph G, a K_4^3 copy is identified with its four vertices.  Two
copies share a 3-edge exactly when their vertex sets meet in three vertices.
Every 3-intersecting family of 4-sets is either a common-triple family or is
contained in a fixed 5-set (the short classification proof is in RESULTS.md).

This program optimizes the latter case.  It forces every K_4^3 of G to lie in
{0,1,2,3,4}, then maximizes the number of present triples with RC2 MaxSAT.
The emitted model is discovery evidence; check_result.py independently
recomputes all definition-level quantities using only the standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF


N = 9
R = 3
FIXED_FIVE = frozenset(range(5))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--anchor-k4", action="store_true")
    parser.add_argument("--json-out", type=Path, default=Path("result.json"))
    args = parser.parse_args()

    started = time.monotonic()
    edges = list(itertools.combinations(range(N), R))
    edge_id = {edge: i + 1 for i, edge in enumerate(edges)}
    four_sets = list(itertools.combinations(range(N), R + 1))

    formula = WCNF()
    forbidden_four_sets = 0
    for vertices in four_sets:
        if set(vertices).issubset(FIXED_FIVE):
            continue
        formula.append(
            [-edge_id[edge] for edge in itertools.combinations(vertices, R)]
        )
        forbidden_four_sets += 1
    if args.anchor_k4:
        # Above the K_4^3-free extremal value 54, an allowed copy exists in
        # the fixed five-set. Its S_5 symmetry moves it to 0123.
        for edge in itertools.combinations(range(4), R):
            formula.append([edge_id[edge]])
    for variable in range(1, len(edges) + 1):
        formula.append([variable], weight=1)

    with RC2(
        formula,
        solver=args.solver,
        adapt=True,
        exhaust=True,
        minz=True,
        trim=5,
    ) as optimizer:
        model = set(optimizer.compute())
        optimum_cost = optimizer.cost

    selected = [edge for edge in edges if edge_id[edge] in model]
    present_four_sets = [
        vertices
        for vertices in four_sets
        if all(edge in set(selected) for edge in itertools.combinations(vertices, R))
    ]
    edge_count = len(selected)
    payload = {
        "schema": "erdos719-n9-k1-fixed5-maxsat-v1",
        "problem": 719,
        "status": "OPTIMAL_SOLVER_RESULT",
        "solver": args.solver,
        "r": R,
        "n": N,
        "fixed_five": sorted(FIXED_FIVE),
        "anchor_k4_0123": args.anchor_k4,
        "edge_universe": len(edges),
        "forbidden_four_set_clauses": forbidden_four_sets,
        "soft_unit_clauses": len(edges),
        "optimum_cost": optimum_cost,
        "maximum_edges": edge_count,
        "present_k4_3_vertex_sets": [list(x) for x in present_four_sets],
        "edges": [list(edge) for edge in selected],
        "certified_ex_3_9": 54,
        "packing_upper_bound": 1,
        "minimum_parts_if_packing_one": edge_count - 3,
        "margin_over_ex_if_packing_one": edge_count - 3 - 54,
        "seconds": time.monotonic() - started,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["content_sha256_without_hash_field"] = hashlib.sha256(canonical).hexdigest()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
