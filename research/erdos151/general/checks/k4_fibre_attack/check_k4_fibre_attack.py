"""Isolated guards for ORDER41_K4_FIBRE_ATTACK.md.

This is not a search for an order-41 counterexample.  It checks the finite
arithmetic, the weighted-duplication identity, and one fixed four-residual
local abstraction which deliberately fails the global alpha <= 9 condition.
Only the Python standard library is used.
"""

from itertools import combinations


U = tuple(range(13))
FANS = tuple(tuple(range(13 + 6 * c, 19 + 6 * c)) for c in range(4))
M = tuple(range(37, 41))
N = 41

# Edges on U union FANS.  There are no edges between different fans.
# The four M vertices and their spoke edges are added below.
LOCAL_EDGES = {
    (0, 6), (0, 7), (0, 14), (0, 22), (0, 23), (0, 28),
    (0, 30), (0, 32), (0, 34),
    (1, 4), (1, 8), (1, 9), (1, 13), (1, 16), (1, 23),
    (1, 30), (1, 33), (1, 36),
    (2, 3), (2, 9), (2, 11), (2, 16), (2, 19), (2, 27),
    (2, 28), (2, 33), (2, 34),
    (3, 5), (3, 12), (3, 13), (3, 20), (3, 23), (3, 25),
    (3, 30), (3, 36),
    (4, 18), (4, 19), (4, 20), (4, 22), (4, 26), (4, 28),
    (4, 31), (4, 34),
    (5, 7), (5, 9), (5, 10), (5, 17), (5, 19), (5, 21),
    (5, 26), (5, 34),
    (6, 10), (6, 15), (6, 17), (6, 19), (6, 20), (6, 25),
    (6, 26), (6, 35),
    (7, 11), (7, 16), (7, 18), (7, 24), (7, 25), (7, 33),
    (7, 36),
    (8, 11), (8, 12), (8, 14), (8, 17), (8, 21), (8, 27),
    (8, 34), (8, 35),
    (9, 14), (9, 15), (9, 20), (9, 24), (9, 29), (9, 32),
    (10, 11), (10, 14), (10, 16), (10, 22), (10, 28),
    (10, 32), (10, 33),
    (11, 15), (11, 20), (11, 26), (11, 29), (11, 31),
    (12, 15), (12, 16), (12, 22), (12, 24), (12, 26),
    (12, 28), (12, 33),
    (13, 14), (13, 15), (13, 17), (14, 18), (16, 17),
    (17, 18),
    (19, 24), (20, 21), (21, 22), (21, 23), (23, 24),
    (25, 27), (25, 29), (26, 27), (27, 30), (28, 29),
    (29, 30),
    (31, 32), (31, 35), (32, 36), (33, 35), (35, 36),
}


def choose2(x):
    return x * (x - 1) // 2


def turan_complement_lower(order, parts):
    """Minimum edges in a graph of order `order` with alpha <= parts."""
    q, r = divmod(order, parts)
    return (parts - r) * choose2(q) + r * choose2(q + 1)


def make_graph():
    edges = {tuple(sorted(edge)) for edge in LOCAL_EDGES}
    edges.update(combinations(M, 2))
    for c, fan in zip(M, FANS):
        edges.update((min(c, a), max(c, a)) for a in fan)
    adjacency = [set() for _ in range(N)]
    for x, y in edges:
        assert 0 <= x < y < N
        adjacency[x].add(y)
        adjacency[y].add(x)
    return edges, adjacency


def is_independent(vertices, adjacency):
    vertices = tuple(vertices)
    return all(y not in adjacency[x] for x, y in combinations(vertices, 2))


