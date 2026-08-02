#!/usr/bin/env python3
"""Bounded, in-memory separation-order diagnostic for F4_N41.

This is deliberately not a SearchSession: it creates no run directory, journal,
lock, checkpoint, or candidate artifact.  Both orders use v4's identical static
CNF and its existing exact cut encoders.  They differ only after every lazy
forbidden K5 in a model has been completely separated.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
V4_PATH = ROOT / "fixed_clique_cegar_v4" / "cegar.py"


def load_v4() -> object:
    spec = importlib.util.spec_from_file_location("_order_benchmark_v4", V4_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {V4_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


v4 = load_v4()
v3 = v4.v3


def add_forbidden(problem: object, graph: object, config: object, sequence: int) -> int:
    """Complete lazy K5 separation, exactly as v4 does before any other oracle."""

    cliques = v4.enumerate_cliques_exact(graph.adjacency(), config.forbidden_clique_size)
    if not cliques:
        return 0
    items = [
        v3.make_batch_item("forbidden_clique", {"vertices": list(vertices)})
        for vertices in cliques
    ]
    encoding = problem.build_cut(
        "forbidden_clique_batch", {"items": items, "logical_cut_count": len(items)}, sequence
    )
    problem.add_encoding(encoding)
    return len(items)


def add_residual(problem: object, graph: object, config: object, sequence: int) -> int:
    result = v4.residual_admissibility_oracle(config, graph)
    if result is None:
        return 0
    # Semantic audit before committing: the exact v4 validator's shape test and
    # a fresh ambient admissibility check for every translated ten-set.
    maximal = v4._nontrivial_maximal(graph.adjacency())
    for item in result.items:
        _, _, _, vertices = v4._validated_residual_translation_shape(config, item)
        members = sum(1 << vertex for vertex in vertices)
        if any((mask & ~members) == 0 for mask in maximal):
            raise AssertionError("residual translation is not globally admissible")
    witness = {
        "items": list(result.items),
        "logical_cut_count": len(result.items),
        "searches": list(result.searches),
        "separation_order": "benchmark",
    }
    encoding = problem.build_cut("residual_admissibility_batch", witness, sequence)
    problem.add_encoding(encoding)
    return len(result.items)


def add_generic(problem: object, graph: object, config: object, sequence: int) -> int:
    result = v3.admissibility_oracle_batch(
        graph, config.target_set_size, config.admissibility_batch_size
    )
    if result is None:
        return 0
    maximal = v4._nontrivial_maximal(graph.adjacency())
    items = []
    for vertices in result.vertex_sets:
        if len(vertices) != config.target_set_size or len(set(vertices)) != len(vertices):
            raise AssertionError("generic oracle did not return a ten-set")
        members = sum(1 << vertex for vertex in vertices)
        if any((mask & ~members) == 0 for mask in maximal):
            raise AssertionError("generic oracle did not return an admissible set")
        items.append(
            v3.make_batch_item(
                "admissibility",
                {
                    "vertices": list(vertices),
                    "candidate_nontrivial_maximal_clique_count": result.maximal_clique_count,
                },
            )
        )
    encoding = problem.build_cut(
        "admissibility_batch",
        {
            "items": items,
            "logical_cut_count": len(items),
            "requested_batch_limit": config.admissibility_batch_size,
            "enumeration_exhausted": result.enumeration_exhausted,
            "oracle_solver_calls": result.solver_calls,
        },
        sequence,
    )
    problem.add_encoding(encoding)
    return len(items)


def add_arrowing(problem: object, graph: object, sequence: int) -> bool:
    result = v4.coloring_oracle(graph)
    if result is None:
        return False
    # The color oracle itself checks this condition; recheck it here so this
    # benchmark never relies on an ordering-only assumption for cut soundness.
    edges = v4.EdgeVariables(graph.n)
    for a, b, c in v4.triangles(graph.adjacency()):
        colors = (
            result.total_colors[edges.index[(a, b)]],
            result.total_colors[edges.index[(a, c)]],
            result.total_colors[edges.index[(b, c)]],
        )
        if colors[0] == colors[1] == colors[2]:
            raise AssertionError("arrowing oracle returned a monochromatic present triangle")
    encoding = problem.build_cut(
        "arrowing", {"total_coloring_hex": v4.pack_bits(result.total_colors)}, sequence
    )
    problem.add_encoding(encoding)
    return True


def timed(callable_: object) -> tuple[object, float]:
    started = time.perf_counter()
    value = callable_()
    return value, time.perf_counter() - started


def fresh_trial(order: str, model_cap: int, seconds: float, trial: int) -> dict[str, object]:
    """Run exactly one in-memory outer trajectory with a matched model cap."""

    if order not in {"residual_first", "arrowing_first"}:
        raise ValueError(order)
    config = v4.load_cases()["F4_N41"]
    problem = v4.OuterProblem(config)
    models = 0
    sequence = 0
    k_free = 0
    reached = Counter()
    batches = Counter()
    logical = Counter()
    oracle_seconds = Counter()
    terminal = "MODEL_LIMIT"
    started = time.perf_counter()
    try:
        while models < model_cap:
            if time.perf_counter() - started >= seconds:
                terminal = "TIME_LIMIT"
                break
            graph = problem.solve()
            if graph is None:
                terminal = "OUTER_UNSAT_NO_PROOF_CERTIFICATE"
                break
            models += 1
            count = add_forbidden(problem, graph, config, sequence)
            if count:
                batches["forbidden_clique"] += 1
                logical["forbidden_clique"] += count
                sequence += 1
                continue

            k_free += 1
            if order == "arrowing_first":
                reached["arrowing"] += 1
                found, elapsed = timed(lambda: add_arrowing(problem, graph, sequence))
                oracle_seconds["arrowing"] += elapsed
                if found:
                    batches["arrowing"] += 1
                    logical["arrowing"] += 1
                    sequence += 1
                    continue

            reached["residual"] += 1
            count, elapsed = timed(lambda: add_residual(problem, graph, config, sequence))
            oracle_seconds["residual"] += elapsed
            if count:
                batches["residual_admissibility"] += 1
                logical["residual_admissibility"] += count
                sequence += 1
                continue

            reached["generic_admissibility"] += 1
            count, elapsed = timed(lambda: add_generic(problem, graph, config, sequence))
            oracle_seconds["generic_admissibility"] += elapsed
            if count:
                batches["generic_admissibility"] += 1
                logical["generic_admissibility"] += count
                sequence += 1
                continue

            if order == "residual_first":
                reached["arrowing"] += 1
                found, elapsed = timed(lambda: add_arrowing(problem, graph, sequence))
                oracle_seconds["arrowing"] += elapsed
                if found:
                    batches["arrowing"] += 1
                    logical["arrowing"] += 1
                    sequence += 1
                    continue
            terminal = "CANDIDATE_NO_INDEPENDENT_VERIFICATION"
            break
    finally:
        problem.close()
    return {
        "trial": trial,
        "order": order,
        "outer_models": models,
        "k5_free_models": k_free,
        "cut_batches": dict(sorted(batches.items())),
        "logical_cuts": dict(sorted(logical.items())),
        "total_logical_cuts": sum(logical.values()),
        "models_reaching_oracle": dict(sorted(reached.items())),
        "oracle_seconds": {key: round(value, 6) for key, value in sorted(oracle_seconds.items())},
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "terminal": terminal,
    }


def first_k5_free_probe() -> dict[str, object]:
    """Time all three dynamic oracles on the same uncommitted first K5-free model."""

    config = v4.load_cases()["F4_N41"]
    problem = v4.OuterProblem(config)
    models = 0
    sequence = 0
    try:
        while True:
            graph = problem.solve()
            if graph is None:
                return {"terminal": "OUTER_UNSAT_NO_PROOF_CERTIFICATE", "outer_models": models}
            models += 1
            count = add_forbidden(problem, graph, config, sequence)
            if count:
                sequence += 1
                continue
            residual, residual_seconds = timed(lambda: v4.residual_admissibility_oracle(config, graph))
            arrowing, arrowing_seconds = timed(lambda: v4.coloring_oracle(graph))
            generic, generic_seconds = timed(
                lambda: v3.admissibility_oracle_batch(
                    graph, config.target_set_size, config.admissibility_batch_size
                )
            )
            return {
                "terminal": "MATCHED_K5_FREE_MODEL",
                "outer_models": models,
                "graph_sha256": graph.graph_sha256,
                "residual_found": residual is not None,
                "residual_logical_cuts": 0 if residual is None else len(residual.items),
                "arrowing_found": arrowing is not None,
                "generic_found": generic is not None,
                "generic_logical_cuts": 0 if generic is None else len(generic.vertex_sets),
                "oracle_seconds": {
                    "residual": round(residual_seconds, 6),
                    "arrowing": round(arrowing_seconds, 6),
                    "generic_admissibility": round(generic_seconds, 6),
                },
            }
    finally:
        problem.close()


def median_field(trials: list[dict[str, object]], key: str) -> float:
    return statistics.median(float(trial[key]) for trial in trials)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=int, default=50)
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=HERE / "benchmark_results.json")
    args = parser.parse_args()
    if args.models <= 0 or args.seconds <= 0 or args.repeats <= 0:
        raise ValueError("models, seconds, and repeats must be positive")

    trials: dict[str, list[dict[str, object]]] = {"residual_first": [], "arrowing_first": []}
    # Alternate the order in each repeat to avoid consistently charging module
    # warm-up or host load to one variant.  CaDiCaL exposes no configured seed
    # in this pinned engine, so these are independent fresh deterministic trials.
    for repeat in range(args.repeats):
        orders = ("residual_first", "arrowing_first")
        if repeat % 2:
            orders = tuple(reversed(orders))
        for order in orders:
            trials[order].append(fresh_trial(order, args.models, args.seconds, repeat))

    comparison = {}
    for order, values in trials.items():
        comparison[order] = {
            "median_outer_models": median_field(values, "outer_models"),
            "median_elapsed_seconds": median_field(values, "elapsed_seconds"),
            "median_total_logical_cuts": median_field(values, "total_logical_cuts"),
            "trials": values,
        }
    result = {
        "benchmark": "F4_N41 in-memory dynamic separation-order diagnostic",
        "orders": {
            "residual_first": ["complete_forbidden_cliques", "residual", "generic_admissibility", "arrowing"],
            "arrowing_first": ["complete_forbidden_cliques", "arrowing", "residual", "generic_admissibility"],
        },
        "matched_first_k5_free_probe": first_k5_free_probe(),
        "limits": {"outer_model_cap_per_trial": args.models, "wall_cap_seconds_per_trial": args.seconds, "repeats": args.repeats},
        "source_sha256": v4.collect_source_hashes(),
        "comparison": comparison,
        "caveats": [
            "No SearchSession or run directory is created; this script cannot read, resume, lock, stop, or modify a production run.",
            "The model cap is the primary matched budget; the wall cap is only a safety limit checked between models.",
            "Fresh trials are deterministic under the pinned solver's default configuration; no solver seed option is exposed by this engine.",
            "Different sound cuts make later SAT trajectories diverge, so this is a bounded scheduling diagnostic, not an exhaustion forecast or an UNSAT claim.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
