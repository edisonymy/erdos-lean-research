"""Definition-level checker for a proposed Murty--Simon counterexample."""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path


def edge_variables(n: int):
    variable = 0
    for u in range(n):
        for v in range(u + 1, n):
            variable += 1
            yield variable, (u, v)


def normalized_edges(n: int, edges: set[tuple[int, int]]) -> set[tuple[int, int]]:
    answer: set[tuple[int, int]] = set()
    for u, v in edges:
        if not (0 <= u < n and 0 <= v < n) or u == v:
            raise ValueError(f"invalid edge {(u, v)}")
        answer.add((min(u, v), max(u, v)))
    if len(answer) != len(edges):
        raise ValueError("duplicate or oppositely oriented edge")
    return answer


def diameter(n: int, edges: set[tuple[int, int]]) -> int | None:
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    answer = 0
    for source in range(n):
        distances = [-1] * n
        distances[source] = 0
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                if distances[v] == -1:
                    distances[v] = distances[u] + 1
                    queue.append(v)
        if -1 in distances:
            return None
        answer = max(answer, max(distances))
    return answer


def verify_diameter2_critical(n: int, edges: set[tuple[int, int]]) -> dict:
    try:
        edges = normalized_edges(n, edges)
    except ValueError as error:
        return {"valid": False, "error": str(error)}
    original_diameter = diameter(n, edges)
    if original_diameter != 2:
        return {
            "valid": False,
            "error": "original graph does not have diameter exactly 2",
            "diameter": original_diameter,
        }
    for edge in sorted(edges):
        reduced_diameter = diameter(n, edges - {edge})
        if reduced_diameter == 2:
            return {
                "valid": False,
                "error": "edge deletion leaves diameter 2",
                "edge": list(edge),
            }
    return {
        "valid": True,
        "n": n,
        "edge_count": len(edges),
        "bound": n * n // 4,
        "counterexample": len(edges) > n * n // 4,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    data = json.loads(args.candidate.read_text(encoding="utf-8"))
    raw_edges = [tuple(map(int, edge)) for edge in data["edges"]]
    if len(raw_edges) != len(set(raw_edges)):
        result = {"valid": False, "error": "duplicate edge entry"}
    else:
        result = verify_diameter2_critical(int(data["n"]), set(raw_edges))
    print(json.dumps(result, indent=2))
    if not result.get("valid") or not result.get("counterexample"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
