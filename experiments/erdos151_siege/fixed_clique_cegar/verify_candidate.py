#!/usr/bin/env python3
"""Independent candidate checker and SAT-instance exporter.

This file deliberately imports no search implementation.  It reconstructs
the graph from the packed edge vector, enumerates ambient-maximal cliques by
a different bounded-degree local-subset algorithm, and rebuilds both oracle
instances.  It uses Glucose rather than the searcher's CaDiCaL.  With
``--emit-cnf`` it also writes portable DIMACS files for proof-producing
external solvers; a bare UNSAT result from this script is not a proof
certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
from pathlib import Path
from typing import Sequence

try:
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Glucose4
except ImportError as exc:  # pragma: no cover
    raise SystemExit("python-sat is required for exact candidate verification") from exc


SCHEMA_VERSION = 1
HERE = Path(__file__).resolve().parent
CASES_PATH = HERE / "cases.json"


def load_approved_presets() -> dict[str, dict[str, object]]:
    raw = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported cases.json schema")
    result: dict[str, dict[str, object]] = {}
    for name, body in raw["cases"].items():
        config = dict(body)
        config["name"] = name
        result[name] = config
    return result


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


def verify_content_hash(payload: dict[str, object], path: Path) -> None:
    stored = payload.get("content_sha256")
    body = dict(payload)
    body.pop("content_sha256", None)
    actual = sha256_bytes(canonical_json_bytes(body))
    if stored != actual:
        raise ValueError(f"candidate content hash mismatch: {actual} != {stored} ({path})")


def with_content_hash(payload: dict[str, object]) -> dict[str, object]:
    body = dict(payload)
    body.pop("content_sha256", None)
    body["content_sha256"] = sha256_bytes(canonical_json_bytes(body))
    return body


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    final = with_content_hash(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(final, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def unpack_bits(encoded: str, count: int) -> tuple[bool, ...]:
    raw = bytes.fromhex(encoded)
    expected = (count + 7) // 8
    if len(raw) != expected:
        raise ValueError(f"packed edge vector has {len(raw)} bytes, expected {expected}")
    if count % 8 and raw and raw[-1] >> (count % 8):
        raise ValueError("packed edge vector has nonzero unused bits")
    return tuple(bool(raw[i >> 3] & (1 << (i & 7))) for i in range(count))


def graph_sha256(n: int, edges_hex: str) -> str:
    domain = b"erdos151-fixed-clique-graph-v1\0"
    return sha256_bytes(domain + n.to_bytes(4, "big") + bytes.fromhex(edges_hex))


def adjacency(n: int, edge_bits: Sequence[bool]) -> list[int]:
    adj = [0] * n
    for bit, (u, v) in zip(edge_bits, itertools.combinations(range(n), 2)):
        if bit:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
    return adj


def is_clique(vertices: Sequence[int], adj: Sequence[int]) -> bool:
    return all((adj[u] >> v) & 1 for u, v in itertools.combinations(vertices, 2))


def enumerate_maximal_cliques_local(adj: Sequence[int]) -> list[tuple[int, ...]]:
    """Enumerate maximal cliques by subsets of each minimum vertex's neighbors.

    This is independent of the searcher's Bron--Kerbosch code.  The production
    degree ceiling nine makes at most 2^9 local subsets relevant per root.
    """

    n = len(adj)
    all_vertices = (1 << n) - 1
    found: set[tuple[int, ...]] = set()
    for root in range(n):
        higher = [v for v in range(root + 1, n) if (adj[root] >> v) & 1]
        for subset_mask in range(1, 1 << len(higher)):
            clique = (root,) + tuple(
                higher[i] for i in range(len(higher)) if (subset_mask >> i) & 1
            )
            if not is_clique(clique, adj):
                continue
            common = all_vertices
            members = 0
            for vertex in clique:
                common &= adj[vertex]
                members |= 1 << vertex
            if not (common & ~members):
                found.add(clique)
    return sorted(found)


def enumerate_triangles(adj: Sequence[int]) -> list[tuple[int, int, int]]:
    result = []
    for triple in itertools.combinations(range(len(adj)), 3):
        if is_clique(triple, adj):
            result.append(triple)
    return result


def write_dimacs(path: Path, variable_count: int, clauses: Sequence[Sequence[int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {variable_count} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")


def build_admissibility_cnf(
    n: int, maximal_cliques: Sequence[Sequence[int]], target: int
) -> tuple[list[list[int]], int]:
    clauses = [[-(v + 1) for v in clique] for clique in maximal_cliques]
    card = CardEnc.atleast(
        lits=list(range(1, n + 1)),
        bound=target,
        top_id=n,
        encoding=EncType.seqcounter,
    )
    clauses.extend(card.clauses)
    return clauses, max(n, card.nv)


def build_coloring_cnf(
    edge_bits: Sequence[bool], n: int, triangles: Sequence[tuple[int, int, int]]
) -> tuple[list[list[int]], int, list[tuple[int, int]]]:
    all_pairs = list(itertools.combinations(range(n), 2))
    present = [pair for pair, bit in zip(all_pairs, edge_bits) if bit]
    variable = {pair: index + 1 for index, pair in enumerate(present)}
    clauses: list[list[int]] = []
    for a, b, c in triangles:
        colors = [variable[(a, b)], variable[(a, c)], variable[(b, c)]]
        clauses.append([-literal for literal in colors])
        clauses.append(colors)
    return clauses, len(present), present


def solve_cnf(
    clauses: Sequence[Sequence[int]], declared_variables: int
) -> tuple[bool, set[int]]:
    # Tautologies introduce variables unused by semantic clauses so emitted
    # and in-memory instances have the same declared variable universe.
    bootstrap = [list(clause) for clause in clauses]
    bootstrap.extend([[v, -v] for v in range(1, declared_variables + 1)])
    with Glucose4(bootstrap_with=bootstrap) as solver:
        sat = solver.solve()
        if sat not in (True, False):
            raise RuntimeError(f"Glucose returned indeterminate status {sat!r}")
        model = {lit for lit in (solver.get_model() or []) if lit > 0}
    return sat, model


def verify_candidate(
    candidate_path: Path,
    *,
    emit_cnf: Path | None = None,
    solve: bool = True,
    approved_preset: str | None = None,
) -> dict[str, object]:
    data = json.loads(candidate_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("candidate must be a JSON object")
    verify_content_hash(data, candidate_path)
    if data.get("artifact_type") != "fixed_clique_cegar_candidate":
        raise ValueError("wrong candidate artifact type")
    config = dict(data["config"])
    graph = dict(data["graph"])
    if approved_preset is not None:
        presets = load_approved_presets()
        if approved_preset not in presets:
            raise ValueError(f"unknown approved preset {approved_preset!r}")
        if config != presets[approved_preset]:
            raise ValueError(
                f"candidate config does not exactly match approved preset {approved_preset}"
            )
    n = int(config["n"])
    if int(graph.get("n", -1)) != n:
        raise ValueError("candidate graph.n does not match config.n")
    count = n * (n - 1) // 2
    edges_hex = str(graph["edges_hex"])
    edge_bits = unpack_bits(edges_hex, count)
    actual_graph_hash = graph_sha256(n, edges_hex)
    if graph.get("graph_sha256") != actual_graph_hash:
        raise ValueError("candidate graph SHA-256 mismatch")

    pairs = list(itertools.combinations(range(n), 2))
    expected_edges = [list(pair) for pair, bit in zip(pairs, edge_bits) if bit]
    if graph.get("edges") != expected_edges:
        raise ValueError("candidate edge list disagrees with packed edge vector")
    if int(graph.get("edge_count", -1)) != len(expected_edges):
        raise ValueError("candidate edge count disagrees with edge vector")

    adj = adjacency(n, edge_bits)
    degrees = [mask.bit_count() for mask in adj]
    if graph.get("degrees") != degrees:
        raise ValueError("recorded degrees disagree with graph")
    degree_min = int(config["degree_min"])
    degree_max = int(config["degree_max"])
    if not all(degree_min <= degree <= degree_max for degree in degrees):
        raise ValueError("degree interval violation")
    fixed_size = int(config["fixed_clique_size"])
    if not is_clique(tuple(range(fixed_size)), adj):
        raise ValueError("fixed clique is absent")

    maximal = enumerate_maximal_cliques_local(adj)
    forbidden_size = int(config["forbidden_clique_size"])
    too_large = next((clique for clique in maximal if len(clique) >= forbidden_size), None)
    if too_large is not None:
        raise ValueError(f"forbidden clique found inside maximal clique {too_large}")
    triangles = enumerate_triangles(adj)
    if int(graph.get("triangle_count", -1)) != len(triangles):
        raise ValueError("recorded triangle count disagrees with graph")

    target = int(config["target_set_size"])
    adm_clauses, adm_vars = build_admissibility_cnf(n, maximal, target)
    color_clauses, color_vars, present_pairs = build_coloring_cnf(
        edge_bits, n, triangles
    )

    formula_manifest: dict[str, object] = {}
    if emit_cnf is not None:
        emit_cnf.mkdir(parents=True, exist_ok=True)
        adm_path = emit_cnf / "admissible-set.cnf"
        color_path = emit_cnf / "triangle-coloring.cnf"
        write_dimacs(adm_path, adm_vars, adm_clauses)
        write_dimacs(color_path, color_vars, color_clauses)
        formula_manifest = {
            "schema_version": SCHEMA_VERSION,
            "candidate": str(candidate_path.resolve()),
            "candidate_file_sha256": file_sha256(candidate_path),
            "candidate_graph_sha256": actual_graph_hash,
            "preset_binding": {
                "requested": approved_preset,
                "status": "MATCHED" if approved_preset else "NOT_REQUESTED",
            },
            "formulas": {
                "admissible_set": {
                    "path": str(adm_path.resolve()),
                    "sha256": file_sha256(adm_path),
                    "variables": adm_vars,
                    "clauses": len(adm_clauses),
                    "meaning": f"SAT iff an admissible set of size at least {target} exists",
                },
                "triangle_coloring": {
                    "path": str(color_path.resolve()),
                    "sha256": file_sha256(color_path),
                    "variables": color_vars,
                    "clauses": len(color_clauses),
                    "meaning": "SAT iff all present edges admit a red/blue coloring with no monochromatic present triangle",
                },
            },
            "warning": "UNSAT must be accompanied by independently checked solver proofs for a proof-grade claim.",
        }
        atomic_write_json(emit_cnf / "manifest.json", formula_manifest)

    checks: list[str] = [
        "candidate JSON content hash",
        "candidate graph.n equals config.n",
        "packed edge vector, raw edge list, graph hash, counts",
        "degree interval and fixed clique",
        "forbidden clique absence",
        "independent local-subset enumeration of all ambient-maximal cliques",
    ]
    if approved_preset is not None:
        checks.append(f"embedded config exactly matches approved preset {approved_preset}")
    result: dict[str, object] = {
        "status": "STRUCTURE_VERIFIED" if not solve else "VERIFYING",
        "candidate": str(candidate_path.resolve()),
        "candidate_file_sha256": file_sha256(candidate_path),
        "candidate_graph_sha256": actual_graph_hash,
        "embedded_config_name": config.get("name"),
        "preset_binding": {
            "requested": approved_preset,
            "status": "MATCHED" if approved_preset else "NOT_REQUESTED",
        },
        "n": n,
        "edge_count": len(present_pairs),
        "degree_minmax": [min(degrees), max(degrees)],
        "triangle_count": len(triangles),
        "nontrivial_ambient_maximal_clique_count": len(maximal),
        "maximum_clique_size": max(map(len, maximal), default=1),
        "checks": checks,
        "formula_manifest": formula_manifest or None,
    }
    if not solve:
        return result

    adm_sat, adm_model = solve_cnf(adm_clauses, adm_vars)
    if adm_sat:
        witness = [v for v in range(n) if v + 1 in adm_model][:target]
        result.update(
            status="FAILED_ADMISSIBLE_SET_EXISTS",
            admissible_set_witness=witness,
        )
        return result
    checks.append(f"Glucose UNSAT: no admissible set of size at least {target}")

    color_sat, color_model = solve_cnf(color_clauses, color_vars)
    if color_sat:
        coloring = [
            {"edge": list(pair), "color": "red" if i + 1 in color_model else "blue"}
            for i, pair in enumerate(present_pairs)
        ]
        result.update(
            status="FAILED_NONARROWING_COLORING_EXISTS",
            coloring_witness=coloring,
        )
        return result
    checks.append("Glucose UNSAT: no red/blue triangle-avoiding coloring of present edges")
    result["status"] = "VERIFIED_BY_INDEPENDENT_ENCODING_NO_PROOF_CERTIFICATES"
    result["warning"] = (
        "Both semantic formulas were UNSAT in Glucose, but proof certificates "
        "are still required for a proof-grade computational claim."
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--emit-cnf", type=Path)
    parser.add_argument("--no-solve", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--approved-preset",
        choices=sorted(load_approved_presets()),
        help="require the embedded config to exactly equal this cases.json preset",
    )
    args = parser.parse_args(argv)
    try:
        result = verify_candidate(
            args.candidate,
            emit_cnf=args.emit_cnf,
            solve=not args.no_solve,
            approved_preset=args.approved_preset,
        )
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        result = {
            "status": "INVALID_ARTIFACT",
            "candidate": str(args.candidate.resolve()),
            "error": f"{type(exc).__name__}: {exc}",
        }
    if args.report:
        atomic_write_json(args.report, result)
    print(json.dumps(with_content_hash(result), indent=2, sort_keys=True))
    return 0 if str(result["status"]).startswith("VERIFIED_") or result["status"] == "STRUCTURE_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
