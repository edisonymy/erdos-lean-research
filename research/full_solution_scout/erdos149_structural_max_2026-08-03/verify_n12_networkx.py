#!/usr/bin/env python3
"""Independent audit of the n=12 catalogue using NetworkX blossom matching.

The discovery script uses its own bit-mask matching recursion.  This verifier
parses the catalogue separately, builds the compatibility graph as a NetworkX
graph, and asks the library's blossom implementation for a maximum matching.
Four vertex-disjoint compatibility edges give four two-edge colour classes and
therefore a strong edge-colouring with 24 - 4 = 20 colours.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import networkx as nx


def parse(line: str) -> tuple[int, list[tuple[int, int]]]:
    n_text, bits = line.split()
    n = int(n_text)
    if n != 12 or len(bits) != 66 or set(bits) - {"0", "1"}:
        raise ValueError("invalid catalogue record")
    edges = []
    cursor = 0
    for u in range(n):
        for v in range(u + 1, n):
            if bits[cursor] == "1":
                edges.append((u, v))
            cursor += 1
    return n, edges


def compatibility(edges: list[tuple[int, int]], n: int) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    if g.number_of_edges() != 24 or any(degree != 4 for _, degree in g.degree()):
        raise AssertionError("record is not a simple 4-regular graph")
    j = nx.Graph()
    j.add_nodes_from(range(24))
    for i, (a, b) in enumerate(edges):
        for k in range(i + 1, len(edges)):
            c, d = edges[k]
            if len({a, b, c, d}) < 4:
                continue
            if not any(g.has_edge(x, y) for x in (a, b) for y in (c, d)):
                j.add_edge(i, k)
    return j


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    raw = args.catalogue.read_bytes()
    distribution: Counter[int] = Counter()
    failures = []
    examples = []
    lines = args.catalogue.read_text(encoding="ascii").splitlines()
    for index, line in enumerate(lines):
        n, edges = parse(line)
        j = compatibility(edges, n)
        matching = nx.algorithms.matching.max_weight_matching(j, maxcardinality=True)
        size = len(matching)
        distribution[size] += 1
        chosen = sorted(sorted(pair) for pair in matching)
        # Directly recheck the four selected compatibility pairs.
        for a, b in chosen[:4]:
            if not j.has_edge(a, b):
                raise AssertionError("blossom returned a non-edge")
        if size < 4:
            failures.append({"catalogue_index": index, "matching_size": size, "edges": edges})
        elif len(examples) < 3:
            examples.append({"catalogue_index": index, "four_blocks": chosen[:4]})

    result = {
        "schema": "erdos149-n12-networkx-independent-audit-v1",
        "catalogue": {
            "path": str(args.catalogue),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "records": len(lines),
            "url": "https://webhome.cs.uvic.ca/~wendym/manjeet/12_4reg.txt",
        },
        "backend": {"package": "networkx", "version": nx.__version__, "algorithm": "max_weight_matching"},
        "matching_size_distribution": dict(sorted(distribution.items())),
        "graphs_with_matching_below_4": len(failures),
        "failures": failures,
        "sample_certificates": examples,
        "status": "VERIFIED" if not failures and len(lines) == 1544 else "CHECK_FAILED",
        "scope": (
            "All 1,544 connected 4-regular graphs in the public n=12 catalogue. "
            "A matching of size four in J is an explicit 20-colour certificate; "
            "this says nothing about non-4-regular order-12 graphs."
        ),
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "records": len(lines),
        "matching_size_distribution": result["matching_size_distribution"],
        "failures": len(failures),
        "status": result["status"],
    }, indent=2))
    return 0 if result["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
