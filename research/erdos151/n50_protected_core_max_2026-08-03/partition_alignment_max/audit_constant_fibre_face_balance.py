#!/usr/bin/env python3
"""Audit the constant-fibre face-balance lemma and its pattern reduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


HIGH_TRIANGLE = {(0, 1), (0, 2), (1, 2)}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pattern_data(record: dict[str, object]) -> tuple[int, int, bool]:
    edges = {tuple(edge) for edge in record["edges"]}  # type: ignore[arg-type]
    optional = len(edges) - 3
    forced_triangles = sum(
        tuple(sorted((left, right))) in edges
        and tuple(sorted((right, left + 3))) in edges
        for left in range(3)
        for right in range(3)
        if left != right
    )
    return optional, forced_triangles, HIGH_TRIANGLE <= edges


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orbit-audit", type=Path, required=True)
    parser.add_argument("--bounded-result", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    orbit = json.loads(args.orbit_audit.read_text(encoding="utf-8"))
    assert orbit["status"] == "PASS_EXACT_ORBIT_COVERAGE"
    assert orbit["K4_free_assignments"] == 2827
    assert orbit["S3_orbit_representatives"] == 515
    representatives = orbit["representatives"]

    # If a,b,c,d count triangles with respectively 3,2,1,0 vertices in C,
    # the three edge-face incidence equations solve to these expressions.
    symbolic = {
        "C_internal_edge_incidence": "3a+b=12+2s",
        "cross_edge_incidence": "b+c=48-2s",
        "R_internal_edge_incidence": "c+3d=12+2s",
        "solved_b": "b=12+2s-3a",
        "solved_c": "c=36-4s+3a",
        "solved_d": "d=2s-8-a",
        "necessary": ["s>=4", "a<=2s-8"],
    }
    # Direct coefficient audit of the solved identities.
    for s in range(4, 10):
        for a in range(0, 20):
            b = 12 + 2 * s - 3 * a
            c = 36 - 4 * s + 3 * a
            d = 2 * s - 8 - a
            assert 3 * a + b == 12 + 2 * s
            assert b + c == 48 - 2 * s
            assert c + 3 * d == 12 + 2 * s
            assert a + b + c + d == 40

    stages = []
    alive = list(representatives)

    def remove(name: str, predicate) -> None:
        nonlocal alive
        rejected, retained = [], []
        for record in alive:
            s, forced, high_triangle = pattern_data(record)
            (rejected if predicate(s, forced, high_triangle) else retained).append(record)
        stages.append(
            {
                "reason": name,
                "rejected_representatives": len(rejected),
                "rejected_raw_assignments": sum(record["orbit_size"] for record in rejected),
                "rejected_indices": [record["index"] for record in rejected],
            }
        )
        alive = retained

    remove("face_balance_s_at_least_4", lambda s, forced, high: s < 4)
    remove("three_high_face_union", lambda s, forced, high: high)
    remove(
        "forced_C_triangles_at_most_2s_minus_8",
        lambda s, forced, high: forced > 2 * s - 8,
    )

    assert [(stage["rejected_representatives"], stage["rejected_raw_assignments"]) for stage in stages] == [
        (61, 299),
        (35, 176),
        (40, 234),
    ]
    assert len(alive) == 379
    assert sum(record["orbit_size"] for record in alive) == 2118
    survivor_indices = {record["index"] for record in alive}

    solver_crosscheck = None
    if args.bounded_result is not None:
        bounded = json.loads(args.bounded_result.read_text(encoding="utf-8"))
        assert bounded["status"] == "INCOMPLETE_BOUNDED_SOLVE"
        records = bounded["records"]
        assert len(records) == len(representatives)
        assert {record["index"] for record in records} == {
            record["index"] for record in representatives
        }
        unsat_indices = {
            record["index"] for record in records if record["status"] == "UNSAT"
        }
        unknown_indices = {
            record["index"] for record in records if record["status"] == "UNKNOWN"
        }
        representative_by_index = {
            record["index"]: record for record in representatives
        }
        analytically_explained = unsat_indices - survivor_indices
        solver_only = unsat_indices & survivor_indices
        solver_crosscheck = {
            "path": str(args.bounded_result),
            "sha256": file_hash(args.bounded_result),
            "solver_UNSAT_representatives": len(unsat_indices),
            "solver_UNSAT_already_explained_analytically": len(analytically_explained),
            "solver_only_UNSAT_among_analytic_survivors": len(solver_only),
            "solver_only_UNSAT_indices": sorted(solver_only),
            "solver_only_UNSAT_raw_assignments": sum(
                representative_by_index[index]["orbit_size"] for index in solver_only
            ),
            "additional_solver_UNKNOWN_representatives_now_excluded_analytically": len(
                unknown_indices - survivor_indices
            ),
        }

    payload = {
        "schema": "erdos151-constant-fibre-face-balance-audit-v1",
        "status": "PASS_ANALYTIC_PATTERN_REDUCTION",
        "scope": (
            "a 21-vertex (10^3,5^18) flag RP2 block with a quotient-essential "
            "marked factor and simple crossings among its six constant fibres"
        ),
        "partition": {
            "C_vertices": 9,
            "R_vertices": 12,
            "degree_sum_C": 60,
            "degree_sum_R": 60,
            "optional_constant_fibre_adjacencies": "s",
            "edges_C": "6+s",
            "edges_R": "6+s",
            "edges_C_R": "48-2s",
        },
        "face_balance": symbolic,
        "forced_triangle_rule": (
            "for each ordered i!=j, quotient edges H_i-H_j and H_j-A_i, "
            "together with the double designated H_i-A_i adjacency, force a "
            "distinct surface triangle in C"
        ),
        "input_orbit_audit": {
            "path": str(args.orbit_audit),
            "sha256": file_hash(args.orbit_audit),
            "representatives": len(representatives),
            "raw_assignments": orbit["K4_free_assignments"],
        },
        "successive_reductions": stages,
        "surviving_representatives": len(alive),
        "surviving_raw_assignments": sum(record["orbit_size"] for record in alive),
        "survivor_edge_count_histogram": dict(
            sorted(Counter(record["edge_count"] for record in alive).items())
        ),
        "survivor_indices": sorted(survivor_indices),
        "bounded_solver_crosscheck": solver_crosscheck,
        "conclusion": (
            "The reduction is human combinatorial once the exact orbit list is "
            "accepted; it is not an exclusion of the remaining 379 representatives."
        ),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "surviving_representatives": payload["surviving_representatives"],
        "surviving_raw_assignments": payload["surviving_raw_assignments"],
        "stage_counts": [
            [stage["rejected_representatives"], stage["rejected_raw_assignments"]]
            for stage in stages
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
