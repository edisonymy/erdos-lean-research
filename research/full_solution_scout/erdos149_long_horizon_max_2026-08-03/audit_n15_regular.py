#!/usr/bin/env python3
"""Fresh reverse-order audit of the connected n=15 4-regular catalogue."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

import networkx as nx


N, M, TARGET = 15, 30, 10


def decode(record: bytes):
    data = record.rstrip(b"\r\n")
    assert data[0] - 63 == N
    stream = "".join(f"{byte - 63:06b}" for byte in data[1:])
    cursor = 0
    edges = []
    neighbours = [set() for _ in range(N)]
    for upper in range(1, N):
        for lower in range(upper):
            if stream[cursor] == "1":
                edges.append((lower, upper))
                neighbours[lower].add(upper)
                neighbours[upper].add(lower)
            cursor += 1
    return edges, neighbours


def compatible(e, f, neighbours):
    return not (set(e) & set(f)) and all(y not in neighbours[x] for x in e for y in f)


def reverse_on_demand(edges, neighbours):
    available = list(range(M - 1, -1, -1))
    chosen = []
    while available and len(chosen) < TARGET:
        i = available.pop(0)
        position = next(
            (pos for pos, j in enumerate(available) if compatible(edges[i], edges[j], neighbours)),
            None,
        )
        if position is not None:
            chosen.append((i, available.pop(position)))
    return chosen if len(chosen) == TARGET else None


def main() -> None:
    started = time.perf_counter()
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    catalogue = here / "15_m30_4regular.g6"
    primary = json.loads((here / "n15_regular_result.json").read_text(encoding="utf-8"))
    raw = catalogue.read_bytes()
    records = raw.splitlines()
    digest = hashlib.sha256(raw).hexdigest()
    geng = root / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"
    count_run = subprocess.run(
        [str(geng), "-c", "-d4", "-D4", "-u", "15", "30"],
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
        chosen = reverse_on_demand(edges, neighbours)
        valid = chosen is not None and len({x for pair in chosen for x in pair}) == 2 * TARGET
        if valid:
            valid = all(compatible(edges[i], edges[j], neighbours) for i, j in chosen)
        if len(edges) != M or [len(block) for block in neighbours] != [4] * N or not valid:
            failures.append({"index": index, "graph6": record.decode("ascii"), "matching": chosen})
        if index in sample_indices:
            nx_edges = {tuple(sorted(edge)) for edge in nx.from_graph6_bytes(record).edges()}
            if nx_edges != set(edges):
                parser_mismatches += 1
    assertions = {
        "stored_count_matches_geng": len(records) == generated_count,
        "catalogue_hash_matches_primary": digest == primary["catalogue"]["sha256"],
        "primary_verified": primary["status"] == "VERIFIED" and not primary["failures"],
        "parser_samples_match": parser_mismatches == 0,
        "fresh_failures_empty": not failures,
    }
    result = {
        "schema": "erdos149-n15-regular-fresh-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "catalogue": {"records": len(records), "bytes": len(raw), "sha256": digest},
        "geng_count": generated_count,
        "geng_binary_sha256": hashlib.sha256(geng.read_bytes()).hexdigest(),
        "fresh_reverse_matchings_of_ten": len(records) - len(failures),
        "networkx_parser_samples": len(sample_indices),
        "networkx_parser_mismatches": parser_mismatches,
        "failures": failures,
        "assertions": assertions,
        "elapsed_seconds": time.perf_counter() - started,
        "claim_boundary": "This audit covers only the connected 4-regular order-15 catalogue.",
    }
    (here / "n15_regular_fresh_audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": result["status"], "records": len(records), "failures": len(failures), "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
