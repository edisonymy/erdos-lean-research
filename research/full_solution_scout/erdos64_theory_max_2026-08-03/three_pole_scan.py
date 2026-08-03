#!/usr/bin/env python3
"""Exact three-pole composition probe for Erdos--Gyarfas.

For a cubic graph K and a vertex v, K-v is a three-terminal pole whose
terminals are the former neighbours of v.  The pole is *dyadic-safe* when it
has no simple cycle of power-of-two length.  Two safe poles, joined by a
perfect matching of their terminals, form a cubic graph.  Every crossing
cycle uses exactly two matching edges, hence has length p+q+2 for a terminal
path length p in the first pole and the corresponding terminal path length q
in the second.

This script extracts all safe poles from the exact-width-three order-22 cubic
census records, computes their complete terminal path-length signatures, and
tests every signature pairing and terminal bijection.  Any putative hit is
rebuilt and checked directly from its edge list.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


Edge = tuple[int, int]
PAIR_INDICES = ((0, 1), (0, 2), (1, 2))


def decode_graph6(record: str) -> tuple[list[set[int]], list[Edge]]:
    text = record.strip()
    if text.startswith(">>graph6<<"):
        text = text[10:]
    n = ord(text[0]) - 63
    if not 0 <= n <= 62:
        raise ValueError("only small graph6 records are supported")
    bits = "".join(f"{ord(character) - 63:06b}" for character in text[1:])
    if len(text) - 1 != (n * (n - 1) // 2 + 5) // 6:
        raise ValueError("noncanonical graph6 record length")
    adjacency = [set() for _ in range(n)]
    edges: list[Edge] = []
    position = 0
    for right in range(1, n):
        for left in range(right):
            if bits[position] == "1":
                adjacency[left].add(right)
                adjacency[right].add(left)
                edges.append((left, right))
            position += 1
    return adjacency, edges


def canonical_cycles_of_length(
    adjacency: list[set[int]], length: int
) -> Iterable[tuple[int, ...]]:
    """Enumerate each undirected simple cycle once as a vertex tuple."""
    n = len(adjacency)
    if length > n:
        return
    for root in range(n):
        allowed = set(range(root + 1, n))
        for first in sorted(adjacency[root] & allowed):
            path = [root, first]
            used = {root, first}

            def visit(vertex: int) -> Iterable[tuple[int, ...]]:
                if len(path) == length:
                    if root in adjacency[vertex] and path[1] < path[-1]:
                        yield tuple(path)
                    return
                for nxt in sorted((adjacency[vertex] & allowed) - used):
                    used.add(nxt)
                    path.append(nxt)
                    yield from visit(nxt)
                    path.pop()
                    used.remove(nxt)

            yield from visit(first)


def dyadic_vertex_core(adjacency: list[set[int]]) -> tuple[set[int], Counter[int]]:
    core = set(range(len(adjacency)))
    counts: Counter[int] = Counter()
    saw = False
    for length in (4, 8, 16, 32, 64):
        if length > len(adjacency):
            continue
        for cycle in canonical_cycles_of_length(adjacency, length):
            saw = True
            counts[length] += 1
            core.intersection_update(cycle)
            if not core:
                # The core cannot recover, but finish the current graph only
                # when callers need counts.  Here safe-pole extraction does
                # not, so the early decision is exact.
                return set(), counts
    return (core if saw else set(range(len(adjacency)))), counts


def has_dyadic_cycle(adjacency: list[set[int]]) -> tuple[bool, int | None]:
    for length in (4, 8, 16, 32, 64):
        if length <= len(adjacency):
            for _ in canonical_cycles_of_length(adjacency, length):
                return True, length
    return False, None


def delete_vertex(
    adjacency: list[set[int]], removed: int
) -> tuple[list[set[int]], list[int], dict[int, int]]:
    kept = [vertex for vertex in range(len(adjacency)) if vertex != removed]
    relabel = {old: new for new, old in enumerate(kept)}
    pole = [set() for _ in kept]
    for old in kept:
        pole[relabel[old]] = {
            relabel[other] for other in adjacency[old] if other != removed
        }
    terminals = sorted(relabel[other] for other in adjacency[removed])
    return pole, terminals, relabel


def simple_path_lengths(
    adjacency: list[set[int]], source: int, target: int
) -> tuple[int, ...]:
    lengths: set[int] = set()
    used = {source}

    def visit(vertex: int, length: int) -> None:
        if vertex == target:
            lengths.add(length)
            return
        for nxt in adjacency[vertex] - used:
            used.add(nxt)
            visit(nxt, length + 1)
            used.remove(nxt)

    visit(source, 0)
    return tuple(sorted(lengths))


def pole_signature(
    adjacency: list[set[int]], terminals: list[int]
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    return tuple(
        simple_path_lengths(adjacency, terminals[first], terminals[second])
        for first, second in PAIR_INDICES
    )  # type: ignore[return-value]


def permuted_pair_index(permutation: tuple[int, int, int], pair: tuple[int, int]) -> int:
    image = tuple(sorted((permutation[pair[0]], permutation[pair[1]])))
    return PAIR_INDICES.index(image)


def signatures_compatible(
    left: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
    right: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]],
    permutation: tuple[int, int, int],
    max_order: int,
) -> bool:
    powers = {power for power in (4, 8, 16, 32, 64, 128) if power <= max_order}
    for left_index, pair in enumerate(PAIR_INDICES):
        right_index = permuted_pair_index(permutation, pair)
        for first_length in left[left_index]:
            for second_length in right[right_index]:
                if first_length + second_length + 2 in powers:
                    return False
    return True


def edge_set(adjacency: list[set[int]]) -> list[Edge]:
    return [
        (left, right)
        for left, row in enumerate(adjacency)
        for right in sorted(row)
        if left < right
    ]


def glue_poles(
    left: list[set[int]],
    left_terminals: list[int],
    right: list[set[int]],
    right_terminals: list[int],
    permutation: tuple[int, int, int],
) -> list[set[int]]:
    offset = len(left)
    result = [set(row) for row in left] + [
        {other + offset for other in row} for row in right
    ]
    for index, left_terminal in enumerate(left_terminals):
        right_terminal = right_terminals[permutation[index]] + offset
        result[left_terminal].add(right_terminal)
        result[right_terminal].add(left_terminal)
    return result


def connected(adjacency: list[set[int]]) -> bool:
    reached = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for other in adjacency[vertex] - reached:
            reached.add(other)
            stack.append(other)
    return len(reached) == len(adjacency)


def load_width_three_records(paths: list[Path]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in paths:
        source = json.loads(path.read_text(encoding="utf-8"))
        for item in source["no_pair_examples"]:
            graph6 = item["graph6"]
            if graph6 in seen:
                continue
            seen.add(graph6)
            records.append(
                {
                    "graph6": graph6,
                    "source": str(path),
                    "physical_line": item["physical_line"],
                }
            )
    return records


def canonical_signature(
    signature: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    variants = []
    for permutation in itertools.permutations(range(3)):
        variants.append(
            tuple(
                signature[permuted_pair_index(permutation, pair)]
                for pair in PAIR_INDICES
            )
        )
    return min(variants)  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument(
        "--scope",
        default="safe vertex-deletion poles from supplied exact hard-core census records",
    )
    args = parser.parse_args()

    records = load_width_three_records(args.inputs)
    stats: Counter[str] = Counter()
    poles: list[dict[str, object]] = []
    for record in records:
        adjacency, _ = decode_graph6(str(record["graph6"]))
        if any(len(row) != 3 for row in adjacency):
            raise AssertionError("source is not cubic")
        core, partial_counts = dyadic_vertex_core(adjacency)
        stats["source_graphs"] += 1
        stats["source_dyadic_cycles_seen_until_vertex_core_decision"] += sum(
            partial_counts.values()
        )
        if core:
            stats["source_graphs_with_nonempty_dyadic_vertex_core"] += 1
        for vertex in sorted(core):
            stats["candidate_vertex_deletions"] += 1
            pole, terminals, _ = delete_vertex(adjacency, vertex)
            if len(terminals) != 3 or sorted(map(len, pole)).count(2) != 3:
                raise AssertionError("malformed three-pole")
            if not connected(pole):
                raise AssertionError("vertex deletion did not produce a connected three-pole")
            unsafe, unsafe_length = has_dyadic_cycle(pole)
            if unsafe:
                raise AssertionError(
                    f"vertex-core deletion retained C{unsafe_length}: {record['graph6']} v={vertex}"
                )
            signature = pole_signature(pole, terminals)
            stats["safe_poles"] += 1
            stats[f"safe_pole_order_{len(pole)}"] += 1
            poles.append(
                {
                    **record,
                    "deleted_vertex": vertex,
                    "pole_order": len(pole),
                    "terminals": terminals,
                    "edges": [list(edge) for edge in edge_set(pole)],
                    "signature": [list(lengths) for lengths in signature],
                    "canonical_signature": [
                        list(lengths) for lengths in canonical_signature(signature)
                    ],
                }
            )

    by_signature: dict[
        tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]], list[int]
    ] = defaultdict(list)
    for index, pole in enumerate(poles):
        signature = tuple(tuple(lengths) for lengths in pole["signature"])
        by_signature[signature].append(index)  # type: ignore[arg-type]
    stats["labelled_signatures"] = len(by_signature)
    stats["canonical_signatures"] = len(
        {
            tuple(tuple(lengths) for lengths in pole["canonical_signature"])
            for pole in poles
        }
    )

    permutations = list(itertools.permutations(range(3)))
    signature_items = list(by_signature.items())
    compatible: dict[str, object] | None = None
    for left_type, (left_signature, left_indices) in enumerate(signature_items):
        for right_type in range(left_type, len(signature_items)):
            right_signature, right_indices = signature_items[right_type]
            stats["signature_pairs"] += 1
            order = int(poles[left_indices[0]]["pole_order"]) + int(
                poles[right_indices[0]]["pole_order"]
            )
            for permutation in permutations:
                stats["signature_pair_bijections"] += 1
                if not signatures_compatible(
                    left_signature, right_signature, permutation, order
                ):
                    continue
                stats["compatible_signature_bijections"] += 1
                left_record = poles[left_indices[0]]
                right_record = poles[right_indices[0]]
                left_adjacency = [set() for _ in range(int(left_record["pole_order"]))]
                right_adjacency = [set() for _ in range(int(right_record["pole_order"]))]
                for u, v in left_record["edges"]:
                    left_adjacency[u].add(v)
                    left_adjacency[v].add(u)
                for u, v in right_record["edges"]:
                    right_adjacency[u].add(v)
                    right_adjacency[v].add(u)
                glued = glue_poles(
                    left_adjacency,
                    list(left_record["terminals"]),
                    right_adjacency,
                    list(right_record["terminals"]),
                    permutation,
                )
                valid = (
                    connected(glued)
                    and all(len(row) == 3 for row in glued)
                    and not has_dyadic_cycle(glued)[0]
                )
                if not valid:
                    raise AssertionError("signature-compatible gluing failed direct verification")
                compatible = {
                    "left_pole_index": left_indices[0],
                    "right_pole_index": right_indices[0],
                    "terminal_permutation": list(permutation),
                    "order": len(glued),
                    "edges": [list(edge) for edge in edge_set(glued)],
                    "edge_sha256": hashlib.sha256(
                        (json.dumps(edge_set(glued), separators=(",", ":")) + "\n").encode()
                    ).hexdigest(),
                    "direct_verification": {
                        "connected": connected(glued),
                        "simple_cubic": all(len(row) == 3 for row in glued),
                        "dyadic_cycle": None,
                    },
                }
                break
            if compatible is not None:
                break
        if compatible is not None:
            break

    payload = {
        "schema": "erdos64-three-pole-composition-scan-v1",
        "scope": args.scope,
        "inputs": [str(path) for path in args.inputs],
        "input_sha256": {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in args.inputs
        },
        "stats": dict(stats),
        "poles": poles,
        "candidate": compatible,
        "complete": True,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if compatible is not None and args.candidate is not None:
        args.candidate.write_text(
            json.dumps(compatible, indent=2) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "stats": payload["stats"],
                "candidate_found": compatible is not None,
                "candidate": compatible,
            },
            sort_keys=True,
        )
    )
    return 10 if compatible is not None else 0


if __name__ == "__main__":
    raise SystemExit(main())
