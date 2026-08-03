#!/usr/bin/env python3
"""Check one canonical geng residue shard for regular order-16 graphs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections import Counter
from pathlib import Path

from n16_regular_stream_primary import (
    EXPECTED_GENG_SHA256,
    TARGET,
    atomic_json,
    blossom,
    compatibility,
    decode,
    first_fit,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("residue", type=int)
    parser.add_argument("modulus", type=int, nargs="?", default=16)
    args = parser.parse_args()
    if not 0 <= args.residue < args.modulus:
        raise ValueError("residue must be in 0..modulus-1")
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    geng = root / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"
    geng_hash = hashlib.sha256(geng.read_bytes()).hexdigest()
    if geng_hash != EXPECTED_GENG_SHA256:
        raise RuntimeError(f"unexpected geng hash {geng_hash}")
    shard = f"{args.residue}/{args.modulus}"
    command = [str(geng), "-q", "-c", "-d4", "-D4", "16", "32", shard]
    result_path = here / f"n16_regular_stream_shard_{args.residue:02d}_of_{args.modulus:02d}.json"
    candidate_path = here / f"n16_regular_pair_obstruction_shard_{args.residue:02d}_of_{args.modulus:02d}.json"
    script_path = Path(__file__).resolve()
    started = time.perf_counter()
    stream_hash = hashlib.sha256()
    stream_bytes = 0
    records = 0
    methods = Counter()
    exact_fallback_sizes = Counter()
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
                    "shard": shard,
                    "record_index_within_shard": records,
                    "graph6": raw.strip().decode("ascii"),
                    "graph6_sha256": hashlib.sha256(raw.strip()).hexdigest(),
                    "edges": edges,
                    "compatibility_matching_number": exact_size,
                    "required_pair_saving": TARGET,
                    "boundary": "A matching below 12 does not by itself prove strong chromatic index above 20; full clique-packing and chromatic verification are required.",
                }
                atomic_json(candidate_path, candidate)
                process.terminate()
                raise RuntimeError(f"pair obstruction frozen in shard {shard} at record {records}")
            used = {vertex for pair in chosen for vertex in pair}
            if len(used) != 2 * TARGET or any(not (comp[left] & (1 << right)) for left, right in chosen):
                process.terminate()
                raise RuntimeError(f"invalid witness in shard {shard} at record {records}")
            methods[method] += 1
            records += 1
        stderr = process.stderr.read().decode("utf-8", errors="replace")
        return_code = process.wait()
    finally:
        if process.poll() is None:
            process.terminate()
    elapsed = time.perf_counter() - started
    result = {
        "schema": "erdos149-n16-regular-stream-shard-v1",
        "status": "CHECKED" if return_code == 0 else "CHECK_FAILED",
        "shard": {"residue": args.residue, "modulus": args.modulus, "text": shard},
        "generator": {
            "command": f"geng -q -c -d4 -D4 16 32 {shard}",
            "sha256": geng_hash,
            "return_code": return_code,
            "stderr": stderr.splitlines(),
        },
        "stream": {
            "records": records,
            "bytes": stream_bytes,
            "sha256": stream_hash.hexdigest(),
            "materialized": False,
        },
        "required_compatibility_matching": TARGET,
        "methods": dict(sorted(methods.items())),
        "exact_fallback_sizes": dict(sorted(exact_fallback_sizes.items())),
        "failures": [],
        "script": {"bytes": script_path.stat().st_size, "sha256": hashlib.sha256(script_path.read_bytes()).hexdigest()},
        "elapsed_seconds": elapsed,
        "records_per_second": records / elapsed,
    }
    atomic_json(result_path, result)
    print(json.dumps({"status": result["status"], "shard": shard, "records": records, "methods": result["methods"], "stream_sha256": result["stream"]["sha256"], "elapsed_seconds": elapsed}, sort_keys=True), flush=True)
    if result["status"] != "CHECKED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
