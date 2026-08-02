"""Regression tests for the isolated schema-5 terminal proof exporter."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import proof_export  # noqa: E402

SMOKE_RUN = HERE / "runs" / "F4_N41_v5_arrowfirst_smoke_20260802"


def _canonical(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _write_hashed(path: Path, payload: dict[str, object]) -> None:
    payload = dict(payload)
    payload.pop("content_sha256", None)
    payload["content_sha256"] = hashlib.sha256(_canonical(payload)).hexdigest()
    path.write_bytes(_canonical(payload))


def _terminal_fixture(tmp_path: Path) -> Path:
    run = tmp_path / "run"
    shutil.copytree(SMOKE_RUN, run)
    metadata = json.loads((run / "metadata.json").read_text(encoding="utf-8"))
    progress = json.loads((run / "progress.json").read_text(encoding="utf-8"))
    progress["status"] = proof_export.TERMINAL_UNSAT_STATUS
    progress["outer_models_seen"] = progress["committed_cut_count"]
    _write_hashed(run / "progress.json", progress)
    result = {
        "schema_version": 5, "run_id": metadata["run_id"],
        "status": proof_export.TERMINAL_UNSAT_STATUS,
        "created_utc": "2000-01-01T00:00:00+00:00", "config": metadata["config"],
        "metadata_content_sha256": metadata["content_sha256"],
        "static_encoding": metadata["static_encoding"],
        "initial_implementation_source_sha256": metadata["source_sha256"],
        "outer_models_seen": progress["committed_cut_count"],
        "committed_cut_count": progress["committed_cut_count"],
        "cut_counts": progress["cut_counts"], "logical_cut_counts": progress["logical_cut_counts"],
        "journal_head_sha256": progress["journal_head_sha256"],
        "journal_file_sha256": progress["journal_file_sha256"],
        "implementation_source_sha256": progress["implementation_source_sha256"],
    }
    _write_hashed(run / "result.json", result)
    return run


class ProofExportTests(unittest.TestCase):
    def test_paused_run_is_not_exportable(self) -> None:
        before = {name: (SMOKE_RUN / name).read_bytes() for name in ("metadata.json", "progress.json", "cuts.jsonl")}
        with self.assertRaisesRegex(ValueError, "permitted only"):
            proof_export.export_terminal_unsat(SMOKE_RUN, Path(self._tmp()) / "out")
        self.assertEqual(before, {name: (SMOKE_RUN / name).read_bytes() for name in before})

    def test_terminal_export_is_deterministic_and_hash_bound(self) -> None:
        tmp_path = Path(self._tmp())
        run = _terminal_fixture(tmp_path)
        manifest = proof_export.export_terminal_unsat(run, tmp_path / "out")
        cnf = (tmp_path / "out" / "formula.cnf").read_bytes()
        self.assertEqual(manifest["cnf"]["sha256"], hashlib.sha256(cnf).hexdigest())
        self.assertEqual(manifest["bindings"]["journal_path_sha256"], hashlib.sha256((run / "cuts.jsonl").read_bytes()).hexdigest())
        with self.assertRaises(FileExistsError):
            proof_export.export_terminal_unsat(run, tmp_path / "out")

    def test_tampered_journal_or_metadata_is_rejected(self) -> None:
        tmp_path = Path(self._tmp())
        run = _terminal_fixture(tmp_path)
        with (run / "cuts.jsonl").open("ab") as handle:
            handle.write(b" ")
        with self.assertRaisesRegex(ValueError, "trailing fragment|journal"):
            proof_export.export_terminal_unsat(run, tmp_path / "out-journal")

        run = _terminal_fixture(tmp_path / "metadata")
        metadata_path = run / "metadata.json"
        metadata_path.write_bytes(metadata_path.read_bytes().replace(b'"schema_version": 5', b'"schema_version": 6', 1))
        with self.assertRaisesRegex(ValueError, "content hash|schema"):
            proof_export.export_terminal_unsat(run, tmp_path / "out-metadata")

    def test_rehashed_source_map_tamper_is_rejected(self) -> None:
        tmp_path = Path(self._tmp())
        run = _terminal_fixture(tmp_path)
        metadata_path = run / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        key = next(iter(metadata["source_sha256"]))
        metadata["source_sha256"][key] = "0" * 64
        _write_hashed(metadata_path, metadata)
        # Keep downstream metadata-hash bindings coherent so rejection reaches
        # the engine source-pin check rather than only the JSON hash check.
        for name in ("progress.json", "result.json"):
            path = run / name
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["metadata_content_sha256"] = metadata["content_sha256"]
            _write_hashed(path, payload)
        with self.assertRaisesRegex(ValueError, "source hashes changed"):
            proof_export.export_terminal_unsat(run, tmp_path / "out-source")

    def _tmp(self) -> str:
        return self.enterContext(__import__("tempfile").TemporaryDirectory())
