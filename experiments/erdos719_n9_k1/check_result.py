#!/usr/bin/env python3
"""Standard-library graph-quantity checker for the #719 n=9 probe.

This checker shares no search code and uses no SAT/MaxSAT library.  It:

* validates the proposed 3-graph;
* enumerates every K_4^3 copy and computes the exact edge-disjoint packing
  number by set-packing recursion;
* independently certifies ex_3(9,K_4^3)=54 using exact t_7=12, two deletion
  inequalities, and checked cyclic Turan constructions at n=8 and n=9; and
* recomputes the exact minimum number e(G)-3 nu(G) of decomposition pieces.
"""

from __future__ import annotations

import argparse
import functools
import itertools
import json
import math
from pathlib import Path


def incidence(n: int):
    edges = list(itertools.combinations(range(n), 3))
    edge_id = {edge: i for i, edge in enumerate(edges)}
    four_sets = list(itertools.combinations(range(n), 4))
    four_masks = [
        sum(1 << edge_id[e] for e in itertools.combinations(vertices, 3))
        for vertices in four_sets
    ]
    return edges, edge_id, four_sets, four_masks


def exact_minimum_hitter(n: int) -> int:
    """Minimum triples meeting every 4-set, used only for n=7."""
    edges, _, _, four_masks = incidence(n)
    covers = [0] * len(edges)
    for four_id, mask in enumerate(four_masks):
        for edge_id in range(len(edges)):
            if mask >> edge_id & 1:
                covers[edge_id] |= 1 << four_id

    @functools.lru_cache(maxsize=None)
    def solve(uncovered: int) -> int:
        if not uncovered:
            return 0
        four_id = (uncovered & -uncovered).bit_length() - 1
        candidates = [i for i in range(len(edges)) if four_masks[four_id] >> i & 1]
        candidates.sort(key=lambda i: (uncovered & covers[i]).bit_count(), reverse=True)
        return 1 + min(solve(uncovered & ~covers[i]) for i in candidates)

    return solve((1 << len(four_masks)) - 1)


def cyclic_turan_edges(part_sizes: tuple[int, int, int]):
    offsets = [0, part_sizes[0], part_sizes[0] + part_sizes[1]]
    parts = [
        set(range(offsets[i], offsets[i] + part_sizes[i])) for i in range(3)
    ]
    n = sum(part_sizes)
    out = []
    allowed = {(1, 1, 1), (2, 1, 0), (0, 2, 1), (1, 0, 2)}
    for edge in itertools.combinations(range(n), 3):
        profile = tuple(len(set(edge) & part) for part in parts)
        if profile in allowed:
            out.append(edge)
    return out


def check_k4_free(n: int, selected_edges) -> None:
    chosen = set(selected_edges)
    for vertices in itertools.combinations(range(n), 4):
        if all(e in chosen for e in itertools.combinations(vertices, 3)):
            raise AssertionError(f"construction contains K_4^3 on {vertices}")


def certify_ex_3_9():
    t7 = exact_minimum_hitter(7)
    if t7 != 12:
        raise AssertionError(f"expected t_7=12, got {t7}")

    # A missing-edge hitter F on n vertices obeys
    # (n-3)|F| = sum_v |F-v| >= n*t_{n-1}.
    t8_lower = math.ceil(8 * t7 / 5)
    construction8 = cyclic_turan_edges((3, 3, 2))
    check_k4_free(8, construction8)
    t8_upper = math.comb(8, 3) - len(construction8)
    if t8_lower != 20 or t8_upper != 20:
        raise AssertionError((t8_lower, t8_upper))

    t9_lower = math.ceil(9 * t8_lower / 6)
    construction9 = cyclic_turan_edges((3, 3, 3))
    check_k4_free(9, construction9)
    t9_upper = math.comb(9, 3) - len(construction9)
    if t9_lower != 30 or t9_upper != 30:
        raise AssertionError((t9_lower, t9_upper))
    return 54, {
        "t7_exact_standard_library": t7,
        "t8_deletion_lower": t8_lower,
        "t8_checked_construction_edges": len(construction8),
        "t9_deletion_lower": t9_lower,
        "t9_checked_construction_edges": len(construction9),
        "deletion_identity": "(n-3)*t_n >= n*t_(n-1)",
    }


def exact_packing(present_masks: list[int]):
    compatible = [0] * len(present_masks)
    for i, left in enumerate(present_masks):
        for j, right in enumerate(present_masks):
            if i != j and left & right == 0:
                compatible[i] |= 1 << j

    @functools.lru_cache(maxsize=None)
    def solve(state: int) -> int:
        if not state:
            return 0
        bit = state & -state
        i = bit.bit_length() - 1
        rest = state ^ bit
        return max(solve(rest), 1 + solve(rest & compatible[i]))

    return solve((1 << len(present_masks)) - 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--json-out", type=Path, default=Path("checked.json"))
    args = parser.parse_args()
    raw = json.loads(args.result.read_text(encoding="utf-8"))
    expected_schema = "erdos719-n9-common-triple-lower-v1"
    if raw.get("schema") != expected_schema:
        raise ValueError(
            f"expected input schema {expected_schema!r}, got {raw.get('schema')!r}"
        )
    n = int(raw["n"])
    r = int(raw["r"])
    if (n, r) != (9, 3):
        raise ValueError("this independent checker is deliberately specialized to n=9,r=3")

    edges, edge_id, four_sets, four_masks = incidence(n)
    normalized = [tuple(sorted(map(int, edge))) for edge in raw["edges"]]
    if len(normalized) != len(set(normalized)):
        raise ValueError("duplicate edge")
    if any(edge not in edge_id for edge in normalized):
        raise ValueError("invalid edge")
    graph_mask = sum(1 << edge_id[edge] for edge in normalized)
    present = [
        (vertices, mask)
        for vertices, mask in zip(four_sets, four_masks)
        if mask & ~graph_mask == 0
    ]
    packing = exact_packing([mask for _, mask in present])
    packing_upper_bound = int(raw["packing_number_upper_bound"])
    if packing > packing_upper_bound:
        raise AssertionError(
            "packing_number_upper_bound: "
            f"reported {packing_upper_bound}, computed exact value {packing}"
        )
    if packing_upper_bound > 1:
        raise ValueError("this package is deliberately scoped to packing number at most one")
    ex_value, ex_certificate = certify_ex_3_9()
    parts = len(normalized) - 3 * packing
    checked = {
        "schema": "erdos719-n9-definition-check-v1",
        "status": "VERIFIED_GRAPH_QUANTITIES",
        "n": n,
        "r": r,
        "edge_count": len(normalized),
        "present_k4_3_vertex_sets": [list(vertices) for vertices, _ in present],
        "exact_edge_disjoint_packing_number": packing,
        "exact_minimum_decomposition_parts": parts,
        "exact_ex_3_9": ex_value,
        "margin_over_ex": parts - ex_value,
        "counterexample": parts > ex_value,
        "ex_certificate": ex_certificate,
    }
    for reported, computed in (
        ("maximum_edges", len(normalized)),
        ("certified_ex_3_9", ex_value),
        ("minimum_parts_if_packing_one", parts),
        ("margin_over_ex_if_packing_one", parts - ex_value),
    ):
        if reported in raw and int(raw[reported]) != computed:
            raise AssertionError(f"{reported}: reported {raw[reported]}, computed {computed}")

    rendered = json.dumps(checked, indent=2, sort_keys=True) + "\n"
    args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
