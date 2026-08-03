#!/usr/bin/env python3
"""Bipartite two-defect block search for Erdős #64.

Target: bipartite F on sides X, Y with |X|=|Y|=h (n=2h, h in 12..15),
degrees all 3 except X[0] and Y[0] which have degree 2, and no cycle of
length 4, 8 or 16 (n<=30 so no larger power fits).

Master equivalence [proved in LEDGER Entry 6]: for such F, let
H_i = F_i + w_i with w_i adjacent to X_i[0], Y_i[0] (two disjoint copies),
G = H_1 + H_2 + bridge w_1w_2.  Then G is cubic, and G has a power-of-two
cycle iff F has a C4, C8 or C16.  So any hit is a full counterexample.

Encoding: biadjacency b[i][j]; row/col degree cards; static C4 via AMO on
common-neighbour pair variables (rows sharing >= 2 columns forbidden);
CEGAR on C8/C16 over the decoded graph.  Symmetry: double-lex on rows
1..h-1 and cols 1..h-1 (defect row/col pinned at index 0).
"""
import itertools
import json
import sys
import time
from collections import deque

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195


def build(h):
    pool = IDPool()
    B = {(i, j): pool.id(("b", i, j)) for i in range(h) for j in range(h)}
    cls = []
    # degrees: row 0 and col 0 have degree 2, others 3 (exact)
    for i in range(h):
        lits = [B[(i, j)] for j in range(h)]
        d = 2 if i == 0 else 3
        cls.extend(CardEnc.equals(lits=lits, bound=d, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    for j in range(h):
        lits = [B[(i, j)] for i in range(h)]
        d = 2 if j == 0 else 3
        cls.extend(CardEnc.equals(lits=lits, bound=d, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    # C4-free: no two rows share two columns
    for i1, i2 in itertools.combinations(range(h), 2):
        for j1, j2 in itertools.combinations(range(h), 2):
            cls.append([-B[(i1, j1)], -B[(i1, j2)], -B[(i2, j1)], -B[(i2, j2)]])
    # symmetry: rows 1..h-1 lex-nonincreasing over columns 0..h-1;
    # cols 1..h-1 lex-nonincreasing (defects pinned at index 0)
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
    for i in range(1, h - 1):
        lex_ge([B[(i, j)] for j in range(h)], [B[(i + 1, j)] for j in range(h)], ("r", i))
    for j in range(1, h - 1):
        lex_ge([B[(i, j)] for i in range(h)], [B[(i, j + 1)] for i in range(h)], ("c", j))
    print(f"h={h} vars~{pool.top} clauses={len(cls)}", flush=True)
    return pool, B, cls


def decode(model, B, h):
    mset = set(model)
    edges = [(i, h + j) for i in range(h) for j in range(h) if B[(i, j)] in mset]
    n = 2 * h
    adj = [[] for _ in range(n)]
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
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


def run(h, time_budget=None, cap=64):
    pool, B, cls = build(h)
    solver = Cadical195(bootstrap_with=cls)
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
        model = solver.get_model()
        n, adj, edges = decode(model, B, h)
        iters += 1
        bad = []
        targets = [L for L in (4, 8, 16, 32) if L <= 2 * h]
        for L in targets:
            cyc = find_cycles_of_length(adj, n, L, cap=cap)
            if cyc:
                bad = [(L, c) for c in cyc]
                break
        if not bad:
            out = {"h": h, "status": "CANDIDATE", "iters": iters, "n": n,
                   "edges": edges, "seconds": round(time.time() - t0, 2)}
            fn = f"candidate_twodefect_h{h}_{int(time.time())}.json"
            with open(fn, "w") as f:
                json.dump(out, f, indent=1)
            print(json.dumps({k: out[k] for k in ("h", "status", "iters", "n")}), flush=True)
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
                x, y = (a, b) if a < b else (b, a)
                lits.append(-B[(x, y - h)])
            solver.add_clause(lits)
        if iters % 100 == 0:
            print(f"... iter {iters} blocked {blocked} t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    h = int(sys.argv[1])
    tb = float(sys.argv[2]) if len(sys.argv) > 2 else None
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 64
    run(h, time_budget=tb, cap=cap)
