#!/usr/bin/env python3
"""Resumable double-CEGAR search for the fixed-clique n=40/41 cases.

The outer SAT variables are exactly the possible graph edges.  Three kinds
of necessary constraints are separated lazily:

* a witnessed forbidden clique is blocked by its usual all-negative clause;
* an admissible target-size vertex set gets an exact projected CNF requiring
  an ambient-maximal nontrivial clique inside that set;
* a non-monochromatic-triangle edge coloring is extended to every pair, and
  gets an exact projected CNF requiring a present monochromatic triangle
  under that fixed total pair coloring.

Every cut is stored with the candidate that violated it in an append-only,
hash-chained journal.  Resumption rechecks the witness and regenerates the
cut before accepting its recorded clause hash.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import itertools
import json
import os
import platform
import sys
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

try:
    import pysat
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    from pysat.solvers import Cadical195
except ImportError as exc:  # pragma: no cover - exercised only on bad setups
    raise SystemExit(
        "python-sat is required; use the repository .venv or install "
        "requirements.txt"
    ) from exc


HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "cases.json"
SCHEMA_VERSION = 1
JOURNAL_NAME = "cuts.jsonl"
METADATA_NAME = "metadata.json"
PROGRESS_NAME = "progress.json"
LOCK_NAME = ".cegar-write.lock"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def with_content_hash(payload: dict[str, object]) -> dict[str, object]:
    result = dict(payload)
    result.pop("content_sha256", None)
    result["content_sha256"] = sha256_bytes(canonical_json_bytes(result))
    return result


def verify_content_hash(payload: dict[str, object], path: Path) -> None:
    expected = payload.get("content_sha256")
    assert isinstance(expected, str), f"missing content hash in {path}"
    body = dict(payload)
    del body["content_sha256"]
    actual = sha256_bytes(canonical_json_bytes(body))
    if actual != expected:
        raise ValueError(f"content hash mismatch in {path}: {actual} != {expected}")


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    final = with_content_hash(payload)
    raw = json.dumps(final, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def read_hashed_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    verify_content_hash(payload, path)
    return payload


class RunDirectoryLock:
    """Atomic, fail-fast exclusive writer lock for one run directory.

    O_CREAT|O_EXCL is the synchronization primitive.  A crashed process may
    leave a stale lock; it is preserved for inspection and must be removed
    only after the operator has established that its recorded process is dead.
    """

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir.resolve()
        self.path = self.run_dir / LOCK_NAME
        self.token = uuid.uuid4().hex
        self.active = False

    def __enter__(self) -> "RunDirectoryLock":
        self.run_dir.mkdir(parents=True, exist_ok=True)
        payload = with_content_hash(
            {
                "schema_version": SCHEMA_VERSION,
                "token": self.token,
                "pid": os.getpid(),
                "host": platform.node(),
                "created_utc": utc_now(),
                "run_dir": str(self.run_dir),
            }
        )
        raw = canonical_json_bytes(payload) + b"\n"
        try:
            descriptor = os.open(
                self.path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
        except FileExistsError as exc:
            try:
                owner = self.path.read_text(encoding="utf-8").strip()
            except OSError:
                owner = "<unreadable>"
            raise RuntimeError(
                f"run directory is locked by another writer: {self.path}; "
                f"owner={owner}"
            ) from exc
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
        except BaseException:
            self.path.unlink(missing_ok=True)
            raise
        self.active = True
        return self

    def assert_held_for(self, run_dir: Path) -> None:
        if not self.active or self.run_dir != run_dir.resolve():
            raise RuntimeError("an active exclusive lock for this run directory is required")
        try:
            payload = read_hashed_json(self.path)
        except (OSError, ValueError) as exc:
            raise RuntimeError("run-directory lock disappeared or is corrupt") from exc
        if payload.get("token") != self.token:
            raise RuntimeError("run-directory lock ownership changed")

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if not self.active:
            return
        self.assert_held_for(self.run_dir)
        self.path.unlink()
        self.active = False


def pack_bits(bits: Sequence[bool]) -> str:
    raw = bytearray((len(bits) + 7) // 8)
    for index, bit in enumerate(bits):
        if bit:
            raw[index >> 3] |= 1 << (index & 7)
    return raw.hex()


def unpack_bits(encoded: str, count: int) -> tuple[bool, ...]:
    raw = bytes.fromhex(encoded)
    expected = (count + 7) // 8
    if len(raw) != expected:
        raise ValueError(f"packed bit length {len(raw)} != expected {expected}")
    if count % 8 and raw and raw[-1] >> (count % 8):
        raise ValueError("nonzero unused packed bits")
    return tuple(bool(raw[i >> 3] & (1 << (i & 7))) for i in range(count))


def clause_stream_sha256(clauses: Iterable[Sequence[int]]) -> str:
    digest = hashlib.sha256()
    for clause in clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest()


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

    def validate(self) -> None:
        if not 2 <= self.fixed_clique_size <= self.n:
            raise ValueError("fixed clique size must lie in [2,n]")
        if not self.fixed_clique_size < self.forbidden_clique_size <= self.n + 1:
            raise ValueError("forbidden clique must be larger than the fixed clique")
        if not 0 <= self.degree_min <= self.degree_max < self.n:
            raise ValueError("invalid degree range")
        if not 2 <= self.target_set_size <= self.n:
            raise ValueError("invalid target set size")

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


class EdgeVariables:
    def __init__(self, n: int):
        self.n = n
        self.pairs = tuple(itertools.combinations(range(n), 2))
        self.index = {pair: i for i, pair in enumerate(self.pairs)}

    @property
    def count(self) -> int:
        return len(self.pairs)

    def var(self, u: int, v: int) -> int:
        if u == v:
            raise ValueError("loops have no edge variable")
        pair = (u, v) if u < v else (v, u)
        return self.index[pair] + 1


@dataclasses.dataclass(frozen=True)
class GraphSnapshot:
    n: int
    edge_bits: tuple[bool, ...]

    def __post_init__(self) -> None:
        expected = self.n * (self.n - 1) // 2
        if self.n < 0 or len(self.edge_bits) != expected:
            raise ValueError(
                f"graph snapshot has {len(self.edge_bits)} edge bits, expected {expected}"
            )

    @classmethod
    def from_hex(cls, n: int, encoded: str) -> "GraphSnapshot":
        count = n * (n - 1) // 2
        return cls(n=n, edge_bits=unpack_bits(encoded, count))

    @property
    def edges_hex(self) -> str:
        return pack_bits(self.edge_bits)

    @property
    def graph_sha256(self) -> str:
        domain = b"erdos151-fixed-clique-graph-v1\0"
        raw = bytes.fromhex(self.edges_hex)
        return sha256_bytes(domain + self.n.to_bytes(4, "big") + raw)

    def adjacency(self) -> tuple[int, ...]:
        adj = [0] * self.n
        for bit, (u, v) in zip(self.edge_bits, itertools.combinations(range(self.n), 2)):
            if bit:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
        return tuple(adj)

    def edge_list(self) -> list[list[int]]:
        return [
            [u, v]
            for bit, (u, v) in zip(
                self.edge_bits, itertools.combinations(range(self.n), 2)
            )
            if bit
        ]


def graph_from_solver_model(n: int, model: Sequence[int]) -> GraphSnapshot:
    positive = {literal for literal in model if literal > 0}
    count = n * (n - 1) // 2
    return GraphSnapshot(n, tuple(var in positive for var in range(1, count + 1)))


def triangles(adj: Sequence[int]) -> list[tuple[int, int, int]]:
    n = len(adj)
    found: list[tuple[int, int, int]] = []
    for u in range(n):
        higher_u = adj[u] & ~((1 << (u + 1)) - 1)
        scan = higher_u
        while scan:
            v_bit = scan & -scan
            scan ^= v_bit
            v = v_bit.bit_length() - 1
            common = adj[u] & adj[v] & ~((1 << (v + 1)) - 1)
            while common:
                w_bit = common & -common
                common ^= w_bit
                found.append((u, v, w_bit.bit_length() - 1))
    return found


def maximal_cliques_bk(adj: Sequence[int]) -> list[int]:
    """Enumerate every ambient inclusion-maximal clique as a bit mask."""

    n = len(adj)
    all_vertices = (1 << n) - 1
    result: list[int] = []

    def expand(chosen: int, possible: int, excluded: int) -> None:
        if not possible and not excluded:
            result.append(chosen)
            return
        union = possible | excluded
        if union:
            pivot = max(
                (i for i in range(n) if (union >> i) & 1),
                key=lambda vertex: (possible & adj[vertex]).bit_count(),
            )
            candidates = possible & ~adj[pivot] & all_vertices
        else:  # unreachable because the base case returned
            candidates = possible
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            vertex = bit.bit_length() - 1
            expand(
                chosen | bit,
                possible & adj[vertex],
                excluded & adj[vertex],
            )
            possible ^= bit
            excluded |= bit

    expand(0, all_vertices, 0)
    return sorted(result)


def find_clique(adj: Sequence[int], size: int) -> tuple[int, ...] | None:
    """Find one clique of the requested size with an exact bitset search."""

    n = len(adj)

    def search(chosen: tuple[int, ...], candidates: int) -> tuple[int, ...] | None:
        if len(chosen) == size:
            return chosen
        need = size - len(chosen)
        scan = candidates
        while scan:
            if scan.bit_count() < need:
                return None
            bit = scan & -scan
            scan ^= bit
            vertex = bit.bit_length() - 1
            found = search(chosen + (vertex,), scan & adj[vertex])
            if found is not None:
                return found
        return None

    return search((), (1 << n) - 1)


def is_clique(vertices: Sequence[int], adj: Sequence[int]) -> bool:
    return all((adj[u] >> v) & 1 for u, v in itertools.combinations(vertices, 2))


def is_ambient_maximal_clique(vertices: Sequence[int], adj: Sequence[int]) -> bool:
    if len(vertices) < 2 or not is_clique(vertices, adj):
        return False
    common = (1 << len(adj)) - 1
    members = 0
    for vertex in vertices:
        members |= 1 << vertex
        common &= adj[vertex]
    return not (common & ~members)


def set_is_admissible(vertices: Sequence[int], adj: Sequence[int]) -> bool:
    members = sum(1 << v for v in vertices)
    return not any(
        clique.bit_count() >= 2 and not (clique & ~members)
        for clique in maximal_cliques_bk(adj)
    )


@dataclasses.dataclass
class CutEncoding:
    clauses: list[list[int]]
    summary: dict[str, object]


def summarize_encoding(
    kind: str, clauses: list[list[int]], pool_before: int, pool_after: int
) -> dict[str, object]:
    return {
        "kind": kind,
        "clause_count": len(clauses),
        "auxiliary_variable_count": pool_after - pool_before,
        "first_auxiliary_variable": pool_before + 1 if pool_after > pool_before else None,
        "last_variable": pool_after,
        "clause_sha256": clause_stream_sha256(clauses),
    }


def encode_admissibility_cut(
    edges: EdgeVariables,
    pool: IDPool,
    vertices: Sequence[int],
    tag: str,
) -> list[list[int]]:
    """Exact projection: S contains a nontrivial ambient-maximal clique.

    Selector z_v chooses the clique K.  Pair clauses make K a clique.  For
    every w outside K, one d_(w,v) must certify a selected v nonadjacent to
    w.  Only the sound direction of each d definition is needed because d is
    existentially quantified.  Conversely an actual maximal K supplies all
    d witnesses, proving exactness after projection to the edge variables.
    """

    selected_vertices = tuple(sorted(set(int(v) for v in vertices)))
    if len(selected_vertices) < 2:
        raise ValueError("an admissibility cut needs at least two vertices")
    if any(v < 0 or v >= edges.n for v in selected_vertices):
        raise ValueError("admissibility-cut vertex out of range")

    z = {v: pool.id(f"{tag}:z:{v}") for v in selected_vertices}
    clauses: list[list[int]] = []

    # At least two selectors, without another cardinality encoding.
    clauses.append(list(z.values()))
    for v in selected_vertices:
        clauses.append([-z[v]] + [z[u] for u in selected_vertices if u != v])

    # Selected vertices form a clique.
    for u, v in itertools.combinations(selected_vertices, 2):
        clauses.append([-z[u], -z[v], edges.var(u, v)])

    # Every nonmember has a certified nonneighbor in the selected clique.
    selected_set = set(selected_vertices)
    for w in range(edges.n):
        disjunction = [z[w]] if w in selected_set else []
        for v in selected_vertices:
            if v == w:
                continue
            d_var = pool.id(f"{tag}:d:{w}:{v}")
            clauses.append([-d_var, z[v]])
            clauses.append([-d_var, -edges.var(w, v)])
            disjunction.append(d_var)
        clauses.append(disjunction)
    return clauses


def encode_arrowing_cut(
    edges: EdgeVariables,
    pool: IDPool,
    total_colors: Sequence[bool],
    tag: str,
) -> list[list[int]]:
    """Exact projection: a graph has a mono triangle in a fixed pair-coloring."""

    if len(total_colors) != edges.count:
        raise ValueError("wrong total-coloring length")
    z = [pool.id(f"{tag}:z:{v}") for v in range(edges.n)]
    mono_color = pool.id(f"{tag}:mono_color")  # true means red
    clauses = CardEnc.equals(
        lits=z, bound=3, vpool=pool, encoding=EncType.seqcounter
    ).clauses
    for index, (u, v) in enumerate(edges.pairs):
        clauses.append([-z[u], -z[v], edges.var(u, v)])
        color_literal = mono_color if total_colors[index] else -mono_color
        clauses.append([-z[u], -z[v], color_literal])
    return clauses


class OuterProblem:
    def __init__(self, config: CaseConfig, collect_clauses: bool = False):
        config.validate()
        self.config = config
        self.edges = EdgeVariables(config.n)
        self.pool = IDPool(start_from=self.edges.count + 1)
        clauses: list[list[int]] = []

        for u, v in itertools.combinations(range(config.fixed_clique_size), 2):
            clauses.append([self.edges.var(u, v)])
        for vertex in range(config.n):
            incident = [
                self.edges.var(vertex, other)
                for other in range(config.n)
                if other != vertex
            ]
            if config.degree_min:
                clauses.extend(
                    CardEnc.atleast(
                        lits=incident,
                        bound=config.degree_min,
                        vpool=self.pool,
                        encoding=EncType.seqcounter,
                    ).clauses
                )
            if config.degree_max < config.n - 1:
                clauses.extend(
                    CardEnc.atmost(
                        lits=incident,
                        bound=config.degree_max,
                        vpool=self.pool,
                        encoding=EncType.seqcounter,
                    ).clauses
                )

        self.static_encoding = {
            "clause_count": len(clauses),
            "edge_variable_count": self.edges.count,
            "auxiliary_variable_count": self.pool.top - self.edges.count,
            "last_variable": self.pool.top,
            "clause_sha256": clause_stream_sha256(clauses),
        }
        self.solver = Cadical195(bootstrap_with=clauses)
        self.collected_clauses = list(clauses) if collect_clauses else None

    def solve(self) -> GraphSnapshot | None:
        result = self.solver.solve()
        if result is False:
            return None
        if result is not True:
            raise RuntimeError(f"outer solver returned indeterminate status {result!r}")
        return graph_from_solver_model(self.config.n, self.solver.get_model() or [])

    def build_cut(
        self, kind: str, witness: dict[str, object], sequence: int
    ) -> CutEncoding:
        before = self.pool.top
        tag = f"cut:{sequence}:{kind}"
        if kind == "forbidden_clique":
            vertices = tuple(int(v) for v in witness["vertices"])
            clauses = [
                [-self.edges.var(u, v) for u, v in itertools.combinations(vertices, 2)]
            ]
        elif kind == "admissibility":
            clauses = encode_admissibility_cut(
                self.edges,
                self.pool,
                [int(v) for v in witness["vertices"]],
                tag,
            )
        elif kind == "arrowing":
            colors = unpack_bits(str(witness["total_coloring_hex"]), self.edges.count)
            clauses = encode_arrowing_cut(self.edges, self.pool, colors, tag)
        else:
            raise ValueError(f"unknown cut kind {kind!r}")
        summary = summarize_encoding(kind, clauses, before, self.pool.top)
        return CutEncoding(clauses, summary)

    def add_encoding(self, encoding: CutEncoding) -> None:
        self.solver.append_formula(encoding.clauses)
        if self.collected_clauses is not None:
            self.collected_clauses.extend(encoding.clauses)

    def close(self) -> None:
        self.solver.delete()


@dataclasses.dataclass(frozen=True)
class AdmissibilityWitness:
    vertices: tuple[int, ...]
    maximal_clique_count: int


def admissibility_oracle(
    graph: GraphSnapshot, target_size: int
) -> AdmissibilityWitness | None:
    """Find exactly target_size vertices containing no ambient maximal clique."""

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
    with Cadical195(bootstrap_with=clauses) as solver:
        result = solver.solve()
        if result is False:
            return None
        if result is not True:
            raise RuntimeError(f"admissibility solver returned {result!r}")
        positive = {literal for literal in (solver.get_model() or []) if literal > 0}
    selected = tuple(v for v in range(graph.n) if v + 1 in positive)[:target_size]
    members = sum(1 << v for v in selected)
    if len(selected) != target_size or any((mask & ~members) == 0 for mask in maximal):
        raise AssertionError("admissibility oracle returned an invalid witness")
    return AdmissibilityWitness(selected, len(maximal))


@dataclasses.dataclass(frozen=True)
class ColoringWitness:
    total_colors: tuple[bool, ...]
    present_red_edges: int
    present_triangle_count: int
    total_monochromatic_triples: int


def _extension_color(graph_hash: str, pair_index: int) -> bool:
    raw = bytes.fromhex(graph_hash) + pair_index.to_bytes(4, "big")
    return bool(hashlib.sha256(raw).digest()[0] & 1)


def coloring_oracle(graph: GraphSnapshot) -> ColoringWitness | None:
    """Find a total red/blue coloring of all present edges with no mono triangle."""

    edges = EdgeVariables(graph.n)
    present_pairs = [pair for bit, pair in zip(graph.edge_bits, edges.pairs) if bit]
    color_var = {pair: index + 1 for index, pair in enumerate(present_pairs)}
    adj = graph.adjacency()
    graph_triangles = triangles(adj)
    clauses: list[list[int]] = []
    for a, b, c in graph_triangles:
        literals = [
            color_var[(a, b)],
            color_var[(a, c)],
            color_var[(b, c)],
        ]
        clauses.append([-literal for literal in literals])  # not all red
        clauses.append(literals)  # not all blue
    with Cadical195(bootstrap_with=clauses) as solver:
        result = solver.solve()
        if result is False:
            return None
        if result is not True:
            raise RuntimeError(f"coloring solver returned {result!r}")
        positive = {literal for literal in (solver.get_model() or []) if literal > 0}

    total = [False] * edges.count
    for index, pair in enumerate(edges.pairs):
        if graph.edge_bits[index]:
            total[index] = color_var[pair] in positive
        else:
            total[index] = _extension_color(graph.graph_sha256, index)

    for a, b, c in graph_triangles:
        colors = [
            total[edges.index[(a, b)]],
            total[edges.index[(a, c)]],
            total[edges.index[(b, c)]],
        ]
        if colors[0] == colors[1] == colors[2]:
            raise AssertionError("coloring oracle returned a monochromatic present triangle")

    mono_total = 0
    for a, b, c in itertools.combinations(range(graph.n), 3):
        colors = (
            total[edges.index[(a, b)]],
            total[edges.index[(a, c)]],
            total[edges.index[(b, c)]],
        )
        mono_total += colors[0] == colors[1] == colors[2]
    return ColoringWitness(
        tuple(total),
        sum(
            graph.edge_bits[index] and total[index]
            for index in range(edges.count)
        ),
        len(graph_triangles),
        mono_total,
    )


def collect_source_hashes() -> dict[str, str]:
    names = ["cegar.py", "verify_candidate.py", "cases.json", "requirements.txt"]
    return {name: file_sha256(HERE / name) for name in names if (HERE / name).exists()}


class CutJournal:
    def __init__(self, path: Path):
        self.path = path
        self.records: list[dict[str, object]] = []
        self.head = "0" * 64
        self._file_digest = hashlib.sha256()
        self._record_end_offsets: list[int] = []

    @staticmethod
    def _record_hash(record_without_hash: dict[str, object]) -> str:
        return sha256_bytes(canonical_json_bytes(record_without_hash))

    def load(self, repair_trailing_fragment: bool = True) -> list[dict[str, object]]:
        if not self.path.exists():
            self.records = []
            self.head = "0" * 64
            self._file_digest = hashlib.sha256()
            self._record_end_offsets = []
            return []
        raw = self.path.read_bytes()
        offset = 0
        valid_end = 0
        records: list[dict[str, object]] = []
        previous = "0" * 64
        lines = raw.splitlines(keepends=True)
        for index, line in enumerate(lines):
            stripped = line.strip()
            line_start = offset
            offset += len(line)
            if not stripped:
                valid_end = offset
                continue
            try:
                record = json.loads(stripped.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                if index != len(lines) - 1 or not repair_trailing_fragment:
                    raise ValueError(f"invalid journal line {index + 1}") from exc
                valid_end = line_start
                break
            if not isinstance(record, dict):
                raise ValueError(f"journal line {index + 1} is not an object")
            stored = record.get("record_sha256")
            body = dict(record)
            body.pop("record_sha256", None)
            actual = self._record_hash(body)
            if stored != actual:
                raise ValueError(f"journal record hash mismatch at line {index + 1}")
            if int(record.get("sequence", -1)) != len(records):
                raise ValueError(f"noncontiguous journal sequence at line {index + 1}")
            if record.get("previous_record_sha256") != previous:
                raise ValueError(f"journal chain mismatch at line {index + 1}")
            previous = str(stored)
            records.append(record)
            valid_end = offset

        needs_newline = bool(raw[:valid_end]) and not raw[:valid_end].endswith(b"\n")
        has_tail = valid_end < len(raw)
        if has_tail:
            if not repair_trailing_fragment:
                raise ValueError("journal has a trailing fragment")
            stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            backup = self.path.with_name(f"{self.path.name}.recovered-tail-{stamp}.bin")
            backup.write_bytes(raw[valid_end:])
            repaired = raw[:valid_end]
            if repaired and not repaired.endswith(b"\n"):
                repaired += b"\n"
            temp = self.path.with_name(f".{self.path.name}.repair-{os.getpid()}")
            temp.write_bytes(repaired)
            os.replace(temp, self.path)
        elif needs_newline:
            with self.path.open("ab") as handle:
                handle.write(b"\n")
                handle.flush()
                os.fsync(handle.fileno())

        self.records = records
        self.head = previous
        self._file_digest = hashlib.sha256()
        normalized_raw = self.path.read_bytes()
        self._file_digest.update(normalized_raw)
        self._record_end_offsets = []
        normalized_offset = 0
        for line in normalized_raw.splitlines(keepends=True):
            normalized_offset += len(line)
            if line.strip():
                self._record_end_offsets.append(normalized_offset)
        if len(self._record_end_offsets) != len(records):
            raise AssertionError("journal offset reconstruction failed")
        return list(records)

    def append(self, body: dict[str, object]) -> dict[str, object]:
        record = dict(body)
        record["sequence"] = len(self.records)
        record["previous_record_sha256"] = self.head
        record["created_utc"] = utc_now()
        record["record_sha256"] = self._record_hash(record)
        raw = canonical_json_bytes(record) + b"\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("ab") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        self.records.append(record)
        self.head = str(record["record_sha256"])
        self._file_digest.update(raw)
        self._record_end_offsets.append(self.path.stat().st_size)
        return record

    def file_sha256(self) -> str:
        return self._file_digest.copy().hexdigest()

    def prefix_file_sha256(self, record_count: int) -> str:
        if not 0 <= record_count <= len(self.records):
            raise ValueError("journal prefix record count is out of range")
        if record_count == len(self.records):
            return self.file_sha256()
        if record_count == 0:
            return sha256_bytes(b"")
        end = self._record_end_offsets[record_count - 1]
        return sha256_bytes(self.path.read_bytes()[:end])

    def prefix_head_sha256(self, record_count: int) -> str:
        if not 0 <= record_count <= len(self.records):
            raise ValueError("journal prefix record count is out of range")
        return "0" * 64 if record_count == 0 else str(
            self.records[record_count - 1]["record_sha256"]
        )


def validate_static_candidate(config: CaseConfig, graph: GraphSnapshot) -> None:
    if graph.n != config.n:
        raise ValueError("candidate order mismatch")
    adj = graph.adjacency()
    degrees = [mask.bit_count() for mask in adj]
    if not all(config.degree_min <= degree <= config.degree_max for degree in degrees):
        raise ValueError("candidate violates the static degree interval")
    fixed = tuple(range(config.fixed_clique_size))
    if not is_clique(fixed, adj):
        raise ValueError("candidate does not contain the fixed clique")


def validate_cut_witness(
    config: CaseConfig, record: dict[str, object]
) -> GraphSnapshot:
    candidate = record.get("candidate")
    if not isinstance(candidate, dict):
        raise ValueError("cut record lacks candidate object")
    graph = GraphSnapshot.from_hex(config.n, str(candidate["edges_hex"]))
    if graph.graph_sha256 != candidate.get("graph_sha256"):
        raise ValueError("cut candidate graph hash mismatch")
    validate_static_candidate(config, graph)
    adj = graph.adjacency()
    kind = str(record["kind"])
    witness = record.get("witness")
    if not isinstance(witness, dict):
        raise ValueError("cut record lacks witness object")
    if kind == "forbidden_clique":
        vertices = tuple(int(v) for v in witness["vertices"])
        if (
            len(vertices) != config.forbidden_clique_size
            or len(set(vertices)) != len(vertices)
            or any(v < 0 or v >= config.n for v in vertices)
            or not is_clique(vertices, adj)
        ):
            raise ValueError("invalid forbidden-clique witness")
    elif kind == "admissibility":
        if find_clique(adj, config.forbidden_clique_size) is not None:
            raise ValueError("admissibility cut was recorded before separating a forbidden clique")
        vertices = tuple(int(v) for v in witness["vertices"])
        if (
            len(vertices) != config.target_set_size
            or len(set(vertices)) != len(vertices)
            or any(v < 0 or v >= config.n for v in vertices)
        ):
            raise ValueError("invalid admissibility witness size")
        if not set_is_admissible(vertices, adj):
            raise ValueError("stored set is not admissible in its candidate")
        if "candidate_nontrivial_maximal_clique_count" in witness:
            actual_count = sum(
                mask.bit_count() >= 2 for mask in maximal_cliques_bk(adj)
            )
            if actual_count != int(witness["candidate_nontrivial_maximal_clique_count"]):
                raise ValueError("stored maximal-clique count is wrong")
    elif kind == "arrowing":
        if find_clique(adj, config.forbidden_clique_size) is not None:
            raise ValueError("arrowing cut was recorded before separating a forbidden clique")
        colors = unpack_bits(str(witness["total_coloring_hex"]), len(graph.edge_bits))
        edges = EdgeVariables(config.n)
        graph_triangles = triangles(adj)
        for a, b, c in graph_triangles:
            triple = (
                colors[edges.index[(a, b)]],
                colors[edges.index[(a, c)]],
                colors[edges.index[(b, c)]],
            )
            if triple[0] == triple[1] == triple[2]:
                raise ValueError("stored coloring has a monochromatic present triangle")
        for index, present in enumerate(graph.edge_bits):
            if not present and colors[index] != _extension_color(graph.graph_sha256, index):
                raise ValueError("stored absent-pair color does not match its declared extension")
        present_red = sum(
            graph.edge_bits[index] and colors[index]
            for index in range(len(graph.edge_bits))
        )
        if present_red != int(witness.get("present_red_edge_count", present_red)):
            raise ValueError("stored red-edge count is wrong")
        if len(graph_triangles) != int(
            witness.get("present_triangle_count", len(graph_triangles))
        ):
            raise ValueError("stored triangle count is wrong")
        mono_total = 0
        for a, b, c in itertools.combinations(range(config.n), 3):
            triple = (
                colors[edges.index[(a, b)]],
                colors[edges.index[(a, c)]],
                colors[edges.index[(b, c)]],
            )
            mono_total += triple[0] == triple[1] == triple[2]
        if mono_total != int(
            witness.get("total_monochromatic_triple_count", mono_total)
        ):
            raise ValueError("stored total monochromatic-triple count is wrong")
    else:
        raise ValueError(f"unknown cut kind {kind!r}")
    return graph


class SearchSession:
    def __init__(
        self,
        run_dir: Path,
        config: CaseConfig,
        *,
        allow_code_drift: bool = False,
        collect_clauses: bool = False,
        validate_records: bool = True,
        repair_journal: bool = True,
        checkpoint_ready: bool = True,
        run_lock: RunDirectoryLock | None = None,
    ):
        self.run_dir = run_dir.resolve()
        self.run_lock = run_lock
        mutating = repair_journal or checkpoint_ready or not (
            self.run_dir / METADATA_NAME
        ).exists()
        if mutating:
            if run_lock is None:
                raise RuntimeError("a run-directory lock is required for a writable session")
            run_lock.assert_held_for(self.run_dir)
        elif not self.run_dir.is_dir():
            raise ValueError(f"run directory does not exist: {self.run_dir}")
        self.config = config
        self.allow_code_drift = allow_code_drift
        self.problem = OuterProblem(config, collect_clauses=collect_clauses)
        self.metadata_path = self.run_dir / METADATA_NAME
        self.progress_path = self.run_dir / PROGRESS_NAME
        self.journal = CutJournal(self.run_dir / JOURNAL_NAME)
        current_sources = collect_source_hashes()
        self.current_sources = current_sources

        if self.metadata_path.exists():
            metadata = read_hashed_json(self.metadata_path)
            recorded_config = CaseConfig.from_dict(dict(metadata["config"]))
            if recorded_config != config:
                raise ValueError("run metadata case configuration does not match")
            if metadata.get("static_encoding") != self.problem.static_encoding:
                raise ValueError("static CNF encoding hash does not reproduce")
            if not allow_code_drift and metadata.get("source_sha256") != current_sources:
                raise ValueError(
                    "implementation source hashes changed; audit the change and pass "
                    "--allow-code-drift only if intentional"
                )
            self.metadata = metadata
        else:
            if (self.run_dir / JOURNAL_NAME).exists():
                raise ValueError("refusing a cut journal without metadata")
            self.metadata = {
                "schema_version": SCHEMA_VERSION,
                "run_id": str(uuid.uuid4()),
                "created_utc": utc_now(),
                "config": config.as_dict(),
                "static_encoding": self.problem.static_encoding,
                "source_sha256": current_sources,
                "runtime": {
                    "python": sys.version,
                    "platform": platform.platform(),
                    "pysat": getattr(pysat, "__version__", "unknown"),
                    "outer_solver": "Cadical195",
                },
                "semantics": {
                    "outer_variables": "one Boolean for every unordered vertex pair; true means present edge",
                    "admissibility_cut": "exact existential projection asserting a nontrivial ambient-maximal clique inside the witnessed set",
                    "arrowing_cut": "exact existential projection asserting a present monochromatic triangle under a fixed total coloring of all pairs",
                    "forbidden_cliques": "separated lazily by witnessed all-negative clique clauses",
                },
            }
            atomic_write_json(self.metadata_path, self.metadata)
            self.metadata = read_hashed_json(self.metadata_path)

        if self.metadata.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("run metadata has an unsupported schema")

        records = self.journal.load(repair_trailing_fragment=repair_journal)
        for record in records:
            if record.get("schema_version") != SCHEMA_VERSION:
                raise ValueError("cut record has an unsupported schema")
            if record.get("run_id") != self.metadata["run_id"]:
                raise ValueError("cut record belongs to a different run")
            if not isinstance(record.get("implementation_source_sha256"), dict):
                raise ValueError("cut record lacks implementation source provenance")
            if validate_records:
                validate_cut_witness(config, record)
            sequence = int(record["sequence"])
            encoding = self.problem.build_cut(
                str(record["kind"]), dict(record["witness"]), sequence
            )
            if encoding.summary != record.get("encoding"):
                raise ValueError(f"cut encoding does not reproduce at sequence {sequence}")
            self.problem.add_encoding(encoding)

        self.models_seen = len(records)
        self.progress: dict[str, object] | None = None
        if self.progress_path.exists():
            progress = read_hashed_json(self.progress_path)
            self._validate_progress(progress)
            self.progress = progress
            self.models_seen = max(self.models_seen, int(progress.get("outer_models_seen", 0)))
        result_path = self.run_dir / "result.json"
        self.result: dict[str, object] | None = None
        if result_path.exists():
            result = read_hashed_json(result_path)
            self._validate_result(result)
            self.result = result
        elif self.progress is not None and self.progress.get("status") in {
            "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION",
            "OUTER_UNSAT_NO_PROOF_CERTIFICATE",
        }:
            raise ValueError("terminal progress exists without its required result.json")
        if checkpoint_ready and self.result is None:
            self._checkpoint("READY")

    @classmethod
    def from_existing(
        cls,
        run_dir: Path,
        *,
        allow_code_drift: bool = False,
        collect_clauses: bool = False,
        validate_records: bool = True,
        repair_journal: bool = False,
        checkpoint_ready: bool = False,
        run_lock: RunDirectoryLock | None = None,
    ) -> "SearchSession":
        metadata = read_hashed_json(run_dir.resolve() / METADATA_NAME)
        config = CaseConfig.from_dict(dict(metadata["config"]))
        return cls(
            run_dir,
            config,
            allow_code_drift=allow_code_drift,
            collect_clauses=collect_clauses,
            validate_records=validate_records,
            repair_journal=repair_journal,
            checkpoint_ready=checkpoint_ready,
            run_lock=run_lock,
        )

    def _assert_writer(self) -> None:
        if self.run_lock is None:
            raise RuntimeError("this operation requires an exclusive run-directory lock")
        self.run_lock.assert_held_for(self.run_dir)

    def _prefix_cut_counts(self, count: int) -> dict[str, int]:
        return dict(
            sorted(Counter(str(r["kind"]) for r in self.journal.records[:count]).items())
        )

    def _validate_bound_artifact(
        self,
        payload: dict[str, object],
        label: str,
        *,
        allow_journal_prefix: bool,
    ) -> int:
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise ValueError(f"{label} has an unsupported schema")
        if payload.get("run_id") != self.metadata["run_id"]:
            raise ValueError(f"{label} run_id does not match metadata")
        if payload.get("config") != self.config.as_dict():
            raise ValueError(f"{label} config does not match metadata")
        if payload.get("metadata_content_sha256") != self.metadata["content_sha256"]:
            raise ValueError(f"{label} is not bound to the current metadata hash")
        if payload.get("static_encoding") != self.metadata["static_encoding"]:
            raise ValueError(f"{label} static encoding does not match metadata")
        if (
            payload.get("initial_implementation_source_sha256")
            != self.metadata["source_sha256"]
        ):
            raise ValueError(f"{label} initial source hashes do not match metadata")
        implementation = payload.get("implementation_source_sha256")
        if not isinstance(implementation, dict):
            raise ValueError(f"{label} lacks implementation source hashes")
        if not self.allow_code_drift and implementation != self.current_sources:
            raise ValueError(f"{label} implementation source hashes are not current")

        cut_count = int(payload.get("committed_cut_count", -1))
        if allow_journal_prefix:
            if not 0 <= cut_count <= len(self.journal.records):
                raise ValueError(f"{label} cut count is not a journal prefix")
        elif cut_count != len(self.journal.records):
            raise ValueError(f"{label} cut count does not match the journal")
        if payload.get("cut_counts") != self._prefix_cut_counts(cut_count):
            raise ValueError(f"{label} cut-kind counts do not match its journal prefix")
        if payload.get("journal_head_sha256") != self.journal.prefix_head_sha256(cut_count):
            raise ValueError(f"{label} journal head does not match")
        if payload.get("journal_file_sha256") != self.journal.prefix_file_sha256(cut_count):
            raise ValueError(f"{label} journal file hash does not match")
        models_seen = int(payload.get("outer_models_seen", -1))
        if not cut_count <= models_seen <= cut_count + 1:
            raise ValueError(f"{label} outer model count is inconsistent with its cuts")
        return cut_count

    def _validate_progress(self, progress: dict[str, object]) -> None:
        self._validate_bound_artifact(
            progress, "progress.json", allow_journal_prefix=True
        )

    def _validate_candidate_linkage(
        self,
        result: dict[str, object],
        progress: dict[str, object],
    ) -> dict[str, object]:
        raw_name = str(result.get("candidate_file", ""))
        if not raw_name or Path(raw_name).name != raw_name:
            raise ValueError("result candidate filename is missing or unsafe")
        candidate_path = self.run_dir / raw_name
        if not candidate_path.is_file():
            raise ValueError("result candidate file does not exist")
        if result.get("candidate_file_sha256") != file_sha256(candidate_path):
            raise ValueError("result candidate file hash does not match")
        candidate = read_hashed_json(candidate_path)
        if candidate.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("candidate has an unsupported schema")
        if candidate.get("artifact_type") != "fixed_clique_cegar_candidate":
            raise ValueError("candidate has the wrong artifact type")
        if candidate.get("config") != self.config.as_dict():
            raise ValueError("candidate config does not match metadata")
        run = candidate.get("run")
        if not isinstance(run, dict):
            raise ValueError("candidate lacks run linkage")
        expected_run_fields = {
            "run_id": self.metadata["run_id"],
            "metadata_content_sha256": self.metadata["content_sha256"],
            "static_encoding": self.metadata["static_encoding"],
            "initial_implementation_source_sha256": self.metadata["source_sha256"],
            "journal_head_sha256": self.journal.head,
            "journal_file_sha256": self.journal.file_sha256(),
        }
        for key, expected in expected_run_fields.items():
            if run.get(key) != expected:
                raise ValueError(f"candidate run linkage mismatch: {key}")
        if run.get("implementation_source_sha256") != result.get(
            "implementation_source_sha256"
        ):
            raise ValueError("candidate/result implementation source hashes differ")
        if int(run.get("outer_models_seen", -1)) != int(
            result.get("outer_models_seen", -2)
        ):
            raise ValueError("candidate/result outer model counts differ")

        graph = candidate.get("graph")
        if not isinstance(graph, dict):
            raise ValueError("candidate lacks graph object")
        if int(graph.get("n", -1)) != self.config.n:
            raise ValueError("candidate graph.n does not match metadata config.n")
        snapshot = GraphSnapshot.from_hex(self.config.n, str(graph["edges_hex"]))
        if snapshot.graph_sha256 != graph.get("graph_sha256"):
            raise ValueError("candidate graph hash does not reproduce")
        if result.get("candidate_graph_sha256") != snapshot.graph_sha256:
            raise ValueError("result candidate graph hash does not match candidate")
        for key in (
            "candidate_file",
            "candidate_file_sha256",
            "candidate_graph_sha256",
        ):
            if progress.get(key) != result.get(key):
                raise ValueError(f"progress/result candidate linkage differs: {key}")
        return candidate

    def _validate_result(self, result: dict[str, object]) -> None:
        self._validate_bound_artifact(result, "result.json", allow_journal_prefix=False)
        status = str(result.get("status", ""))
        terminal = {
            "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION",
            "OUTER_UNSAT_NO_PROOF_CERTIFICATE",
        }
        if status not in terminal:
            raise ValueError(f"result.json has nonterminal or unknown status {status!r}")
        if self.progress is None:
            raise ValueError("result.json exists without progress.json")
        progress = self.progress
        if progress.get("status") != status:
            raise ValueError("progress/result terminal statuses differ")
        for key in (
            "run_id",
            "config",
            "metadata_content_sha256",
            "static_encoding",
            "initial_implementation_source_sha256",
            "implementation_source_sha256",
            "outer_models_seen",
            "committed_cut_count",
            "cut_counts",
            "journal_head_sha256",
            "journal_file_sha256",
        ):
            if progress.get(key) != result.get(key):
                raise ValueError(f"progress/result linkage differs: {key}")
        if status == "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION":
            if int(result["outer_models_seen"]) != len(self.journal.records) + 1:
                raise ValueError("candidate result has an inconsistent outer model count")
            self._validate_candidate_linkage(result, progress)
        else:
            if int(result["outer_models_seen"]) != len(self.journal.records):
                raise ValueError("outer-UNSAT result has an inconsistent outer model count")
            if any(
                key in result
                for key in (
                    "candidate_file",
                    "candidate_file_sha256",
                    "candidate_graph_sha256",
                )
            ):
                raise ValueError("outer-UNSAT result unexpectedly links a candidate")

    def _cut_counts(self) -> dict[str, int]:
        return dict(sorted(Counter(str(r["kind"]) for r in self.journal.records).items()))

    def _checkpoint(self, status: str, **extra: object) -> None:
        self._assert_writer()
        payload: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.metadata["run_id"],
            "config": self.config.as_dict(),
            "metadata_content_sha256": self.metadata["content_sha256"],
            "static_encoding": self.metadata["static_encoding"],
            "initial_implementation_source_sha256": self.metadata["source_sha256"],
            "status": status,
            "updated_utc": utc_now(),
            "outer_models_seen": self.models_seen,
            "committed_cut_count": len(self.journal.records),
            "cut_counts": self._cut_counts(),
            "journal_head_sha256": self.journal.head,
            "journal_file_sha256": self.journal.file_sha256(),
            "implementation_source_sha256": self.current_sources,
        }
        payload.update(extra)
        atomic_write_json(self.progress_path, payload)
        self.progress = read_hashed_json(self.progress_path)

    def _commit_cut(
        self,
        kind: str,
        witness: dict[str, object],
        graph: GraphSnapshot,
    ) -> dict[str, object]:
        self._assert_writer()
        if collect_source_hashes() != self.current_sources:
            raise RuntimeError("implementation sources changed during this invocation")
        sequence = len(self.journal.records)
        provisional = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.metadata["run_id"],
            "kind": kind,
            "candidate": {
                "graph_sha256": graph.graph_sha256,
                "edges_hex": graph.edges_hex,
            },
            "witness": witness,
            "outer_model_number": self.models_seen,
            "implementation_source_sha256": self.current_sources,
        }
        validate_cut_witness(self.config, provisional)
        encoding = self.problem.build_cut(kind, witness, sequence)
        provisional["encoding"] = encoding.summary
        record = self.journal.append(provisional)
        self.problem.add_encoding(encoding)
        self._checkpoint("RUNNING", last_candidate_graph_sha256=graph.graph_sha256)
        return record

    def _write_result(self, status: str, **extra: object) -> Path:
        self._assert_writer()
        if collect_source_hashes() != self.current_sources:
            raise RuntimeError("implementation sources changed before result write")
        payload: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.metadata["run_id"],
            "status": status,
            "created_utc": utc_now(),
            "config": self.config.as_dict(),
            "metadata_content_sha256": self.metadata["content_sha256"],
            "static_encoding": self.metadata["static_encoding"],
            "initial_implementation_source_sha256": self.metadata["source_sha256"],
            "outer_models_seen": self.models_seen,
            "committed_cut_count": len(self.journal.records),
            "cut_counts": self._cut_counts(),
            "journal_head_sha256": self.journal.head,
            "journal_file_sha256": self.journal.file_sha256(),
            "implementation_source_sha256": self.current_sources,
        }
        payload.update(extra)
        path = self.run_dir / "result.json"
        atomic_write_json(path, payload)
        self.result = read_hashed_json(path)
        return path

    def _dump_candidate(
        self,
        graph: GraphSnapshot,
        admissibility_stats: dict[str, object],
        coloring_stats: dict[str, object],
    ) -> Path:
        self._assert_writer()
        if collect_source_hashes() != self.current_sources:
            raise RuntimeError("implementation sources changed before candidate dump")
        adj = graph.adjacency()
        degrees = [mask.bit_count() for mask in adj]
        verifier = HERE / "verify_candidate.py"
        preset = load_cases().get(self.config.name)
        approved_preset = self.config.name if preset == self.config else None
        preset_argument = (
            f" --approved-preset {approved_preset}" if approved_preset is not None else ""
        )
        payload: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": "fixed_clique_cegar_candidate",
            "created_utc": utc_now(),
            "run": {
                "run_id": self.metadata["run_id"],
                "metadata_content_sha256": self.metadata["content_sha256"],
                "static_encoding": self.metadata["static_encoding"],
                "initial_implementation_source_sha256": self.metadata["source_sha256"],
                "journal_head_sha256": self.journal.head,
                "journal_file_sha256": self.journal.file_sha256(),
                "outer_models_seen": self.models_seen,
                "implementation_source_sha256": self.current_sources,
            },
            "config": self.config.as_dict(),
            "graph": {
                "n": graph.n,
                "graph_sha256": graph.graph_sha256,
                "edges_hex": graph.edges_hex,
                "edges": graph.edge_list(),
                "edge_count": sum(graph.edge_bits),
                "degrees": degrees,
                "triangle_count": len(triangles(adj)),
            },
            "oracle_results": {
                "admissibility": {
                    "result": "UNSAT_NO_ADMISSIBLE_TARGET_SET",
                    **admissibility_stats,
                },
                "coloring": {
                    "result": "UNSAT_NO_TRIANGLE_AVOIDING_EDGE_COLORING",
                    **coloring_stats,
                },
                "warning": "These are solver results, not independently checkable UNSAT certificates.",
            },
            "independent_verification": {
                "script": str(verifier),
                "script_sha256": file_sha256(verifier),
                "approved_preset": approved_preset,
                "command": (
                    f'"{sys.executable}" "{verifier}" CANDIDATE.json '
                    f"--emit-cnf VERIFY_DIR{preset_argument}"
                ),
                "note": "The verifier reconstructs graph properties, maximal cliques, and both SAT instances independently from the raw edge list.",
            },
        }
        name = f"candidate-{graph.graph_sha256[:16]}.json"
        path = self.run_dir / name
        atomic_write_json(path, payload)
        candidate_file_hash = file_sha256(path)
        self._write_result(
            "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION",
            candidate_file=name,
            candidate_file_sha256=candidate_file_hash,
            candidate_graph_sha256=graph.graph_sha256,
        )
        self._checkpoint(
            "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION",
            candidate_file=name,
            candidate_file_sha256=candidate_file_hash,
            candidate_graph_sha256=graph.graph_sha256,
        )
        if self.result is None:
            raise AssertionError("candidate result write did not persist")
        self._validate_result(self.result)
        return path

    def run(self, max_iterations: int = 1, time_limit_seconds: float = 0.0) -> str:
        """Run at most max_iterations outer models; zero means no model limit."""

        self._assert_writer()
        if max_iterations < 0 or time_limit_seconds < 0:
            raise ValueError("limits must be nonnegative")
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

                forbidden = find_clique(adj, self.config.forbidden_clique_size)
                if forbidden is not None:
                    self._commit_cut(
                        "forbidden_clique",
                        {"vertices": list(forbidden)},
                        graph,
                    )
                    continue

                admissible = admissibility_oracle(graph, self.config.target_set_size)
                if admissible is not None:
                    self._commit_cut(
                        "admissibility",
                        {
                            "vertices": list(admissible.vertices),
                            "candidate_nontrivial_maximal_clique_count": admissible.maximal_clique_count,
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
                            mask.bit_count() >= 2
                            for mask in maximal_cliques_bk(adj)
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
        if self.problem.collected_clauses is None:
            raise ValueError("session was not opened with clause collection")
        clauses = self.problem.collected_clauses
        max_var = max((abs(lit) for clause in clauses for lit in clause), default=0)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="ascii", newline="\n") as handle:
            handle.write(f"p cnf {max_var} {len(clauses)}\n")
            for clause in clauses:
                handle.write(" ".join(map(str, clause)) + " 0\n")
        return {
            "path": str(path.resolve()),
            "sha256": file_sha256(path),
            "variables": max_var,
            "clauses": len(clauses),
            "journal_head_sha256": self.journal.head,
            "scope": "current relaxation containing every committed cut; forbidden cliques not yet witnessed remain lazy",
        }

    def audit_summary(self) -> dict[str, object]:
        if self.progress is None:
            raise ValueError("audit requires a bound progress.json")
        if int(self.progress["committed_cut_count"]) != len(self.journal.records):
            raise ValueError(
                "progress.json is a valid but stale journal prefix; resume once under "
                "the writer lock before treating the audit as current"
            )
        progress_summary = {
            "status": self.progress["status"],
            "path": str(self.progress_path),
            "file_sha256": file_sha256(self.progress_path),
            "journal_head_sha256": self.progress["journal_head_sha256"],
        }
        result_summary: dict[str, object] | None = None
        candidate_summary: dict[str, object] | None = None
        if self.result is not None:
            result_path = self.run_dir / "result.json"
            result_summary = {
                "status": self.result["status"],
                "path": str(result_path),
                "file_sha256": file_sha256(result_path),
            }
            if self.result["status"] == "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION":
                candidate_path = self.run_dir / str(self.result["candidate_file"])
                candidate_summary = {
                    "path": str(candidate_path),
                    "file_sha256": file_sha256(candidate_path),
                    "graph_sha256": self.result["candidate_graph_sha256"],
                }
        return {
            "status": "AUDIT_OK",
            "run_dir": str(self.run_dir),
            "run_id": self.metadata["run_id"],
            "config": self.config.as_dict(),
            "static_encoding": self.problem.static_encoding,
            "cut_count": len(self.journal.records),
            "cut_counts": self._cut_counts(),
            "journal_head_sha256": self.journal.head,
            "journal_file_sha256": self.journal.file_sha256(),
            "initial_implementation_source_sha256": self.metadata["source_sha256"],
            "current_implementation_source_sha256": self.current_sources,
            "progress": progress_summary,
            "result": result_summary,
            "candidate": candidate_summary,
            "checked": [
                "metadata content hash",
                "static CNF reproduction",
                "journal record hashes and hash chain",
                "per-cut implementation source provenance",
                "stored violating candidate graph hash and static constraints",
                "every cut witness against its stored candidate",
                "every regenerated cut clause hash",
                "progress metadata/static/source binding and journal-prefix linkage",
                "terminal result linkage to progress and the full journal",
                "candidate filename, file hash, graph hash, order, and run linkage when present",
            ],
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-cases", help="print the four production presets")

    run = sub.add_parser("run", help="create or resume a bounded CEGAR run")
    run.add_argument("--case", required=True, choices=sorted(load_cases()))
    run.add_argument("--run-dir", required=True, type=Path)
    run.add_argument(
        "--max-iterations",
        type=int,
        default=1,
        help="outer models in this invocation; 0 is unlimited (default: 1)",
    )
    run.add_argument(
        "--time-limit-seconds",
        type=float,
        default=0.0,
        help="checked between outer models; 0 is unlimited",
    )
    run.add_argument("--allow-code-drift", action="store_true")

    audit = sub.add_parser("audit", help="replay and validate a run journal")
    audit.add_argument("--run-dir", required=True, type=Path)
    audit.add_argument("--allow-code-drift", action="store_true")

    export = sub.add_parser("export", help="rebuild the current outer CNF as DIMACS")
    export.add_argument("--run-dir", required=True, type=Path)
    export.add_argument("--cnf", required=True, type=Path)
    export.add_argument("--manifest", type=Path)
    export.add_argument("--allow-code-drift", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "list-cases":
        print(json.dumps({k: v.as_dict() for k, v in load_cases().items()}, indent=2))
        return 0
    if args.command == "run":
        config = load_cases()[args.case]
        with RunDirectoryLock(args.run_dir) as run_lock:
            session = SearchSession(
                args.run_dir,
                config,
                allow_code_drift=args.allow_code_drift,
                run_lock=run_lock,
            )
            try:
                status = session.run(args.max_iterations, args.time_limit_seconds)
                print(json.dumps({"status": status, "run_dir": str(session.run_dir)}))
            finally:
                session.problem.close()
        return 0
    if args.command == "audit":
        session = SearchSession.from_existing(
            args.run_dir, allow_code_drift=args.allow_code_drift
        )
        try:
            print(json.dumps(session.audit_summary(), indent=2, sort_keys=True))
        finally:
            session.problem.close()
        return 0
    if args.command == "export":
        session = SearchSession.from_existing(
            args.run_dir,
            allow_code_drift=args.allow_code_drift,
            collect_clauses=True,
        )
        try:
            manifest = session.export_dimacs(args.cnf)
            manifest_path = args.manifest or args.cnf.with_suffix(args.cnf.suffix + ".json")
            atomic_write_json(manifest_path, manifest)
            print(json.dumps(with_content_hash(manifest), indent=2, sort_keys=True))
        finally:
            session.problem.close()
        return 0
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
