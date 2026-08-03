#!/usr/bin/env python3
"""Definition-level sanity checks for the global threshold-seven closure.

The analytic proof is in REPORT.md.  This script checks the finite algebraic
and coloring endpoints without graph libraries:

* the only loopless 4-regular multigraph on three vertices is the doubled
  triangle;
* its (simple) line graph is K6;
* the odd-set density inequality used for sets of size at least five;
* the red C5 / blue complementary C5 coloring of K5 has no monochromatic
  triangle, and its pullback along every proper coloring of every graph on at
  most five vertices is safe.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def k5_edge_color(a: int, b: int) -> int:
    """0 on a fixed C5, 1 on its complement."""
    if a > b:
        a, b = b, a
    red = {tuple(sorted(e)) for e in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 0))}
    return 0 if (a, b) in red else 1


def main() -> None:
    # A loopless multigraph on vertices {0,1,2} is determined by three
    # multiplicities.  Solve the degree-four equations by finite enumeration.
    roots = []
    for m01, m02, m12 in itertools.product(range(5), repeat=3):
        if m01 + m02 == m01 + m12 == m02 + m12 == 4:
            roots.append((m01, m02, m12))
    assert roots == [(2, 2, 2)]

    # The six edges of the doubled triangle are pairwise incident, so its
    # simple line graph is K6.
    root_edges = [(0, 1)] * 2 + [(0, 2)] * 2 + [(1, 2)] * 2
    line_edges = []
    for i, j in itertools.combinations(range(6), 2):
        if set(root_edges[i]) & set(root_edges[j]):
            line_edges.append((i, j))
    assert len(line_edges) == 15

    density_table = []
    for s in range(5, 102, 2):
        ratio = 4 * s / (s - 1)
        assert ratio <= 5
        density_table.append({"odd_set_size": s, "upper_bound": ratio})

    k5_triangles = []
    for tri in itertools.combinations(range(5), 3):
        colors = [k5_edge_color(a, b) for a, b in itertools.combinations(tri, 2)]
        assert len(set(colors)) == 2
        k5_triangles.append({"vertices": tri, "edge_colors": colors})

    # Exhaust every graph on at most five vertices and every proper map to K5.
    # Whenever a triangle is present, its image uses three distinct colors and
    # the pulled-back K5 edge-coloring is nonmonochromatic.
    pullback_instances = 0
    for n in range(1, 6):
        possible = tuple(itertools.combinations(range(n), 2))
        for mask in range(1 << len(possible)):
            edges = tuple(e for i, e in enumerate(possible) if (mask >> i) & 1)
            eset = set(edges)
            triangles = [
                tri
                for tri in itertools.combinations(range(n), 3)
                if all(tuple(sorted(e)) in eset for e in itertools.combinations(tri, 2))
            ]
            for phi in itertools.product(range(5), repeat=n):
                if any(phi[a] == phi[b] for a, b in edges):
                    continue
                pullback_instances += 1
                for tri in triangles:
                    colors = [
                        k5_edge_color(phi[a], phi[b])
                        for a, b in itertools.combinations(tri, 2)
                    ]
                    assert len(set(colors)) == 2

    result = {
        "status": "VERIFIED",
        "three_vertex_four_regular_roots": roots,
        "doubled_triangle_line_graph_order": 6,
        "doubled_triangle_line_graph_edges": len(line_edges),
        "doubled_triangle_line_graph_is_K6": len(line_edges) == 15,
        "odd_density_formula": "2e(S) <= 4|S| <= 5(|S|-1) for odd |S|>=5",
        "density_table": density_table,
        "k5_triangle_checks": k5_triangles,
        "proper_pullback_instances_through_order_5": pullback_instances,
    }
    out = HERE / "independent_global_audit.result.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"result_sha256={sha256(out)}")


if __name__ == "__main__":
    main()
