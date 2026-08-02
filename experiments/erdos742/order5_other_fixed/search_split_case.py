"""Solve one disjoint fixed-edge-count case for the remaining order-five actions.

The monolithic search uses a weighted automaton for

    (# fixed--fixed edges) + 5 * (# moving edge orbits) = 157.

For a supplied feasible fixed-edge count, the audited base encoder instead
uses two ordinary exact-cardinality constraints.  The cases partition the
monolithic search space and retain the same centralizer lex leaders.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
FIXED5 = HERE.parent / "order5_fixed5"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(FIXED5))

from generate_cases import (  # noqa: E402
    build_formula,
    decode_model,
    normalize_formula,
    sha256,
)
from search import add_centralizer_lex  # noqa: E402


def feasible_fixed_edge_counts(fixed: int) -> list[int]:
    singleton_orbits = fixed * (fixed - 1) // 2
    cycles = (25 - fixed) // 5
    moving_orbits = fixed * cycles + 2 * cycles + 5 * cycles * (cycles - 1) // 2
    return [
        fixed_edges
        for fixed_edges in range(singleton_orbits + 1)
        if (157 - fixed_edges) % 5 == 0
        and 0 <= (157 - fixed_edges) // 5 <= moving_orbits
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed", type=int, choices=(10, 15, 20), required=True)
    parser.add_argument("--fixed-edge-count", type=int, required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()

    feasible = feasible_fixed_edge_counts(args.fixed)
    if args.fixed_edge_count not in feasible:
        raise ValueError(
            f"infeasible fixed-edge count {args.fixed_edge_count}; expected one of {feasible}"
        )

    started = time.perf_counter()
    formula, metadata = build_formula(
        args.fixed,
        quotient=True,
        fixed_edge_count=args.fixed_edge_count,
        max_degree=17,
        no_dominating_edge=True,
        unique_witness_markers=True,
    )
    metadata["centralizer_lex"] = add_centralizer_lex(formula, args.fixed)
    metadata["clause_normalization"] = normalize_formula(formula)
    metadata["total_variables"] = formula.nv
    metadata["total_clauses"] = len(formula.clauses)
    metadata["split_partition"] = {
        "feasible_fixed_edge_counts": feasible,
        "selected_fixed_edge_count": args.fixed_edge_count,
        "cases": len(feasible),
    }
    args.cnf.parent.mkdir(parents=True, exist_ok=True)
    formula.to_file(str(args.cnf))
    metadata["cnf_sha256"] = sha256(args.cnf)
    metadata["build_seconds"] = time.perf_counter() - started

    if not args.build_only:
        solved = time.perf_counter()
        with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
            sat = solver.solve()
            metadata["solver"] = args.solver
            metadata["solver_result"] = "SAT" if sat else "UNSAT"
            metadata["solver_seconds"] = time.perf_counter() - solved
            metadata["solver_stats"] = solver.accum_stats()
            if sat:
                candidate = decode_model(solver.get_model(), args.fixed, quotient=True)
                args.candidate.parent.mkdir(parents=True, exist_ok=True)
                args.candidate.write_text(
                    json.dumps(candidate, indent=2) + "\n", encoding="utf-8"
                )
                metadata["candidate_sha256"] = sha256(args.candidate)

    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
