#!/usr/bin/env python3
"""Scan the complete order-24 hard-core pair-insertion family for safe 3-poles.

This is orthogonal to the marked-edge scan of the same operation family: it
intersects *vertices* of dyadic cycles.  A surviving vertex can be deleted to
give a dyadic-safe three-terminal pole for the exact gluing theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

from three_pole_scan import (
    PAIR_INDICES,
    canonical_signature,
    connected,
    decode_graph6,
    delete_vertex,
    dyadic_vertex_core,
    edge_set,
    glue_poles,
    has_dyadic_cycle,
    pole_signature,
    signatures_compatible,
)


Edge = tuple[int, int]


def insert_edge_pair(
    adjacency: list[set[int]], first: Edge, second: Edge
) -> list[set[int]]:
    n = len(adjacency)
    result = [set(row) for row in adjacency] + [set(), set()]
    for (u, v), new in ((first, n), (second, n + 1)):
        result[u].remove(v)
        result[v].remove(u)
        result[u].add(new)
        result[v].add(new)
        result[new].update((u, v))
    result[n].add(n + 1)
    result[n + 1].add(n)
    return result


def source_records(paths: list[Path]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for part, path in enumerate(paths):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for record in payload["no_pair_examples"]:
            result.append(
                {
                    "part": part,
                    "physical_line": record["physical_line"],
                    "graph6": record["graph6"],
                }
            )
    return result


def adjacency_from_edges(order: int, edges: list[list[int]]) -> list[set[int]]:
    result = [set() for _ in range(order)]
    for u, v in edges:
        result[u].add(v)
        result[v].add(u)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()

    sources = source_records(args.inputs)
    if len(sources) != 645:
        raise ValueError(f"expected 645 sources, found {len(sources)}")
    stats: Counter[str] = Counter()
    poles: list[dict[str, object]] = []
    for source in sources:
        adjacency, source_edges = decode_graph6(str(source["graph6"]))
        for first, second in itertools.combinations(source_edges, 2):
            child = insert_edge_pair(adjacency, first, second)
            if not connected(child) or any(len(row) != 3 for row in child):
                raise AssertionError("edge-pair insertion did not produce a connected cubic graph")
            stats["operation_instances"] += 1
            core, counts = dyadic_vertex_core(child)
            stats["dyadic_cycles_seen_until_decision"] += sum(counts.values())
            if core:
                stats["children_with_nonempty_dyadic_vertex_core"] += 1
            for vertex in sorted(core):
                pole, terminals, _ = delete_vertex(child, vertex)
                if not connected(pole):
                    raise AssertionError("vertex deletion did not produce a connected three-pole")
                unsafe, length = has_dyadic_cycle(pole)
                if unsafe:
                    raise AssertionError(f"core deletion retained C{length}")
                signature = pole_signature(pole, terminals)
                stats["safe_poles"] += 1
                poles.append(
                    {
                        "source": source,
                        "source_edge_pair": [list(first), list(second)],
                        "deleted_vertex": vertex,
                        "pole_order": len(pole),
                        "terminals": terminals,
                        "edges": [list(item) for item in edge_set(pole)],
                        "signature": [list(lengths) for lengths in signature],
                        "canonical_signature": [
                            list(lengths) for lengths in canonical_signature(signature)
                        ],
                    }
                )

    by_signature: dict[tuple[tuple[int, ...], ...], list[int]] = defaultdict(list)
    for index, pole in enumerate(poles):
        signature = tuple(tuple(lengths) for lengths in pole["signature"])
        by_signature[signature].append(index)
    stats["labelled_signatures"] = len(by_signature)
    stats["canonical_signatures"] = len(
        {
            tuple(tuple(lengths) for lengths in pole["canonical_signature"])
            for pole in poles
        }
    )

    candidate: dict[str, object] | None = None
    signature_items = list(by_signature.items())
    for left_type, (left_signature, left_indices) in enumerate(signature_items):
        for right_type in range(left_type, len(signature_items)):
            right_signature, right_indices = signature_items[right_type]
            stats["signature_pairs"] += 1
            order = int(poles[left_indices[0]]["pole_order"]) + int(
                poles[right_indices[0]]["pole_order"]
            )
            for permutation in itertools.permutations(range(3)):
                stats["signature_pair_bijections"] += 1
                if not signatures_compatible(
                    left_signature, right_signature, permutation, order  # type: ignore[arg-type]
                ):
                    continue
                stats["compatible_signature_bijections"] += 1
                left_record = poles[left_indices[0]]
                right_record = poles[right_indices[0]]
                left = adjacency_from_edges(
                    int(left_record["pole_order"]), left_record["edges"]
                )
                right = adjacency_from_edges(
                    int(right_record["pole_order"]), right_record["edges"]
                )
                glued = glue_poles(
                    left,
                    list(left_record["terminals"]),
                    right,
                    list(right_record["terminals"]),
                    permutation,
                )
                unsafe, unsafe_length = has_dyadic_cycle(glued)
                if unsafe or not connected(glued) or any(len(row) != 3 for row in glued):
                    raise AssertionError(
                        f"signature-compatible gluing failed direct check: C{unsafe_length}"
                    )
                candidate = {
                    "left_pole": left_record,
                    "right_pole": right_record,
                    "terminal_permutation": list(permutation),
                    "order": len(glued),
                    "edges": [list(item) for item in edge_set(glued)],
                    "direct_verification": {
                        "connected": True,
                        "simple_cubic": True,
                        "dyadic_cycle": None,
                    },
                }
                break
            if candidate is not None:
                break
        if candidate is not None:
            break

    payload = {
        "schema": "erdos64-pair-insertion-vertex-pole-scan-v1",
        "scope": "all 340560 edge-pair insertions from all 645 order-22 width-three sources",
        "inputs": [str(path) for path in args.inputs],
        "input_sha256": {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in args.inputs
        },
        "stats": dict(stats),
        "poles": poles,
        "candidate": candidate,
        "complete": stats["operation_instances"] == 340560,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if candidate is not None and args.candidate is not None:
        args.candidate.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "stats": payload["stats"],
                "candidate_found": candidate is not None,
                "complete": payload["complete"],
            },
            sort_keys=True,
        )
    )
    return 10 if candidate is not None else 0 if payload["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
