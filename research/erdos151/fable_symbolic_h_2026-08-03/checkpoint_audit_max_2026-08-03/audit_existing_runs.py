#!/usr/bin/env python3
"""Read-only forensic audit of the three stopped n=50 CEGAR lanes."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKET = HERE.parent
WORKSPACE = HERE.parents[3]
PINNED_COMMIT = "26c37d7041e9c422e0f8606af2c105b617708968"


LANES = [
    {
        "name": "inherited-degree9",
        "script": "cegar_face.py",
        "stdout": "cegar_face_n50_d9.stdout.log",
        "stderr": "cegar_face_n50_d9.stderr.log",
        "result": "cegar_face_n50_d9.json",
        "pattern": r"round (\d+).*cuts\+=(\d+)",
    },
    {
        "name": "matching3",
        "script": "cegar_face_matching3.py",
        "stdout": "cegar_face_matching3_n50_d9.stdout.log",
        "stderr": "cegar_face_matching3_n50_d9.stderr.log",
        "result": "cegar_face_matching3_n50_d9.json",
        "pattern": r"round (\d+).*cuts\+=(\d+)",
    },
    {
        "name": "matching3-tcg3",
        "script": "cegar_face_matching3_tcg3.py",
        "stdout": "cegar_face_matching3_tcg3_n50_d9.stdout.log",
        "stderr": "cegar_face_matching3_tcg3_n50_d9.stderr.log",
        "result": "cegar_face_matching3_tcg3_n50_d9.json",
        "pattern": r"round (\d+).*tcg3=([^ ]+) adm=(\d+)",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def assignments_and_loads(source: str, name: str) -> tuple[list[int], list[int]]:
    tree = ast.parse(source)
    stores, loads = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            (stores if isinstance(node.ctx, ast.Store) else loads).append(node.lineno)
    return sorted(stores), sorted(loads)


def pinned_blob(path: Path) -> bytes:
    relative = path.relative_to(WORKSPACE).as_posix()
    process = subprocess.run(
        ["git", "show", f"{PINNED_COMMIT}:{relative}"],
        cwd=WORKSPACE,
        capture_output=True,
        check=True,
    )
    return process.stdout


def main() -> None:
    records = []
    for lane in LANES:
        script = PACKET / lane["script"]
        stdout = PACKET / lane["stdout"]
        stderr = PACKET / lane["stderr"]
        result = PACKET / lane["result"]
        lines = stdout.read_text(encoding="utf-8-sig").splitlines()
        matches = [re.search(lane["pattern"], line) for line in lines]
        matches = [match for match in matches if match]
        assert matches
        # The worktree is shared and may contain a successor under active
        # development.  Audit the exact stopped blob, pinned by commit and by
        # the production metadata's SHA-256, rather than the drifting file.
        source_bytes = pinned_blob(script)
        source = source_bytes.decode("utf-8-sig")
        stores, loads = assignments_and_loads(source, "partition")
        records.append(
            {
                "name": lane["name"],
                "script": {
                    "path": str(script.relative_to(PACKET.parent.parent.parent)),
                    "pinned_commit": PINNED_COMMIT,
                    "pinned_bytes": len(source_bytes),
                    "pinned_sha256": hashlib.sha256(source_bytes).hexdigest(),
                    "current_worktree_sha256": sha256(script),
                    "current_worktree_differs": (
                        hashlib.sha256(source_bytes).hexdigest() != sha256(script)
                    ),
                },
                "stdout": {
                    "path": stdout.name,
                    "bytes": stdout.stat().st_size,
                    "sha256": sha256(stdout),
                    "sample_lines": len(matches),
                    "last_sample": lines[-1],
                    "last_sampled_round": int(matches[-1].group(1)),
                },
                "stderr_bytes": stderr.stat().st_size,
                "result_exists": result.exists(),
                "durable_cut_payload_in_stdout": False,
                "durable_cut_payload_in_result": result.exists(),
                "partition_ast": {"stores": stores, "loads": loads},
            }
        )

    combined = records[-1]
    assert 395 in combined["partition_ast"]["stores"]
    assert 489 in combined["partition_ast"]["loads"]
    assert all(not row["result_exists"] for row in records)
    assert all(row["stderr_bytes"] == 0 for row in records)
    result = {
        "schema": "erdos151-stopped-cegar-forensic-audit-v1",
        "status": "PASS",
        "lanes": records,
        "findings": [
            {
                "severity": "CRITICAL",
                "id": "NO-RECOVERABLE-CUTS",
                "finding": (
                    "All learned clauses existed only in solver memory.  Stdout "
                    "samples every ten rounds and stores counts but no h-sets or "
                    "partitions; terminal JSON was never written.  No exact or "
                    "partial semantic replay can be reconstructed from artifacts."
                ),
            },
            {
                "severity": "HIGH",
                "id": "COMBINED-SAT-TERMINAL-UNBOUND",
                "finding": (
                    "In the combined implementation, partition is assigned only "
                    "on the partition-found branch (line 395) but is read in the "
                    "candidate condition at line 489.  The desired conjunction "
                    "raw_partition is None and no admissible h-set therefore "
                    "raises UnboundLocalError instead of preserving a candidate."
                ),
            },
            {
                "severity": "HIGH",
                "id": "TERMINAL-WRITES-NONATOMIC",
                "finding": (
                    "All terminal/result writes use direct write_text/json.dump "
                    "to the final path without temporary-file fsync, atomic rename, "
                    "or read-back.  A crash can leave a truncated apparent result."
                ),
            },
            {
                "severity": "HIGH",
                "id": "NO-FINAL-CNF",
                "finding": (
                    "The combined lane records only formula counts.  It cannot "
                    "emit the exact final DIMACS formula, and no proof-producing "
                    "solver/checker path is invoked after in-memory UNSAT."
                ),
            },
            {
                "severity": "MEDIUM",
                "id": "DYNAMIC-VARIABLE-ORDER",
                "finding": (
                    "Triangle-witness variable IDs are allocated lazily in cut "
                    "discovery order.  Exact numeric CNF replay therefore requires "
                    "the full ordered cut stream and pinned encoder environment; "
                    "the logs preserve neither."
                ),
            },
        ],
        "claim_boundary": (
            "This is a code/artifact audit.  It makes no SAT, UNSAT, or proximity "
            "claim for the n=50 mathematical instance."
        ),
    }
    output = HERE / "audit_existing_runs.result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
