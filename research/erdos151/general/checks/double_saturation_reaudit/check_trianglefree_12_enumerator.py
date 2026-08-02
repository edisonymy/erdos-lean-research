"""Independent exact enumerator for the sparse triangle-free core lemma.

This checker does not import or call the supplied component-profile checker.
It uses NetworkX only to generate one representative of each unlabelled
tree.  Its own bitset routines add one or two nonedges and compute triangle
counts and independence numbers exactly.

Completeness is elementary.  Deleting one edge outside a spanning tree from
any connected unicyclic graph produces a tree; deleting two does the same
for any connected bicyclic graph.  Thus adding all one- or two-nonedge sets
to every unlabelled tree representative covers every connected graph of
cyclomatic number one or two, possibly more than once.
"""

from __future__ import annotations

from itertools import combinations
import hashlib
import json
from pathlib import Path

import networkx as nx


N = 12
CATALOGUE_PATH = Path("experiments/erdos128/r36_17.g6")


def adjacency_from_edges(order, edges):
    adjacency = [0] * order
    for left, right in edges:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
    return adjacency


def exact_alpha(adjacency):
    order = len(adjacency)
    best = 0
    for subset in range(1 << order):
        if subset.bit_count() <= best:
            continue
        remaining = subset
        independent = True
        while remaining:
            bit = remaining & -remaining
            vertex = bit.bit_length() - 1
            remaining ^= bit
            if adjacency[vertex] & remaining:
                independent = False
                break
        if independent:
            best = subset.bit_count()
    return best


def is_triangle_free(adjacency):
    for vertex, neighbours in enumerate(adjacency):
        remaining = neighbours & ~((1 << (vertex + 1)) - 1)
        while remaining:
            bit = remaining & -remaining
            other = bit.bit_length() - 1
            remaining ^= bit
            if adjacency[vertex] & adjacency[other]:
                return False
    return True


def degree_sequence(adjacency):
    return tuple(sorted(mask.bit_count() for mask in adjacency))


def decode_short_graph6(record):
    """Decode short-form graph6 without using NetworkX's graph6 parser."""
    values = [ord(character) - 63 for character in record.strip()]
    assert values and 0 <= values[0] <= 62
    order = values[0]
    bits = []
    for value in values[1:]:
        assert 0 <= value <= 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    required = order * (order - 1) // 2
    assert len(bits) >= required
    assert all(bit == 0 for bit in bits[required:])
    edges = []
    cursor = 0
    for right in range(1, order):
        for left in range(right):
            if bits[cursor]:
                edges.append((left, right))
            cursor += 1
    return adjacency_from_edges(order, edges)


def catalogue_local_check():
    payload = CATALOGUE_PATH.read_bytes()
    records = [line for line in payload.decode("ascii").splitlines() if line]
    invariants = []
    for record in records:
        adjacency = decode_short_graph6(record)
        invariants.append({
            "order": len(adjacency),
            "edges": sum(mask.bit_count() for mask in adjacency) // 2,
            "triangle_free": is_triangle_free(adjacency),
            "alpha": exact_alpha(adjacency),
            "minimum_degree": min(mask.bit_count() for mask in adjacency),
        })
    edge_histogram = {
        edge_count: sum(item["edges"] == edge_count for item in invariants)
        for edge_count in sorted({item["edges"] for item in invariants})
    }
    assert hashlib.sha256(payload).hexdigest() == (
        "3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361"
    )
    assert len(records) == 7
    assert all(item["order"] == 17 for item in invariants)
    assert all(item["triangle_free"] for item in invariants)
    assert all(item["alpha"] <= 5 for item in invariants)
    assert all(item["minimum_degree"] >= 4 for item in invariants)
    assert edge_histogram == {40: 2, 41: 3, 42: 2}
    return {
        "path": str(CATALOGUE_PATH).replace("\\", "/"),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "records": len(records),
        "edge_histogram": edge_histogram,
        "minimum_degrees": [item["minimum_degree"] for item in invariants],
        "alphas": [item["alpha"] for item in invariants],
        "all_triangle_free": True,
        "external_completeness_checked": False,
    }


def tree_edge_sets(order):
    if order == 1:
        yield frozenset()
        return
    for graph in nx.generators.nonisomorphic_trees(order):
        yield frozenset(tuple(sorted(edge)) for edge in graph.edges())