def max_independent_set(vertices, adjacency):
    """Exact branch-and-bound MIS, adequate for this fixed 41-vertex graph."""
    vertices = tuple(vertices)
    relabel = {v: i for i, v in enumerate(vertices)}
    masks = [0] * len(vertices)
    for v in vertices:
        i = relabel[v]
        for w in adjacency[v]:
            if w in relabel:
                masks[i] |= 1 << relabel[w]

    best_mask = 0

    def visit(candidates, chosen):
        nonlocal best_mask
        if chosen.bit_count() + candidates.bit_count() <= best_mask.bit_count():
            return
        if not candidates:
            if chosen.bit_count() > best_mask.bit_count():
                best_mask = chosen
            return

        scan = candidates
        pivot = -1
        pivot_degree = -1
        while scan:
            bit = scan & -scan
            v = bit.bit_length() - 1
            scan ^= bit
            degree = (masks[v] & candidates).bit_count()
            if degree > pivot_degree:
                pivot = v
                pivot_degree = degree

        pivot_bit = 1 << pivot
        visit(candidates & ~pivot_bit & ~masks[pivot], chosen | pivot_bit)
        visit(candidates & ~pivot_bit, chosen)

    visit((1 << len(vertices)) - 1, 0)
    return tuple(vertices[i] for i in range(len(vertices)) if best_mask >> i & 1)


def is_ambient_maximal_edge(x, y, adjacency):
    return y in adjacency[x] and not (adjacency[x] & adjacency[y])


def check_weighted_duplication_identity():
    states = 0
    for saturated_count in range(5):
        for m_degree in range(1, 4):
            for multiplicity in range(min(saturated_count, m_degree) + 1):
                for u_degree in range(10 - m_degree):
                    cut_sum = multiplicity * u_degree
                    once = u_degree if multiplicity else 0
                    duplication = max(0, multiplicity - 1) * u_degree
                    assert cut_sum == once + duplication
                    assert duplication <= (
                        max(0, min(saturated_count, m_degree) - 1)
                        * (9 - m_degree)
                    )
                    states += 1
    return states


def check_ledger_and_scalar_survivor():
    profiles = []
    for t in range(5):
        for n3 in range(3):
            for n2 in range(7):
                if 3 * t + 2 * n2 + 5 * n3 <= 12:
                    profiles.append((t, n2, n3))
    assert len(profiles) == 29
    assert profiles[0] == (0, 0, 0)

    t = n2 = n3 = 0
    u = 13 + t + n2 + 2 * n3
    positive = 37 - u
    saturated_count = 4
    cut_lower = 2 * u - 6
    u_lower = 2 * turan_complement_lower(u, 6) + saturated_count * cut_lower
    u_budget = 9 * u
    positive_lower = saturated_count * cut_lower + 2 * turan_complement_lower(positive, 9)
    positive_budget = 9 * positive - (24 - t)
    assert (u, positive, cut_lower) == (13, 24, 20)
    assert (u_lower, u_budget) == (96, 117)
    assert (positive_lower, positive_budget) == (122, 192)
    return len(profiles), u_lower, u_budget, positive_lower, positive_budget


