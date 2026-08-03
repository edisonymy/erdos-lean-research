"""Separate CEGAR successor combining the matching>=3 and TCG-3 gates.

This file deliberately does not import, resume, or mutate either live solver
process.  Its static main-SAT formula is the audited matching-3 successor
formula.  For every decoded model, an external exact SAT oracle tests whether
the graph's triangle hypergraph is two-colorable.  A positive partition adds
one sound clause over the inherited one-way triangle witnesses.

Usage:
    python -X utf8 cegar_face_matching3_tcg3.py N H ROUNDS OUT.json \
        [MIN_DEGREE] [CHECKPOINT.jsonl]
"""

from __future__ import annotations

import itertools
import json
import random
import sys
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195

from cegar_checkpoint import (
    CutJournal,
    ExclusiveRunLock,
    RecordingCadical,
    atomic_write_text,
    file_hash,
    rng_state_from_json,
    rng_state_to_json,
)

from cegar_face_matching3 import (
    actual_maximal_edges,
    add_matching_gate,
    install_maximal_witnesses,
    validate_matching_gate,
)
from tcg3_separator import (
    find_triangle_free_two_partition,
    graph_triangles,
    partition_is_triangle_free,
    tcg3_cut,
)


def build_static_formula(n: int, h: int, min_degree: int = 0):
    """Build the matching-3 static formula and return its audited accounting."""

    if not 0 <= min_degree <= h - 1:
        raise ValueError("min_degree must lie between 0 and h-1")
    if n < 6:
        raise ValueError("matching>=3 requires at least six vertices")

    pool = IDPool()
    edges = {
        pair: pool.id(("edge",) + pair)
        for pair in itertools.combinations(range(n), 2)
    }

    def ev(u: int, v: int) -> int:
        return edges[(min(u, v), max(u, v))]

    solver = RecordingCadical()
    k4_clauses = 0
    for four in itertools.combinations(range(n), 4):
        solver.add_clause([-ev(a, b) for a, b in itertools.combinations(four, 2)])
        k4_clauses += 1

    degree_clauses = 0
    for vertex in range(n):
        incident = [ev(vertex, other) for other in range(n) if other != vertex]
        at_most = CardEnc.atmost(
            incident, bound=h - 1, vpool=pool, encoding=EncType.seqcounter
        )
        for clause in at_most.clauses:
            solver.add_clause(clause)
        degree_clauses += len(at_most.clauses)
        if min_degree:
            at_least = CardEnc.atleast(
                incident,
                bound=min_degree,
                vpool=pool,
                encoding=EncType.seqcounter,
            )
            for clause in at_least.clauses:
                solver.add_clause(clause)
            degree_clauses += len(at_least.clauses)

    graph_degree_variables = pool.top
    graph_degree_clauses = k4_clauses + degree_clauses
    maximal_witnesses, maximal_stats = install_maximal_witnesses(
        solver, pool, n, ev
    )
    selected, matching_stats = add_matching_gate(
        solver, pool, n, maximal_witnesses, required=3
    )
    static_clauses = (
        graph_degree_clauses
        + maximal_stats["maximal_witness_clauses"]
        + matching_stats["matching_gate_clauses"]
    )
    base_stats = {
        "schema": "erdos151-matching3-tcg3-static-formula-v1",
        "variables": pool.top,
        "clauses": static_clauses,
        "edge_variables": len(edges),
        "graph_and_degree_variables": graph_degree_variables,
        "graph_and_degree_clauses": graph_degree_clauses,
        "k4_clauses": k4_clauses,
        "degree_clauses": degree_clauses,
        **maximal_stats,
        **matching_stats,
        "tcg3_main_sat_static_variables": 0,
        "tcg3_main_sat_static_clauses": 0,
        "tcg3_external_oracle_variables": n,
        "tcg3_external_oracle_clause_bound": 2 * sum(
            1 for _ in itertools.combinations(range(n), 3)
        ),
        "formula_relation": (
            "same static formula as cegar_face_matching3.py; TCG-3 contributes "
            "only model-dependent learned clauses"
        ),
    }
    return solver, pool, edges, ev, maximal_witnesses, selected, base_stats


