#!/usr/bin/env python3
"""Complete compatibility-matching check of the public n=13 4-regular catalogue."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import networkx as nx


HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / "13_4reg.txt"
OUTPUT = HERE / "n13_4regular_result.json"


def parse(line: str) -> list[tuple[int, int]]:
    n_text, bits = line.split()
    n = int(n_text)
    assert n == 13 and len(bits) == 78 and not (set(bits) - {"0", "1"})
    edges = []
    cursor = 0
    for u in range(n):
        for v in range(u + 1, n):
            if bits[cursor] == "1":
                edges.append((u, v))
            cursor += 1
    assert len(edges) == 26
    return edges


def compatibility(edges: list[tuple[int, int]]) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(13))
    graph.add_edges_from(edges)
    assert set(dict(graph.degree()).values()) == {4}
    jgraph = nx.Graph()
    jgraph.add_nodes_from(range(26))
    for i, e in enumerate(edges):
        for k in range(i + 1, len(edges)):
            f = edges[k]
            if len(set(e) | set(f)) == 4 and not any(graph.has_edge(x, y) for x in e for y in f):
                jgraph.add_edge(i, k)
    return jgraph


def main() -> None:
    raw = CATALOGUE.read_bytes()
    lines = CATALOGUE.read_text(encoding="ascii").splitlines()
    distribution = Counter()
    failures = []
    minimum_examples = []
    minimum = 100
    for index, line in enumerate(lines):
        edges = parse(line)
        jgraph = compatibility(edges)
        matching = nx.max_weight_matching(jgraph, maxcardinality=True)
        size = len(matching)
        distribution[size] += 1
        if size < minimum:
            minimum = size
            minimum_examples = [{"index": index, "edges": edges, "matching": sorted(sorted(x) for x in matching)}]
        elif size == minimum and len(minimum_examples) < 5:
            minimum_examples.append({"index": index, "edges": edges, "matching": sorted(sorted(x) for x in matching)})
        if size < 6:
            failures.append({"index": index, "matching_size": size, "edges": edges})
    result = {
        "schema": "erdos149-n13-4regular-catalogue-v1",
        "catalogue": {
            "url": "https://webhome.cs.uvic.ca/~wendym/manjeet/13_4reg.txt",
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "records": len(lines),
        },
        "backend": {"networkx": nx.__version__, "algorithm": "max_weight_matching"},
        "matching_size_distribution": dict(sorted(distribution.items())),
        "minimum_matching_size": minimum,
        "minimum_examples": minimum_examples,
        "graphs_below_six": len(failures),
        "failures": failures,
        "status": "VERIFIED" if len(lines) == 10778 and not failures else "CHECK_FAILED",
        "scope": (
            "All connected 4-regular graphs in the public order-13 catalogue. "
            "Six disjoint compatibility pairs save six colours from 26, giving a strong 20-edge-colouring."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "records": len(lines),
        "distribution": result["matching_size_distribution"],
        "minimum": minimum,
        "below_six": len(failures),
        "status": result["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
