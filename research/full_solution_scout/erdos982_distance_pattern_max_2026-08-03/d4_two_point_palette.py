#!/usr/bin/env python3
"""Exact palette-preserving extension test for the convex D4 octagon.

The seed, after scaling b=1, is

    (+/-r,0), (0,+/-r), (+/-1,+/-1),  1 < r < 2.

At each seed vertex the four squared distances to the other seed vertices
form a known four-element palette.  This program finds *all* points x=(u,v)
whose squared distance to every seed vertex belongs to that vertex's old
palette.  It is lossless for this restricted extension problem: subtracting
the conditions at (r,0) and (-r,0) forces u to be a difference of two palette
entries divided by 4r, and similarly for v.

All membership equations and their gcds are computed over QQ[r].  Floating
point is used only to classify roots geometrically and to print diagnostics;
the defining factors and rational coordinate functions are retained.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import sympy as sp


R = sp.symbols("r", positive=True)


def expression_key(expr: sp.Expr) -> str:
    return sp.srepr(sp.cancel(expr))


def unique_expressions(values: Iterable[sp.Expr]) -> list[sp.Expr]:
    out: dict[str, sp.Expr] = {}
    for value in values:
        value = sp.cancel(value)
        out[expression_key(value)] = value
    return sorted(out.values(), key=sp.default_sort_key)


def numerator_poly(expr: sp.Expr) -> sp.Poly:
    numerator, _denominator = sp.fraction(sp.cancel(expr))
    return sp.Poly(sp.expand(numerator), R, domain=sp.QQ)


def gcd_nonzero(polynomials: Iterable[sp.Poly]) -> sp.Poly | None:
    answer: sp.Poly | None = None
    for polynomial in polynomials:
        if polynomial.is_zero:
            continue
        answer = polynomial.monic() if answer is None else sp.gcd(answer, polynomial).monic()
        if answer.degree() == 0:
            return answer
    return answer


def cross(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def strict_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    pts = sorted(set(points))
    if len(pts) < 3:
        return []
    lower: list[tuple[float, float]] = []
    for point in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 1e-10:
            lower.pop()
        lower.append(point)
    upper: list[tuple[float, float]] = []
    for point in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 1e-10:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def real_roots_in_open_interval(poly: sp.Poly, low: float, high: float) -> list[sp.Expr]:
    roots: list[sp.Expr] = []
    # all_roots returns exact radicals or CRootOf objects and accounts for
    # multiplicity.  Square-free below means every retained root is unique.
    for root in sp.Poly(poly.sqf_part(), R).all_roots():
        approximation = complex(sp.N(root, 40))
        if abs(approximation.imag) < 1e-25 and low < approximation.real < high:
            roots.append(root)
    return roots


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("d4_two_point_palette.json"))
    args = parser.parse_args()

    c = R**2 - 2 * R + 2
    d = R**2 + 2 * R + 2
    axial_palette = (4 * R**2, 2 * R**2, c, d)
    diagonal_palette = (sp.Integer(8), sp.Integer(4), c, d)

    possible_coordinate_values = unique_expressions(
        (right - left) / (4 * R)
        for left in axial_palette
        for right in axial_palette
    )

    seed_symbolic = (
        (R, 0, axial_palette),
        (0, R, axial_palette),
        (-R, 0, axial_palette),
        (0, -R, axial_palette),
        (1, 1, diagonal_palette),
        (-1, 1, diagonal_palette),
        (-1, -1, diagonal_palette),
        (1, -1, diagonal_palette),
    )

    candidate_records: list[dict[str, object]] = []
    identity_records: list[dict[str, str]] = []
    tested_coordinate_pairs = 0
    polynomial_survivors = 0

    for u in possible_coordinate_values:
        for v in possible_coordinate_values:
            tested_coordinate_pairs += 1
            membership_polynomials: list[sp.Poly] = []
            for px, py, palette in seed_symbolic:
                squared_distance = sp.expand((u - px) ** 2 + (v - py) ** 2)
                membership = sp.prod(squared_distance - value for value in palette)
                membership_polynomials.append(numerator_poly(membership))

            common = gcd_nonzero(membership_polynomials)
            if common is None:
                identity_records.append({"u": str(u), "v": str(v)})
                continue
            if common.degree() == 0:
                continue
            polynomial_survivors += 1

            factorization = sp.factor_list(common.as_expr())[1]
            for factor_expr, _multiplicity in factorization:
                factor = sp.Poly(factor_expr, R, domain=sp.QQ).monic()
                for root in real_roots_in_open_interval(factor, 1.0, 2.0):
                    r_value = float(sp.N(root, 30))
                    u_value = float(sp.N(u.subs(R, root), 30))
                    v_value = float(sp.N(v.subs(R, root), 30))
                    seed_numeric = [
                        (r_value, 0.0),
                        (0.0, r_value),
                        (-r_value, 0.0),
                        (0.0, -r_value),
                        (1.0, 1.0),
                        (-1.0, 1.0),
                        (-1.0, -1.0),
                        (1.0, -1.0),
                    ]
                    point = (u_value, v_value)
                    duplicate_distance = min(
                        (u_value - px) ** 2 + (v_value - py) ** 2
                        for px, py in seed_numeric
                    )
                    hull = strict_hull(seed_numeric + [point])
                    distinct = duplicate_distance > 1e-16
                    preserves_all_seed_vertices = distinct and len(hull) == 9

                    # Exact membership is represented by the common factor.
                    # This numerical residual is a guard against implementation
                    # mistakes in root selection, not the proof of membership.
                    palettes_numeric = []
                    for px, py, palette in seed_symbolic:
                        actual = (u_value - float(sp.N(px.subs(R, root) if hasattr(px, "subs") else px))) ** 2
                        actual += (v_value - float(sp.N(py.subs(R, root) if hasattr(py, "subs") else py))) ** 2
                        vals = [float(sp.N(value.subs(R, root), 30)) for value in palette]
                        palettes_numeric.append(min(abs(actual - value) for value in vals))

                    candidate_records.append({
                        "factor": str(factor.as_expr()),
                        "factor_coefficients_high_to_low": [str(value) for value in factor.all_coeffs()],
                        "r_approx": r_value,
                        "u": str(u),
                        "v": str(v),
                        "point_approx": [u_value, v_value],
                        "minimum_squared_separation_from_seed": duplicate_distance,
                        "distinct_from_seed": distinct,
                        "strict_hull_size_with_seed": len(hull),
                        "preserves_all_seed_vertices": preserves_all_seed_vertices,
                        "maximum_palette_residual": max(palettes_numeric),
                    })

    # Several coordinate representations can coincide at a special algebraic
    # root.  Deduplicate only for the headline counts; retain every exact route.
    unique_geometric: dict[tuple[int, int, int], dict[str, object]] = {}
    for record in candidate_records:
        key = (
            round(float(record["r_approx"]) * 10**10),
            round(float(record["point_approx"][0]) * 10**10),
            round(float(record["point_approx"][1]) * 10**10),
        )
        unique_geometric.setdefault(key, record)

    payload = {
        "claim_scope": "D4 seed plus points using only every old vertex's four-value palette",
        "lossless_within_scope": True,
        "convexity_interval": [1, 2],
        "possible_coordinate_value_count": len(possible_coordinate_values),
        "possible_coordinate_values": [str(value) for value in possible_coordinate_values],
        "tested_coordinate_pairs": tested_coordinate_pairs,
        "coordinate_pairs_with_nonconstant_common_factor": polynomial_survivors,
        "all_membership_identity_coordinate_pairs": identity_records,
        "exact_routes_in_interval": len(candidate_records),
        "unique_geometric_candidates_in_interval": len(unique_geometric),
        "unique_distinct_candidates": sum(bool(r["distinct_from_seed"]) for r in unique_geometric.values()),
        "unique_candidates_preserving_all_eight_seed_vertices": sum(
            bool(r["preserves_all_seed_vertices"]) for r in unique_geometric.values()
        ),
        "candidates": candidate_records,
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    args.out.write_bytes(encoded + b"\n")
    print(json.dumps({
        key: payload[key]
        for key in (
            "possible_coordinate_value_count",
            "tested_coordinate_pairs",
            "coordinate_pairs_with_nonconstant_common_factor",
            "exact_routes_in_interval",
            "unique_geometric_candidates_in_interval",
            "unique_distinct_candidates",
            "unique_candidates_preserving_all_eight_seed_vertices",
        )
    }, indent=2))
    print("sha256", hashlib.sha256(encoded + b"\n").hexdigest())


if __name__ == "__main__":
    main()
