"""Durable, hash-chained checkpoints for the n=50 CEGAR successors.

The journal stores semantic cut certificates rather than solver-internal
state.  Rebuilding the deterministic static formula and replaying the valid
prefix reconstructs exactly the recorded incremental formula, verified by a
per-round formula hash.  CaDiCaL's private learned-clause/branching state is
not serialized, so the future model sequence after a resume may legitimately
diverge from an uninterrupted run.  A truncated final line is quarantined;
any other parse, sequence, or hash failure is fatal.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any

from pysat.formula import CNF
from pysat.solvers import Cadical195


SCHEMA = "erdos151-matching3-tcg3-checkpoint-v1"


class ExclusiveRunLock:
    """Hold one OS byte-range lock for the lifetime of a journal writer.

    The lock is released by the kernel if the process dies.  Every writer to a
    journal must honor this lock; readers remain lock-free.  This protects
    ordinary process/AppX teardown and accidental double launches.  It is not
    advertised as a guarantee against sudden power loss.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._stream = None

    def __enter__(self) -> "ExclusiveRunLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        stream = self.path.open("a+b")
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        try:
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            stream.close()
            raise RuntimeError(
                f"checkpoint journal already has an active writer: {self.path}"
            ) from error
        self._stream = stream
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._stream is None:
            return
        try:
            self._stream.seek(0)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(self._stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._stream.fileno(), fcntl.LOCK_UN)
        finally:
            self._stream.close()
            self._stream = None


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def object_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def file_hash(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_write_text(path: str | Path, text: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, destination)


def atomic_write_bytes(path: str | Path, payload: bytes) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    with temporary.open("wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, destination)


def rng_state_to_json(state: tuple[Any, ...]) -> dict[str, object]:
    version, values, gaussian = state
    return {"version": int(version), "values": list(values), "gaussian": gaussian}


def rng_state_from_json(payload: dict[str, object]) -> tuple[Any, ...]:
    values = payload.get("values")
    if not isinstance(values, list) or not all(isinstance(value, int) for value in values):
        raise ValueError("invalid RNG state values")
    version = payload.get("version")
    if not isinstance(version, int):
        raise ValueError("invalid RNG state version")
    return version, tuple(values), payload.get("gaussian")


class RecordingCadical:
    """A CaDiCaL facade retaining every input clause for exact export/hash."""

    def __init__(self) -> None:
        self._solver = Cadical195()
        self.clauses: list[tuple[int, ...]] = []
        self._formula_digest = hashlib.sha256()

    def add_clause(self, clause: list[int] | tuple[int, ...]) -> None:
        frozen = tuple(int(literal) for literal in clause)
        if not frozen:
            raise ValueError("refusing to record an empty clause")
        self.clauses.append(frozen)
        self._formula_digest.update(struct.pack("<I", len(frozen)))
        for literal in frozen:
            self._formula_digest.update(struct.pack("<q", literal))
        self._solver.add_clause(list(frozen))

    def solve(self) -> bool:
        return bool(self._solver.solve())

    def get_model(self) -> list[int]:
        model = self._solver.get_model()
        if model is None:
            raise RuntimeError("model requested without SAT result")
        return model

    def delete(self) -> None:
        self._solver.delete()

    def formula_hash(self) -> str:
        return self._formula_digest.hexdigest()

    def write_dimacs_atomic(self, path: str | Path) -> None:
        destination = Path(path)
        temporary = destination.with_name(destination.name + ".tmp")
        destination.parent.mkdir(parents=True, exist_ok=True)
        CNF(from_clauses=[list(clause) for clause in self.clauses]).to_file(
            str(temporary)
        )
        with temporary.open("ab") as stream:
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)


class CutJournal:
    def __init__(
        self,
        path: str | Path,
        config: dict[str, object],
        static_formula_sha256: str,
    ) -> None:
        self.path = Path(path)
        self.config = config
        self.static_formula_sha256 = static_formula_sha256
        self.records: list[dict[str, object]] = []
        self.last_hash = "0" * 64
        self.ignored_truncated_tail = False
        if self.path.exists():
            self._load()
        else:
            self._create()

    def _create(self) -> None:
        header_core = {
            "type": "header",
            "schema": SCHEMA,
            "config": self.config,
            "static_formula_sha256": self.static_formula_sha256,
        }
        header = {**header_core, "record_sha256": object_hash(header_core)}
        atomic_write_text(self.path, canonical_json(header) + "\n")
        self.last_hash = str(header["record_sha256"])

    def _load(self) -> None:
        raw = self.path.read_bytes()
        lines = raw.splitlines(keepends=True)
        if lines and not lines[-1].endswith((b"\n", b"\r")):
            truncated_tail = lines[-1]
            lines = lines[:-1]
            self.ignored_truncated_tail = True
            tail_hash = hashlib.sha256(truncated_tail).hexdigest()
            tail_path = self.path.with_name(
                self.path.name + f".truncated-tail-{tail_hash}.bin"
            )
            if not tail_path.exists():
                atomic_write_bytes(tail_path, truncated_tail)
            atomic_write_bytes(self.path, b"".join(lines))
        if not lines:
            raise ValueError("checkpoint has no complete header line")
        decoded: list[dict[str, object]] = []
        for index, line in enumerate(lines):
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid complete checkpoint line {index}: {error}") from error
            if not isinstance(value, dict):
                raise ValueError(f"checkpoint line {index} is not an object")
            decoded.append(value)
        header = decoded[0]
        claimed_header_hash = header.get("record_sha256")
        header_core = {key: value for key, value in header.items() if key != "record_sha256"}
        if claimed_header_hash != object_hash(header_core):
            raise ValueError("checkpoint header hash mismatch")
        if header_core.get("schema") != SCHEMA:
            raise ValueError("checkpoint schema mismatch")
        if header_core.get("config") != self.config:
            raise ValueError("checkpoint configuration mismatch")
        if header_core.get("static_formula_sha256") != self.static_formula_sha256:
            raise ValueError("checkpoint static-formula hash mismatch")
        previous = str(claimed_header_hash)
        for expected_sequence, record in enumerate(decoded[1:]):
            claimed = record.get("record_sha256")
            core = {key: value for key, value in record.items() if key != "record_sha256"}
            if core.get("type") != "round":
                raise ValueError(f"checkpoint record {expected_sequence} has wrong type")
            if core.get("sequence") != expected_sequence:
                raise ValueError(f"checkpoint sequence mismatch at {expected_sequence}")
            if core.get("previous_sha256") != previous:
                raise ValueError(f"checkpoint hash-chain mismatch at {expected_sequence}")
            if claimed != object_hash(core):
                raise ValueError(f"checkpoint record hash mismatch at {expected_sequence}")
            self.records.append(record)
            previous = str(claimed)
        self.last_hash = previous

    def append_round(self, payload: dict[str, object]) -> dict[str, object]:
        core = {
            "type": "round",
            "sequence": len(self.records),
            "previous_sha256": self.last_hash,
            **payload,
        }
        record = {**core, "record_sha256": object_hash(core)}
        encoded = (canonical_json(record) + "\n").encode("ascii")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("ab") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        self.records.append(record)
        self.last_hash = str(record["record_sha256"])
        return record

    def write_state(self, path: str | Path, extra: dict[str, object]) -> None:
        payload = {
            "schema": SCHEMA,
            "journal": self.path.as_posix(),
            "journal_sha256": file_hash(self.path),
            "last_record_sha256": self.last_hash,
            "completed_rounds": len(self.records),
            "ignored_truncated_tail_on_load": self.ignored_truncated_tail,
            "config": self.config,
            "static_formula_sha256": self.static_formula_sha256,
            **extra,
        }
        atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")
