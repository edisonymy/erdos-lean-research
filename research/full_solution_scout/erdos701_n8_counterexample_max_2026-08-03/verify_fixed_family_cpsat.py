#!/usr/bin/env python3
"""Definition-level and exact-beta audit of a fixed n=8 family."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from ortools.sat.python import cp_model


N = 8
M = 1 << N


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--seconds", type=float, default=300.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    family = sorted(set(source["family_masks"]))
    recorded = sorted(set(source["witness_masks"]))
    fset = set(family)

    union = 0
    for s in family:
        union |= s
    down_violations = [
        (s, t) for s in family for t in range(M)
        if (t & s) == t and t not in fset
    ]
    subset_violations = [s for s in recorded if s not in fset]
    empty_violations = [s for s in recorded if s == 0]
    disjoint_violations = [
        (s, t) for i, s in enumerate(recorded) for t in recorded[i + 1:]
        if (s & t) == 0
    ]
    stars = [sum(1 for s in family if s & (1 << x)) for x in range(N)]

    vertices = [s for s in family if s != 0]
    model = cp_model.CpModel()
    b = {s: model.new_bool_var(f"b_{s}") for s in vertices}
    disjoint_constraints = 0
    for i, s in enumerate(vertices):
        for t in vertices[i + 1:]:
            if (s & t) == 0:
                model.add(b[s] + b[t] <= 1)
                disjoint_constraints += 1
    objective = sum(b.values())
    model.maximize(objective)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = 7010831
    started = time.time()
    answer = solver.solve(model)
    elapsed = time.time() - started
    statuses = {
        cp_model.OPTIMAL: "OPTIMAL_CERTIFIED_BY_SOLVER",
        cp_model.FEASIBLE: "FEASIBLE_NOT_PROVED_OPTIMAL",
        cp_model.INFEASIBLE: "INFEASIBLE_UNEXPECTED",
        cp_model.UNKNOWN: "UNKNOWN_TIMEOUT",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
    }
    chosen = None
    beta = None
    if answer in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = [s for s in vertices if solver.value(b[s])]
        beta = len(chosen)

    result = {
        "schema": "erdos701-fixed-family-cpsat-audit-v1",
        "source": str(args.source),
        "definition_audit": {
            "ground_union": union,
            "ground_union_is_255": union == M - 1,
            "empty_in_family": 0 in fset,
            "down_violations": down_violations,
            "recorded_subset_violations": subset_violations,
            "recorded_empty_violations": empty_violations,
            "recorded_disjoint_pairs": disjoint_violations,
            "recorded_witness_size": len(recorded),
            "star_sizes": stars,
            "recorded_minimum_star_gap": min(len(recorded) - z for z in stars),
        },
        "exact_beta_cpsat": {
            "status": statuses.get(answer, str(answer)),
            "elapsed_seconds": elapsed,
            "time_limit_seconds": args.seconds,
            "disjoint_constraints": disjoint_constraints,
            "maximum_intersecting_size": beta,
            "maximum_intersecting_masks": chosen,
            "best_objective_bound": solver.best_objective_bound,
            "conflicts": solver.num_conflicts,
            "branches": solver.num_branches,
            "response_stats": solver.response_stats(),
        },
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.out.write_bytes(payload.encode())
    print(json.dumps({
        "status": result["exact_beta_cpsat"]["status"],
        "beta": beta,
        "max_star": max(stars),
        "recorded_size": len(recorded),
        "sha256": hashlib.sha256(payload.encode()).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
