"""Exact audit for REPORT.md (Erdos #128 global amplification lane)."""

from fractions import Fraction as F
from itertools import combinations


def extreme_half_min(weights, edges):
    """Minimum edge energy at total mass 1/2 for an independent-cluster quotient.

    With no within-cluster edges, mass transfer between two fractional
    coordinates is linear or concave.  Hence a minimum has at most one
    fractional coordinate, so enumerating box-simplex extreme points is exact.
    """

    m = len(weights)
    edge_set = {tuple(sorted(edge)) for edge in edges}
    best = None
    witness = None
    for mask in range(1 << m):
        full_mass = sum(
            (weights[i] for i in range(m) if (mask >> i) & 1), F(0)
        )
        if full_mass > F(1, 2):
            continue
        remainder = F(1, 2) - full_mass
        partial_choices = [None] if remainder == 0 else [
            j
            for j in range(m)
            if not ((mask >> j) & 1) and remainder <= weights[j]
        ]
        for partial in partial_choices:
            z = [weights[i] if (mask >> i) & 1 else F(0) for i in range(m)]
            if partial is not None:
                z[partial] = remainder
            energy = sum((z[i] * z[j] for i, j in edge_set), F(0))
            if best is None or energy < best:
                best = energy
                witness = z
    assert best is not None
    return best, witness


def audit_balanced_identities():
    # Exact polynomial coefficient checks for the two displayed identities.
    # Polynomials are stored from constant term upward.
    def mul(a, b):
        out = [F(0)] * (len(a) + len(b) - 1)
        for i, ai in enumerate(a):
            for j, bj in enumerate(b):
                out[i + j] += ai * bj
        return out

    def add(a, b):
        n = max(len(a), len(b))
        return [
            (a[i] if i < len(a) else F(0))
            + (b[i] if i < len(b) else F(0))
            for i in range(n)
        ]

    # r=1/2-x, B=r(2x-1/2), K=2(B-1/50).
    r = [F(1, 2), F(-1)]
    B = mul(r, [F(-1, 2), F(2)])
    K = add([2 * c for c in B], [F(-1, 25)])
    left = add([c / 5 for c in r], [-c for c in K])
    right = [F(16, 25), -F(16, 5), F(4)]  # 4(5x-2)^2/25
    assert left == right

    # Verify after multiplying by 25x:
    # 1/25 - 2rK/(x/2) = -Q/(25x).
    # Therefore x - 100 r K = -Q.
    x_poly = [F(0), F(1)]
    lhs = add(x_poly, [-100 * c for c in mul(r, K)])
    q_negative = [F(27), F(-203), F(500), F(-400)]
    assert lhs == q_negative

    # Q'(x)=1200x^2-1000x+203 has the stated roots.
    def qprime(x):
        return 1200 * x * x - 1000 * x + 203

    assert qprime(F(7, 20)) == 0
    assert qprime(F(29, 60)) == 0
    q_at_join = (
        400 * F(7, 20) ** 3
        - 500 * F(7, 20) ** 2
        + 203 * F(7, 20)
        - 27
    )
    assert q_at_join == F(-1, 20)


def audit_c5():
    weights = [F(1, 5)] * 5
    edges = [(i, (i + 1) % 5) for i in range(5)]
    beta, _ = extreme_half_min(weights, edges)
    assert beta == F(1, 50)


def two_block_quotient(symmetrize=False):
    x = F(1997, 5000)
    h = x / 2
    c = F(787, 10000)
    p1, q1 = F(77, 1000), F(687, 5000)
    p2, q2 = F(621, 5000), F(1419, 10000)
    t = F(1201, 10000)
    atoms = [c, h - c, h - c, c]
    if symmetrize:
        t += (q1 - p1) + (q2 - p2)
        q1, q2 = p1, p2
    weights = atoms + [p1, q1, p2, q2, t]
    # T1={0,1}; T2={0,2}; indices 4,5 and 6,7 are block sides.
    edges = []
    edges.extend((4, i) for i in (0, 1))
    edges.extend((5, i) for i in (2, 3))
    edges.extend((6, i) for i in (0, 2))
    edges.extend((7, i) for i in (1, 3))
    edges.extend([(4, 5), (6, 7)])
    edges.extend((8, i) for i in range(4))
    assert sum(weights, F(0)) == 1
    return weights, edges