def check_fixed_local_abstraction():
    edges, adjacency = make_graph()
    assert len(edges) == 151

    degrees = [len(adjacency[v]) for v in range(N)]
    assert min(degrees) == 5
    assert max(degrees) == 9
    assert [degrees[v] for v in U] == [9] * 13
    assert [degrees[v] for v in M] == [9] * 4

    assert all(y in adjacency[x] for x, y in combinations(M, 2))
    assert not any(
        all(y in adjacency[x] for x, y in combinations(vertices, 2))
        for vertices in combinations(range(N), 5)
    )

    # Exact M-neighbourhood classes: 13 core vertices and four singleton fans.
    for u in U:
        assert not (adjacency[u] & set(M))
    for c, fan in zip(M, FANS):
        for a in fan:
            assert adjacency[a] & set(M) == {c}

    e_u = sum(1 for x, y in edges if x in U and y in U)
    cut_edges = []
    singleton_counts = []
    seeded_counts = []
    residual_alphas = []

    for fan in FANS:
        fan_set = set(fan)
        residual = U + fan
        cut_edges.append(sum(len(adjacency[u] & fan_set) for u in U))

        fibres = {a: [] for a in fan}
        for u in U:
            neighbours = adjacency[u] & fan_set
            assert neighbours
            if len(neighbours) == 1:
                a = next(iter(neighbours))
                fibres[a].append(u)
                assert is_ambient_maximal_edge(u, a, adjacency)
        assert max(map(len, fibres.values())) <= 1
        singleton_counts.append(sum(map(len, fibres.values())))

        # Each residual is triangle-free and has alpha exactly six.
        assert not any(
            all(y in adjacency[x] for x, y in combinations(triple, 2))
            for triple in combinations(residual, 3)
        )
        alpha_witness = max_independent_set(residual, adjacency)
        assert len(alpha_witness) == 6
        residual_alphas.append(len(alpha_witness))

        # Every independent six-set supplies the seeded core-anchor consequence.
        seed_count = 0
        for seed in combinations(residual, 6):
            if not is_independent(seed, adjacency):
                continue
            seed_count += 1
            seed_set = set(seed)
            for z in set(U) - seed_set:
                assert any(
                    x in adjacency[z] and is_ambient_maximal_edge(z, x, adjacency)
                    for x in seed
                )
        assert seed_count
        seeded_counts.append(seed_count)

    assert e_u == 18
    assert cut_edges == [20, 21, 20, 20]
    assert singleton_counts == [6, 6, 6, 6]
    assert residual_alphas == [6, 6, 6, 6]
    assert 2 * e_u + sum(cut_edges) == 13 * 9

    global_independent = max_independent_set(range(N), adjacency)
    assert len(global_independent) == 15

    # Exact maxima in the cross-fan shadows R(I), grouped by |I|.  The
    # abstraction happens to pass the rank-six shadow but fails the lower
    # ranks badly; this pinpoints why seeded six-sets alone are insufficient.
    shadow_maxima = []
    shadow_witnesses = []
    outside_u = set(range(N)) - set(U)
    for rank in range(7):
        best = (-1, (), ())
        for seed in combinations(U, rank):
            if not is_independent(seed, adjacency):
                continue
            seed_set = set(seed)
            shadow = tuple(
                x for x in outside_u if not (adjacency[x] & seed_set)
            )
            independent = max_independent_set(shadow, adjacency)
            if len(independent) > best[0]:
                best = (len(independent), seed, independent)
        shadow_maxima.append(best[0])
        shadow_witnesses.append((best[1], best[2]))
    assert shadow_maxima == [15, 14, 13, 10, 8, 4, 1]
    assert shadow_maxima[6] <= 3
    assert shadow_maxima[2] > 7

    # This ten-set is already independent.  It is retained as an explicit
    # warning that the local abstraction does not include global alpha <= 9.
    fatal_ten_set = (1, 3, 7, 10, 17, 19, 21, 26, 34, 35)
    assert is_independent(fatal_ten_set, adjacency)

    return {
        "edges": len(edges),
        "degrees": (min(degrees), max(degrees)),
        "e_u": e_u,
        "cuts": cut_edges,
        "singletons": singleton_counts,
        "residual_alphas": residual_alphas,
        "seeded_sets": seeded_counts,
        "global_alpha": len(global_independent),
        "global_alpha_witness": global_independent,
        "shadow_maxima": shadow_maxima,
        "rank_two_shadow_witness": shadow_witnesses[2],
        "fatal_ten_set": fatal_ten_set,
    }


def main():
    weighted_states = check_weighted_duplication_identity()
    scalar = check_ledger_and_scalar_survivor()
    witness = check_fixed_local_abstraction()

    print("weighted duplication states:", weighted_states)
    print("ledger profiles:", scalar[0])
    print("rigid U lower/budget:", scalar[1], "/", scalar[2])
    print("rigid positive-part lower/budget:", scalar[3], "/", scalar[4])
    print("fixed abstraction edges:", witness["edges"])
    print("degree interval:", witness["degrees"])
    print("e(U):", witness["e_u"])
    print("cut edges:", witness["cuts"])
    print("singleton vertices per cut:", witness["singletons"])
    print("residual alpha=beta:", witness["residual_alphas"])
    print("independent six-seeds checked:", witness["seeded_sets"])
    print("global alpha (deliberate failure):", witness["global_alpha"])
    print("global alpha witness:", witness["global_alpha_witness"])
    print("max alpha(R(I)) by |I|=0..6:", witness["shadow_maxima"])
    print("rank-two shadow witness:", witness["rank_two_shadow_witness"])
    print("fatal independent ten-set:", witness["fatal_ten_set"])
    print("status: CHECKED")


if __name__ == "__main__":
    main()
