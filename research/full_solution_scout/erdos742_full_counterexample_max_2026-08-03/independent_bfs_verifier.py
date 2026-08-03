"""Standalone definition checker for a proposed Erdos-742 graph.

This file deliberately does not import either search implementation.  It uses
adjacency sets and a fresh breadth-first search after each edge deletion.  A
candidate JSON file may be either ``{"n": 25, "edges": [...]}`` or a search
result containing a non-null ``candidate_edges`` field.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from itertools import combinations
from pathlib import Path


def normalized_edges(n: int, raw_edges: object) -> set[tuple[int, int]]:
    if not isinstance(raw_edges, list):
        raise ValueError("edges must be a JSON list")
    result: set[tuple[int, int]] = set()
    for item in raw_edges:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"invalid edge entry: {item!r}")
        u, v = item
        if not isinstance(u, int) or not isinstance(v, int):
            raise ValueError(f"non-integral endpoint: {item!r}")
        if not (0 <= u < n and 0 <= v < n) or u == v:
            raise ValueError(f"endpoint outside a simple graph: {item!r}")
        edge = (u, v) if u < v else (v, u)
        if edge in result:
            raise ValueError(f"duplicate edge: {edge!r}")
        result.add(edge)
    return result


def distances_from(
    n: int, edges: set[tuple[int, int]], source: int
) -> list[int | None]:
    neighbours = [set() for _ in range(n)]
    for u, v in edges:
        neighbours[u].add(v)
        neighbours[v].add(u)
    distances: list[int | None] = [None] * n
    distances[source] = 0
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in neighbours[u]:
            if distances[v] is None:
                distances[v] = distances[u] + 1  # type: ignore[operator]
                queue.append(v)
    return distances


def diameter(n: int, edges: set[tuple[int, int]]) -> int | None:
    answer = 0
    for source in range(n):
        distances = distances_from(n, edges, source)
        if any(value is None for value in distances):
            return None
        answer = max(answer, max(value for value in distances if value is not None))
    return answer


def verify(n: int, edges: set[tuple[int, int]]) -> dict[str, object]:
    original = diameter(n, edges)
    removable = []
    deletion_diameters = {}
    if original == 2:
        for edge in sorted(edges):
            after = diameter(n, edges - {edge})
            if after == 2:
                removable.append(edge)
            elif len(deletion_diameters) < 8:
                deletion_diameters[str(edge)] = after
    threshold = n * n // 4
    return {
        "valid_diameter2_critical": original == 2 and not removable,
        "n": n,
        "edge_count": len(edges),
        "murty_simon_floor": threshold,
        "would_be_counterexample": (
            original == 2 and not removable and len(edges) > threshold
        ),
        "original_diameter": original,
        "removable_edge_count": len(removable),
        "removable_edges": removable,
        "sample_critical_deletion_diameters": deletion_diameters,
    }


def self_test() -> dict[str, object]:
    left = range(12)
    right = range(12, 25)
    complete_bipartite = {(u, v) for u in left for v in right}
    plus_internal = complete_bipartite | {(12, 13)}
    # Preserve the internal edge but split its 12 common neighbours between
    # its endpoints.  This is a 145-edge C5+ / subdivided-bipartite control.
    c5_plus = set(plus_internal)
    c5_plus -= {
        (a, 13) if a < 6 else (a, 12)
        for a in left
    }
    positive = verify(25, complete_bipartite)
    nonbipartite_positive = verify(25, c5_plus)
    negative = verify(25, plus_internal)
    passed = (
        positive["valid_diameter2_critical"] is True
        and positive["edge_count"] == 156
        and nonbipartite_positive["valid_diameter2_critical"] is True
        and nonbipartite_positive["edge_count"] == 145
        and negative["valid_diameter2_critical"] is False
        and negative["edge_count"] == 157
        and negative["removable_edge_count"] == 25
    )
    return {
        "passed": passed,
        "positive_control_K12,13": positive,
        "positive_control_C5_plus": nonbipartite_positive,
        "negative_control_K12,13_plus_edge": negative,
    }


def load_candidate(path: Path) -> tuple[int, set[tuple[int, int]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    n = data.get("n", 25)
    if not isinstance(n, int) or n < 3:
        raise ValueError("n must be an integer at least 3")
    raw_edges = data.get("edges")
    if raw_edges is None:
        raw_edges = data.get("candidate_edges")
    if raw_edges is None:
        raise ValueError("no edges or non-null candidate_edges field")
    return n, normalized_edges(n, raw_edges)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        if not result["passed"]:
            raise SystemExit(1)
        return
    if args.candidate is None:
        parser.error("provide candidate JSON or --self-test")
    n, edges = load_candidate(args.candidate)
    print(json.dumps(verify(n, edges), indent=2))


if __name__ == "__main__":
    main()
