"""Finite guards for ORDER41_K5_TRIANGLE_SATURATION.md.

This is not an order-41 graph search and does not verify catalogue
completeness.  It checks the full-fan set-system minimum, the exact degree
arithmetic, the forced sparse equality graph, and the terminal independent
hitting-set statement.
"""

from itertools import combinations, product
from math import comb, factorial


N = 12
FULL_FAN_SIZE = 5
MIN_FULL_CUT = 19
MIN_DEFICIENT_CUT = 10
MIN_U_EDGES = 11
U_DEGREE_BUDGET = 12 * 9


def full_fan_set_system():
    """DP over twelve nonempty subsets with each singleton label used once."""
    states = {(0, 0): 1}  # (used singleton labels, total incidences) -> count
    for _ in range(N):
        next_states = {}
        for (used, total), ways in states.items():
            for neighbourhood in range(1, 1 << FULL_FAN_SIZE):
                size = neighbourhood.bit_count()
                if size == 1 and used & neighbourhood:
                    continue
                next_used = used | neighbourhood if size == 1 else used
                key = (next_used, total + size)
                next_states[key] = next_states.get(key, 0) + ways
        states = next_states

    minimum = min(total for (_, total), ways in states.items() if ways)
    equality_count = sum(
        ways for (_, total), ways in states.items() if total == minimum
    )
    expected = (
        comb(N, FULL_FAN_SIZE)
        * factorial(FULL_FAN_SIZE)
        * comb(FULL_FAN_SIZE, 2) ** (N - FULL_FAN_SIZE)
    )
    assert minimum == MIN_FULL_CUT
    assert equality_count == expected == 950_400_000_000
    return minimum, equality_count


def arithmetic_states():
    """Enumerate all slack allocations after the five analytic lower bounds."""
    states = []
    for e_u in range(MIN_U_EDGES, comb(N, 2) + 1):
        baseline = 2 * e_u + 4 * MIN_FULL_CUT + MIN_DEFICIENT_CUT
        slack = U_DEGREE_BUDGET - baseline
        if slack < 0:
            continue
        # Four full-cut increments and one deficient-cut increment.
        for increments in product(range(slack + 1), repeat=5):
            if sum(increments) <= slack:
                full = tuple(MIN_FULL_CUT + value for value in increments[:4])
                deficient = MIN_DEFICIENT_CUT + increments[4]
                states.append((e_u, full, deficient))
    assert states == [(11, (19, 19, 19, 19), 10)]
    return states


def equality_graph():
    """Return adjacency masks for C5 disjoint-union C5 disjoint-union K2."""
    adjacency = [0] * N

    def add_edge(left, right):
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left

    for offset in (0, 5):
        for vertex in range(5):
            add_edge(offset + vertex, offset + (vertex + 1) % 5)
    add_edge(10, 11)
    return adjacency


def is_independent(vertex_mask, adjacency):
    remaining = vertex_mask
    while remaining:
        bit = remaining & -remaining
        vertex = bit.bit_length() - 1
        remaining -= bit
        if adjacency[vertex] & remaining:
            return False
    return True


def is_clique(vertex_mask, adjacency):
    vertices = [vertex for vertex in range(N) if vertex_mask >> vertex & 1]
    return all(
        adjacency[left] >> right & 1
        for left, right in combinations(vertices, 2)
    )


def graph_and_hitting_checks():
    adjacency = equality_graph()
    edges = sum(mask.bit_count() for mask in adjacency) // 2
    triangles = sum(
        1
        for triple in combinations(range(N), 3)
        if all(adjacency[left] >> right & 1
               for left, right in combinations(triple, 2))
    )
    independent_sets = [
        vertex_mask
        for vertex_mask in range(1 << N)
        if is_independent(vertex_mask, adjacency)
    ]
    alpha = max(vertex_mask.bit_count() for vertex_mask in independent_sets)
    maximum_sets = {
        vertex_mask
        for vertex_mask in independent_sets
        if vertex_mask.bit_count() == alpha
    }
    hitting_sets = [
        endpoint_set
        for endpoint_set in independent_sets
        if all(endpoint_set & maximum_set for maximum_set in maximum_sets)
    ]

    assert edges == 11
    assert triangles == 0
    assert alpha == 5
    assert len(independent_sets) == 11 * 11 * 3 == 363
    assert len(maximum_sets) == 5 * 5 * 2 == 50
    assert hitting_sets == []
    assert all(
        any(not (endpoint_set & maximum_set) for maximum_set in maximum_sets)
        for endpoint_set in independent_sets
    )

    # A triangle-free graph has no clique of order three.  This exhausts all
    # possible D0 cliques in the forced equality graph, including empty and
    # singleton choices, and checks the deficient-cut minimum 12-|D0|=10.
    d0_cliques = [
        vertex_mask
        for vertex_mask in range(1 << N)
        if is_clique(vertex_mask, adjacency)
    ]
    maximum_d0 = max(vertex_mask.bit_count() for vertex_mask in d0_cliques)
    assert len(d0_cliques) == 1 + N + edges == 24
    assert maximum_d0 == 2
    assert N - maximum_d0 == MIN_DEFICIENT_CUT

    return {
        "edges": edges,
        "triangles": triangles,
        "alpha": alpha,
        "independent_sets": len(independent_sets),
        "maximum_sets": len(maximum_sets),
        "hitting_sets": len(hitting_sets),
        "d0_cliques": len(d0_cliques),
        "maximum_d0": maximum_d0,
    }


def main():
    cut_minimum, equality_count = full_fan_set_system()
    states = arithmetic_states()
    report = graph_and_hitting_checks()

    print("status: CHECKED")
    print(f"full_fan_cut_minimum: {cut_minimum}")
    print(f"full_fan_equality_assignments: {equality_count}")
    print(f"arithmetic_states: {len(states)}")
    print("forced_state: e(U)=11, full_cuts=(19,19,19,19), deficient_cut=10")
    print("U_type: C5 disjoint-union C5 disjoint-union K2")
    print(
        "U_invariants: "
        f"e={report['edges']}, triangles={report['triangles']}, "
        f"alpha={report['alpha']}"
    )
    print(f"D0_cliques: {report['d0_cliques']}, maximum_D0: {report['maximum_d0']}")
    print(f"independent_sets_in_U: {report['independent_sets']}")
    print(f"maximum_independent_5_sets: {report['maximum_sets']}")
    print(f"independent_sets_hitting_all_maximum_sets: {report['hitting_sets']}")
    print("scope: finite set-system/arithmetic/hitting guards; no catalogue or order-41 search")


if __name__ == "__main__":
    main()
