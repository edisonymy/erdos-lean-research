#!/usr/bin/env python3
"""Exhaustive <=7-edge counterexample search for an uncovered #561 tuple.

Targets:
  red  F_R = K_{1,2} disjoint-union K_{1,1} = P3 + K2
  blue F_B = 2 K_{1,2} = 2 P3

The conjectured formula gives 8, so any arrowing host with <=7 edges is a
full counterexample to the universal conjecture.  Isolated host vertices are
irrelevant.  Connected types come from the complete NetworkX atlas through
seven vertices, plus all nonisomorphic eight-vertex trees (the only connected
eight-vertex graphs with <=7 edges).  Component multisets give the complete
isolate-free host class.
"""

from __future__ import annotations

import itertools
import hashlib
import json
import platform
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
OUT = HERE / "search_result.json"
WITNESSES = HERE / "host_avoiding_colorings.json"
MAX_EDGES = 7


def normalized_edges(graph: nx.Graph) -> tuple[tuple[int, int], ...]:
    nodes = sorted(graph.nodes())
    relabel = {v: i for i, v in enumerate(nodes)}
    return tuple(
        sorted(
            (min(relabel[a], relabel[b]), max(relabel[a], relabel[b]))
            for a, b in graph.edges()
        )
    )


def component_types() -> list[dict]:
    """One representative of every connected type with 1..7 edges."""
    types: list[dict] = []
    for atlas_index, graph in enumerate(nx.graph_atlas_g()):
        n = graph.number_of_nodes()
        m = graph.number_of_edges()
        if n >= 2 and 1 <= m <= MAX_EDGES and nx.is_connected(graph):
            types.append(
                {
                    "source": f"networkx_graph_atlas:{atlas_index}",
                    "n": n,
                    "m": m,
                    "edges": normalized_edges(graph),
                }
            )
    for tree_index, graph in enumerate(nx.nonisomorphic_trees(8)):
        types.append(
            {
                "source": f"networkx_nonisomorphic_trees_8:{tree_index}",
                "n": 8,
                "m": 7,
                "edges": normalized_edges(graph),
            }
        )
    types.sort(key=lambda c: (c["m"], c["n"], c["source"]))
    for index, component in enumerate(types):
        component["type_id"] = index
    return types


def component_multisets(types: list[dict], total_edges: int):
    """Yield every multiset of component types with the requested edge sum."""

    def rec(start: int, remaining: int, acc: list[dict]):
        if remaining == 0:
            yield tuple(acc)
            return
        for i in range(start, len(types)):
            component = types[i]
            if component["m"] > remaining:
                break
            acc.append(component)
            yield from rec(i, remaining - component["m"], acc)
            acc.pop()

    yield from rec(0, total_edges, [])


def assemble(components: tuple[dict, ...]):
    offset = 0
    edges: list[tuple[int, int]] = []
    for component in components:
        edges.extend((a + offset, b + offset) for a, b in component["edges"])
        offset += component["n"]
    return offset, tuple(edges)


