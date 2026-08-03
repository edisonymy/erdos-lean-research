#!/usr/bin/env python3
"""Fresh audit of the n=13, m=25 catalogue and five-pair witnesses."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

import networkx as nx


N = 13


def decode(raw: bytes) -> tuple[list[tuple[int, int]], list[set[int]]]:
    text = raw.rstrip(b"\r\n")
    assert text[0] - 63 == N
    stream = "".join(f"{byte - 63:06b}" for byte in text[1:])
    cursor = 0
    edges: list[tuple[int, int]] = []
    neighbours = [set() for _ in range(N)]
    for right in range(1, N):
        for left in range(right):
            if stream[cursor] == "1":
                edges.append((left, right))
                neighbours[left].add(right)
                neighbours[right].add(left)
            cursor += 1
    return edges, neighbours


def compatible(
    e: tuple[int, int], f: tuple[int, int], neighbours: list[set[int]]
) -> bool:
    return not (set(e) & set(f)) and all(y not in neighbours[x] for x in e for y in f)


def reverse_greedy_five(
    edges: list[tuple[int, int]], neighbours: list[set[int]]
) -> list[tuple[int, int]] | None:
    pairs = [
        (i, j)
        for i in range(len(edges) - 1, -1, -1)
        for j in range(i - 1, -1, -1)
        if compatible(edges[i], edges[j], neighbours)
    ]
    used: set[int] = set()
    chosen: list[tuple[int, int]] = []
    for i, j in pairs:
        if i not in used and j not in used:
            chosen.append((i, j))
            used.update((i, j))
            if len(chosen) == 5:
                return chosen
    return None


def connected(neighbours: list[set[int]]) -> bool:
    seen = {0}
    todo = [0]
    while todo:
        vertex = todo.pop()
        for other in neighbours[vertex] - seen:
            seen.add(other)
            todo.append(other)
    return len(seen) == N


def main() -> None:
    started = time.perf_counter()
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    catalogue = here / "13_m25_min3.g6"
    primary_result = json.loads((here / "n13_almost_regular_result.json").read_text(encoding="utf-8"))
    raw_catalogue = catalogue.read_bytes()
    records = raw_catalogue.splitlines()
    catalogue_hash = hashlib.sha256(raw_catalogue).hexdigest()

    geng = root / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"
    count_run = subprocess.run(
        [str(geng), "-c", "-d3", "-D4", "-u", "13", "25"],
        check=True,
        capture_output=True,
        text=True,
    )
    count_text = count_run.stdout + count_run.stderr
    match = re.search(r"([0-9]+) graphs generated", count_text)
    assert match
    generated_count = int(match.group(1))

    failures: list[dict] = []
    networkx_sample_mismatches = 0
    sample_indices = {round(k * (len(records) - 1) / 256) for k in range(257)}
    for index, raw in enumerate(records):
        edges, neighbours = decode(raw)
        degrees = sorted(map(len, neighbours))
        chosen = reverse_greedy_five(edges, neighbours)
        valid_chosen = chosen is not None and len({x for pair in chosen for x in pair}) == 10
        if valid_chosen:
            valid_chosen = all(compatible(edges[i], edges[j], neighbours) for i, j in chosen)
        if len(edges) != 25 or degrees != [3, 3] + [4] * 11 or not connected(neighbours) or not valid_chosen:
            failures.append(
                {
                    "index": index,
                    "graph6": raw.decode("ascii"),
                    "edges": len(edges),
                    "degrees": degrees,
                    "connected": connected(neighbours),
                    "matching_of_five": chosen,
                }
            )
        if index in sample_indices:
            parsed = nx.from_graph6_bytes(raw)
            nx_edges = {tuple(sorted(edge)) for edge in parsed.edges()}
            if nx_edges != set(edges):
                networkx_sample_mismatches += 1

    assertions = {
        "stored_records_equal_geng_count": len(records) == generated_count,
        "all_records_unique": len(set(records)) == len(records),
        "catalogue_hash_matches_primary": catalogue_hash == primary_result["catalogue"]["sha256"],
        "primary_status_verified": primary_result["status"] == "VERIFIED",
        "primary_failures_empty": not primary_result["failures"],
        "networkx_sample_mismatches_zero": networkx_sample_mismatches == 0,
        "fresh_full_failures_empty": not failures,
    }
    output = {
        "schema": "erdos149-n13-almost-regular-fresh-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "catalogue": {
            "records": len(records),
            "bytes": len(raw_catalogue),
            "sha256": catalogue_hash,
            "unique_records": len(set(records)),
        },
        "geng": {
            "path": str(geng),
            "sha256": hashlib.sha256(geng.read_bytes()).hexdigest(),
            "command": "geng -c -d3 -D4 -u 13 25",
            "reported_records": generated_count,
        },
        "fresh_checker": {
            "records_checked": len(records),
            "reverse_order_greedy_matchings_of_five": len(records) - len(failures),
            "networkx_parser_samples": len(sample_indices),
            "networkx_parser_mismatches": networkx_sample_mismatches,
            "failures": failures,
        },
        "assertions": assertions,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "This audit covers only the connected order-13, m=25, degree-3/4 catalogue slice.",
    }
    out = here / "n13_almost_regular_fresh_audit.json"
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "elapsed_seconds": output["elapsed_seconds"], "failures": len(failures)}, sort_keys=True))


if __name__ == "__main__":
    main()
