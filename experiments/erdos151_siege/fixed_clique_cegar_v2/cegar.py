#!/usr/bin/env python3
"""Schema-v2 batched fixed-clique CEGAR search.

The audited schema-v1 implementation at commit a167ff8 is loaded read-only and
source-pinned.  This module changes the static forbidden-clique policy and the
journaled cut unit, so v1 run directories are deliberately not resumable here.
"""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
UPSTREAM_DIR = HERE.parent / "fixed_clique_cegar"
CASES_PATH = HERE / "cases.json"
SCHEMA_VERSION = 2
UPSTREAM_COMMIT = "a167ff8453bd605985d7d743e80529e04c70d652"
UPSTREAM_EXPECTED_SHA256 = {
    "cegar.py": "c0795a26297d0b3a9d624b418f69857bb68884c0125ff8f941b38ab52a0232e6",
    "verify_candidate.py": "2979e842e681b66c1a0c82c590b037c80a0457196fd6c4889b4e85ad1413d363",
    "cases.json": "001343ad3f49cd7c501ae63483c56a58068f301d45f3eb90afec9a5d8c9d606a",
    "requirements.txt": "34ffbeff9bca7b83c0acfb0b8614db5c391c7c9b4a28eb8c2b7539afd85d6169",
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_upstream_snapshot() -> None:
    actual = {
        name: _sha256_file(UPSTREAM_DIR / name)
        for name in UPSTREAM_EXPECTED_SHA256
    }
    if actual != UPSTREAM_EXPECTED_SHA256:
        raise RuntimeError(
            "the read-only a167ff8 upstream snapshot no longer matches its pin: "
            f"expected={UPSTREAM_EXPECTED_SHA256}, actual={actual}"
        )


def _load_upstream() -> object:
    verify_upstream_snapshot()
    path = UPSTREAM_DIR / "cegar.py"
    name = "_erdos151_fixed_clique_cegar_a167ff8_readonly"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pinned upstream implementation from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_v1 = _load_upstream()
_V1OuterProblem = _v1.OuterProblem
_V1SearchSession = _v1.SearchSession
_v1_validate_cut_witness = _v1.validate_cut_witness

# Stable public aliases.  Their implementations are part of the pinned source
# hash set below; v2 never writes into UPSTREAM_DIR.
CardEnc = _v1.CardEnc
Cadical195 = _v1.Cadical195
CutEncoding = _v1.CutEncoding
EdgeVariables = _v1.EdgeVariables
EncType = _v1.EncType
GraphSnapshot = _v1.GraphSnapshot
IDPool = _v1.IDPool
RunDirectoryLock = _v1.RunDirectoryLock
admissibility_oracle_v1 = _v1.admissibility_oracle
atomic_write_json = _v1.atomic_write_json
canonical_json_bytes = _v1.canonical_json_bytes
clause_stream_sha256 = _v1.clause_stream_sha256
coloring_oracle = _v1.coloring_oracle
file_sha256 = _v1.file_sha256
find_clique = _v1.find_clique
graph_from_solver_model = _v1.graph_from_solver_model
is_clique = _v1.is_clique
load_hashed_json = _v1.read_hashed_json
maximal_cliques_bk = _v1.maximal_cliques_bk
pack_bits = _v1.pack_bits
set_is_admissible = _v1.set_is_admissible
sha256_bytes = _v1.sha256_bytes
summarize_encoding = _v1.summarize_encoding
triangles = _v1.triangles
unpack_bits = _v1.unpack_bits
validate_static_candidate = _v1.validate_static_candidate


@dataclasses.dataclass(frozen=True)
class CaseConfig:
    name: str
    n: int
    fixed_clique_size: int
    forbidden_clique_size: int
    degree_min: int
    degree_max: int
    target_set_size: int
    scope: str
    forbidden_mode: str = "lazy"
    admissibility_batch_size: int = 8

    def validate(self) -> None:
        if not 2 <= self.fixed_clique_size <= self.n:
            raise ValueError("fixed clique size must lie in [2,n]")
        if not self.fixed_clique_size < self.forbidden_clique_size <= self.n + 1:
            raise ValueError("forbidden clique must be larger than the fixed clique")
        if not 0 <= self.degree_min <= self.degree_max < self.n:
            raise ValueError("invalid degree range")
        if not 2 <= self.target_set_size <= self.n:
            raise ValueError("invalid target set size")
        if self.forbidden_mode not in {"lazy", "eager"}:
            raise ValueError("forbidden_mode must be 'lazy' or 'eager'")
        if not 1 <= self.admissibility_batch_size <= 1024:
            raise ValueError("admissibility_batch_size must lie in [1,1024]")

    def as_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "CaseConfig":
        result = cls(
            name=str(value["name"]),
            n=int(value["n"]),
            fixed_clique_size=int(value["fixed_clique_size"]),
            forbidden_clique_size=int(value["forbidden_clique_size"]),
            degree_min=int(value["degree_min"]),
            degree_max=int(value["degree_max"]),
            target_set_size=int(value["target_set_size"]),
            scope=str(value["scope"]),
            forbidden_mode=str(value.get("forbidden_mode", "lazy")),
            admissibility_batch_size=int(value.get("admissibility_batch_size", 8)),
        )
        result.validate()
        return result


def load_cases() -> dict[str, CaseConfig]:
    raw = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported cases.json schema")
    result: dict[str, CaseConfig] = {}
    for name, body in raw["cases"].items():
        value = dict(body)
        value["name"] = name
        result[name] = CaseConfig.from_dict(value)
    return result


def collect_source_hashes() -> dict[str, str]:
    verify_upstream_snapshot()
    paths = {
        "v2/cegar.py": HERE / "cegar.py",
        "v2/verify_candidate.py": HERE / "verify_candidate.py",
        "v2/cases.json": HERE / "cases.json",
        "v2/requirements.txt": HERE / "requirements.txt",
        "upstream-a167ff8/cegar.py": UPSTREAM_DIR / "cegar.py",
        "upstream-a167ff8/verify_candidate.py": UPSTREAM_DIR / "verify_candidate.py",
        "upstream-a167ff8/cases.json": UPSTREAM_DIR / "cases.json",
        "upstream-a167ff8/requirements.txt": UPSTREAM_DIR / "requirements.txt",
    }
    return {name: _sha256_file(path) for name, path in paths.items()}


def enumerate_cliques_exact(adj: Sequence[int], size: int) -> list[tuple[int, ...]]:
    """Enumerate every clique of ``size`` once, in lexicographic order."""

    n = len(adj)
    if size < 0:
        raise ValueError("clique size must be nonnegative")
    found: list[tuple[int, ...]] = []

    def extend(chosen: tuple[int, ...], candidates: int) -> None:
        need = size - len(chosen)
        if need == 0:
            found.append(chosen)
            return
        scan = candidates
        while scan.bit_count() >= need:
            bit = scan & -scan
            scan ^= bit
            vertex = bit.bit_length() - 1
            extend(chosen + (vertex,), scan & adj[vertex])

    extend((), (1 << n) - 1)
    return found


@dataclasses.dataclass(frozen=True)
class AdmissibilityBatch:
    vertex_sets: tuple[tuple[int, ...], ...]
    maximal_clique_count: int
    enumeration_exhausted: bool
    solver_calls: int


def admissibility_oracle_batch(
    graph: GraphSnapshot,
    target_size: int,
    batch_limit: int,
) -> AdmissibilityBatch | None:
    """Find up to ``batch_limit`` distinct admissible target-size sets.

    After each target set S is read from a model, ``OR(v notin selection for
    v in S)`` blocks S and every superset of S.  Because admissibility is
    downward closed and every returned witness is trimmed to exactly the
    target size, this enumerates distinct witnesses without losing any other
    target-size witness.
    """

    if batch_limit < 1:
        raise ValueError("batch_limit must be positive")
    adj = graph.adjacency()
    maximal = [mask for mask in maximal_cliques_bk(adj) if mask.bit_count() >= 2]
    clauses = [
        [-(vertex + 1) for vertex in range(graph.n) if (mask >> vertex) & 1]
        for mask in maximal
    ]
    clauses.extend(
        CardEnc.atleast(
            lits=list(range(1, graph.n + 1)),
            bound=target_size,
            top_id=graph.n,
            encoding=EncType.seqcounter,
        ).clauses
    )
    witnesses: list[tuple[int, ...]] = []
    calls = 0
    exhausted = False
    with Cadical195(bootstrap_with=clauses) as solver:
        while len(witnesses) < batch_limit:
            calls += 1
            result = solver.solve()
            if result is False:
                exhausted = True
                break
            if result is not True:
                raise RuntimeError(
                    f"admissibility solver returned indeterminate status {result!r}"
                )
            positive = {literal for literal in (solver.get_model() or []) if literal > 0}
            selected = tuple(
                v for v in range(graph.n) if v + 1 in positive
            )[:target_size]
            members = sum(1 << v for v in selected)
            if len(selected) != target_size or any(
                (mask & ~members) == 0 for mask in maximal
            ):
                raise AssertionError("admissibility oracle returned an invalid witness")
            witnesses.append(selected)
            solver.add_clause([-(v + 1) for v in selected])
    if not witnesses:
        return None
    return AdmissibilityBatch(tuple(witnesses), len(maximal), exhausted, calls)


def _item_hash(kind: str, payload: dict[str, object]) -> str:
    return sha256_bytes(
        b"erdos151-fixed-clique-cegar-v2-batch-item\0"
        + canonical_json_bytes({"kind": kind, "witness": payload})
    )


def make_batch_item(kind: str, payload: dict[str, object]) -> dict[str, object]:
    result = dict(payload)
    result["item_sha256"] = _item_hash(kind, payload)
    return result


def _verify_batch_item_hash(kind: str, item: dict[str, object]) -> None:
    body = dict(item)
    stored = body.pop("item_sha256", None)
    if stored != _item_hash(kind, body):
        raise ValueError("batch item hash does not reproduce")


def encode_admissibility_batch(
    edges: EdgeVariables,
    pool: IDPool,
    items: Sequence[dict[str, object]],
    tag: str,
) -> tuple[list[list[int]], list[dict[str, object]]]:
    clauses: list[list[int]] = []
    summaries: list[dict[str, object]] = []
    for index, item in enumerate(items):
        before = pool.top
        item_clauses = _v1.encode_admissibility_cut(
            edges,
            pool,
            [int(v) for v in item["vertices"]],
            f"{tag}:item:{index}",
        )
        summary = summarize_encoding(
            "admissibility", item_clauses, before, pool.top
        )
        summary["item_index"] = index
        summary["item_sha256"] = item["item_sha256"]
        summaries.append(summary)
        clauses.extend(item_clauses)
    return clauses, summaries


def _update_clause_digest(digest: object, clauses: Iterable[Sequence[int]]) -> int:
    count = 0
    for clause in clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
        count += 1
    return count


class OuterProblem(_V1OuterProblem):
    """Outer SAT instance with selectable eager/lazy forbidden cliques."""

    def __init__(self, config: CaseConfig, collect_clauses: bool = False):
        config.validate()
        self.config = config
        self.edges = EdgeVariables(config.n)
        self.pool = IDPool(start_from=self.edges.count + 1)
        base: list[list[int]] = []
        for u, v in itertools.combinations(range(config.fixed_clique_size), 2):
            base.append([self.edges.var(u, v)])
        for vertex in range(config.n):
            incident = [
                self.edges.var(vertex, other)
                for other in range(config.n)
                if other != vertex
            ]
            if config.degree_min:
                base.extend(
                    CardEnc.atleast(
                        lits=incident,
                        bound=config.degree_min,
                        vpool=self.pool,
                        encoding=EncType.seqcounter,
                    ).clauses
                )
            if config.degree_max < config.n - 1:
                base.extend(
                    CardEnc.atmost(
                        lits=incident,
                        bound=config.degree_max,
                        vpool=self.pool,
                        encoding=EncType.seqcounter,
                    ).clauses
                )

        digest = hashlib.sha256()
        static_clause_count = _update_clause_digest(digest, base)
        self.solver = Cadical195(bootstrap_with=base)
        self.collected_clauses = list(base) if collect_clauses else None
        eager_count = 0
        if config.forbidden_mode == "eager":
            chunk: list[list[int]] = []
            for vertices in itertools.combinations(
                range(config.n), config.forbidden_clique_size
            ):
                clause = [
                    -self.edges.var(u, v)
                    for u, v in itertools.combinations(vertices, 2)
                ]
                digest.update(" ".join(map(str, clause)).encode("ascii"))
                digest.update(b" 0\n")
                static_clause_count += 1
                eager_count += 1
                chunk.append(clause)
                if len(chunk) == 8192:
                    self.solver.append_formula(chunk)
                    if self.collected_clauses is not None:
                        self.collected_clauses.extend(chunk)
                    chunk = []
            if chunk:
                self.solver.append_formula(chunk)
                if self.collected_clauses is not None:
                    self.collected_clauses.extend(chunk)

        self.static_encoding = {
            "clause_count": static_clause_count,
            "edge_variable_count": self.edges.count,
            "auxiliary_variable_count": self.pool.top - self.edges.count,
            "last_variable": self.pool.top,
            "clause_sha256": digest.hexdigest(),
            "forbidden_mode": config.forbidden_mode,
            "eager_forbidden_clause_count": eager_count,
        }

    def build_cut(
        self, kind: str, witness: dict[str, object], sequence: int
    ) -> CutEncoding:
        before = self.pool.top
        tag = f"cut:{sequence}:{kind}"
        if kind == "forbidden_clique_batch":
            items = [dict(item) for item in witness["items"]]
            clauses: list[list[int]] = []
            item_summaries: list[dict[str, object]] = []
            for index, item in enumerate(items):
                vertices = tuple(int(v) for v in item["vertices"])
                item_clauses = [[
                    -self.edges.var(u, v)
                    for u, v in itertools.combinations(vertices, 2)
                ]]
                summary = summarize_encoding(
                    "forbidden_clique", item_clauses, self.pool.top, self.pool.top
                )
                summary["item_index"] = index
                summary["item_sha256"] = item["item_sha256"]
                item_summaries.append(summary)
                clauses.extend(item_clauses)
        elif kind == "admissibility_batch":
            items = [dict(item) for item in witness["items"]]
            clauses, item_summaries = encode_admissibility_batch(
                self.edges, self.pool, items, tag
            )
        else:
            return super().build_cut(kind, witness, sequence)
        summary = summarize_encoding(kind, clauses, before, self.pool.top)
        summary["logical_cut_count"] = len(items)
        summary["item_encodings"] = item_summaries
        return CutEncoding(clauses, summary)


def validate_cut_witness(
    config: CaseConfig, record: dict[str, object]
) -> GraphSnapshot:
    kind = str(record["kind"])
    if kind not in {"forbidden_clique_batch", "admissibility_batch"}:
        return _v1_validate_cut_witness(config, record)
    candidate = record.get("candidate")
    if not isinstance(candidate, dict):
        raise ValueError("cut record lacks candidate object")
    graph = GraphSnapshot.from_hex(config.n, str(candidate["edges_hex"]))
    if graph.graph_sha256 != candidate.get("graph_sha256"):
        raise ValueError("cut candidate graph hash mismatch")
    validate_static_candidate(config, graph)
    witness = record.get("witness")
    if not isinstance(witness, dict):
        raise ValueError("batch record lacks witness object")
    raw_items = witness.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("batch record must contain at least one item")
    items = [dict(item) for item in raw_items]
    if int(witness.get("logical_cut_count", -1)) != len(items):
        raise ValueError("batch logical cut count is wrong")
    adj = graph.adjacency()
    if kind == "forbidden_clique_batch":
        actual = enumerate_cliques_exact(adj, config.forbidden_clique_size)
        stored: list[tuple[int, ...]] = []
        for item in items:
            _verify_batch_item_hash("forbidden_clique", item)
            vertices = tuple(int(v) for v in item["vertices"])
            if (
                len(vertices) != config.forbidden_clique_size
                or tuple(sorted(vertices)) != vertices
                or any(v < 0 or v >= config.n for v in vertices)
                or not is_clique(vertices, adj)
            ):
                raise ValueError("invalid forbidden-clique batch item")
            stored.append(vertices)
        if stored != actual:
            raise ValueError("forbidden-clique batch is not the exact complete list")
    else:
        if find_clique(adj, config.forbidden_clique_size) is not None:
            raise ValueError(
                "admissibility batch was recorded before separating forbidden cliques"
            )
        maximal = [mask for mask in maximal_cliques_bk(adj) if mask.bit_count() >= 2]
        seen: set[tuple[int, ...]] = set()
        for item in items:
            _verify_batch_item_hash("admissibility", item)
            vertices = tuple(int(v) for v in item["vertices"])
            if (
                len(vertices) != config.target_set_size
                or tuple(sorted(vertices)) != vertices
                or len(set(vertices)) != len(vertices)
                or any(v < 0 or v >= config.n for v in vertices)
            ):
                raise ValueError("invalid admissibility batch item")
            members = sum(1 << v for v in vertices)
            if any((mask & ~members) == 0 for mask in maximal):
                raise ValueError("invalid admissibility batch item")
            if vertices in seen:
                raise ValueError("duplicate admissibility batch item")
            seen.add(vertices)
            if int(item.get("candidate_nontrivial_maximal_clique_count", -1)) != len(
                maximal
            ):
                raise ValueError("stored maximal-clique count is wrong")
        requested_limit = int(witness.get("requested_batch_limit", -1))
        if requested_limit != config.admissibility_batch_size or len(items) > requested_limit:
            raise ValueError("stored admissibility batch limit is wrong")
        exhausted = witness.get("enumeration_exhausted")
        if not isinstance(exhausted, bool):
            raise ValueError("stored enumeration_exhausted flag is not Boolean")
        expected_calls = len(items) + int(exhausted)
        if int(witness.get("oracle_solver_calls", -1)) != expected_calls:
            raise ValueError("stored admissibility oracle call count is wrong")
        if not exhausted and len(items) != requested_limit:
            raise ValueError("a non-exhausted batch must reach its requested limit")
        if exhausted:
            clauses = [
                [-(vertex + 1) for vertex in range(config.n) if (mask >> vertex) & 1]
                for mask in maximal
            ]
            clauses.extend(
                CardEnc.atleast(
                    lits=list(range(1, config.n + 1)),
                    bound=config.target_set_size,
                    top_id=config.n,
                    encoding=EncType.seqcounter,
                ).clauses
            )
            clauses.extend([[-(v + 1) for v in vertices] for vertices in seen])
            with Cadical195(bootstrap_with=clauses) as solver:
                if solver.solve() is not False:
                    raise ValueError("stored exhausted admissibility batch is incomplete")
    return graph


class SearchSession(_V1SearchSession):
    def __init__(self, *args: object, checkpoint_ready: bool = True, **kwargs: object):
        run_dir = Path(args[0] if args else kwargs["run_dir"]).resolve()
        was_new = not (run_dir / _v1.METADATA_NAME).exists()
        self._repair_terminal_progress = bool(kwargs.get("repair_journal", True))
        self._terminal_repair_allows_code_drift = bool(
            kwargs.get("allow_code_drift", False)
        )
        if not was_new:
            # Reject a wrong-engine run before the inherited writable constructor
            # has any opportunity to repair its journal tail.
            preflight = load_hashed_json(run_dir / _v1.METADATA_NAME)
            implementation = preflight.get("implementation")
            if (
                preflight.get("schema_version") != SCHEMA_VERSION
                or not isinstance(implementation, dict)
                or implementation.get("engine") != "fixed_clique_cegar_v2"
            ):
                raise ValueError("run metadata is not a fixed_clique_cegar_v2 run")
        super().__init__(*args, checkpoint_ready=False, **kwargs)
        if was_new:
            metadata = dict(self.metadata)
            metadata.pop("content_sha256", None)
            metadata["implementation"] = {
                "engine": "fixed_clique_cegar_v2",
                "schema": SCHEMA_VERSION,
                "upstream_commit": UPSTREAM_COMMIT,
                "upstream_source_pin": UPSTREAM_EXPECTED_SHA256,
                "journal_unit": "one candidate with a conjunctive batch of independently hashed cuts",
            }
            metadata["semantics"] = {
                "outer_variables": "one Boolean for every unordered vertex pair; true means present edge",
                "admissibility_cut": "each batch item is the exact existential projection asserting a nontrivial ambient-maximal clique inside that witnessed set",
                "arrowing_cut": "exact existential projection asserting a present monochromatic triangle under a fixed total coloring of all pairs",
                "forbidden_cliques": (
                    "all forbidden-clique clauses are static"
                    if self.config.forbidden_mode == "eager"
                    else "every forbidden clique in a violating candidate is journaled and added as one complete batch"
                ),
            }
            atomic_write_json(self.metadata_path, metadata)
            self.metadata = load_hashed_json(self.metadata_path)
        else:
            implementation = self.metadata.get("implementation")
            if not isinstance(implementation, dict) or implementation.get("engine") != "fixed_clique_cegar_v2":
                raise ValueError("run metadata is not a fixed_clique_cegar_v2 run")
            if implementation.get("upstream_source_pin") != UPSTREAM_EXPECTED_SHA256:
                raise ValueError("run metadata has a different upstream source pin")
        expected_source_keys = set(self.current_sources)
        for record in self.journal.records:
            source_map = record.get("implementation_source_sha256")
            if not isinstance(source_map, dict) or set(source_map) != expected_source_keys:
                raise ValueError("journal record has a malformed implementation source map")
            if any(
                not isinstance(value, str)
                or len(value) != 64
                or any(char not in "0123456789abcdef" for char in value)
                for value in source_map.values()
            ):
                raise ValueError("journal record has a malformed implementation source hash")
            if not self.allow_code_drift and source_map != self.current_sources:
                raise ValueError("journal record implementation source hashes are not current")
        if checkpoint_ready and self.result is None:
            self._checkpoint("READY")

    def _prefix_logical_cut_counts(self, count: int) -> dict[str, int]:
        result: Counter[str] = Counter()
        for record in self.journal.records[:count]:
            kind = str(record["kind"])
            if kind.endswith("_batch"):
                logical_kind = kind.removesuffix("_batch")
                result[logical_kind] += int(record["witness"]["logical_cut_count"])
            else:
                result[kind] += 1
        return dict(sorted(result.items()))

    def _logical_cut_counts(self) -> dict[str, int]:
        return self._prefix_logical_cut_counts(len(self.journal.records))

    def _validate_progress(self, progress: dict[str, object]) -> None:
        super()._validate_progress(progress)
        count = int(progress["committed_cut_count"])
        if progress.get("logical_cut_counts") != self._prefix_logical_cut_counts(count):
            raise ValueError("progress.json logical-cut counts do not match its journal prefix")

    def _validate_candidate_linkage(
        self,
        result: dict[str, object],
        progress: dict[str, object],
    ) -> dict[str, object]:
        candidate = super()._validate_candidate_linkage(result, progress)
        independent = candidate.get("independent_verification")
        if not isinstance(independent, dict):
            raise ValueError("candidate lacks independent-verifier provenance")
        run = candidate.get("run")
        if not isinstance(run, dict):
            raise ValueError("candidate lacks run linkage")
        source_map = run.get("implementation_source_sha256")
        if not isinstance(source_map, dict):
            raise ValueError("candidate run lacks implementation source hashes")
        if independent.get("script_sha256") != source_map.get("v2/verify_candidate.py"):
            raise ValueError("candidate independent-verifier hash does not match run sources")
        preset = load_cases().get(self.config.name)
        expected_preset = self.config.name if preset == self.config else None
        if independent.get("approved_preset") != expected_preset:
            raise ValueError("candidate independent-verifier preset binding is wrong")
        command = str(independent.get("command", ""))
        if expected_preset is not None and f"--approved-preset {expected_preset}" not in command:
            raise ValueError("candidate independent-verifier command omits its preset binding")
        return candidate

    def _validate_result(self, result: dict[str, object]) -> None:
        if result.get("logical_cut_counts") != self._logical_cut_counts():
            raise ValueError("result.json logical-cut counts do not match the journal")
        try:
            super()._validate_result(result)
            return
        except ValueError:
            status = str(result.get("status", ""))
            terminal = {
                "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION",
                "OUTER_UNSAT_NO_PROOF_CERTIFICATE",
            }
            progress_status = (
                None if self.progress is None else str(self.progress.get("status", ""))
            )
            can_repair = (
                self._repair_terminal_progress
                and not self._terminal_repair_allows_code_drift
                and self.run_lock is not None
                and status in terminal
                and progress_status not in terminal
            )
            if not can_repair:
                raise

        # A crash can occur after the atomically written terminal result but
        # before the matching progress checkpoint.  Treat result.json as the
        # commit record only after it passes the complete base validator against
        # a synthetic matching progress object, including candidate linkage.
        stale_progress = self.progress
        self.progress = dict(result)
        try:
            super()._validate_result(result)
        except BaseException:
            self.progress = stale_progress
            raise
        self.models_seen = int(result["outer_models_seen"])
        linkage = {
            key: result[key]
            for key in (
                "candidate_file",
                "candidate_file_sha256",
                "candidate_graph_sha256",
            )
            if key in result
        }
        self._checkpoint(status, **linkage)
        super()._validate_result(result)

    def _write_result(self, status: str, **extra: object) -> Path:
        extra.setdefault("logical_cut_counts", self._logical_cut_counts())
        return super()._write_result(status, **extra)

    def _checkpoint(self, status: str, **extra: object) -> None:
        extra.setdefault("logical_cut_counts", self._logical_cut_counts())
        super()._checkpoint(status, **extra)

    def run(self, max_iterations: int = 1, time_limit_seconds: float = 0.0) -> str:
        self._assert_writer()
        if (
            max_iterations < 0
            or not math.isfinite(time_limit_seconds)
            or time_limit_seconds < 0
        ):
            raise ValueError("limits must be finite and nonnegative")
        if self.result is not None:
            return str(self.result["status"])
        started = time.monotonic()
        processed = 0
        try:
            while max_iterations == 0 or processed < max_iterations:
                if time_limit_seconds and time.monotonic() - started >= time_limit_seconds:
                    break
                graph = self.problem.solve()
                if graph is None:
                    self._write_result(
                        "OUTER_UNSAT_NO_PROOF_CERTIFICATE",
                        logical_cut_counts=self._logical_cut_counts(),
                        warning=(
                            "Incremental CaDiCaL returned UNSAT, but this run did not "
                            "emit a proof. Export the rebuilt CNF and obtain/check a proof "
                            "before making an exhaustion claim."
                        ),
                    )
                    self._checkpoint("OUTER_UNSAT_NO_PROOF_CERTIFICATE")
                    if self.result is None:
                        raise AssertionError("outer-UNSAT result write did not persist")
                    self._validate_result(self.result)
                    return "OUTER_UNSAT_NO_PROOF_CERTIFICATE"

                processed += 1
                self.models_seen += 1
                validate_static_candidate(self.config, graph)
                adj = graph.adjacency()
                forbidden = enumerate_cliques_exact(
                    adj, self.config.forbidden_clique_size
                )
                if forbidden:
                    if self.config.forbidden_mode == "eager":
                        raise AssertionError(
                            "eager forbidden-clique CNF admitted a forbidden clique"
                        )
                    items = [
                        make_batch_item(
                            "forbidden_clique", {"vertices": list(vertices)}
                        )
                        for vertices in forbidden
                    ]
                    self._commit_cut(
                        "forbidden_clique_batch",
                        {"items": items, "logical_cut_count": len(items)},
                        graph,
                    )
                    continue

                admissible = admissibility_oracle_batch(
                    graph,
                    self.config.target_set_size,
                    self.config.admissibility_batch_size,
                )
                if admissible is not None:
                    items = [
                        make_batch_item(
                            "admissibility",
                            {
                                "vertices": list(vertices),
                                "candidate_nontrivial_maximal_clique_count": admissible.maximal_clique_count,
                            },
                        )
                        for vertices in admissible.vertex_sets
                    ]
                    self._commit_cut(
                        "admissibility_batch",
                        {
                            "items": items,
                            "logical_cut_count": len(items),
                            "requested_batch_limit": self.config.admissibility_batch_size,
                            "enumeration_exhausted": admissible.enumeration_exhausted,
                            "oracle_solver_calls": admissible.solver_calls,
                        },
                        graph,
                    )
                    continue

                coloring = coloring_oracle(graph)
                if coloring is not None:
                    self._commit_cut(
                        "arrowing",
                        {
                            "total_coloring_hex": pack_bits(coloring.total_colors),
                            "present_red_edge_count": coloring.present_red_edges,
                            "present_triangle_count": coloring.present_triangle_count,
                            "total_monochromatic_triple_count": coloring.total_monochromatic_triples,
                            "absent_pair_extension": "sha256(graph_sha256 || big_endian_pair_index), low bit",
                        },
                        graph,
                    )
                    continue

                candidate_path = self._dump_candidate(
                    graph,
                    {
                        "nontrivial_ambient_maximal_clique_count": sum(
                            mask.bit_count() >= 2 for mask in maximal_cliques_bk(adj)
                        ),
                        "target_set_size": self.config.target_set_size,
                    },
                    {
                        "present_edge_count": sum(graph.edge_bits),
                        "present_triangle_count": len(triangles(adj)),
                    },
                )
                print(f"candidate dumped: {candidate_path}")
                return "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION"
        except KeyboardInterrupt:
            self._checkpoint("PAUSED_BY_INTERRUPT")
            return "PAUSED_BY_INTERRUPT"

        self._checkpoint(
            "PAUSED_AT_LIMIT",
            invocation_models_processed=processed,
            invocation_elapsed_seconds=round(time.monotonic() - started, 3),
        )
        return "PAUSED_AT_LIMIT"

    def export_dimacs(self, path: Path) -> dict[str, object]:
        manifest = super().export_dimacs(path)
        manifest["scope"] = (
            "current exact static K_t-free outer CNF plus every committed cut"
            if self.config.forbidden_mode == "eager"
            else "current relaxation containing every committed complete candidate batch; unseen forbidden cliques remain lazy"
        )
        manifest["logical_cut_counts"] = self._logical_cut_counts()
        return manifest

    def audit_summary(self) -> dict[str, object]:
        summary = super().audit_summary()
        summary["logical_cut_counts"] = self._logical_cut_counts()
        summary["checked"].append(
            "every batch item hash, witness, per-item clause hash, and complete forbidden-clique list"
        )
        summary["checked"].append(
            "logical-cut totals in progress/result against their exact journal prefixes"
        )
        summary["checked"].append(
            "journal and candidate independent-verifier source provenance"
        )
        return summary


# The inherited persistence/CLI code resolves these names dynamically in its
# own module globals.  Patching only this private in-memory module preserves the
# on-disk upstream byte-for-byte while reusing its audited machinery.
_v1.SCHEMA_VERSION = SCHEMA_VERSION
_v1.HERE = HERE
_v1.CASES_PATH = CASES_PATH
_v1.CaseConfig = CaseConfig
_v1.load_cases = load_cases
_v1.collect_source_hashes = collect_source_hashes
_v1.OuterProblem = OuterProblem
_v1.validate_cut_witness = validate_cut_witness
_v1.SearchSession = SearchSession


def main(argv: Sequence[str] | None = None) -> int:
    return _v1.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
