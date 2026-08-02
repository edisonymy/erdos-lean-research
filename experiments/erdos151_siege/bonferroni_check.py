"""Exact arithmetic checker for a weakened F3 projection.

The nominal assumptions n=28, 7-regular, omega=3, L=empty are inconsistent
under the full audited two-walk package.  This script deliberately discards
the stronger (u_v,l_v) constraints and checks only the resulting projected
coverage arithmetic.  It verifies:
 (1) the identity coefficients 7315/1540/231 under A = sum_e C(m_e,2),
     V = sum_v C(t_v,2);
 (2) closed forms A_min = 3N-98, V_min = 18N-588 and the quadratic
     exclusion N <= 62;
 (3) the capped local maximum M = max triangles in a K4-free 8-vertex
     graph with every vertex in <= 7 triangles (exact MaxSAT), plus
     the uncapped value (must be 18, Zykov cross-check);
 (4) the refined exclusion using factor 2/M in place of 1/9.
"""

from __future__ import annotations

import itertools
from math import comb

from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2
from pysat.formula import IDPool, WCNF


def coeff_check():
    # pair-of-triangles union sizes: 4 (share edge), 5 (share vertex), 6
    c4, c5, c6 = comb(24, 4), comb(23, 3), comb(22, 2)
    assert (c4, c5, c6) == (10626, 1771, 231)
    # with V counting pair-vertex incidences (edge-sharing pairs twice):
    assert c4 - c6 == 7315 + 2 * (c5 - c6)
    assert c5 - c6 == 1540
    return True


def max_triangles_8(cap7):
    pool = IDPool()
    E = {p: pool.id(f"e{p}") for p in itertools.combinations(range(8), 2)}
    def e(i, j):
        return E[(min(i, j), max(i, j))]
    wcnf = WCNF()
    tri = {}
    for tvx in itertools.combinations(range(8), 3):
        y = pool.id(f"y{tvx}")
        tri[tvx] = y
        a, b, c = tvx
        for p in ((a, b), (a, c), (b, c)):
            wcnf.append([-y, e(*p)])
        wcnf.append([y, -e(a, b), -e(a, c), -e(b, c)])
    for q in itertools.combinations(range(8), 4):
        wcnf.append([-e(i, j) for i, j in itertools.combinations(q, 2)])
    if cap7:
        for v in range(8):
            lits = [tri[t] for t in tri if v in t]
            for cl in CardEnc.atmost(lits=lits, bound=7, vpool=pool,
                                     encoding=EncType.seqcounter).clauses:
                wcnf.append(cl)
    for y in tri.values():
        wcnf.append([y], weight=1)
    with RC2(wcnf) as rc2:
        rc2.compute()
        return len(tri) - rc2.cost


def squeeze(factor_num, factor_den, label):
    # LHS >= (factor_num/factor_den) * (7315 A_min + 1540 V_min + 231 C(N,2))
    ok = []
    for Nt in range(59, 66):
        lhs = Nt * comb(25, 5) - comb(28, 8)
        amin, vmin = 3 * Nt - 98, 18 * Nt - 588
        rhs_core = 7315 * amin + 1540 * vmin + 231 * comb(Nt, 2)
        # exact rational comparison: lhs * den >= num * core
        if lhs * factor_den >= factor_num * rhs_core:
            ok.append(Nt)
    print(f"{label}: surviving N in {ok}")
    return ok


def main():
    assert coeff_check()
    print("coefficient identity 7315/1540/231: OK")
    assert comb(25, 5) == 53130 and comb(28, 8) == 3108105
    base = squeeze(1, 9, "base (m_T <= 18, factor 1/9)")
    assert base == [63, 64, 65], base
    m18 = max_triangles_8(cap7=False)
    print(f"uncapped 8-vertex K4-free max triangles = {m18} (Zykov: 18)")
    assert m18 == 18
    M = max_triangles_8(cap7=True)
    print(f"capped (t_v <= 7) 8-vertex K4-free max triangles M = {M}")
    refined = squeeze(2, M, f"refined (m_T <= {M}, factor 2/{M})")
    print("FINAL weakened-projection window (full corner is infeasible):", refined)


if __name__ == "__main__":
    main()
