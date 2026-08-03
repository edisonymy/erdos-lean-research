#!/usr/bin/env python3
"""Audit and solve the finite six-fibre quotient-pattern decomposition.

The three mandatory quotient edges are H_i--A_i.  The other twelve edges on
the labelled vertices H_0,H_1,H_2,A_0,A_1,A_2 have 2^12 assignments.  We keep
exactly the assignments with no K4, then quotient by simultaneous permutation
of the three indexed pairs (H_i,A_i).  This symmetry preserves every labelled
constraint in ``rp2_constant_fibre_k4_sat.Encoding``; the six residual marked
K2s are fixed pointwise.

Run ``--audit-only`` first.  Solving uses bounded Glucose calls and reports
SAT, UNSAT, or UNKNOWN separately for every representative.  UNKNOWN is never
treated as evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path

from pysat.solvers import Solver

from rp2_constant_fibre_k4_sat import Encoding, FIBRES, HIGH, LEAF_PAIRS, RESIDUAL_MARKED


N_FIBRES = len(FIBRES)
ALL_PAIRS = tuple(itertools.combinations(range(N_FIBRES), 2))
MANDATORY = frozenset((index, index + 3) for index in range(3))
OPTIONAL = tuple(edge for edge in ALL_PAIRS if edge not in MANDATORY)
PERMUTATIONS = tuple(itertools.permutations(range(3)))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def has_k4(edges: frozenset[tuple[int, int]]) -> bool:
    return any(
        all(tuple(sorted(pair)) in edges for pair in itertools.combinations(four, 2))
        for four in itertools.combinations(range(N_FIBRES), 4)
    )


def bitmask(edges: frozenset[tuple[int, int]]) -> int:
    return sum(1 << index for index, edge in enumerate(ALL_PAIRS) if edge in edges)


def transform(
    edges: frozenset[tuple[int, int]], permutation: tuple[int, int, int]
) -> frozenset[tuple[int, int]]:
    def image(vertex: int) -> int:
        return permutation[vertex] if vertex < 3 else permutation[vertex - 3] + 3

    return frozenset(
        tuple(sorted((image(left), image(right)))) for left, right in edges
    )


def enumerate_patterns() -> tuple[
    list[frozenset[tuple[int, int]]],
    list[frozenset[tuple[int, int]]],
    dict[frozenset[tuple[int, int]], frozenset[tuple[int, int]]],
]:
    raw = []
    for choices in range(1 << len(OPTIONAL)):
        edges = frozenset(
            set(MANDATORY)
            | {
                edge
                for index, edge in enumerate(OPTIONAL)
                if choices & (1 << index)
            }
        )
        if not has_k4(edges):
            raw.append(edges)

    raw_set = set(raw)
    canonical = {
        edges: min(
            (transform(edges, permutation) for permutation in PERMUTATIONS),
            key=bitmask,
        )
        for edges in raw
    }
    representatives = sorted(set(canonical.values()), key=lambda e: (len(e), bitmask(e)))

    # Exact coverage and closure audit, independent of any SAT call.
    assert len(OPTIONAL) == 12
    assert len(raw) == len(raw_set) == 2827
    assert len(representatives) == 515
    assert all(MANDATORY <= edges and not has_k4(edges) for edges in raw)
    assert all(
        transform(edges, permutation) in raw_set
        for edges in raw
        for permutation in PERMUTATIONS
    )
    covered = set()
    for representative in representatives:
        orbit = {transform(representative, permutation) for permutation in PERMUTATIONS}
        assert representative == min(orbit, key=bitmask)
        assert not (covered & orbit)
        covered |= orbit
    assert covered == raw_set
    assert all(canonical[edges] in representatives for edges in raw)
    return raw, representatives, canonical


def symmetry_schema_audit() -> dict[str, object]:
    """Check that the S3 action preserves the non-auxiliary constraint data."""

    residual = frozenset(frozenset(edge) for edge in RESIDUAL_MARKED)
    records = []
    for permutation in PERMUTATIONS:
        vertex_map = {vertex: vertex for vertex in range(21)}
        for index in range(3):
            vertex_map[index] = permutation[index]
            source_pair = LEAF_PAIRS[index]
            target_pair = LEAF_PAIRS[permutation[index]]
            vertex_map[source_pair[0]] = target_pair[0]
            vertex_map[source_pair[1]] = target_pair[1]
        mapped_high = {vertex_map[vertex] for vertex in HIGH}
        mapped_leaf_pairs = {
            frozenset(vertex_map[vertex] for vertex in pair) for pair in LEAF_PAIRS
        }
        mapped_residual = {
            frozenset(vertex_map[vertex] for vertex in edge) for edge in RESIDUAL_MARKED
        }
        assert mapped_high == set(HIGH)
        assert mapped_leaf_pairs == {frozenset(pair) for pair in LEAF_PAIRS}
        assert mapped_residual == residual
        assert len(set(vertex_map.values())) == 21
        records.append(
            {
                "index_permutation": list(permutation),
                "vertex_permutation": [vertex_map[index] for index in range(21)],
            }
        )
    return {
        "group_order": len(PERMUTATIONS),
        "preserves_degree_classes": True,
        "preserves_marked_P3_family_with_leaf_orientation": True,
        "fixes_residual_marked_K2s_pointwise": True,
        "actions": records,
    }


def coverage_payload() -> tuple[dict[str, object], list[frozenset[tuple[int, int]]]]:
    raw, representatives, canonical = enumerate_patterns()
    orbit_sizes = Counter()
    for representative in representatives:
        orbit_sizes[len({transform(representative, p) for p in PERMUTATIONS})] += 1
    payload = {
        "schema": "erdos151-rp2-constant-fibre-pattern-orbits-v1",
        "status": "PASS_EXACT_ORBIT_COVERAGE",
        "six_fibres": [list(fibre) for fibre in FIBRES],
        "all_pair_count": len(ALL_PAIRS),
        "mandatory_pairs": [list(edge) for edge in sorted(MANDATORY)],
        "optional_pair_count": len(OPTIONAL),
        "all_optional_assignments": 1 << len(OPTIONAL),
        "K4_free_assignments": len(raw),
        "S3_orbit_representatives": len(representatives),
        "orbit_size_histogram": dict(sorted(orbit_sizes.items())),
        "edge_count_histogram_raw": dict(sorted(Counter(map(len, raw)).items())),
        "edge_count_histogram_representatives": dict(
            sorted(Counter(map(len, representatives)).items())
        ),
        "canonical_map_entries": len(canonical),
        "union_of_representative_orbits_equals_raw_set": True,
        "symmetry_schema_audit": symmetry_schema_audit(),
        "representatives": [
            {
                "index": index,
                "bitmask_on_all_15_pairs": bitmask(edges),
                "edge_count": len(edges),
                "edges": [list(edge) for edge in sorted(edges)],
                "orbit_size": len({transform(edges, p) for p in PERMUTATIONS}),
            }
            for index, edges in enumerate(representatives)
        ],
    }
    return payload, representatives


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cnf", type=Path)
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--solver", default="glucose42", choices=("glucose42", "minisat22"))
    parser.add_argument("--conflict-budget", type=int, default=25_000)
    args = parser.parse_args()
    if not args.audit_only and args.cnf is None:
        parser.error("--cnf is required unless --audit-only is used")
    if args.conflict_budget <= 0:
        parser.error("--conflict-budget must be positive")

    started = time.time()
    payload, representatives = coverage_payload()
    payload["audit_only"] = args.audit_only
    payload["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.audit_only:
        payload["elapsed_seconds"] = time.time() - started
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(json.dumps({key: payload[key] for key in (
            "status", "K4_free_assignments", "S3_orbit_representatives", "orbit_size_histogram"
        )}, sort_keys=True))
        return

    encoding = Encoding(forbid_constant_k4=False)
    assert args.cnf is not None
    encoding.cnf.to_file(args.cnf)
    records = []
    first_model = None
    with Solver(name=args.solver, bootstrap_with=encoding.cnf) as solver:
        prior_conflicts = 0
        for index, edges in enumerate(representatives):
            assumptions = [
                encoding.quotient_edge(*pair)
                if pair in edges
                else -encoding.quotient_edge(*pair)
                for pair in ALL_PAIRS
            ]
            assert len(assumptions) == len(set(map(abs, assumptions))) == 15
            solver.conf_budget(args.conflict_budget)
            branch_started = time.time()
            answer = solver.solve_limited(assumptions=assumptions)
            stats = solver.accum_stats()
            conflicts = int(stats.get("conflicts", 0))
            record = {
                "index": index,
                "bitmask_on_all_15_pairs": bitmask(edges),
                "edge_count": len(edges),
                "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
                "elapsed_seconds": time.time() - branch_started,
                "incremental_conflicts": conflicts - prior_conflicts,
            }
            prior_conflicts = conflicts
            records.append(record)
            if answer is True:
                model = solver.get_model()
                assert model is not None
                first_model = encoding.audit_model(model)
                assert not first_model["constant_fibre_K4s"]
                record["model_graph6"] = first_model["graph6"]
                break

    counts = Counter(record["status"] for record in records)
    payload.update(
        {
            "status": (
                "SAT_COUNTERCONFIGURATION"
                if counts["SAT"]
                else "PASS_ALL_REPRESENTATIVES_UNSAT"
                if len(records) == len(representatives) and counts["UNSAT"] == len(representatives)
                else "INCOMPLETE_BOUNDED_SOLVE"
            ),
            "solver": args.solver,
            "conflict_budget_per_representative": args.conflict_budget,
            "base_cnf": {
                "path": str(args.cnf),
                "variables": encoding.pool.top,
                "clauses": len(encoding.cnf.clauses),
                "sha256": digest(args.cnf),
                "note": "the fifteen K4 clauses are replaced by complete pattern assumptions",
            },
            "solved_representative_count": counts["SAT"] + counts["UNSAT"],
            "solve_status_counts": dict(sorted(counts.items())),
            "representative_solve_records": records,
            "first_model": first_model,
            "elapsed_seconds": time.time() - started,
            "claim_boundary": (
                "UNKNOWN branches are no evidence. Complete representative UNSAT is a "
                "coverage-audited computational exclusion only until every relevant "
                "UNSAT result receives an independently checked proof certificate."
            ),
        }
    )
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": payload["status"],
        "solve_status_counts": payload["solve_status_counts"],
        "solved_representative_count": payload["solved_representative_count"],
        "elapsed_seconds": payload["elapsed_seconds"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