def connected_rank_candidates(order, rank):
    """Generate every connected rank-1/rank-2 graph up to isomorphism cover.

    The output can contain isomorphic and even identically labelled repeats;
    this is intentional and harmless for an exhaustive counterexample hunt.
    """
    assert rank in (1, 2)
    all_edges = frozenset(combinations(range(order), 2))
    for tree_edges in tree_edge_sets(order):
        nonedges = sorted(all_edges - tree_edges)
        for additions in combinations(nonedges, rank):
            yield tree_edges | frozenset(additions)


def tree_minima():
    result = {}
    for order in range(1, N + 1):
        alphas = []
        count = 0
        for edges in tree_edge_sets(order):
            count += 1
            alphas.append(exact_alpha(adjacency_from_edges(order, edges)))
        result[order] = {
            "unlabelled_trees": count,
            "minimum_alpha": min(alphas),
        }
        assert result[order]["minimum_alpha"] == (order + 1) // 2
    return result


def ranked_connected_stats(max_order, rank):
    result = {}
    for order in range(1, max_order + 1):
        raw = 0
        triangle_free = 0
        minimum_alpha = None
        minimum_degree_sequences = set()
        if order >= rank + 2:
            for edges in connected_rank_candidates(order, rank):
                raw += 1
                adjacency = adjacency_from_edges(order, edges)
                if not is_triangle_free(adjacency):
                    continue
                triangle_free += 1
                alpha = exact_alpha(adjacency)
                if minimum_alpha is None or alpha < minimum_alpha:
                    minimum_alpha = alpha
                    minimum_degree_sequences = {degree_sequence(adjacency)}
                elif alpha == minimum_alpha:
                    minimum_degree_sequences.add(degree_sequence(adjacency))
        result[order] = {
            "raw_spanning_tree_extensions": raw,
            "triangle_free_extensions": triangle_free,
            "minimum_alpha": minimum_alpha,
            "degree_sequences_at_minimum_alpha": [
                list(sequence) for sequence in sorted(minimum_degree_sequences)
            ],
        }
    return result


def verify_r33_upper():
    """Brute force every labelled six-vertex graph for R(3,3)<=6."""
    edges = tuple(combinations(range(6), 2))
    triangle_free = 0
    counterexamples = 0
    for mask in range(1 << len(edges)):
        chosen = [edge for index, edge in enumerate(edges) if (mask >> index) & 1]
        adjacency = adjacency_from_edges(6, chosen)
        if not is_triangle_free(adjacency):
            continue
        triangle_free += 1
        if exact_alpha(adjacency) <= 2:
            counterexamples += 1
    assert counterexamples == 0
    return {
        "labelled_graphs": 1 << len(edges),
        "triangle_free_labelled_graphs": triangle_free,
        "triangle_free_graphs_with_alpha_at_most_2": counterexamples,
    }


def compositions(total, parts, minimum=1):
    if parts == 1:
        if total >= minimum:
            yield (total,)
        return
    for first in range(minimum, total - minimum * (parts - 1) + 1):
        for rest in compositions(total - first, parts - 1, minimum):
            yield (first,) + rest


def lower_bound_profiles(tree, unicyclic):
    """Exhaust every component/cycle-rank profile possible with e<=10."""
    bad = []
    checked = 0

    # k=2 forces a forest: e >= n-k=10, hence e<=10 has rank zero.
    for orders in compositions(N, 2):
        checked += 1
        lower = sum(tree[order]["minimum_alpha"] for order in orders)
        if lower <= 5:
            bad.append({"orders": orders, "ranks": (0, 0), "alpha": lower})

    # k=3 has total rank at most one: a forest or one unicyclic component.
    for orders in compositions(N, 3):
        checked += 1
        lower = sum(tree[order]["minimum_alpha"] for order in orders)
        if lower <= 5:
            bad.append({"orders": orders, "ranks": (0, 0, 0), "alpha": lower})
        for cyclic_position in range(3):
            cycle_order = orders[cyclic_position]
            cycle_minimum = unicyclic[cycle_order]["minimum_alpha"]
            if cycle_minimum is None:
                continue
            checked += 1
            lower = cycle_minimum + sum(
                tree[order]["minimum_alpha"]
                for index, order in enumerate(orders)
                if index != cyclic_position
            )
            if lower <= 5:
                bad.append({
                    "orders": orders,
                    "ranks": tuple(1 if index == cyclic_position else 0
                                   for index in range(3)),
                    "alpha": lower,
                })
    assert bad == []
    return {"profiles_checked": checked, "profiles_with_alpha_at_most_5": bad}