def find_admissible_sets(
    adj: list[int], h: int, want: int, rng: random.Random
) -> list[tuple[int, ...]]:
    """Preserve the inherited randomized-then-complete admissible-set oracle."""

    n = len(adj)
    maximal_adj = [0] * n
    for u, v in actual_maximal_edges(adj):
        maximal_adj[u] |= 1 << v
        maximal_adj[v] |= 1 << u
    found: list[tuple[int, ...]] = []

    def rec(
        order: list[int], index: int, subset: int, count: int, budget: list[int]
    ) -> bool:
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

        def rec_full(index: int, subset: int, count: int) -> bool:
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


def decode_graph(
    n: int, edges: dict[tuple[int, int], int], positive: set[int]
) -> tuple[list[int], int, list[list[int]]]:
    adj = [0] * n
    edge_list = []
    for (u, v), variable in edges.items():
        if variable in positive:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
            edge_list.append([u, v])
    return adj, len(edge_list), edge_list


def rebalance_partition(
    adj: list[int], partition: tuple[tuple[int, ...], tuple[int, ...]]
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], int]:
    """Greedily reduce imbalance while preserving both triangle-free sides."""

    sides = [set(partition[0]), set(partition[1])]
    n = len(adj)
    assert sides[0].isdisjoint(sides[1])
    assert sides[0] | sides[1] == set(range(n))
    moves = 0
    while abs(len(sides[0]) - len(sides[1])) > 1:
        source_index = 0 if len(sides[0]) > len(sides[1]) else 1
        target_index = 1 - source_index
        target_mask = sum(1 << vertex for vertex in sides[target_index])
        moved = False
        for vertex in sorted(sides[source_index]):
            common = adj[vertex] & target_mask
            cursor = common
            creates_triangle = False
            while cursor:
                neighbour = (cursor & -cursor).bit_length() - 1
                cursor &= cursor - 1
                if adj[neighbour] & common:
                    creates_triangle = True
                    break
            if creates_triangle:
                continue
            sides[source_index].remove(vertex)
            sides[target_index].add(vertex)
            moves += 1
            moved = True
            break
        if not moved:
            break
    result = (tuple(sorted(sides[0])), tuple(sorted(sides[1])))
    assert partition_is_triangle_free(adj, *result)
    return result, moves


def new_telemetry() -> dict[str, object]:
    return {
        "schema": "erdos151-matching3-tcg3-cut-telemetry-v1",
        "solver_calls": 0,
        "admissible_oracle": {
            "queries": 0,
            "full_batch_queries": 0,
            "partial_batch_queries": 0,
            "complete_miss_queries": 0,
            "sets_found": 0,
            "seconds": 0.0,
        },
        "tcg3_oracle": {
            "queries": 0,
            "partitionable": 0,
            "nonpartitionable": 0,
            "triangles_seen": 0,
            "enumeration_seconds": 0.0,
            "solver_seconds": 0.0,
        },
        "cuts": {
            "admissible_clauses": 0,
            "tcg3_clauses": 0,
            "tcg3_literals": 0,
            "tcg3_min_literals": None,
            "tcg3_max_literals": 0,
            "tcg3_new_triangle_witnesses": 0,
        },
    }


