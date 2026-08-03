#!/usr/bin/env python3
"""Exact finite proof that H8 cannot accept a ninth locally-3-distance point.

For a new point p to preserve the three-distance property at every old H8
vertex, |p-v|^2 must be one of the three squared radii already visible from v.
Choices at the three noncollinear axial centers A0,A2,A1 determine p over
Q(sqrt(3)); this checker exhausts all 3^3 choices and tests all eight centers.
"""

from __future__ import annotations

import json

from check_harborth_field import NAMES, ONE, POINTS, Q3, R, ZERO, dist2


def main():
    allowed = []
    for i in range(8):
        allowed.append({dist2(POINTS[i], POINTS[j]) for j in range(8) if i != j})
        assert len(allowed[-1]) == 3

    # Indices in angular order: A0=0, A1=2, A2=4.
    i_right, i_top, i_left = 0, 2, 4
    triples_consistent = []
    fully_valid = []
    best_support = 0
    best_candidates = []

    for u in allowed[i_right]:
        for v in allowed[i_left]:
            # Subtract the A0/A2 circle equations: 4 R x = v-u.
            x = (v - u) / (4 * R)
            radial_square = u + 2 * R * x - R * R  # x^2+y^2
            for w in allowed[i_top]:
                # The A1 circle equation gives y uniquely.
                y = (radial_square + R * R - w) / (2 * R)
                if x * x + y * y != radial_square:
                    continue
                p = (x, y)
                assert dist2(p, POINTS[i_right]) == u
                assert dist2(p, POINTS[i_left]) == v
                assert dist2(p, POINTS[i_top]) == w
                triples_consistent.append(p)
                support = [i for i in range(8) if dist2(p, POINTS[i]) in allowed[i]]
                if len(support) > best_support:
                    best_support = len(support)
                    best_candidates = [(p, support)]
                elif len(support) == best_support:
                    best_candidates.append((p, support))
                if len(support) == 8:
                    fully_valid.append(p)

    # This is the exact nonextendibility certificate.
    assert not fully_valid
    assert best_support < 8

    def point_text(p):
        return [p[0].text(), p[1].text()]

    result = {
        "checker": "exhaustive exact Q(sqrt(3)) circle-choice elimination",
        "three_centers": [NAMES[i_right], NAMES[i_left], NAMES[i_top]],
        "radius_choice_branches": 27,
        "branches_consistent_at_three_centers": len(triples_consistent),
        "fully_valid_extension_points": len(fully_valid),
        "maximum_old_centers_satisfied": best_support,
        "maximal_support_witnesses": [
            {"point": point_text(p), "centers": [NAMES[i] for i in support]}
            for p, support in best_candidates
        ],
        "status": "VERIFIED_NO_EXTENSION",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
