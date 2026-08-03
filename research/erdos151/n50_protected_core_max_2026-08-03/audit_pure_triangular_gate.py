#!/usr/bin/env python3
"""Arithmetic audit for the order-50 pure-triangular chromatic gate."""

from __future__ import annotations

import json
import math
from pathlib import Path


def matching_bound(n: int, beta_upper: int) -> dict[str, int]:
    q = 3 * math.ceil((beta_upper + 1) / 4)
    packing_upper = beta_upper + (q - 2) * (beta_upper // 2)
    lower = math.ceil((n - packing_upper) / 2)
    return {
        "n": n,
        "beta_upper": beta_upper,
        "q": q,
        "P_q": packing_upper,
        "maximal_edge_matching_lower": lower,
    }


def main() -> None:
    n, h, beta_upper = 50, 11, 10
    q = 3 * math.ceil(h / 4)
    two_class_lower = math.ceil(2 * n / q)
    maximal_edge_cover_lower = two_class_lower - beta_upper
    assumed_matching_upper = 2
    matching_cover_upper = 2 * assumed_matching_upper
    outside_cover_lower = n - matching_cover_upper
    sorted_class_second_upper = beta_upper // 2
    outside_cover_upper = beta_upper + 7 * sorted_class_second_upper
    assert q == 9
    assert two_class_lower == 12
    assert two_class_lower > beta_upper
    assert maximal_edge_cover_lower == 2
    assert matching_cover_upper == 4
    assert outside_cover_lower == 46
    assert outside_cover_upper == 45
    assert outside_cover_lower > outside_cover_upper
    example_50 = matching_bound(50, 10)
    example_59 = matching_bound(59, 11)
    assert example_50 == {
        "n": 50,
        "beta_upper": 10,
        "q": 9,
        "P_q": 45,
        "maximal_edge_matching_lower": 3,
    }
    assert example_59 == {
        "n": 59,
        "beta_upper": 11,
        "q": 9,
        "P_q": 46,
        "maximal_edge_matching_lower": 7,
    }
    payload = {
        "schema": "erdos151-order50-pure-triangular-gate-audit-v1",
        "status": "PASS",
        "n": n,
        "h": h,
        "beta_upper": beta_upper,
        "chromatic_upper": q,
        "two_largest_color_classes_lower": two_class_lower,
        "maximal_edge_cover_lower_on_that_set": maximal_edge_cover_lower,
        "assumed_maximal_edge_matching_upper": assumed_matching_upper,
        "matching_endpoint_cover_upper": matching_cover_upper,
        "vertices_outside_matching_cover_lower": outside_cover_lower,
        "sorted_second_color_remainder_upper": sorted_class_second_upper,
        "vertices_outside_matching_cover_upper": outside_cover_upper,
        "maximal_edge_matching_lower": 3,
        "uniform_matching_burden": {
            "q": "3*ceil((beta_upper+1)/4)",
            "P_q": "beta_upper+(q-2)*floor(beta_upper/2)",
            "bound": "nu(M)>=ceil((n-P_q)/2)",
            "examples": [example_50, example_59],
            "scope": "finite and non-asymptotic",
        },
        "contradiction": f"beta >= {two_class_lower} > {beta_upper}",
        "logical_dependencies": [
            "K4-free and every edge triangular imply every open neighborhood is ambient-admissible, hence Delta<=beta",
            "Lovasz maximum-degree decomposition with all part bounds equal to 3",
            "Brooks theorem on each K4-free maximum-degree-at-most-3 part",
            "the union of two proper color classes is triangle-free and hence ambient-admissible in the pure-triangular K4-free case",
            "under matching number at most 2, endpoints of a maximal matching cover M with at most 4 vertices",
            "after deleting that cover, every union of two F-color-class remainders is ambient-admissible and has size at most 10",
        ],
        "claim_boundary": (
            "numeric replay only; the written proof in "
            "PURE_TRIANGULAR_CHROMATIC_GATE.md carries the logical audit"
        ),
    }
    output = Path(__file__).with_name("audit_pure_triangular_gate.result.json")
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
