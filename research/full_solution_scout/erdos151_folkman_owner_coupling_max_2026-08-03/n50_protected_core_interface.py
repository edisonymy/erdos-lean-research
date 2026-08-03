#!/usr/bin/env python3
"""Replay the exact degree-ten interface for a protected K4-free core at n=50."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    raw = args.census.read_bytes()
    census = json.loads(raw)
    assert census["parameters"] == {
        "direct_definition_edge_limit": 11,
        "max_edges": 11,
        "triangle_free": True,
    }
    assert census["counts"]["all_graphs"] == 161
    assert all(x["direct_definition_checked"] for x in census["all_obstructions"])

    obstructions = census["all_obstructions"]
    first = [x for x in obstructions if x["m"] == 10]
    through_eleven = [x for x in obstructions if x["m"] in (10, 11)]
    assert len(first) == 4
    assert len(through_eleven) == 10
    type_counts = Counter((x["m"], x["n"]) for x in through_eleven)
    assert type_counts == Counter({(10, 8): 3, (10, 9): 1,
                                  (11, 8): 2, (11, 9): 3, (11, 10): 1})

    # For beta<=10, Theorem 2.1 at a degree-ten vertex has m=50-10-1=39.
    saturation_rhs = 10**2 - 2 * 39
    assert saturation_rhs == 22
    cases = []
    for core_triangles in (10, 11):
        for extrinsic_triangles in range(2):
            for kappa in range(3):
                if 2 * (core_triangles + extrinsic_triangles) + kappa <= saturation_rhs:
                    cases.append(
                        {
                            "core_triangles": core_triangles,
                            "extrinsic_triangles": extrinsic_triangles,
                            "degree_defect_kappa": kappa,
                        }
                    )
    assert cases == [
        {"core_triangles": 10, "extrinsic_triangles": 0, "degree_defect_kappa": 0},
        {"core_triangles": 10, "extrinsic_triangles": 0, "degree_defect_kappa": 1},
        {"core_triangles": 10, "extrinsic_triangles": 0, "degree_defect_kappa": 2},
        {"core_triangles": 10, "extrinsic_triangles": 1, "degree_defect_kappa": 0},
        {"core_triangles": 11, "extrinsic_triangles": 0, "degree_defect_kappa": 0},
    ]

    payload = {
        "schema": "erdos151-n50-protected-core-interface-v1",
        "target": {
            "order": 50,
            "H": 11,
            "counterexample_beta_upper_bound": 10,
            "scope": "conditional on order 50 being the least counterexample order",
            "degree_range_from_least_counterexample_window_and_R3_10_upper_41": [9, 10],
        },
        "degree_ten_saturation": {
            "inequality": "2*t_G(v)+kappa(v)<=22",
            "surviving_integer_cases": cases,
        },
        "link_census": {
            "path": str(args.census),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "all_trianglefree_delta_at_least_2_graphs_through_11_edges": 161,
            "first_nonuniversally_adaptable_edge_count": 10,
            "first_obstruction_count": 4,
            "obstructions_through_11_edges": 10,
            "type_counts_by_edges_and_order": {
                f"m={m},n={n}": count
                for (m, n), count in sorted(type_counts.items())
            },
            "graph6": [x["graph6"] for x in sorted(
                through_eleven, key=lambda x: (x["m"], x["n"], x["graph6"])
            )],
        },
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
