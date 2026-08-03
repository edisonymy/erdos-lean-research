#!/usr/bin/env python3
"""Independent nauty/custom-code audit of the threshold-six link classification.

This intentionally shares neither NetworkX's atlas/parser nor its graph algorithms
with signed_link_obstructions.py.  It streams connected minimum-degree-two graphs
from nauty geng, parses graph6 directly, and checks all edge signings and spoke
colourings from the definition.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENG = ROOT / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"
OUT = HERE / "root_independent_threshold6_audit.result.json"


def parse_graph6(raw: bytes) -> tuple[int, tuple[tuple[int, int], ...]]:
    data = raw.strip()
    if not data or data[0] == 126:
        raise ValueError("only short graph6 records are expected")
    n = data[0] - 63
    bits: list[int] = []
    for byte in data[1:]:
        value = byte - 63
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    edges: list[tuple[int, int]] = []
    k = 0
    # graph6 orders upper-triangle entries by columns: (0,1),(0,2),(1,2),...
    for v in range(1, n):
        for u in range(v):
            if bits[k]:
                edges.append((u, v))
            k += 1
    return n, tuple(edges)


def adapted_exists(n: int, edges: tuple[tuple[int, int], ...], signing: int) -> bool:
    for spokes in range(1 << n):
        okay = True
        for i, (u, v) in enumerate(edges):
            sigma = (signing >> i) & 1
            if ((spokes >> u) & 1) == sigma == ((spokes >> v) & 1):
                okay = False
                break
        if okay:
            return True
    return False


def first_bad_signing(n: int, edges: tuple[tuple[int, int], ...]) -> int | None:
    for signing in range(1 << len(edges)):
        if not adapted_exists(n, edges, signing):
            return signing
    return None


def bipartite_after_deleting_some_edge(
    n: int, edges: tuple[tuple[int, int], ...]
) -> bool:
    for deleted in range(len(edges)):
        adjacency = [[] for _ in range(n)]
        for i, (u, v) in enumerate(edges):
            if i == deleted:
                continue
            adjacency[u].append(v)
            adjacency[v].append(u)
        colors = [-1] * n
        good = True
        for start in range(n):
            if colors[start] != -1:
                continue
            colors[start] = 0
            stack = [start]
            while stack and good:
                u = stack.pop()
                for v in adjacency[u]:
                    if colors[v] == -1:
                        colors[v] = colors[u] ^ 1
                        stack.append(v)
                    elif colors[v] == colors[u]:
                        good = False
                        break
        if good:
            return True
    return False


def degree_sequence(n: int, edges: tuple[tuple[int, int], ...]) -> list[int]:
    degrees = [0] * n
    for u, v in edges:
        degrees[u] += 1
        degrees[v] += 1
    return sorted(degrees, reverse=True)


def main() -> None:
    if not GENG.exists():
        raise FileNotFoundError(GENG)
    stream_hash = hashlib.sha256()
    records: list[dict] = []
    checked = 0
    for n in range(3, 7):
        command = [str(GENG), "-cq", "-d2", str(n), "1:6"]
        process = subprocess.run(command, check=True, capture_output=True)
        for raw in process.stdout.splitlines():
            stream_hash.update(raw + b"\n")
            order, edges = parse_graph6(raw)
            if len(edges) > 6:
                continue
            checked += 1
            bad = first_bad_signing(order, edges)
            deletion = bipartite_after_deleting_some_edge(order, edges)
            if (bad is None) != deletion:
                raise AssertionError(
                    f"definition/characterization mismatch for {raw.decode()}"
                )
            if bad is not None:
                records.append(
                    {
                        "graph6": raw.decode(),
                        "n": order,
                        "m": len(edges),
                        "degree_sequence": degree_sequence(order, edges),
                        "first_bad_signing": bad,
                    }
                )
    payload = {
        "schema": "erdos151-threshold6-independent-nauty-audit-v1",
        "status": "VERIFIED" if len(records) == 2 else "FAILED",
        "geng_path": str(GENG),
        "geng_sha256": hashlib.sha256(GENG.read_bytes()).hexdigest(),
        "geng_stream_sha256": stream_hash.hexdigest(),
        "connected_min_degree_2_graphs_checked": checked,
        "nonuniversally_adaptable": records,
        "expected_isomorphism_types": [
            {"name": "K4", "n": 4, "m": 6, "degree_sequence": [3, 3, 3, 3]},
            {"name": "bowtie", "n": 5, "m": 6, "degree_sequence": [4, 2, 2, 2, 2]},
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    if payload["status"] != "VERIFIED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
