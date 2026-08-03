#!/usr/bin/env python3
"""Independent assignment-based audit of d4_two_point_palette.py.

Unlike the primary checker, this script enumerates the four palette choices at
the four axial seed vertices.  Those choices determine u and v.  It then takes
an exact gcd of the two axial placement equations and the four diagonal
membership products, and uses exact real-root counting on (1,2).
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    r = sp.symbols("r")
    c = r**2 - 2 * r + 2
    d = r**2 + 2 * r + 2
    axial = (4 * r**2, 2 * r**2, c, d)
    diagonal = (sp.Integer(8), sp.Integer(4), c, d)
    diagonal_points = ((1, 1), (-1, 1), (-1, -1), (1, -1))

    assignments = 0
    nonconstant_gcds = 0
    roots_in_interval = 0
    witnesses = []

    def polynomial(expr: sp.Expr) -> sp.Poly:
        numerator = sp.fraction(sp.cancel(expr))[0]
        return sp.Poly(sp.expand(numerator), r, domain=sp.QQ)

    for east_i, west_i, north_i, south_i in itertools.product(range(4), repeat=4):
        assignments += 1
        east, west = axial[east_i], axial[west_i]
        north, south = axial[north_i], axial[south_i]
        u = sp.cancel((west - east) / (4 * r))
        v = sp.cancel((south - north) / (4 * r))

        constraints = [
            polynomial((u - r) ** 2 + v**2 - east),
            polynomial(u**2 + (v - r) ** 2 - north),
        ]
        for px, py in diagonal_points:
            distance = (u - px) ** 2 + (v - py) ** 2
            constraints.append(polynomial(sp.prod(distance - value for value in diagonal)))

        common = None
        for constraint in constraints:
            if constraint.is_zero:
                continue
            common = constraint.monic() if common is None else sp.gcd(common, constraint).monic()
            if common.degree() == 0:
                break
        if common is None:
            # This would be a continuous family and therefore a witness.
            roots_in_interval += 1
            witnesses.append({
                "assignment": [east_i, west_i, north_i, south_i],
                "u": str(u),
                "v": str(v),
                "common": "identically zero",
            })
            continue
        if common.degree() == 0:
            continue
        nonconstant_gcds += 1
        count = int(common.sqf_part().count_roots(1, 2))
        roots_in_interval += count
        if count:
            witnesses.append({
                "assignment": [east_i, west_i, north_i, south_i],
                "u": str(u),
                "v": str(v),
                "common": str(common.as_expr()),
                "root_count_open_interval_1_2": count,
            })

    payload = {
        "scope": "D4 seed, one new point restricted to each old vertex's old palette",
        "method": "independent enumeration of four axial palette assignments",
        "assignments": assignments,
        "assignments_with_nonconstant_common_gcd": nonconstant_gcds,
        "exact_real_roots_in_open_interval_1_2": roots_in_interval,
        "verified_no_extension": roots_in_interval == 0,
        "witnesses": witnesses,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print("sha256", hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
