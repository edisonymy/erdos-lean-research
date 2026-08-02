"""Small exact checks for ORDER41_K5_RIGID_ATTACK.md.

This is not a search for an order-41 graph.  It checks only the finite
arithmetic squeeze and the 11-vertex transversal obstruction used in the
proof.  The graph-theoretic reductions leading to those two finite objects
remain proofs in the companion note.
"""

from itertools import product


COMPONENTS = (
    (0, 1, 2),
    (3, 4),
    (5, 6),
    (7, 8),
    (9, 10),
)
N = 11


def mask(vertices):
    value = 0
    for vertex in vertices:
        value |= 1 << vertex
    return value


COMPONENT_MASKS = tuple(mask(component) for component in COMPONENTS)


def is_independent(vertex_mask):
    return all((vertex_mask & component_mask).bit_count() <= 1
               for component_mask in COMPONENT_MASKS)


def main():
    # Five fan cuts have at least 17 edges each.  Together with e(U) >= 7
    # and the degree-nine budget on the eleven U vertices, the only integer
    # possibility is e(U)=7 and all five cut sizes equal 17.
    arithmetic_states = []
    for e_u in range(7, 56):
        min_cut_sum = 5 * 17
        if 2 * e_u + min_cut_sum <= 11 * 9:
            slack = 11 * 9 - 2 * e_u - min_cut_sum
            for increments in product(range(slack + 1), repeat=5):
                if sum(increments) <= slack:
                    arithmetic_states.append(
                        (e_u, tuple(17 + value for value in increments))
                    )

    assert arithmetic_states == [(7, (17, 17, 17, 17, 17))]

    # Equality in Turan's theorem makes U = K3 disjoint union 4 K2.  Its
    # maximum independent sets are precisely the 3*2^4 transversals.
    transversals = {
        mask(choice)
        for choice in product(*COMPONENTS)
    }
    assert len(transversals) == 48
    assert all(is_independent(choice) for choice in transversals)
    assert all(choice.bit_count() == 5 for choice in transversals)

    independent_sets = [
        vertex_mask
        for vertex_mask in range(1 << N)
        if is_independent(vertex_mask)
    ]
    assert len(independent_sets) == 4 * 3**4 == 324

    # For a vertex a outside U, the U-endpoints of F-maximal edges incident
    # with a form an independent set L.  No independent L hits every maximum
    # independent transversal of U, so some independent five-set I avoids L.
    independent_transversal_hitting_sets = [
        left
        for left in independent_sets
        if all(left & transversal for transversal in transversals)
    ]
    assert independent_transversal_hitting_sets == []

    print("status: CHECKED")
    print("arithmetic_states: 1")
    print("forced_state: e(U)=7, cut_sizes=(17,17,17,17,17)")
    print("U_type: K3 disjoint-union 4K2")
    print("maximum_independent_transversals: 48")
    print("independent_sets_in_U: 324")
    print("independent_sets_hitting_all_transversals: 0")
    print("scope: finite arithmetic/transversal check only; no order-41 search")


if __name__ == "__main__":
    main()
