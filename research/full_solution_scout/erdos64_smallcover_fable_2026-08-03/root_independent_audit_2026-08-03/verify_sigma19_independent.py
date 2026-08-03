#!/usr/bin/env python3
"""Independent, standard-library audit of ``sigma19_model.json``.

This deliberately imports no campaign searcher or checker.  It validates the
raw graph, the redundant line description, exact small-cycle counts, selected
long-cycle witnesses, distance profiles, and the finite walk-regularity test.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, deque
from pathlib import Path


def canonical_cycle(path: list[int]) -> tuple[int, ...]:
    """Canonicalize an unoriented cycle whose minimum vertex is first."""
    assert path[0] == min(path)
    rev = [path[0], *reversed(path[1:])]
    return min(tuple(path), tuple(rev))


def cycles_of_length(adj: list[set[int]], length: int, cap: int | None = None):
    """Enumerate simple unoriented cycles exactly once, or stop at ``cap``."""
    n = len(adj)
    found: set[tuple[int, ...]] = set()
    for root in range(n):
        used = {root}
        path = [root]

        def dfs(v: int) -> bool:
            if len(path) == length:
                if root in adj[v]:
                    found.add(canonical_cycle(path))
                    return cap is not None and len(found) >= cap
                return False
            for w in sorted(adj[v]):
                # Make root the unique minimum vertex on the cycle.
                if w <= root or w in used:
                    continue
                used.add(w)
                path.append(w)
                if dfs(w):
                    return True
                path.pop()
                used.remove(w)
            return False

        if dfs(root):
            break
    return sorted(found)


def distance_profile(adj: list[set[int]], source: int) -> tuple[int, ...]:
    dist = [-1] * len(adj)
    dist[source] = 0
    queue = deque([source])
    while queue:
        v = queue.popleft()
        for w in adj[v]:
            if dist[w] == -1:
                dist[w] = dist[v] + 1
                queue.append(w)
    assert all(d >= 0 for d in dist)
    counts = Counter(dist)
    return tuple(counts[d] for d in range(max(dist) + 1))


def closed_walk_diagonals(adj: list[set[int]], max_length: int):
    """Return diag(A^k), k=0..max_length, using integer walk DP."""
    n = len(adj)
    out = []
    for source in range(n):
        cur = [0] * n
        cur[source] = 1
        vals = [1]
        for _ in range(max_length):
            nxt = [0] * n
            for v, count in enumerate(cur):
                if count:
                    for w in adj[v]:
                        nxt[w] += count
            cur = nxt
            vals.append(cur[source])
        out.append(vals)
    return [tuple(out[v][k] for v in range(n)) for k in range(max_length + 1)]


def main(model_path: Path, output_path: Path | None = None) -> int:
    raw = model_path.read_bytes()
    data = json.loads(raw)
    n = data["n"]
    raw_edges = [tuple(edge) for edge in data["edges"]]
    normalized = [tuple(sorted(edge)) for edge in raw_edges]

    assert n == 38
    assert len(normalized) == len(set(normalized))
    assert all(0 <= u < v < n for u, v in normalized)

    adj = [set() for _ in range(n)]
    for u, v in normalized:
        adj[u].add(v)
        adj[v].add(u)

    # Independent BFS bipartition, rather than trusting the supplied labels.
    color = [-1] * n
    components = 0
    for seed in range(n):
        if color[seed] != -1:
            continue
        components += 1
        color[seed] = 0
        queue = deque([seed])
        while queue:
            v = queue.popleft()
            for w in adj[v]:
                assert color[w] != color[v]
                if color[w] == -1:
                    color[w] = 1 - color[v]
                    queue.append(w)

    sides = [color.count(0), color.count(1)]
    degrees = [len(a) for a in adj]
    assert components == 1
    assert sorted(sides) == [19, 19]
    assert degrees == [3] * n

    # The redundant hypergraph description must reconstruct exactly the graph.
    supplied_lines = [tuple(sorted(line)) for line in data["lines"]]
    assert len(supplied_lines) == 19
    assert all(len(line) == 3 and len(set(line)) == 3 for line in supplied_lines)
    line_edges = sorted((p, 19 + j) for j, line in enumerate(supplied_lines) for p in line)
    assert sorted(normalized) == line_edges
    point_degrees = Counter(p for line in supplied_lines for p in line)
    assert point_degrees == Counter({p: 3 for p in range(19)})
    pair_degrees = Counter(tuple(sorted((a, b))) for line in supplied_lines for a in line for b in line if a < b)
    assert max(pair_degrees.values()) == 1

    cycles4 = cycles_of_length(adj, 4)
    cycles6 = cycles_of_length(adj, 6)
    cycles8 = cycles_of_length(adj, 8)
    cycles16 = cycles_of_length(adj, 16, cap=1)
    cycles32 = cycles_of_length(adj, 32, cap=1)
    assert not cycles4
    # The handover says "38 hexagons".  Canonical unoriented enumeration
    # gives 19; the handover does not document what convention gave 38.
    assert len(cycles6) == 19
    assert not cycles8
    assert cycles16
    assert cycles32

    profiles = [distance_profile(adj, v) for v in range(n)]
    profile_counts = Counter(profiles)
    assert profile_counts == Counter({(1, 3, 6, 9, 12, 7): 38})

    # A graph on n vertices is walk-regular iff diag(A^k) is constant for
    # k=0,...,n-1; higher powers follow from Cayley-Hamilton.
    diagonals = closed_walk_diagonals(adj, n - 1)
    nonconstant_lengths = [k for k, diag in enumerate(diagonals) if len(set(diag)) != 1]
    assert not nonconstant_lengths

    result = {
        "model": str(model_path),
        "model_sha256": hashlib.sha256(raw).hexdigest(),
        "n": n,
        "edges": len(normalized),
        "connected_components": components,
        "bipartition_sizes": sides,
        "degree_multiset": dict(Counter(degrees)),
        "line_count": len(supplied_lines),
        "line_sizes": dict(Counter(map(len, supplied_lines))),
        "point_degrees": dict(Counter(point_degrees.values())),
        "maximum_pair_multiplicity": max(pair_degrees.values()),
        "cycle_counts": {"4": len(cycles4), "6": len(cycles6), "8": len(cycles8)},
        "cycle16_witness": cycles16[0],
        "cycle32_witness": cycles32[0],
        "distance_profiles": {str(k): v for k, v in profile_counts.items()},
        "walk_regular_test": {
            "checked_closed_walk_lengths": [0, n - 1],
            "nonconstant_lengths": nonconstant_lengths,
        },
        "verdict": "PASS",
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if output_path:
        output_path.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    raise SystemExit(main(src, dst))
