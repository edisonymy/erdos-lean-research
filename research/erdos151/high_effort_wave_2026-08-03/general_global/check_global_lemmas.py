"""Standard-library replay for GLOBAL_CORE_AND_ERDOS_ROGERS.md.

This checks finite arithmetic and two explicitly bounded local witnesses.  It
does not search for an order-41 counterexample and does not certify the cited
published theorems.
"""

from __future__ import annotations

from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from json import dumps
from math import ceil, comb, floor
from pathlib import Path


HERE = Path(__file__).resolve().parent
ERDOS151 = HERE.parents[1]


def zykov_cliques(parts: int, order: int) -> int:
    """Number of top cliques in the balanced complete `parts`-partite graph."""
    q, r = divmod(order, parts)
    answer = 1
    for _ in range(parts - r):
        answer *= q
    for _ in range(r):
        answer *= q + 1
    return answer


def check_degree_and_maximum_set_caps() -> dict[str, int]:
    out: dict[str, int] = {}
    for n in (40, 41):
        r = 9
        m = n - r - 1
        out[f"degree_cap_rhs_n{n}"] = r * r - 2 * m
        out[f"maximum_set_cap_rhs_n{n}"] = r * r + 3 * r - 2 * n
    assert out == {
        "degree_cap_rhs_n40": 21,
        "maximum_set_cap_rhs_n40": 28,
        "degree_cap_rhs_n41": 19,
        "maximum_set_cap_rhs_n41": 26,
    }
    return out


def check_pure_layers() -> dict[str, dict[str, int]]:
    answer: dict[str, dict[str, int]] = {}
    expected = {
        40: {"K4_lower": 436, "K4_upper": 270,
             "K5_lower": 2612, "K5_upper": 192},
        41: {"K4_lower": 483, "K4_upper": 276,
             "K5_lower": 2974, "K5_upper": 196},
    }
    for n in (40, 41):
        row: dict[str, int] = {}
        for s in (4, 5):
            lower = Fraction(comb(n, s), comb(10, s))
            z = zykov_cliques(s - 1, 9)
            upper = Fraction(n * z, s)
            row[f"K{s}_lower"] = ceil(lower)
            row[f"K{s}_upper"] = floor(upper)
            assert lower > upper
        assert row == expected[n]
        answer[str(n)] = row
    assert zykov_cliques(3, 8) == 18
    assert zykov_cliques(3, 9) == 27
    assert zykov_cliques(4, 9) == 24
    return answer


def check_coverage() -> dict[str, int]:
    n = 41
    total = comb(n, 10)
    k4_max = n * 18 // 4
    k4_unit = comb(n - 4, 6)
    residual = total - k4_max * k4_unit
    edge_unit = comb(n - 2, 8)
    triangle_unit = comb(n - 3, 7)
    assert (total, k4_max, k4_unit) == (1_121_099_408, 184, 2_324_784)
    assert (edge_unit, triangle_unit, residual) == (
        61_523_748, 12_620_256, 693_339_152
    )
    assert ceil(residual / triangle_unit) == 55
    assert ceil(residual / edge_unit) == 12

    # The colex/Kruskal--Katona extremal value for nine graph edges:
    # 9=C(4,2)+C(3,1), hence at most C(4,3)+C(3,2)=7 triangles.
    assert comb(4, 2) + comb(3, 1) == 9
    assert comb(4, 3) + comb(3, 2) == 7
    return {
        "ten_sets": total,
        "K4_max": k4_max,
        "K4_coverage_unit": k4_unit,
        "edge_unit": edge_unit,
        "triangle_unit": triangle_unit,
        "coverage_residual": residual,
        "triangles_if_no_edges": 55,
        "edges_if_no_triangles": 12,
    }


