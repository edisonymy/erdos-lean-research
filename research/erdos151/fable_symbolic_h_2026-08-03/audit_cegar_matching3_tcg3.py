#!/usr/bin/env python3
"""Integration and bounded A/B audit for the matching-3 + TCG-3 successor."""

from __future__ import annotations

import contextlib
import io
import itertools
import json
import math
import re
from pathlib import Path

from cegar_face_matching3 import (
    actual_maximal_edges,
    solve_face as solve_matching3,
)
from cegar_face_matching3_tcg3 import (
    build_static_formula,
    rebalance_partition,
    solve_face as solve_combined,
)
from tcg3_separator import (
    find_triangle_free_two_partition,
    partition_is_triangle_free,
)


PACKET = Path(__file__).resolve().parent


def adjacency(n: int, edges: set[tuple[int, int]]) -> list[int]:
    result = [0] * n
    for u, v in edges:
        result[u] |= 1 << v
        result[v] |= 1 << u
    return result


def has_matching_three(edges: list[tuple[int, int]]) -> bool:
    return any(
        len({vertex for edge in chosen for vertex in edge}) == 6
        for chosen in itertools.combinations(edges, 3)
    )


def cut_length(partition: tuple[tuple[int, ...], tuple[int, ...]]) -> int:
    return sum(math.comb(len(side), 3) for side in partition)


def audit_rebalancer_n6() -> dict[str, object]:
    n = 6
    all_edges = list(itertools.combinations(range(n), 2))
    gate_graphs = 0
    partitionable_gate_graphs = 0
    total_moves = 0
    strict_improvements = 0
    for graph_mask in range(1 << len(all_edges)):
        graph_edges = {
            edge for index, edge in enumerate(all_edges) if (graph_mask >> index) & 1
        }
        adj = adjacency(n, graph_edges)
        if not has_matching_three(actual_maximal_edges(adj)):
            continue
        gate_graphs += 1
        raw = find_triangle_free_two_partition(adj)
        if raw is None:
            continue
        partitionable_gate_graphs += 1
        balanced, moves = rebalance_partition(adj, raw)
        assert set(balanced[0]).isdisjoint(balanced[1])
        assert set(balanced[0]) | set(balanced[1]) == set(range(n))
        assert partition_is_triangle_free(adj, *balanced)
        assert cut_length(balanced) <= cut_length(raw)
        total_moves += moves
        strict_improvements += int(cut_length(balanced) < cut_length(raw))
    assert gate_graphs == 3640
    return {
        "all_labeled_graphs_screened": 1 << len(all_edges),
        "matching3_gate_graphs": gate_graphs,
        "partitionable_gate_graphs": partitionable_gate_graphs,
        "valid_rebalanced_partitions": partitionable_gate_graphs,
        "total_vertex_moves": total_moves,
        "strict_cut_length_improvements": strict_improvements,
        "invariant": "triangle-free, full partition, and cut length never increases",
    }


def validate_combined_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    summary = payload["summary"]
    telemetry = payload["telemetry"]
    cuts = telemetry["cuts"]
    log = payload["log"]
    assert telemetry["solver_calls"] == len(log) + 1
    assert cuts["tcg3_clauses"] == telemetry["tcg3_oracle"]["partitionable"]
    assert cuts["admissible_clauses"] == sum(
        record["admissible"]["sets_found"] for record in log
    )
    assert cuts["tcg3_literals"] == sum(
        record["tcg3"].get("cut_literals", 0) for record in log
    )
    for record in log:
        tcg = record["tcg3"]
        if tcg["status"] == "partition-found":
            a, b = tcg["partition_sizes"]
            assert a + b == summary["n"]
            assert tcg["cut_literals"] == math.comb(a, 3) + math.comb(b, 3)
            raw_a, raw_b = tcg["raw_partition_sizes"]
            assert math.comb(a, 3) + math.comb(b, 3) <= (
                math.comb(raw_a, 3) + math.comb(raw_b, 3)
            )
    final_formula = payload["final_formula"]
    static_formula = payload["static_formula"]
    assert final_formula["clauses"] == (
        static_formula["clauses"]
        + final_formula["triangle_definition_clauses"]
        + final_formula["admissible_cut_clauses"]
        + final_formula["tcg3_cut_clauses"]
    )
    return payload


