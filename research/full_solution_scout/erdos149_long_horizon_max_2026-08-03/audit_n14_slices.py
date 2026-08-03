#!/usr/bin/env python3
"""Independent full replay of an order-14 catalogue slice."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

import networkx as nx


N = 14


def decode(raw: bytes) -> tuple[list[tuple[int, int]], list[set[int]]]:
    data = raw.rstrip(b"\r\n")
    assert data[0] == N + 63
    bit_string = "".join(f"{byte - 63:06b}" for byte in data[1:])
    cursor = 0
    edges: list[tuple[int, int]] = []
    neighbours = [set() for _ in range(N)]
    for upper in range(1, N):
        for lower in range(upper):
            if bit_string[cursor] == "1":
                edges.append((lower, upper))
                neighbours[lower].add(upper)
                neighbours[upper].add(lower)
            cursor += 1
    return edges, neighbours


def compatible(e: tuple[int, int], f: tuple[int, int], neighbours: list[set[int]]) -> bool:
    if e[0] in f or e[1] in f:
        return False
    return all(y not in neighbours[x] for x in e for y in f)


def reverse_on_demand(
    edges: list[tuple[int, int]], neighbours: list[set[int]], target: int
) -> list[tuple[int, int]] | None:
    available = list(range(len(edges) - 1, -1, -1))
    chosen: list[tuple[int, int]] = []
    while available and len(chosen) < target:
        i = available.pop(0)
        partner_position = next(
            (position for position, j in enumerate(available) if compatible(edges[i], edges[j], neighbours)),
            None,
        )
        if partner_position is not None:
            j = available.pop(partner_position)
            chosen.append((i, j))
    return chosen if len(chosen) == target else None


def connected(neighbours: list[set[int]]) -> bool:
    reached = {0}
    frontier = [0]
    while frontier:
        vertex = frontier.pop()
        for other in neighbours[vertex] - reached:
            reached.add(other)
            frontier.append(other)
    return len(reached) == N


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("m", type=int, choices=(27, 28))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    path = args.catalogue.resolve()
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    primary_path = here / f"n14_m{args.m}_result.json"
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    raw = path.read_bytes()
    records = raw.splitlines()
    digest = hashlib.sha256(raw).hexdigest()
    target = args.m - 20
    expected_degrees = [3, 3] + [4] * 12 if args.m == 27 else [4] * 14

    geng = root / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"
    minimum_degree = "3" if args.m == 27 else "4"
    count_run = subprocess.run(
        [str(geng), "-c", f"-d{minimum_degree}", "-D4", "-u", "14", str(args.m)],
        check=True,
        capture_output=True,
        text=True,
    )
    count_match = re.search(r"([0-9]+) graphs generated", count_run.stdout + count_run.stderr)
    assert count_match
    generated_count = int(count_match.group(1))

    sample_indices = {round(k * (len(records) - 1) / 256) for k in range(257)}
    parser_mismatches = 0
    failures = []
    for index, record in enumerate(records):
        edges, neighbours = decode(record)
        chosen = reverse_on_demand(edges, neighbours, target)
        valid = chosen is not None and len({x for pair in chosen for x in pair}) == 2 * target
        if valid:
            valid = all(compatible(edges[i], edges[j], neighbours) for i, j in chosen)
        if (
            len(edges) != args.m
            or sorted(map(len, neighbours)) != expected_degrees
            or not connected(neighbours)
            or not valid
        ):
            failures.append(
                {
                    "index": index,
                    "graph6": record.decode("ascii"),
                    "edge_count": len(edges),
                    "degrees": sorted(map(len, neighbours)),
                    "connected": connected(neighbours),
                    "matching": chosen,
                }
            )
        if index in sample_indices:
            nx_graph = nx.from_graph6_bytes(record)
            nx_edges = {tuple(sorted(edge)) for edge in nx_graph.edges()}
            if nx_edges != set(edges):
                parser_mismatches += 1

    assertions = {
        "stored_count_matches_geng": len(records) == generated_count,
        "catalogue_hash_matches_primary": digest == primary["catalogue"]["sha256"],
        "primary_verified": primary["status"] == "VERIFIED" and not primary["failures"],
        "networkx_parser_samples_match": parser_mismatches == 0,
        "fresh_failures_empty": not failures,
    }
    result = {
        "schema": "erdos149-n14-slice-fresh-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "edge_count": args.m,
        "required_compatibility_matching": target,
        "catalogue": {
            "path": str(path),
            "records": len(records),
            "bytes": len(raw),
            "sha256": digest,
        },
        "geng": {
            "command": f"geng -c -d{minimum_degree} -D4 -u 14 {args.m}",
            "reported_records": generated_count,
            "binary_sha256": hashlib.sha256(geng.read_bytes()).hexdigest(),
        },
        "fresh_reverse_matchings": len(records) - len(failures),
        "networkx_parser_samples": len(sample_indices),
        "networkx_parser_mismatches": parser_mismatches,
        "failures": failures,
        "assertions": assertions,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "This audit covers only the stated order-14 catalogue slice.",
    }
    output = args.out or here / f"n14_m{args.m}_fresh_audit.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "records": len(records), "failures": len(failures), "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
