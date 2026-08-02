#!/usr/bin/env python3
"""Bounded independent fast-path for a v5 F4_N41 candidate.

This module intentionally imports neither the fixed-clique CEGAR search nor
any existing candidate verifier.  It reads the emitted JSON envelope itself,
reconstructs the graph twice (from the packed vector and the raw edge list),
and only signs off a claim when all bounded exact checks finish.

The intended input is a schema-5 ``fixed_clique_cegar_candidate`` for F4_N41.
It is a *screening verifier*: SAT/UNSAT solver conclusions are independently
cross-checked when python-sat is installed, but no proof certificate is made.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


N = 41
TARGET = 10
PAIR_ORDER = tuple(itertools.combinations(range(N), 2))
F4_CONFIG = {
    "name": "F4_N41",
    "n": 41,
    "fixed_clique_size": 4,
    "forbidden_clique_size": 5,
    "degree_min": 5,
    "degree_max": 9,
    "target_set_size": 10,
    "scope": (
        "labelled order-41 graphs containing the fixed K4 on vertices 0..3, "
        "containing no K5, satisfying |Z_c|<=22, with complete-forbidden then "
        "arrowing-first, residual admissible-7, generic-global separation"
    ),
    "forbidden_mode": "lazy",
    "admissibility_batch_size": 8,
    "residual_beta_bound": 22,
    "residual_admissibility_target_size": 7,
}
GRAPH_DOMAIN = b"erdos151-fixed-clique-graph-v1\0"


class CandidateError(ValueError):
    pass


class LimitReached(RuntimeError):
    pass


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def graph_hash(n: int, packed: bytes) -> str:
    return sha256(GRAPH_DOMAIN + n.to_bytes(4, "big") + packed)


def edge_list_hash(edges: Sequence[tuple[int, int]]) -> str:
    return sha256(canonical_json([[u, v] for u, v in edges]))


def unpack_edge_vector(encoded: object, n: int) -> tuple[tuple[int, int], ...]:
    if not isinstance(encoded, str):
        raise CandidateError("graph.edges_hex must be a hexadecimal string")
    try:
        raw = bytes.fromhex(encoded)
    except ValueError as exc:
        raise CandidateError("graph.edges_hex is not hexadecimal") from exc
    count = n * (n - 1) // 2
    if len(raw) != (count + 7) // 8:
        raise CandidateError("packed edge vector length is wrong")
    if count % 8 and raw[-1] >> (count % 8):
        raise CandidateError("packed edge vector has nonzero unused bits")
    return tuple(pair for i, pair in enumerate(itertools.combinations(range(n), 2)) if raw[i >> 3] & (1 << (i & 7)))


def parse_edge_list(value: object, n: int) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, list):
        raise CandidateError("graph.edges must be a list")
    edges: list[tuple[int, int]] = []
    for row in value:
        if not isinstance(row, list) or len(row) != 2:
            raise CandidateError("raw edge record is malformed")
        u, v = row
        if type(u) is not int or type(v) is not int or not 0 <= u < v < n:
            raise CandidateError(f"raw edge is noncanonical or out of range: {row!r}")
        edges.append((u, v))
    if edges != sorted(edges) or len(edges) != len(set(edges)):
        raise CandidateError("raw edge list must be sorted and duplicate-free")
    return tuple(edges)


def build_adjacency(edges: Iterable[tuple[int, int]], n: int = N) -> tuple[int, ...]:
    masks = [0] * n
    for u, v in edges:
        masks[u] |= 1 << v
        masks[v] |= 1 << u
    return tuple(masks)


def vertices(mask: int) -> Iterable[int]:
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def is_clique(mask: int, adjacency: Sequence[int]) -> bool:
    for vertex in vertices(mask):
        if (mask ^ (1 << vertex)) & ~adjacency[vertex]:
            return False
    return True


def enumerate_ambient_maximal_cliques(adjacency: Sequence[int]) -> tuple[int, ...]:
    """Enumerate all ambient maximal cliques via local higher-neighborhoods.

    Under the F4 degree cap this examines at most 41 * 2^9 local subsets.
    It is deliberately not Bron--Kerbosch and not copied from the CEGAR lane.
    """
    n = len(adjacency)
    all_vertices = (1 << n) - 1
    found: set[int] = set()
    for root in range(n):
        higher = [v for v in vertices(adjacency[root]) if v > root]
        for selection in range(1, 1 << len(higher)):
            mask = 1 << root
            for index, vertex in enumerate(higher):
                if selection & (1 << index):
                    mask |= 1 << vertex
            if not is_clique(mask, adjacency):
                continue
            common = all_vertices
            for vertex in vertices(mask):
                common &= adjacency[vertex]
            if common == 0:
                found.add(mask)
    return tuple(sorted(found, key=lambda item: (item.bit_count(), item)))


def enumerate_triangles(adjacency: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    result: list[tuple[int, int, int]] = []
    for a in range(len(adjacency)):
        for b in vertices(adjacency[a] & ~((1 << (a + 1)) - 1)):
            for c in vertices(adjacency[a] & adjacency[b] & ~((1 << (b + 1)) - 1)):
                result.append((a, b, c))
    return tuple(result)


@dataclass
class Budget:
    limit: int
    nodes: int = 0

    def tick(self) -> None:
        self.nodes += 1
        if self.limit and self.nodes > self.limit:
            raise LimitReached(f"node limit {self.limit} reached")


def independent_set_of_size(adjacency: Sequence[int], target: int, budget: Budget) -> tuple[int, ...] | None:
    """Exact include/exclude search for an independent set of exactly target."""
    n = len(adjacency)

    def search(chosen: int, available: int) -> int | None:
        budget.tick()
        if chosen.bit_count() == target:
            return chosen
        if chosen.bit_count() + available.bit_count() < target:
            return None
        # Branch on a locally most constraining remaining vertex.
        candidate = max(vertices(available), key=lambda v: (available & adjacency[v]).bit_count())
        chosen_result = search(chosen | (1 << candidate), available & ~adjacency[candidate] & ~(1 << candidate))
        if chosen_result is not None:
            return chosen_result
        return search(chosen, available & ~(1 << candidate))

    answer = search(0, (1 << n) - 1)
    return tuple(vertices(answer)) if answer is not None else None


def small_hitting_set(cliques: Sequence[int], n: int, maximum: int, budget: Budget) -> tuple[int, ...] | None:
    """Exact B&B for a clique transversal of size at most ``maximum``.

    Its complement is an admissible set.  Therefore a hit is equivalent to
    beta(G) >= n - maximum; exhaustive failure proves beta(G) <= n-maximum-1.
    """
    unique = tuple(sorted(set(cliques), key=lambda mask: (mask.bit_count(), mask)))

    def disjoint_lower_bound(unhit: Sequence[int]) -> int:
        used = 0
        count = 0
        for clique in unhit:
            if clique & used == 0:
                used |= clique
                count += 1
        return count

    def search(chosen: int, unhit: tuple[int, ...]) -> int | None:
        budget.tick()
        if not unhit:
            return chosen
        if chosen.bit_count() >= maximum:
            return None
        if chosen.bit_count() + disjoint_lower_bound(unhit) > maximum:
            return None
        clique = min(unhit, key=lambda mask: (mask.bit_count(), mask))
        # Higher occurrence first gives a good transversal witness quickly.
        frequency = {v: sum(bool(mask & (1 << v)) for mask in unhit) for v in vertices(clique)}
        for vertex in sorted(frequency, key=lambda v: (-frequency[v], v)):
            answer = search(
                chosen | (1 << vertex),
                tuple(mask for mask in unhit if not (mask & (1 << vertex))),
            )
            if answer is not None:
                return answer
        return None

    answer = search(0, unique)
    return tuple(vertices(answer)) if answer is not None else None


def dpll(clauses: Sequence[Sequence[int]], variable_count: int, budget: Budget) -> tuple[bool, list[int] | None]:
    """A compact independent SAT decision engine with exhaustive DPLL search."""
    frozen = tuple(tuple(clause) for clause in clauses)

    def propagate(assignment: list[int]) -> bool:
        changed = True
        while changed:
            changed = False
            for clause in frozen:
                unassigned = 0
                unit = 0
                satisfied = False
                for literal in clause:
                    value = assignment[abs(literal)]
                    if value == 0:
                        unassigned += 1
                        unit = literal
                    elif (value > 0) == (literal > 0):
                        satisfied = True
                        break
                if satisfied:
                    continue
                if unassigned == 0:
                    return False
                if unassigned == 1:
                    variable, value = abs(unit), 1 if unit > 0 else -1
                    if assignment[variable] and assignment[variable] != value:
                        return False
                    if assignment[variable] == 0:
                        assignment[variable] = value
                        changed = True
        return True

    def search(assignment: list[int]) -> list[int] | None:
        budget.tick()
        assignment = assignment[:]
        if not propagate(assignment):
            return None
        scores = [0] * (variable_count + 1)
        signs = [0] * (variable_count + 1)
        unresolved = False
        for clause in frozen:
            if any(assignment[abs(literal)] and (assignment[abs(literal)] > 0) == (literal > 0) for literal in clause):
                continue
            unresolved = True
            for literal in clause:
                if assignment[abs(literal)] == 0:
                    scores[abs(literal)] += 1
                    signs[abs(literal)] += 1 if literal > 0 else -1
        if not unresolved:
            return assignment
        variable = max((v for v in range(1, variable_count + 1) if assignment[v] == 0), key=lambda v: (scores[v], -v))
        first = 1 if signs[variable] >= 0 else -1
        for value in (first, -first):
            next_assignment = assignment[:]
            next_assignment[variable] = value
            answer = search(next_assignment)
            if answer is not None:
                return answer
        return None

    model = search([0] * (variable_count + 1))
    return model is not None, model


def triangle_coloring_cnf(edges: Sequence[tuple[int, int]], triangles: Sequence[tuple[int, int, int]]) -> tuple[list[list[int]], dict[tuple[int, int], int]]:
    ids = {edge: i + 1 for i, edge in enumerate(edges)}
    clauses: list[list[int]] = []
    for a, b, c in triangles:
        tri = [ids[(a, b)], ids[(a, c)], ids[(b, c)]]
        clauses.extend((tri, [-literal for literal in tri]))
    return clauses, ids


def pysat_crosscheck(kind: str, n: int, cliques: Sequence[int], edges: Sequence[tuple[int, int]], triangles: Sequence[tuple[int, int, int]]) -> dict[str, object]:
    """A separately implemented SAT encoding, optional at runtime."""
    try:
        from pysat.card import CardEnc, EncType  # type: ignore[import-not-found]
        from pysat.solvers import Glucose4  # type: ignore[import-not-found]
    except ImportError:
        return {"available": False, "status": "NOT_AVAILABLE"}
    if kind == "admissible_10":
        clauses = [[-(v + 1) for v in vertices(clique)] for clique in cliques]
        card = CardEnc.equals(list(range(1, n + 1)), bound=TARGET, top_id=n, encoding=EncType.seqcounter)
        clauses.extend(card.clauses)
        variable_count = card.nv
    elif kind == "triangle_coloring":
        clauses, ids = triangle_coloring_cnf(edges, triangles)
        variable_count = len(ids)
    else:
        raise ValueError(kind)
    with Glucose4(bootstrap_with=clauses) as solver:
        sat = solver.solve()
    return {"available": True, "status": "SAT" if sat else "UNSAT", "variables": variable_count, "clauses": len(clauses), "solver": "Glucose4"}


def read_v5_candidate(path: Path) -> tuple[dict[str, object], tuple[tuple[int, int], ...], tuple[int, ...], dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CandidateError("candidate root must be an object")
    body = dict(data)
    stored_content_hash = body.pop("content_sha256", None)
    if stored_content_hash != sha256(canonical_json(body)):
        raise CandidateError("candidate content_sha256 mismatch")
    if data.get("schema_version") != 5 or data.get("artifact_type") != "fixed_clique_cegar_candidate":
        raise CandidateError("not a schema-5 fixed_clique_cegar candidate")
    if data.get("config") != F4_CONFIG:
        raise CandidateError("candidate is not an exact F4_N41 v5 configuration")
    graph = data.get("graph")
    if not isinstance(graph, dict) or graph.get("n") != N:
        raise CandidateError("candidate graph is not order 41")
    raw_edges = parse_edge_list(graph.get("edges"), N)
    packed_edges = unpack_edge_vector(graph.get("edges_hex"), N)
    if raw_edges != packed_edges:
        raise CandidateError("raw edge list and packed edge vector disagree")
    packed = bytes.fromhex(str(graph["edges_hex"]))
    if graph.get("graph_sha256") != graph_hash(N, packed):
        raise CandidateError("graph_sha256 mismatch")
    if graph.get("edge_count") != len(raw_edges):
        raise CandidateError("edge_count mismatch")
    adjacency = build_adjacency(raw_edges)
    degrees = [mask.bit_count() for mask in adjacency]
    if graph.get("degrees") != degrees:
        raise CandidateError("recorded degree list disagrees with reconstructed graph")
    if graph.get("triangle_count") != len(enumerate_triangles(adjacency)):
        raise CandidateError("recorded triangle count disagrees with reconstructed graph")
    provenance = {
        "candidate_file_sha256": file_sha256(path),
        "candidate_content_sha256": stored_content_hash,
        "graph_sha256": graph["graph_sha256"],
        "raw_edge_list_sha256": edge_list_hash(raw_edges),
        "packed_vector_sha256": sha256(packed),
    }
    return data, raw_edges, adjacency, provenance


def make_report(path: Path, *, node_limit: int, include_sat_crosscheck: bool) -> dict[str, object]:
    report: dict[str, object] = {
        "schema": "erdos151-v5-f4-candidate-fastpath-v1",
        "checker_file_sha256": file_sha256(Path(__file__)),
        "candidate": str(path.resolve()),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": (
            "A SIGNED_OFF_SCREENING result is an exact bounded reconstruction and "
            "decision result under this implementation. It is not a proof-grade "
            "computational certificate: no DRAT/LRAT proofs are emitted."
        ),
        "limits": {"per_decision_node_limit": node_limit, "n": N, "maximum_local_clique_subsets": N * (1 << 9)},
    }
    try:
        _data, edges, adjacency, provenance = read_v5_candidate(path)
    except (OSError, json.JSONDecodeError, CandidateError, TypeError, KeyError) as exc:
        report.update(status="REJECTED_ARTIFACT", signed_off=False, error=f"{type(exc).__name__}: {exc}")
        report["report_content_sha256"] = sha256(canonical_json(report))
        return report

    degrees = [mask.bit_count() for mask in adjacency]
    fixed_k4 = all(adjacency[u] & (1 << v) for u, v in itertools.combinations(range(4), 2))
    base_checks = {
        "order_41": len(adjacency) == N,
        "simple_canonical_edges": True,
        "raw_and_packed_reconstruction_agree": True,
        "degree_5_to_9": min(degrees) >= 5 and max(degrees) <= 9,
        "fixed_K4_0_1_2_3": fixed_k4,
    }
    report.update(provenance=provenance, edge_count=len(edges), degree_sequence=degrees, degree_min=max(0, min(degrees)), degree_max=max(degrees), structural_checks=base_checks)
    if not all(base_checks.values()):
        report.update(status="REJECTED_STRUCTURE", signed_off=False, claim_boundary="Structural gate failed; semantic decision checks were deliberately not run.")
        report["report_content_sha256"] = sha256(canonical_json(report))
        return report

    cliques = enumerate_ambient_maximal_cliques(adjacency)
    triangles = enumerate_triangles(adjacency)
    omega = max((mask.bit_count() for mask in cliques), default=1)
    report.update(
        ambient_maximal_clique_count=len(cliques),
        nontrivial_ambient_maximal_clique_count=sum(mask.bit_count() >= 2 for mask in cliques),
        triangle_count=len(triangles),
        omega=omega,
        clique_checks={"all_ambient_inclusion_maximal": True, "omega_exactly_4": omega == 4},
    )
    if omega != 4:
        report.update(status="REJECTED_CLIQUE", signed_off=False)
        report["report_content_sha256"] = sha256(canonical_json(report))
        return report

    outcomes: dict[str, object] = {}
    try:
        alpha_budget = Budget(node_limit)
        independent = independent_set_of_size(adjacency, TARGET, alpha_budget)
        outcomes["alpha_at_most_9"] = {"status": "UNSAT" if independent is None else "SAT", "nodes": alpha_budget.nodes, "independent_10_witness": list(independent) if independent else None}

        beta_budget = Budget(node_limit)
        transversal = small_hitting_set(tuple(mask for mask in cliques if mask.bit_count() >= 2), N, N - TARGET, beta_budget)
        outcomes["beta_at_most_9_bnb"] = {"status": "UNSAT" if transversal is None else "SAT", "nodes": beta_budget.nodes, "clique_transversal_at_most_31": list(transversal) if transversal else None}

        color_budget = Budget(node_limit)
        color_clauses, color_ids = triangle_coloring_cnf(edges, triangles)
        colorable, model = dpll(color_clauses, len(color_ids), color_budget)
        color_witness = None
        if colorable and model is not None:
            color_witness = [[u, v, "red" if model[var] > 0 else "blue"] for (u, v), var in sorted(color_ids.items())]
        outcomes["edge_arrows_3_3_dpll"] = {"status": "SAT" if colorable else "UNSAT", "nodes": color_budget.nodes, "triangle_avoiding_coloring": color_witness}
    except LimitReached as exc:
        report.update(status="INCONCLUSIVE_NODE_LIMIT", signed_off=False, decisions=outcomes, error=str(exc))
        report["report_content_sha256"] = sha256(canonical_json(report))
        return report

    if include_sat_crosscheck:
        outcomes["beta_at_most_9_sat_crosscheck"] = pysat_crosscheck("admissible_10", N, cliques, edges, triangles)
        outcomes["edge_arrows_3_3_sat_crosscheck"] = pysat_crosscheck("triangle_coloring", N, cliques, edges, triangles)
    report["decisions"] = outcomes
    primary_ok = (
        outcomes["alpha_at_most_9"]["status"] == "UNSAT"
        and outcomes["beta_at_most_9_bnb"]["status"] == "UNSAT"
        and outcomes["edge_arrows_3_3_dpll"]["status"] == "UNSAT"
    )
    crosschecks = [outcomes.get("beta_at_most_9_sat_crosscheck"), outcomes.get("edge_arrows_3_3_sat_crosscheck")]
    crosscheck_ok = all(item is None or item.get("status") in ("UNSAT", "NOT_AVAILABLE") for item in crosschecks if isinstance(item, dict))
    if primary_ok and crosscheck_ok:
        report.update(status="SIGNED_OFF_SCREENING", signed_off=True)
    elif primary_ok:
        report.update(status="CROSSCHECK_DISAGREEMENT", signed_off=False)
    else:
        report.update(status="REJECTED_SEMANTIC", signed_off=False)
    report["report_content_sha256"] = sha256(canonical_json(report))
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="schema-5 candidate JSON")
    parser.add_argument("--report", type=Path, help="write the machine-readable report")
    parser.add_argument("--node-limit", type=int, default=2_000_000, help="per exact decision; zero disables this guard")
    parser.add_argument("--no-sat-crosscheck", action="store_true", help="skip optional independently encoded Glucose checks")
    args = parser.parse_args(argv)
    if args.node_limit < 0:
        parser.error("--node-limit must be nonnegative")
    result = make_report(args.candidate.resolve(), node_limit=args.node_limit, include_sat_crosscheck=not args.no_sat_crosscheck)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if result["signed_off"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
