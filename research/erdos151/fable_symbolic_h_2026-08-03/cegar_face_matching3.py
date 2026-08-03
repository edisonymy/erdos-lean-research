"""Successor K4-free-face CEGAR with a global matching-of-three gate.

This is a separate successor to ``cegar_face.py``.  It does not mutate or
resume any inherited process or output.  The extra gate is sound for the
order-50, beta<=10 target by the audited maximal-edge matching theorem in
``n50_protected_core_max_2026-08-03/PURE_TRIANGULAR_CHROMATIC_GATE.md``.

Maximal-edge variables retain the inherited one-way witness semantics:
``m_uv`` true implies that ``uv`` is present and has no common neighbour.
Separate ``s_uv`` variables select a matching of at least three such
witnesses; no at-most constraint is placed on the cut-witness variables.

Usage:
    python -X utf8 cegar_face_matching3.py N H ROUNDS OUT.json [MIN_DEGREE]
"""

from __future__ import annotations

import itertools
import json
import random
import sys
import time
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195


def install_maximal_witnesses(solver, pool, n, ev):
    """Create all one-way maximal-edge witnesses used by cuts and the gate."""

    before = pool.top
    clauses = 0
    witnesses = {}
    for u, v in itertools.combinations(range(n), 2):
        witness = pool.id(("maximal-edge-witness", u, v))
        witnesses[(u, v)] = witness
        solver.add_clause([-witness, ev(u, v)])
        clauses += 1
        for x in range(n):
            if x in (u, v):
                continue
            solver.add_clause([-witness, -ev(u, x), -ev(v, x)])
            clauses += 1
    return witnesses, {
        "maximal_witness_variables": pool.top - before,
        "maximal_witness_clauses": clauses,
        "semantics": "m_uv implies uv is an edge with no common neighbour",
    }


def add_matching_gate(solver, pool, n, maximal_witnesses, required=3):
    """Require a selected matching of ``required`` maximal-edge witnesses."""

    if not 0 <= required <= n // 2:
        raise ValueError(required)
    before = pool.top
    clauses = 0
    selected = {}
    for edge, maximal in maximal_witnesses.items():
        selector = pool.id(("selected-maximal-edge",) + edge)
        selected[edge] = selector
        solver.add_clause([-selector, maximal])
        clauses += 1

    per_vertex_aux_before = pool.top
    per_vertex_clauses = 0
    for vertex in range(n):
        incident = [
            selector for edge, selector in selected.items() if vertex in edge
        ]
        cnf = CardEnc.atmost(
            incident, bound=1, vpool=pool, encoding=EncType.seqcounter
        )
        for clause in cnf.clauses:
            solver.add_clause(clause)
        per_vertex_clauses += len(cnf.clauses)
    per_vertex_aux = pool.top - per_vertex_aux_before

    global_aux_before = pool.top
    cnf = CardEnc.atleast(
        list(selected.values()),
        bound=required,
        vpool=pool,
        encoding=EncType.seqcounter,
    )
    for clause in cnf.clauses:
        solver.add_clause(clause)
    global_clauses = len(cnf.clauses)
    global_aux = pool.top - global_aux_before
    clauses += per_vertex_clauses + global_clauses
    return selected, {
        "required_matching_size": required,
        "selector_variables": len(selected),
        "per_vertex_atmost_aux_variables": per_vertex_aux,
        "global_atleast_aux_variables": global_aux,
        "matching_gate_variables": pool.top - before,
        "selector_bridge_clauses": len(selected),
        "per_vertex_atmost_clauses": per_vertex_clauses,
        "global_atleast_clauses": global_clauses,
        "matching_gate_clauses": clauses,
    }


def actual_maximal_edges(adj):
    n = len(adj)
    return [
        (u, v)
        for u, v in itertools.combinations(range(n), 2)
        if ((adj[u] >> v) & 1) and not (adj[u] & adj[v])
    ]


