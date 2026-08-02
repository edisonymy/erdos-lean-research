#!/usr/bin/env python3
"""Bounded, non-production benchmarks for single-cut versus batched CEGAR."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path
from typing import Sequence

import cegar as v2


def percentile(values: Sequence[int], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def safe_journal_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.endswith("\n"):
                break
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                # A concurrently appended final fragment is outside the stable
                # prefix and is intentionally ignored by this read-only probe.
                break
            if isinstance(value, dict):
                records.append(value)
            else:
                raise ValueError(f"non-object journal line {line_number} in {path}")
    return records


def evenly_sample(values: Sequence[dict[str, object]], limit: int) -> list[dict[str, object]]:
    if len(values) <= limit:
        return list(values)
    return [values[(i * len(values)) // limit] for i in range(limit)]


def analyze_journal(run_dir: Path, sample_limit: int = 256) -> dict[str, object]:
    metadata = v2.load_hashed_json(run_dir / "metadata.json")
    config = v2.CaseConfig.from_dict(dict(metadata["config"]))
    records = safe_journal_records(run_dir / "cuts.jsonl")
    forbidden_records = [r for r in records if r.get("kind") == "forbidden_clique"]
    sampled = evenly_sample(forbidden_records, sample_limit)
    counts: list[int] = []
    separation_seconds = 0.0
    for record in sampled:
        candidate = dict(record["candidate"])
        graph = v2.GraphSnapshot.from_hex(config.n, str(candidate["edges_hex"]))
        started = time.perf_counter()
        cliques = v2.enumerate_cliques_exact(
            graph.adjacency(), config.forbidden_clique_size
        )
        separation_seconds += time.perf_counter() - started
        counts.append(len(cliques))
    return {
        "run_dir": str(run_dir.resolve()),
        "stable_prefix_record_count": len(records),
        "cut_counts": {
            kind: sum(record.get("kind") == kind for record in records)
            for kind in ("forbidden_clique", "admissibility", "arrowing")
        },
        "forbidden_candidate_sample_count": len(sampled),
        "all_forbidden_cliques_per_sampled_candidate": {
            "minimum": min(counts, default=0),
            "median": percentile(counts, 0.5),
            "mean": statistics.fmean(counts) if counts else 0.0,
            "p90": percentile(counts, 0.9),
            "maximum": max(counts, default=0),
            "total": sum(counts),
        },
        "same_candidate_logical_cut_multiplier": (
            statistics.fmean(counts) if counts else 0.0
        ),
        "batch_enumeration_seconds_total": separation_seconds,
        "batch_enumeration_microseconds_per_candidate": (
            1e6 * separation_seconds / len(sampled) if sampled else 0.0
        ),
    }


def run_relaxation(
    config: v2.CaseConfig,
    strategy: str,
    *,
    max_models: int,
    time_limit_seconds: float,
) -> dict[str, object]:
    if strategy not in {"single", "batch", "eager"}:
        raise ValueError("unknown strategy")
    effective = dataclass_replace(
        config,
        forbidden_mode="eager" if strategy == "eager" else "lazy",
    )
    initialized = time.perf_counter()
    problem = (
        v2._V1OuterProblem(effective)
        if strategy == "single"
        else v2.OuterProblem(effective)
    )
    initialization_seconds = time.perf_counter() - initialized
    started = time.perf_counter()
    models = 0
    logical_cuts = 0
    clauses_added = 0
    cut_counts: dict[str, int] = {}
    terminal = "MODEL_LIMIT"
    sequence = 0
    try:
        while models < max_models:
            if time_limit_seconds and time.perf_counter() - started >= time_limit_seconds:
                terminal = "TIME_LIMIT"
                break
            graph = problem.solve()
            if graph is None:
                terminal = "OUTER_UNSAT"
                break
            models += 1
            adj = graph.adjacency()
            if strategy == "single":
                forbidden = v2.find_clique(adj, effective.forbidden_clique_size)
                if forbidden is not None:
                    encoding = problem.build_cut(
                        "forbidden_clique",
                        {"vertices": list(forbidden)},
                        sequence,
                    )
                    kind = "forbidden_clique"
                    item_count = 1
                else:
                    admissible = v2.admissibility_oracle_v1(
                        graph, effective.target_set_size
                    )
                    if admissible is not None:
                        encoding = problem.build_cut(
                            "admissibility",
                            {"vertices": list(admissible.vertices)},
                            sequence,
                        )
                        kind = "admissibility"
                        item_count = 1
                    else:
                        coloring = v2.coloring_oracle(graph)
                        if coloring is None:
                            terminal = "CANDIDATE"
                            break
                        encoding = problem.build_cut(
                            "arrowing",
                            {"total_coloring_hex": v2.pack_bits(coloring.total_colors)},
                            sequence,
                        )
                        kind = "arrowing"
                        item_count = 1
            else:
                forbidden_all = v2.enumerate_cliques_exact(
                    adj, effective.forbidden_clique_size
                )
                if forbidden_all:
                    if strategy == "eager":
                        raise AssertionError("eager formula admitted a forbidden clique")
                    items = [
                        v2.make_batch_item(
                            "forbidden_clique", {"vertices": list(vertices)}
                        )
                        for vertices in forbidden_all
                    ]
                    encoding = problem.build_cut(
                        "forbidden_clique_batch",
                        {"items": items, "logical_cut_count": len(items)},
                        sequence,
                    )
                    kind = "forbidden_clique"
                    item_count = len(items)
                else:
                    admissible_batch = v2.admissibility_oracle_batch(
                        graph,
                        effective.target_set_size,
                        effective.admissibility_batch_size,
                    )
                    if admissible_batch is not None:
                        items = [
                            v2.make_batch_item(
                                "admissibility", {"vertices": list(vertices)}
                            )
                            for vertices in admissible_batch.vertex_sets
                        ]
                        encoding = problem.build_cut(
                            "admissibility_batch",
                            {"items": items, "logical_cut_count": len(items)},
                            sequence,
                        )
                        kind = "admissibility"
                        item_count = len(items)
                    else:
                        coloring = v2.coloring_oracle(graph)
                        if coloring is None:
                            terminal = "CANDIDATE"
                            break
                        encoding = problem.build_cut(
                            "arrowing",
                            {"total_coloring_hex": v2.pack_bits(coloring.total_colors)},
                            sequence,
                        )
                        kind = "arrowing"
                        item_count = 1
            problem.add_encoding(encoding)
            sequence += 1
            logical_cuts += item_count
            clauses_added += len(encoding.clauses)
            cut_counts[kind] = cut_counts.get(kind, 0) + item_count
    finally:
        problem.close()
    elapsed = time.perf_counter() - started
    return {
        "strategy": strategy,
        "config": effective.as_dict(),
        "terminal": terminal,
        "initialization_seconds": initialization_seconds,
        "search_seconds": elapsed,
        "wall_seconds": initialization_seconds + elapsed,
        "outer_models": models,
        "logical_cuts": logical_cuts,
        "logical_cut_counts": cut_counts,
        "dynamic_clauses_added": clauses_added,
        "outer_models_per_search_second": models / elapsed if elapsed else 0.0,
        "logical_cuts_per_search_second": logical_cuts / elapsed if elapsed else 0.0,
        "static_encoding": problem.static_encoding,
    }


def dataclass_replace(config: v2.CaseConfig, **changes: object) -> v2.CaseConfig:
    values = config.as_dict()
    values.update(changes)
    return v2.CaseConfig.from_dict(values)


def ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def comparison(single: dict[str, object], batch: dict[str, object]) -> dict[str, object]:
    return {
        "batch_vs_single_logical_cuts_per_second": ratio(
            float(batch["logical_cuts_per_search_second"]),
            float(single["logical_cuts_per_search_second"]),
        ),
        "batch_vs_single_outer_model_reduction": ratio(
            float(single["outer_models"]), float(batch["outer_models"])
        ),
        "note": (
            "Solver paths diverge after the first batch. Logical cuts/second is a "
            "throughput measure, not a proof that wall-clock exhaustion scales by this ratio."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--journal-run", action="append", default=[], type=Path)
    parser.add_argument("--sample-limit", type=int, default=256)
    parser.add_argument("--seconds", type=float, default=3.0)
    parser.add_argument("--models", type=int, default=100000)
    parser.add_argument("--smoke-repeats", type=int, default=30)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    smoke = v2.CaseConfig(
        name="SMOKE_N7_TERMINAL",
        n=7,
        fixed_clique_size=3,
        forbidden_clique_size=4,
        degree_min=0,
        degree_max=6,
        target_set_size=7,
        scope="bounded terminal smoke benchmark only",
        forbidden_mode="lazy",
        admissibility_batch_size=8,
    )
    if args.smoke_repeats < 1:
        raise ValueError("--smoke-repeats must be positive")
    smoke_trials: list[dict[str, object]] = []
    for _ in range(args.smoke_repeats):
        smoke_trials.append(
            {
                "single": run_relaxation(
                    smoke,
                    "single",
                    max_models=args.models,
                    time_limit_seconds=max(args.seconds, 1.0),
                ),
                "batch": run_relaxation(
                    smoke,
                    "batch",
                    max_models=args.models,
                    time_limit_seconds=max(args.seconds, 1.0),
                ),
            }
        )
    single_walls = [float(trial["single"]["wall_seconds"]) for trial in smoke_trials]
    batch_walls = [float(trial["batch"]["wall_seconds"]) for trial in smoke_trials]
    smoke_summary = {
        "repeats": args.smoke_repeats,
        "single_terminal_statuses": sorted(
            {str(trial["single"]["terminal"]) for trial in smoke_trials}
        ),
        "batch_terminal_statuses": sorted(
            {str(trial["batch"]["terminal"]) for trial in smoke_trials}
        ),
        "single_outer_model_counts": sorted(
            {int(trial["single"]["outer_models"]) for trial in smoke_trials}
        ),
        "batch_outer_model_counts": sorted(
            {int(trial["batch"]["outer_models"]) for trial in smoke_trials}
        ),
        "single_median_wall_seconds": statistics.median(single_walls),
        "batch_median_wall_seconds": statistics.median(batch_walls),
        "median_wall_speedup": statistics.median(single_walls)
        / statistics.median(batch_walls),
        "single_mean_wall_seconds": statistics.fmean(single_walls),
        "batch_mean_wall_seconds": statistics.fmean(batch_walls),
        "mean_wall_speedup": statistics.fmean(single_walls)
        / statistics.fmean(batch_walls),
    }
    production: dict[str, object] = {}
    for name in ("F3_N41", "F4_N41", "F5_N41"):
        config = v2.load_cases()[name]
        single = run_relaxation(
            config, "single", max_models=args.models, time_limit_seconds=args.seconds
        )
        batch = run_relaxation(
            config, "batch", max_models=args.models, time_limit_seconds=args.seconds
        )
        entry: dict[str, object] = {
            "single": single,
            "batch": batch,
            "comparison": comparison(single, batch),
        }
        if name in {"F3_N41", "F4_N41"}:
            eager = run_relaxation(
                config, "eager", max_models=args.models, time_limit_seconds=args.seconds
            )
            entry["eager"] = eager
            entry["eager_static_combination_count"] = math.comb(
                config.n, config.forbidden_clique_size
            )
        production[name] = entry
    result = {
        "schema_version": 1,
        "benchmark_kind": "bounded non-production in-memory relaxation",
        "limits": {"search_seconds_per_trial": args.seconds, "model_cap": args.models},
        "journal_snapshots": [
            analyze_journal(path, args.sample_limit) for path in args.journal_run
        ],
        "smoke": {"summary": smoke_summary, "trials": smoke_trials},
        "production_dimension": production,
        "caveats": [
            "No production run directory is created or modified.",
            "The bounded trials do not establish UNSAT and emit no proof certificate.",
            "Initialization and search time are reported separately.",
            "Different learned clauses cause solver trajectories to diverge after batching.",
        ],
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        v2.atomic_write_json(args.output, result)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
