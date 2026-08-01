#!/usr/bin/env python3
"""Independent exhaustive checker for an Erdos-128 counterexample edge list."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", type=Path)
    args = parser.parse_args()
    data = json.loads(args.graph.read_text(encoding="utf-8"))
    n = int(data["n"])
    edges = {tuple(sorted(map(int, edge))) for edge in data["edges"]}
    assert all(0 <= i < j < n for i, j in edges)
    assert len(edges) == len(data["edges"]), "duplicate edge"

    for triple in itertools.combinations(range(n), 3):
        if all(tuple(sorted(edge)) in edges for edge in itertools.combinations(triple, 2)):
            raise SystemExit(f"FAIL: triangle {triple}")

    k = n // 2
    target = n * n // 50 + 1
    minimum = None
    witnesses = []
    for subset in itertools.combinations(range(n), k):
        count = sum(tuple(sorted(edge)) in edges for edge in itertools.combinations(subset, 2))
        if minimum is None or count < minimum:
            minimum = count
            witnesses = [subset]
        elif count == minimum and len(witnesses) < 10:
            witnesses.append(subset)
    if minimum is None or minimum < target:
        raise SystemExit(f"FAIL: minimum half edges {minimum} < required {target}; {witnesses[:1]}")
    print(json.dumps({"result": "valid counterexample", "n": n, "edge_count": len(edges),
                      "half_size": k, "minimum_half_edges": minimum,
                      "required_half_edges": target, "sample_minimizers": witnesses}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
