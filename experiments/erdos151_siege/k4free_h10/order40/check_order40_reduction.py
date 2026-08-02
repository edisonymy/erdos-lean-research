#!/usr/bin/env python3
"""Standard-library arithmetic audit for ORDER40_RESIDUAL.md.

This checker exhausts the integer fibre-size projection and verifies the
two equality-row counts.  It does not check the cited graph-theoretic
theorems or construct/verify an arrowing core.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def beta_lower_small_order(n: int) -> int:
    if n <= 0:
        return 0
    if n <= 2:
        return 1
    if n <= 5:
        return 2
    if n <= 8:
        return 3
    raise ValueError(n)


def rows_for_r(r: int) -> list[dict]:
    q = 40 - r
    pair_cap = 9 - beta_lower_small_order(r - 2)
    survivors = []
    # Equation (5) itself bounds every weight by pair_cap (pair it with a
    # zero fibre if necessary), so this finite box is complete.
    for weights in itertools.combinations_with_replacement(
        range(pair_cap + 1), r
    ):
        if r >= 2 and weights[-1] + weights[-2] > pair_cap:
            continue
        c = sum(weights)
        s = sum(weight > 0 for weight in weights)
        if s < r - 2:
            continue
        # Turán/outside-degree inequality (6).
        if c < 4 * r + 4 * s - 2 * (r * r // 3):
            continue
        for b in range(q - c + 1):
            if q * (r - 2) + 2 * b > 8 * c:
                continue
            # If a core-degree-nine vertex exists, every fibre is nonempty.
            if b > 0 and s < r:
                continue
            survivors.append(
                {
                    "weights": list(weights),
                    "nonempty_fibres": s,
                    "boundary_endpoints": c,
                    "core_degree9": b,
                }
            )
    return survivors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()
    rows = []
    expected = {
        8: [{
            "weights": [3] * 8,
            "nonempty_fibres": 8,
            "boundary_endpoints": 24,
            "core_degree9": 0,
        }],
        10: [{
            "weights": [3] * 10,
            "nonempty_fibres": 10,
            "boundary_endpoints": 30,
            "core_degree9": 0,
        }],
    }
    for r in range(2, 11):
        survivors = rows_for_r(r)
        assert survivors == expected.get(r, []), (r, survivors)
        rows.append({"r": r, "survivors": survivors})

    # r=0,1 eight-color/matching-deletion averages.
    small_remainder = {
        "r0": {"pair_score_sum_lower": 7 * 40 - 20},
        "r1": {"pair_score_sum_lower": 7 * 39 - 19},
        "nine_per_pair_total": 28 * 9,
    }
    assert small_remainder["r0"]["pair_score_sum_lower"] > 28 * 9
    assert small_remainder["r1"]["pair_score_sum_lower"] > 28 * 9

    equality_checks = {
        "r8_fibre_pairs": 8 * 7 // 2,
        "r8_max_blocked_by_one_link": 12,
        "r10_triangles": 30 * 10 // 3,
        "r10_fibre_triples": 10 * 9 * 8 // 6,
    }
    assert equality_checks["r8_max_blocked_by_one_link"] < equality_checks[
        "r8_fibre_pairs"
    ]
    assert equality_checks["r10_triangles"] < equality_checks[
        "r10_fibre_triples"
    ]

    script = Path(__file__).resolve()
    result = {
        "status": "VERIFIED_ARITHMETIC",
        "scope": (
            "Integer fibre funnel and displayed counts only; external "
            "theorems and graph-semantic lemmas require proof audit."
        ),
        "rows": rows,
        "small_remainder": small_remainder,
        "equality_checks": equality_checks,
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.emit:
        args.emit.write_bytes((rendered + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
