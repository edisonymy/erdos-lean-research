#!/usr/bin/env python3
"""Independent SymPy audit of H8, including exact Jacobian and EDM ranks."""

from __future__ import annotations

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".deps"))

import sympy as sp


def main():
    r = 1 + sp.sqrt(3)
    pts = [
        (r, 0), (1, 1), (0, r), (-1, 1),
        (-r, 0), (-1, -1), (0, -r), (1, -1),
    ]
    names = ["A0", "B0", "A1", "B1", "A2", "B2", "A3", "B3"]
    d = sp.zeros(8)
    classes = {}
    for i in range(8):
        for j in range(i + 1, 8):
            dij = sp.expand((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2)
            d[i, j] = d[j, i] = dij
            classes.setdefault(dij, []).append((i, j))
    assert set(classes) == {sp.Integer(4), sp.Integer(8), 8 + 4 * sp.sqrt(3), 16 + 8 * sp.sqrt(3)}
    local = [len({d[i, j] for j in range(8) if i != j}) for i in range(8)]
    assert local == [3] * 8

    # EDM criterion and embedding rank.
    J = sp.eye(8) - sp.ones(8) / 8
    gram = sp.simplify(-sp.Rational(1, 2) * J * d * J)
    X = sp.Matrix(pts)
    assert sp.simplify(gram - X * X.T) == sp.zeros(8)
    assert gram.rank() == 2

    # Generate all equality constraints independently and differentiate before
    # substituting H8.  Rank 12 is the maximum compatible with similarities.
    variables = sp.symbols("x0:8 y0:8")
    xs, ys = variables[:8], variables[8:]

    def sqdist(i, j):
        return (xs[i] - xs[j]) ** 2 + (ys[i] - ys[j]) ** 2

    equality_eqs = []
    for edges in classes.values():
        i0, j0 = edges[0]
        for i, j in edges[1:]:
            equality_eqs.append(sqdist(i, j) - sqdist(i0, j0))
    substitution = {xs[i]: pts[i][0] for i in range(8)} | {ys[i]: pts[i][1] for i in range(8)}
    equality_jac = sp.Matrix(equality_eqs).jacobian(variables).subs(substitution)
    equality_rank = equality_jac.rank()
    assert equality_rank == 12

    # Independently generate the equivalence closure forced only by equal
    # distances at a common vertex.  Equal singleton diameters at disjoint
    # vertices are deliberately not identified.
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
        incident = {}
        for other in range(8):
            if vertex == other:
                continue
            edge = tuple(sorted((vertex, other)))
            incident.setdefault(d[vertex, other], []).append(edge)
        for edges in incident.values():
            for edge in edges[1:]:
                union(edges[0], edge)
    local_classes = {}
    for edge in all_edges:
        local_classes.setdefault(find(edge), []).append(edge)
    local_eqs = []
    for edges in local_classes.values():
        i0, j0 = edges[0]
        for i, j in edges[1:]:
            local_eqs.append(sqdist(i, j) - sqdist(i0, j0))
    local_jac = sp.Matrix(local_eqs).jacobian(variables).subs(substitution)
    local_rank = local_jac.rank()
    assert sorted(map(len, local_classes.values()), reverse=True) == [12, 12, 1, 1, 1, 1]
    assert local_rank == 12

    length_variables = sp.symbols("L0:4")
    ordered = sorted(classes, key=lambda z: float(z.evalf()))
    augmented_eqs = []
    for k, value in enumerate(ordered):
        for i, j in classes[value]:
            augmented_eqs.append(sqdist(i, j) - length_variables[k])
    augmented_vars = variables + length_variables
    augmented_sub = substitution | {length_variables[k]: ordered[k] for k in range(4)}
    augmented_jac = sp.Matrix(augmented_eqs).jacobian(augmented_vars).subs(augmented_sub)
    augmented_rank = augmented_jac.rank()
    assert augmented_rank == 16

    # Exact convexity failure: each diagonal-square vertex has l1 norm 2,
    # strictly below the axial diamond radius 1+sqrt(3).
    hull_slack = sp.simplify(r - 2)
    assert hull_slack.is_positive
    turns = []
    for i in range(8):
        a, b, c = pts[i], pts[(i + 1) % 8], pts[(i + 2) % 8]
        turn = sp.expand((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]))
        turns.append(sp.signsimp(turn))
    assert any(t.is_positive for t in turns) and any(t.is_negative for t in turns)

    result = {
        "checker": f"SymPy {sp.__version__}",
        "global_squared_distances": [str(v) for v in ordered],
        "global_class_sizes": [len(classes[v]) for v in ordered],
        "local_distance_counts": dict(zip(names, local)),
        "centered_edm_gram_rank": gram.rank(),
        "distance_equality_jacobian_rank": equality_rank,
        "distance_equality_jacobian_nullity": 16 - equality_rank,
        "minimal_local_equivalence_class_sizes": sorted(map(len, local_classes.values()), reverse=True),
        "minimal_local_collision_jacobian_rank": local_rank,
        "minimal_local_collision_jacobian_nullity": 16 - local_rank,
        "augmented_framework_jacobian_rank": augmented_rank,
        "augmented_framework_jacobian_nullity": 20 - augmented_rank,
        "inner_point_hull_slack": str(hull_slack),
        "angular_turns": [str(t) for t in turns],
        "status": "VERIFIED",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
