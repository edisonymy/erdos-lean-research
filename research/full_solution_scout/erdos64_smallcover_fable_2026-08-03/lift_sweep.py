#!/usr/bin/env python3
"""Lane 3: cyclic voltage-lift sweep for dyadic-cycle-free cubic graphs.

For a cubic base B and modulus m, assign voltages in Z_m to cotree edges
(tree edges 0).  The lift has n = |B|*m vertices and is cubic.  We scan
lifts with n <= NMAX (so only powers of two up to 64 matter), filtering:
girth >= 9 kills C4/C8; then exact C16, C32, C64 checks by rooted DFS
with distance pruning.  Any survivor is a full counterexample (cubic!).

Enumeration: full when m^r <= FULL_CAP, else random sampling.
Scoring for the log: first dyadic length present.
"""
import itertools
import json
import random
import sys
import time
from collections import deque

BASES = {}


def add_base(name, n, edges):
    BASES[name] = (n, sorted((min(u, v), max(u, v)) for (u, v) in edges))


def lcf(n, lst, reps):
    edges = set()
    for i in range(n):
        edges.add((min(i, (i + 1) % n), max(i, (i + 1) % n)))
    full = lst * reps
    for i, s in enumerate(full):
        j = (i + s) % n
        edges.add((min(i, j), max(i, j)))
    return sorted(edges)


add_base("k33", 6, [(0, 3), (0, 4), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5)])
add_base("q3", 8, [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6), (3, 7),
                   (4, 5), (4, 6), (5, 7), (6, 7)])
add_base("heawood", 14, lcf(14, [5, -5], 7))
add_base("moebiuskantor", 16, lcf(16, [5, -5], 8))
add_base("pappus", 18, lcf(18, [5, 7, -7, 7, -7, -5], 3))
add_base("desargues", 20, lcf(20, [5, -5, 9, -9], 5))
add_base("tuttecoxeter", 30, lcf(30, [-13, -9, 7, -7, 9, 13], 5))
add_base("petersen", 10, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (1, 6), (2, 7),
                          (3, 8), (4, 9), (5, 7), (7, 9), (9, 6), (6, 8), (8, 5)])


def spanning_tree(n, edges):
    adj = {}
    for (u, v) in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    seen = {0}
    tree = set()
    q = deque([0])
    par = {}
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                tree.add((min(u, v), max(u, v)))
                q.append(v)
    return tree


def build_lift(n, edges, tree, volts, m):
    N = n * m
    adj = [[] for _ in range(N)]
    cot = [e for e in edges if e not in tree]
    volt_map = {e: 0 for e in tree}
    for e, a in zip(cot, volts):
        volt_map[e] = a
    for (u, v) in edges:
        a = volt_map[(u, v)]
        for i in range(m):
            x = u * m + i
            y = v * m + ((i + a) % m)
            adj[x].append(y)
            adj[y].append(x)
    return N, adj


def girth_at_most(adj, N, g):
    # BFS-based girth: returns True if girth <= g
    best = 10 ** 9
    for r in range(N):
        dist = [-1] * N
        par = [-1] * N
        dist[r] = 0
        q = deque([r])
        while q:
            u = q.popleft()
            if 2 * dist[u] >= best or 2 * dist[u] >= g:  # threshold prune only when g small
                continue
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    par[v] = u
                    q.append(v)
                elif par[u] != v:
                    c = dist[u] + dist[v] + 1
                    if c < best:
                        best = c
                        if best <= g:
                            return True, best
    return best <= g, best


def bfs_dist(adj, src, N):
    dist = [-1] * N
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def has_cycle_len(adj, N, L, roots=None, deadline=None):
    adj_set = [set(a) for a in adj]
    rng = range(N) if roots is None else roots
    for r in rng:
        dist = bfs_dist(adj, r, N)
        used = [False] * N
        used[r] = True
        found = [False]

        def dfs(v, k):
            if found[0] or (deadline and time.time() > deadline):
                return
            if k == L - 1:
                if r in adj_set[v]:
                    found[0] = True
                return
            for w in adj[v]:
                if w <= r or used[w]:
                    continue
                d = dist[w]
                if d < 0 or d > L - (k + 1):
                    continue
                used[w] = True
                dfs(w, k + 1)
                used[w] = False
        dfs(r, 0)
        if found[0]:
            return True
        if deadline and time.time() > deadline:
            return None
    return False


def scan(base, m, budget_s, full_cap=200000, nmax=126, seed=1):
    n, edges = BASES[base]
    if n * m > nmax:
        return
    tree = spanning_tree(n, edges)
    r = len(edges) - len(tree)
    total = m ** r
    rng = random.Random(seed)
    t0 = time.time()
    best = None
    tried = 0
    survivors = []

    def volt_iter():
        if total <= full_cap:
            yield from itertools.product(range(m), repeat=r)
        else:
            while True:
                yield tuple(rng.randrange(m) for _ in range(r))

    for volts in volt_iter():
        if time.time() - t0 > budget_s:
            break
        tried += 1
        N, adj = build_lift(n, edges, tree, volts, m)
        _, g = girth_at_most(adj, N, 10 ** 9)  # exact girth
        if g in (4, 8, 16, 32, 64):
            continue  # dyadic girth: dead immediately
        res = {"volts": volts, "girth": g}
        ok = True
        todo = [L for L in (8, 16, 32, 64) if g < L <= N]
        for L in todo:
            has = has_cycle_len(adj, N, L, deadline=time.time() + 120)
            if has is None:
                res[f"C{L}"] = "TIMEOUT"
                ok = False
                break
            res[f"C{L}"] = has
            if has:
                ok = False
                break
        if ok:
            survivors.append(res)
            print(json.dumps({"base": base, "m": m, "SURVIVOR": res}), flush=True)
            with open(f"lift_survivor_{base}_{m}_{tried}.json", "w") as f:
                json.dump({"base": base, "m": m, "n": N, "volts": list(volts),
                           "edges": [[u, v] for u in range(N) for v in adj[u] if u < v]}, f)
        else:
            if best is None:
                best = res
    print(json.dumps({"base": base, "m": m, "n": n * m, "rank": r, "tried": tried,
                      "girth9_examples": best, "survivors": len(survivors),
                      "seconds": round(time.time() - t0, 1)}), flush=True)


if __name__ == "__main__":
    seed = 20260803
    plan = []
    for base, mmax in [("heawood", 9), ("moebiuskantor", 7), ("pappus", 7),
                       ("desargues", 6), ("tuttecoxeter", 4), ("k33", 21),
                       ("q3", 15), ("petersen", 12)]:
        for m in range(3, mmax + 1):
            plan.append((base, m))
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 60
    for base, m in plan:
        scan(base, m, budget, seed=seed)
