"""Exact decision of the K4-free face of Erdos #151 at small order.

Question(n, h): does there exist a K4-free graph G on n vertices with
max degree <= h-1 and NO admissible h-set (admissible = contains no
triangle of G and no maximal edge of G)?  A YES graph has
beta(G) <= h-1 < h <= H(n) (published R(3,h) upper bounds) — a full
counterexample to #151.  A NO (UNSAT) is a certified exclusion of the
K4-free face at order n.

Soundness of the imposed constraints for ANY counterexample of this face:
beta >= Delta forces Delta <= h-1; beta >= alpha makes alpha <= h-1
(added lazily as cuts when the oracle returns an independent h-set,
which is a special admissible set anyway).

CEGAR: SAT model -> oracle finds admissible h-sets (exact B&B over
triangle + maximal-edge obstructions) -> cuts:  for each found W,
   OR_{triples t in W} y_t  OR  OR_{pairs uv in W} m_uv
with lazy defs y_t -> its 3 edges (y true forces a triangle inside W),
m_uv -> e_uv and m_uv -> not(e_uw & e_vw) for all w (m true forces uv to
be a maximal edge inside W).  Both directions are sufficient for cut
soundness: any graph in which W is admissible violates the cut.

Usage: python -X utf8 cegar_face.py N H ROUNDS OUT.json [MIN_DEGREE]
"""
from __future__ import annotations

import itertools
import json
import random
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195


