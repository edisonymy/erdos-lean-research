#!/usr/bin/env python3
"""Self-contained finite certificate for ex_3(9, K_4^(3)) = 54.

Only the Python standard library is used.  The lower bound on the complementary
four-set hitting number starts from an exhaustive t_7 recurrence; deletion
inequalities propagate it to n=8,9; explicit checked cyclic constructions meet
both propagated bounds.
"""

from __future__ import annotations

import argparse
import functools
import itertools
import json
import math
from pathlib import Path


SCHEMA = "ex3-9-k4-3-self-contained-certificate-v1"


def triples(n: int) -> list[tuple[int, int, int]]:
    return list(itertools.combinations(range(n), 3))


def four_sets(n: int) -> list[tuple[int, int, int, int]]:
    return list(itertools.combinations(range(n), 4))


def exact_t7_certificate() -> dict:
    n = 7
    edge_list = triples(n)
    edge_id = {edge: index for index, edge in enumerate(edge_list)}
    quads = four_sets(n)
    quad_masks = [
        sum(1 << edge_id[edge] for edge in itertools.combinations(quad, 3))
        for quad in quads
    ]
    covers = [0] * len(edge_list)
    for quad_id, quad_mask in enumerate(quad_masks):
        for candidate_edge_id in range(len(edge_list)):
            if quad_mask >> candidate_edge_id & 1:
                covers[candidate_edge_id] |= 1 << quad_id

    @functools.lru_cache(maxsize=None)
    def solve(uncovered_quad_mask: int) -> int:
        if not uncovered_quad_mask:
            return 0
        first_quad_id = (uncovered_quad_mask & -uncovered_quad_mask).bit_length() - 1
        candidates = [
            candidate_edge_id
            for candidate_edge_id in range(len(edge_list))
            if quad_masks[first_quad_id] >> candidate_edge_id & 1
        ]
        candidates.sort(
            key=lambda candidate_edge_id: (
                -(uncovered_quad_mask & covers[candidate_edge_id]).bit_count(),
                candidate_edge_id,
            )
        )
        return 1 + min(
            solve(uncovered_quad_mask & ~covers[candidate_edge_id])
            for candidate_edge_id in candidates
        )

    root = (1 << len(quads)) - 1
    optimum = solve(root)
    witness_ids: list[int] = []
    state = root
    while state:
        target = solve(state) - 1
        first_quad_id = (state & -state).bit_length() - 1
        candidates = [
            candidate_edge_id
            for candidate_edge_id in range(len(edge_list))
            if quad_masks[first_quad_id] >> candidate_edge_id & 1
        ]
        candidates.sort(
            key=lambda candidate_edge_id: (
                -(state & covers[candidate_edge_id]).bit_count(),
                candidate_edge_id,
            )
        )
        chosen = next(
            candidate_edge_id
            for candidate_edge_id in candidates
            if solve(state & ~covers[candidate_edge_id]) == target
        )
        witness_ids.append(chosen)
        state &= ~covers[chosen]

    if optimum != 12 or len(witness_ids) != 12:
        raise AssertionError((optimum, witness_ids))
    witness = [edge_list[index] for index in witness_ids]
    if any(
        not any(set(edge) <= set(quad) for edge in witness)
        for quad in quads
    ):
        raise AssertionError("reconstructed t_7 witness misses a 4-set")
    cache = solve.cache_info()
    return {
        "n": n,
        "triple_count": len(edge_list),
        "four_set_count": len(quads),
        "exact_minimum_hitter": optimum,
        "explicit_optimal_hitter": [list(edge) for edge in witness],
        "memoized_states_evaluated": cache.misses,
        "recurrence": (
            "Choose the lexicographically first uncovered 4-set and take 1 + "
            "the minimum over its four triples; every hitting completion must "
            "take at least one branch triple."
        ),
    }


def cyclic_construction(part_sizes: tuple[int, int, int]) -> dict:
    offsets = [0, part_sizes[0], part_sizes[0] + part_sizes[1]]
    parts = [
        set(range(offsets[index], offsets[index] + part_sizes[index]))
        for index in range(3)
    ]
    n = sum(part_sizes)
    allowed_profiles = {(1, 1, 1), (2, 1, 0), (0, 2, 1), (1, 0, 2)}
    selected = []
    for edge in triples(n):
        profile = tuple(len(set(edge) & part) for part in parts)
        if profile in allowed_profiles:
            selected.append(edge)
    selected_set = set(selected)
    violating_four_sets = [
        quad
        for quad in four_sets(n)
        if all(edge in selected_set for edge in itertools.combinations(quad, 3))
    ]
    if violating_four_sets:
        raise AssertionError(f"construction contains K_4^3: {violating_four_sets}")
    missing = [edge for edge in triples(n) if edge not in selected_set]
    if any(
        not any(set(edge) <= set(quad) for edge in missing)
        for quad in four_sets(n)
    ):
        raise AssertionError("complement is not a four-set hitter")
    return {
        "part_sizes": list(part_sizes),
        "allowed_profiles": [
            list(profile)
            for profile in sorted(allowed_profiles)
        ],
        "k4_3_free": True,
        "selected_edge_count": len(selected),
        "selected_edges": [list(edge) for edge in selected],
        "missing_hitter_count": len(missing),
        "missing_hitter_triples": [list(edge) for edge in missing],
        "checked_four_set_count": math.comb(n, 4),
    }


def build_certificate() -> dict:
    t7 = exact_t7_certificate()
    construction8 = cyclic_construction((3, 3, 2))
    construction9 = cyclic_construction((3, 3, 3))
    t8_lower = math.ceil(8 * t7["exact_minimum_hitter"] / 5)
    t9_lower = math.ceil(9 * t8_lower / 6)
    if (
        t8_lower,
        construction8["missing_hitter_count"],
        t9_lower,
        construction9["missing_hitter_count"],
    ) != (20, 20, 30, 30):
        raise AssertionError("deletion bounds do not meet constructions")
    return {
        "schema": SCHEMA,
        "claim": "ex_3(9, K_4^(3)) = 54",
        "claim_scope": "finite n=9 extremal value only",
        "complement_identity": "ex_3(n,K_4^(3)) = C(n,3) - t_n",
        "deletion_identity": "(n-3) t_n >= n t_(n-1)",
        "t7_exhaustive_base": t7,
        "n8": {
            "deletion_lower_bound_on_t8": t8_lower,
            "construction": construction8,
            "exact_t8": 20,
        },
        "n9": {
            "deletion_lower_bound_on_t9": t9_lower,
            "construction": construction9,
            "exact_t9": 30,
            "total_triples": math.comb(9, 3),
            "exact_ex_3_9": math.comb(9, 3) - 30,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args()
    certificate = build_certificate()
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")


if __name__ == "__main__":
    main()