def equality_profiles(tree, unicyclic, bicyclic):
    """Exhaust component/cycle-rank profiles possible at e=11."""
    survivors = []
    checked = 0

    # k=1 is a tree and k=2 has ranks (1,0).
    assert tree[N]["minimum_alpha"] >= 6
    for orders in compositions(N, 2):
        for cyclic_position in range(2):
            cycle_order = orders[cyclic_position]
            cycle_minimum = unicyclic[cycle_order]["minimum_alpha"]
            if cycle_minimum is None:
                continue
            checked += 1
            tree_order = orders[1 - cyclic_position]
            lower = cycle_minimum + tree[tree_order]["minimum_alpha"]
            if lower <= 5:
                survivors.append({"orders": orders, "ranks": (1, 0), "alpha": lower})

    # k=3 has total rank two: either (2,0,0) or (1,1,0).
    for orders in compositions(N, 3):
        for cyclic_position in range(3):
            cycle_order = orders[cyclic_position]
            cycle_minimum = bicyclic[cycle_order]["minimum_alpha"]
            if cycle_minimum is None:
                continue
            checked += 1
            lower = cycle_minimum + sum(
                tree[order]["minimum_alpha"]
                for index, order in enumerate(orders)
                if index != cyclic_position
            )
            if lower <= 5:
                survivors.append({
                    "orders": orders,
                    "ranks": tuple(2 if index == cyclic_position else 0
                                   for index in range(3)),
                    "alpha": lower,
                })

        for tree_position in range(3):
            cycle_positions = [index for index in range(3) if index != tree_position]
            cycle_minima = [unicyclic[orders[index]]["minimum_alpha"]
                            for index in cycle_positions]
            if any(value is None for value in cycle_minima):
                continue
            checked += 1
            lower = tree[orders[tree_position]]["minimum_alpha"] + sum(cycle_minima)
            if lower <= 5:
                survivors.append({
                    "orders": orders,
                    "ranks": tuple(0 if index == tree_position else 1
                                   for index in range(3)),
                    "alpha": lower,
                })

    normalized = {
        (tuple(sorted(item["orders"])), tuple(sorted(item["ranks"])), item["alpha"])
        for item in survivors
    }
    assert normalized == {((2, 5, 5), (0, 1, 1), 5)}

    # At order five, every triangle-free unicyclic minimum-alpha extension
    # has degree sequence (2,2,2,2,2), hence is C5.  The order-two tree is K2.
    assert unicyclic[5]["minimum_alpha"] == 2
    assert unicyclic[5]["degree_sequences_at_minimum_alpha"] == [[2, 2, 2, 2, 2]]
    assert tree[2] == {"unlabelled_trees": 1, "minimum_alpha": 1}

    return {
        "profiles_checked": checked,
        "normalized_survivors": [
            {"component_orders": [2, 5, 5], "cycle_ranks": [0, 1, 1], "alpha": 5}
        ],
        "survivor_isomorphism_type": "K2 disjoint-union C5 disjoint-union C5",
    }


def main():
    r33 = verify_r33_upper()
    catalogue = catalogue_local_check()
    tree = tree_minima()
    unicyclic = ranked_connected_stats(N - 1, 1)
    bicyclic = ranked_connected_stats(N - 2, 2)
    sparse = lower_bound_profiles(tree, unicyclic)
    equality = equality_profiles(tree, unicyclic, bicyclic)

    report = {
        "status": "VERIFIED",
        "scope": "independent exhaustive spanning-tree extension audit of the triangle-free n=12 alpha<=5 edge minimum and equality case",
        "networkx_version": nx.__version__,
        "pinned_catalogue_local_check": catalogue,
        "r33_labelled_check": r33,
        "tree_minima": tree,
        "unicyclic_stats": unicyclic,
        "bicyclic_stats": bicyclic,
        "edge_at_most_10_component_profiles": sparse,
        "edge_equal_11_component_profiles": equality,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
