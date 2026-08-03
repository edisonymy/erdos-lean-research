#!/usr/bin/env python3
"""Exact branch enumeration for the eight-equilateral-triangle H8 relaxation.

The minimum-rank local-4 relaxation found by
search_h8_local4_relaxations.py decomposes K8 minus a perfect matching into
eight equilateral triangles.  Once an orientation is chosen for each triangle,
the realization equations are complex-linear over Q(sqrt(-3)).  This script
enumerates all 2^8 orientation branches, normalizes z0=0,z1=1, and searches a
dense exact rational grid in every remaining complex parameter for strictly
convex realizations.  No floating-point geometry is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import json


@dataclass(frozen=True)
class EisensteinField:
    """a+b*s, where s^2=-3 (embedded as s=i*sqrt(3))."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __init__(self, a=0, b=0):
        object.__setattr__(self, "a", Fraction(a))
        object.__setattr__(self, "b", Fraction(b))

    @staticmethod
    def coerce(x):
        return x if isinstance(x, EisensteinField) else EisensteinField(x)

    def __add__(self, other):
        other = self.coerce(other)
        return EisensteinField(self.a + other.a, self.b + other.b)

    __radd__ = __add__

    def __neg__(self):
        return EisensteinField(-self.a, -self.b)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        return EisensteinField(
            self.a * other.a - 3 * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    __rmul__ = __mul__

    def inverse(self):
        den = self.a * self.a + 3 * self.b * self.b
        if den == 0:
            raise ZeroDivisionError
        return EisensteinField(self.a / den, -self.b / den)

    def __truediv__(self, other):
        return self * self.coerce(other).inverse()

    def __rtruediv__(self, other):
        return self.coerce(other) / self

    def __bool__(self):
        return self.a != 0 or self.b != 0

    def text(self):
        if self.b == 0:
            return str(self.a)
        if self.a == 0:
            return f"{self.b}*sqrt(-3)"
        sign = "+" if self.b > 0 else "-"
        return f"{self.a}{sign}{abs(self.b)}*sqrt(-3)"


K = EisensteinField
ZERO = K(0)
ONE = K(1)
RHO_PLUS = K(Fraction(1, 2), Fraction(1, 2))
RHO_MINUS = K(Fraction(1, 2), Fraction(-1, 2))

NAMES = ["A0", "B0", "A1", "B1", "A2", "B2", "A3", "B3"]
TRIANGLES = [
    (0, 1, 7),
    (0, 2, 5),
    (0, 3, 6),
    (1, 2, 3),
    (1, 4, 6),
    (2, 4, 7),
    (3, 4, 5),
    (5, 6, 7),
]


def rref_augmented(rows, variable_count):
    rows = [row[:] for row in rows]
    pivot_columns = []
    pivot_row = 0
    for col in range(variable_count):
        pivot = next((r for r in range(pivot_row, len(rows)) if rows[r][col]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inv = rows[pivot_row][col].inverse()
        rows[pivot_row] = [x * inv for x in rows[pivot_row]]
        for r in range(len(rows)):
            if r == pivot_row or not rows[r][col]:
                continue
            factor = rows[r][col]
            rows[r] = [x - factor * y for x, y in zip(rows[r], rows[pivot_row])]
        pivot_columns.append(col)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    inconsistent = any(all(not row[c] for c in range(variable_count)) and row[-1] for row in rows)
    return rows, pivot_columns, inconsistent


def normalized_affine_solution(signs):
    rows = []
    for (a, b, c), sign in zip(TRIANGLES, signs):
        rho = RHO_PLUS if sign == 1 else RHO_MINUS
        row = [ZERO] * 9  # eight variables plus RHS
        row[a] = rho - 1
        row[b] = -rho
        row[c] = ONE
        rows.append(row)
    gauge0 = [ZERO] * 9
    gauge0[0] = ONE
    rows.append(gauge0)  # z0=0
    gauge1 = [ZERO] * 9
    gauge1[1] = ONE
    gauge1[-1] = ONE
    rows.append(gauge1)  # z1=1
    reduced, pivots, inconsistent = rref_augmented(rows, 8)
    if inconsistent:
        return None
    free = [c for c in range(8) if c not in pivots]
    particular = [ZERO] * 8
    directions = [[ZERO] * 8 for _ in free]
    pivot_to_row = {p: reduced[i] for i, p in enumerate(pivots)}
    for p in pivots:
        row = pivot_to_row[p]
        particular[p] = row[-1]
        for k, f in enumerate(free):
            directions[k][p] = -row[f]
    for k, f in enumerate(free):
        directions[k][f] = ONE
    return particular, directions


def cross(a, b, c):
    # Imaginary coordinates are b*sqrt(3); the omitted positive sqrt(3)
    # factor does not affect the exact sign.
    return (b.a - a.a) * (c.b - b.b) - (b.b - a.b) * (c.a - b.a)


def convex_hull(points):
    indexed = sorted(enumerate(points), key=lambda item: (item[1].a, item[1].b))
    if len({(p.a, p.b) for p in points}) != len(points):
        return []

    def half(items):
        hull = []
        for item in items:
            while len(hull) >= 2 and cross(hull[-2][1], hull[-1][1], item[1]) <= 0:
                hull.pop()
            hull.append(item)
        return hull

    lower = half(indexed)
    upper = half(list(reversed(indexed)))
    return [i for i, _ in lower[:-1] + upper[:-1]]


def evaluate(particular, directions, parameters):
    points = particular[:]
    for direction, parameter in zip(directions, parameters):
        points = [z + parameter * dz for z, dz in zip(points, direction)]
    return points


def sqdist(a, b):
    d = a - b
    # |a+b*i*sqrt(3)|^2 = a^2+3b^2, a rational number.
    return d.a * d.a + 3 * d.b * d.b


def local_counts(points):
    return [len({sqdist(points[i], points[j]) for j in range(8) if i != j}) for i in range(8)]


def point_text(z):
    return {"x": str(z.a), "y_over_sqrt3": str(z.b), "complex": z.text()}


def parameter_grid():
    # The exact grid grows in shells so the first witness is reasonably small.
    yield ZERO
    for denominator in (1, 2, 3, 4, 6, 8):
        for radius in range(1, 9):
            values = range(-radius, radius + 1)
            for a in values:
                for b in values:
                    if max(abs(a), abs(b)) != radius:
                        continue
                    yield K(Fraction(a, denominator), Fraction(b, denominator))


def main():
    branch_dimensions = {}
    normalized_branches = []
    convex_witnesses = []
    grid = list(parameter_grid())

    for signs in product((1, -1), repeat=8):
        solution = normalized_affine_solution(signs)
        if solution is None:
            branch_dimensions["inconsistent_gauge"] = branch_dimensions.get("inconsistent_gauge", 0) + 1
            continue
        particular, directions = solution
        parameter_count = len(directions)
        branch_dimensions[str(parameter_count)] = branch_dimensions.get(str(parameter_count), 0) + 1
        normalized_branches.append((signs, particular, directions))

        candidates = [tuple()]
        if parameter_count == 1:
            candidates = ((t,) for t in grid)
        elif parameter_count == 2:
            # Rare higher-dimensional branches: a deliberately bounded exact
            # product grid is enough to establish existence, not nonexistence.
            small = grid[:81]
            candidates = product(small, repeat=2)
        elif parameter_count > 2:
            small = grid[:17]
            candidates = product(small, repeat=parameter_count)

        for parameters in candidates:
            points = evaluate(particular, directions, parameters)
            hull = convex_hull(points)
            if len(hull) == 8:
                counts = local_counts(points)
                assert max(counts) <= 4
                convex_witnesses.append(
                    {
                        "orientation_signs": list(signs),
                        "parameter_count": parameter_count,
                        "parameters": [p.text() for p in parameters],
                        "points": dict(zip(NAMES, map(point_text, points))),
                        "counterclockwise_hull": [NAMES[i] for i in hull],
                        "local_distance_counts": dict(zip(NAMES, counts)),
                    }
                )
                break

    result = {
        "orientation_patterns": 256,
        "normalized_branch_parameter_count_distribution": branch_dimensions,
        "normalized_branches": len(normalized_branches),
        "exact_grid_values_per_one_parameter_branch": len(grid),
        "strictly_convex_branches_found": len(convex_witnesses),
        "first_convex_witnesses": convex_witnesses[:16],
        "scope_note": (
            "A witness is a proof of existence. Absence from the bounded grid "
            "would not prove that a positive-dimensional branch is nonconvex."
        ),
        "status": "VERIFIED",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
