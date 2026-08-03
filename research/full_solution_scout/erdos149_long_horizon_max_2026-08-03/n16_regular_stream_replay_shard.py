#!/usr/bin/env python3
"""Independent reverse/on-demand replay of one regular n=16 geng shard."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections import Counter
from pathlib import Path

import networkx as nx


N, M, TARGET = 16, 32, 12
EXPECTED_GENG_SHA256 = "64fa2d95bdaff155ce0fc748d4cba83a50e5ffb03e3acc5f41d86581c0bba7ef"


def decode_independent(raw: bytes):
    data = raw.rstrip(b"\r\n")
    if not data or data[0] - 63 != N:
        raise ValueError("invalid graph6 order header")
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
    if len(edges) != M or any(len(block) != 4 for block in neighbours):
        raise ValueError("decoded graph is not 4-regular")
    reached = {0}
    frontier = [0]
    while frontier:
        vertex = frontier.pop()
        for other in neighbours[vertex] - reached:
            reached.add(other)
            frontier.append(other)
    if len(reached) != N:
        raise ValueError("decoded graph is disconnected")
    return edges, neighbours


def compatible(edge, other, neighbours):
    if edge[0] in other or edge[1] in other:
        return False
    return all(y not in neighbours[x] for x in edge for y in other)


def reverse_on_demand(edges, neighbours):
    available = list(range(M - 1, -1, -1))
    chosen = []
    while available and len(chosen) < TARGET:
        index = available.pop(0)
        position = next(
            (
                position
                for position, other in enumerate(available)
                if compatible(edges[index], edges[other], neighbours)
            ),
            None,
        )
        if position is not None:
            chosen.append((index, available.pop(position)))
    return chosen if len(chosen) == TARGET else None


def exact_matching(edges, neighbours):
    graph = nx.Graph()
    graph.add_nodes_from(range(M))
    for index in range(M):
        for other in range(index + 1, M):
            if compatible(edges[index], edges[other], neighbours):
                graph.add_edge(index, other)
    matching = nx.max_weight_matching(graph, maxcardinality=True)
    normalized = sorted(tuple(sorted(pair)) for pair in matching)
    return (normalized[:TARGET] if len(normalized) >= TARGET else None), len(normalized)


def write_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("residue", type=int)
    parser.add_argument("modulus", type=int, nargs="?", default=16)
    args = parser.parse_args()
    if not 0 <= args.residue < args.modulus:
        raise ValueError("bad residue")
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    primary_path = here / f"n16_regular_stream_shard_{args.residue:02d}_of_{args.modulus:02d}.json"
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    expected_records = primary["stream"]["records"]
    expected_stream_hash = primary["stream"]["sha256"]
    sample_indices = {
        round(step * (expected_records - 1) / 8)
        for step in range(9)
    }
    geng = root / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"
    geng_hash = hashlib.sha256(geng.read_bytes()).hexdigest()
    if geng_hash != EXPECTED_GENG_SHA256:
        raise RuntimeError(f"unexpected geng hash {geng_hash}")
    shard = f"{args.residue}/{args.modulus}"
    command = [str(geng), "-q", "-c", "-d4", "-D4", "16", "32", shard]
    result_path = here / f"n16_regular_replay_shard_{args.residue:02d}_of_{args.modulus:02d}.json"
    discrepancy_path = here / f"n16_regular_replay_discrepancy_{args.residue:02d}_of_{args.modulus:02d}.json"
    started = time.perf_counter()
    digest = hashlib.sha256()
    stream_bytes = records = parser_mismatches = 0
    methods = Counter()
    exact_fallback_sizes = Counter()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdout is not None and process.stderr is not None
    try:
        for raw in process.stdout:
            digest.update(raw)
            stream_bytes += len(raw)
            edges, neighbours = decode_independent(raw)
            if records in sample_indices:
                parsed = nx.from_graph6_bytes(raw.strip())
                parsed_edges = {tuple(sorted(edge)) for edge in parsed.edges()}
                if parsed_edges != set(edges):
                    parser_mismatches += 1
            chosen = reverse_on_demand(edges, neighbours)
            method = "reverse_on_demand"
            exact_size = None
            if chosen is None:
                chosen, exact_size = exact_matching(edges, neighbours)
                exact_fallback_sizes[exact_size] += 1
                method = "networkx_blossom"
            if chosen is None:
                discrepancy = {
                    "schema": "erdos149-n16-regular-replay-discrepancy-v1",
                    "status": "PAIR_SAVING_OBSTRUCTION_OR_CHECKER_DISAGREEMENT",
                    "shard": shard,
                    "record_index_within_shard": records,
                    "graph6": raw.strip().decode("ascii"),
                    "graph6_sha256": hashlib.sha256(raw.strip()).hexdigest(),
                    "edges": edges,
                    "compatibility_matching_number": exact_size,
                    "required_pair_saving": TARGET,
                }
                write_json(discrepancy_path, discrepancy)
                process.terminate()
                raise RuntimeError(f"replay obstruction in shard {shard} record {records}")
            if len({vertex for pair in chosen for vertex in pair}) != 2 * TARGET:
                process.terminate()
                raise RuntimeError(f"nonmatching replay witness in shard {shard} record {records}")
            if any(not compatible(edges[left], edges[right], neighbours) for left, right in chosen):
                process.terminate()
                raise RuntimeError(f"incompatible replay witness in shard {shard} record {records}")
            methods[method] += 1
            records += 1
        stderr = process.stderr.read().decode("utf-8", errors="replace")
        return_code = process.wait()
    finally:
        if process.poll() is None:
            process.terminate()
    stream_hash = digest.hexdigest()
    assertions = {
        "generator_returned_zero": return_code == 0,
        "record_count_matches_primary": records == expected_records,
        "stream_hash_matches_primary": stream_hash == expected_stream_hash,
        "networkx_parser_samples_match": parser_mismatches == 0,
    }
    elapsed = time.perf_counter() - started
    script_path = Path(__file__).resolve()
    result = {
        "schema": "erdos149-n16-regular-stream-replay-shard-v1",
        "status": "VERIFIED" if all(assertions.values()) else "CHECK_FAILED",
        "shard": {"residue": args.residue, "modulus": args.modulus, "text": shard},
        "generator": {
            "command": f"geng -q -c -d4 -D4 16 32 {shard}",
            "sha256": geng_hash,
            "return_code": return_code,
            "stderr": stderr.splitlines(),
        },
        "stream": {"records": records, "bytes": stream_bytes, "sha256": stream_hash, "materialized": False},
        "primary_expectation": {
            "path": primary_path.name,
            "sha256": hashlib.sha256(primary_path.read_bytes()).hexdigest(),
            "records": expected_records,
            "stream_sha256": expected_stream_hash,
        },
        "required_compatibility_matching": TARGET,
        "methods": dict(sorted(methods.items())),
        "exact_fallback_sizes": dict(sorted(exact_fallback_sizes.items())),
        "networkx_parser_samples": len(sample_indices),
        "networkx_parser_mismatches": parser_mismatches,
        "failures": [],
        "assertions": assertions,
        "script": {"bytes": script_path.stat().st_size, "sha256": hashlib.sha256(script_path.read_bytes()).hexdigest()},
        "elapsed_seconds": elapsed,
        "records_per_second": records / elapsed,
    }
    write_json(result_path, result)
    print(json.dumps({"status": result["status"], "shard": shard, "records": records, "methods": result["methods"], "stream_hash_matches": assertions["stream_hash_matches_primary"], "parser_mismatches": parser_mismatches, "elapsed_seconds": elapsed}, sort_keys=True), flush=True)
    if result["status"] != "VERIFIED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
