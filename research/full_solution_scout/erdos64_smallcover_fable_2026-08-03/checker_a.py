#!/usr/bin/env python3
"""Checker A: standard-library-only exact cycle-length existence checker.

Input: JSON {"n": int, "edges": [[u,v], ...]} (0-indexed vertices).
For each target length L (default: all powers of two up to n), decide
whether a simple cycle of length exactly L exists, by exhaustive rooted
DFS with distance pruning.  Also reports minimum degree, simplicity,
and the full sorted degree sequence.

This file is deliberately self-contained and shares no code with the
SAT searcher; it is one of the two independent verifiers.
"""
import json
import sys
from collections import deque


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


def has_cycle_of_length(adj, n, L):
    """Exact: does a simple cycle of length exactly L exist?

    Roots on the minimum-labelled vertex of the cycle: for each root r,
    search simple paths from r using only vertices > r, and close back
    to r at exactly length L.  Distance pruning: from current vertex v
    with k edges used, need dist_r(v) <= L - k.
    """
    if L < 3 or L > n:
        return None  # impossible trivially
    for r in range(n):
        dist = bfs_dist(adj, r, n)
        # restrict to vertices >= r reachable within budget
        used = [False] * n
        used[r] = True
        found = [False]

        def dfs(v, k):
            # k edges used from r to v along the path
            if found[0]:
                return
            if k == L - 1:
                # need edge v->r to close
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
                if found[0]:
                    return

        adj_set = [set(a) for a in adj]
        dfs(r, 0)
        if found[0]:
            return True
    return False


def main(path):
    with open(path) as f:
        data = json.load(f)
    n = data["n"]
    edges = [tuple(e) for e in data["edges"]]
    # simplicity
    seen = set()
    simple = True
    for (u, v) in edges:
        if u == v or (u, v) in seen or (v, u) in seen:
            simple = False
        seen.add((u, v))
    adj = [[] for _ in range(n)]
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    degs = sorted(len(a) for a in adj)
    mind = degs[0] if degs else 0
    targets = []
    L = 4
    while L <= n:
        targets.append(L)
        L *= 2
    report = {
        "n": n,
        "m_edges": len(edges),
        "simple": simple,
        "min_degree": mind,
        "degree_sequence_head": degs[:10],
        "power_of_two_cycles": {},
    }
    counterexample = simple and mind >= 3
    for L in targets:
        present = has_cycle_of_length(adj, n, L)
        report["power_of_two_cycles"][str(L)] = bool(present)
        if present:
            counterexample = False
    report["is_counterexample"] = counterexample
    print(json.dumps(report, indent=1))
    return 0 if counterexample else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
