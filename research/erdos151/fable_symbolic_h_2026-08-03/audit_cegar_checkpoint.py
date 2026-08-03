"""Adversarial regression checks for the hash-chained CEGAR checkpoint."""

from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import sys
import tempfile

from pysat.formula import CNF
from pysat.solvers import Glucose42

from cegar_checkpoint import CutJournal, ExclusiveRunLock
from cegar_face_matching3_tcg3 import solve_face


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_lines(path: pathlib.Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def independent_unsat(path: pathlib.Path) -> bool:
    formula = CNF(from_file=str(path))
    with Glucose42(bootstrap_with=formula.clauses) as solver:
        return not solver.solve()


def expect_value_error(callable_object) -> bool:
    try:
        callable_object()
    except ValueError:
        return True
    return False


def expect_runtime_error(callable_object) -> bool:
    try:
        callable_object()
    except RuntimeError:
        return True
    return False


def main() -> None:
    destination = pathlib.Path(sys.argv[1])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="cegar-checkpoint-audit-", dir=destination.parent
    ) as temporary_name:
        temporary = pathlib.Path(temporary_name)

        split_output = temporary / "split.json"
        split_journal = temporary / "split.cuts.jsonl"
        first = solve_face(10, 4, 2, split_output, checkpoint_path=split_journal)
        if first["result"] != "ROUND-CAP-UNKNOWN":
            raise AssertionError(first)
        split_prefix = json_lines(split_journal)
        resumed = solve_face(10, 4, 10, split_output, checkpoint_path=split_journal)

        fresh_output = temporary / "fresh.json"
        fresh_journal = temporary / "fresh.cuts.jsonl"
        fresh = solve_face(10, 4, 10, fresh_output, checkpoint_path=fresh_journal)
        fresh_records = json_lines(fresh_journal)
        prefix_formula_hashes_equal = [
            split_prefix[index]["formula_sha256_after_round"]
            == fresh_records[index]["formula_sha256_after_round"]
            for index in range(1, len(split_prefix))
        ]

        split_payload = json.loads(split_output.read_text(encoding="utf-8"))
        fresh_payload = json.loads(fresh_output.read_text(encoding="utf-8"))
        split_cnf = pathlib.Path(split_payload["summary"]["final_cnf"])
        fresh_cnf = pathlib.Path(fresh_payload["summary"]["final_cnf"])

        config = {"control": 1}
        simple = temporary / "simple.jsonl"
        journal = CutJournal(simple, config, "a" * 64)
        journal.append_round({"round": 0, "payload": [1, 2, 3]})

        partial = temporary / "partial.jsonl"
        shutil.copyfile(simple, partial)
        with partial.open("ab") as stream:
            stream.write(b'{"type":"round"')
        recovered = CutJournal(partial, config, "a" * 64)
        quarantined = list(temporary.glob("partial.jsonl.truncated-tail-*.bin"))
        recovered.append_round({"round": 1, "payload": [4, 5, 6]})
        recovered_again = CutJournal(partial, config, "a" * 64)

        corrupt = temporary / "corrupt.jsonl"
        lines = simple.read_bytes().splitlines(keepends=True)
        damaged = bytearray(lines[1])
        position = damaged.find(b'"payload"')
        damaged[position] = ord("P")
        corrupt.write_bytes(lines[0] + bytes(damaged))
        middle_corruption_rejected = expect_value_error(
            lambda: CutJournal(corrupt, config, "a" * 64)
        )
        config_mismatch_rejected = expect_value_error(
            lambda: CutJournal(simple, {"control": 2}, "a" * 64)
        )
        lock_path = temporary / "writer.lock"
        with ExclusiveRunLock(lock_path):
            concurrent_writer_rejected = expect_runtime_error(
                lambda: ExclusiveRunLock(lock_path).__enter__()
            )
        with ExclusiveRunLock(lock_path):
            lock_released_after_exit = True

        checks = {
            "split_prefix_formula_hashes_equal_fresh": all(prefix_formula_hashes_equal),
            "split_resume_result_unsat": resumed["result"] == "UNSAT",
            "fresh_result_unsat": fresh["result"] == "UNSAT",
            "split_cnf_independently_unsat_glucose42": independent_unsat(split_cnf),
            "fresh_cnf_independently_unsat_glucose42": independent_unsat(fresh_cnf),
            "partial_tail_detected": recovered.ignored_truncated_tail,
            "partial_tail_quarantined": len(quarantined) == 1,
            "journal_append_after_tail_repair": len(recovered_again.records) == 2,
            "middle_corruption_rejected": middle_corruption_rejected,
            "configuration_mismatch_rejected": config_mismatch_rejected,
            "concurrent_writer_rejected": concurrent_writer_rejected,
            "lock_released_after_exit": lock_released_after_exit,
            "resume_formula_may_diverge_after_checkpoint": (
                resumed["final_formula_sha256"] != fresh["final_formula_sha256"]
            ),
        }
        result = {
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "interpretation": (
                "The persisted input formula is reconstructed exactly through the "
                "checkpoint. Future solver models may diverge because private "
                "CaDiCaL learned state is intentionally not serialized."
            ),
            "split_terminal": resumed,
            "fresh_terminal": fresh,
            "source_sha256": {
                "audit_cegar_checkpoint.py": sha256(pathlib.Path(__file__)),
                "cegar_checkpoint.py": sha256(pathlib.Path(__file__).with_name("cegar_checkpoint.py")),
                "cegar_face_matching3_tcg3.py": sha256(
                    pathlib.Path(__file__).with_name("cegar_face_matching3_tcg3.py")
                ),
            },
        }
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