def solve_face(n, h, max_rounds, outpath, cuts_per_round=24,
               seed=2026, min_degree=0):
    if not 0 <= min_degree <= h - 1:
        raise ValueError("min_degree must lie between 0 and h-1")
    rng = random.Random(seed)
    pool = IDPool()
    E = {}
    for u in range(n):
        for v in range(u + 1, n):
            E[(u, v)] = pool.id(f"e{u}_{v}")

    def ev(u, v):
        return E[(min(u, v), max(u, v))]

    solver = Cadical195()
    # no K4
    nk4 = 0
    for q in itertools.combinations(range(n), 4):
        solver.add_clause([-ev(a, b)
                           for a, b in itertools.combinations(q, 2)])
        nk4 += 1
    # degree cap h-1
    for u in range(n):
        lits = [ev(u, v) for v in range(n) if v != u]
        cnf = CardEnc.atmost(lits=lits, bound=h - 1, vpool=pool,
                             encoding=EncType.seqcounter)
        for cl in cnf.clauses:
            solver.add_clause(cl)
        if min_degree:
            cnf = CardEnc.atleast(lits=lits, bound=min_degree, vpool=pool,
                                  encoding=EncType.seqcounter)
            for cl in cnf.clauses:
                solver.add_clause(cl)

    y_def = {}   # triple -> var (defined lazily)
    m_def = {}   # pair -> var

    def y_var(t):
        if t not in y_def:
            v_ = pool.id(f"y{t}")
            y_def[t] = v_
            a, b, c = t
            solver.add_clause([-v_, ev(a, b)])
            solver.add_clause([-v_, ev(a, c)])
            solver.add_clause([-v_, ev(b, c)])
        return y_def[t]

    def m_var(p):
        if p not in m_def:
            v_ = pool.id(f"m{p}")
            m_def[p] = v_
            u, w = p
            solver.add_clause([-v_, ev(u, w)])
            for x in range(n):
                if x != u and x != w:
                    solver.add_clause([-v_, -ev(u, x), -ev(w, x)])
        return m_def[p]

    def oracle_admissible(adj, want):
        """Find up to `want` admissible h-sets by randomized exact-ish
        B&B; returns list of vertex tuples (empty if none exist —
        verified by one deterministic complete run)."""
        tri_block = [set() for _ in range(n)]
        maxe = [0] * n
        for u in range(n):
            for v in range(u + 1, n):
                if (adj[u] >> v) & 1 and not (adj[u] & adj[v]):
                    maxe[u] |= 1 << v
                    maxe[v] |= 1 << u
        found = []

        def rec(order, idx, s, cnt, budget):
            if cnt >= h:
                found.append(tuple(i for i in range(n) if (s >> i) & 1))
                return True
            if idx >= n or cnt + (n - idx) < h or budget[0] <= 0:
                return False
            budget[0] -= 1
            v = order[idx]
            common = adj[v] & s
            ok = not (maxe[v] & s)
            if ok:
                c = common
                while c:
                    w = (c & -c).bit_length() - 1
                    c &= c - 1
                    if adj[w] & common:
                        ok = False
                        break
            if ok and rec(order, idx + 1, s | (1 << v), cnt + 1, budget):
                return True
            return rec(order, idx + 1, s, cnt, budget)

        base = list(range(n))
        for _ in range(want * 3):
            if len(found) >= want:
                break
            order = base[:]
            rng.shuffle(order)
            rec(order, 0, 0, 0, [200000])
        if not found:
            # one complete deterministic pass (no budget) to certify none
            def rec_full(idx, s, cnt):
                if cnt >= h:
                    found.append(tuple(i for i in range(n)
                                       if (s >> i) & 1))
                    return True
                if idx >= n or cnt + (n - idx) < h:
                    return False
                v = idx
                common = adj[v] & s
                ok = not (maxe[v] & s)
                if ok:
                    c = common
                    while c:
                        w = (c & -c).bit_length() - 1
                        c &= c - 1
                        if adj[w] & common:
                            ok = False
                            break
                if ok and rec_full(idx + 1, s | (1 << v), cnt + 1):
                    return True
                return rec_full(idx + 1, s, cnt)
            rec_full(0, 0, 0)
        return found

    t0 = time.time()
    log = []
    for rnd in range(max_rounds):
        sat = solver.solve()
        if not sat:
            res = {"n": n, "h": h, "min_degree": min_degree, "result": "UNSAT",
                   "rounds": rnd, "cuts_y": len(y_def),
                   "cuts_m": len(m_def),
                   "elapsed_s": round(time.time() - t0, 1),
                   "meaning": "K4-free face EXCLUDED at this order "
                              "(no K4-free counterexample with "
                              "Delta<=h-1)"}
            json.dump({"summary": res, "log": log},
                      open(outpath, "w", encoding="utf-8"), indent=1)
            print(json.dumps(res), flush=True)
            return res
        model = solver.get_model()
        pos = set(x for x in model if x > 0)
        adj = [0] * n
        edges = 0
        for (u, v), var in E.items():
            if var in pos:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                edges += 1
        sets_found = oracle_admissible(adj, cuts_per_round)
        if not sets_found:
            rec = {"n": n, "h": h, "min_degree": min_degree, "result": "SAT-CANDIDATE",
                   "round": rnd, "edges": edges,
                   "edge_list": sorted([u, v] for (u, v), var in E.items()
                                       if var in pos),
                   "elapsed_s": round(time.time() - t0, 1)}
            json.dump(rec, open(outpath, "w", encoding="utf-8"), indent=1)
            print("!!!! SAT-CANDIDATE: K4-free graph with beta<h "
                  f"at n={n} -> {outpath}", flush=True)
            return rec
        for W in sets_found:
            cut = [y_var(t) for t in itertools.combinations(W, 3)]
            cut += [m_var(p) for p in itertools.combinations(W, 2)]
            solver.add_clause(cut)
        log.append({"round": rnd, "edges": edges,
                    "cuts_added": len(sets_found),
                    "t": round(time.time() - t0, 1)})
        if rnd % 10 == 0:
            print(f"[n={n}] round {rnd} edges={edges} "
                  f"cuts+={len(sets_found)} y={len(y_def)} "
                  f"m={len(m_def)} {time.time()-t0:.0f}s", flush=True)
    res = {"n": n, "h": h, "min_degree": min_degree, "result": "ROUND-CAP-UNKNOWN",
           "rounds": max_rounds, "elapsed_s": round(time.time() - t0, 1)}
    json.dump({"summary": res, "log": log},
              open(outpath, "w", encoding="utf-8"), indent=1)
    print(json.dumps(res), flush=True)
    return res


if __name__ == "__main__":
    n_, h_, r_ = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    min_degree_ = int(sys.argv[5]) if len(sys.argv) >= 6 else 0
    solve_face(n_, h_, r_, sys.argv[4], min_degree=min_degree_)
