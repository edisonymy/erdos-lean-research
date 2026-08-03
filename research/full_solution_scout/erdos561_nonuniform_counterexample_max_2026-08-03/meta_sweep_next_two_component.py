#!/usr/bin/env python3
"""One capped meta-sweep over all next uncovered 2-by-2 #561 tuples <=10.

The program first enumerates every unordered pair of descending positive
two-entry degree sequences whose conjectured formula is at most 10.  It
filters proved families before searching.  After the separately completed
formula-8 tuple, exactly two uncovered tuples remain.  They are ranked by a
structural failure heuristic and checked against one shared complete nauty
catalogue of isolate-free hosts through nine edges.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GENG = ROOT / ".tmp" / "nauty-env" / "Library" / "bin" / "geng.exe"
OUT = HERE / "meta_sweep_result.json"
WITNESSES = HERE / "meta_sweep_avoiding_colorings.json"
MAX_FORMULA = 10
MAX_HOST_EDGES = MAX_FORMULA - 1


def formula_layers(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int, int]:
    return (
        a[0] + b[0] - 1,
        max(a[0] + b[1] - 1, a[1] + b[0] - 1),
        a[1] + b[1] - 1,
    )


def proved_family_reasons(a: tuple[int, int], b: tuple[int, int]) -> list[str]:
    """Conservative primary-theorem filter specialized to two components each."""
    reasons: list[str] = []
    if a[0] == a[1] and b[0] == b[1]:
        reasons.append("BEFRS_uniform_both")
    if all(value % 2 == 1 for value in a + b):
        reasons.append("Cheng14_and_DJKR2.5_all_odd")
    if a == (1, 1) or b == (1, 1):
        reasons.append("Cheng14_one_side_matching")
    # With equal component counts, if both tails are 1 we may orient the
    # colors so the larger top degree is a_1; Cheng 18 then applies.
    if a[1] == 1 and b[1] == 1:
        reasons.append("Cheng18_both_tails_one")
    # DJKR Theorem 2.4: two equal stars versus a forest all of whose degrees
    # are at least two.  It is symmetric under exchanging colors.
    if (a[0] == a[1] and b[1] >= 2) or (b[0] == b[1] and a[1] >= 2):
        reasons.append("DJKR2.4_two_equal_stars_vs_min_degree_two")

    layers = formula_layers(a, b)
    # Use the strict inequality in the primary theorem / DJKR statement,
    # rather than the >= typo/paraphrase in Fu--Luo--Ni v3.
    gyori_schelp = all(
        layer * (layer - 1) // 2 > sum(layers[index:])
        for index, layer in enumerate(layers)
    )
    if gyori_schelp:
        reasons.append("Gyori_Schelp_strict_numeric_condition")
    return reasons


def tuple_audit():
    sequences = [(x, y) for x in range(1, MAX_FORMULA + 1) for y in range(1, x + 1)]
    rows = []
    uncovered = []
    for i, a in enumerate(sequences):
        for b in sequences[i:]:
            layers = formula_layers(a, b)
            value = sum(layers)
            if value > MAX_FORMULA:
                continue
            reasons = proved_family_reasons(a, b)
            row = {
                "a": list(a),
                "b": list(b),
                "layers": list(layers),
                "formula": value,
                "proved_family_reasons": reasons,
                "uncovered": not reasons,
            }
            rows.append(row)
            if not reasons:
                uncovered.append(row)
    return rows, uncovered


def connected_types_from_geng():
    types = []
    stream_hash = hashlib.sha256()
    stderr_rows = []
    for n in range(2, MAX_HOST_EDGES + 2):
        command = [str(GENG), "-cq", str(n), f"1:{MAX_HOST_EDGES}"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert process.stdout is not None
        for raw in process.stdout:
            stream_hash.update(raw)
            graph = nx.from_graph6_bytes(raw.strip())
            m = graph.number_of_edges()
            if 1 <= m <= MAX_HOST_EDGES:
                types.append(
                    {
                        "n": n,
                        "m": m,
                        "edges": tuple(sorted(tuple(sorted(edge)) for edge in graph.edges())),
                        "g6": raw.strip().decode("ascii"),
                    }
                )
        stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
        code = process.wait()
        if code:
            raise RuntimeError(f"geng failed at n={n} with code {code}: {stderr}")
        stderr_rows.append(stderr)
    types.sort(key=lambda row: (row["m"], row["n"], row["g6"]))
    for index, row in enumerate(types):
        row["type_id"] = index
    return types, stream_hash.hexdigest(), stderr_rows


def component_multisets(types: list[dict], total_edges: int):
    def rec(start: int, remaining: int, acc: list[dict]):
        if remaining == 0:
            yield tuple(acc)
            return
        for i in range(start, len(types)):
            component = types[i]
            if component["m"] > remaining:
                break
            acc.append(component)
            yield from rec(i, remaining - component["m"], acc)
            acc.pop()

    yield from rec(0, total_edges, [])


def assemble(components: tuple[dict, ...]):
    offset = 0
    edges = []
    for component in components:
        edges.extend((a + offset, b + offset) for a, b in component["edges"])
        offset += component["n"]
    return offset, tuple(edges)


def star_embeddings(n: int, edges: tuple[tuple[int, int], ...], degree: int):
    incidence: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for edge_index, (a, b) in enumerate(edges):
        incidence[a].append((b, edge_index))
        incidence[b].append((a, edge_index))
    embeddings: set[tuple[frozenset[int], int]] = set()
    for center in range(n):
        for leaves in itertools.combinations(incidence[center], degree):
            vertices = frozenset([center, *(neighbor for neighbor, _ in leaves)])
            mask = sum(1 << edge_index for _, edge_index in leaves)
            embeddings.add((vertices, mask))
    return tuple(embeddings)


def forest_masks(n: int, edges: tuple[tuple[int, int], ...], degrees: tuple[int, int]):
    left = star_embeddings(n, edges, degrees[0])
    right = star_embeddings(n, edges, degrees[1])
    masks: set[int] = set()
    for vertices_a, mask_a in left:
        for vertices_b, mask_b in right:
            if vertices_a.isdisjoint(vertices_b):
                masks.add(mask_a | mask_b)
    return tuple(sorted(masks))


def first_avoiding_coloring(n: int, edges, red_degrees, blue_degrees):
    red_patterns = forest_masks(n, edges, red_degrees)
    blue_patterns = forest_masks(n, edges, blue_degrees)
    full = (1 << len(edges)) - 1
    for red in range(full + 1):
        blue = full ^ red
        if any((red & pattern) == pattern for pattern in red_patterns):
            continue
        if not any((blue & pattern) == pattern for pattern in blue_patterns):
            return red, len(red_patterns), len(blue_patterns)
    return None, len(red_patterns), len(blue_patterns)


def main() -> None:
    started = time.time()
    if not GENG.exists():
        raise FileNotFoundError(GENG)
    audit_rows, uncovered = tuple_audit()
    expected_uncovered = {
        ((2, 1), (2, 2), 8),
        ((2, 1), (3, 2), 9),
        ((2, 2), (3, 1), 10),
    }
    actual_uncovered = {
        (tuple(row["a"]), tuple(row["b"]), row["formula"]) for row in uncovered
    }
    if actual_uncovered != expected_uncovered:
        raise AssertionError(f"unexpected theorem-filter result: {actual_uncovered}")

    # The formula-8 row was already exhaustively checked and independently
    # audited.  Rank the two remaining rows by structural distance from known
    # families rather than lexicographically.
    rank_keys = {
        ((2, 1), (3, 2)): 1,  # both targets nonuniform; furthest from exact families
        ((2, 2), (3, 1)): 2,  # one uniform; misses DJKR 2.4 only through tail degree 1
    }
    targets = [
        row for row in uncovered
        if (tuple(row["a"]), tuple(row["b"])) in rank_keys
    ]
    targets.sort(key=lambda row: rank_keys[(tuple(row["a"]), tuple(row["b"]))])
    targets[0]["structural_rank_reason"] = (
        "both forests are nonuniform and mixed-parity, so this tuple is furthest from the uniform and all-odd proofs"
    )
    targets[1]["structural_rank_reason"] = (
        "one forest is uniform; the tuple escapes DJKR Theorem 2.4 only because the other forest has a degree-1 tail"
    )

    types, stream_hash, stderr_rows = connected_types_from_geng()
    connected_counts = Counter(row["m"] for row in types)
    host_counts: Counter[int] = Counter()
    target_stats = []
    for rank, target in enumerate(targets, 1):
        target_stats.append(
            {
                "rank": rank,
                "a": target["a"],
                "b": target["b"],
                "layers": target["layers"],
                "formula": target["formula"],
                "edge_ceiling": target["formula"] - 1,
                "structural_rank_reason": target["structural_rank_reason"],
                "hosts_checked": 0,
                "avoiding_colorings_saved": 0,
                "arrowing_hosts": [],
            }
        )
    witness_records = {str(rank): [] for rank in range(1, len(targets) + 1)}

    for m in range(1, MAX_HOST_EDGES + 1):
        for components in component_multisets(types, m):
            n, edges = assemble(components)
            host_counts[m] += 1
            for target_index, target in enumerate(targets):
                stats = target_stats[target_index]
                if m > stats["edge_ceiling"]:
                    continue
                red, red_count, blue_count = first_avoiding_coloring(
                    n, edges, tuple(target["a"]), tuple(target["b"])
                )
                stats["hosts_checked"] += 1
                row = {
                    "n": n,
                    "m": m,
                    "edges": [list(edge) for edge in edges],
                    "component_graph6": [component["g6"] for component in components],
                }
                if red is None:
                    row["red_pattern_count"] = red_count
                    row["blue_pattern_count"] = blue_count
                    stats["arrowing_hosts"].append(row)
                else:
                    row["avoiding_red_mask"] = red
                    witness_records[str(target_index + 1)].append(row)
                    stats["avoiding_colorings_saved"] += 1

    witness_payload = {
        "schema": "erdos561-two-component-meta-sweep-witnesses-v1",
        "targets": [
            {"rank": row["rank"], "a": row["a"], "b": row["b"]}
            for row in target_stats
        ],
        "records_by_rank": witness_records,
    }
    WITNESSES.write_text(json.dumps(witness_payload, indent=2) + "\n", encoding="utf-8")
    any_hit = any(row["arrowing_hosts"] for row in target_stats)
    result = {
        "schema": "erdos561-two-component-meta-sweep-v1",
        "scope": "all genuinely uncovered asymmetric two-component tuples with formula <=10 after the audited formula-8 probe",
        "parameter_audit": audit_rows,
        "uncovered_rows_before_removing_completed_formula_8": uncovered,
        "ranked_targets": target_stats,
        "catalogue": {
            "generator": "nauty geng connected graph6 types followed by component multisets",
            "geng_path": str(GENG),
            "geng_sha256": hashlib.sha256(GENG.read_bytes()).hexdigest(),
            "graph6_stream_sha256": stream_hash,
            "geng_stderr": stderr_rows,
            "connected_type_counts_by_edges": {
                str(m): connected_counts[m] for m in range(1, MAX_HOST_EDGES + 1)
            },
            "host_type_counts_by_edges": {
                str(m): host_counts[m] for m in range(1, MAX_HOST_EDGES + 1)
            },
            "host_types_generated_through_9_edges": sum(host_counts.values()),
        },
        "witness_file": WITNESSES.name,
        "witness_file_sha256": hashlib.sha256(WITNESSES.read_bytes()).hexdigest(),
        "outcome": "COUNTEREXAMPLE_FOUND" if any_hit else "NO_COUNTEREXAMPLE_IN_CAPPED_META_SWEEP",
        "full_problem_resolved": any_hit,
        "stop_rule": "stop after these two rows unless a candidate appears",
        "python_version": sys.version,
        "networkx_version": nx.__version__,
        "elapsed_seconds": time.time() - started,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

    if any_hit:
        # Freeze a single standalone candidate for the two independent
        # definition-level verifiers.
        for stats in target_stats:
            if stats["arrowing_hosts"]:
                candidate = {
                    "red_degrees": stats["a"],
                    "blue_degrees": stats["b"],
                    "formula": stats["formula"],
                    **stats["arrowing_hosts"][0],
                }
                (HERE / "meta_candidate.json").write_text(
                    json.dumps(candidate, indent=2) + "\n", encoding="utf-8"
                )
                break


if __name__ == "__main__":
    main()
