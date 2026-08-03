"""Resumable exact-64 counterexample probe for Erdős #719.

The SAT variables c_e mean that triple e is missing from a 64-edge 3-graph on
nine vertices.  Exactly twenty are true.  Whenever four present tetrahedra
are pairwise edge-disjoint, their sixteen distinct triples yield the valid
clause OR_{e in union} c_e.  Reaching a model with no such packing is a
candidate, not a publication-ready result.  Incremental UNSAT has no proof.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import time
import uuid

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195


SCHEMA = "erdos719-exact64-complement-cegar-v1"
N = 9
MISSING_COUNT = 20
TRIPLES = tuple(itertools.combinations(range(N), 3))
TRIPLE_INDEX = {edge: index for index, edge in enumerate(TRIPLES)}
TETS = tuple(itertools.combinations(range(N), 4))
TET_EDGE_IDS = tuple(
    tuple(TRIPLE_INDEX[edge] for edge in itertools.combinations(vertices, 3))
    for vertices in TETS
)
TET_MASKS = tuple(sum(1 << edge for edge in edges) for edges in TET_EDGE_IDS)


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def with_hash(body: dict[str, object]) -> dict[str, object]:
    result = dict(body)
    result["content_sha256"] = sha256_bytes(canonical_json(body))
    return result


def atomic_json(path: Path, body: dict[str, object]) -> None:
    payload = json.dumps(with_hash(body), sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def verify_hashed_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    stored = payload.pop("content_sha256", None)
    if stored != sha256_bytes(canonical_json(payload)):
        raise ValueError(f"content hash mismatch: {path}")
    payload["content_sha256"] = stored
    return payload


class RunLock:
    def __init__(self, run_dir: Path):
        self.path = run_dir / ".writer.lock"
        self.active = False

    def __enter__(self) -> "RunLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        body = with_hash({"schema": SCHEMA, "pid": os.getpid(), "created_utc": utc_now()})
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical_json(body) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        self.active = True
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.active:
            self.path.unlink()
            self.active = False


def present_tetrahedra(missing: set[int]) -> tuple[int, ...]:
    return tuple(index for index, edges in enumerate(TET_EDGE_IDS) if not any(edge in missing for edge in edges))


def find_packing_four(missing: set[int]) -> tuple[int, int, int, int] | None:
    """Return four present tetrahedra with pairwise-disjoint triple sets."""

    candidates = present_tetrahedra(missing)

    def search(start: int, used: int, chosen: tuple[int, ...]) -> tuple[int, ...] | None:
        need = 4 - len(chosen)
        if need == 0:
            return chosen
        if len(candidates) - start < need:
            return None
        for position in range(start, len(candidates)):
            tet = candidates[position]
            mask = TET_MASKS[tet]
            if mask & used:
                continue
            answer = search(position + 1, used | mask, chosen + (tet,))
            if answer is not None:
                return answer
        return None

    result = search(0, 0, ())
    if result is None:
        return None
    if len(result) != 4:
        raise AssertionError("packing oracle returned wrong cardinality")
    return result  # type: ignore[return-value]


def packing_clause(packing: tuple[int, int, int, int]) -> tuple[int, ...]:
    edges = tuple(sorted(edge for tet in packing for edge in TET_EDGE_IDS[tet]))
    if len(edges) != 16 or len(set(edges)) != 16:
        raise ValueError("packing is not four edge-disjoint tetrahedra")
    return tuple(edge + 1 for edge in edges)


def validate_record(record: dict[str, object], expected_sequence: int, previous: str) -> tuple[int, ...]:
    stored = record.get("record_sha256")
    body = dict(record)
    body.pop("record_sha256", None)
    if stored != sha256_bytes(canonical_json(body)):
        raise ValueError(f"record hash mismatch at sequence {expected_sequence}")
    if record.get("schema") != SCHEMA or record.get("sequence") != expected_sequence:
        raise ValueError("journal schema/sequence mismatch")
    if record.get("previous_record_sha256") != previous:
        raise ValueError("journal chain mismatch")
    packing = tuple(int(x) for x in record["tetrahedron_indices"])
    if len(packing) != 4 or any(x < 0 or x >= len(TETS) for x in packing):
        raise ValueError("invalid tetrahedron indices")
    clause = packing_clause(packing)  # also checks edge-disjointness
    if list(clause) != record.get("clause"):
        raise ValueError("stored clause differs from packing")
    return clause


def load_journal(path: Path) -> tuple[list[dict[str, object]], str]:
    records: list[dict[str, object]] = []
    previous = "0" * 64
    if not path.exists():
        return records, previous
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise ValueError("journal has a trailing fragment; preserve and audit manually")
    for line in raw.splitlines():
        if not line.strip():
            continue
        record = json.loads(line.decode("utf-8"))
        validate_record(record, len(records), previous)
        previous = str(record["record_sha256"])
        records.append(record)
    return records, previous


def append_record(path: Path, sequence: int, previous: str, packing: tuple[int, int, int, int], missing: set[int]) -> dict[str, object]:
    clause = packing_clause(packing)
    body: dict[str, object] = {
        "schema": SCHEMA,
        "sequence": sequence,
        "previous_record_sha256": previous,
        "tetrahedron_indices": list(packing),
        "tetrahedron_vertices": [list(TETS[index]) for index in packing],
        "clause": list(clause),
        "violating_complement_sha256": sha256_bytes(bytes(index in missing for index in range(len(TRIPLES)))),
    }
    record = dict(body)
    record["record_sha256"] = sha256_bytes(canonical_json(body))
    validate_record(record, sequence, previous)
    if any(literal - 1 in missing for literal in clause):
        raise AssertionError("new cut is not violated by current complement")
    with path.open("ab") as handle:
        handle.write(canonical_json(record) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    return record


def base_encoding() -> tuple[list[list[int]], int, str]:
    pool = IDPool(start_from=len(TRIPLES) + 1)
    clauses = CardEnc.equals(
        lits=list(range(1, len(TRIPLES) + 1)),
        bound=MISSING_COUNT,
        vpool=pool,
        encoding=EncType.seqcounter,
    ).clauses
    digest = sha256_bytes(canonical_json(clauses))
    return clauses, pool.top, digest


def candidate_payload(run_id: str, missing: set[int]) -> dict[str, object]:
    present = [list(TRIPLES[index]) for index in range(len(TRIPLES)) if index not in missing]
    body: dict[str, object] = {
        "schema": "erdos719-exact64-candidate-v1",
        "run_id": run_id,
        "generated_utc": utc_now(),
        "vertices": N,
        "edge_count": len(present),
        "packing_cap_screened": 3,
        "missing_edges": [list(TRIPLES[index]) for index in sorted(missing)],
        "edges": present,
        "claim_boundary": "Candidate requires an independent exact packing checker, ex_3 bridge audit, current open-status audit, and public priority check.",
    }
    return with_hash(body)


def run(run_dir: Path, max_iterations: int, time_limit_seconds: float) -> str:
    if max_iterations < 0 or time_limit_seconds < 0 or not math.isfinite(time_limit_seconds):
        raise ValueError("limits must be finite and nonnegative")
    run_dir = run_dir.resolve()
    metadata_path = run_dir / "metadata.json"
    progress_path = run_dir / "progress.json"
    journal_path = run_dir / "cuts.jsonl"
    source_hash = file_sha256(Path(__file__))
    base, top, base_hash = base_encoding()

    with RunLock(run_dir):
        if metadata_path.exists():
            metadata = verify_hashed_json(metadata_path)
            if metadata.get("schema") != SCHEMA or metadata.get("source_sha256") != source_hash:
                raise ValueError("metadata schema/source mismatch")
            if metadata.get("base_clause_sha256") != base_hash or metadata.get("base_last_variable") != top:
                raise ValueError("base encoding mismatch")
        else:
            metadata_body: dict[str, object] = {
                "schema": SCHEMA,
                "run_id": str(uuid.uuid4()),
                "created_utc": utc_now(),
                "source_sha256": source_hash,
                "triple_count": len(TRIPLES),
                "tetrahedron_count": len(TETS),
                "missing_count": MISSING_COUNT,
                "base_clause_count": len(base),
                "base_last_variable": top,
                "base_clause_sha256": base_hash,
                "claim_boundary": "Incremental UNSAT has no proof; a candidate needs independent verification.",
            }
            atomic_json(metadata_path, metadata_body)
            metadata = verify_hashed_json(metadata_path)

        records, head = load_journal(journal_path)
        clauses = list(base)
        for sequence, record in enumerate(records):
            previous = "0" * 64 if sequence == 0 else str(records[sequence - 1]["record_sha256"])
            clauses.append(list(validate_record(record, sequence, previous)))

        started = time.monotonic()
        invocation = 0
        with Cadical195(bootstrap_with=clauses) as solver:
            while max_iterations == 0 or invocation < max_iterations:
                if time_limit_seconds and time.monotonic() - started >= time_limit_seconds:
                    break
                sat = solver.solve()
                if sat is False:
                    status = "UNSAT_NO_CERTIFICATE"
                    atomic_json(progress_path, {
                        "schema": SCHEMA,
                        "run_id": metadata["run_id"],
                        "status": status,
                        "updated_utc": utc_now(),
                        "cut_count": len(records),
                        "journal_head_sha256": head,
                        "warning": "No proof certificate was emitted; make no UNSAT claim.",
                    })
                    return status
                if sat is not True:
                    raise RuntimeError(f"solver returned {sat!r}")
                invocation += 1
                positive = {literal for literal in (solver.get_model() or []) if literal > 0}
                missing = {index for index in range(len(TRIPLES)) if index + 1 in positive}
                if len(missing) != MISSING_COUNT:
                    raise AssertionError("cardinality encoding admitted wrong complement size")
                packing = find_packing_four(missing)
                if packing is None:
                    candidate = candidate_payload(str(metadata["run_id"]), missing)
                    candidate_path = run_dir / "candidate.json"
                    candidate_path.write_text(json.dumps(candidate, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
                    status = "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION"
                    atomic_json(progress_path, {
                        "schema": SCHEMA,
                        "run_id": metadata["run_id"],
                        "status": status,
                        "updated_utc": utc_now(),
                        "cut_count": len(records),
                        "journal_head_sha256": head,
                        "candidate_file_sha256": file_sha256(candidate_path),
                    })
                    return status
                record = append_record(journal_path, len(records), head, packing, missing)
                records.append(record)
                head = str(record["record_sha256"])
                solver.add_clause(list(record["clause"]))
                atomic_json(progress_path, {
                    "schema": SCHEMA,
                    "run_id": metadata["run_id"],
                    "status": "RUNNING",
                    "updated_utc": utc_now(),
                    "cut_count": len(records),
                    "journal_head_sha256": head,
                    "invocation_models": invocation,
                })

        status = "PAUSED_AT_LIMIT"
        atomic_json(progress_path, {
            "schema": SCHEMA,
            "run_id": metadata["run_id"],
            "status": status,
            "updated_utc": utc_now(),
            "cut_count": len(records),
            "journal_head_sha256": head,
            "invocation_models": invocation,
            "invocation_elapsed_seconds": round(time.monotonic() - started, 3),
        })
        return status


def self_test() -> None:
    if len(TRIPLES) != 84 or len(TETS) != 126:
        raise AssertionError("universe size mismatch")
    complete_packing = find_packing_four(set())
    if complete_packing is None:
        raise AssertionError("complete 3-graph should contain four disjoint tetrahedra")
    clause = packing_clause(complete_packing)
    if len(clause) != 16:
        raise AssertionError("packing clause size mismatch")
    killed = {clause[0] - 1}
    if all(not any(edge in killed for edge in TET_EDGE_IDS[tet]) for tet in complete_packing):
        raise AssertionError("hitting edge did not kill recorded packing")
    base, top, digest = base_encoding()
    with Cadical195(bootstrap_with=base) as solver:
        if solver.solve() is not True:
            raise AssertionError("base exact-20 encoding should be satisfiable")
        model = {literal for literal in (solver.get_model() or []) if literal > 0}
        if sum(index + 1 in model for index in range(84)) != 20:
            raise AssertionError("base model cardinality mismatch")
    print(json.dumps({
        "status": "PASS",
        "triple_count": len(TRIPLES),
        "tetrahedron_count": len(TETS),
        "packing_clause_size": len(clause),
        "base_clause_count": len(base),
        "base_last_variable": top,
        "base_clause_sha256": digest,
    }, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("self-test")
    command = sub.add_parser("run")
    command.add_argument("--run-dir", required=True, type=Path)
    command.add_argument("--max-iterations", type=int, default=1000)
    command.add_argument("--time-limit-seconds", type=float, default=600.0)
    args = parser.parse_args()
    if args.command == "self-test":
        self_test()
        return 0
    status = run(args.run_dir, args.max_iterations, args.time_limit_seconds)
    print(json.dumps({"status": status, "run_dir": str(args.run_dir.resolve())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
