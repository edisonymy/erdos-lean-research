#!/usr/bin/env python3
"""Exhaustively test the 11-vertex connected 4-regular catalogue for #149.

For a graph G, let J have vertex set E(G), with two vertices adjacent exactly
when the corresponding edges are strongly independent in G.  A strong edge
colouring of G is a partition of V(J) into cliques.

Every graph in the input has 22 edges.  Such a graph is strongly 20-edge-
colourable exactly when J contains either a triangle (one colour class of
size three, saving two colours) or a matching of size two (two size-two
classes, also saving two colours).  Otherwise it needs at least 21 colours.

The catalogue format is the upper triangle of the adjacency matrix, in row
order, preceded by the vertex count.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def parse_catalogue_line(line: str) -> tuple[int, list[tuple[int, int]]]:
    fields = line.split()
    if len(fields) != 2:
        raise ValueError(f"bad catalogue line: {line!r}")
    n = int(fields[0])
    bits = fields[1].strip()
    if len(bits) != n * (n - 1) // 2 or set(bits) - {"0", "1"}:
        raise ValueError("bad upper-triangle bit string")
    edges: list[tuple[int, int]] = []
    cursor = 0
    for u in range(n):
        for v in range(u + 1, n):
            if bits[cursor] == "1":
                edges.append((u, v))
            cursor += 1
    return n, edges


def validate_regular(n: int, edges: list[tuple[int, int]]) -> list[set[int]]:
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        if u == v or v in adjacency[u]:
            raise ValueError("input is not a simple graph")
        adjacency[u].add(v)
        adjacency[v].add(u)
    if len(edges) != 22 or any(len(neighbours) != 4 for neighbours in adjacency):
        raise ValueError("input graph is not 4-regular of order 11")
    return adjacency


def strongly_independent(
    first: tuple[int, int],
    second: tuple[int, int],
    adjacency: list[set[int]],
) -> bool:
    a, b = first
    c, d = second
    if len({a, b, c, d}) != 4:
        return False
    return all(y not in adjacency[x] for x in (a, b) for y in (c, d))


def independent_pair_graph(
    edges: list[tuple[int, int]], adjacency: list[set[int]]
) -> list[set[int]]:
    pair_graph = [set() for _ in edges]
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            if strongly_independent(edges[i], edges[j], adjacency):
                pair_graph[i].add(j)
                pair_graph[j].add(i)
    return pair_graph


def find_triangle(pair_graph: list[set[int]]) -> tuple[int, int, int] | None:
    for a in range(len(pair_graph)):
        for b in pair_graph[a]:
            if b <= a:
                continue
            common = pair_graph[a] & pair_graph[b]
            candidates = [c for c in common if c > b]
            if candidates:
                return a, b, min(candidates)
    return None


def find_two_disjoint_pair_edges(
    pair_graph: list[set[int]],
) -> tuple[tuple[int, int], tuple[int, int]] | None:
    pair_edges = [
        (a, b)
        for a in range(len(pair_graph))
        for b in pair_graph[a]
        if a < b
    ]
    for i, first in enumerate(pair_edges):
        for second in pair_edges[i + 1 :]:
            if len(set(first + second)) == 4:
                return first, second
    return None


def colouring_witness(
    edge_count: int,
    triangle: tuple[int, int, int] | None,
    matching: tuple[tuple[int, int], tuple[int, int]] | None,
) -> list[int]:
    blocks: list[list[int]] = []
    used: set[int] = set()
    if triangle is not None:
        blocks.append(list(triangle))
        used.update(triangle)
    elif matching is not None:
        blocks.extend([list(matching[0]), list(matching[1])])
        used.update(matching[0])
        used.update(matching[1])
    else:
        raise ValueError("no 20-colouring certificate")
    blocks.extend([[edge] for edge in range(edge_count) if edge not in used])
    if len(blocks) > 20:
        raise AssertionError("certificate uses too many colours")
    colours = [-1] * edge_count
    for colour, block in enumerate(blocks):
        for edge in block:
            colours[edge] = colour
    if min(colours) < 0:
        raise AssertionError("incomplete colouring")
    return colours


def check_colouring(
    colours: list[int], pair_graph: list[set[int]]
) -> None:
    for a in range(len(colours)):
        for b in range(a + 1, len(colours)):
            if colours[a] == colours[b] and b not in pair_graph[a]:
                raise AssertionError("same-colour edges are not strongly independent")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    raw = args.catalogue.read_bytes()
    lines = args.catalogue.read_text(encoding="ascii").splitlines()
    records = []
    pair_edge_distribution: Counter[int] = Counter()
    triangle_count = 0
    matching_count = 0
    candidates = []

    for index, line in enumerate(lines):
        n, edges = parse_catalogue_line(line)
        adjacency = validate_regular(n, edges)
        pair_graph = independent_pair_graph(edges, adjacency)
        triangle = find_triangle(pair_graph)
        matching = find_two_disjoint_pair_edges(pair_graph)
        pair_edge_count = sum(map(len, pair_graph)) // 2
        pair_edge_distribution[pair_edge_count] += 1
        triangle_count += triangle is not None
        matching_count += matching is not None
        record = {
            "catalogue_index": index,
            "strongly_independent_pair_count": pair_edge_count,
            "triangle": list(triangle) if triangle is not None else None,
            "matching_size_two": (
                [list(matching[0]), list(matching[1])]
                if matching is not None
                else None
            ),
        }
        if triangle is None and matching is None:
            record["edges"] = [list(edge) for edge in edges]
            candidates.append(record)
        else:
            colours = colouring_witness(len(edges), triangle, matching)
            check_colouring(colours, pair_graph)
            record["colour_count"] = max(colours) + 1
        records.append(record)

    result = {
        "schema": "erdos149-n11-4regular-catalogue-check-v1",
        "claim_scope": (
            "all 265 connected 4-regular graphs of order 11 in the cited "
            "geng catalogue; the only possible disconnected order split is "
            "5+6, and each component then has at most 12 edges, so colouring "
            "each component edge distinctly and reusing colours between "
            "components gives a strong colouring with at most 12 colours"
        ),
        "catalogue": {
            "path": str(args.catalogue),
            "url": "https://webhome.cs.uvic.ca/~wendym/manjeet/11_4reg.txt",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "line_count": len(lines),
        },
        "graphs_checked": len(records),
        "graphs_with_triangle_certificate": triangle_count,
        "graphs_with_matching_size_two_certificate": matching_count,
        "strongly_independent_pair_count_distribution": dict(
            sorted(pair_edge_distribution.items())
        ),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "records": records,
        "status": "CANDIDATE_FOUND" if candidates else "NO_CANDIDATE_IN_SCOPE",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "graphs_checked",
        "graphs_with_triangle_certificate",
        "graphs_with_matching_size_two_certificate",
        "candidate_count",
        "status",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
