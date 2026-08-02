"""Candidate-first search for the remaining order-five actions at order 25.

This imports the already audited definition-level quotient encoder from the
fixed-five certificate package and adds lex leaders for generators of the
centralizer of the chosen order-five permutation.  A SAT edge list must still
pass ``../verify_graph.py`` independently.  UNSAT output is exploratory until
it is accompanied by a separately replayed proof certificate.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from pysat.solvers import Solver


PACKAGE = Path(__file__).resolve().parents[1] / "order5_fixed5"
sys.path.insert(0, str(PACKAGE))

from generate_cases import (  # noqa: E402
    N,
    add_lex_leader,
    build_formula,
    decode_model,
    edge_orbits,
    normalize_formula,
    sha256,
)


def centralizer_generators(fixed: int) -> list[tuple[str, list[int]]]:
    generators: list[tuple[str, list[int]]] = []

    # Adjacent transpositions generate all permutations of the fixed points.
    for left in range(fixed - 1):
        permutation = list(range(N))
        permutation[left], permutation[left + 1] = (
            permutation[left + 1],
            permutation[left],
        )
        generators.append((f"swap_fixed_{left}_{left + 1}", permutation))

    cycles = (N - fixed) // 5
    for cycle_index in range(cycles - 1):
        permutation = list(range(N))
        left_start = fixed + 5 * cycle_index
        right_start = left_start + 5
        for offset in range(5):
            permutation[left_start + offset] = right_start + offset
            permutation[right_start + offset] = left_start + offset
        generators.append((f"swap_cycles_{cycle_index}_{cycle_index + 1}", permutation))

    for cycle_index in range(cycles):
        permutation = list(range(N))
        start = fixed + 5 * cycle_index
        for offset in range(5):
            permutation[start + offset] = start + (offset + 1) % 5
        generators.append((f"rotate_cycle_{cycle_index}", permutation))
    return generators


def add_centralizer_lex(formula, fixed: int) -> dict:
    orbits = edge_orbits(fixed)
    edge_for_pair = {
        pair: variable
        for variable, orbit in enumerate(orbits, start=1)
        for pair in orbit
    }
    primary = list(range(1, len(orbits) + 1))
    generators = centralizer_generators(fixed)
    before_nv, before_clauses = formula.nv, len(formula.clauses)
    for _, permutation in generators:
        image = []
        for orbit in orbits:
            u, v = orbit[0]
            pair = tuple(sorted((permutation[u], permutation[v])))
            image.append(edge_for_pair[pair])
        add_lex_leader(formula, primary, image)
    return {
        "generators": [name for name, _ in generators],
        "variables": formula.nv - before_nv,
        "clauses": len(formula.clauses) - before_clauses,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed", type=int, choices=(10, 15, 20), required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()

    started = time.perf_counter()
    formula, metadata = build_formula(
        args.fixed,
        quotient=True,
        max_degree=17,
        no_dominating_edge=True,
        unique_witness_markers=True,
    )
    metadata["centralizer_lex"] = add_centralizer_lex(formula, args.fixed)
    metadata["clause_normalization"] = normalize_formula(formula)
    metadata["total_variables"] = formula.nv
    metadata["total_clauses"] = len(formula.clauses)
    args.cnf.parent.mkdir(parents=True, exist_ok=True)
    formula.to_file(str(args.cnf))
    metadata["cnf_sha256"] = sha256(args.cnf)
    metadata["build_seconds"] = time.perf_counter() - started

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
