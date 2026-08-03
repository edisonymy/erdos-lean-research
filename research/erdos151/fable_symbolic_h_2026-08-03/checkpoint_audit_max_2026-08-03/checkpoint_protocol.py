#!/usr/bin/env python3
"""Reference semantic-cut journal for the n=50 CEGAR successor.

This module is deliberately independent of the production solver.  It does
not import PySAT or any campaign encoding.  Its job is narrower:

* validate that every persisted learned clause is one of the two mathematically
  sound schemas (an h-set obstruction or a full two-partition obstruction),
* make records immutable and hash chained,
* commit each record before the live solver is allowed to apply its cuts, and
* recover only a complete, verified prefix after interruption.

The production integration MUST call ``commit_record`` before adding the
record's clauses to its in-memory solver.  A return from ``commit_record`` is
the commit point.  Temporary files are never part of the journal.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Iterable


MANIFEST_SCHEMA = "erdos151-cegar-semantic-journal-manifest-v1"
RECORD_SCHEMA = "erdos151-cegar-semantic-cut-record-v1"
MANIFEST_DOMAIN = b"erdos151-cegar-manifest-v1\x00"
RECORD_DOMAIN = b"erdos151-cegar-record-v1\x00"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RUN_FILE = re.compile(r"^RUN\.([0-9a-f]{64})\.json$")
RECORD_FILE = re.compile(r"^(\d{9})\.([0-9a-f]{64})\.json$")


class JournalError(RuntimeError):
    """A journal is malformed, ambiguous, corrupt, or semantically unsafe."""


def canonical_json(value: Any) -> bytes:
    """The sole byte representation hashed by this protocol."""

    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _is_hash(value: Any) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def _require_hash(value: Any, field: str) -> str:
    if not _is_hash(value):
        raise JournalError(f"{field} is not a lowercase SHA-256")
    return value


def _require_exact_keys(value: dict[str, Any], keys: set[str], what: str) -> None:
    actual = set(value)
    if actual != keys:
        raise JournalError(
            f"{what} keys differ: missing={sorted(keys-actual)}, "
            f"extra={sorted(actual-keys)}"
        )


def _require_int(value: Any, field: str, low: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise JournalError(f"{field} is not an integer")
    if low is not None and value < low:
        raise JournalError(f"{field} is below {low}")
    return value


def validate_manifest(manifest: dict[str, Any]) -> None:
    required = {
        "schema",
        "run_id",
        "n",
        "h",
        "min_degree",
        "max_degree",
        "seed",
        "cuts_per_round",
        "required_maximal_edge_matching",
        "static_variables",
        "static_clauses",
        "static_cnf_sha256",
        "variable_map_sha256",
        "source_bundle_sha256",
        "environment_lock_sha256",
        "soundness_packet_sha256",
    }
    _require_exact_keys(manifest, required, "manifest")
    if manifest["schema"] != MANIFEST_SCHEMA:
        raise JournalError("wrong manifest schema")
    if not isinstance(manifest["run_id"], str) or not manifest["run_id"]:
        raise JournalError("run_id must be a nonempty string")
    n = _require_int(manifest["n"], "n", 1)
    h = _require_int(manifest["h"], "h", 1)
    minimum = _require_int(manifest["min_degree"], "min_degree", 0)
    maximum = _require_int(manifest["max_degree"], "max_degree", 0)
    if minimum > maximum or maximum >= n:
        raise JournalError("invalid degree interval")
    _require_int(manifest["seed"], "seed", 0)
    _require_int(manifest["cuts_per_round"], "cuts_per_round", 1)
    required_matching = _require_int(
        manifest["required_maximal_edge_matching"],
        "required_maximal_edge_matching",
        0,
    )
    if required_matching > n // 2:
        raise JournalError("matching requirement exceeds floor(n/2)")
    _require_int(manifest["static_variables"], "static_variables", 1)
    _require_int(manifest["static_clauses"], "static_clauses", 1)
    for key in (
        "static_cnf_sha256",
        "variable_map_sha256",
        "source_bundle_sha256",
        "environment_lock_sha256",
        "soundness_packet_sha256",
    ):
        _require_hash(manifest[key], key)
    if h > n:
        raise JournalError("h cannot exceed n for this journal")


def manifest_hash(manifest: dict[str, Any]) -> str:
    validate_manifest(manifest)
    return hashlib.sha256(MANIFEST_DOMAIN + canonical_json(manifest)).hexdigest()


def _validate_sorted_vertices(
    vertices: Any, *, n: int, expected_length: int | None, field: str
) -> list[int]:
    if not isinstance(vertices, list):
        raise JournalError(f"{field} is not a list")
    if any(isinstance(v, bool) or not isinstance(v, int) for v in vertices):
        raise JournalError(f"{field} contains a non-integer")
    if vertices != sorted(set(vertices)):
        raise JournalError(f"{field} must be strictly increasing")
    if any(v < 0 or v >= n for v in vertices):
        raise JournalError(f"{field} has an out-of-range vertex")
    if expected_length is not None and len(vertices) != expected_length:
        raise JournalError(
            f"{field} has length {len(vertices)}, expected {expected_length}"
        )
    return vertices


def validate_cut(cut: dict[str, Any], manifest: dict[str, Any]) -> None:
    if not isinstance(cut, dict):
        raise JournalError("cut is not an object")
    kind = cut.get("kind")
    n, h = manifest["n"], manifest["h"]
    if kind == "admissible_h_set":
        _require_exact_keys(cut, {"kind", "vertices"}, "admissible cut")
        _validate_sorted_vertices(
            cut["vertices"], n=n, expected_length=h, field="vertices"
        )
        return
    if kind == "tcg3_partition":
        _require_exact_keys(cut, {"kind", "side_zero"}, "TCG-3 cut")
        side = _validate_sorted_vertices(
            cut["side_zero"], n=n, expected_length=None, field="side_zero"
        )
        # Canonical color-complement representative.  Storing one side is
        # sufficient because the other is its complement.
        if 0 not in side:
            raise JournalError("canonical TCG-3 side_zero must contain vertex 0")
        if len(side) == n:
            raise JournalError("TCG-3 partition must have two nonempty sides")
        other_size = n - len(side)
        if len(side) < 3 and other_size < 3:
            raise JournalError("TCG-3 cut would be empty")
        return
    raise JournalError(f"unknown cut kind: {kind!r}")


def validate_record_body(
    body: dict[str, Any], manifest: dict[str, Any], expected_index: int, prev: str
) -> None:
    required = {
        "schema",
        "run_id",
        "index",
        "round",
        "prev_sha256",
        "static_cnf_sha256",
        "model_edge_sha256",
        "cuts",
    }
    _require_exact_keys(body, required, "record body")
    if body["schema"] != RECORD_SCHEMA:
        raise JournalError("wrong record schema")
    if body["run_id"] != manifest["run_id"]:
        raise JournalError("record belongs to a different run")
    if _require_int(body["index"], "index", 0) != expected_index:
        raise JournalError("record index is not contiguous")
    if _require_int(body["round"], "round", 0) != expected_index:
        raise JournalError("v1 requires exactly one committed record per round")
    if body["prev_sha256"] != prev:
        raise JournalError("hash-chain predecessor mismatch")
    if body["static_cnf_sha256"] != manifest["static_cnf_sha256"]:
        raise JournalError("record static-CNF digest mismatch")
    _require_hash(body["model_edge_sha256"], "model_edge_sha256")
    cuts = body["cuts"]
    if not isinstance(cuts, list) or not cuts:
        raise JournalError("a nonterminal round must commit at least one cut")
    tcg_positions = []
    for index, cut in enumerate(cuts):
        validate_cut(cut, manifest)
        if cut["kind"] == "tcg3_partition":
            tcg_positions.append(index)
    if len(tcg_positions) > 1:
        raise JournalError("at most one TCG-3 partition is allowed per round")
    if tcg_positions and tcg_positions != [0]:
        raise JournalError("TCG-3 cut must precede admissible-set cuts")
    admissible_count = sum(c["kind"] == "admissible_h_set" for c in cuts)
    if admissible_count > manifest["cuts_per_round"]:
        raise JournalError("too many admissible cuts in a round")


def record_hash(body: dict[str, Any]) -> str:
    prev = _require_hash(body.get("prev_sha256"), "prev_sha256")
    return hashlib.sha256(
        RECORD_DOMAIN + bytes.fromhex(prev) + canonical_json(body)
    ).hexdigest()


def _write_through_rename(source: Path, destination: Path) -> None:
    """Same-directory atomic publication, with Windows write-through."""

    if source.parent.resolve() != destination.parent.resolve():
        raise JournalError("atomic rename must stay in one directory")
    if os.name == "nt":
        # MOVEFILE_WRITE_THROUGH.  Deliberately omit MOVEFILE_REPLACE_EXISTING:
        # immutable journal objects must never replace an existing object.
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        move_file_ex = kernel32.MoveFileExW
        move_file_ex.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
        move_file_ex.restype = ctypes.c_int
        if not move_file_ex(str(source), str(destination), 0x8):
            raise ctypes.WinError(ctypes.get_last_error())
    else:
        # Atomic no-replace publication: a second writer cannot overwrite an
        # immutable object between the caller's existence check and commit.
        os.link(source, destination)
        source.unlink()
        directory_fd = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)


def _commit_immutable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise JournalError(f"immutable object collision: {path.name}")
        return
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        _write_through_rename(temporary, path)
        if path.read_bytes() != data:
            raise JournalError(f"read-back mismatch after commit: {path.name}")
    finally:
        if temporary.exists():
            temporary.unlink()


def create_manifest(directory: Path, manifest: dict[str, Any]) -> str:
    digest = manifest_hash(manifest)
    envelope = {"manifest": manifest, "sha256": digest}
    _commit_immutable(
        directory / f"RUN.{digest}.json", canonical_json(envelope) + b"\n"
    )
    return digest


def commit_record(
    directory: Path,
    manifest: dict[str, Any],
    body: dict[str, Any],
    *,
    expected_index: int,
    prev: str,
) -> str:
    """Durably commit a semantic transaction; apply its cuts only afterward."""

    validate_manifest(manifest)
    validate_record_body(body, manifest, expected_index, prev)
    digest = record_hash(body)
    envelope = {"body": body, "sha256": digest}
    _commit_immutable(
        directory / f"{expected_index:09d}.{digest}.json",
        canonical_json(envelope) + b"\n",
    )
    return digest


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="ascii"))
    except Exception as exc:  # A corrupt committed object is fatal, not skipped.
        raise JournalError(f"cannot parse {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise JournalError(f"{path.name} is not a JSON object")
    return value


def scan_journal(directory: Path) -> dict[str, Any]:
    """Verify one manifest and the entire unambiguous committed chain."""

    temporary = sorted(
        {p.name for p in directory.glob("*.tmp")}
        | {p.name for p in directory.glob(".*.tmp")}
    )
    manifest_files = []
    records_by_index: dict[int, list[tuple[Path, str]]] = {}
    unexpected = []
    for path in directory.iterdir():
        if not path.is_file() or path.name.endswith(".tmp"):
            continue
        match = RUN_FILE.fullmatch(path.name)
        if match:
            manifest_files.append((path, match.group(1)))
            continue
        match = RECORD_FILE.fullmatch(path.name)
        if match:
            records_by_index.setdefault(int(match.group(1)), []).append(
                (path, match.group(2))
            )
            continue
        unexpected.append(path.name)
    if unexpected:
        raise JournalError(f"unexpected committed files: {sorted(unexpected)}")
    if len(manifest_files) != 1:
        raise JournalError(f"expected exactly one run manifest, found {len(manifest_files)}")
    manifest_path, named_manifest_hash = manifest_files[0]
    envelope = _load_json(manifest_path)
    _require_exact_keys(envelope, {"manifest", "sha256"}, "manifest envelope")
    manifest = envelope["manifest"]
    if not isinstance(manifest, dict):
        raise JournalError("manifest payload is not an object")
    computed_manifest_hash = manifest_hash(manifest)
    if envelope["sha256"] != computed_manifest_hash:
        raise JournalError("manifest envelope hash mismatch")
    if named_manifest_hash != computed_manifest_hash:
        raise JournalError("manifest filename hash mismatch")

    if records_by_index:
        maximum = max(records_by_index)
        expected_indices = set(range(maximum + 1))
        missing = sorted(expected_indices - set(records_by_index))
        if missing:
            raise JournalError(f"record-index gap: {missing[:10]}")
    else:
        maximum = -1

    prev = computed_manifest_hash
    cut_counts = {"admissible_h_set": 0, "tcg3_partition": 0}
    record_hashes = []
    for index in range(maximum + 1):
        candidates = records_by_index[index]
        if len(candidates) != 1:
            raise JournalError(f"fork at record index {index}")
        path, named_hash = candidates[0]
        envelope = _load_json(path)
        _require_exact_keys(envelope, {"body", "sha256"}, "record envelope")
        body = envelope["body"]
        if not isinstance(body, dict):
            raise JournalError("record body is not an object")
        validate_record_body(body, manifest, index, prev)
        computed = record_hash(body)
        if envelope["sha256"] != computed:
            raise JournalError(f"record {index} envelope hash mismatch")
        if named_hash != computed:
            raise JournalError(f"record {index} filename hash mismatch")
        for cut in body["cuts"]:
            cut_counts[cut["kind"]] += 1
        record_hashes.append(computed)
        prev = computed

    normalized = {
        "manifest_sha256": computed_manifest_hash,
        "record_hashes": record_hashes,
    }
    return {
        "schema": "erdos151-cegar-semantic-journal-audit-v1",
        "status": "PASS",
        "run_id": manifest["run_id"],
        "records": len(record_hashes),
        "head_sha256": prev,
        "cut_counts": cut_counts,
        "normalized_chain_sha256": hashlib.sha256(
            canonical_json(normalized)
        ).hexdigest(),
        "temporary_files_ignored": temporary,
    }


def canonical_tcg_side_zero(
    side_a: Iterable[int], side_b: Iterable[int], n: int
) -> list[int]:
    a, b = sorted(side_a), sorted(side_b)
    if set(a) & set(b):
        raise JournalError("partition sides overlap")
    if set(a) | set(b) != set(range(n)):
        raise JournalError("partition sides do not cover exactly range(n)")
    if not a or not b:
        raise JournalError("partition sides must both be nonempty")
    if 0 in a:
        return a
    if 0 in b:
        return b
    raise JournalError("partition omits vertex 0")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("journal", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = scan_journal(args.journal.resolve())
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
