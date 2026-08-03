#!/usr/bin/env python3
"""Adversarial tests for the standalone semantic-journal protocol."""

from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from checkpoint_protocol import (
    JournalError,
    MANIFEST_SCHEMA,
    RECORD_SCHEMA,
    canonical_json,
    canonical_tcg_side_zero,
    commit_record,
    create_manifest,
    scan_journal,
)


H = "1" * 64


def manifest() -> dict:
    return {
        "schema": MANIFEST_SCHEMA,
        "run_id": "adversarial-control",
        "n": 10,
        "h": 4,
        "min_degree": 0,
        "max_degree": 3,
        "seed": 2026,
        "cuts_per_round": 2,
        "required_maximal_edge_matching": 3,
        "static_variables": 123,
        "static_clauses": 456,
        "static_cnf_sha256": "2" * 64,
        "variable_map_sha256": "3" * 64,
        "source_bundle_sha256": "4" * 64,
        "environment_lock_sha256": "5" * 64,
        "soundness_packet_sha256": "6" * 64,
    }


def body(index: int, prev: str) -> dict:
    return {
        "schema": RECORD_SCHEMA,
        "run_id": "adversarial-control",
        "index": index,
        "round": index,
        "prev_sha256": prev,
        "static_cnf_sha256": "2" * 64,
        "model_edge_sha256": ("a" if index == 0 else "b") * 64,
        "cuts": [
            {"kind": "tcg3_partition", "side_zero": [0, 1, 2, 3, 4]},
            {"kind": "admissible_h_set", "vertices": [0, 2, 4, 6]},
        ],
    }


def expect_failure(label: str, function) -> str:
    try:
        function()
    except JournalError as exc:
        return f"{label}: {exc}"
    raise AssertionError(f"{label}: corruption was accepted")


def main() -> None:
    findings = []
    with tempfile.TemporaryDirectory(prefix="erdos151-journal-test-") as raw:
        root = Path(raw)
        m = manifest()
        mh = create_manifest(root, m)
        first = commit_record(root, m, body(0, mh), expected_index=0, prev=mh)
        second = commit_record(root, m, body(1, first), expected_index=1, prev=first)
        clean = scan_journal(root)
        assert clean["records"] == 2
        assert clean["head_sha256"] == second
        assert clean["cut_counts"] == {
            "admissible_h_set": 2,
            "tcg3_partition": 2,
        }

        # A partial temporary object is ignored and explicitly reported.
        partial = root / ".000000002.deadbeef.json.partial.tmp"
        partial.write_bytes(b'{"body":')
        with_temp = scan_journal(root)
        assert partial.name in with_temp["temporary_files_ignored"]

        # A bit flip in a committed record is fatal; it is never skipped.
        record0 = next(root.glob("000000000.*.json"))
        original = record0.read_bytes()
        parsed = json.loads(original)
        parsed["body"]["cuts"][1]["vertices"] = [0, 2, 4, 7]
        record0.write_bytes(canonical_json(parsed) + b"\n")
        findings.append(expect_failure("tampered-middle", lambda: scan_journal(root)))
        record0.write_bytes(original)

        # A second object at one index is a fork even when individually valid.
        fork = copy.deepcopy(body(0, mh))
        fork["model_edge_sha256"] = "c" * 64
        from checkpoint_protocol import record_hash

        fork_hash = record_hash(fork)
        fork_path = root / f"000000000.{fork_hash}.json"
        fork_path.write_bytes(
            canonical_json({"body": fork, "sha256": fork_hash}) + b"\n"
        )
        findings.append(expect_failure("fork", lambda: scan_journal(root)))
        fork_path.unlink()

        # Semantic malformed cuts fail before publication.
        bad_set = body(2, second)
        bad_set["cuts"] = [
            {"kind": "admissible_h_set", "vertices": [0, 1, 2]}
        ]
        findings.append(
            expect_failure(
                "wrong-h-set-size",
                lambda: commit_record(
                    root, m, bad_set, expected_index=2, prev=second
                ),
            )
        )
        bad_partition = body(2, second)
        bad_partition["cuts"] = [
            {"kind": "tcg3_partition", "side_zero": [1, 2, 3]}
        ]
        findings.append(
            expect_failure(
                "noncanonical-partition",
                lambda: commit_record(
                    root, m, bad_partition, expected_index=2, prev=second
                ),
            )
        )
        assert canonical_tcg_side_zero([3, 4], [0, 1, 2], 5) == [0, 1, 2]
        findings.append(
            expect_failure(
                "partition-omits-vertex",
                lambda: canonical_tcg_side_zero([3], [0, 1, 2], 5),
            )
        )

    result = {
        "schema": "erdos151-checkpoint-protocol-tests-v1",
        "status": "PASS",
        "tests": {
            "clean_two-record_roundtrip": "PASS",
            "partial_temp_ignored_and_reported": "PASS",
            "committed_bitflip_rejected": "PASS",
            "same-index_fork_rejected": "PASS",
            "wrong_h_set_rejected": "PASS",
            "noncanonical_partition_rejected": "PASS",
            "canonical_complement_selection": "PASS",
            "partition_coverage_rejected": "PASS",
        },
        "expected_failures": findings,
        "scope": (
            "protocol and semantic-record validation only; this does not audit "
            "the static graph CNF or certify an n=50 result"
        ),
    }
    output = Path(__file__).with_name("test_checkpoint_protocol.result.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