def red_target_masks(edges: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    """All edge masks witnessing P3 disjoint-union K2."""
    masks: set[int] = set()
    for i, j in itertools.combinations(range(len(edges)), 2):
        shared = set(edges[i]) & set(edges[j])
        if len(shared) != 1:
            continue
        path_vertices = set(edges[i]) | set(edges[j])
        for k, edge in enumerate(edges):
            if k != i and k != j and path_vertices.isdisjoint(edge):
                masks.add((1 << i) | (1 << j) | (1 << k))
    return tuple(sorted(masks))


def blue_target_masks(edges: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    """All edge masks witnessing two vertex-disjoint copies of P3."""
    paths: list[tuple[frozenset[int], int]] = []
    for i, j in itertools.combinations(range(len(edges)), 2):
        if len(set(edges[i]) & set(edges[j])) == 1:
            paths.append((frozenset(set(edges[i]) | set(edges[j])), (1 << i) | (1 << j)))
    masks: set[int] = set()
    for (vertices_a, mask_a), (vertices_b, mask_b) in itertools.combinations(paths, 2):
        if vertices_a.isdisjoint(vertices_b):
            masks.add(mask_a | mask_b)
    return tuple(sorted(masks))


def first_avoiding_coloring(edges: tuple[tuple[int, int], ...]):
    red_patterns = red_target_masks(edges)
    blue_patterns = blue_target_masks(edges)
    full = (1 << len(edges)) - 1
    for red in range(full + 1):
        blue = full ^ red
        has_red = any((red & pattern) == pattern for pattern in red_patterns)
        if has_red:
            continue
        has_blue = any((blue & pattern) == pattern for pattern in blue_patterns)
        if not has_blue:
            return red, len(red_patterns), len(blue_patterns)
    return None, len(red_patterns), len(blue_patterns)


def main() -> None:
    started = time.time()
    types = component_types()
    connected_counts = Counter(component["m"] for component in types)
    catalogue_counts: Counter[int] = Counter()
    colorings_checked_upper_bound = 0
    arrowing_hosts: list[dict] = []
    witness_records: list[dict] = []
    avoiding_witness_digest_rows: list[str] = []

    for m in range(1, MAX_EDGES + 1):
        for components in component_multisets(types, m):
            n, edges = assemble(components)
            red, red_pattern_count, blue_pattern_count = first_avoiding_coloring(edges)
            catalogue_counts[m] += 1
            colorings_checked_upper_bound += 1 << m
            signature = ",".join(str(c["type_id"]) for c in components)
            if red is None:
                arrowing_hosts.append(
                    {
                        "n": n,
                        "m": m,
                        "edges": [list(e) for e in edges],
                        "component_type_ids": [c["type_id"] for c in components],
                        "component_sources": [c["source"] for c in components],
                        "red_embedding_pattern_count": red_pattern_count,
                        "blue_embedding_pattern_count": blue_pattern_count,
                    }
                )
            else:
                avoiding_witness_digest_rows.append(f"{m}:{signature}:{red}")
                witness_records.append(
                    {
                        "n": n,
                        "m": m,
                        "edges": [list(e) for e in edges],
                        "component_type_ids": [c["type_id"] for c in components],
                        "component_sources": [c["source"] for c in components],
                        "avoiding_red_mask": red,
                    }
                )

    # A compact checksum of every null witness without bloating the artifact.
    witness_sha256 = hashlib.sha256(
        "\n".join(avoiding_witness_digest_rows).encode("ascii")
    ).hexdigest()
    witness_payload = {
        "schema": "erdos561-nonuniform-avoiding-colorings-v1",
        "red_target": "K_{1,2} disjoint-union K_{1,1}",
        "blue_target": "2 K_{1,2}",
        "records": witness_records,
    }
    WITNESSES.write_text(json.dumps(witness_payload, indent=2) + "\n", encoding="utf-8")
    result = {
        "schema": "erdos561-nonuniform-host-search-v1",
        "erdos_problem": 561,
        "targets": {
            "red": "K_{1,2} disjoint-union K_{1,1}",
            "blue": "2 K_{1,2}",
            "red_degrees": [2, 1],
            "blue_degrees": [2, 2],
        },
        "formula_layers": [3, 3, 2],
        "conjectured_value": 8,
        "counterexample_edge_ceiling": MAX_EDGES,
        "catalogue_basis": (
            "complete NetworkX graph atlas for connected types on <=7 vertices, "
            "plus every nonisomorphic tree on 8 vertices; component multisets"
        ),
        "networkx_version": nx.__version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "connected_type_counts_by_edges": {
            str(m): connected_counts[m] for m in range(1, MAX_EDGES + 1)
        },
        "host_type_counts_by_edges": {
            str(m): catalogue_counts[m] for m in range(1, MAX_EDGES + 1)
        },
        "host_types_checked": sum(catalogue_counts.values()),
        "colorings_per_host_upper_bound_sum": colorings_checked_upper_bound,
        "avoiding_witness_rows_sha256": witness_sha256,
        "avoiding_colorings_file": WITNESSES.name,
        "avoiding_colorings_file_sha256": hashlib.sha256(WITNESSES.read_bytes()).hexdigest(),
        "avoiding_colorings_saved": len(witness_records),
        "arrowing_hosts": arrowing_hosts,
        "outcome": "COUNTEREXAMPLE_FOUND" if arrowing_hosts else "NO_COUNTEREXAMPLE_AT_MOST_7_EDGES",
        "full_problem_resolved": bool(arrowing_hosts),
        "elapsed_seconds": time.time() - started,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
