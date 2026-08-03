#!/usr/bin/env python3
"""Independent hostile checks of the frozen root checkpoint successor.

Writes only inside this audit directory or an automatically removed temporary
directory.  The production modules are imported but never edited.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import struct
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from pysat.formula import CNF
from pysat.solvers import Glucose42


HERE = Path(__file__).resolve().parent
PACKET = HERE.parent
sys.path.insert(0, str(PACKET))

import cegar_checkpoint as checkpoint  # noqa: E402
import cegar_face_matching3_tcg3 as runner  # noqa: E402


EXPECTED = {
    "cegar_checkpoint.py": "0862f5f4ca6719c4a211133379619d3777387f79d9ed6024e87e00bf0d2fdc09",
    "cegar_face_matching3_tcg3.py": "e9f69347eee7d077421188bfcccf20f0173dc3e1767c3b1e643d7f0942be9bf7",
    "audit_cegar_checkpoint.py": "db41581d8026a5939bc8de1e21b4f871471ff90f61facd149ccb27c50097a5d5",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expect_value_error(function) -> str:
    try:
        function()
    except ValueError as exc:
        return str(exc)
    raise AssertionError("semantically bad but rehashed checkpoint was accepted")


def rewrite_single_record(path: Path, mutate) -> None:
    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(lines) == 2
    mutate(lines[1])
    core = {key: value for key, value in lines[1].items() if key != "record_sha256"}
    lines[1]["record_sha256"] = checkpoint.object_hash(core)
    path.write_text(
        "".join(checkpoint.canonical_json(line) + "\n" for line in lines),
        encoding="ascii",
    )


def independently_unsat(path: Path) -> bool:
    formula = CNF(from_file=str(path))
    with Glucose42(bootstrap_with=formula.clauses) as solver:
        return not solver.solve()


def independent_clause_stream_hash(clauses: list[list[int]]) -> str:
    digest = hashlib.sha256()
    for clause in clauses:
        digest.update(struct.pack("<I", len(clause)))
        for literal in clause:
            digest.update(struct.pack("<q", literal))
    return digest.hexdigest()


def main() -> None:
    actual = {name: sha256(PACKET / name) for name in EXPECTED}
    assert actual == EXPECTED
    source = (PACKET / "cegar_checkpoint.py").read_text(encoding="utf-8")
    runner_source = (PACKET / "cegar_face_matching3_tcg3.py").read_text(
        encoding="utf-8"
    )

    with tempfile.TemporaryDirectory(prefix="root-successor-hostile-", dir=HERE) as raw:
        temp = Path(raw)

        # Regression for the exact latent failure in the stopped blob.  The
        # oracles are deliberately stubbed: this tests control flow and durable
        # candidate emission, not the candidate's mathematics.
        candidate_out = temp / "candidate.json"
        candidate_journal = temp / "candidate.cuts.jsonl"
        with patch.object(runner, "find_triangle_free_two_partition", return_value=None), patch.object(
            runner, "find_admissible_sets", return_value=[]
        ), contextlib.redirect_stdout(io.StringIO()):
            candidate = runner.solve_face(
                6,
                4,
                1,
                candidate_out,
                checkpoint_path=candidate_journal,
            )
        assert candidate["result"] == "SAT-CANDIDATE"
        candidate_payload = json.loads(candidate_out.read_text(encoding="utf-8"))
        assert candidate_payload["summary"]["result"] == "SAT-CANDIDATE"
        assert candidate_payload["checkpoint"]["completed_rounds"] == 0

        # Produce a genuine one-round checkpoint, then create two malicious but
        # correctly rehashed variants.  Integrity hashes alone must not make
        # semantically malformed cuts replayable.
        base_out = temp / "one-round.json"
        base_journal = temp / "one-round.cuts.jsonl"
        with contextlib.redirect_stdout(io.StringIO()):
            capped = runner.solve_face(
                10, 4, 1, base_out, checkpoint_path=base_journal
            )
        assert capped["result"] == "ROUND-CAP-UNKNOWN"

        wrong_set = temp / "wrong-set.cuts.jsonl"
        wrong_set.write_bytes(base_journal.read_bytes())

        def make_wrong_set(record: dict) -> None:
            sets = record["admissible_sets"]
            assert isinstance(sets, list) and sets
            sets[0] = sets[0][:-1]

        rewrite_single_record(wrong_set, make_wrong_set)
        wrong_set_error = expect_value_error(
            lambda: runner.solve_face(
                10,
                4,
                2,
                temp / "wrong-set.json",
                checkpoint_path=wrong_set,
            )
        )

        wrong_partition = temp / "wrong-partition.cuts.jsonl"
        wrong_partition.write_bytes(base_journal.read_bytes())

        def make_wrong_partition(record: dict) -> None:
            partition = record["tcg3_partition"]
            assert isinstance(partition, list) and len(partition) == 2
            moved = partition[1].pop()
            assert moved not in partition[0]

        rewrite_single_record(wrong_partition, make_wrong_partition)
        wrong_partition_error = expect_value_error(
            lambda: runner.solve_face(
                10,
                4,
                2,
                temp / "wrong-partition.json",
                checkpoint_path=wrong_partition,
            )
        )

        # Fresh terminal CNF: count equality plus independent solver result.
        terminal_out = temp / "terminal.json"
        terminal_journal = temp / "terminal.cuts.jsonl"
        with contextlib.redirect_stdout(io.StringIO()):
            terminal = runner.solve_face(
                10, 4, 20, terminal_out, checkpoint_path=terminal_journal
            )
        assert terminal["result"] == "UNSAT"
        payload = json.loads(terminal_out.read_text(encoding="utf-8"))
        cnf_path = Path(payload["summary"]["final_cnf"])
        formula = CNF(from_file=str(cnf_path))
        assert len(formula.clauses) == payload["final_formula"]["clauses"]
        assert sha256(cnf_path) == payload["summary"]["final_cnf_sha256"]
        assert independent_clause_stream_hash(formula.clauses) == payload["summary"][
            "final_formula_sha256"
        ]
        independent = independently_unsat(cnf_path)
        assert independent

        result = {
            "schema": "erdos151-root-checkpoint-hostile-audit-v1",
            "status": "CONDITIONAL-PASS",
            "frozen_source_sha256": actual,
            "checks": {
                "frozen_hashes_exact": True,
                "sat_terminal_control_flow_and_atomic_payload": True,
                "rehashed_wrong_h_set_rejected_on_replay": True,
                "rehashed_nonpartition_rejected_on_replay": True,
                "exported_cnf_clause_count_exact": True,
                "exported_cnf_sha256_exact": True,
                "exported_cnf_clause_stream_hash_exact": True,
                "exported_small_control_independently_unsat_glucose42": independent,
                "root_regression_audit_status": json.loads(
                    (PACKET / "audit_cegar_checkpoint.result.json").read_text(
                        encoding="utf-8"
                    )
                )["status"],
            },
            "expected_replay_errors": {
                "wrong_h_set": wrong_set_error,
                "nonpartition": wrong_partition_error,
            },
            "remaining_gaps": {
                "exclusive_single_writer_lock_present": any(
                    token in source
                    for token in ("msvcrt.locking", "O_EXCL", "LockFileEx")
                ),
                "sudden_power_loss_durability_explicitly_not_claimed": True,
                "proof_certificate_generation_absent": (
                    "drat" not in runner_source.lower()
                    and "lrat" not in runner_source.lower()
                ),
            },
            "interpretation": (
                "The exact frozen successor is formula-replay sound for one "
                "writer under ordinary process/AppX interruption, and the OS-held "
                "lock rejects a second writer.  A claim-grade UNSAT still needs "
                "a checked DRAT/LRAT proof from the exported CNF; sudden-power-loss "
                "durability is explicitly outside the implementation's claim."
            ),
            "claim_boundary": (
                "All SAT/UNSAT checks here are n=6/n=10 controls; no n=50 "
                "mathematical outcome is asserted."
            ),
        }

    output = HERE / "audit_root_successor.result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
