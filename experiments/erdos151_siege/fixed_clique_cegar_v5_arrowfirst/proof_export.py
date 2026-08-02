#!/usr/bin/env python3
"""Read-only, terminal-UNSAT CNF exporter for schema-5 arrowing-first runs.

This adapter deliberately does not modify ``cegar.py`` and never obtains a
run-directory writer lock. It reconstructs static CNF and every journal cut.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Sequence

HERE = Path(__file__).resolve().parent
ENGINE_PATH = HERE / "cegar.py"
SCHEMA_VERSION = 1
TERMINAL_UNSAT_STATUS = "OUTER_UNSAT_NO_PROOF_CERTIFICATE"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _write_hashed_json(path: Path, payload: dict[str, Any]) -> None:
    body = dict(payload)
    body.pop("content_sha256", None)
    body["content_sha256"] = _sha256_bytes(_canonical_json_bytes(body))
    path.write_bytes(_canonical_json_bytes(body))


def _load_engine() -> Any:
    """Load the audited engine without importing this adapter into its hashes."""
    spec = importlib.util.spec_from_file_location("_erdos151_fixed_clique_cegar_v5_proof_export", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load engine from {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _render_dimacs(clauses: Sequence[Sequence[int]]) -> tuple[bytes, int]:
    max_var = max((abs(lit) for clause in clauses for lit in clause), default=0)
    rendered = [f"p cnf {max_var} {len(clauses)}\n".encode("ascii")]
    rendered.extend((" ".join(map(str, clause)) + " 0\n").encode("ascii") for clause in clauses)
    return b"".join(rendered), max_var


def _open_terminal_session(engine: Any, run_dir: Path) -> Any:
    # These flags keep inherited persistence strictly read-only: no repair,
    # checkpoint, lock, or outer solve invocation.
    session = engine.SearchSession.from_existing(
        run_dir.resolve(), allow_code_drift=False, collect_clauses=True,
        validate_records=True, repair_journal=False, checkpoint_ready=False,
        run_lock=None,
    )
    result = session.result
    if result is None or result.get("status") != TERMINAL_UNSAT_STATUS:
        status = None if result is None else result.get("status")
        session.problem.close()
        raise ValueError("proof export is permitted only for a preserved " f"{TERMINAL_UNSAT_STATUS} result.json (found {status!r})")
    return session


def reconstruct_terminal_unsat(run_dir: Path) -> tuple[bytes, dict[str, Any]]:
    """Rebuild and independently re-rebuild the current journal formula."""
    engine = _load_engine()
    first = _open_terminal_session(engine, run_dir)
    try:
        clauses = first.problem.collected_clauses
        if clauses is None:
            raise AssertionError("clause collection was unexpectedly disabled")
        dimacs, variables = _render_dimacs(clauses)
        metadata, progress, result = first.metadata, first.progress, first.result
        if progress is None or result is None:
            raise AssertionError("terminal session lacks bound progress/result")
        bindings: dict[str, Any] = {
            "run_id": metadata["run_id"],
            "metadata_content_sha256": metadata["content_sha256"],
            "metadata_file_sha256": _sha256_file(run_dir / "metadata.json"),
            "progress_content_sha256": progress["content_sha256"],
            "progress_file_sha256": _sha256_file(run_dir / "progress.json"),
            "result_content_sha256": result["content_sha256"],
            "result_file_sha256": _sha256_file(run_dir / "result.json"),
            "journal_head_sha256": first.journal.head,
            "journal_file_sha256": first.journal.file_sha256(),
            "journal_path_sha256": _sha256_file(run_dir / "cuts.jsonl"),
            "committed_cut_count": len(first.journal.records),
            "static_encoding": metadata["static_encoding"],
            "recorded_initial_sources": metadata["source_sha256"],
            "replayed_engine_sources": first.current_sources,
            "engine_cegar_py_sha256": _sha256_file(ENGINE_PATH),
        }
    finally:
        first.problem.close()

    # Determinism check happens before any output is written and repeats all
    # source, journal, witness, and regenerated-cut validation.
    second = _open_terminal_session(engine, run_dir)
    try:
        second_clauses = second.problem.collected_clauses
        if second_clauses is None:
            raise AssertionError("clause collection was unexpectedly disabled")
        repeated, repeated_variables = _render_dimacs(second_clauses)
    finally:
        second.problem.close()
    if repeated != dimacs or repeated_variables != variables:
        raise RuntimeError("two read-only CNF reconstructions were not byte-identical")
    bindings["variables"] = variables
    bindings["clauses"] = len(clauses)
    return dimacs, bindings


def export_terminal_unsat(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Create a fresh directory containing ``formula.cnf`` and a manifest."""
    run_dir, output_dir = run_dir.resolve(), output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing output directory: {output_dir}")
    dimacs, bindings = reconstruct_terminal_unsat(run_dir)
    output_dir.mkdir(parents=True)
    cnf_path = output_dir / "formula.cnf"
    cnf_path.write_bytes(dimacs)
    manifest: dict[str, Any] = {
        "artifact_type": "erdos151_schema5_terminal_unsat_cnf_export",
        "export_schema_version": SCHEMA_VERSION,
        "terminal_status_required": TERMINAL_UNSAT_STATUS,
        "warning": "This export is proof-ready input only; it does not establish UNSAT or any theorem.",
        "cnf": {
            "filename": cnf_path.name, "sha256": _sha256_file(cnf_path), "bytes": len(dimacs),
            "variables": bindings.pop("variables"), "clauses": bindings.pop("clauses"),
            "format": "DIMACS CNF, ASCII, LF newlines, deterministic clause order",
        },
        "bindings": bindings,
        "exporter": {"filename": Path(__file__).name, "sha256": _sha256_file(Path(__file__)), "engine_filename": ENGINE_PATH.name},
        "replay": {
            "method": "two separate executions of the same read-only reconstruction path compared byte-for-byte before export",
            "scope": "engine static CNF plus every committed journal cut; lazy forbidden-clique policy retained exactly as recorded",
        },
    }
    manifest_path = output_dir / "manifest.json"
    _write_hashed_json(manifest_path, manifest)
    return json.loads(manifest_path.read_text(encoding="ascii"))


def _solver_instructions() -> str:
    root = HERE.parents[2]
    cadical = root / "third_party" / "cadical" / "cadical-linux"
    drat = root / "third_party" / "drat-trim" / "drat-trim"
    lrat = root / "third_party" / "drat-trim" / "lrat-check"
    return f"""Linux/WSL proof workflow (not run by this exporter):

  # Consult solver --help for proof options; do not treat its UNSAT exit as a proof.
  {cadical} formula.cnf proof.drat
  {drat} formula.cnf proof.drat -L proof.lrat
  {lrat} formula.cnf proof.lrat

Record SHA-256 hashes of formula.cnf, manifest.json, proof, and checker logs.
The bundled binaries are Linux executables and are not invoked on this Windows host.
"""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="read-only terminal-UNSAT CNF export")
    export.add_argument("--run-dir", required=True, type=Path)
    export.add_argument("--output-dir", required=True, type=Path)
    sub.add_parser("solver-instructions", help="print proof generation/check commands")
    args = parser.parse_args(argv)
    if args.command == "solver-instructions":
        print(_solver_instructions(), end="")
        return 0
    print(json.dumps(export_terminal_unsat(args.run_dir, args.output_dir), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
