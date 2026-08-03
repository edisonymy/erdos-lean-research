#!/usr/bin/env python3
"""Independent audit of three concrete HoG seeds cited by arXiv:2605.16542.

The primary checker uses its own graph6 parser, bitset Bron--Kerbosch, and
CaDiCaL exact-cardinality SAT.  NetworkX plus RC2 is used as a structurally
independent beta checker.  The 43-vertex graph is intentionally not put
through another unbounded arrowing run after two bounded attempts timed out.
"""

from __future__ import annotations

import hashlib
import json
import platform
import time
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix
from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2
from pysat.formula import IDPool, WCNF
from pysat.solvers import Solver


HERE = Path(__file__).resolve().parent
OUT = HERE / "audit_literature_seeds.result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_graph6(raw: bytes) -> list[int]:
    text = raw.strip()
    if text.startswith(b">>graph6<<"):
        text = text[len(b">>graph6<<") :]
    values = [byte - 63 for byte in text]
    if not values or any(not 0 <= value <= 63 for value in values):
        raise ValueError("invalid graph6 alphabet")
    if values[0] <= 62:
        n, offset = values[0], 1
    elif len(values) >= 4 and values[1] <= 62:
        n = (values[1] << 12) | (values[2] << 6) | values[3]
        offset = 4
    else:
        if len(values) < 8:
            raise ValueError("truncated long graph6 header")
        n = 0
        for value in values[2:8]:
            n = (n << 6) | value
        offset = 8
    bits = []
    for value in values[offset:]:
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    needed = n * (n - 1) // 2
    if len(bits) < needed:
        raise ValueError("truncated graph6 payload")
    adjacency = [0] * n
    cursor = 0
    # graph6's upper triangle is column-major.
    for high in range(1, n):
        for low in range(high):
            if bits[cursor]:
                adjacency[low] |= 1 << high
                adjacency[high] |= 1 << low
            cursor += 1
    return adjacency


def edges(adjacency: list[int]) -> list[tuple[int, int]]:
    return [
        (u, v)
        for u in range(len(adjacency))
        for v in range(u + 1, len(adjacency))
        if adjacency[u] >> v & 1
    ]


def triangles(adjacency: list[int]) -> list[tuple[int, int, int]]:
    found = []
    for a in range(len(adjacency)):
        for b in range(a + 1, len(adjacency)):
            if not (adjacency[a] >> b & 1):
                continue
            common = adjacency[a] & adjacency[b] & ~((1 << (b + 1)) - 1)
            while common:
                bit = common & -common
                common ^= bit
                found.append((a, b, bit.bit_length() - 1))
    return found


def maximal_clique_masks(adjacency: list[int]) -> list[int]:
    result: list[int] = []

    def bron_kerbosch(chosen: int, possible: int, excluded: int) -> None:
        if not possible and not excluded:
            if chosen.bit_count() >= 2:
                result.append(chosen)
            return
        union = possible | excluded
        if union:
            pivot = max(
                (v for v in range(len(adjacency)) if union >> v & 1),
                key=lambda v: (possible & adjacency[v]).bit_count(),
            )
            candidates = possible & ~adjacency[pivot]
        else:
            candidates = possible
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            vertex = bit.bit_length() - 1
            bron_kerbosch(
                chosen | bit,
                possible & adjacency[vertex],
                excluded & adjacency[vertex],
            )
            possible ^= bit
            excluded |= bit

    bron_kerbosch(0, (1 << len(adjacency)) - 1, 0)
    return sorted(result, key=lambda mask: (mask.bit_count(), mask))


def arrow_decision(adjacency: list[int], solver_name: str) -> tuple[bool, list[int] | None]:
    edge_list = edges(adjacency)
    index = {edge: i + 1 for i, edge in enumerate(edge_list)}
    clauses = []
    for a, b, c in triangles(adjacency):
        variables = [index[(a, b)], index[(a, c)], index[(b, c)]]
        clauses.extend((variables, [-x for x in variables]))
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    if model is not None:
        positive = {literal for literal in model if literal > 0}
        for a, b, c in triangles(adjacency):
            colors = [index[(a, b)] in positive, index[(a, c)] in positive, index[(b, c)] in positive]
            assert not (all(colors) or not any(colors))
    return not sat, model


def delete_vertex(adjacency: list[int], removed: int) -> list[int]:
    keep = [vertex for vertex in range(len(adjacency)) if vertex != removed]
    relabel = {old: new for new, old in enumerate(keep)}
    result = [0] * len(keep)
    for old_u in keep:
        for old_v in keep:
            if old_u < old_v and adjacency[old_u] >> old_v & 1:
                u, v = relabel[old_u], relabel[old_v]
                result[u] |= 1 << v
                result[v] |= 1 << u
    return result