def validate_matching_gate(adj, positive, maximal_witnesses, selected):
    actual = set(actual_maximal_edges(adj))
    chosen = [edge for edge, var in selected.items() if var in positive]
    endpoints = [vertex for edge in chosen for vertex in edge]
    assert len(chosen) >= 3
    assert len(endpoints) == len(set(endpoints))
    assert set(chosen) <= actual
    assert all(maximal_witnesses[edge] in positive for edge in chosen)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(adj)))
    graph.add_edges_from(actual)
    maximum = nx.max_weight_matching(graph, maxcardinality=True)
    assert len(maximum) >= 3
    return {
        "actual_maximal_edge_count": len(actual),
        "actual_maximal_matching_size": len(maximum),
        "selected_maximal_edges": [list(edge) for edge in sorted(chosen)],
        "selected_count": len(chosen),
    }


def solve_face(
    n,
    h,
    max_rounds,
    outpath,
    cuts_per_round=24,
    seed=2026,
    min_degree=0,
):
    if not 0 <= min_degree <= h - 1:
        raise ValueError("min_degree must lie between 0 and h-1")
    rng = random.Random(seed)
    pool = IDPool()
    edges = {
        pair: pool.id(("edge",) + pair)
        for pair in itertools.combinations(range(n), 2)
    }

    def ev(u, v):
        return edges[(min(u, v), max(u, v))]

    solver = Cadical195()
    static_clauses = 0
    for four in itertools.combinations(range(n), 4):
        solver.add_clause([-ev(a, b) for a, b in itertools.combinations(four, 2)])
        static_clauses += 1
    degree_clauses = 0
    for u in range(n):
        incident = [ev(u, v) for v in range(n) if v != u]
        cnf = CardEnc.atmost(
            incident, bound=h - 1, vpool=pool, encoding=EncType.seqcounter
        )
        for clause in cnf.clauses:
            solver.add_clause(clause)
        degree_clauses += len(cnf.clauses)
        if min_degree:
            cnf = CardEnc.atleast(
                incident, bound=min_degree, vpool=pool, encoding=EncType.seqcounter
            )
            for clause in cnf.clauses:
                solver.add_clause(clause)
            degree_clauses += len(cnf.clauses)
    static_clauses += degree_clauses

    maximal_witnesses, maximal_stats = install_maximal_witnesses(
        solver, pool, n, ev
    )
    selected, matching_stats = add_matching_gate(
        solver, pool, n, maximal_witnesses, required=3
    )
    static_clauses += (
        maximal_stats["maximal_witness_clauses"]
        + matching_stats["matching_gate_clauses"]
    )
    base_stats = {
        "variables": pool.top,
        "clauses": static_clauses,
        "k4_clauses": sum(1 for _ in itertools.combinations(range(n), 4)),
        "degree_clauses": degree_clauses,
        **maximal_stats,
        **matching_stats,
    }

    triangle_witnesses = {}

    def triangle_var(triple):
        if triple not in triangle_witnesses:
            witness = pool.id(("triangle-witness",) + triple)
            triangle_witnesses[triple] = witness
            a, b, c = triple
            solver.add_clause([-witness, ev(a, b)])
            solver.add_clause([-witness, ev(a, c)])
            solver.add_clause([-witness, ev(b, c)])
        return triangle_witnesses[triple]

    def oracle_admissible(adj, want):
        maximal_adj = [0] * n
        for u, v in actual_maximal_edges(adj):
            maximal_adj[u] |= 1 << v
            maximal_adj[v] |= 1 << u
        found = []

        def rec(order, index, subset, count, budget):
            if count >= h:
                found.append(tuple(v for v in range(n) if (subset >> v) & 1))
                return True
            if index >= n or count + (n - index) < h or budget[0] <= 0:
                return False
            budget[0] -= 1
            vertex = order[index]
            common = adj[vertex] & subset
            ok = not (maximal_adj[vertex] & subset)
            if ok:
                cursor = common
                while cursor:
                    other = (cursor & -cursor).bit_length() - 1
                    cursor &= cursor - 1
                    if adj[other] & common:
                        ok = False
                        break
            if ok and rec(order, index + 1, subset | (1 << vertex), count + 1, budget):
                return True
            return rec(order, index + 1, subset, count, budget)

        base = list(range(n))
        for _ in range(want * 3):
            if len(found) >= want:
                break
            order = base[:]
            rng.shuffle(order)
            rec(order, 0, 0, 0, [200000])
        if not found:
            def rec_full(index, subset, count):
                if count >= h:
                    found.append(tuple(v for v in range(n) if (subset >> v) & 1))
                    return True
                if index >= n or count + (n - index) < h:
                    return False
                vertex = index
                common = adj[vertex] & subset
                ok = not (maximal_adj[vertex] & subset)
                if ok:
                    cursor = common
                    while cursor:
                        other = (cursor & -cursor).bit_length() - 1
                        cursor &= cursor - 1
                        if adj[other] & common:
                            ok = False
                            break
                if ok and rec_full(index + 1, subset | (1 << vertex), count + 1):
                    return True
                return rec_full(index + 1, subset, count)

            rec_full(0, 0, 0)
        return found

    started = time.time()
    log = []
    for round_index in range(max_rounds):
        satisfiable = solver.solve()
        if not satisfiable:
            result = {
                "n": n,
                "h": h,
                "min_degree": min_degree,
                "result": "UNSAT",
                "rounds": round_index,
                "cuts_y": len(triangle_witnesses),
                "cuts_m": len(maximal_witnesses),
                "base_stats": base_stats,
                "elapsed_s": round(time.time() - started, 1),
                "meaning": (
                    "K4-free face with the proved matching>=3 gate excluded; "
                    "publishable only after final-CNF proof certification"
                ),
            }
            Path(outpath).write_text(
                json.dumps({"summary": result, "log": log}, indent=1) + "\n",
                encoding="utf-8",
            )
            print(json.dumps(result), flush=True)
            return result

        positive = {literal for literal in solver.get_model() if literal > 0}
        adj = [0] * n
        edge_count = 0
        for (u, v), variable in edges.items():
            if variable in positive:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                edge_count += 1
        gate_validation = validate_matching_gate(
            adj, positive, maximal_witnesses, selected
        )
        sets_found = oracle_admissible(adj, cuts_per_round)
        if not sets_found:
            record = {
                "n": n,
                "h": h,
                "min_degree": min_degree,
                "result": "SAT-CANDIDATE",
                "round": round_index,
                "edges": edge_count,
                "edge_list": [
                    list(edge)
                    for edge, variable in sorted(edges.items())
                    if variable in positive
                ],
                "matching_gate_validation": gate_validation,
                "base_stats": base_stats,
                "elapsed_s": round(time.time() - started, 1),
            }
            Path(outpath).write_text(
                json.dumps(record, indent=1) + "\n", encoding="utf-8"
            )
            print(f"SAT-CANDIDATE -> {outpath}", flush=True)
            return record

        for vertex_set in sets_found:
            cut = [
                triangle_var(triple)
                for triple in itertools.combinations(vertex_set, 3)
            ]
            cut.extend(
                maximal_witnesses[pair]
                for pair in itertools.combinations(vertex_set, 2)
            )
            solver.add_clause(cut)
        log.append(
            {
                "round": round_index,
                "edges": edge_count,
                "cuts_added": len(sets_found),
                "actual_maximal_edges": gate_validation[
                    "actual_maximal_edge_count"
                ],
                "actual_maximal_matching": gate_validation[
                    "actual_maximal_matching_size"
                ],
                "t": round(time.time() - started, 1),
            }
        )
        if round_index % 10 == 0:
            print(
                f"[n={n}] round {round_index} edges={edge_count} "
                f"cuts+={len(sets_found)} y={len(triangle_witnesses)} "
                f"m={len(maximal_witnesses)} "
                f"nuM={gate_validation['actual_maximal_matching_size']} "
                f"{time.time()-started:.0f}s",
                flush=True,
            )

    result = {
        "n": n,
        "h": h,
        "min_degree": min_degree,
        "result": "ROUND-CAP-UNKNOWN",
        "rounds": max_rounds,
        "base_stats": base_stats,
        "elapsed_s": round(time.time() - started, 1),
    }
    Path(outpath).write_text(
        json.dumps({"summary": result, "log": log}, indent=1) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result), flush=True)
    return result


if __name__ == "__main__":
    n_arg, h_arg, rounds_arg = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    minimum = int(sys.argv[5]) if len(sys.argv) >= 6 else 0
    solve_face(n_arg, h_arg, rounds_arg, sys.argv[4], min_degree=minimum)
