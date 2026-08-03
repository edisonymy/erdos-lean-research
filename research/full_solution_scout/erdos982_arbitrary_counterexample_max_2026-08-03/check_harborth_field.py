#!/usr/bin/env python3
"""Exact, dependency-free audit of the Harborth--Fishburn H8 configuration.

Arithmetic is performed in Q(sqrt(3)), represented as pairs of Fractions.
The checker verifies the complete distance partition, local distance counts,
failure of strict convexity, the Euclidean distance matrix, and infinitesimal
rigidity of the four-colour distance-equality framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json


@dataclass(frozen=True)
class Q3:
    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __init__(self, a=0, b=0):
        object.__setattr__(self, "a", Fraction(a))
        object.__setattr__(self, "b", Fraction(b))

    @staticmethod
    def coerce(x):
        return x if isinstance(x, Q3) else Q3(x)

    def __add__(self, other):
        other = self.coerce(other)
        return Q3(self.a + other.a, self.b + other.b)

    __radd__ = __add__

    def __neg__(self):
        return Q3(-self.a, -self.b)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        return Q3(
            self.a * other.a + 3 * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    __rmul__ = __mul__

    def inverse(self):
        den = self.a * self.a - 3 * self.b * self.b
        if den == 0:
            raise ZeroDivisionError
        return Q3(self.a / den, -self.b / den)

    def __truediv__(self, other):
        return self * self.coerce(other).inverse()

    def __rtruediv__(self, other):
        return self.coerce(other) / self

    def sign(self):
        """Exact sign, using irrationality of sqrt(3)."""
        if self.a == 0 and self.b == 0:
            return 0
        if self.a >= 0 and self.b >= 0:
            return 1
        if self.a <= 0 and self.b <= 0:
            return -1
        comparison = self.a * self.a - 3 * self.b * self.b
        if self.a > 0:  # a + b sqrt(3), with b < 0
            return 1 if comparison > 0 else -1
        # a < 0 and b > 0
        return 1 if comparison < 0 else -1

    def text(self):
        if self.b == 0:
            return str(self.a)
        if self.a == 0:
            return f"{self.b}*sqrt(3)"
        sign = "+" if self.b > 0 else "-"
        return f"{self.a}{sign}{abs(self.b)}*sqrt(3)"


ZERO = Q3(0)
ONE = Q3(1)
R = Q3(1, 1)  # 1 + sqrt(3)


def dot(p, q):
    return p[0] * q[0] + p[1] * q[1]


def dist2(p, q):
    d = (p[0] - q[0], p[1] - q[1])
    return dot(d, d)


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])


def matrix_rank(a):
    a = [row[:] for row in a]
    if not a:
        return 0
    rows, cols = len(a), len(a[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next((r for r in range(pivot_row, rows) if a[r][col] != ZERO), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        inv = a[pivot_row][col].inverse()
        a[pivot_row] = [x * inv for x in a[pivot_row]]
        for r in range(rows):
            if r == pivot_row or a[r][col] == ZERO:
                continue
            factor = a[r][col]
            a[r] = [x - factor * y for x, y in zip(a[r], a[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


# Angular order.  A_i are the axial square and B_i the diagonal square.
NAMES = ["A0", "B0", "A1", "B1", "A2", "B2", "A3", "B3"]
POINTS = [
    (R, ZERO),
    (ONE, ONE),
    (ZERO, R),
    (-ONE, ONE),
    (-R, ZERO),
    (-ONE, -ONE),
    (ZERO, -R),
    (ONE, -ONE),
]


def edge_gradient(i, j):
    row = [ZERO for _ in range(16)]
    dx = POINTS[i][0] - POINTS[j][0]
    dy = POINTS[i][1] - POINTS[j][1]
    row[2 * i] = 2 * dx
    row[2 * i + 1] = 2 * dy
    row[2 * j] = -2 * dx
    row[2 * j + 1] = -2 * dy
    return row


def main():
    expected = {Q3(4), Q3(8), Q3(8, 4), Q3(16, 8)}
    classes = {}
    dmat = [[ZERO for _ in range(8)] for _ in range(8)]
    for i in range(8):
        for j in range(i + 1, 8):
            d = dist2(POINTS[i], POINTS[j])
            dmat[i][j] = dmat[j][i] = d
            classes.setdefault(d, []).append((i, j))
    assert set(classes) == expected

    local = []
    local_multiplicities = []
    for i in range(8):
        counts = {}
        for j in range(8):
            if i != j:
                counts[dmat[i][j]] = counts.get(dmat[i][j], 0) + 1
        assert len(counts) == 3
        local.append(len(counts))
        local_multiplicities.append(sorted(counts.values()))
    assert local_multiplicities[0::2] == [[1, 2, 4]] * 4
    assert local_multiplicities[1::2] == [[1, 2, 4]] * 4

    # In angular order the cross-products alternate signs, so the octagonal
    # circuit is not strictly convex.  More strongly, all B_i lie strictly
    # inside conv{A_0,...,A_3}, since |x|+|y|=2 < R=1+sqrt(3).
    turn_signs = [cross(POINTS[i], POINTS[(i + 1) % 8], POINTS[(i + 2) % 8]).sign() for i in range(8)]
    assert set(turn_signs) == {-1, 1}
    hull_slack = R - 2
    assert hull_slack.sign() == 1

    # Euclidean distance matrix audit.  The points are centered, so
    # -1/2 J D J must equal the coordinate Gram matrix exactly.
    row_means = [sum(row, ZERO) / 8 for row in dmat]
    grand_mean = sum(row_means, ZERO) / 8
    edm_gram = [
        [-(dmat[i][j] - row_means[i] - row_means[j] + grand_mean) / 2 for j in range(8)]
        for i in range(8)
    ]
    coordinate_gram = [[dot(POINTS[i], POINTS[j]) for j in range(8)] for i in range(8)]
    assert edm_gram == coordinate_gram
    assert matrix_rank(edm_gram) == 2

    # Rigidity audit 1: preserve only equalities between edges in the same
    # distance class.  There are 16 coordinate variables; rank 12 leaves
    # exactly the four similarity motions (2 translations, rotation, scale).
    equality_jacobian = []
    for edges in classes.values():
        base = edge_gradient(*edges[0])
        for edge in edges[1:]:
            grad = edge_gradient(*edge)
            equality_jacobian.append([x - y for x, y in zip(grad, base)])
    equality_rank = matrix_rank(equality_jacobian)
    assert equality_rank == 12

    # The preceding audit is stronger than the local-distance condition when
    # two equal edges never participate in the same vertex palette.  Compute
    # the *minimal* equivalence relation generated only by equal incident
    # edges.  The two axial diameters and two diagonal diameters split into
    # four singleton classes, leaving class sizes 12,12,1,1,1,1.  Crucially,
    # those strictly local constraints alone still have rank 12.
    all_edges = [(i, j) for i in range(8) for j in range(i + 1, 8)]
    parent = {edge: edge for edge in all_edges}

    def find(edge):
        while parent[edge] != edge:
            parent[edge] = parent[parent[edge]]
            edge = parent[edge]
        return edge

    def union(edge1, edge2):
        root1, root2 = find(edge1), find(edge2)
        if root1 != root2:
            parent[root2] = root1

    for vertex in range(8):
        incident_groups = {}
        for other in range(8):
            if vertex == other:
                continue
            edge = tuple(sorted((vertex, other)))
            incident_groups.setdefault(dmat[vertex][other], []).append(edge)
        for edges in incident_groups.values():
            for edge in edges[1:]:
                union(edges[0], edge)
    local_classes = {}
    for edge in all_edges:
        local_classes.setdefault(find(edge), []).append(edge)
    assert sorted(map(len, local_classes.values()), reverse=True) == [12, 12, 1, 1, 1, 1]
    local_jacobian = []
    for edges in local_classes.values():
        base = edge_gradient(*edges[0])
        for edge in edges[1:]:
            grad = edge_gradient(*edge)
            local_jacobian.append([x - y for x, y in zip(grad, base)])
    local_rank = matrix_rank(local_jacobian)
    assert local_rank == 12

    # Rigidity audit 2: introduce one squared-length variable per global class.
    # Rank 16 in 20 variables again leaves exactly four similarity motions.
    ordered_classes = sorted(classes, key=lambda x: float(x.a) + float(x.b) * 3 ** 0.5)
    class_index = {d: k for k, d in enumerate(ordered_classes)}
    augmented_jacobian = []
    for d, edges in classes.items():
        for i, j in edges:
            row = edge_gradient(i, j) + [ZERO] * 4
            row[16 + class_index[d]] = -ONE
            augmented_jacobian.append(row)
    augmented_rank = matrix_rank(augmented_jacobian)
    assert augmented_rank == 16

    # Both local collisions are exactly the same quadratic equation.
    collision = R * R - 2 * R - 2
    assert collision == ZERO

    result = {
        "checker": "dependency-free exact Q(sqrt(3)) arithmetic",
        "coordinates": {name: [x.text(), y.text()] for name, (x, y) in zip(NAMES, POINTS)},
        "global_squared_distance_classes": {
            d.text(): [[NAMES[i], NAMES[j]] for i, j in edges]
            for d, edges in classes.items()
        },
        "local_distance_counts": dict(zip(NAMES, local)),
        "local_class_multiplicities": dict(zip(NAMES, local_multiplicities)),
        "angular_turn_signs": turn_signs,
        "inner_point_hull_slack_R_minus_2": hull_slack.text(),
        "centered_edm_gram_rank": matrix_rank(edm_gram),
        "distance_equality_jacobian_rank": equality_rank,
        "distance_equality_jacobian_nullity": 16 - equality_rank,
        "minimal_local_equivalence_class_sizes": sorted(map(len, local_classes.values()), reverse=True),
        "minimal_local_collision_jacobian_rank": local_rank,
        "minimal_local_collision_jacobian_nullity": 16 - local_rank,
        "augmented_framework_jacobian_rank": augmented_rank,
        "augmented_framework_jacobian_nullity": 20 - augmented_rank,
        "collision_polynomial_at_R": collision.text(),
        "status": "VERIFIED",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
