"""Standard-library guard for the 12-vertex triangle-free core lemma.

This exhausts the component-order, cyclomatic-number, and parity profiles
used by the analytic proof in ORDER41_K5_DOUBLE_SATURATION.md.  It also
checks the equality construction C5 + C5 + K2 directly.  It is deliberately
not an enumeration of all graphs on twelve vertices.
"""

from itertools import combinations, product


N = 12


def positive_compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in positive_compositions(total - first, parts - 1):
            yield (first,) + rest


def nonnegative_compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in nonnegative_compositions(total - first, parts - 1):
            yield (first,) + rest


def alpha_allocations(parts, budget=5):
    for total in range(parts, budget + 1):
        yield from positive_compositions(total, parts)


def tree_alpha_floor(order):
    return (order + 1) // 2


def unicyclic_alpha_floor(order):
    return order // 2


def profile_lower_alpha(orders, cycle_ranks):
    lower = 0
    for order, rank in zip(orders, cycle_ranks):
        if rank == 0:
            lower += tree_alpha_floor(order)
        elif rank == 1:
            if order < 4:  # a triangle-free unicyclic component has >=4 vertices
                return None
            lower += unicyclic_alpha_floor(order)
        else:
            raise ValueError("rank >=2 is handled by the bicyclic dichotomy")
    return lower


def max_vertices_with_many_components(parts):
    # Only alpha 1 and 2 occur for parts >=4 under total alpha <=5.
    # Triangle-free graphs with alpha <=1 have at most 2 vertices; with
    # alpha <=2 they have at most 5 vertices (R(3,3)=6).
    order_cap = {1: 2, 2: 5}
    return max(
        sum(order_cap[value] for value in allocation)
        for allocation in alpha_allocations(parts)
    )


def graph_invariants(adjacency):
    order = len(adjacency)
    edges = sum(mask.bit_count() for mask in adjacency) // 2
    triangles = 0
    for a, b, c in combinations(range(order), 3):
        if ((adjacency[a] >> b) & 1
                and (adjacency[a] >> c) & 1
                and (adjacency[b] >> c) & 1):
            triangles += 1
    alpha = 0
    for subset in range(1 << order):
        if subset.bit_count() <= alpha:
            continue
        remaining = subset
        independent = True
        while remaining:
            bit = remaining & -remaining
            vertex = bit.bit_length() - 1
            remaining -= bit
            if adjacency[vertex] & remaining:
                independent = False
                break
        if independent:
            alpha = subset.bit_count()
    return order, edges, triangles, alpha


def equality_graph():
    adjacency = [0] * N

    def add_edge(left, right):
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left

    for offset in (0, 5):
        for vertex in range(5):
            add_edge(offset + vertex, offset + (vertex + 1) % 5)
    add_edge(10, 11)
    return adjacency


def main():
    assert max_vertices_with_many_components(4) == 11
    assert max_vertices_with_many_components(5) == 10

    # If m<=10 and k components, total cyclomatic number is at most
    # 10-(12-k).  The k=1 bound is negative; k=2 gives forests; k=3 gives
    # forests or exactly one unicyclic component.  Exhaust every order and
    # placement profile and verify alpha >=6.
    sparse_profiles = 0
    sparse_bad_profiles = []
    for components in (1, 2, 3):
        max_cycle_rank = 10 - (N - components)
        if max_cycle_rank < 0:
            continue
        for total_rank in range(max_cycle_rank + 1):
            for ranks in nonnegative_compositions(total_rank, components):
                if any(rank > 1 for rank in ranks):
                    continue
                for orders in positive_compositions(N, components):
                    lower = profile_lower_alpha(orders, ranks)
                    if lower is None:
                        continue
                    sparse_profiles += 1
                    if lower <= 5:
                        sparse_bad_profiles.append((orders, ranks, lower))
    assert sparse_bad_profiles == []

    # At m=11, k=1 and k=2 still force alpha>=6.  For k=3, cycle-rank
    # distribution (1,1,0) is the only possible equality route after the
    # analytic bicyclic dichotomy.  Exhaust its order/parity profiles.
    assert tree_alpha_floor(12) == 6
    two_component_equality_profiles = 0
    for ranks in ((1, 0), (0, 1)):
        for orders in positive_compositions(N, 2):
            lower = profile_lower_alpha(orders, ranks)
            if lower is None:
                continue
            assert lower >= 6
            two_component_equality_profiles += 1

    equality_profiles = set()
    two_unicyclic_profiles = 0
    for ranks in set(product((0, 1), repeat=3)):
        if sum(ranks) != 2:
            continue
        for orders in positive_compositions(N, 3):
            lower = profile_lower_alpha(orders, ranks)
            if lower is None:
                continue
            two_unicyclic_profiles += 1
            if lower <= 5:
                # Equality requires both unicyclic components to be
                # non-bipartite.  Triangle-freeness makes each order >=5.
                if all(order >= 5 for order, rank in zip(orders, ranks)
                       if rank == 1):
                    equality_profiles.add(tuple(sorted(orders)))
    assert equality_profiles == {(2, 5, 5)}

    # Guard the two branches of the bicyclic-core argument arithmetically.
    bicyclic_profiles = 0
    for bicyclic_position in range(3):
        for orders in positive_compositions(N, 3):
            q = orders[bicyclic_position]
            trees = [orders[index] for index in range(3)
                     if index != bicyclic_position]
            # Branch 1: one vertex hits every odd cycle.
            branch_one = q // 2 + sum(tree_alpha_floor(value)
                                      for value in trees)
            assert branch_one >= 6
            # Branch 2: two disjoint odd cycles.  Triangle-freeness gives
            # q>=10; with two nonempty trees and total order 12 this forces
            # (q,trees)=(10,[1,1]), and the two cycles supply alpha>=4.
            if q >= 10:
                assert sorted(trees) == [1, 1]
                assert 4 + sum(tree_alpha_floor(value) for value in trees) >= 6
            bicyclic_profiles += 1

    invariants = graph_invariants(equality_graph())
    assert invariants == (12, 11, 0, 5)

    print("status: CHECKED")
    print("four_component_max_order_at_alpha5: 11")
    print("five_component_max_order_at_alpha5: 10")
    print(f"sparse_component_profiles_checked: {sparse_profiles}")
    print("sparse_profiles_with_alpha_at_most_5: 0")
    print(f"two_component_equality_profiles_checked: {two_component_equality_profiles}")
    print(f"two_unicyclic_profiles_checked: {two_unicyclic_profiles}")
    print("equality_order_profile: (2,5,5)")
    print(f"bicyclic_order_profiles_checked: {bicyclic_profiles}")
    print("equality_graph: C5 disjoint-union C5 disjoint-union K2")
    print("equality_graph_invariants: n=12, e=11, triangles=0, alpha=5")
    print("scope: exhaustive component-profile guard; not all-graph enumeration")


if __name__ == "__main__":
    main()
