#!/usr/bin/env python3
"""Small-cover core search v2.

Adds over v1:
  - static pure-incidence C8 (quadrilateral clauses via z/c3);
  - static mixed C8 with 3 lines + 2 core edges (t=3 pattern):
      cycle a L1 b L2 c L3 d - e - a  =>
      -z(ab) v -z(bc) v -z(cd) v -e(de) v -e(ea) v c3(abc) v c3(bcd);
  - adjacent-transposition graph-lex symmetry on points over the combined
    (core-row, incidence-row) vectors;
  - CEGAR for remaining C8 shapes (t<=2) and C16 (+C32 if 2*sigma>=32).
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
    triples = list(itertools.combinations(range(sigma), 3))
    E = {pq: pool.id(("e", pq)) for pq in pairs}
    Y = {(pq, j): pool.id(("y", pq, j)) for pq in pairs for j in range(M)}
    Z = {pq: pool.id(("z", pq)) for pq in pairs}
    W = {(t, j): pool.id(("w", t, j)) for t in triples for j in range(M)}
    C3 = {t: pool.id(("c3", t)) for t in triples}
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
        cls.extend(CardEnc.atleast(lits=lits, bound=3, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)
    for p in range(sigma):
        lits = [X[(p, j)] for j in range(M)]
        lits += [E[(min(p, q), max(p, q))] for q in range(sigma) if q != p]
        cls.extend(CardEnc.atleast(lits=lits, bound=3, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)
    for pq in pairs:
        p, q = pq
        for j in range(M):
            y = Y[(pq, j)]
            cls.append([-y, X[(p, j)]])
            cls.append([-y, X[(q, j)]])
            cls.append([-X[(p, j)], -X[(q, j)], y])
        cls.extend(CardEnc.atmost(lits=[Y[(pq, j)] for j in range(M)], bound=1,
                                  vpool=pool, encoding=EncType.seqcounter).clauses)
        z = Z[pq]
        for j in range(M):
            cls.append([-Y[(pq, j)], z])
        cls.append([-z] + [Y[(pq, j)] for j in range(M)])
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

    def ev(p, q):
        return E[(min(p, q), max(p, q))]

    def zv(p, q):
        return Z[(min(p, q), max(p, q))]

    def c3v(a, b, c):
        return C3[tuple(sorted((a, b, c)))]

    # core C4 + mixed C4
    for quad in itertools.combinations(range(sigma), 4):
        a, b, c, d = quad
        for cyc in ([a, b, c, d], [a, b, d, c], [a, c, b, d]):
            p0, p1, p2, p3 = cyc
            cls.append([-ev(p0, p1), -ev(p1, p2), -ev(p2, p3), -ev(p3, p0)])
    for p, r in pairs:
        for q in range(sigma):
            if q == p or q == r:
                continue
            cls.append([-ev(p, q), -ev(q, r), -zv(p, r)])
    # pure incidence C8 (quadrilaterals)
    for quad in itertools.combinations(range(sigma), 4):
        a, b, c, d = quad
        for cyc in ([a, b, c, d], [a, b, d, c], [a, c, b, d]):
            p0, p1, p2, p3 = cyc
            cls.append([
                -zv(p0, p1), -zv(p1, p2), -zv(p2, p3), -zv(p3, p0),
                c3v(p0, p1, p2), c3v(p1, p2, p3), c3v(p2, p3, p0), c3v(p3, p0, p1)])
    # t=3 mixed C8, shape A (adjacent core edges): a L1 b L2 c L3 d - e - a
    cnt3 = 0
    for a, b, c, d in itertools.permutations(range(sigma), 4):
        if a > d:
            continue  # reflection canon
        for e_ in range(sigma):
            if e_ in (a, b, c, d):
                continue
            cls.append([-zv(a, b), -zv(b, c), -zv(c, d), -ev(d, e_), -ev(e_, a),
                        c3v(a, b, c), c3v(b, c, d)])
            cnt3 += 1
    # t=3 mixed C8, shape B (separated core edges), gap pattern (2,3,3):
    # cycle e L1 a L2 b - c L3 d - e:  z(ea), z(ab), core(bc), z(cd), core(de)
    # Degeneracies: L1=L2 <=> c3(eab) [exact, consecutive-anchored];
    # L2=L3 <=> c3(abc) AND c3(abd); L1=L3 <=> c3(eac) AND c3(ead).
    # Conjunctions expand into 4 clauses per pattern (sound and complete).
    for a, b, c, d, e_ in itertools.permutations(range(sigma), 5):
        if b > e_:
            continue  # reflection canon: (a,b,c,d,e) ~ (a,e,d,c,b)
        base = [-zv(e_, a), -zv(a, b), -ev(b, c), -zv(c, d), -ev(d, e_),
                c3v(e_, a, b)]
        for x1 in (c3v(a, b, c), c3v(a, b, d)):
            for x2 in (c3v(e_, a, c), c3v(e_, a, d)):
                cls.append(base + [x1, x2])
        cnt3 += 4
    # symmetry: adjacent-transposition graph-lex on points
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
    for p in range(sigma - 1):
        q = p + 1
        others = [r for r in range(sigma) if r not in (p, q)]
        A = [ev(p, r) for r in others] + [X[(p, j)] for j in range(M)]
        B = [ev(q, r) for r in others] + [X[(q, j)] for j in range(M)]
        lex_ge(A, B, ("pt", p))
    for j in range(M - 1):
        lex_ge([X[(p, j)] for p in range(sigma)], [X[(p, j + 1)] for p in range(sigma)], ("c", j))
    print(f"sigma={sigma} M={M} vars~{pool.top} clauses={len(cls)} t3={cnt3}", flush=True)
    return pool, X, U, E, M, cls


def decode(model, X, U, E, sigma, M):
    mset = set(model)
    lines = []
    for j in range(M):
        if U[j] in mset:
            lines.append((j, frozenset(p for p in range(sigma) if X[(p, j)] in mset)))
    core = [pq for pq, v in E.items() if v in mset]
    return lines, core


def mixed_graph(sigma, lines, core):
    n = sigma + len(lines)
    adj = [[] for _ in range(n)]
    for (p, q) in core:
        adj[p].append(q)
        adj[q].append(p)
    for i, (_, line) in enumerate(lines):
        lv = sigma + i
        for p in line:
            adj[p].append(lv)
            adj[lv].append(p)
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


def run(sigma, time_budget=None, cap=256, blocks_path=None):
    pool, X, U, E, M, cls = build(sigma)
    targets = [L for L in (4, 8, 16, 32) if L <= 2 * sigma]
    solver = Cadical195(bootstrap_with=cls)
    t0 = time.time()
    iters = 0
    blocked = {}
    hist = {}
    nresumed = 0
    bf = None
    if blocks_path:
        try:
            with open(blocks_path) as f:
                for line in f:
                    lits = json.loads(line)
                    solver.add_clause(lits)
                    nresumed += 1
        except FileNotFoundError:
            pass
        bf = open(blocks_path, "a")
        print(f"resumed {nresumed} blocking clauses", flush=True)
    while True:
        if time_budget and time.time() - t0 > time_budget:
            print(json.dumps({"sigma": sigma, "status": "TIMEOUT", "iters": iters,
                              "blocked": blocked, "hist": hist,
                              "seconds": round(time.time() - t0, 1)}), flush=True)
            return "TIMEOUT"
        if not solver.solve():
            print(json.dumps({"sigma": sigma, "status": "UNSAT", "iters": iters,
                              "blocked": blocked, "hist": hist,
                              "seconds": round(time.time() - t0, 2)}), flush=True)
            return "UNSAT"
        model = solver.get_model()
        lines, core = decode(model, X, U, E, sigma, M)
        n, adj = mixed_graph(sigma, lines, core)
        iters += 1
        bad = []
        for L in targets:
            cyc = find_cycles_of_length(adj, n, L, cap=cap)
            if cyc:
                bad = [(L, c) for c in cyc]
                break
        if not bad:
            out = {"sigma": sigma, "status": "CANDIDATE", "iters": iters,
                   "m_lines": len(lines), "n": n,
                   "lines": [sorted(line) for _, line in lines],
                   "core_edges": [list(pq) for pq in core],
                   "seconds": round(time.time() - t0, 2)}
            fn = f"candidate_core2_sigma{sigma}_{int(time.time())}.json"
            with open(fn, "w") as f:
                json.dump(out, f, indent=1)
            print(json.dumps({k: out[k] for k in ("sigma", "status", "iters", "m_lines", "n")}), flush=True)
            print(f"WROTE {fn}", flush=True)
            return "CANDIDATE"
        L = bad[0][0]
        blocked[L] = blocked.get(L, 0) + len(bad)
        for _, cyc in bad:
            t = sum(1 for v in cyc if v >= sigma)
            if L == 8:
                hist[t] = hist.get(t, 0) + 1
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
            if bf:
                bf.write(json.dumps(lits) + "\n")
        if bf:
            bf.flush()
        if iters % 100 == 0:
            print(f"... iter {iters} blocked {blocked} hist {hist} t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    sigma = int(sys.argv[1])
    tb = float(sys.argv[2]) if len(sys.argv) > 2 else None
    bp = sys.argv[3] if len(sys.argv) > 3 else None
    run(sigma, time_budget=tb, blocks_path=bp)