def audit_false_symmetrization():
    beta_original, _ = extreme_half_min(*two_block_quotient(False))
    beta_symmetrized, _ = extreme_half_min(*two_block_quotient(True))
    assert beta_original == F(43527, 3125000)
    assert beta_symmetrized == F(221503, 25000000)
    assert beta_symmetrized < beta_original < F(1, 50)


CHVATAL_EDGES = {
    (0, 1), (0, 4), (0, 6), (0, 9),
    (1, 2), (1, 5), (1, 7),
    (2, 3), (2, 6), (2, 8),
    (3, 4), (3, 7), (3, 9),
    (4, 5), (4, 8),
    (5, 10), (5, 11),
    (6, 10), (6, 11),
    (7, 8), (7, 11),
    (8, 10),
    (9, 10), (9, 11),
}


def independent(subset):
    return all(tuple(sorted(edge)) not in CHVATAL_EDGES for edge in combinations(subset, 2))


def audit_chvatal(epsilon=F(1, 1000)):
    assert 0 < epsilon < F(1, 20)
    vertices = range(12)
    neighbors = {v: set() for v in vertices}
    for u, v in CHVATAL_EDGES:
        neighbors[u].add(v)
        neighbors[v].add(u)

    # Triangle-free and diameter two (every nonedge has a common neighbor).
    for triple in combinations(vertices, 3):
        assert not all(tuple(sorted(edge)) in CHVATAL_EDGES for edge in combinations(triple, 2))
    for u, v in combinations(vertices, 2):
        if (u, v) not in CHVATAL_EDGES:
            assert neighbors[u] & neighbors[v]

    I = {0, 2, 5, 7}
    x = F(19, 50)
    weights = {v: F(19, 200) for v in I}
    weights.update({
        1: F(1, 20) - epsilon,
        3: epsilon,
        4: F(19, 100) - epsilon,
        6: F(19, 200),
        8: F(19, 100) - epsilon,
        9: epsilon,
        10: epsilon,
        11: F(19, 200),
    })
    assert all(weight > 0 for weight in weights.values())
    assert sum(weights.values(), F(0)) == 1
    assert sum((weights[v] for v in I), F(0)) == x

    max_independent_weight = F(0)
    for mask in range(1 << 12):
        subset = [v for v in vertices if (mask >> v) & 1]
        if independent(subset):
            value = sum((weights[v] for v in subset), F(0))
            max_independent_weight = max(max_independent_weight, value)
    assert max_independent_weight == x

    type_weights = {
        v: sum((weights[i] for i in neighbors[v] & I), F(0))
        for v in vertices if v not in I
    }
    low = {v for v, value in type_weights.items() if value <= x / 3}
    assert low == {9, 10}
    assert sum((weights[v] for v in low), F(0)) == 2 * epsilon
    assert set(type_weights.values()) == {x / 4, x / 2, x}

    weighted_degrees = {
        v: sum((weights[u] for u in neighbors[v]), F(0)) for v in vertices
    }
    assert min(weighted_degrees.values()) > F(19, 100)
    assert min(weighted_degrees.values()) > F(2, 25)


def main():
    audit_balanced_identities()
    audit_c5()
    audit_false_symmetrization()
    for epsilon in (F(1, 1000000), F(1, 1000), F(1, 100), F(49, 1000)):
        audit_chvatal(epsilon)
    print("PASS balanced identities")
    print("PASS beta(C5 balanced blow-up) = 1/50")
    print("PASS exact two-block symmetrization falsifier")
    print("PASS Chvatal low-type mass family across four exact epsilon scales")


if __name__ == "__main__":
    main()
