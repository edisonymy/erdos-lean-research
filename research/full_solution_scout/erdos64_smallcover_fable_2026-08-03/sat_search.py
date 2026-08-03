#!/usr/bin/env python3
"""Small-cover Erdős #64 search, Stage 1+2 (pure bipartite).

Object: linear hypergraph on sigma points, m <= floor(C(sigma,2)/3) lines,
line sizes >= 3, point degrees >= 3, incidence graph avoiding C8 and C16
(C4 impossible by linearity).  Any model is a minimum-degree-3 bipartite
graph whose cycles all have length <= 2*sigma <= 30 and avoid {4,8,16},
i.e. a counterexample to Erdős--Gyárfás.

Encoding:
  x[p][j]  point p on line j
  u[j]     line j used (monotone: used lines form a prefix)
  y[pq][j] <-> x[p][j] & x[q][j];  sum_j y[pq][j] <= 1  (linearity => no C4)
  z[pq]    <-> OR_j y[pq][j]       (p,q collinear)
  w[abc][j]<-> x&x&x;  c3[abc] <-> OR_j w  (triple collinear)
  C8 static: for each 4-subset and each of 3 cyclic orders:
     -z01 v -z12 v -z23 v -z30 v c3(012) v c3(123) v c3(230) v c3(301)
  C16: CEGAR with exact 16-cycle finder on the decoded incidence graph.
Symmetry: u-prefix; double-lex (cols >=lex next col among first MAXLEX;
rows >=lex next row) -- both satisfiability-preserving.
"""
import itertools
import json
import sys
import time
from collections import deque

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195


