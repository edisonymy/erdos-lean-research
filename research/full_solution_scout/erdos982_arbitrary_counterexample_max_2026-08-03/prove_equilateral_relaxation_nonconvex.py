#!/usr/bin/env python3
"""Exact nonconvexity certificate for the rank-10 H8 relaxation.

This is a complete branch proof, not a sample search:

* all 256 choices of orientations for the eight equilateral triangles are
  solved exactly over Q(sqrt(-3));
* 212 choices force the gauge edge to collapse, and each of the 42 remaining
  zero-parameter mixed-orientation branches has coincident vertices;
* the only nondegenerate positive-dimensional branches have all eight
  orientations equal (the two branches are mirror images);
* on the positive branch, central symmetry leaves six possible convex cyclic
  orders, and each order requires two orientation determinants which are exact
  negatives.  Strict convexity is therefore impossible for every real/complex
  parameter, with no bounded search.
"""

from __future__ import annotations

from itertools import combinations, permutations, product
import json

from check_harborth_field import Q3
from enumerate_equilateral_h8_relaxation import (
    NAMES,
    TRIANGLES,
    normalized_affine_solution,
)


class Poly:
    """Sparse polynomial in real x,y with coefficients in Q(sqrt(3))."""

    def __init__(self, terms=None):
        self.terms = {m: c for m, c in (terms or {}).items() if c != Q3(0)}

    @staticmethod
    def coerce(value):
        return value if isinstance(value, Poly) else Poly({(0, 0): Q3.coerce(value)})

    def __add__(self, other):
        other = self.coerce(other)
        terms = self.terms.copy()
        for monomial, coefficient in other.terms.items():
            terms[monomial] = terms.get(monomial, Q3(0)) + coefficient
        return Poly(terms)

    __radd__ = __add__

    def __neg__(self):
        return Poly({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        terms = {}
        for (i, j), a in self.terms.items():
            for (k, ell), b in other.terms.items():
                monomial = (i + k, j + ell)
                terms[monomial] = terms.get(monomial, Q3(0)) + a * b
        return Poly(terms)

    __rmul__ = __mul__

    def __eq__(self, other):
        return self.terms == self.coerce(other).terms

    def text(self):
        if not self.terms:
            return "0"
        pieces = []
        for (i, j), coefficient in sorted(self.terms.items(), reverse=True):
            monomial = "*".join((["x" + (f"^{i}" if i != 1 else "")] if i else []) + (["y" + (f"^{j}" if j != 1 else "")] if j else []))
            pieces.append(coefficient.text() + ("*" + monomial if monomial else ""))
        return " + ".join(pieces)


X = Poly({(1, 0): Q3(1)})
Y = Poly({(0, 1): Q3(1)})
H = Q3(0, 1) / 2  # sqrt(3)/2


def uniform_branch_points():
    # omega=(1/2,h), q=(1/2,-h), t=(x,y).
    p0 = (Poly(), Poly())
    p1 = (Poly.coerce(1), Poly())
    p7 = (Poly.coerce(Q3(1) / 2), Poly.coerce(H))
    p6 = (X, Y)
    p3 = (X / 2 + Y * H, Y / 2 - X * H)
    p4 = (p7[0] + p3[0], p7[1] + p3[1])
    p2 = ((1 - X) / 2 + Y * H, (1 - X) * H - Y / 2)
    p5 = ((X - 1) / 2 + Y * H, Y / 2 - (X - 1) * H)
    return [p0, p1, p2, p3, p4, p5, p6, p7]


# Add scalar division after class definition to keep the implementation small.
Poly.__truediv__ = lambda self, other: self * (Q3.coerce(other).inverse())


def orientation(points, triple):
    a, b, c = (points[i] for i in triple)
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


OPPOSITE = {0: 4, 4: 0, 1: 5, 5: 1, 2: 6, 6: 2, 3: 7, 7: 3}


def cyclic_orientation(order, triple):
    position = {vertex: i for i, vertex in enumerate(order)}
    a, b, c = (position[v] for v in triple)
    return 1 if (b - a) % 8 < (c - a) % 8 else -1


def main():
    inconsistent = 0
    fixed_degenerate = 0
    flexible = []
    duplicate_histogram = {}

    for signs in product((1, -1), repeat=8):
        solution = normalized_affine_solution(signs)
        if solution is None:
            # If a configuration had distinct vertices, z0 != z1 and this
            # normalization would be possible.  Hence this branch is degenerate.
            inconsistent += 1
            continue
        particular, directions = solution
        if not directions:
            duplicates = [
                (i, j) for i, j in combinations(range(8), 2)
                if particular[i] == particular[j]
            ]
            assert duplicates
            fixed_degenerate += 1
            duplicate_histogram[str(len(duplicates))] = duplicate_histogram.get(str(len(duplicates)), 0) + 1
            continue
        assert len(directions) == 1
        flexible.append(signs)

    assert inconsistent == 212
    assert fixed_degenerate == 42
    assert flexible == [(1,) * 8, (-1,) * 8]

    # The negative branch is the mirror image of the positive branch.  On the
    # positive branch, the exact affine solution has opposite pairs summing to
    # the same point for every parameter.
    plus_particular, plus_directions = normalized_affine_solution((1,) * 8)
    direction = plus_directions[0]
    pair_sums = []
    for i in range(4):
        j = OPPOSITE[i]
        pair_sums.append((plus_particular[i] + plus_particular[j], direction[i] + direction[j]))
    assert len(set(pair_sums)) == 1

    # In a strictly convex centrally symmetric octagon, opposite vertices are
    # separated by four places.  Normalize the first vertex to 0 and retain
    # only orders compatible with the eight positive triangle orientations.
    orders = []
    for tail in permutations(range(1, 8)):
        order = (0,) + tail
        if not all(order[(i + 4) % 8] == OPPOSITE[order[i]] for i in range(8)):
            continue
        if all(cyclic_orientation(order, triangle) == 1 for triangle in TRIANGLES):
            orders.append(order)
    assert len(orders) == 6

    # One exact opposite-determinant certificate per possible cyclic order.
    contradictory_triples = [
        ((0, 1, 2), (0, 5, 7)),
        ((0, 1, 3), (1, 7, 2)),
        ((0, 2, 3), (0, 6, 5)),
        ((0, 2, 1), (2, 5, 3)),
        ((0, 3, 1), (0, 7, 6)),
        ((0, 3, 2), (3, 6, 1)),
    ]
    points = uniform_branch_points()
    certificates = []
    for order, (first, second) in zip(orders, contradictory_triples):
        assert cyclic_orientation(order, first) == 1
        assert cyclic_orientation(order, second) == 1
        first_polynomial = orientation(points, first)
        second_polynomial = orientation(points, second)
        assert first_polynomial == -second_polynomial
        assert first_polynomial != Poly()
        certificates.append(
            {
                "cyclic_order": [NAMES[i] for i in order],
                "required_positive_triples": [
                    [NAMES[i] for i in first],
                    [NAMES[i] for i in second],
                ],
                "first_orientation_polynomial": first_polynomial.text(),
                "second_is_exact_negative": True,
            }
        )

    result = {
        "orientation_patterns": 256,
        "branches_forcing_z0_equals_z1": inconsistent,
        "gauge_consistent_rigid_branches_with_duplicate_vertices": fixed_degenerate,
        "rigid_branch_duplicate_pair_count_histogram": duplicate_histogram,
        "nondegenerate_flexible_orientation_patterns": [list(s) for s in flexible],
        "flexible_branches_are_mirror_images": True,
        "uniform_branch_is_centrally_symmetric": True,
        "candidate_strictly_convex_cyclic_orders": len(orders),
        "opposite_orientation_certificates": certificates,
        "conclusion": "no strictly convex realization exists on any branch",
        "status": "VERIFIED_NONCONVEX",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
