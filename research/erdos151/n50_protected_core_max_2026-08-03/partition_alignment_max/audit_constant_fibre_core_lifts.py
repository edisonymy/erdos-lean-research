#!/usr/bin/env python3
"""Exhaust the nine-vertex endpoint lifts of constant-fibre patterns.

This is deliberately a local necessary-condition audit, not a surface
constructor.  Every full quotient-essential RP2 block induces one of the
enumerated endpoint lifts, so a pattern with no surviving lift is impossible.
Patterns with a surviving lift are merely unresolved.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


N = 9
HIGH = (0, 1, 2)
LEAF_PAIRS = ((3, 4), (5, 6), (7, 8))
MANDATORY_FIBRE_EDGES = {(0, 3), (1, 4), (2, 5)}
EDGE_ORDER = tuple(itertools.combinations(range(N), 2))
EDGE_INDEX = {edge: index for index, edge in enumerate(EDGE_ORDER)}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_edge(adjacency: list[int], left: int, right: int) -> None:
    adjacency[left] |= 1 << right
    adjacency[right] |= 1 << left


def has_edge(adjacency: list[int], left: int, right: int) -> bool:
    return bool(adjacency[left] & (1 << right))


def core_code(adjacency: list[int]) -> int:
    return sum(
        1 << EDGE_INDEX[(left, right)]
        for left, right in EDGE_ORDER
        if has_edge(adjacency, left, right)
    )


def triangle_count(adjacency: list[int]) -> int:
    return sum(
        has_edge(adjacency, left, middle)
        and has_edge(adjacency, left, right)
        and has_edge(adjacency, middle, right)
        for left, middle, right in itertools.combinations(range(N), 3)
    )


def has_K4(adjacency: list[int]) -> bool:
    return any(
        all(has_edge(adjacency, left, right) for left, right in itertools.combinations(four, 2))
        for four in itertools.combinations(range(N), 4)
    )


def edge_codegree_upper_ok(adjacency: list[int]) -> bool:
    return all(
        (adjacency[left] & adjacency[right]).bit_count() <= 2
        for left, right in EDGE_ORDER
        if has_edge(adjacency, left, right)
    )


def positions_realize_induced_cycle(
    adjacency: list[int], neighbours: list[int], positions: dict[int, int], length: int
) -> bool:
    return all(
        has_edge(adjacency, left, right)
        == ((positions[left] - positions[right]) % length in (1, length - 1))
        for left, right in itertools.combinations(neighbours, 2)
    )


def partial_link_embeds(adjacency: list[int], vertex: int) -> bool:
    neighbours = [other for other in range(N) if has_edge(adjacency, vertex, other)]
    length = 10 if vertex in HIGH else 5
    if len(neighbours) > length:
        return False

    if vertex in HIGH:
        first, opposite = LEAF_PAIRS[vertex]
        assert first in neighbours and opposite in neighbours
        others = [item for item in neighbours if item not in (first, opposite)]
        for selected in itertools.permutations(
            [position for position in range(length) if position not in (0, 5)],
            len(others),
        ):
            positions = {first: 0, opposite: 5, **dict(zip(others, selected))}
            if positions_realize_induced_cycle(adjacency, neighbours, positions, length):
                return True
        return False

    if not neighbours:
        return True
    # Rotation lets the least labelled known neighbour be fixed at position 0.
    anchor = min(neighbours)
    others = [item for item in neighbours if item != anchor]
    for selected in itertools.permutations(range(1, length), len(others)):
        positions = {anchor: 0, **dict(zip(others, selected))}
        if positions_realize_induced_cycle(adjacency, neighbours, positions, length):
            return True
    return False


def all_partial_links_embed(adjacency: list[int]) -> bool:
    return all(partial_link_embeds(adjacency, vertex) for vertex in range(N))


def face_balance_ok(adjacency: list[int], optional_edges: int) -> bool:
    a = triangle_count(adjacency)
    b = 12 + 2 * optional_edges - 3 * a
    c = 36 - 4 * optional_edges + 3 * a
    d = 2 * optional_edges - 8 - a
    return min(a, b, c, d) >= 0 and a + b + c + d == 40


def lift_choices(quotient_edges: set[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    choices = []
    for left, right in sorted(quotient_edges - MANDATORY_FIBRE_EDGES):
        if right < 3:
            choices.append([(left, right)])
        elif left < 3:
            choices.append([(left, leaf) for leaf in LEAF_PAIRS[right - 3]])
        else:
            choices.append(
                [
                    (left_leaf, right_leaf)
                    for left_leaf in LEAF_PAIRS[left - 3]
                    for right_leaf in LEAF_PAIRS[right - 3]
                ]
            )
    return choices


def build_core(selected_edges: tuple[tuple[int, int], ...]) -> list[int]:
    adjacency = [0] * N
    for center, leaves in zip(HIGH, LEAF_PAIRS):
        add_edge(adjacency, center, leaves[0])
        add_edge(adjacency, center, leaves[1])
    for edge in selected_edges:
        add_edge(adjacency, *edge)
    return adjacency


def classify_core(adjacency: list[int], optional_edges: int) -> str:
    if has_K4(adjacency):
        return "surface_K4"
    if not edge_codegree_upper_ok(adjacency):
        return "internal_edge_codegree_gt_2"
    if not face_balance_ok(adjacency, optional_edges):
        return "face_balance"
    if not all_partial_links_embed(adjacency):
        return "partial_link_nonembeddable"
    return "PASS_NECESSARY_LOCAL_CHECKS"


def audit_control(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["satisfiable"]
    adjacency = [0] * N
    for left, right in payload["model"]["edges"]:
        if left < N and right < N:
            add_edge(adjacency, left, right)
    multiplicities = payload["model"]["constant_fibre_multiplicity"]
    optional = sum(
        value > 0
        for key, value in multiplicities.items()
        if key not in {"0-3", "1-4", "2-5"}
    )
    status = classify_core(adjacency, optional)
    assert status == "PASS_NECESSARY_LOCAL_CHECKS"
    return {
        "path": str(path),
        "sha256": digest(path),
        "optional_quotient_edges": optional,
        "surface_C_edges": sum(row.bit_count() for row in adjacency) // 2,
        "surface_C_triangles": triangle_count(adjacency),
        "core_code": core_code(adjacency),
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orbit-audit", type=Path, required=True)
    parser.add_argument("--analytic-audit", type=Path, required=True)
    parser.add_argument("--control-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    orbit = json.loads(args.orbit_audit.read_text(encoding="utf-8"))
    analytic = json.loads(args.analytic_audit.read_text(encoding="utf-8"))
    assert orbit["status"] == "PASS_EXACT_ORBIT_COVERAGE"
    assert analytic["status"] == "PASS_ANALYTIC_PATTERN_REDUCTION"
    survivor_indices = set(analytic["survivor_indices"])
    representatives = {
        record["index"]: record for record in orbit["representatives"]
    }
    assert len(survivor_indices) == 379

    records = []
    total_lifts = 0
    total_passing_lifts = 0
    excluded_indices = set()
    global_reasons: Counter[str] = Counter()
    for index in sorted(survivor_indices):
        representative = representatives[index]
        quotient_edges = {tuple(edge) for edge in representative["edges"]}
        optional = len(quotient_edges) - 3
        choices = lift_choices(quotient_edges)
        expected = 1
        for alternatives in choices:
            expected *= len(alternatives)
        reasons: Counter[str] = Counter()
        passing_codes = []
        seen_codes = set()
        for selected in itertools.product(*choices):
            adjacency = build_core(selected)
            code = core_code(adjacency)
            assert code not in seen_codes
            seen_codes.add(code)
            reason = classify_core(adjacency, optional)
            reasons[reason] += 1
            global_reasons[reason] += 1
            if reason == "PASS_NECESSARY_LOCAL_CHECKS":
                passing_codes.append(code)
        assert len(seen_codes) == expected
        total_lifts += expected
        total_passing_lifts += len(passing_codes)
        if not passing_codes:
            excluded_indices.add(index)
        records.append(
            {
                "index": index,
                "quotient_edge_count": len(quotient_edges),
                "optional_edge_count": optional,
                "orbit_size": representative["orbit_size"],
                "endpoint_lift_count": expected,
                "reason_counts": dict(sorted(reasons.items())),
                "passing_lift_count": len(passing_codes),
                "first_passing_core_codes": passing_codes[:5],
            }
        )

    surviving_indices = survivor_indices - excluded_indices
    excluded_raw = sum(representatives[index]["orbit_size"] for index in excluded_indices)
    surviving_raw = sum(representatives[index]["orbit_size"] for index in surviving_indices)
    assert excluded_raw + surviving_raw == analytic["surviving_raw_assignments"]
    assert total_lifts == 37852

    payload = {
        "schema": "erdos151-constant-fibre-core-lifts-v1",
        "status": "PASS_EXHAUSTIVE_LOCAL_LIFT_FILTER",
        "scope": (
            "endpoint lifts of the 379 analytically surviving six-fibre patterns "
            "into their nine actual surface vertices; necessary local conditions only"
        ),
        "soundness_boundary": (
            "Every full quotient-essential block induces one enumerated lift. Zero "
            "passing lifts excludes a quotient pattern; a passing lift is not a full surface."
        ),
        "checks": [
            "ambient K4-free on C",
            "at most two common C-neighbours on every present C-edge",
            "exact C/R face-balance nonnegativity",
            "each partial C-link embeds inducedly in C10 or C5",
            "the marked leaves occupy antipodal C10 positions",
        ],
        "positive_control": audit_control(args.control_result),
        "inputs": {
            "orbit_audit": {"path": str(args.orbit_audit), "sha256": digest(args.orbit_audit)},
            "analytic_audit": {"path": str(args.analytic_audit), "sha256": digest(args.analytic_audit)},
        },
        "input_representatives": len(survivor_indices),
        "input_raw_assignments": analytic["surviving_raw_assignments"],
        "endpoint_lifts_exhausted": total_lifts,
        "endpoint_lift_reason_counts": dict(sorted(global_reasons.items())),
        "passing_endpoint_lifts": total_passing_lifts,
        "excluded_representatives": len(excluded_indices),
        "excluded_raw_assignments": excluded_raw,
        "surviving_representatives": len(surviving_indices),
        "surviving_raw_assignments": surviving_raw,
        "excluded_indices": sorted(excluded_indices),
        "surviving_indices": sorted(surviving_indices),
        "records": records,
        "claim_boundary": (
            "This is a solver-free exhaustive finite filter of local cores, not a "
            "human classification and not an exclusion of any surviving pattern."
        ),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        key: payload[key]
        for key in (
            "status",
            "endpoint_lifts_exhausted",
            "passing_endpoint_lifts",
            "excluded_representatives",
            "excluded_raw_assignments",
            "surviving_representatives",
            "surviving_raw_assignments",
        )
    }, sort_keys=True))


if __name__ == "__main__":
    main()
