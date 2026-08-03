#!/usr/bin/env python3
"""Small-cover Erdős #64 search, Stage 3: cover S (|S|=sigma) MAY have
internal edges; L independent.  Cycles <= 2*sigma, so for sigma <= 15 the
forbidden lengths are exactly {4,8,16}; for sigma in 16..19 add 32.

Static: linearity (no two lines share a point pair), core C4s, mixed C4s
(2-core-path with collinear endpoints).  CEGAR: C8, C16 (and C32 when
2*sigma >= 32) on the decoded mixed graph, batched blocking clauses.

Any verified model = min-degree-3 graph avoiding all power-of-two cycle
lengths = counterexample to Erdős–Gyárfás.
"""
import itertools
import json
import sys
import time
from collections import deque

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195


def build(sigma):
    M = (sigma * (sigma - 1) // 2) // 3
    pool = IDPool()
    X = {(p, j): pool.id(("x", p, j)) for p in range(sigma) for j in range(M)}
    U = {j: pool.id(("u", j)) for j in range(M)}
    pairs = list(itertools.combinations(range(sigma), 2))
    E = {pq: pool.id(("e", pq)) for pq in pairs}
    Y = {(pq, j): pool.id(("y", pq, j)) for pq in pairs for j in range(M)}
    Z = {pq: pool.id(("z", pq)) for pq in pairs}
    cls = []
    for j in range(M):
        for p in range(sigma):
            cls.append([-X[(p, j)], U[j]])
    for j in range(M - 1):
        cls.append([-U[j + 1], U[j]])
    for j in range(M):
        a = [pool.id(("alias", j, k)) for k in range(3)]
        for k in range(3):
            cls.append([U[j], a[k]])
            cls.append([-a[k], -U[j]])
        lits = [X[(p, j)] for p in range(sigma)] + a
        enc = CardEnc.atleast(lits=lits, bound=3, vpool=pool, encoding=EncType.seqcounter)
        cls.extend(enc.clauses)
    # degrees on S: lines + core edges >= 3
    for p in range(sigma):
        lits = [X[(p, j)] for j in range(M)]
        lits += [E[(min(p, q), max(p, q))] for q in range(sigma) if q != p]
        enc = CardEnc.atleast(lits=lits, bound=3, vpool=pool, encoding=EncType.seqcounter)
        cls.extend(enc.clauses)
    # y defs + linearity + z defs
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
        z = Z[pq]
        for j in range(M):
            cls.append([-Y[(pq, j)], z])
        cls.append([-z] + [Y[(pq, j)] for j in range(M)])

    def ev(p, q):
        return E[(min(p, q), max(p, q))]

    def zv(p, q):
        return Z[(min(p, q), max(p, q))]

    # core C4s
    for quad in itertools.combinations(range(sigma), 4):
        a, b, c, d = quad
        for cyc in ([a, b, c, d], [a, b, d, c], [a, c, b, d]):
            p0, p1, p2, p3 = cyc
            cls.append([-ev(p0, p1), -ev(p1, p2), -ev(p2, p3), -ev(p3, p0)])
    # mixed C4s: p-q-r core path + p,r collinear
    for p, r in pairs:
        for q in range(sigma):
            if q == p or q == r:
                continue
            cls.append([-ev(p, q), -ev(q, r), -zv(p, r)])
    # column lex symmetry (lines only; core untouched by line permutation)
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
    for j in range(M - 1):
        lex_ge([X[(p, j)] for p in range(sigma)], [X[(p, j + 1)] for p in range(sigma)], ("c", j))
    print(f"sigma={sigma} M={M} vars~{pool.top} clauses={len(cls)}", flush=True)
    return pool, X, U, E, M, cls


def decode(model, X, U, E, sigma, M):
    mset = set(model)
    lines = []
    for j in range(M):
        if U[j] in mset:
            line = frozenset(p for p in range(sigma) if X[(p, j)] in mset)
            lines.append((j, line))
    core = [pq for pq, v in E.items() if v in mset]
    return lines, core


def mixed_graph(sigma, lines, core):
    n = sigma + len(lines)
    adj = [[] for _ in range(n)]
    edges = []
    for (p, q) in core:
        adj[p].append(q)
        adj[q].append(p)
        edges.append((p, q, "core"))
    for i, (_, line) in enumerate(lines):
        lv = sigma + i
        for p in sorted(line):
            adj[p].append(lv)
            adj[lv].append(p)
            edges.append((p, lv, "inc"))
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


def find_cycles_of_length(adj, n, L, cap=64):
    """Collect up to `cap` distinct simple cycles of length exactly L."""
    adj_set = [set(a) for a in adj]
    out = []
    seen = set()
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


def run(sigma, time_budget=None, cap=64):
    pool, X, U, E, M, cls = build(sigma)
    targets = [L for L in (4, 8, 16, 32) if L <= 2 * sigma]
    solver = Cadical195(bootstrap_with=cls)
    t0 = time.time()
    iters = 0
    blocked = {}
    while True:
        if time_budget and time.time() - t0 > time_budget:
            print(json.dumps({"sigma": sigma, "status": "TIMEOUT", "iters": iters,
                              "blocked": blocked, "seconds": round(time.time() - t0, 1)}), flush=True)
            return "TIMEOUT"
        if not solver.solve():
            print(json.dumps({"sigma": sigma, "status": "UNSAT", "iters": iters,
                              "blocked": blocked, "seconds": round(time.time() - t0, 2)}), flush=True)
            return "UNSAT"
        model = solver.get_model()
        lines, core = decode(model, X, U, E, sigma, M)
        n, adj, edges = mixed_graph(sigma, lines, core)
        iters += 1
        bad = []
        for L in targets:
            cyc = find_cycles_of_length(adj, n, L, cap=cap)
            if cyc:
                bad = [(L, c) for c in cyc]
                break
        if not bad:
            out = {
                "sigma": sigma, "status": "CANDIDATE", "iters": iters,
                "m_lines": len(lines), "n": n,
                "lines": [sorted(line) for _, line in lines],
                "core_edges": [list(pq) for pq in core],
                "seconds": round(time.time() - t0, 2),
            }
            fn = f"candidate_core_sigma{sigma}_{int(time.time())}.json"
            with open(fn, "w") as f:
                json.dump(out, f, indent=1)
            print(json.dumps({k: out[k] for k in ("sigma", "status", "iters", "m_lines", "n")}), flush=True)
            print(f"WROTE {fn}", flush=True)
            return "CANDIDATE"
        L = bad[0][0]
        if L == 4:
            print(f"WARNING: static C4 leaked: {bad[0][1]}", flush=True)
        blocked[L] = blocked.get(L, 0) + len(bad)
        for _, cyc in bad:
            lits = []
            for i in range(len(cyc)):
                a, b = cyc[i], cyc[(i + 1) % len(cyc)]
                if a < sigma and b < sigma:
                    lits.append(-E[(min(a, b), max(a, b))])
                else:
                    p, lv = (a, b) if a < sigma else (b, a)
                    j = lines[lv - sigma][0]
                    lits.append(-X[(p, j)])
            solver.add_clause(lits)
        if iters % 100 == 0:
            print(f"... iter {iters} blocked {blocked} t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    sigma = int(sys.argv[1])
    tb = float(sys.argv[2]) if len(sys.argv) > 2 else None
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 64
    run(sigma, time_budget=tb, cap=cap)
