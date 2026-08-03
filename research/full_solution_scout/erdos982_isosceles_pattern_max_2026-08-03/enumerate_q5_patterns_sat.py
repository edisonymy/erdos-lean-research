#!/usr/bin/env python3
"""Boolean-SAT version of the convex-decagon q=5 pattern enumerator.

The mathematical constraints are identical to enumerate_q5_patterns.py, but
edge-colour and missing-colour variables are encoded one-hot in CNF.  This is
the production enumerator; the Z3 implementation is retained as an independent
small-instance/model cross-check.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import threading
import time
from pathlib import Path

from pysat.solvers import Solver

from enumerate_q5_patterns import (
    EDGES,
    N,
    Q,
    VERTICES,
    canonical_dihedral,
    crosses,
    cyclic_side,
    edge,
)


class Variables:
    def __init__(self) -> None:
        self.next = 1
        self.edge_colour: dict[tuple[tuple[int, int], int], int] = {}
        self.missing: dict[tuple[int, int], int] = {}
        for e in EDGES:
            for c in range(Q):
                self.edge_colour[e, c] = self._new()
        for v in VERTICES:
            for c in range(Q):
                self.missing[v, c] = self._new()

    def _new(self) -> int:
        value = self.next
        self.next += 1
        return value

    def x(self, a: int, b: int, c: int) -> int:
        return self.edge_colour[edge(a, b), c]


def exactly_one(variables: list[int]) -> list[list[int]]:
    return [variables] + [[-a, -b] for a, b in itertools.combinations(variables, 2)]


def build_cnf(
    shortest: int,
    longest: int,
    order4: tuple[int, ...],
    exactly_four_local: bool,
):
    var = Variables()
    clauses: list[list[int]] = []

    # Every edge has exactly one global distance colour.
    for e in EDGES:
        clauses.extend(exactly_one([var.edge_colour[e, c] for c in range(Q)]))
    for c in range(Q):
        clauses.append([var.edge_colour[e, c] for e in EDGES])

    # At every vertex at least one of the five global colours is absent.  The
    # optional exactly-four restriction is only a diagnostic sub-branch; it is
    # not lossless for the original locally-at-most-four condition.
    for v in VERTICES:
        missing_here = [var.missing[v, c] for c in range(Q)]
        if exactly_four_local:
            clauses.extend(exactly_one(missing_here))
        else:
            clauses.append(missing_here)
        for c in range(Q):
            incident = [var.x(v, w, c) for w in VERTICES if w != v]
            for x in incident:
                clauses.append([-var.missing[v, c], -x])
            clauses.append([var.missing[v, c]] + incident)

    # Fixed five-cap endpoint colour orders.  The global colour labels are
    # broken by c(01),c(02),c(03),c(04) = 0,1,2,3.
    for j, c in zip((1, 2, 3, 4), (0, 1, 2, 3)):
        clauses.append([var.x(0, j, c)])
    for j, c in zip((3, 2, 1, 0), order4):
        clauses.append([var.x(4, j, c)])

    # At most one equal-distance witness on each cyclic side of a base.
    for base in EDGES:
        others = [v for v in VERTICES if v not in base]
        for side in (0, 1):
            apices = [v for v in others if cyclic_side(base, v) == side]
            for p, q in itertools.combinations(apices, 2):
                for c in range(Q):
                    for d in range(Q):
                        clauses.append([
                            -var.x(p, base[0], c),
                            -var.x(p, base[1], c),
                            -var.x(q, base[0], d),
                            -var.x(q, base[1], d),
                        ])

    # No monochromatic K4.
    for quad in itertools.combinations(VERTICES, 4):
        qedges = list(itertools.combinations(quad, 2))
        for c in range(Q):
            clauses.append([-var.edge_colour[e, c] for e in qedges])

    # Shortest edges cannot cross; disjoint diameter edges must cross.
    for e, f in itertools.combinations(EDGES, 2):
        if crosses(e, f):
            clauses.append([-var.edge_colour[e, shortest], -var.edge_colour[f, shortest]])
        elif len(set(e + f)) == 4:
            clauses.append([-var.edge_colour[e, longest], -var.edge_colour[f, longest]])

    return var, clauses


def decode_model(model: list[int], var: Variables, shortest: int, longest: int, order4: tuple[int, ...]):
    positive = set(x for x in model if x > 0)
    colours = tuple(
        next(c for c in range(Q) if var.edge_colour[e, c] in positive)
        for e in EDGES
    )
    edge_counts = [colours.count(c) for c in range(Q)]
    degrees = []
    for c in range(Q):
        degrees.append([
            sum(colours[EDGES.index(edge(v, w))] == c for w in VERTICES if w != v)
            for v in VERTICES
        ])
    return {
        "edge_colours": list(colours),
        "canonical_dihedral": list(canonical_dihedral(colours)),
        "edge_counts": edge_counts,
        "support_sizes": [sum(d > 0 for d in row) for row in degrees],
        "degree_profiles": [sorted((d for d in row if d), reverse=True) for row in degrees],
        "shortest_colour": shortest,
        "longest_colour": longest,
        "cap_order_at_0": [0, 1, 2, 3],
        "cap_order_at_4": list(order4),
    }


def admissible_cases():
    order0 = (0, 1, 2, 3)
    for prefix in itertools.permutations((0, 1, 2, 4), 3):
        order4 = prefix + (3,)
        for shortest in range(Q):
            for longest in range(Q):
                if shortest == longest:
                    continue
                if shortest in order0 and order0.index(shortest) != 0:
                    continue
                if longest in order0 and order0.index(longest) != 3:
                    continue
                if shortest in order4 and order4.index(shortest) != 0:
                    continue
                if longest in order4 and order4.index(longest) != 3:
                    continue
                has_total_order = False
                for total in itertools.permutations(range(Q)):
                    if total[0] != shortest or total[-1] != longest:
                        continue
                    rank = {c: i for i, c in enumerate(total)}
                    if all(rank[a] < rank[b] for a, b in zip(order0, order0[1:])) and all(
                        rank[a] < rank[b] for a, b in zip(order4, order4[1:])
                    ):
                        has_total_order = True
                        break
                if not has_total_order:
                    continue
                yield shortest, longest, order4


def run(
    max_models: int,
    per_case: int,
    conflict_budget: int,
    wall_seconds_per_solve: float,
    exactly_four_local: bool,
    seconds: float,
    retain: int,
    solver_name: str,
) -> dict:
    started = time.monotonic()
    raw = 0
    cases = 0
    sat_cases = 0
    unknown_cases = 0
    seen = set()
    records = []
    status = "BOUNDED_CASE_SWEEP_COMPLETE"
    clause_counts = []
    case_summaries = []

    for shortest, longest, order4 in admissible_cases():
        if time.monotonic() - started >= seconds:
            status = "TIME_CAP"
            break
        cases += 1
        var, clauses = build_cnf(shortest, longest, order4, exactly_four_local)
        clause_counts.append(len(clauses))
        case_had_model = False
        case_models = 0
        terminal = "SAMPLE_CAP"
        with Solver(name=solver_name, bootstrap_with=clauses) as solver:
            while (
                raw < max_models
                and case_models < per_case
                and time.monotonic() - started < seconds
            ):
                solver.conf_budget(conflict_budget)
                timer = threading.Timer(wall_seconds_per_solve, solver.interrupt)
                timer.daemon = True
                timer.start()
                try:
                    solve_status = solver.solve_limited(expect_interrupt=True)
                finally:
                    timer.cancel()
                    try:
                        solver.clear_interrupt()
                    except NotImplementedError:
                        pass
                if solve_status is None:
                    unknown_cases += 1
                    terminal = "UNKNOWN_AFTER_MODELS" if case_models else "UNKNOWN_NO_MODEL"
                    break
                if not solve_status:
                    terminal = "UNSAT_AFTER_MODELS" if case_models else "PROVED_UNSAT_NO_MODEL"
                    break
                case_had_model = True
                model = solver.get_model()
                record = decode_model(model, var, shortest, longest, order4)
                raw += 1
                case_models += 1
                key = tuple(record["canonical_dihedral"])
                if key not in seen:
                    seen.add(key)
                    if len(records) < retain:
                        records.append(record)
                solver.add_clause([
                    -var.edge_colour[e, int(c)] for e, c in zip(EDGES, record["edge_colours"])
                ])
        if case_had_model:
            sat_cases += 1
        case_summaries.append({
            "shortest_colour": shortest,
            "longest_colour": longest,
            "cap_order_at_4": list(order4),
            "models_sampled": case_models,
            "terminal": terminal,
        })
        if raw >= max_models:
            status = "MODEL_CAP"
            break
        if time.monotonic() - started >= seconds:
            status = "TIME_CAP"
            break

    return {
        "status": status,
        "n": N,
        "global_distance_colours": Q,
        "raw_models": raw,
        "dihedral_colour_orbits_seen": len(seen),
        "cases_started": cases,
        "cases_with_model": sat_cases,
        "cases_terminated_unknown": unknown_cases,
        "cases_proved_unsat_without_model": sum(c["terminal"] == "PROVED_UNSAT_NO_MODEL" for c in case_summaries),
        "cases_sampled_sat": sum(c["models_sampled"] > 0 for c in case_summaries),
        "elapsed_seconds": time.monotonic() - started,
        "solver": solver_name,
        "variable_count": Variables().next - 1,
        "clause_count_range": [min(clause_counts), max(clause_counts)] if clause_counts else None,
        "max_models": max_models,
        "per_case": per_case,
        "conflict_budget_per_solve": conflict_budget,
        "wall_seconds_per_solve": wall_seconds_per_solve,
        "exactly_four_local_diagnostic_restriction": exactly_four_local,
        "seconds": seconds,
        "retained": records,
        "case_summaries": case_summaries,
        "scope": "necessary global-five-distance colour patterns with cap, witness-side, shortest and diameter constraints; not Euclidean realizability",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-models", type=int, default=10000)
    parser.add_argument("--per-case", type=int, default=20)
    parser.add_argument("--conflict-budget", type=int, default=100000)
    parser.add_argument("--wall-seconds-per-solve", type=float, default=5.0)
    parser.add_argument("--exactly-four-local", action="store_true")
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--retain", type=int, default=1000)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("q5_patterns_sat.json"))
    args = parser.parse_args()
    payload = run(
        args.max_models,
        args.per_case,
        args.conflict_budget,
        args.wall_seconds_per_solve,
        args.exactly_four_local,
        args.seconds,
        args.retain,
        args.solver,
    )
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "retained"}, sort_keys=True))
    print("sha256", hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
