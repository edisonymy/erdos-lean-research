#!/usr/bin/env python3
"""Exploratory CEGAR-SAT search over 8-sheeted permutation covers of K4.

After gauge-fixing a star spanning tree, a cover is determined by three
permutations of eight sheets.  Simultaneous sheet relabelling conjugates all
three permutations.  This program fixes the first permutation to one canonical
representative of each *nonidentity* conjugacy class, then excludes concrete
C4/C8/C16/C32 witnesses until CaDiCaL reports UNSAT or a candidate survives.

Important: the UNSAT results are not accompanied by DRAT/LRAT proofs.  They are
exploratory computational evidence, not a publishable computer-assisted theorem.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from collections.abc import Iterator
from pathlib import Path

from pysat import __version__ as pysat_version
from pysat.solvers import Solver

from verify_graph import find_simple_cycle, verify_cycle


Q = 8
COTREE_EDGES = [(1, 2), (1, 3), (2, 3)]
TARGET_LENGTHS = [4, 8, 16, 32]


def integer_partitions(total: int, minimum: int = 1) -> Iterator[list[int]]:
    if total == 0:
        yield []
        return
    for first in range(minimum, total + 1):
        for rest in integer_partitions(total - first, first):
            yield [first] + rest


def canonical_permutation(cycle_type: list[int]) -> list[int]:
    permutation = list(range(Q))
    start = 0
    for length in cycle_type:
        for offset in range(length):
            permutation[start + offset] = start + ((offset + 1) % length)
        start += length
    return permutation


def variables() -> tuple[dict[tuple[int, int, int], int], list[list[int]]]:
    variable: dict[tuple[int, int, int], int] = {}
    next_variable = 0
    for edge_index in range(3):
        for source in range(Q):
            for target in range(Q):
                next_variable += 1
                variable[edge_index, source, target] = next_variable

    clauses: list[list[int]] = []
    for edge_index in range(3):
        for source in range(Q):
            row = [variable[edge_index, source, target] for target in range(Q)]
            clauses.append(row)
            clauses.extend([-row[a], -row[b]] for a in range(Q) for b in range(a + 1, Q))
        for target in range(Q):
            column = [variable[edge_index, source, target] for source in range(Q)]
            clauses.append(column)
            clauses.extend(
                [-column[a], -column[b]] for a in range(Q) for b in range(a + 1, Q)
            )
    return variable, clauses


def model_to_cover(
    model: list[int], variable: dict[tuple[int, int, int], int]
) -> tuple[list[int], list[list[int]], dict[tuple[int, int], int]]:
    positive = {literal for literal in model if literal > 0}
    permutations = [
        [
            next(target for target in range(Q) if variable[e, source, target] in positive)
            for source in range(Q)
        ]
        for e in range(3)
    ]
    adjacency = [0] * (4 * Q)
    variable_for_lifted_edge: dict[tuple[int, int], int] = {}

    # Gauge-fixed star edges have identity permutations.
    for u, v in [(0, 1), (0, 2), (0, 3)]:
        for sheet in range(Q):
            x, y = u * Q + sheet, v * Q + sheet
            adjacency[x] |= 1 << y
            adjacency[y] |= 1 << x

    for edge_index, (u, v) in enumerate(COTREE_EDGES):
        for source, target in enumerate(permutations[edge_index]):
            x, y = u * Q + source, v * Q + target
            adjacency[x] |= 1 << y
            adjacency[y] |= 1 << x
            variable_for_lifted_edge[min(x, y), max(x, y)] = variable[
                edge_index, source, target
            ]
    return adjacency, permutations, variable_for_lifted_edge


def edge_list(adjacency: list[int]) -> list[list[int]]:
    return [
        [u, v]
        for u in range(len(adjacency))
        for v in range(u + 1, len(adjacency))
        if adjacency[u] & (1 << v)
    ]


def solve_type(
    cycle_type: list[int],
    variable: dict[tuple[int, int, int], int],
    base_clauses: list[list[int]],
    deadline: float | None,
) -> dict[str, object]:
    fixed = canonical_permutation(cycle_type)
    units = [[variable[0, source, fixed[source]]] for source in range(Q)]
    iterations = 0
    started = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=base_clauses + units) as solver:
        while deadline is None or time.monotonic() < deadline:
            if not solver.solve():
                return {
                    "cycle_type": cycle_type,
                    "status": "UNSAT",
                    "iterations": iterations,
                    "seconds": round(time.monotonic() - started, 6),
                }

            adjacency, permutations, variable_for_edge = model_to_cover(
                solver.get_model(), variable
            )
            iterations += 1
            bad_cycle: tuple[int, list[int]] | None = None
            for length in TARGET_LENGTHS:
                witness = find_simple_cycle(adjacency, length)
                if witness is not None:
                    verify_cycle(adjacency, witness, length)
                    bad_cycle = (length, witness)
                    break

            if bad_cycle is None:
                return {
                    "cycle_type": cycle_type,
                    "status": "CANDIDATE",
                    "iterations": iterations,
                    "seconds": round(time.monotonic() - started, 6),
                    "permutations": permutations,
                    "certificate": {"n": 4 * Q, "edges": edge_list(adjacency)},
                }

            _, witness = bad_cycle
            used_variables: list[int] = []
            for x, y in zip(witness, witness[1:]):
                literal = variable_for_edge.get((min(x, y), max(x, y)))
                if literal is not None and literal not in used_variables:
                    used_variables.append(literal)
            if not used_variables:
                raise AssertionError("target cycle unexpectedly uses only fixed tree edges")
            # If every variable edge of this witnessed cycle is selected, the
            # fixed tree edges complete the same cycle.  Therefore at least one
            # selected variable edge must change in every surviving model.
            solver.add_clause([-literal for literal in used_variables])

    return {
        "cycle_type": cycle_type,
        "status": "TIMEOUT",
        "iterations": iterations,
        "seconds": round(time.monotonic() - started, 6),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--seconds-per-type",
        type=float,
        default=0.0,
        help="0 (default) means no timeout; positive values are exploratory only",
    )
    parser.add_argument("--candidate-out", type=Path)
    args = parser.parse_args()

    variable, base_clauses = variables()
    cycle_types = [partition for partition in integer_partitions(Q) if partition != [1] * Q]
    cycle_types.sort(key=lambda value: (-max(value), len(value), value))
    print(
        json.dumps(
            {
                "python": platform.python_version(),
                "pysat": pysat_version,
                "solver": "cadical195",
                "q": Q,
                "target_lengths": TARGET_LENGTHS,
                "nonidentity_cycle_types": len(cycle_types),
                "random_seed": None,
            },
            sort_keys=True,
        )
    )

    results: list[dict[str, object]] = []
    for cycle_type in cycle_types:
        deadline = (
            None
            if args.seconds_per_type <= 0
            else time.monotonic() + args.seconds_per_type
        )
        result = solve_type(cycle_type, variable, base_clauses, deadline)
        results.append(result)
        print(json.dumps(result, sort_keys=True), flush=True)
        if result["status"] == "CANDIDATE":
            if args.candidate_out is not None:
                args.candidate_out.write_text(
                    json.dumps(result["certificate"], indent=2) + "\n", encoding="utf-8"
                )
            return 10

    statuses = {str(result["status"]) for result in results}
    if statuses == {"UNSAT"}:
        print(
            "All 21 nonidentity conjugacy classes are UNSAT. "
            "The identity-first case is reduced by cotree-edge symmetry: if another "
            "cotree permutation is nonidentity, move it into the first slot by an "
            "automorphism of K4 fixing the star centre; if all three are identity, "
            "the cover is eight disjoint copies of K4 and contains C4."
        )
        print("LIMITATION: no DRAT/LRAT proof was generated or checked.")
        return 0
    print(f"Incomplete statuses: {sorted(statuses)}")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