def build(sigma, exact3=False, verbose=True, symmetry=True):
    M = (sigma * (sigma - 1) // 2) // 3
    pool = IDPool()
    X = {(p, j): pool.id(("x", p, j)) for p in range(sigma) for j in range(M)}
    U = {j: pool.id(("u", j)) for j in range(M)}
    pairs = list(itertools.combinations(range(sigma), 2))
    triples = list(itertools.combinations(range(sigma), 3))
    Y = {(pq, j): pool.id(("y", pq, j)) for pq in pairs for j in range(M)}
    Z = {pq: pool.id(("z", pq)) for pq in pairs}
    W = {(t, j): pool.id(("w", t, j)) for t in triples for j in range(M)}
    C3 = {t: pool.id(("c3", t)) for t in triples}
    cls = []
    # x -> u ; u prefix monotone
    for j in range(M):
        for p in range(sigma):
            cls.append([-X[(p, j)], U[j]])
    for j in range(M - 1):
        cls.append([-U[j + 1], U[j]])
    # u -> line size >= 3 (aliases for -u counted three times)
    for j in range(M):
        a = [pool.id(("alias", j, k)) for k in range(3)]
        for k in range(3):
            cls.append([U[j], a[k]])       # -u -> alias true
            cls.append([-a[k], -U[j]])     # alias -> -u
        lits = [X[(p, j)] for p in range(sigma)] + a
        enc = CardEnc.atleast(lits=lits, bound=3, vpool=pool, encoding=EncType.seqcounter)
        cls.extend(enc.clauses)
        if exact3:
            enc2 = CardEnc.atmost(lits=[X[(p, j)] for p in range(sigma)], bound=3,
                                  vpool=pool, encoding=EncType.seqcounter)
            cls.extend(enc2.clauses)
    # point degrees >= 3
    for p in range(sigma):
        enc = CardEnc.atleast(lits=[X[(p, j)] for j in range(M)], bound=3,
                              vpool=pool, encoding=EncType.seqcounter)
        cls.extend(enc.clauses)
    # y defs + linearity
    for pq in pairs:
        p, q = pq
        for j in range(M):
            y = Y[(pq, j)]
            cls.append([-y, X[(p, j)]])
            cls.append([-y, X[(q, j)]])
            cls.append([-X[(p, j)], -X[(q, j)], y])
        enc = CardEnc.atmost(lits=[Y[(pq, j)] for j in range(M)], bound=1,
                             vpool=pool, encoding=EncType.seqcounter)
        cls.extend(enc.clauses)
        # z defs
        z = Z[pq]
        for j in range(M):
            cls.append([-Y[(pq, j)], z])
        cls.append([-z] + [Y[(pq, j)] for j in range(M)])
    # w defs + c3
    for t in triples:
        a, b, c = t
        for j in range(M):
            w = W[(t, j)]
            cls.append([-w, X[(a, j)]])
            cls.append([-w, X[(b, j)]])
            cls.append([-w, X[(c, j)]])
            cls.append([-X[(a, j)], -X[(b, j)], -X[(c, j)], w])
        cc = C3[t]
        for j in range(M):
            cls.append([-W[(t, j)], cc])
        cls.append([-cc] + [W[(t, j)] for j in range(M)])
    # C8 static
    def zv(p, q):
        return Z[(min(p, q), max(p, q))]

    def c3v(a, b, c):
        return C3[tuple(sorted((a, b, c)))]

    nquad = 0
    for quad in itertools.combinations(range(sigma), 4):
        a, b, c, d = quad
        for cyc in ([a, b, c, d], [a, b, d, c], [a, c, b, d]):
            p0, p1, p2, p3 = cyc
            cls.append([
                -zv(p0, p1), -zv(p1, p2), -zv(p2, p3), -zv(p3, p0),
                c3v(p0, p1, p2), c3v(p1, p2, p3), c3v(p2, p3, p0), c3v(p3, p0, p1),
            ])
            nquad += 1
    # symmetry: double lex.  col_j >=lex col_{j+1}; row_p >=lex row_{p+1}
    def lex_ge(avars, bvars, tag):
        # a >=lex b.  e_k: prefixes equal up to k.
        k = len(avars)
        e = [pool.id(("lexeq", tag, i)) for i in range(k + 1)]
        cls.append([e[0]])
        for i in range(k):
            # e[i] -> (a_i >= b_i):  -e[i] v a_i v -b_i
            cls.append([-e[i], avars[i], -bvars[i]])
            # e[i+1] <-> e[i] & (a_i == b_i)  (only -> needed for soundness of use)
            cls.append([-e[i + 1], e[i]])
            cls.append([-e[i + 1], avars[i], -bvars[i]])
            cls.append([-e[i + 1], -avars[i], bvars[i]])
            cls.append([-e[i], -avars[i], -bvars[i], e[i + 1]])
            cls.append([-e[i], avars[i], bvars[i], e[i + 1]])
    if symmetry:
        for j in range(M - 1):
            lex_ge([X[(p, j)] for p in range(sigma)], [X[(p, j + 1)] for p in range(sigma)], ("c", j))
        for p in range(sigma - 1):
            lex_ge([X[(p, j)] for j in range(M)], [X[(p + 1, j)] for j in range(M)], ("r", p))
    if verbose:
        print(f"sigma={sigma} M={M} vars~{pool.top} clauses={len(cls)} quadclauses={nquad}", flush=True)
    return pool, X, U, M, cls


def decode(model, X, U, sigma, M):
    mset = set(model)
    lines = []
    for j in range(M):
        if U[j] in mset:
            line = frozenset(p for p in range(sigma) if X[(p, j)] in mset)
            lines.append((j, line))
    return lines


def incidence_graph(sigma, lines):
    # vertices 0..sigma-1 points; sigma+i for i-th used line
    n = sigma + len(lines)
    adj = [[] for _ in range(n)]
    edges = []
    for i, (_, line) in enumerate(lines):
        lv = sigma + i
        for p in sorted(line):
            adj[p].append(lv)
            adj[lv].append(p)
            edges.append((p, lv))
    return n, adj, edges


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


def find_cycle_of_length(adj, n, L):
    """Return a list of vertices of one simple cycle of length exactly L, or None."""
    adj_set = [set(a) for a in adj]
    for r in range(n):
        dist = bfs_dist(adj, r, n)
        used = [False] * n
        used[r] = True
        path = [r]
        res = []

        def dfs(v, k):
            if res:
                return
            if k == L - 1:
                if r in adj_set[v]:
                    res.append(list(path))
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
                if res:
                    return
        dfs(r, 0)
        if res:
            return res[0]
    return None


def run(sigma, exact3=False, max_iters=200000, time_budget=None):
    pool, X, U, M, cls = build(sigma, exact3=exact3)
    solver = Cadical195(bootstrap_with=cls)
    t0 = time.time()
    iters = 0
    blocked = {8: 0, 16: 0}
    while True:
        if time_budget and time.time() - t0 > time_budget:
            print(json.dumps({"sigma": sigma, "status": "TIMEOUT", "iters": iters,
                              "blocked": blocked, "seconds": time.time() - t0}), flush=True)
            return "TIMEOUT"
        sat = solver.solve()
        if not sat:
            print(json.dumps({"sigma": sigma, "status": "UNSAT", "iters": iters,
                              "blocked": blocked, "seconds": round(time.time() - t0, 2)}), flush=True)
            return "UNSAT"
        model = solver.get_model()
        lines = decode(model, X, U, sigma, M)
        n, adj, edges = incidence_graph(sigma, lines)
        # sanity: C4 and C8 must be impossible; check anyway
        bad = None
        for L in [t for t in (4, 8, 16, 32) if t <= 2 * sigma]:
            cyc = find_cycle_of_length(adj, n, L)
            if cyc is not None:
                bad = (L, cyc)
                break
        iters += 1
        if bad is None:
            out = {
                "sigma": sigma, "status": "CANDIDATE", "iters": iters,
                "m_lines": len(lines), "n": n,
                "lines": [sorted(line) for _, line in lines],
                "edges": edges,
                "seconds": round(time.time() - t0, 2),
            }
            fn = f"candidate_sigma{sigma}_{int(time.time())}.json"
            with open(fn, "w") as f:
                json.dump(out, f, indent=1)
            print(json.dumps({k: out[k] for k in ("sigma", "status", "iters", "m_lines", "n")}), flush=True)
            print(f"WROTE {fn}", flush=True)
            return "CANDIDATE"
        L, cyc = bad
        if L in (4, 8):
            print(f"WARNING: static encoding leaked C{L}: {cyc}", flush=True)
        blocked[L] = blocked.get(L, 0) + 1
        # block: at least one incidence on the cycle must go
        lits = []
        for i in range(len(cyc)):
            a, b = cyc[i], cyc[(i + 1) % len(cyc)]
            p, lv = (a, b) if a < sigma else (b, a)
            j = lines[lv - sigma][0]
            lits.append(-X[(p, j)])
        solver.add_clause(lits)
        if iters % 200 == 0:
            print(f"... iter {iters} blocked {blocked} t={time.time()-t0:.0f}s", flush=True)
        if iters >= max_iters:
            print(json.dumps({"sigma": sigma, "status": "ITER_CAP", "iters": iters}), flush=True)
            return "ITER_CAP"


if __name__ == "__main__":
    sigma = int(sys.argv[1])
    exact3 = len(sys.argv) > 2 and sys.argv[2] == "exact3"
    tb = float(sys.argv[3]) if len(sys.argv) > 3 else None
    run(sigma, exact3=exact3, time_budget=tb)