def run_ab_controls() -> dict[str, object]:
    records = []
    for seed in (2026, 2027, 2028):
        baseline_path = PACKET / f"control_ab_matching3_n10_h4_seed{seed}.json"
        combined_path = PACKET / f"control_ab_combined_n10_h4_seed{seed}.json"
        with contextlib.redirect_stdout(io.StringIO()):
            baseline = solve_matching3(
                10, 4, 200, baseline_path, cuts_per_round=24, seed=seed
            )
            combined = solve_combined(
                10, 4, 200, combined_path, cuts_per_round=24, seed=seed
            )
        assert baseline["result"] == "UNSAT"
        assert combined["result"] == "UNSAT"
        combined_payload = validate_combined_payload(combined_path)
        records.append(
            {
                "seed": seed,
                "matching3_result": baseline["result"],
                "matching3_rounds": baseline["rounds"],
                "combined_result": combined["result"],
                "combined_rounds": combined["rounds"],
                "combined_tcg3_queries": combined_payload["telemetry"][
                    "tcg3_oracle"
                ]["queries"],
                "combined_tcg3_hits": combined_payload["telemetry"][
                    "tcg3_oracle"
                ]["partitionable"],
                "combined_admissible_phase_counts": {
                    key: combined_payload["telemetry"]["admissible_oracle"][key]
                    for key in (
                        "full_batch_queries",
                        "partial_batch_queries",
                        "complete_miss_queries",
                    )
                },
            }
        )

    baseline6_path = PACKET / "control_ab_matching3_n6_h4_seed2026.json"
    combined6_path = PACKET / "control_ab_combined_n6_h4_seed2026.json"
    with contextlib.redirect_stdout(io.StringIO()):
        baseline6 = solve_matching3(6, 4, 100, baseline6_path, seed=2026)
        combined6 = solve_combined(6, 4, 100, combined6_path, seed=2026)
    assert baseline6["result"] == "SAT-CANDIDATE"
    assert combined6["result"] == "UNSAT"
    baseline_adj = adjacency(6, {tuple(edge) for edge in baseline6["edge_list"]})
    baseline_partition = find_triangle_free_two_partition(baseline_adj)
    assert baseline_partition is not None
    combined6_payload = validate_combined_payload(combined6_path)
    return {
        "matched_n10_h4": records,
        "n6_separator_control": {
            "matching3_only": baseline6["result"],
            "matching3_candidate_has_triangle_free_two_partition": True,
            "combined": combined6["result"],
            "combined_rounds": combined6["rounds"],
            "combined_tcg3_hits": combined6_payload["telemetry"]["tcg3_oracle"][
                "partitionable"
            ],
            "meaning": (
                "semantic separator control only; the small-order UNSAT is not "
                "a proof-certified theorem result"
            ),
        },
    }


def static_formula_audit() -> dict[str, object]:
    metadata = json.loads(
        (PACKET / "cegar_face_matching3_n50_d9.meta.json").read_text(
            encoding="utf-8-sig"
        )
    )
    solver, _pool, _edges, _ev, _maximal, _selected, stats = build_static_formula(
        50, 11, 9
    )
    solver.delete()
    expected = metadata["static_formula"]
    assert stats["variables"] == expected["variables"] == 47241
    assert stats["clauses"] == expected["clauses"] == 379713
    assert stats["graph_and_degree_variables"] == expected[
        "graph_and_degree_variables"
    ]
    assert stats["graph_and_degree_clauses"] == expected[
        "graph_and_degree_clauses"
    ]
    assert stats["maximal_witness_variables"] == expected[
        "maximal_witness_variables"
    ]
    assert stats["maximal_witness_clauses"] == expected[
        "maximal_witness_clauses"
    ]
    assert stats["matching_gate_variables"] == expected[
        "matching_gate_variables_beyond_maximal_witnesses"
    ]
    assert stats["matching_gate_clauses"] == expected[
        "matching_gate_clauses_beyond_maximal_witnesses"
    ]
    return {
        "status": "exact match to the audited matching3 production metadata",
        "variables": stats["variables"],
        "clauses": stats["clauses"],
        "graph_and_degree_variables": stats["graph_and_degree_variables"],
        "graph_and_degree_clauses": stats["graph_and_degree_clauses"],
        "maximal_witness_variables": stats["maximal_witness_variables"],
        "maximal_witness_clauses": stats["maximal_witness_clauses"],
        "matching_gate_variables": stats["matching_gate_variables"],
        "matching_gate_clauses": stats["matching_gate_clauses"],
        "tcg3_main_sat_static_variables": stats[
            "tcg3_main_sat_static_variables"
        ],
        "tcg3_main_sat_static_clauses": stats["tcg3_main_sat_static_clauses"],
        "tcg3_external_oracle_variables": stats["tcg3_external_oracle_variables"],
        "tcg3_external_oracle_clause_bound": stats[
            "tcg3_external_oracle_clause_bound"
        ],
    }