def size_model(adjacency: list[int], clique_masks: list[int], target: int) -> list[int] | None:
    n = len(adjacency)
    clauses = [
        [-(v + 1) for v in range(n) if mask >> v & 1]
        for mask in clique_masks
    ]
    pool = IDPool(start_from=n + 1)
    clauses.extend(
        CardEnc.atleast(
            lits=list(range(1, n + 1)),
            bound=target,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
    )
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None
        positive = {literal for literal in solver.get_model() if 1 <= literal <= n}
    witness = [v for v in range(n) if v + 1 in positive]
    assert len(witness) >= target
    assert all(mask & sum(1 << v for v in witness) != mask for mask in clique_masks)
    return witness


def beta_rc2(adjacency: list[int], nx_cliques: list[list[int]]) -> tuple[int, list[int]]:
    formula = WCNF()
    for clique in nx_cliques:
        formula.append([-(v + 1) for v in clique])
    for v in range(len(adjacency)):
        formula.append([v + 1], weight=1)
    with RC2(formula, solver="cadical195") as rc2:
        model = rc2.compute()
    positive = {literal for literal in model if 1 <= literal <= len(adjacency)}
    witness = [v for v in range(len(adjacency)) if v + 1 in positive]
    return len(witness), witness


def beta_milp(adjacency: list[int], clique_masks: list[int]) -> tuple[int, list[int], dict]:
    """Compute beta through the complementary minimum clique transversal."""
    n = len(adjacency)
    rows = []
    cols = []
    data = []
    for row, mask in enumerate(clique_masks):
        for vertex in range(n):
            if mask >> vertex & 1:
                rows.append(row)
                cols.append(vertex)
                data.append(1.0)
    matrix = csr_matrix((data, (rows, cols)), shape=(len(clique_masks), n))
    result = milp(
        c=np.ones(n),
        integrality=np.ones(n),
        bounds=Bounds(np.zeros(n), np.ones(n)),
        constraints=LinearConstraint(matrix, np.ones(len(clique_masks)), np.full(len(clique_masks), np.inf)),
        options={"presolve": True},
    )
    assert result.success and result.x is not None
    transversal = {v for v, value in enumerate(result.x) if value > 0.5}
    assert all(any(v in transversal for v in range(n) if mask >> v & 1) for mask in clique_masks)
    witness = [v for v in range(n) if v not in transversal]
    return len(witness), witness, {
        "status": int(result.status),
        "message": result.message,
        "minimum_transversal": len(transversal),
        "mip_gap": getattr(result, "mip_gap", None),
        "mip_node_count": getattr(result, "mip_node_count", None),
    }


def basic_record(path: Path) -> tuple[list[int], nx.Graph, list[int], list[list[int]], dict]:
    adjacency = parse_graph6(path.read_bytes())
    graph = nx.Graph()
    graph.add_nodes_from(range(len(adjacency)))
    graph.add_edges_from(edges(adjacency))
    custom = maximal_clique_masks(adjacency)
    nx_cliques = sorted(
        (sorted(clique) for clique in nx.find_cliques(graph) if len(clique) >= 2),
        key=lambda clique: (len(clique), clique),
    )
    nx_masks = sorted(
        (sum(1 << v for v in clique) for clique in nx_cliques),
        key=lambda mask: (mask.bit_count(), mask),
    )
    assert custom == nx_masks
    degree_values = [mask.bit_count() for mask in adjacency]
    record = {
        "file": path.name,
        "sha256": sha256(path),
        "graph6": path.read_text(encoding="ascii").strip(),
        "n": len(adjacency),
        "m": len(edges(adjacency)),
        "minimum_degree": min(degree_values),
        "maximum_degree": max(degree_values),
        "degree_distribution": dict(sorted(Counter(map(str, degree_values)).items())),
        "triangle_count": len(triangles(adjacency)),
        "maximal_clique_count": len(custom),
        "maximal_clique_size_distribution": dict(
            sorted(Counter(str(mask.bit_count()) for mask in custom).items())
        ),
        "clique_checkers_agree": True,
    }
    return adjacency, graph, custom, nx_cliques, record


def audited_beta(adjacency: list[int], custom: list[int], nx_cliques: list[list[int]]) -> dict:
    beta, witness_b = beta_rc2(adjacency, nx_cliques)
    beta_a, witness_a, milp_audit = beta_milp(adjacency, custom)
    assert beta_a == beta
    return {
        "beta": beta,
        "checker_a": "custom graph6 + bitset Bron-Kerbosch + SciPy/HiGHS binary MILP minimum clique transversal",
        "checker_a_witness": witness_a,
        "checker_a_optimization": milp_audit,
        "checker_b": "NetworkX find_cliques + RC2 weighted MaxSAT",
        "checker_b_witness": witness_b,
    }


def main() -> int:
    started = time.time()
    records = {}
    for graph_id in (51288, 51177, 51171):
        path = HERE / f"HoG_{graph_id}.g6"
        adjacency, _, custom, nx_cliques, record = basic_record(path)
        if graph_id in (51288, 51177):
            record.update(audited_beta(adjacency, custom, nx_cliques))
            arrow_a, model_a = arrow_decision(adjacency, "cadical195")
            arrow_b, model_b = arrow_decision(adjacency, "glucose4")
            assert arrow_a == arrow_b
            record.update(
                {
                    "edge_arrows_3_3": arrow_a,
                    "arrow_checker_a": "CaDiCaL 1.9.5",
                    "arrow_checker_b": "Glucose 4",
                    "avoiding_coloring_exists": model_a is not None,
                    "avoiding_coloring_model_a": model_a,
                    "avoiding_coloring_model_b": model_b,
                }
            )
        else:
            beta_value, beta_witness, beta_milp_audit = beta_milp(adjacency, custom)
            nx_masks = [sum(1 << v for v in clique) for clique in nx_cliques]
            beta_sat_witness = size_model(adjacency, nx_masks, beta_value)
            beta_plus_one = size_model(adjacency, nx_masks, beta_value + 1)
            assert beta_sat_witness is not None and beta_plus_one is None
            vertex_deletion_audit = []
            for removed in range(len(adjacency)):
                reduced = delete_vertex(adjacency, removed)
                arrow_a, model_a = arrow_decision(reduced, "cadical195")
                arrow_b, model_b = arrow_decision(reduced, "glucose4")
                assert not arrow_a and not arrow_b and model_a is not None and model_b is not None
                vertex_deletion_audit.append(
                    {
                        "removed_vertex": removed,
                        "remaining_edges": len(edges(reduced)),
                        "cadical_positive_literal_count": sum(literal > 0 for literal in model_a),
                        "glucose_positive_literal_count": sum(literal > 0 for literal in model_b),
                    }
                )
            record.update(
                {
                    "edge_arrows_3_3": "PUBLISHED_CLAIM_NOT_INDEPENDENTLY_REPLAYED_IN_PULSE",
                    "bounded_replay_attempts": [
                        {"solver": "Kissat 4.0.4", "limit_seconds": 120, "status": "TIMEOUT"},
                        {"solver": "CaDiCaL 1.9.5", "limit_seconds": 60, "status": "TIMEOUT"},
                    ],
                    "beta": beta_value,
                    "beta_checker_a": "custom graph6 + bitset Bron-Kerbosch + SciPy/HiGHS binary MILP",
                    "beta_checker_a_witness": beta_witness,
                    "beta_checker_a_optimization": beta_milp_audit,
                    "beta_checker_b": "NetworkX find_cliques + CaDiCaL exact-cardinality SAT at beta and beta+1",
                    "beta_checker_b_witness": beta_sat_witness,
                    "beta_checker_b_beta_plus_one_unsat": True,
                    "beta_degree_lower_bound": record["maximum_degree"],
                    "all_43_vertex_deleted_subgraphs_nonarrowing": True,
                    "vertex_deletion_checkers": ["CaDiCaL 1.9.5", "Glucose 4"],
                    "vertex_deletion_audit": vertex_deletion_audit,
                }
            )
        records[str(graph_id)] = record

    records["51288"].update(
        {
            "H_n": 4,
            "H_basis": "R(3,4)=9 <= 11 < R(3,5)=14",
            "gap_beta_minus_H": records["51288"]["beta"] - 4,
            "eligibility": "edge-arrowing but far above #151 target",
        }
    )
    records["51171"].update(
        {
            "H_n": 10,
            "H_basis": "R(3,10)<=41 <= 43 < R(3,11), with R(3,11)>=47",
            "gap_beta_minus_H": records["51171"]["beta"] - 10,
            "gap_beta_minus_counterexample_ceiling_9": records["51171"]["beta"] - 9,
            "eligibility": "published edge-arrowing seed, exactly beta=25 and far outside #151 target",
        }
    )
    records["51177"].update(
        {
            "H_n": "12_OR_13",
            "H_basis": "current bounds leave R(3,13) unresolved across n=63",
            "gap_beta_minus_H_lower_bound": records["51177"]["beta"] - 13,
            "eligibility": "INELIGIBLE: independently has a triangle-avoiding edge 2-coloring; paper claims only vertex-arrowing",
        }
    )
    result = {
        "schema": "erdos151-noncayley-literature-seeds-audit-v1",
        "primary_paper": "https://arxiv.org/abs/2605.16542",
        "house_of_graphs_api": "https://houseofgraphs.org/api/download_graph",
        "records": records,
        "runtime_seconds": time.time() - started,
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "claim_boundary": "No full or one-away #151 candidate; exact beta claims apply only to HoG 51288 and 51177.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: {k: value for k, value in row.items() if k in {"n", "m", "beta", "beta_lower_bound", "H_n", "edge_arrows_3_3", "eligibility"}} for key, row in records.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
