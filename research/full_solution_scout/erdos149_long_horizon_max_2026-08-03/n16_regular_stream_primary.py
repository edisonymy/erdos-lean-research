#!/usr/bin/env python3
"""Stream all connected 4-regular n=16 graphs from geng and find 12 pairs."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from collections import Counter
from pathlib import Path

import networkx as nx


N, M, TARGET = 16, 32, 12
EXPECTED_RECORDS = 8_037_418
EXPECTED_GENG_SHA256 = "64fa2d95bdaff155ce0fc748d4cba83a50e5ffb03e3acc5f41d86581c0bba7ef"


def decode(raw: bytes):
    data = raw.strip()
    if not data or data[0] != N + 63:
        raise ValueError("invalid unheaded order-16 graph6 record")
    edges = []
    adjacency = [0] * N
    payload_index = 1
    remaining = 0
    value = 0
    for upper in range(1, N):
        for lower in range(upper):
            if remaining == 0:
                value = data[payload_index] - 63
                payload_index += 1
                remaining = 6
            remaining -= 1
            if (value >> remaining) & 1:
                edges.append((lower, upper))
                adjacency[lower] |= 1 << upper
                adjacency[upper] |= 1 << lower
    if len(edges) != M or any(block.bit_count() != 4 for block in adjacency):
        raise ValueError("record is not 4-regular with 32 edges")
    reached = 1
    frontier = 1
    while frontier:
        low = frontier & -frontier
        vertex = low.bit_length() - 1
        frontier ^= low
        new = adjacency[vertex] & ~reached
        reached |= new
        frontier |= new
    if reached.bit_count() != N:
        raise ValueError("record is disconnected")
    return edges, adjacency


def compatibility(edges, adjacency):
    comp = [0] * M
    endpoint_masks = [(1 << left) | (1 << right) for left, right in edges]
    for index, (left, right) in enumerate(edges):
        forbidden = adjacency[left] | adjacency[right] | endpoint_masks[index]
        for other in range(index + 1, M):
            if not forbidden & endpoint_masks[other]:
                comp[index] |= 1 << other
                comp[other] |= 1 << index
    return comp


def first_fit(comp, reverse=False):
    unused = (1 << M) - 1
    chosen = []
    while unused and len(chosen) < TARGET:
        index = unused.bit_length() - 1 if reverse else (unused & -unused).bit_length() - 1
        neighbours = comp[index] & unused
        if neighbours:
            other = neighbours.bit_length() - 1 if reverse else (neighbours & -neighbours).bit_length() - 1
            chosen.append((index, other))
            unused &= ~((1 << index) | (1 << other))
        else:
            unused &= ~(1 << index)
    return chosen if len(chosen) == TARGET else None


def blossom(comp):
    graph = nx.Graph()
    graph.add_nodes_from(range(M))
    for index, neighbours in enumerate(comp):
        remaining = neighbours & ~((1 << (index + 1)) - 1)
        while remaining:
            low = remaining & -remaining
            graph.add_edge(index, low.bit_length() - 1)
            remaining ^= low
    matching = nx.max_weight_matching(graph, maxcardinality=True)
    normalized = sorted(tuple(sorted(pair)) for pair in matching)
    return normalized[:TARGET] if len(normalized) >= TARGET else None, len(normalized)


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    geng = root / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"
    geng_hash = hashlib.sha256(geng.read_bytes()).hexdigest()
    if geng_hash != EXPECTED_GENG_SHA256:
        raise RuntimeError(f"unexpected geng hash {geng_hash}")
    command = [str(geng), "-q", "-c", "-d4", "-D4", "16", "32"]
    checkpoint_path = here / "n16_regular_stream_primary_checkpoint.json"
    result_path = here / "n16_regular_stream_primary_result.json"
    candidate_path = here / "n16_regular_pair_obstruction_candidate.json"
    script_path = Path(__file__).resolve()
    started = time.perf_counter()
    stream_hash = hashlib.sha256()
    stream_bytes = 0
    records = 0
    methods = Counter()
    exact_fallback_sizes = Counter()
    thresholds = [
        (25, (EXPECTED_RECORDS + 3) // 4),
        (50, (EXPECTED_RECORDS + 1) // 2),
        (75, (3 * EXPECTED_RECORDS + 3) // 4),
    ]
    threshold_cursor = 0
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdout is not None and process.stderr is not None
    try:
        for raw in process.stdout:
            stream_hash.update(raw)
            stream_bytes += len(raw)
            edges, adjacency = decode(raw)
            comp = compatibility(edges, adjacency)
            chosen = first_fit(comp)
            method = "low_first"
            exact_size = None
            if chosen is None:
                chosen = first_fit(comp, reverse=True)
                method = "high_first"
            if chosen is None:
                chosen, exact_size = blossom(comp)
                method = "blossom"
                exact_fallback_sizes[exact_size] += 1
            if chosen is None:
                candidate = {
                    "schema": "erdos149-n16-regular-pair-obstruction-v1",
                    "status": "PAIR_SAVING_OBSTRUCTION_ONLY",
                    "record_index": records,
                    "graph6": raw.strip().decode("ascii"),
                    "graph6_sha256": hashlib.sha256(raw.strip()).hexdigest(),
                    "edges": edges,
                    "compatibility_matching_number": exact_size,
                    "required_pair_saving": TARGET,
                    "boundary": "A matching below 12 does not by itself prove strong chromatic index above 20; full clique-packing and chromatic verification are required.",
                }
                atomic_json(candidate_path, candidate)
                process.terminate()
                raise RuntimeError(f"pair obstruction frozen at record {records}")
            used = {vertex for pair in chosen for vertex in pair}
            if len(used) != 2 * TARGET or any(not (comp[left] & (1 << right)) for left, right in chosen):
                process.terminate()
                raise RuntimeError(f"invalid matching witness at record {records}")
            methods[method] += 1
            records += 1
            if threshold_cursor < len(thresholds) and records >= thresholds[threshold_cursor][1]:
                percent = thresholds[threshold_cursor][0]
                elapsed = time.perf_counter() - started
                checkpoint = {
                    "schema": "erdos149-n16-regular-stream-checkpoint-v1",
                    "status": "RUNNING",
                    "percent": percent,
                    "records": records,
                    "expected_records": EXPECTED_RECORDS,
                    "methods": dict(sorted(methods.items())),
                    "exact_fallback_sizes": dict(sorted(exact_fallback_sizes.items())),
                    "stream_bytes_so_far": stream_bytes,
                    "elapsed_seconds": elapsed,
                    "records_per_second": records / elapsed,
                }
                atomic_json(checkpoint_path, checkpoint)
                print(json.dumps(checkpoint, sort_keys=True), flush=True)
                threshold_cursor += 1
        stderr = process.stderr.read().decode("utf-8", errors="replace")
        return_code = process.wait()
    finally:
        if process.poll() is None:
            process.terminate()
    elapsed = time.perf_counter() - started
    result = {
        "schema": "erdos149-n16-regular-stream-primary-v1",
        "status": "VERIFIED" if return_code == 0 and records == EXPECTED_RECORDS else "CHECK_FAILED",
        "scope": "All connected 4-regular graphs on 16 vertices streamed directly from pinned geng.",
        "generator": {
            "command": "geng -q -c -d4 -D4 16 32",
            "path": str(geng),
            "sha256": geng_hash,
            "return_code": return_code,
            "stderr": stderr.splitlines(),
        },
        "stream": {
            "records": records,
            "expected_records": EXPECTED_RECORDS,
            "bytes": stream_bytes,
            "sha256": stream_hash.hexdigest(),
            "materialized": False,
        },
        "required_compatibility_matching": TARGET,
        "methods": dict(sorted(methods.items())),
        "exact_fallback_sizes": dict(sorted(exact_fallback_sizes.items())),
        "failures": [],
        "script": {
            "bytes": script_path.stat().st_size,
            "sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
        },
        "elapsed_seconds": elapsed,
        "records_per_second": records / elapsed,
        "claim_boundary": "Twelve compatibility pairs give a strong 20-edge-colouring in this regular slice; this file is only the primary streaming pass until independently replayed.",
    }
    atomic_json(result_path, result)
    atomic_json(
        checkpoint_path,
        {
            "schema": "erdos149-n16-regular-stream-checkpoint-v1",
            "status": result["status"],
            "percent": 100,
            "records": records,
            "expected_records": EXPECTED_RECORDS,
            "methods": result["methods"],
            "exact_fallback_sizes": result["exact_fallback_sizes"],
            "stream_bytes": stream_bytes,
            "stream_sha256": result["stream"]["sha256"],
            "elapsed_seconds": elapsed,
        },
    )
    print(json.dumps({"status": result["status"], "records": records, "methods": result["methods"], "stream_sha256": result["stream"]["sha256"], "elapsed_seconds": elapsed}, sort_keys=True), flush=True)
    if result["status"] != "VERIFIED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
