#!/usr/bin/env python3
"""Exhaustive counterexample probe for the first uncovered #561 tuple.

The symmetric target is F = K_{1,2} disjoint-union K_{1,1}.  For
(n_1,n_2)=(m_1,m_2)=(2,1), the Burr--Erdos--Faudree--Rousseau--Schelp
formula predicts size-Ramsey number 3+2+1 = 6.  A graph with at most five
edges that arrows (F,F) would therefore refute the full conjecture.

This program enumerates every isolate-free unlabelled simple graph having at
most five edges.  It first enumerates connected isomorphism types (a connected
m-edge graph has at most m+1 vertices), then takes every multiset of connected
components.  It checks all two-colourings of every resulting graph.

No graph library or SAT solver is used.  The separate verify_catalogue.py uses
a deliberately different F detector (injective embeddings) and separately
reconstructs the catalogue.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "probe_result.json"
MAX_EDGES = 5


def connected(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = {0}
    todo = [0]
    while todo:
        v = todo.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                todo.append(w)
    return len(seen) == n


def relabel_edges(
    edges: tuple[tuple[int, int], ...], perm: tuple[int, ...]
) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((min(perm[a], perm[b]), max(perm[a], perm[b])) for a, b in edges))


def canonical_connected(
    n: int, edges: tuple[tuple[int, int], ...]
) -> tuple[tuple[int, int], ...]:
    """Lexicographically least edge tuple over all vertex relabellings."""
    return min(relabel_edges(edges, p) for p in itertools.permutations(range(n)))


def connected_types() -> dict[int, list[dict]]:
    by_m: dict[int, list[dict]] = defaultdict(list)
    for m in range(1, MAX_EDGES + 1):
        seen: set[tuple[tuple[int, int], ...]] = set()
        for n in range(2, m + 2):
            universe = tuple(itertools.combinations(range(n), 2))
            for edges in itertools.combinations(universe, m):
                if not connected(n, edges):
                    continue
                canon = canonical_connected(n, edges)
                if canon in seen:
                    continue
                seen.add(canon)
                by_m[m].append({"n": n, "m": m, "edges": canon})
        by_m[m].sort(key=lambda x: (x["n"], x["edges"]))
    return by_m


def component_signature(component: dict) -> str:
    edge_part = ",".join(f"{a}-{b}" for a, b in component["edges"])
    return f"n{component['n']}m{component['m']}:{edge_part}"


def graph_from_components(components: tuple[dict, ...]) -> tuple[int, tuple[tuple[int, int], ...]]:
    offset = 0
    edges: list[tuple[int, int]] = []
    for c in components:
        edges.extend((a + offset, b + offset) for a, b in c["edges"])
        offset += c["n"]
    return offset, tuple(edges)


def component_multisets(types: list[dict], total_edges: int):
    """Yield each nondecreasing multiset of connected types of given size."""
    types = sorted(types, key=lambda c: (c["m"], component_signature(c)))

    def rec(start: int, remaining: int, acc: list[dict]):
        if remaining == 0:
            yield tuple(acc)
            return
        for i in range(start, len(types)):
            c = types[i]
            if c["m"] > remaining:
                break
            acc.append(c)
            yield from rec(i, remaining - c["m"], acc)
            acc.pop()

    yield from rec(0, total_edges, [])


def has_F_fast(edges: tuple[tuple[int, int], ...], chosen_mask: int) -> bool:
    """Detect P3 disjoint-union K2 using edge intersections."""
    chosen = [edges[i] for i in range(len(edges)) if chosen_mask & (1 << i)]
    for i, e1 in enumerate(chosen):
        s1 = set(e1)
        for j in range(i + 1, len(chosen)):
            e2 = chosen[j]
            s2 = set(e2)
            if len(s1 & s2) != 1:
                continue
            path_vertices = s1 | s2
            for k, e3 in enumerate(chosen):
                if k == i or k == j:
                    continue
                if path_vertices.isdisjoint(e3):
                    return True
    return False


def avoiding_coloring(edges: tuple[tuple[int, int], ...]) -> int | None:
    all_mask = (1 << len(edges)) - 1
    for red in range(all_mask + 1):
        blue = all_mask ^ red
        if not has_F_fast(edges, red) and not has_F_fast(edges, blue):
            return red
    return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    conn = connected_types()
    flat = [c for m in sorted(conn) for c in conn[m]]
    catalogue: list[dict] = []
    arrows: list[dict] = []

    for m in range(1, MAX_EDGES + 1):
        for components in component_multisets(flat, m):
            n, edges = graph_from_components(components)
            red = avoiding_coloring(edges)
            row = {
                "n": n,
                "m": m,
                "edges": [list(e) for e in edges],
                "component_signatures": [component_signature(c) for c in components],
                "avoiding_red_mask": red,
            }
            catalogue.append(row)
            if red is None:
                arrows.append(row)

    result = {
        "claim_scope": "bounded counterexample probe only",
        "erdos_problem": 561,
        "target": "F1=F2=K_{1,2} disjoint-union K_{1,1}",
        "parameters": {"n": [2, 1], "m": [2, 1]},
        "conjectured_value": 6,
        "counterexample_search_edge_ceiling": MAX_EDGES,
        "method": "all isolate-free unlabelled graphs via connected types and component multisets; all 2-colorings",
        "connected_type_counts_by_edges": {str(m): len(conn[m]) for m in sorted(conn)},
        "host_type_counts_by_edges": {
            str(m): sum(1 for row in catalogue if row["m"] == m)
            for m in range(1, MAX_EDGES + 1)
        },
        "host_types_checked": len(catalogue),
        "arrowing_hosts_at_most_five_edges": arrows,
        "outcome": "COUNTEREXAMPLE_FOUND" if arrows else "NO_COUNTEREXAMPLE_IN_THIS_TUPLE",
        "interpretation": (
            "A listed arrowing host would refute the full conjecture."
            if arrows
            else "This null result does not solve Erdős #561; it only clears the first small nonuniform tuple below its conjectured bound."
        ),
        "catalogue": catalogue,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result["artifact_sha256_before_hash_field"] = sha256(OUT)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "connected_type_counts_by_edges",
        "host_type_counts_by_edges",
        "host_types_checked",
        "outcome",
    )}, indent=2))


if __name__ == "__main__":
    main()
