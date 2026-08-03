#!/usr/bin/env python3
"""Independent standard-library audit of the a=10, q=6 residual gate.

This auditor deliberately imports neither topology producer nor Z3.  It:

1. independently parses and filters the nauty ``geng`` stream;
2. independently constructs the 166 path/cycle length topologies;
3. enumerates simple paths directly in the subdivided fixed skeleton;
4. builds every locally admissible path/cycle component signature; and
5. uses exact set-packing DP to test endpoint and color multiplicities.

No full residual graph is discarded unless a single R segment plus a simple
fixed-skeleton path already makes C4, C8, C16, or C32.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
from pathlib import Path


Edge = tuple[int, int]
CountVector = tuple[int, ...]


def decode_graph6(record: bytes) -> list[set[int]]:
    data = record.rstrip(b"\r\n")
    if not data:
        raise ValueError("empty graph6 record")
    order = data[0] - 63
    if not 0 <= order <= 62:
        raise ValueError("extended graph6 order is outside this audit")
    payload = []
    for char in data[1:]:
        value = char - 63
        if not 0 <= value < 64:
            raise ValueError("bad graph6 byte")
        payload.extend((value >> bit) & 1 for bit in range(5, -1, -1))
    graph = [set() for _ in range(order)]
    cursor = 0
    for high in range(1, order):
        for low in range(high):
            if payload[cursor]:
                graph[low].add(high)
                graph[high].add(low)
            cursor += 1
    return graph


def graph_edges(graph: list[set[int]]) -> tuple[Edge, ...]:
    return tuple(
        sorted((u, v) for u in range(len(graph)) for v in graph[u] if u < v)
    )


def is_two_degenerate(graph: list[set[int]]) -> bool:
    remaining = set(range(len(graph)))
    while remaining:
        low = next(
            (v for v in remaining if len(graph[v] & remaining) <= 2), None
        )
        if low is None:
            return False
        remaining.remove(low)
    return True


def contains_cycle(graph: list[set[int]], length: int) -> bool:
    order = len(graph)
    for start in range(order):
        def search(last: int, path: tuple[int, ...]) -> bool:
            if len(path) == length:
                return start in graph[last]
            for nxt in graph[last]:
                if nxt <= start or nxt in path:
                    continue
                if search(nxt, (*path, nxt)):
                    return True
            return False

        for first in graph[start]:
            if first > start and search(first, (start, first)):
                return True
    return False


def independent_kernel_scan(geng: Path) -> tuple[list[tuple[str, tuple[Edge, ...]]], dict[str, object]]:
    proc = subprocess.Popen(
        [str(geng), "-q", "-c", "-d2", "-D4", "10", "14"],
        stdout=subprocess.PIPE,
    )
    assert proc.stdout is not None
    stream = bytearray()
    eligible = []
    raw_count = 0
    two_deg_count = 0
    c4_free_count = 0
    c8_free_count = 0
    for record in proc.stdout:
        stream.extend(record)
        raw_count += 1
        graph = decode_graph6(record)
        if not is_two_degenerate(graph):
            continue
        two_deg_count += 1
        if contains_cycle(graph, 4):
            continue
        c4_free_count += 1
        if contains_cycle(graph, 8):
            continue
        c8_free_count += 1
        eligible.append((record.decode("ascii").strip(), graph_edges(graph)))
    if proc.wait():
        raise RuntimeError("geng failed")
    return eligible, {
        "raw_records": raw_count,
        "raw_stream_sha256": hashlib.sha256(stream).hexdigest().upper(),
        "two_degenerate": two_deg_count,
        "then_c4_free": c4_free_count,
        "then_c8_free": c8_free_count,
        "eligible_graph6": [code for code, _ in eligible],
    }


def integer_partitions(total: int, least: int = 1):
    if total == 0:
        yield ()
        return
    for first in range(least, total + 1):
        for tail in integer_partitions(total - first, first):
            yield (first, *tail)


def independent_topologies() -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    answer = set()
    for paths in itertools.combinations_with_replacement(range(13), 7):
        used = sum(paths)
        if used > 12:
            continue
        remainder = 12 - used
        for cycles in integer_partitions(remainder):
            if all(part >= 3 and part not in (4, 8) for part in cycles):
                answer.add((paths, cycles))
    return sorted(answer)


def build_subdivided_skeleton(j_edges: tuple[Edge, ...]) -> list[set[int]]:
    graph = [set() for _ in range(10 + len(j_edges))]
    for label, (u, v) in enumerate(j_edges):
        middle = 10 + label
        graph[u].add(middle)
        graph[middle].add(u)
        graph[v].add(middle)
        graph[middle].add(v)
    return graph


def all_simple_path_lengths(graph: list[set[int]], source: int, target: int) -> set[int]:
    answer: set[int] = set()

    def search(last: int, used: int, length: int) -> None:
        if last == target:
            answer.add(length)
            return
        for nxt in graph[last]:
            if used & (1 << nxt):
                continue
            search(nxt, used | (1 << nxt), length + 1)

    search(source, 1 << source, 0)
    return answer


def append_leaf(graph: list[set[int]], neighbor: int) -> tuple[list[set[int]], int]:
    clone = [set(row) for row in graph]
    leaf = len(clone)
    clone.append({neighbor})
    clone[neighbor].add(leaf)
    return clone, leaf


def direct_skeleton_relations(j_edges: tuple[Edge, ...]):
    base = build_subdivided_skeleton(j_edges)
    d2 = len(j_edges)
    color_color = [[set() for _ in range(10)] for _ in range(10)]
    for left in range(10):
        one_leaf_graph, source = append_leaf(base, left)
        for right in range(10):
            two_leaf_graph, target = append_leaf(one_leaf_graph, right)
            color_color[left][right] = all_simple_path_lengths(
                two_leaf_graph, source, target
            )
    edge_color = [[set() for _ in range(10)] for _ in range(d2)]
    for edge_label in range(d2):
        source = 10 + edge_label
        for color in range(10):
            graph, target = append_leaf(base, color)
            edge_color[edge_label][color] = all_simple_path_lengths(
                graph, source, target
            )
    edge_edge = [[set() for _ in range(d2)] for _ in range(d2)]
    for left in range(d2):
        for right in range(d2):
            if left != right:
                edge_edge[left][right] = all_simple_path_lengths(
                    base, 10 + left, 10 + right
                )
    return color_color, edge_color, edge_edge


def relation_masks(path_lengths, maximum_distance: int, powers: tuple[int, ...]):
    rows = []
    left_count = len(path_lengths)
    right_count = len(path_lengths[0])
    for distance in range(maximum_distance + 1):
        relation = [0] * left_count
        for left in range(left_count):
            for right in range(right_count):
                if all(distance + length not in powers for length in path_lengths[left][right]):
                    relation[left] |= 1 << right
        rows.append(relation)
    return rows


def add_counts(left: CountVector, right: CountVector) -> CountVector:
    return tuple(x + y for x, y in zip(left, right))


def bounded(counts: CountVector, target: CountVector) -> bool:
    return all(x <= y for x, y in zip(counts, target))


def enumerate_color_signatures(
    length: int,
    target: CountVector,
    pair_relations: list[list[int]],
    initial_domains: list[int],
    cyclic: bool,
) -> tuple[set[CountVector], int]:
    if length == 0:
        return {tuple(0 for _ in target)}, 1
    assignments = [-1] * length
    used = [0] * len(target)
    signatures: set[CountVector] = set()
    nodes = 0

    def allowed_between(i: int, j: int, ci: int, cj: int) -> bool:
        delta = abs(i - j)
        if not (pair_relations[delta][ci] & (1 << cj)):
            return False
        if cyclic and not (pair_relations[length - delta][ci] & (1 << cj)):
            return False
        return True

    def domain(position: int) -> int:
        mask = initial_domains[position]
        for color, cap in enumerate(target):
            if used[color] >= cap:
                mask &= ~(1 << color)
        for other, other_color in enumerate(assignments):
            if other_color < 0:
                continue
            permitted = 0
            probe = mask
            while probe:
                bit = probe & -probe
                color = bit.bit_length() - 1
                if allowed_between(position, other, color, other_color):
                    permitted |= bit
                probe ^= bit
            mask = permitted
        return mask

    def search(depth: int) -> None:
        nonlocal nodes
        nodes += 1
        if depth == length:
            signatures.add(tuple(used))
            return
        best = -1
        best_domain = 0
        best_size = len(target) + 1
        for position, current in enumerate(assignments):
            if current >= 0:
                continue
            mask = domain(position)
            size = mask.bit_count()
            if size == 0:
                return
            if size < best_size:
                best, best_domain, best_size = position, mask, size
        probe = best_domain
        while probe:
            bit = probe & -probe
            color = bit.bit_length() - 1
            assignments[best] = color
            used[color] += 1
            search(depth + 1)
            used[color] -= 1
            assignments[best] = -1
            probe ^= bit

    search(0)
    return signatures, nodes


def component_signature_tables(j_edges: tuple[Edge, ...]):
    degree = [0] * 10
    for u, v in j_edges:
        degree[u] += 1
        degree[v] += 1
    target = tuple(4 - value for value in degree)
    if sum(target) != 12:
        raise AssertionError("bad q=6 multiplicity")
    powers = (4, 8, 16, 32)
    cc_paths, ec_paths, ee_paths = direct_skeleton_relations(j_edges)
    cc = relation_masks(cc_paths, 13, powers)
    ec = relation_masks(ec_paths, 13, powers)
    ee = relation_masks(ee_paths, 13, powers)
    all_colors = (1 << 10) - 1

    path_tables: dict[int, set[tuple[int, CountVector]]] = {}
    cycle_tables: dict[int, set[CountVector]] = {}
    node_counts = {"path": {}, "cycle": {}}
    for length in range(13):
        signatures: set[tuple[int, CountVector]] = set()
        nodes = 0
        distance_between_endpoints = length + 1
        for left in range(14):
            for right in range(14):
                if left == right or not (ee[distance_between_endpoints][left] & (1 << right)):
                    continue
                domains = []
                for index in range(length):
                    from_left = index + 1
                    from_right = length - index
                    mask = all_colors
                    mask &= ec[from_left][left]
                    # ec is edge-to-color and skeleton paths are undirected.
                    permitted_right = 0
                    for color in range(10):
                        if ec[from_right][right] & (1 << color):
                            permitted_right |= 1 << color
                    mask &= permitted_right
                    domains.append(mask)
                color_sigs, visited = enumerate_color_signatures(
                    length, target, cc, domains, False
                )
                nodes += visited
                endpoint_mask = (1 << left) | (1 << right)
                signatures.update((endpoint_mask, counts) for counts in color_sigs)
        path_tables[length] = signatures
        node_counts["path"][str(length)] = nodes

    for length in (3, 5, 6, 7, 9, 10, 11, 12):
        signatures, nodes = enumerate_color_signatures(
            length, target, cc, [all_colors] * length, True
        )
        cycle_tables[length] = signatures
        node_counts["cycle"][str(length)] = nodes
    return target, path_tables, cycle_tables, node_counts


def topology_feasible(
    topology: tuple[tuple[int, ...], tuple[int, ...]],
    target: CountVector,
    paths: dict[int, set[tuple[int, CountVector]]],
    cycles: dict[int, set[CountVector]],
) -> tuple[bool, int]:
    zero = tuple(0 for _ in target)
    states: set[tuple[int, CountVector]] = {(0, zero)}
    transitions = 0
    # Components are unordered.  Processing the smallest signature tables
    # first is an exact join reordering and avoids a large irrelevant prefix.
    for length in sorted(topology[1], key=lambda value: len(cycles[value])):
        next_states = set()
        for used_mask, used_counts in states:
            for component_counts in cycles[length]:
                transitions += 1
                total = add_counts(used_counts, component_counts)
                if bounded(total, target):
                    next_states.add((used_mask, total))
        states = next_states
        if not states:
            return False, transitions
    for length in sorted(topology[0], key=lambda value: len(paths[value])):
        next_states = set()
        for used_mask, used_counts in states:
            for component_mask, component_counts in paths[length]:
                transitions += 1
                if used_mask & component_mask:
                    continue
                total = add_counts(used_counts, component_counts)
                if bounded(total, target):
                    next_states.add((used_mask | component_mask, total))
        states = next_states
        if not states:
            return False, transitions
    return ((1 << 14) - 1, target) in states, transitions


def stable_hash(value: object) -> str:
    payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geng", type=Path, required=True)
    parser.add_argument("--kernel-index", type=int, action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    eligible, kernel_audit = independent_kernel_scan(args.geng)
    if len(eligible) != 4:
        raise AssertionError(f"expected four kernels, got {len(eligible)}")
    topologies = independent_topologies()
    if len(topologies) != 166:
        raise AssertionError(f"expected 166 topologies, got {len(topologies)}")
    indices = args.kernel_index or list(range(4))
    results = []
    for index in indices:
        code, edges = eligible[index]
        target, path_tables, cycle_tables, nodes = component_signature_tables(edges)
        survivors = []
        locally_nonempty = []
        packing_records = []
        transitions = 0
        for topology in topologies:
            if all(path_tables[length] for length in topology[0]) and all(
                cycle_tables[length] for length in topology[1]
            ):
                locally_nonempty.append(topology)
            feasible, work = topology_feasible(
                topology, target, path_tables, cycle_tables
            )
            transitions += work
            if topology in locally_nonempty:
                packing_records.append(
                    {
                        "paths": topology[0],
                        "cycles": topology[1],
                        "feasible": feasible,
                        "transitions": work,
                    }
                )
            if feasible:
                survivors.append(topology)
        signature_summary = {
            "path": {str(k): len(v) for k, v in path_tables.items()},
            "cycle": {str(k): len(v) for k, v in cycle_tables.items()},
        }
        length_one_masks = sorted({mask for mask, _ in path_tables[1]})
        length_two_color_support = sorted(
            {
                color
                for _, counts in path_tables[2]
                for color, count in enumerate(counts)
                if count
            }
        )
        missing_positive_colors = [
            color
            for color, count in enumerate(target)
            if count and color not in length_two_color_support
        ]
        row = {
            "kernel_index": index,
            "kernel_graph6": code,
            "kernel_edges": edges,
            "target_color_counts": target,
            "topologies_checked": len(topologies),
            "locally_nonempty_topologies": locally_nonempty,
            "packing_records": packing_records,
            "surviving_topologies": survivors,
            "status": "VERIFIED_NO_ASSIGNMENT" if not survivors else "SURVIVOR",
            "component_signature_counts": signature_summary,
            "length_one_endpoint_masks": length_one_masks,
            "length_two_color_support": length_two_color_support,
            "length_two_missing_positive_colors": missing_positive_colors,
            "component_signature_hash": stable_hash(
                {
                    "paths": {
                        str(k): sorted((mask, counts) for mask, counts in value)
                        for k, value in path_tables.items()
                    },
                    "cycles": {
                        str(k): sorted(value) for k, value in cycle_tables.items()
                    },
                }
            ),
            "color_search_nodes": nodes,
            "packing_transitions": transitions,
        }
        results.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)

    output = {
        "schema": "erdos64-a10-residual-gate-independent-audit-v1",
        "status": (
            "VERIFIED_COMPLETE_NO_ASSIGNMENT"
            if len(results) == 4 and all(row["status"] == "VERIFIED_NO_ASSIGNMENT" for row in results)
            else "PARTIAL_OR_SURVIVOR"
        ),
        "geng_sha256": hashlib.sha256(args.geng.read_bytes()).hexdigest().upper(),
        "kernel_scan": kernel_audit,
        "topology_count": len(topologies),
        "topology_hash": stable_hash(topologies),
        "results": results,
    }
    if args.output:
        args.output.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    else:
        print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if output["status"] != "PARTIAL_OR_SURVIVOR" else 10


if __name__ == "__main__":
    raise SystemExit(main())
