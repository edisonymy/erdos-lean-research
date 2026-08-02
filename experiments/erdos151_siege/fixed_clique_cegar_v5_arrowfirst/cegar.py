#!/usr/bin/env python3
"""Schema-v5 fixed-clique CEGAR with an arrowing-first separation oracle.

The schema-v3 implementation is loaded read-only and source-pinned.  V4 keeps
its static CNF and exact global admissibility cut encoding.  After complete
lazy forbidden-K5 separation it separates arrowing, then every fixed-clique
residual Z_c, then generic admissible-10 witnesses.  No earlier run directory
is readable as a v5 run directory.
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
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
V3_DIR = HERE.parent / "fixed_clique_cegar_v3"
CASES_PATH = HERE / "cases.json"
SCHEMA_VERSION = 5
V3_EXPECTED_SHA256 = {
    "cegar.py": "47085d027ac908e1af0851db904f19160d278bbf257048d599a9d8bedbdc8197",
    "verify_candidate.py": "df776a5c79ac438fd59c8e98447dd961059613a861bf12f8a563ab5dddfff5c4",
    "verify_static.py": "b93588581b6b6b2a440c01f5dedc54c477894b5a0f97d668e44d635213d77c97",
    "cases.json": "84355cdfd9dcf6bed7781b34fe6ba5d13d3e496ce96fd24f310f955df337963f",
    "requirements.txt": "63022582ca3ae3a45911331f74428edb2b38f471c15ceda82bac4dbe9377865a",
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_v3_snapshot() -> None:
    actual = {name: _sha256_file(V3_DIR / name) for name in V3_EXPECTED_SHA256}
    if actual != V3_EXPECTED_SHA256:
        raise RuntimeError(
            "the read-only fixed_clique_cegar_v3 snapshot has drifted: "
            f"expected={V3_EXPECTED_SHA256}, actual={actual}"
        )


def _load_v3() -> object:
    verify_v3_snapshot()
    name = "_erdos151_fixed_clique_cegar_v3_readonly_for_v5"
    spec = importlib.util.spec_from_file_location(name, V3_DIR / "cegar.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load pinned v3 implementation")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


v3 = _load_v3()
_base = v3._v1
_V3CaseConfig = v3.CaseConfig
_V1SearchSession = v3._V1SearchSession
_v3_validate_cut_witness = v3.validate_cut_witness

CardEnc = v3.CardEnc
Cadical195 = v3.Cadical195
CutEncoding = v3.CutEncoding
EdgeVariables = v3.EdgeVariables
EncType = v3.EncType
GraphSnapshot = v3.GraphSnapshot
IDPool = v3.IDPool
RunDirectoryLock = v3.RunDirectoryLock
atomic_write_json = v3.atomic_write_json
canonical_json_bytes = v3.canonical_json_bytes
coloring_oracle = v3.coloring_oracle
enumerate_cliques_exact = v3.enumerate_cliques_exact
is_clique = v3.is_clique
load_hashed_json = v3.load_hashed_json
make_batch_item = v3.make_batch_item
maximal_cliques_bk = v3.maximal_cliques_bk
pack_bits = v3.pack_bits
sha256_bytes = v3.sha256_bytes
triangles = v3.triangles


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
    residual_beta_bound: int | None = None
    residual_admissibility_target_size: int | None = None

    def validate(self) -> None:
        # Reuse every v3 structural/static validation rule.
        _V3CaseConfig(
            self.name,
            self.n,
            self.fixed_clique_size,
            self.forbidden_clique_size,
            self.degree_min,
            self.degree_max,
            self.target_set_size,
            self.scope,
            self.forbidden_mode,
            self.admissibility_batch_size,
            self.residual_beta_bound,
        ).validate()
        target = self.residual_admissibility_target_size
        if target is not None:
            if self.forbidden_clique_size != self.fixed_clique_size + 1:
                raise ValueError("residual separation requires M to become maximum")
            if target != self.target_set_size - (self.fixed_clique_size - 1):
                raise ValueError("residual target does not translate to target_set_size")
            if target < 2:
                raise ValueError("residual admissibility target must be at least two")

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
            residual_beta_bound=(None if value.get("residual_beta_bound") is None else int(value["residual_beta_bound"])),
            residual_admissibility_target_size=(None if value.get("residual_admissibility_target_size") is None else int(value["residual_admissibility_target_size"])),
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
    verify_v3_snapshot()
    paths = {
        "v5-arrowfirst/cegar.py": HERE / "cegar.py",
        "v5-arrowfirst/verify_candidate.py": HERE / "verify_candidate.py",
        "v5-arrowfirst/verify_static.py": HERE / "verify_static.py",
        "v5-arrowfirst/cases.json": HERE / "cases.json",
        "v5-arrowfirst/requirements.txt": HERE / "requirements.txt",
        **{f"pinned-v3/{name}": V3_DIR / name for name in V3_EXPECTED_SHA256},
    }
    return {name: _sha256_file(path) for name, path in paths.items()}


def residual_vertices(config: CaseConfig, graph: GraphSnapshot, c: int) -> tuple[int, ...]:
    """Compute Z_c exactly; adjacency to c itself is deliberately irrelevant."""

    if not 0 <= c < config.fixed_clique_size:
        raise ValueError("c is not a fixed-clique vertex")
    adj = graph.adjacency()
    return tuple(
        x
        for x in range(config.fixed_clique_size, config.n)
        if all(not ((adj[x] >> p) & 1) for p in range(config.fixed_clique_size) if p != c)
    )


def _induced_adjacency(adj: Sequence[int], vertices: Sequence[int]) -> tuple[int, ...]:
    index = {vertex: i for i, vertex in enumerate(vertices)}
    return tuple(
        sum(1 << index[w] for w in vertices if w != vertex and ((adj[vertex] >> w) & 1))
        for vertex in vertices
    )


@dataclasses.dataclass(frozen=True)
class SubsetAdmissibilityWitness:
    vertices: tuple[int, ...]
    nontrivial_maximal_clique_count: int
    solver_calls: int = 1


def admissible_subset_oracle(
    graph: GraphSnapshot, universe: Sequence[int], target_size: int
) -> SubsetAdmissibilityWitness | None:
    """Find a set admissible in the induced graph on ``universe``.

    Maximality is computed in G[universe], not in the ambient graph.  This is
    the stronger condition needed for the residual-to-global implication.
    """

    vertices = tuple(sorted(map(int, universe)))
    if len(set(vertices)) != len(vertices) or any(v < 0 or v >= graph.n for v in vertices):
        raise ValueError("invalid induced universe")
    if target_size < 0:
        raise ValueError("target_size must be nonnegative")
    if len(vertices) < target_size:
        return None
    local_adj = _induced_adjacency(graph.adjacency(), vertices)
    maximal = [mask for mask in maximal_cliques_bk(local_adj) if mask.bit_count() >= 2]
    clauses = [
        [-(i + 1) for i in range(len(vertices)) if (mask >> i) & 1]
        for mask in maximal
    ]
    clauses.extend(
        CardEnc.atleast(
            lits=list(range(1, len(vertices) + 1)),
            bound=target_size,
            top_id=len(vertices),
            encoding=EncType.seqcounter,
        ).clauses
    )
    with Cadical195(bootstrap_with=clauses) as solver:
        result = solver.solve()
        if result is False:
            return None
        if result is not True:
            raise RuntimeError(f"residual admissibility solver returned {result!r}")
        positive = {literal for literal in (solver.get_model() or []) if literal > 0}
    selected_local = tuple(i for i in range(len(vertices)) if i + 1 in positive)[:target_size]
    members = sum(1 << i for i in selected_local)
    if len(selected_local) != target_size or any((mask & ~members) == 0 for mask in maximal):
        raise AssertionError("residual oracle returned an invalid induced witness")
    return SubsetAdmissibilityWitness(
        tuple(vertices[i] for i in selected_local), len(maximal)
    )


@dataclasses.dataclass(frozen=True)
class ResidualSeparation:
    items: tuple[dict[str, object], ...]
    searches: tuple[dict[str, object], ...]


def _validated_residual_translation_shape(
    config: CaseConfig, item: dict[str, object]
) -> tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    """Validate the graph-independent shape consumed by the global encoder."""

    target = config.residual_admissibility_target_size
    if target is None:
        raise ValueError("residual separation is disabled")
    c = int(item["fixed_clique_vertex"])
    fixed = tuple(range(config.fixed_clique_size))
    if c not in fixed:
        raise ValueError("invalid residual fixed-clique vertex")
    residual = tuple(int(v) for v in item["residual_vertices"])
    if (
        len(residual) != target
        or len(set(residual)) != target
        or tuple(sorted(residual)) != residual
        or any(v < config.fixed_clique_size or v >= config.n for v in residual)
    ):
        raise ValueError("residual admissibility set must contain exactly target distinct outside vertices")
    fixed_part = tuple(p for p in fixed if p != c)
    if item.get("fixed_clique_part") != list(fixed_part):
        raise ValueError("residual fixed-clique part does not reproduce")
    global_vertices = tuple(sorted((*fixed_part, *residual)))
    if (
        len(global_vertices) != config.target_set_size
        or len(set(global_vertices)) != config.target_set_size
        or item.get("vertices") != list(global_vertices)
        or len(set(int(v) for v in item["vertices"])) != config.target_set_size
    ):
        raise ValueError("translated global set must contain exactly target_set_size distinct vertices")
    return c, residual, fixed_part, global_vertices


def residual_admissibility_oracle(
    config: CaseConfig, graph: GraphSnapshot
) -> ResidualSeparation | None:
    target = config.residual_admissibility_target_size
    if target is None:
        return None
    fixed = tuple(range(config.fixed_clique_size))
    items: list[dict[str, object]] = []
    searches: list[dict[str, object]] = []
    ambient_maximal_count = sum(
        mask.bit_count() >= 2 for mask in maximal_cliques_bk(graph.adjacency())
    )
    for c in fixed:
        z = residual_vertices(config, graph, c)
        found = admissible_subset_oracle(graph, z, target)
        searches.append(
            {
                "fixed_clique_vertex": c,
                "z_vertices": list(z),
                "z_size": len(z),
                "target_size": target,
                "result": "FOUND" if found is not None else "NO_WITNESS",
                "oracle_solver_calls": int(len(z) >= target),
            }
        )
        if found is None:
            continue
        fixed_part = tuple(p for p in fixed if p != c)
        global_vertices = tuple(sorted((*fixed_part, *found.vertices)))
        payload = {
            "fixed_clique_vertex": c,
            "z_vertices": list(z),
            "residual_vertices": list(found.vertices),
            "residual_target_size": target,
            "residual_beta_bound_violated": target - 1,
            "residual_nontrivial_maximal_clique_count": found.nontrivial_maximal_clique_count,
            "fixed_clique_part": list(fixed_part),
            "vertices": list(global_vertices),
            "candidate_nontrivial_maximal_clique_count": ambient_maximal_count,
            "translation": "(M\\{c}) union S; ambient-maximal K subset S implies K maximal in G[Z_c]",
        }
        _validated_residual_translation_shape(config, payload)
        items.append(v3.make_batch_item("residual_admissibility", payload))
    if not items:
        return None
    return ResidualSeparation(tuple(items), tuple(searches))


class OuterProblem(v3.OuterProblem):
    def build_cut(self, kind: str, witness: dict[str, object], sequence: int) -> CutEncoding:
        if kind != "residual_admissibility_batch":
            return super().build_cut(kind, witness, sequence)
        before = self.pool.top
        items = [dict(item) for item in witness["items"]]
        for item in items:
            _validated_residual_translation_shape(self.config, item)
        clauses, summaries = v3.encode_admissibility_batch(
            self.edges, self.pool, items, f"cut:{sequence}:{kind}"
        )
        summary = v3.summarize_encoding(kind, clauses, before, self.pool.top)
        summary["logical_cut_count"] = len(items)
        summary["item_encodings"] = summaries
        summary["translation_encoding"] = "exact existing global admissibility cut generator"
        return CutEncoding(clauses, summary)


def _nontrivial_maximal(adj: Sequence[int]) -> list[int]:
    return [mask for mask in maximal_cliques_bk(adj) if mask.bit_count() >= 2]


def _vertex_mask(vertices: Sequence[int]) -> int:
    mask = 0
    for vertex in vertices:
        mask |= 1 << int(vertex)
    return mask


def validate_cut_witness(config: CaseConfig, record: dict[str, object]) -> GraphSnapshot:
    if str(record["kind"]) != "residual_admissibility_batch":
        return _v3_validate_cut_witness(config, record)
    candidate = record.get("candidate")
    witness = record.get("witness")
    if not isinstance(candidate, dict) or not isinstance(witness, dict):
        raise ValueError("residual cut lacks candidate or witness object")
    graph = GraphSnapshot.from_hex(config.n, str(candidate["edges_hex"]))
    if graph.graph_sha256 != candidate.get("graph_sha256"):
        raise ValueError("cut candidate graph hash mismatch")
    v3.validate_static_candidate(config, graph)
    adj = graph.adjacency()
    if v3.find_clique(adj, config.forbidden_clique_size) is not None:
        raise ValueError("residual separation was recorded before forbidden cliques")
    raw_items = witness.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("residual batch must contain at least one item")
    items = [dict(item) for item in raw_items]
    if int(witness.get("logical_cut_count", -1)) != len(items):
        raise ValueError("residual batch logical cut count is wrong")
    target = config.residual_admissibility_target_size
    if target is None:
        raise ValueError("residual separation is disabled")
    fixed = tuple(range(config.fixed_clique_size))
    ambient_maximal = _nontrivial_maximal(adj)
    seen_c: set[int] = set()
    for item in items:
        v3._verify_batch_item_hash("residual_admissibility", item)
        c, residual, fixed_part, global_vertices = _validated_residual_translation_shape(
            config, item
        )
        if c in seen_c or c not in fixed:
            raise ValueError("duplicate or invalid residual fixed-clique vertex")
        seen_c.add(c)
        z = residual_vertices(config, graph, c)
        if item.get("z_vertices") != list(z):
            raise ValueError("stored Z_c does not exactly reproduce")
        if not set(residual) <= set(z):
            raise ValueError("invalid residual admissibility set")
        local_adj = _induced_adjacency(adj, z)
        local_maximal = _nontrivial_maximal(local_adj)
        local_index = {vertex: i for i, vertex in enumerate(z)}
        members = _vertex_mask(tuple(local_index[v] for v in residual))
        if any((mask & ~members) == 0 for mask in local_maximal):
            raise ValueError("residual set is not G[Z_c]-admissible")
        if int(item.get("residual_nontrivial_maximal_clique_count", -1)) != len(local_maximal):
            raise ValueError("residual maximal-clique count is wrong")
        if int(item.get("residual_target_size", -1)) != target or int(item.get("residual_beta_bound_violated", -1)) != target - 1:
            raise ValueError("residual target/beta provenance is wrong")
        global_members = _vertex_mask(global_vertices)
        if any((mask & ~global_members) == 0 for mask in ambient_maximal):
            raise ValueError("translated global set is not admissible")
        if int(item.get("candidate_nontrivial_maximal_clique_count", -1)) != len(ambient_maximal):
            raise ValueError("ambient maximal-clique count is wrong")
    searches = witness.get("searches")
    if not isinstance(searches, list) or len(searches) != len(fixed):
        raise ValueError("residual search provenance is incomplete")
    for c, raw in enumerate(searches):
        search = dict(raw)
        z = residual_vertices(config, graph, c)
        if search.get("fixed_clique_vertex") != c or search.get("z_vertices") != list(z) or search.get("z_size") != len(z) or search.get("target_size") != target:
            raise ValueError("residual search provenance does not reproduce")
        expected = "FOUND" if c in seen_c else "NO_WITNESS"
        if search.get("result") != expected or int(search.get("oracle_solver_calls", -1)) != int(len(z) >= target):
            raise ValueError("residual search result provenance is wrong")
        if expected == "NO_WITNESS" and admissible_subset_oracle(graph, z, target) is not None:
            raise ValueError("claimed residual NO_WITNESS is false")
    return graph


class SearchSession(v3.SearchSession):
    def __init__(self, *args: object, checkpoint_ready: bool = True, **kwargs: object):
        run_dir = Path(args[0] if args else kwargs["run_dir"]).resolve()
        was_new = not (run_dir / _base.METADATA_NAME).exists()
        self._repair_terminal_progress = bool(kwargs.get("repair_journal", True))
        self._terminal_repair_allows_code_drift = bool(kwargs.get("allow_code_drift", False))
        if not was_new:
            preflight = load_hashed_json(run_dir / _base.METADATA_NAME)
            implementation = preflight.get("implementation")
            if (
                preflight.get("schema_version") != SCHEMA_VERSION
                or not isinstance(implementation, dict)
                or implementation.get("engine") != "fixed_clique_cegar_v5_arrowfirst"
                or implementation.get("schema") != SCHEMA_VERSION
            ):
                raise ValueError("run metadata is not a fixed_clique_cegar_v5_arrowfirst run")
        _V1SearchSession.__init__(self, *args, checkpoint_ready=False, **kwargs)
        if was_new:
            metadata = dict(self.metadata)
            metadata.pop("content_sha256", None)
            metadata["implementation"] = {
                "engine": "fixed_clique_cegar_v5_arrowfirst",
                "schema": SCHEMA_VERSION,
                "pinned_v3_source_sha256": V3_EXPECTED_SHA256,
                "journal_unit": "one candidate with a conjunctive batch of independently hashed cuts",
                "dynamic_extension": "arrowing-first, then induced-admissibility separation translated through the global cut encoder",
                "config_sha256": sha256_bytes(canonical_json_bytes(self.config.as_dict())),
            }
            metadata["semantics"] = {
                "separation_order": "complete forbidden clique, arrowing, residual admissibility for every c, generic global admissibility",
                "residual_admissibility_cut": "S is admissible in G[Z_c], then (M\\{c}) union S is globally admissible and is encoded by the exact global admissibility generator",
                "residual_maximality_direction": "ambient-maximal clique contained in Z_c implies maximal in the induced graph G[Z_c]",
                "v3_static_encoding": "unchanged exact residual reification and cardinality bounds",
            }
            atomic_write_json(self.metadata_path, metadata)
            self.metadata = load_hashed_json(self.metadata_path)
        else:
            implementation = self.metadata.get("implementation")
            if (
                not isinstance(implementation, dict)
                or implementation.get("engine") != "fixed_clique_cegar_v5_arrowfirst"
                or implementation.get("schema") != SCHEMA_VERSION
                or implementation.get("pinned_v3_source_sha256") != V3_EXPECTED_SHA256
            ):
                raise ValueError("run metadata has a different v3 source pin")
            if implementation.get("config_sha256") != sha256_bytes(canonical_json_bytes(self.config.as_dict())):
                raise ValueError("run metadata config hash does not reproduce")
        expected_keys = set(self.current_sources)
        for record in self.journal.records:
            source_map = record.get("implementation_source_sha256")
            if not isinstance(source_map, dict) or set(source_map) != expected_keys:
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

    def _validate_candidate_linkage(self, result: dict[str, object], progress: dict[str, object]) -> dict[str, object]:
        candidate = _V1SearchSession._validate_candidate_linkage(self, result, progress)
        independent = candidate.get("independent_verification")
        run = candidate.get("run")
        if not isinstance(independent, dict) or not isinstance(run, dict):
            raise ValueError("candidate lacks verifier provenance")
        source_map = run.get("implementation_source_sha256")
        if (
            not isinstance(source_map, dict)
            or set(source_map) != set(self.current_sources)
            or any(
                not isinstance(value, str)
                or len(value) != 64
                or any(char not in "0123456789abcdef" for char in value)
                for value in source_map.values()
            )
            or independent.get("script_sha256") != source_map.get("v5-arrowfirst/verify_candidate.py")
        ):
            raise ValueError("candidate verifier hash does not match v5-arrowfirst run sources")
        preset = load_cases().get(self.config.name)
        expected = self.config.name if preset == self.config else None
        if independent.get("approved_preset") != expected:
            raise ValueError("candidate verifier preset binding is wrong")
        verifier = HERE / "verify_candidate.py"
        preset_argument = f" --approved-preset {expected}" if expected is not None else ""
        expected_command = (
            f'"{sys.executable}" "{verifier}" CANDIDATE.json '
            f"--emit-cnf VERIFY_DIR{preset_argument}"
        )
        if independent.get("script") != str(verifier):
            raise ValueError("candidate independent-verifier script binding is wrong")
        if independent.get("command") != expected_command:
            raise ValueError("candidate independent-verifier command/preset binding is wrong")
        return candidate

    def run(self, max_iterations: int = 1, time_limit_seconds: float = 0.0) -> str:
        self._assert_writer()
        if max_iterations < 0 or not math.isfinite(time_limit_seconds) or time_limit_seconds < 0:
            raise ValueError("limits must be finite and nonnegative")
        if self.result is not None:
            return str(self.result["status"])
        started = time.monotonic()
        processed = 0
        last_residual_searches: list[dict[str, object]] = []
        try:
            while max_iterations == 0 or processed < max_iterations:
                if time_limit_seconds and time.monotonic() - started >= time_limit_seconds:
                    break
                graph = self.problem.solve()
                if graph is None:
                    self._write_result("OUTER_UNSAT_NO_PROOF_CERTIFICATE", warning="Incremental UNSAT has no proof certificate; make no UNSAT claim.")
                    self._checkpoint("OUTER_UNSAT_NO_PROOF_CERTIFICATE")
                    return "OUTER_UNSAT_NO_PROOF_CERTIFICATE"
                processed += 1
                self.models_seen += 1
                v3.validate_static_candidate(self.config, graph)
                adj = graph.adjacency()
                forbidden = enumerate_cliques_exact(adj, self.config.forbidden_clique_size)
                if forbidden:
                    items = [v3.make_batch_item("forbidden_clique", {"vertices": list(vertices)}) for vertices in forbidden]
                    self._commit_cut("forbidden_clique_batch", {"items": items, "logical_cut_count": len(items)}, graph)
                    continue
                # The v5 schedule is intentionally fixed: complete K5 batches
                # above, then arrowing, then the full residual sweep, then the
                # inherited generic global separator.  Every committed cut is
                # still replayed through the unchanged exact validators.
                coloring = coloring_oracle(graph)
                if coloring is not None:
                    self._commit_cut("arrowing", {"total_coloring_hex": pack_bits(coloring.total_colors), "present_red_edge_count": coloring.present_red_edges, "present_triangle_count": coloring.present_triangle_count, "total_monochromatic_triple_count": coloring.total_monochromatic_triples, "absent_pair_extension": "sha256(graph_sha256 || big_endian_pair_index), low bit"}, graph)
                    continue
                residual = residual_admissibility_oracle(self.config, graph)
                if residual is not None:
                    last_residual_searches = list(residual.searches)
                    self._commit_cut(
                        "residual_admissibility_batch",
                        {
                            "items": list(residual.items),
                            "logical_cut_count": len(residual.items),
                            "searches": list(residual.searches),
                            "separation_order": "after_arrowing_before_generic_global_admissibility",
                        },
                        graph,
                    )
                    continue
                last_residual_searches = [
                    {
                        "fixed_clique_vertex": c,
                        "z_vertices": list(residual_vertices(self.config, graph, c)),
                        "result": "NO_WITNESS",
                    }
                    for c in range(self.config.fixed_clique_size)
                ]
                admissible = v3.admissibility_oracle_batch(graph, self.config.target_set_size, self.config.admissibility_batch_size)
                if admissible is not None:
                    items = [
                        v3.make_batch_item("admissibility", {"vertices": list(vertices), "candidate_nontrivial_maximal_clique_count": admissible.maximal_clique_count})
                        for vertices in admissible.vertex_sets
                    ]
                    self._commit_cut("admissibility_batch", {"items": items, "logical_cut_count": len(items), "requested_batch_limit": self.config.admissibility_batch_size, "enumeration_exhausted": admissible.enumeration_exhausted, "oracle_solver_calls": admissible.solver_calls}, graph)
                    continue
                candidate_path = self._dump_candidate(
                    graph,
                    {"nontrivial_ambient_maximal_clique_count": len(_nontrivial_maximal(adj)), "target_set_size": self.config.target_set_size, "residual_searches": last_residual_searches},
                    {"present_edge_count": sum(graph.edge_bits), "present_triangle_count": len(triangles(adj))},
                )
                print(f"candidate dumped: {candidate_path}")
                return "CANDIDATE_REQUIRES_INDEPENDENT_VERIFICATION"
        except KeyboardInterrupt:
            self._checkpoint("PAUSED_BY_INTERRUPT")
            return "PAUSED_BY_INTERRUPT"
        self._checkpoint("PAUSED_AT_LIMIT", invocation_models_processed=processed, invocation_elapsed_seconds=round(time.monotonic() - started, 3))
        return "PAUSED_AT_LIMIT"

    def audit_summary(self) -> dict[str, object]:
        summary = super().audit_summary()
        summary["checked"].append("exact Z_c, induced maximality, residual witness, global translation, and unchanged global cut encoding")
        summary["checked"].append("schema-v5 run-root isolation and complete v5-arrowfirst plus pinned-v3 source binding")
        return summary


# The inherited persistence/CLI resolves these symbols dynamically.  Only the
# private in-memory modules loaded for this process are patched.
for module in (v3, _base):
    module.SCHEMA_VERSION = SCHEMA_VERSION
    module.HERE = HERE
    module.CASES_PATH = CASES_PATH
    module.CaseConfig = CaseConfig
    module.load_cases = load_cases
    module.collect_source_hashes = collect_source_hashes
    module.OuterProblem = OuterProblem
    module.validate_cut_witness = validate_cut_witness
    module.SearchSession = SearchSession


def main(argv: Sequence[str] | None = None) -> int:
    return _base.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