def live_log_snapshot(path: Path, include_matching: bool) -> dict[str, object]:
    pattern = re.compile(
        r"round (?P<round>\d+).*cuts\+=(?P<cuts>\d+) "
        r"y=(?P<y>\d+) m=(?P<m>\d+)"
        + (r" nuM=(?P<matching>\d+)" if include_matching else "")
    )
    records = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = pattern.search(line)
        if match:
            records.append({key: int(value) for key, value in match.groupdict().items()})
    assert records
    recent = records[-25:]
    result = {
        "path": path.name,
        "last_sampled_round": records[-1]["round"],
        "last_sample_y": records[-1]["y"],
        "last_sample_m": records[-1]["m"],
        "recent_samples": len(recent),
        "recent_samples_all_full_24_cut_batches": all(
            record["cuts"] == 24 for record in recent
        ),
        "observed_oracle_phase": (
            "randomized-full-batch"
            if all(record["cuts"] == 24 for record in recent)
            else "mixed"
        ),
    }
    if include_matching:
        result["recent_actual_maximal_matching_range"] = [
            min(record["matching"] for record in recent),
            max(record["matching"] for record in recent),
        ]
    return result


def main() -> None:
    static = static_formula_audit()
    rebalance = audit_rebalancer_n6()
    controls = run_ab_controls()
    inherited_snapshot = live_log_snapshot(
        PACKET / "cegar_face_n50_d9.stdout.log", include_matching=False
    )
    matching3_snapshot = live_log_snapshot(
        PACKET / "cegar_face_matching3_n50_d9.stdout.log", include_matching=True
    )
    payload = {
        "schema": "erdos151-matching3-tcg3-integration-audit-v1",
        "status": "PASS",
        "static_formula_n50": static,
        "rebalancer_exhaustive_n6_matching3_projection": rebalance,
        "bounded_ab_controls": controls,
        "live_read_only_snapshots": {
            "inherited": inherited_snapshot,
            "matching3": matching3_snapshot,
            "interpretation": (
                "sampled cuts+=24 is the randomized full-batch branch; the "
                "deterministic complete-miss branch returns zero cuts"
            ),
        },
        "formula_comparison": {
            "combined_vs_matching3_static": "identical",
            "combined_vs_inherited_static_edge_projection": (
                "strict target-valid strengthening by the audited matching>=3 gate"
            ),
            "combined_fresh_vs_inherited_live": (
                "incomparable: the fresh combined solver lacks the inherited "
                "run's accumulated admissible cuts, while the inherited solver "
                "lacks matching>=3 and TCG-3"
            ),
        },
        "scheduler_recommendation": {
            "choice": "combined-successor",
            "launch_state": "NOT LAUNCHED; report and authorization first",
            "basis": (
                "choose the target-valid stronger formulation because the "
                "inherited run is still observed in randomized full-batch cut "
                "discovery, not the deterministic complete-oracle phase; this "
                "choice does not use elapsed human time"
            ),
            "caveat": (
                "the current live formula states are incomparable and no n=50 "
                "TCG-3 hit rate has been measured"
            ),
        },
        "claim_boundary": (
            "small controls are regression evidence only; production UNSAT still "
            "requires final-CNF proof certification and SAT requires independent "
            "graph validation"
        ),
    }
    output = Path(__file__).with_name(
        "audit_cegar_matching3_tcg3.result.json"
    )
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
