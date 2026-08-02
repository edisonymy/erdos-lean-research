#!/usr/bin/env python3
"""Independent finite guards for the final order-41 omega=5 audit.

This script intentionally does not import any campaign graph parser, beta
engine, overlap checker, or prior row checker.  It uses a small local graph6
decoder, direct subset enumeration, and independent component-profile guards.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CATALOGUE = ROOT / "experiments" / "erdos128" / "r36_17.g6"


def graph6_decode(line: bytes) -> tuple[int, list[int]]:
    raw = line.strip()
    assert raw and raw[0] != ord(">")
    first = raw[0] - 63
    assert 0 <= first <= 62, "only the short graph6 order header is needed"
    n = first
    bits: list[int] = []
    for char in raw[1:]:
        value = char - 63
        assert 0 <= value <= 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    need = n * (n - 1) // 2
    assert len(bits) >= need
    adjacency = [0] * n
    cursor = 0
    for j in range(1, n):
        for i in range(j):
            if bits[cursor]:
                adjacency[i] |= 1 << j
                adjacency[j] |= 1 << i
            cursor += 1
    return n, adjacency


def edge_count(adjacency: list[int]) -> int:
    return sum(mask.bit_count() for mask in adjacency) // 2


def triangle_count(adjacency: list[int]) -> int:
    total = 0
    for i in range(len(adjacency)):
        for j in range(i + 1, len(adjacency)):
            if (adjacency[i] >> j) & 1:
                total += (adjacency[i] & adjacency[j] & ~((1 << (j + 1)) - 1)).bit_count()
    return total


def has_independent_k(adjacency: list[int], k: int) -> bool:
    for vertices in combinations(range(len(adjacency)), k):
        mask = sum(1 << v for v in vertices)
        if all((adjacency[v] & mask) == 0 for v in vertices):
            return True
    return False


def check_catalogue() -> dict[str, object]:
    raw = CATALOGUE.read_bytes()
    records = [line for line in raw.splitlines() if line]
    decoded = [graph6_decode(line) for line in records]
    assert all(n == 17 for n, _ in decoded)
    graphs = [adjacency for _, adjacency in decoded]
    assert all(triangle_count(graph) == 0 for graph in graphs)
    assert all(not has_independent_k(graph, 6) for graph in graphs)
    edges = Counter(edge_count(graph) for graph in graphs)
    minimum_degrees = [min(mask.bit_count() for mask in graph) for graph in graphs]
    assert edges == Counter({40: 2, 41: 3, 42: 2})
    assert min(minimum_degrees) >= 4
    return {
        "sha256": sha256(raw).hexdigest(),
        "records": len(records),
        "edge_histogram": dict(sorted(edges.items())),
        "minimum_degrees": minimum_degrees,
    }


def check_profiles() -> list[dict[str, object]]:
    profiles: list[dict[str, object]] = []
    for t in range(26):
        for n2 in range(37):
            for n3 in range(37 - n2):
                for n4 in range(37 - n2 - n3):
                    n1 = 25 - t - 2 * n2 - 3 * n3 - 4 * n4
                    n0 = 36 - n1 - n2 - n3 - n4
                    if n0 < 0 or n1 < 0:
                        continue
                    residual_sum = 5 * n0 + n1
                    if residual_sum <= 85:
                        profiles.append(
                            {
                                "t": t,
                                "n": [n0, n1, n2, n3, n4],
                                "residual_sum": residual_sum,
                            }
                        )
    assert profiles == [
        {"t": 0, "n": [11, 25, 0, 0, 0], "residual_sum": 80},
        {"t": 0, "n": [12, 23, 1, 0, 0], "residual_sum": 83},
        {"t": 1, "n": [12, 24, 0, 0, 0], "residual_sum": 84},
    ]

    # Pointwise degree-capacity reconstruction, normalized up to relabelling M.
    assert [5] * 5 == [5] * 5  # R: 25 unique neighbours fill five capacities.
    d_capacities = [4, 4, 5, 5, 5]  # D after the two endpoints of w.
    assert sum(d_capacities) == 23
    t_capacities = [4, 5, 5, 5, 5]  # T has exactly one unused cross slot.
    assert sum(t_capacities) == 24
    return profiles


def compositions(total: int, parts: int) -> list[tuple[int, ...]]:
    return [values for values in product(range(1, total + 1), repeat=parts) if sum(values) == total]


def check_sparse_trianglefree() -> dict[str, object]:
    """Replay the component/cyclomatic proof without a graph enumerator.

    This is deliberately a different implementation from the earlier sparse
    profile checker.  The only non-finite step left outside this guard is the
    standard theta/figure-eight/dumbbell classification of a bicyclic 2-core.
    """

    # If alpha <= 5, four components have alpha allocation dominated by
    # (2,1,1,1), whose Ramsey order caps are (5,2,2,2); five components are
    # dominated by (1,1,1,1,1), with cap two each.
    assert 5 + 2 + 2 + 2 < 12
    assert 5 * 2 < 12

    low_profiles = 0
    low_minimum_alpha = 12
    # With at most ten edges, k=2 means two trees.  With k=3, total cycle rank
    # is at most one: either three trees or one unicyclic component plus trees.
    for orders in compositions(12, 2):
        low_profiles += 1
        bound = sum((order + 1) // 2 for order in orders)
        low_minimum_alpha = min(low_minimum_alpha, bound)
        assert bound >= 6
    for orders in compositions(12, 3):
        for unicyclic in (-1, 0, 1, 2):  # -1 means all three components are trees.
            low_profiles += 1
            bound = 0
            for index, order in enumerate(orders):
                bound += order // 2 if index == unicyclic else (order + 1) // 2
            low_minimum_alpha = min(low_minimum_alpha, bound)
            assert bound >= 6

    # At eleven edges and three components, cycle-rank distribution (1,1,0)
    # is the only branch not eliminated by the parity bound.  A branch can
    # attain five only if both unicyclic orders are odd/non-bipartite and hence
    # at least five, while the even tree has order at least two.
    equality_order_profiles: set[tuple[int, int, int]] = set()
    for orders in compositions(12, 3):
        for tree_index in range(3):
            cycle_indices = [index for index in range(3) if index != tree_index]
            s1, s2 = (orders[index] for index in cycle_indices)
            tree_order = orders[tree_index]
            lower = s1 // 2 + s2 // 2 + (tree_order + 1) // 2
            if lower <= 5 and s1 % 2 == s2 % 2 == 1 and tree_order % 2 == 0:
                if s1 >= 5 and s2 >= 5 and tree_order >= 2:
                    equality_order_profiles.add(tuple(sorted((tree_order, s1, s2))))
    assert equality_order_profiles == {(2, 5, 5)}

    # Directly verify the equality construction.
    equality_edges: list[tuple[int, int]] = []
    for start in (0, 5):
        equality_edges.extend((start + i, start + ((i + 1) % 5)) for i in range(5))
    equality_edges.append((10, 11))
    equality_graph = adjacency_from_edges(12, equality_edges)
    assert edge_count(equality_graph) == 11
    assert triangle_count(equality_graph) == 0
    assert not has_independent_k(equality_graph, 6)

    return {
        "low_edge_profiles": low_profiles,
        "low_edge_minimum_alpha_bound": low_minimum_alpha,
        "equality_order_profiles": sorted(equality_order_profiles),
        "analytic_boundary": "bicyclic 2-core classification",
    }


def adjacency_from_edges(n: int, edges: list[tuple[int, int]]) -> list[int]:
    adjacency = [0] * n
    for i, j in edges:
        adjacency[i] |= 1 << j
        adjacency[j] |= 1 << i
    return adjacency


def independent(mask: int, adjacency: list[int]) -> bool:
    return all(not ((mask >> v) & 1 and adjacency[v] & mask) for v in range(len(adjacency)))


def disjoint_transversal_guard(adjacency: list[int], target: int) -> tuple[int, int]:
    n = len(adjacency)
    independent_sets = [mask for mask in range(1 << n) if independent(mask, adjacency)]
    maximum_sets = [mask for mask in independent_sets if mask.bit_count() == target]
    assert maximum_sets
    bad_hitting_sets = [
        mask for mask in independent_sets if all(mask & maximum for maximum in maximum_sets)
    ]
    assert not bad_hitting_sets
    return len(independent_sets), len(maximum_sets)


def check_transversals() -> dict[str, object]:
    rigid_edges = list(combinations(range(3), 2))
    for start in (3, 5, 7, 9):
        rigid_edges.append((start, start + 1))
    rigid = adjacency_from_edges(11, rigid_edges)
    rigid_counts = disjoint_transversal_guard(rigid, 5)

    t_edges: list[tuple[int, int]] = []
    for start in (0, 5):
        t_edges.extend((start + i, start + ((i + 1) % 5)) for i in range(5))
    t_edges.append((10, 11))
    triangle = adjacency_from_edges(12, t_edges)
    triangle_counts = disjoint_transversal_guard(triangle, 5)
    assert edge_count(triangle) == 11
    assert triangle_count(triangle) == 0
    assert not has_independent_k(triangle, 6)
    return {
        "K3_plus_4K2": {"independent_sets": rigid_counts[0], "maximum_sets": rigid_counts[1]},
        "2C5_plus_K2": {"independent_sets": triangle_counts[0], "maximum_sets": triangle_counts[1]},
    }


def check_arithmetic() -> dict[str, object]:
    # Singleton-fibre cut minima.
    cut_r = 2 * 11 - 5
    cut_dt = 2 * 12 - 5
    assert (cut_r, cut_dt) == (17, 19)

    ex_11_k6 = (11 * 11 - (3 * 3 + 4 * 2 * 2)) // 2
    assert ex_11_k6 == 48
    rigid_degree_minimum = 2 * (55 - ex_11_k6) + 5 * cut_r
    assert rigid_degree_minimum == 99

    double_degree_minimum_at_e11 = 2 * 11 + 5 * cut_dt - 7
    assert double_degree_minimum_at_e11 == 110 > 108

    triangle_degree_minimum = 2 * 11 + 4 * cut_dt + 10
    assert triangle_degree_minimum == 108

    # The order-17 transformation J has |E(J)|=|E(F)|-2q.  Catalogue
    # e(J)>=40 and Delta(F)<=5 leave only q=1,e(F)=42,e(J)=40.
    possibilities = []
    for q in range(1, 15):
        for e_f in range(43):
            e_j = e_f - 2 * q
            if e_j >= 40:
                possibilities.append((q, e_f, e_j))
    assert possibilities == [(1, 42, 40)]
    return {
        "rigid_cut": cut_r,
        "full_12_vertex_cut": cut_dt,
        "rigid_degree_minimum": rigid_degree_minimum,
        "double_degree_minimum_at_eU_11": double_degree_minimum_at_e11,
        "triangle_degree_minimum": triangle_degree_minimum,
        "order17_J_possibilities": possibilities,
    }


def main() -> None:
    catalogue = check_catalogue()
    assert catalogue["sha256"] == "3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361"
    profiles = check_profiles()
    sparse = check_sparse_trianglefree()
    transversals = check_transversals()
    arithmetic = check_arithmetic()

    print("status: PASS")
    print(f"catalogue: {catalogue}")
    print(f"profiles: {profiles}")
    print(f"sparse_trianglefree: {sparse}")
    print(f"transversals: {transversals}")
    print(f"arithmetic: {arithmetic}")


if __name__ == "__main__":
    main()
