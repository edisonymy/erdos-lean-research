"""Exhaustive falsification tests for two local D2C counting lemmas."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from verify_graph import diameter


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    result = [set() for _ in range(n)]
    for u, v in edges:
        result[u].add(v)
        result[v].add(u)
    return result


def has_local_witness(
    n: int, edges: set[tuple[int, int]], u: int, v: int
) -> bool:
    """Exact proposed characterization of an edge critical for diameter two."""
    neighbours = adjacency(n, edges)
    if not (neighbours[u] & neighbours[v]):
        return True
    for x in neighbours[u] - neighbours[v] - {v}:
        if neighbours[x] & neighbours[v] == {u}:
            return True
    for y in neighbours[v] - neighbours[u] - {u}:
        if neighbours[y] & neighbours[u] == {v}:
            return True
    return False


def count_statistics(n: int, edges: set[tuple[int, int]]) -> tuple[int, int]:
    neighbours = adjacency(n, edges)
    triangle_free_edges = sum(not (neighbours[u] & neighbours[v]) for u, v in edges)
    unique_common_nonedges = sum(
        len(neighbours[u] & neighbours[v]) == 1
        for u, v in itertools.combinations(range(n), 2)
        if (u, v) not in edges
    )
    return triangle_free_edges, unique_common_nonedges


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=6)
    parser.add_argument("--result", type=Path)
    args = parser.parse_args()
    if not 2 <= args.max_n <= 6:
        raise SystemExit("the exhaustive audit supports 2 <= max-n <= 6")

    rows = []
    for n in range(2, args.max_n + 1):
        pairs = list(itertools.combinations(range(n), 2))
        diameter_two_graphs = 0
        edge_instances = 0
        critical_graphs = 0
        maximum_edges = -1
        minimum_count_slack = None
        count_equalities = 0
        for mask in range(1 << len(pairs)):
            edges = {pairs[index] for index in range(len(pairs)) if mask >> index & 1}
            if diameter(n, edges) != 2:
                continue
            diameter_two_graphs += 1
            graph_is_critical = True
            for edge in edges:
                edge_instances += 1
                definition = diameter(n, edges - {edge}) != 2
                local = has_local_witness(n, edges, *edge)
                if definition != local:
                    raise AssertionError((n, sorted(edges), edge, definition, local))
                graph_is_critical &= definition
            if not graph_is_critical:
                continue
            critical_graphs += 1
            maximum_edges = max(maximum_edges, len(edges))
            d_count, s_count = count_statistics(n, edges)
            slack = d_count + 2 * s_count - len(edges)
            if slack < 0:
                raise AssertionError((n, sorted(edges), d_count, s_count, slack))
            minimum_count_slack = (
                slack if minimum_count_slack is None else min(minimum_count_slack, slack)
            )
            count_equalities += int(slack == 0)
        rows.append(
            {
                "n": n,
                "diameter_two_graphs": diameter_two_graphs,
                "edge_instances": edge_instances,
                "diameter_two_critical_graphs": critical_graphs,
                "maximum_edges": maximum_edges,
                "murty_simon_bound": n * n // 4,
                "minimum_D_plus_2S_minus_m": minimum_count_slack,
                "count_inequality_equalities": count_equalities,
            }
        )

    result = {
        "max_n": args.max_n,
        "witness_mismatches": 0,
        "count_inequality_violations": 0,
        "rows": rows,
        "definitions": {
            "D": "edges whose endpoints have no common neighbour",
            "S": "nonedges whose endpoints have exactly one common neighbour",
            "tested_inequality": "|E| <= D + 2*S",
        },
        "claim_scope": "exhaustive falsification test; the lemmas also have direct proofs",
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.result:
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