def adjacency(order: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    adj = [set() for _ in range(order)]
    for x, y in edges:
        assert 0 <= x < y < order
        adj[x].add(y)
        adj[y].add(x)
    return adj


def all_cliques(vertices, size: int, adj: list[set[int]]):
    for candidate in combinations(vertices, size):
        if all(y in adj[x] for x, y in combinations(candidate, 2)):
            yield candidate


def support_witness(
    clique: tuple[int, ...], c: int, adj: list[set[int]]
) -> tuple[int, ...] | None:
    """Ambient relaxation of the necessary supported-K4 predicate.

    It replaces every Q-edge and Q-to-M degree by the corresponding ambient
    quantity.  Therefore failure here rigorously implies failure for every
    possible core Q containing the clique.
    """
    clique_set = set(clique)
    outside_neighbours = tuple(sorted(adj[c] - clique_set))
    for size in range(2, min(5, len(outside_neighbours)) + 1):
        for selected in combinations(outside_neighbours, size):
            selected_set = set(selected)
            extra_sum = 0
            locally_supported = True
            for x in selected:
                other_m = len(adj[x] & clique_set) - 1
                within = len(adj[x] & selected_set)
                if within + other_m < 2:
                    locally_supported = False
                    break
                extra_sum += other_m
            if not locally_supported:
                continue
            internal_edges = sum(
                y in adj[x] for x, y in combinations(selected, 2)
            )
            if internal_edges + extra_sum >= size + 1:
                return selected
    return None


def check_k4_minus_edge_falsifier() -> dict[str, object]:
    m = (0, 1, 2, 3)
    fans = tuple(tuple(range(4 + 6 * c, 10 + 6 * c)) for c in range(4))
    order = 28
    edges: set[tuple[int, int]] = {
        tuple(sorted(edge)) for edge in combinations(m, 2)
    }
    chosen_supports = []
    for c, fan in zip(m, fans):
        for x in fan:
            edges.add(tuple(sorted((c, x))))
        selected = fan[:4]
        missing = frozenset(selected[:2])
        for x, y in combinations(selected, 2):
            if frozenset((x, y)) != missing:
                edges.add((x, y))
        chosen_supports.append(selected)

    adj = adjacency(order, edges)
    assert not any(all_cliques(range(order), 5, adj))
    for c, expected in zip(m, chosen_supports):
        witness = support_witness(m, c, adj)
        assert witness is not None
        assert len(witness) == 4
        e_witness = sum(y in adj[x] for x, y in combinations(witness, 2))
        assert e_witness == 5
        assert len(adj[c]) == 9
        triangles_at_c = sum(y in adj[x] for x, y in combinations(adj[c], 2))
        assert triangles_at_c == 8
    return {
        "order_of_local_model": order,
        "omega_at_most": 4,
        "support_sizes": [4, 4, 4, 4],
        "support_edges": [5, 5, 5, 5],
        "M_degrees": [9, 9, 9, 9],
        "M_triangle_counts": [8, 8, 8, 8],
    }


def load_fixed_abstraction():
    path = (
        ERDOS151 / "general" / "checks" / "k4_fibre_attack"
        / "check_k4_fibre_attack.py"
    )
    spec = spec_from_file_location("fixed_k4_fibre_checker", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_fixed_abstraction_support() -> dict[str, object]:
    fixed = load_fixed_abstraction()
    edges, adj = fixed.make_graph()
    cliques = tuple(all_cliques(range(fixed.N), 4, adj))
    assert cliques == (fixed.M,)
    support = {}
    for c in fixed.M:
        witness = support_witness(fixed.M, c, adj)
        support[str(c)] = witness
        assert witness is None

    blue_edges = {
        edge for edge in edges
        if any(edge[0] in fan and edge[1] in fan for fan in fixed.FANS)
    }
    blue_edges.update({(37, 39), (37, 40), (38, 39)})
    triangles = tuple(all_cliques(range(fixed.N), 3, adj))
    for triangle in triangles:
        triangle_edges = {
            tuple(sorted(edge)) for edge in combinations(triangle, 2)
        }
        assert triangle_edges & blue_edges
        assert not triangle_edges <= blue_edges
    assert len(blue_edges) == 25
    return {
        "edge_count": len(edges),
        "triangle_count": len(triangles),
        "K4_count": len(cliques),
        "unique_K4": list(cliques[0]),
        "ambient_support_witnesses": support,
        "good_coloring_blue_edges": len(blue_edges),
        "conclusion": "explicitly certified not (3,3)-arrowing",
    }


def check_aggregate_support_arithmetic() -> dict[str, int]:
    maximum_a = -1
    maximizer = None
    for n2 in range(7):
        for n3 in range(3):
            if 2 * n2 + 5 * n3 <= 12:
                value = n2 + 3 * n3
                if value > maximum_a:
                    maximum_a = value
                    maximizer = (n2, n3)
    assert maximum_a == 7
    assert maximizer == (1, 2)

    # Four disjoint singleton K4-e supports.
    w = 4 * 4
    a = 0
    b = 4 * 5
    assert 2 * a + b >= w + 4
    assert a + b >= w
    return {"A_max": maximum_a, "A_max_n2": 1, "A_max_n3": 2,
            "toy_W": w, "toy_A": a, "toy_B": b}


def main() -> None:
    result = {
        "status": "PASS",
        "degree_and_set_caps": check_degree_and_maximum_set_caps(),
        "pure_layers": check_pure_layers(),
        "coverage": check_coverage(),
        "aggregate_support": check_aggregate_support_arithmetic(),
        "K4_minus_edge_falsifier": check_k4_minus_edge_falsifier(),
        "fixed_abstraction": check_fixed_abstraction_support(),
        "claim_boundary": (
            "finite arithmetic and bounded witnesses only; no order-41 "
            "counterexample search and no certification of cited theorems"
        ),
    }
    print(dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
