#!/usr/bin/env python3
"""Exhaustive small-order audit of the successor matching-of-three gate."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from pysat.formula import IDPool
from pysat.solvers import Cadical195

from cegar_face_matching3 import (
    actual_maximal_edges,
    add_matching_gate,
    install_maximal_witnesses,
    validate_matching_gate,
)


def build_gate(n: int):
    pool = IDPool()
    edge_variables = {
        edge: pool.id(("audit-edge",) + edge)
        for edge in itertools.combinations(range(n), 2)
    }

    def ev(u: int, v: int) -> int:
        return edge_variables[(min(u, v), max(u, v))]

    solver = Cadical195()
    maximal, maximal_stats = install_maximal_witnesses(solver, pool, n, ev)
    selected, matching_stats = add_matching_gate(
        solver, pool, n, maximal, required=3
    )
    return solver, pool, edge_variables, maximal, selected, {
        **maximal_stats,
        **matching_stats,
    }


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[int]:
    result = [0] * n
    for u, v in edges:
        result[u] |= 1 << v
        result[v] |= 1 << u
    return result


def has_three_matching(edges: list[tuple[int, int]]) -> bool:
    return any(
        len({vertex for edge in chosen for vertex in edge}) == 6
        for chosen in itertools.combinations(edges, 3)
    )


def validate_sat_control(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    assert payload["result"] == "SAT-CANDIDATE"
    n, h = payload["n"], payload["h"]
    graph_edges = {tuple(edge) for edge in payload["edge_list"]}
    adj = adjacency(n, graph_edges)
    degrees = [bits.bit_count() for bits in adj]
    assert max(degrees, default=0) <= h - 1
    assert all(
        not all(tuple(sorted(edge)) in graph_edges for edge in itertools.combinations(four, 2))
        for four in itertools.combinations(range(n), 4)
    )
    maximal_edges = actual_maximal_edges(adj)
    assert has_three_matching(maximal_edges)
    admissible = []
    for subset in itertools.combinations(range(n), h):
        subset_set = set(subset)
        contains_maximal = any(set(edge) <= subset_set for edge in maximal_edges)
        contains_triangle = any(
            all(tuple(sorted(edge)) in graph_edges for edge in itertools.combinations(triple, 2))
            for triple in itertools.combinations(subset, 3)
        )
        if not contains_maximal and not contains_triangle:
            admissible.append(subset)
    assert not admissible
    selected_edges = {
        tuple(edge)
        for edge in payload["matching_gate_validation"]["selected_maximal_edges"]
    }
    assert selected_edges <= set(maximal_edges)
    assert len({vertex for edge in selected_edges for vertex in edge}) == 2 * len(selected_edges)
    assert len(selected_edges) >= 3
    return {
        "path": path.name,
        "status": "PASS",
        "n": n,
        "h": h,
        "degree_sequence": sorted(degrees),
        "maximal_edge_count": len(maximal_edges),
        "admissible_h_set_count": len(admissible),
        "selected_matching_size": len(selected_edges),
    }


def main() -> None:
    n = 6
    all_edges = list(itertools.combinations(range(n), 2))
    solver, pool, edge_vars, maximal, selected, gate_stats_n6 = build_gate(n)
    sat_graphs = 0
    expected_sat_graphs = 0
    for mask in range(1 << len(all_edges)):
        graph_edges = {
            edge for index, edge in enumerate(all_edges) if (mask >> index) & 1
        }
        adj = adjacency(n, graph_edges)
        maximal_edges = actual_maximal_edges(adj)
        expected = has_three_matching(maximal_edges)
        expected_sat_graphs += int(expected)
        assumptions = [
            edge_vars[edge] if edge in graph_edges else -edge_vars[edge]
            for edge in all_edges
        ]
        satisfiable = solver.solve(assumptions=assumptions)
        assert satisfiable == expected, (mask, maximal_edges, expected, satisfiable)
        if satisfiable:
            sat_graphs += 1
            positive = {literal for literal in solver.get_model() if literal > 0}
            validation = validate_matching_gate(adj, positive, maximal, selected)
            assert validation["actual_maximal_matching_size"] == 3
    assert sat_graphs == expected_sat_graphs

    controls = {
        "three_disjoint_edges": {(0, 1), (2, 3), (4, 5)},
        "two_disjoint_edges": {(0, 1), (2, 3)},
        "star": {(0, vertex) for vertex in range(1, 6)},
        "two_triangles": {
            (0, 1),
            (0, 2),
            (1, 2),
            (3, 4),
            (3, 5),
            (4, 5),
        },
        "triangular_prism": {
            (0, 1),
            (1, 2),
            (0, 2),
            (3, 4),
            (4, 5),
            (3, 5),
            (0, 3),
            (1, 4),
            (2, 5),
        },
    }
    control_records = []
    for name, graph_edges in controls.items():
        adj = adjacency(n, graph_edges)
        maximal_edges = actual_maximal_edges(adj)
        expected = has_three_matching(maximal_edges)
        assumptions = [
            edge_vars[edge] if edge in graph_edges else -edge_vars[edge]
            for edge in all_edges
        ]
        satisfiable = solver.solve(assumptions=assumptions)
        assert satisfiable == expected
        control_records.append(
            {
                "name": name,
                "expected": "SAT" if expected else "UNSAT",
                "solver": "SAT" if satisfiable else "UNSAT",
                "maximal_edges": [list(edge) for edge in maximal_edges],
            }
        )

    # Measure only the successor gate at production order; do not solve n=50.
    solver50, pool50, _edges50, _maximal50, _selected50, gate_stats_n50 = build_gate(50)
    del solver50
    end_to_end = []
    control_dir = Path(__file__).resolve().parent
    sat_path = control_dir / "control_matching3_n6_h4.json"
    unsat_path = control_dir / "control_matching3_n10_h4.json"
    if sat_path.is_file():
        end_to_end.append(validate_sat_control(sat_path))
    if unsat_path.is_file():
        unsat_payload = json.loads(unsat_path.read_text(encoding="utf-8-sig"))
        assert unsat_payload["summary"]["result"] == "UNSAT"
        end_to_end.append(
            {
                "path": unsat_path.name,
                "status": "PASS",
                "n": unsat_payload["summary"]["n"],
                "h": unsat_payload["summary"]["h"],
                "solver_result": "UNSAT",
                "rounds": unsat_payload["summary"]["rounds"],
                "claim_boundary": "regression control, not a proof-certified theorem result",
            }
        )
    payload = {
        "schema": "erdos151-cegar-matching3-gate-audit-v1",
        "status": "PASS",
        "semantics": (
            "m_uv is a one-way maximal-edge witness; separate s_uv variables "
            "select at least three pairwise vertex-disjoint witnesses"
        ),
        "exhaustive_n6": {
            "graphs_checked": 1 << len(all_edges),
            "expected_sat_graphs": expected_sat_graphs,
            "solver_sat_graphs": sat_graphs,
            "equivalence": "SAT iff the actual maximal-edge graph has matching number 3",
        },
        "controls": control_records,
        "end_to_end_controls": end_to_end,
        "gate_stats_n6": gate_stats_n6,
        "gate_stats_n50": gate_stats_n50,
        "claim_boundary": (
            "gate-only audit; production CEGAR outcomes retain the original "
            "SAT-model and UNSAT-proof certification requirements"
        ),
    }
    output = Path(__file__).with_name("audit_cegar_matching3_gate.result.json")
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
