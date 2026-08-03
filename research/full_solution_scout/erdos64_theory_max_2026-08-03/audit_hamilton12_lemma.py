#!/usr/bin/env python3
"""Independent finite audit of the Hamiltonian order-12 chord lemma.

Standard library only.  This corroborates, but is not needed by, the explicit
matching proof in POSTPUBLICATION_PLUS7_FINITE_WINDOW.md.
"""

from __future__ import annotations

import itertools
import json


BASE = {tuple(sorted((vertex, (vertex + 1) % 12))) for vertex in range(12)}
PARITY_EDGES = list(itertools.combinations(range(6), 2))


def adjacency(edges: set[tuple[int, int]]) -> list[set[int]]:
    answer = [set() for _ in range(12)]
    for left, right in edges:
        answer[left].add(right)
        answer[right].add(left)
    return answer


def find_cycle(edges: set[tuple[int, int]], length: int) -> tuple[int, ...] | None:
    adj = adjacency(edges)
    for start in range(12):
        def visit(path: tuple[int, ...]) -> tuple[int, ...] | None:
            if len(path) == length:
                return path if start in adj[path[-1]] else None
            for nxt in sorted(adj[path[-1]]):
                if nxt > start and nxt not in path:
                    result = visit((*path, nxt))
                    if result is not None:
                        return result
            return None

        result = visit((start,))
        if result is not None:
            return result
    return None


def covers(vertices: range, edges: tuple[tuple[int, int], ...]) -> bool:
    return all(any(vertex in edge for edge in edges) for vertex in vertices)


def inclusion_minimal_cover(edges: tuple[tuple[int, int], ...]) -> bool:
    return covers(range(6), edges) and all(
        not covers(range(6), edges[:index] + edges[index + 1 :])
        for index in range(len(edges))
    )


def lifted(edges: tuple[tuple[int, int], ...], parity: int) -> set[tuple[int, int]]:
    return {
        tuple(sorted((2 * left + parity, 2 * right + parity))) for left, right in edges
    }


def main() -> int:
    survivors = []
    cover_counts = {size: 0 for size in range(3, 6)}
    for size in range(3, 6):
        for chosen in itertools.combinations(PARITY_EDGES, size):
            if not inclusion_minimal_cover(chosen):
                continue
            cover_counts[size] += 1
            graph = BASE | lifted(chosen, 0)
            if find_cycle(graph, 4) is None and find_cycle(graph, 8) is None:
                survivors.append(chosen)

    pair_witnesses = []
    for even in survivors:
        for odd in survivors:
            graph = BASE | lifted(even, 0) | lifted(odd, 1)
            witness = find_cycle(graph, 4) or find_cycle(graph, 8)
            pair_witnesses.append(
                {
                    "even": even,
                    "odd": odd,
                    "witness": witness,
                }
            )

    expected = {
        ((0, 1), (2, 3), (4, 5)),
        ((0, 1), (2, 5), (3, 4)),
        ((0, 3), (1, 2), (4, 5)),
        ((0, 3), (1, 4), (2, 5)),
        ((0, 5), (1, 2), (3, 4)),
        ((0, 5), (1, 4), (2, 3)),
    }
    verified = set(survivors) == expected and all(row["witness"] for row in pair_witnesses)
    print(
        json.dumps(
            {
                "minimal_edge_cover_counts_by_size": cover_counts,
                "single_parity_survivors": survivors,
                "survivor_pairs": len(pair_witnesses),
                "all_pairs_have_c4_or_c8": all(row["witness"] for row in pair_witnesses),
                "verified": verified,
            },
            indent=2,
        )
    )
    return 0 if verified else 10


if __name__ == "__main__":
    raise SystemExit(main())