def _solve_face_locked(
    n: int,
    h: int,
    max_rounds: int,
    outpath: str | Path,
    cuts_per_round: int = 24,
    seed: int = 2026,
    min_degree: int = 0,
    checkpoint_path: str | Path | None = None,
) -> dict[str, object]:
    (
        solver,
        pool,
        edges,
        ev,
        maximal_witnesses,
        selected,
        base_stats,
    ) = build_static_formula(n, h, min_degree)
    if not isinstance(solver, RecordingCadical):
        raise TypeError("checkpointed runner requires a recording solver")
    rng = random.Random(seed)
    triangle_witnesses: dict[tuple[int, int, int], int] = {}
    dynamic_definition_clauses = 0
    telemetry = new_telemetry()
    round_log: list[dict[str, object]] = []

    def triangle_var(triple: tuple[int, int, int]) -> int:
        nonlocal dynamic_definition_clauses
        if triple not in triangle_witnesses:
            witness = pool.id(("triangle-witness",) + triple)
            triangle_witnesses[triple] = witness
            a, b, c = triple
            solver.add_clause([-witness, ev(a, b)])
            solver.add_clause([-witness, ev(a, c)])
            solver.add_clause([-witness, ev(b, c)])
            dynamic_definition_clauses += 3
        return triangle_witnesses[triple]

    def final_formula_stats() -> dict[str, int]:
        cuts = telemetry["cuts"]
        assert isinstance(cuts, dict)
        learned = int(cuts["admissible_clauses"]) + int(cuts["tcg3_clauses"])
        return {
            "variables": pool.top,
            "clauses": base_stats["clauses"]
            + dynamic_definition_clauses
            + learned,
            "triangle_witness_variables": len(triangle_witnesses),
            "triangle_definition_clauses": dynamic_definition_clauses,
            "admissible_cut_clauses": int(cuts["admissible_clauses"]),
            "tcg3_cut_clauses": int(cuts["tcg3_clauses"]),
        }

    outpath = Path(outpath)
    checkpoint = Path(checkpoint_path or (str(outpath) + ".cuts.jsonl"))
    state_path = Path(str(checkpoint) + ".state.json")
    final_cnf_path = Path(str(outpath) + ".final.cnf")
    static_formula_sha256 = solver.formula_hash()
    journal_config: dict[str, object] = {
        "n": n,
        "h": h,
        "min_degree": min_degree,
        "cuts_per_round": cuts_per_round,
        "seed": seed,
        "semantic_order": "tcg3-cut-then-admissible-cuts",
    }
    journal = CutJournal(checkpoint, journal_config, static_formula_sha256)

    def validate_vertex_set(values: object, expected_size: int | None) -> tuple[int, ...]:
        if not isinstance(values, list) or not all(isinstance(value, int) for value in values):
            raise ValueError("checkpoint vertex set is not an integer list")
        result = tuple(values)
        if tuple(sorted(set(result))) != result:
            raise ValueError("checkpoint vertex set is not sorted and unique")
        if any(value < 0 or value >= n for value in result):
            raise ValueError("checkpoint vertex is out of range")
        if expected_size is not None and len(result) != expected_size:
            raise ValueError("checkpoint vertex set has the wrong size")
        return result

    def replay_record(record: dict[str, object]) -> None:
        partition_payload = record.get("tcg3_partition")
        if partition_payload is not None:
            if not isinstance(partition_payload, list) or len(partition_payload) != 2:
                raise ValueError("checkpoint TCG-3 partition has the wrong shape")
            side_zero = validate_vertex_set(partition_payload[0], None)
            side_one = validate_vertex_set(partition_payload[1], None)
            if set(side_zero).intersection(side_one) or set(side_zero).union(side_one) != set(range(n)):
                raise ValueError("checkpoint TCG-3 sides do not partition the vertices")
            solver.add_clause(tcg3_cut(side_zero, side_one, triangle_var))
        sets_payload = record.get("admissible_sets")
        if not isinstance(sets_payload, list):
            raise ValueError("checkpoint admissible_sets is not a list")
        for values in sets_payload:
            vertex_set = validate_vertex_set(values, h)
            clause = [triangle_var(triple) for triple in itertools.combinations(vertex_set, 3)]
            clause.extend(
                maximal_witnesses[pair]
                for pair in itertools.combinations(vertex_set, 2)
            )
            solver.add_clause(clause)

    for expected_round, record in enumerate(journal.records):
        if record.get("round") != expected_round:
            raise ValueError(f"checkpoint round mismatch at {expected_round}")
        replay_record(record)
        if record.get("formula_sha256_after_round") != solver.formula_hash():
            raise ValueError(f"checkpoint formula replay mismatch at {expected_round}")
    if journal.records:
        latest = journal.records[-1]
        saved_telemetry = latest.get("telemetry")
        saved_rng_state = latest.get("rng_state")
        if not isinstance(saved_telemetry, dict) or not isinstance(saved_rng_state, dict):
            raise ValueError("checkpoint lacks telemetry or RNG state")
        telemetry = saved_telemetry
        rng.setstate(rng_state_from_json(saved_rng_state))
    start_round = len(journal.records)

    def write_payload(summary: dict[str, object]) -> None:
        payload = {
            "summary": summary,
            "static_formula": base_stats,
            "final_formula": final_formula_stats(),
            "telemetry": telemetry,
            "log": round_log,
            "checkpoint": {
                "path": checkpoint.as_posix(),
                "sha256": file_hash(checkpoint),
                "completed_rounds": len(journal.records),
                "last_record_sha256": journal.last_hash,
                "resumed": bool(start_round),
            },
        }
        atomic_write_text(
            outpath, json.dumps(payload, indent=2, sort_keys=True) + "\n"
        )

    started = time.perf_counter()
    for round_index in range(start_round, max_rounds):
        solver_started = time.perf_counter()
        satisfiable = solver.solve()
        solver_seconds = time.perf_counter() - solver_started
        telemetry["solver_calls"] = int(telemetry["solver_calls"]) + 1
        if not satisfiable:
            solver.write_dimacs_atomic(final_cnf_path)
            summary = {
                "n": n,
                "h": h,
                "min_degree": min_degree,
                "seed": seed,
                "cuts_per_round": cuts_per_round,
                "result": "UNSAT",
                "rounds": round_index,
                "final_cnf": final_cnf_path.as_posix(),
                "final_cnf_sha256": file_hash(final_cnf_path),
                "final_formula_sha256": solver.formula_hash(),
                "elapsed_s": round(time.perf_counter() - started, 6),
                "claim_boundary": (
                    "requires final-CNF serialization and independent proof "
                    "certification before theorem use"
                ),
            }
            write_payload(summary)
            print(json.dumps(summary, sort_keys=True), flush=True)
            solver.delete()
            return summary

        positive = {literal for literal in solver.get_model() if literal > 0}
        adj, edge_count, edge_list = decode_graph(n, edges, positive)
        gate_validation = validate_matching_gate(
            adj, positive, maximal_witnesses, selected
        )

        enumeration_started = time.perf_counter()
        triangles = graph_triangles(adj)
        enumeration_seconds = time.perf_counter() - enumeration_started
        tcg_started = time.perf_counter()
        raw_partition = find_triangle_free_two_partition(adj)
        tcg_seconds = time.perf_counter() - tcg_started
        tcg = telemetry["tcg3_oracle"]
        assert isinstance(tcg, dict)
        tcg["queries"] = int(tcg["queries"]) + 1
        tcg["triangles_seen"] = int(tcg["triangles_seen"]) + len(triangles)
        tcg["enumeration_seconds"] = float(tcg["enumeration_seconds"]) + enumeration_seconds
        tcg["solver_seconds"] = float(tcg["solver_seconds"]) + tcg_seconds

        tcg_record: dict[str, object]
        if raw_partition is None:
            tcg["nonpartitionable"] = int(tcg["nonpartitionable"]) + 1
            tcg_record = {
                "status": "exact-nonpartitionable",
                "triangle_count": len(triangles),
                "enumeration_s": round(enumeration_seconds, 6),
                "oracle_s": round(tcg_seconds, 6),
                "cut_added": False,
            }
        else:
            tcg["partitionable"] = int(tcg["partitionable"]) + 1
            partition, rebalance_moves = rebalance_partition(adj, raw_partition)
            before_witnesses = len(triangle_witnesses)
            cut = tcg3_cut(*partition, triangle_var)
            solver.add_clause(cut)
            new_witnesses = len(triangle_witnesses) - before_witnesses
            cuts = telemetry["cuts"]
            assert isinstance(cuts, dict)
            cuts["tcg3_clauses"] = int(cuts["tcg3_clauses"]) + 1
            cuts["tcg3_literals"] = int(cuts["tcg3_literals"]) + len(cut)
            cuts["tcg3_new_triangle_witnesses"] = (
                int(cuts["tcg3_new_triangle_witnesses"]) + new_witnesses
            )
            prior_min = cuts["tcg3_min_literals"]
            cuts["tcg3_min_literals"] = (
                len(cut) if prior_min is None else min(int(prior_min), len(cut))
            )
            cuts["tcg3_max_literals"] = max(
                int(cuts["tcg3_max_literals"]), len(cut)
            )
            tcg_record = {
                "status": "partition-found",
                "triangle_count": len(triangles),
                "raw_partition_sizes": [
                    len(raw_partition[0]),
                    len(raw_partition[1]),
                ],
                "partition_sizes": [len(partition[0]), len(partition[1])],
                "rebalance_moves": rebalance_moves,
                "enumeration_s": round(enumeration_seconds, 6),
                "oracle_s": round(tcg_seconds, 6),
                "cut_added": True,
                "cut_literals": len(cut),
                "new_triangle_witnesses": new_witnesses,
            }

        admissible_started = time.perf_counter()
        sets_found = find_admissible_sets(adj, h, cuts_per_round, rng)
        admissible_seconds = time.perf_counter() - admissible_started
        admissible = telemetry["admissible_oracle"]
        assert isinstance(admissible, dict)
        admissible["queries"] = int(admissible["queries"]) + 1
        admissible["sets_found"] = int(admissible["sets_found"]) + len(sets_found)
        admissible["seconds"] = float(admissible["seconds"]) + admissible_seconds
        if not sets_found:
            admissible["complete_miss_queries"] = (
                int(admissible["complete_miss_queries"]) + 1
            )
            admissible_phase = "deterministic-complete-miss"
        elif len(sets_found) >= cuts_per_round:
            admissible["full_batch_queries"] = (
                int(admissible["full_batch_queries"]) + 1
            )
            admissible_phase = "randomized-full-batch"
        else:
            admissible["partial_batch_queries"] = (
                int(admissible["partial_batch_queries"]) + 1
            )
            admissible_phase = "randomized-partial-batch"

        for vertex_set in sets_found:
            admissible_cut = [
                triangle_var(triple)
                for triple in itertools.combinations(vertex_set, 3)
            ]
            admissible_cut.extend(
                maximal_witnesses[pair]
                for pair in itertools.combinations(vertex_set, 2)
            )
            solver.add_clause(admissible_cut)
        cuts = telemetry["cuts"]
        assert isinstance(cuts, dict)
        cuts["admissible_clauses"] = int(cuts["admissible_clauses"]) + len(
            sets_found
        )

        round_record = {
            "round": round_index,
            "edges": edge_count,
            "solver_s": round(solver_seconds, 6),
            "actual_maximal_edges": gate_validation["actual_maximal_edge_count"],
            "actual_maximal_matching": gate_validation[
                "actual_maximal_matching_size"
            ],
            "tcg3": tcg_record,
            "admissible": {
                "phase": admissible_phase,
                "sets_found": len(sets_found),
                "oracle_s": round(admissible_seconds, 6),
            },
            "triangle_witnesses": len(triangle_witnesses),
            "elapsed_s": round(time.perf_counter() - started, 6),
        }
        round_log.append(round_record)

        if not sets_found and raw_partition is None:
            summary = {
                "n": n,
                "h": h,
                "min_degree": min_degree,
                "seed": seed,
                "cuts_per_round": cuts_per_round,
                "result": "SAT-CANDIDATE",
                "round": round_index,
                "edges": edge_count,
                "edge_list": edge_list,
                "matching_gate_validation": gate_validation,
                "tcg3_validation": "triangle hypergraph is not two-colorable",
                "elapsed_s": round(time.perf_counter() - started, 6),
                "claim_boundary": (
                    "requires independent exact beta, K4, and edge-arrowing "
                    "validation before theorem use"
                ),
            }
            write_payload(summary)
            print(f"SAT-CANDIDATE -> {outpath}", flush=True)
            solver.delete()
            return summary

        journal.append_round(
            {
                "round": round_index,
                "tcg3_partition": (
                    [list(partition[0]), list(partition[1])]
                    if raw_partition is not None
                    else None
                ),
                "admissible_sets": [list(vertex_set) for vertex_set in sets_found],
                "rng_state": rng_state_to_json(rng.getstate()),
                "telemetry": telemetry,
                "round_summary": round_record,
                "formula_sha256_after_round": solver.formula_hash(),
            }
        )
        if round_index % 10 == 0:
            journal.write_state(
                state_path,
                {
                    "next_round": round_index + 1,
                    "variables": pool.top,
                    "clauses": len(solver.clauses),
                    "formula_sha256": solver.formula_hash(),
                    "triangle_witness_variables": len(triangle_witnesses),
                },
            )

        if round_index % 10 == 0:
            print(
                f"[combined n={n}] round {round_index} edges={edge_count} "
                f"tcg3={tcg_record['status']} adm={len(sets_found)} "
                f"phase={admissible_phase} y={len(triangle_witnesses)} "
                f"nuM={gate_validation['actual_maximal_matching_size']} "
                f"{time.perf_counter()-started:.2f}s",
                flush=True,
            )

    summary = {
        "n": n,
        "h": h,
        "min_degree": min_degree,
        "seed": seed,
        "cuts_per_round": cuts_per_round,
        "result": "ROUND-CAP-UNKNOWN",
        "rounds": max_rounds,
        "elapsed_s": round(time.perf_counter() - started, 6),
        "claim_boundary": "bounded control only; no mathematical result",
    }
    journal.write_state(
        state_path,
        {
            "next_round": max_rounds,
            "variables": pool.top,
            "clauses": len(solver.clauses),
            "formula_sha256": solver.formula_hash(),
            "triangle_witness_variables": len(triangle_witnesses),
        },
    )
    write_payload(summary)
    print(json.dumps(summary, sort_keys=True), flush=True)
    solver.delete()
    return summary


def solve_face(
    n: int,
    h: int,
    max_rounds: int,
    outpath: str | Path,
    cuts_per_round: int = 24,
    seed: int = 2026,
    min_degree: int = 0,
    checkpoint_path: str | Path | None = None,
) -> dict[str, object]:
    """Run with one exclusive writer for the checkpoint and result pair."""

    output = Path(outpath)
    checkpoint = Path(checkpoint_path or (str(output) + ".cuts.jsonl"))
    lock_path = Path(str(checkpoint) + ".writer.lock")
    with ExclusiveRunLock(lock_path):
        return _solve_face_locked(
            n,
            h,
            max_rounds,
            output,
            cuts_per_round=cuts_per_round,
            seed=seed,
            min_degree=min_degree,
            checkpoint_path=checkpoint,
        )


if __name__ == "__main__":
    n_arg, h_arg, rounds_arg = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    minimum = int(sys.argv[5]) if len(sys.argv) >= 6 else 0
    checkpoint_arg = sys.argv[6] if len(sys.argv) >= 7 else None
    solve_face(
        n_arg,
        h_arg,
        rounds_arg,
        sys.argv[4],
        min_degree=minimum,
        checkpoint_path=checkpoint_arg,
    )
