#!/usr/bin/env python3
"""Independent, intentionally simple verifier for a pulse_149 JSON artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("result", type=Path)
    args = ap.parse_args()
    raw = args.result.read_bytes()
    data = json.loads(raw)
    edges = [tuple(x) for x in data["edges"]]
    assert len(edges) == 22 and len(set(edges)) == 22
    assert all(0 <= a < b < 11 for a, b in edges)

    degrees = [0] * 11
    edge_set = set(edges)
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1
    assert degrees == [4] * 11

    def compatible(e1: tuple[int, int], e2: tuple[int, int]) -> bool:
        a, b = e1
        c, d = e2
        if len({a, b, c, d}) != 4:
            return False
        return all(
            tuple(sorted(x)) not in edge_set
            for x in ((a, c), (a, d), (b, c), (b, d))
        )

    recomputed = []
    for i in range(22):
        for j in range(i + 1, 22):
            if compatible(edges[i], edges[j]):
                recomputed.append([i, j])
    assert recomputed == sorted(data["compatibility_edges"])

    colours = data.get("explicit_strong_colouring")
    if colours is not None:
        assert len(colours) == 22
        assert len(set(colours)) <= 20
        for i in range(22):
            for j in range(i + 1, 22):
                if colours[i] == colours[j]:
                    assert compatible(edges[i], edges[j])

    print(json.dumps({
        "verified": True,
        "regular_degree": 4,
        "edge_count": 22,
        "compatibility_edge_count": len(recomputed),
        "strong_colours": None if colours is None else len(set(colours)),
        "result_sha256": hashlib.sha256(raw).hexdigest(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
