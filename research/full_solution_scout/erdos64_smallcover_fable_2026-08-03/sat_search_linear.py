#!/usr/bin/env python3
"""Unified linear-system searcher (static C4+C8, CEGAR C16/C32).

A bipartite graph with sides P (points, |P|=sigma) and L (lines, |L|=m)
and no C4 is exactly a linear hypergraph; its incidence C8s are exactly
"quadrilaterals": 4 points a,b,c,d cyclically collinear via 4 distinct
lines, which under linearity is captured statically by
   -z(ab) v -z(bc) v -z(cd) v -z(da) v c3(abc) v c3(bcd) v c3(cda) v c3(dab)
over the three cyclic orders of every 4-subset (proof: LEDGER entries 3-5).
C16 (and C32 when it fits) are handled by CEGAR.

Modes:
  twodefect h : sigma=m=h, point 0 and line 0 have degree/size 2, all
                others exactly 3.  Hit = bipartite two-defect block F
                (Entry 6) = full counterexample via the bridge doubling.
  cover s     : sigma=s, m free <= C(s,2)/3, sizes >= 3, degrees >= 3
                (the Stage-1/2 family, for cross-checking sat_search.py).
"""
import itertools
import json
import sys
import time
from collections import deque

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195


def build(sigma, m, pt_exact, ln_exact, defect_pt=None, defect_ln=None):
    """pt_exact/ln_exact: exact degree/size for each point/line (None = >=3 free).

    defect_pt/defect_ln: index with degree/size 2 when exact mode.
    """
    pool = IDPool()
    X = {(p, j): pool.id(("x", p, j)) for p in range(sigma) for j in range(m)}
    pairs = list(itertools.combinations(range(sigma), 2))
    triples = list(itertools.combinations(range(sigma), 3))
    Y = {(pq, j): pool.id(("y", pq, j)) for pq in pairs for j in range(m)}
    Z = {pq: pool.id(("z", pq)) for pq in pairs}
    W = {(t, j): pool.id(("w", t, j)) for t in triples for j in range(m)}
    C3 = {t: pool.id(("c3", t)) for t in triples}
    cls = []
    for j in range(m):
        lits = [X[(p, j)] for p in range(sigma)]
        d = 2 if j == defect_ln else 3
        if ln_exact:
            cls.extend(CardEnc.equals(lits=lits, bound=d, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        else:
            cls.extend(CardEnc.atleast(lits=lits, bound=3, vpool=pool,
                                       encoding=EncType.seqcounter).clauses)
    for p in range(sigma):
        lits = [X[(p, j)] for j in range(m)]
        d = 2 if p == defect_pt else 3
        if pt_exact:
            cls.extend(CardEnc.equals(lits=lits, bound=d, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        else:
            cls.extend(CardEnc.atleast(lits=lits, bound=3, vpool=pool,
                                       encoding=EncType.seqcounter).clauses)
    for pq in pairs:
        p, q = pq
        for j in range(m):
            y = Y[(pq, j)]
            cls.append([-y, X[(p, j)]])
            cls.append([-y, X[(q, j)]])
            cls.append([-X[(p, j)], -X[(q, j)], y])
        cls.extend(CardEnc.atmost(lits=[Y[(pq, j)] for j in range(m)], bound=1,
                                  vpool=pool, encoding=EncType.seqcounter).clauses)
        z = Z[pq]
        for j in range(m):
            cls.append([-Y[(pq, j)], z])
        cls.append([-z] + [Y[(pq, j)] for j in range(m)])
    for t in triples:
        a, b, c = t
        for j in range(m):
            w = W[(t, j)]
            cls.append([-w, X[(a, j)]])
            cls.append([-w, X[(b, j)]])
            cls.append([-w, X[(c, j)]])
            cls.append([-X[(a, j)], -X[(b, j)], -X[(c, j)], w])
        cc = C3[t]
        for j in range(m):
            cls.append([-W[(t, j)], cc])
        cls.append([-cc] + [W[(t, j)] for j in range(m)])

    def zv(p, q):
        return Z[(min(p, q), max(p, q))]

    def c3v(a, b, c):
        return C3[tuple(sorted((a, b, c)))]

    for quad in itertools.combinations(range(sigma), 4):
        a, b, c, d = quad
        for cyc in ([a, b, c, d], [a, b, d, c], [a, c, b, d]):
            p0, p1, p2, p3 = cyc
            cls.append([
                -zv(p0, p1), -zv(p1, p2), -zv(p2, p3), -zv(p3, p0),
                c3v(p0, p1, p2), c3v(p1, p2, p3), c3v(p2, p3, p0), c3v(p3, p0, p1)])

    def lex_ge(avars, bvars, tag):
        k = len(avars)
        e = [pool.id(("lexeq", tag, i)) for i in range(k + 1)]
        cls.append([e[0]])
        for i in range(k):
            cls.append([-e[i], avars[i], -bvars[i]])
            cls.append([-e[i + 1], e[i]])
            cls.append([-e[i + 1], avars[i], -bvars[i]])
            cls.append([-e[i + 1], -avars[i], bvars[i]])
            cls.append([-e[i], -avars[i], -bvars[i], e[i + 1]])
            cls.append([-e[i], avars[i], bvars[i], e[i + 1]])
    r0 = 1 if defect_pt == 0 else 0
    c0 = 1 if defect_ln == 0 else 0
    for j in range(c0, m - 1):
        lex_ge([X[(p, j)] for p in range(sigma)], [X[(p, j + 1)] for p in range(sigma)], ("c", j))
    for p in range(r0, sigma - 1):
        lex_ge([X[(p, j)] for j in range(m)], [X[(p + 1, j)] for j in range(m)], ("r", p))
    print(f"sigma={sigma} m={m} vars~{pool.top} clauses={len(cls)}", flush=True)
    return pool, X, cls


def decode(model, X, sigma, m):
    mset = set(model)
    lines = []
    for j in range(m):
        line = frozenset(p for p in range(sigma) if X[(p, j)] in mset)
        lines.append(line)
    return lines


def graph_of(sigma, lines):
    n = sigma + len(lines)
    adj = [[] for _ in range(n)]
    for i, line in enumerate(lines):
        for p in line:
            adj[p].append(sigma + i)
            adj[sigma + i].append(p)
    return n, adj


def bfs_dist(adj, src, n):
    dist = [-1] * n
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def find_cycles_of_length(adj, n, L, cap=256):
    adj_set = [set(a) for a in adj]
    out, seen = [], set()
    for r in range(n):
        if len(out) >= cap:
            break
        dist = bfs_dist(adj, r, n)
        used = [False] * n
        used[r] = True
        path = [r]

        def dfs(v, k):
            if len(out) >= cap:
                return
            if k == L - 1:
                if r in adj_set[v]:
                    key = frozenset(path)
                    if key not in seen:
                        seen.add(key)
                        out.append(list(path))
                return
            for w in adj[v]:
                if w <= r or used[w]:
                    continue
                d = dist[w]
                if d < 0 or d > L - (k + 1):
                    continue
                used[w] = True
                path.append(w)
                dfs(w, k + 1)
                path.pop()
                used[w] = False
        dfs(r, 0)
    return out


def run_twodefect(h, time_budget=None, cap=256):
    pool, X, cls = build(h, h, True, True, defect_pt=0, defect_ln=0)
    solver = Cadical195(bootstrap_with=cls)
    targets = [L for L in (4, 8, 16, 32) if L <= 2 * h]
    t0 = time.time()
    iters = 0
    blocked = {}
    while True:
        if time_budget and time.time() - t0 > time_budget:
            print(json.dumps({"h": h, "status": "TIMEOUT", "iters": iters,
                              "blocked": blocked, "seconds": round(time.time() - t0, 1)}), flush=True)
            return "TIMEOUT"
        if not solver.solve():
            print(json.dumps({"h": h, "status": "UNSAT", "iters": iters,
                              "blocked": blocked, "seconds": round(time.time() - t0, 2)}), flush=True)
            return "UNSAT"
        lines = decode(solver.get_model(), X, h, h)
        n, adj = graph_of(h, lines)
        iters += 1
        bad = []
        for L in targets:
            cyc = find_cycles_of_length(adj, n, L, cap=cap)
            if cyc:
                bad = [(L, c) for c in cyc]
                break
        if not bad:
            edges = [(p, h + i) for i, line in enumerate(lines) for p in line]
            out = {"h": h, "status": "CANDIDATE", "iters": iters, "n": n,
                   "edges": edges, "lines": [sorted(l) for l in lines],
                   "seconds": round(time.time() - t0, 2)}
            fn = f"candidate_linear_twodefect_h{h}_{int(time.time())}.json"
            with open(fn, "w") as f:
                json.dump(out, f, indent=1)
            print(json.dumps({k: out[k] for k in ("h", "status", "iters", "n")}), flush=True)
            print(f"WROTE {fn}", flush=True)
            return "CANDIDATE"
        L = bad[0][0]
        if L in (4, 8):
            print(f"WARNING: static leak C{L}: {bad[0][1]}", flush=True)
        blocked[L] = blocked.get(L, 0) + len(bad)
        for _, cyc in bad:
            lits = []
            for i in range(len(cyc)):
                a, b = cyc[i], cyc[(i + 1) % len(cyc)]
                p, lv = (a, b) if a < h else (b, a)
                lits.append(-X[(p, lv - h)])
            solver.add_clause(lits)
        if iters % 50 == 0:
            print(f"... iter {iters} blocked {blocked} t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "twodefect":
        h = int(sys.argv[2])
        tb = float(sys.argv[3]) if len(sys.argv) > 3 else None
        run_twodefect(h, time_budget=tb)
    else:
        raise SystemExit("unknown mode")
