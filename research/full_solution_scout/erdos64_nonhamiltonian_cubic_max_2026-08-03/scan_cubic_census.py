#!/usr/bin/env python3
"""Exact marked-edge scan of a canonical connected cubic graph6 census.

The input is expected to contain one isomorphism-class representative per
line, as produced by nauty geng with ``-c -d3 -D3``.  This program does not
trust those switches: every record is independently parsed and checked for
simplicity, connectedness, and cubic degree.

Hamiltonicity is decided exactly using the cubic-graph equivalence

    Hamilton cycle <=> a perfect matching whose complementary 2-factor is
                         connected.

The dyadic edge core is computed by searching, for each edge of one initial
dyadic cycle, for a dyadic cycle avoiding that edge.  This is logically
equivalent to intersecting every dyadic cycle edge set but avoids enumerating
irrelevant cycles.  Any survivor is subjected to the Mersenne-cycle test from
the predecessor's suppression lemma.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Iterable


Edge = tuple[int, int]

KNOWN_CONNECTED_CUBIC_COUNTS = {
    4: 1,
    6: 2,
    8: 5,
    10: 19,
    12: 85,
    14: 509,
    16: 4060,
    18: 41301,
    20: 510489,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def parse_graph6(raw: bytes) -> tuple[list[int], list[Edge]]:
    """Parse a small graph6 record (n <= 62) without external libraries."""
    data = raw.strip()
    if data.startswith(b">>graph6<<"):
        data = data[len(b">>graph6<<") :]
    if not data:
        raise ValueError("empty graph6 record")
    n = data[0] - 63
    if not 0 <= n <= 62:
        raise ValueError("only the small graph6 order form is accepted")
    payload = [value - 63 for value in data[1:]]
    if any(not 0 <= value < 64 for value in payload):
        raise ValueError("invalid graph6 character")
    required = (n * (n - 1) // 2 + 5) // 6
    if len(payload) != required:
        raise ValueError(f"graph6 payload has {len(payload)} sextets, expected {required}")

    rows = [0] * n
    edges: list[Edge] = []
    bit_index = 0
    for high in range(1, n):
        for low in range(high):
            sextet = payload[bit_index // 6]
            present = (sextet >> (5 - bit_index % 6)) & 1
            bit_index += 1
            if present:
                rows[low] |= 1 << high
                rows[high] |= 1 << low
                edges.append((low, high))
    return rows, edges


def is_connected(rows: list[int]) -> bool:
    if not rows:
        return False
    seen = 1
    frontier = 1
    while frontier:
        bit = frontier & -frontier
        frontier ^= bit
        vertex = bit.bit_length() - 1
        fresh = rows[vertex] & ~seen
        seen |= fresh
        frontier |= fresh
    return seen.bit_count() == len(rows)


def matching_complement_cycle(rows: list[int]) -> tuple[bool, list[Edge] | None]:
    """Exact Hamiltonicity test for a cubic graph via perfect matchings."""
    n = len(rows)
    all_vertices = (1 << n) - 1
    mate = [-1] * n

    def complement_connected() -> bool:
        seen = 1
        frontier = 1
        while frontier:
            bit = frontier & -frontier
            frontier ^= bit
            u = bit.bit_length() - 1
            choices = rows[u] & ~(1 << mate[u]) & ~seen
            seen |= choices
            frontier |= choices
        return seen == all_vertices

    def visit(unmatched: int) -> bool:
        if not unmatched:
            return complement_connected()

        # Fail-first selection is exact and sharply reduces negative cases.
        scan = unmatched
        chosen_u = -1
        chosen_choices = 0
        chosen_count = n + 1
        while scan:
            bit = scan & -scan
            scan ^= bit
            u = bit.bit_length() - 1
            choices = rows[u] & unmatched
            count = choices.bit_count()
            if count < chosen_count:
                chosen_u, chosen_choices, chosen_count = u, choices, count
                if count <= 1:
                    break
        if chosen_count == 0:
            return False

        u_bit = 1 << chosen_u
        choices = chosen_choices & ~u_bit
        while choices:
            v_bit = choices & -choices
            choices ^= v_bit
            v = v_bit.bit_length() - 1
            mate[chosen_u] = v
            mate[v] = chosen_u
            if visit(unmatched & ~u_bit & ~v_bit):
                return True
            mate[chosen_u] = mate[v] = -1
        return False

    found = visit(all_vertices)
    if not found:
        return False, None
    matching = [(u, mate[u]) for u in range(n) if u < mate[u]]
    return True, matching


def cycle_of_length(
    rows: list[int], length: int, banned_edge: Edge | None = None
) -> list[int] | None:
    """Find a simple cycle of exact length, optionally avoiding one edge."""
    n = len(rows)
    if length > n:
        return None
    all_vertices = (1 << n) - 1
    banned_u, banned_v = banned_edge if banned_edge is not None else (-1, -1)

    def without_banned(u: int, choices: int) -> int:
        if u == banned_u:
            return choices & ~(1 << banned_v)
        if u == banned_v:
            return choices & ~(1 << banned_u)
        return choices

    for root in range(n):
        greater = all_vertices & ~((1 << (root + 1)) - 1)
        starts = without_banned(root, rows[root]) & greater
        while starts:
            first_bit = starts & -starts
            starts ^= first_bit
            first = first_bit.bit_length() - 1
            path = [root, first]

            def dfs(vertex: int, used: int) -> list[int] | None:
                if len(path) == length:
                    closing = without_banned(vertex, rows[vertex])
                    return path.copy() if closing & (1 << root) else None
                choices = without_banned(vertex, rows[vertex]) & greater & ~used
                while choices:
                    bit = choices & -choices
                    choices ^= bit
                    path.append(bit.bit_length() - 1)
                    result = dfs(path[-1], used | bit)
                    if result is not None:
                        return result
                    path.pop()
                return None

            result = dfs(first, (1 << root) | first_bit)
            if result is not None:
                return result
    return None


def cycle_edges(cycle: list[int]) -> list[Edge]:
    closed = cycle[1:] + cycle[:1]
    return [tuple(sorted((u, v))) for u, v in zip(cycle, closed)]


def first_cycle_at_lengths(
    rows: list[int], lengths: Iterable[int], banned_edge: Edge | None = None
) -> tuple[int | None, list[int] | None]:
    for length in lengths:
        witness = cycle_of_length(rows, length, banned_edge)
        if witness is not None:
            return length, witness
    return None, None


def cycle_through_edge(rows: list[int], edge: Edge, length: int) -> list[int] | None:
    """Find a length-cycle through edge via an alternate simple u-v path."""
    source, target = edge
    path = [source]

    def dfs(vertex: int, used: int, edges_left: int) -> list[int] | None:
        if edges_left == 0:
            return path.copy() if vertex == target else None
        if vertex == target:
            return None
        choices = rows[vertex] & ~used
        if vertex == source:
            choices &= ~(1 << target)
        while choices:
            bit = choices & -choices
            choices ^= bit
            path.append(bit.bit_length() - 1)
            result = dfs(path[-1], used | bit, edges_left - 1)
            if result is not None:
                return result
            path.pop()
        return None

    return dfs(source, 1 << source, length - 1)


def dyadic_core(rows: list[int], edges: list[Edge]) -> tuple[list[Edge], dict[str, object]]:
    dyadic = [length for length in (4, 8, 16, 32) if length <= len(rows)]
    first_length, first = first_cycle_at_lengths(rows, dyadic)
    if first is None:
        return edges.copy(), {
            "first_dyadic_length": None,
            "first_dyadic_cycle": None,
            "no_dyadic_cycle": True,
        }

    core: list[Edge] = []
    avoiding_witnesses = 0
    for edge in cycle_edges(first):
        _, witness = first_cycle_at_lengths(rows, dyadic, banned_edge=edge)
        if witness is None:
            core.append(edge)
        else:
            avoiding_witnesses += 1
    return sorted(core), {
        "first_dyadic_length": first_length,
        "first_dyadic_cycle": first,
        "no_dyadic_cycle": False,
        "initial_cycle_edges_eliminated_by_avoiding_witness": avoiding_witnesses,
    }


def write_raw_edges(path: Path, n: int, edges: list[Edge]) -> None:
    lines = [f"p edge {n} {len(edges)}"]
    lines.extend(f"e {u} {v}" for u, v in sorted(edges))
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def dump_candidate(
    output_dir: Path,
    order: int,
    index: int,
    edges: list[Edge],
    marked: Edge | None,
    reason: str,
    graph6_record: str,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"candidate_n{order}_i{index}"
    cubic_path = output_dir / f"{stem}_cubic.edges"
    write_raw_edges(cubic_path, order, edges)
    payload: dict[str, object] = {
        "reason": reason,
        "cubic_order": order,
        "census_index_one_based": index,
        "graph6": graph6_record,
        "marked_edge": list(marked) if marked is not None else None,
        "cubic_raw_edge_file": cubic_path.name,
    }
    if marked is not None:
        terminal = order
        block_edges = [edge for edge in edges if edge != marked]
        block_edges.extend([(marked[0], terminal), (marked[1], terminal)])
        block_edges = sorted(block_edges)
        block_path = output_dir / f"{stem}_block.edges"
        write_raw_edges(block_path, order + 1, block_edges)

        block_n = order + 1
        composed_edges = block_edges.copy()
        composed_edges.extend((u + block_n, v + block_n) for u, v in block_edges)
        composed_edges.append((terminal, terminal + block_n))
        composed_path = output_dir / f"{stem}_composed.edges"
        write_raw_edges(composed_path, 2 * block_n, sorted(composed_edges))
        payload.update(
            {
                "block_raw_edge_file": block_path.name,
                "composed_raw_edge_file": composed_path.name,
                "block_order": block_n,
                "composed_order": 2 * block_n,
            }
        )
    json_path = output_dir / f"{stem}.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def scan_file(path: Path, candidate_dir: Path, progress_every: int) -> dict[str, object]:
    started = time.monotonic()
    stats: Counter[str] = Counter()
    first_core_example: dict[str, object] | None = None
    candidate: dict[str, object] | None = None
    observed_order: int | None = None

    with path.open("rb") as handle:
        for index, raw in enumerate(handle, start=1):
            if not raw.strip() or raw.startswith(b">>"):
                continue
            rows, edges = parse_graph6(raw)
            n = len(rows)
            if observed_order is None:
                observed_order = n
            elif observed_order != n:
                raise ValueError(f"mixed orders in {path}: {observed_order} and {n}")
            if len(edges) != 3 * n // 2:
                raise ValueError(f"record {index}: edge count is not 3n/2")
            if any(row.bit_count() != 3 for row in rows):
                raise ValueError(f"record {index}: graph is not cubic")
            if not is_connected(rows):
                raise ValueError(f"record {index}: graph is disconnected")
            stats["validated_connected_simple_cubic"] += 1

            hamiltonian, matching = matching_complement_cycle(rows)
            stats["hamiltonian" if hamiltonian else "nonhamiltonian"] += 1

            core, detail = dyadic_core(rows, edges)
            if detail["no_dyadic_cycle"]:
                stats["no_dyadic_cycle"] += 1
                candidate = dump_candidate(
                    candidate_dir,
                    n,
                    index,
                    edges,
                    None,
                    "cubic graph has no dyadic cycle",
                    raw.strip().decode("ascii"),
                )
                break
            if not core:
                stats["empty_dyadic_core"] += 1
            else:
                stats["nonempty_dyadic_core"] += 1
                stats["core_edges_before_mersenne"] += len(core)
                if first_core_example is None:
                    first_core_example = {
                        "index_one_based": index,
                        "graph6": raw.strip().decode("ascii"),
                        "hamiltonian": hamiltonian,
                        "hamiltonian_complement_matching": matching,
                        "core": [list(edge) for edge in core],
                        "detail": detail,
                    }

                mersenne = [length for length in (3, 7, 15, 31) if length <= n]
                survivors: list[Edge] = []
                for edge in core:
                    if not any(cycle_through_edge(rows, edge, length) for length in mersenne):
                        survivors.append(edge)
                stats["core_edges_after_mersenne"] += len(survivors)
                if survivors:
                    candidate = dump_candidate(
                        candidate_dir,
                        n,
                        index,
                        edges,
                        survivors[0],
                        "marked edge survives dyadic-core and Mersenne filters",
                        raw.strip().decode("ascii"),
                    )
                    break

            if progress_every and stats["validated_connected_simple_cubic"] % progress_every == 0:
                elapsed = time.monotonic() - started
                print(
                    json.dumps(
                        {
                            "file": str(path),
                            "processed": stats["validated_connected_simple_cubic"],
                            "nonhamiltonian": stats["nonhamiltonian"],
                            "seconds": round(elapsed, 3),
                        },
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                    flush=True,
                )

    count = stats["validated_connected_simple_cubic"]
    expected = KNOWN_CONNECTED_CUBIC_COUNTS.get(observed_order or -1)
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "order": observed_order,
        "expected_connected_cubic_count": expected,
        "count_matches_expected": candidate is None and expected == count,
        "stats": dict(stats),
        "first_nonempty_core_example": first_core_example,
        "candidate": candidate,
        "complete": candidate is None and expected == count,
        "seconds": round(time.monotonic() - started, 6),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--progress-every", type=int, default=10000)
    args = parser.parse_args()

    started = time.monotonic()
    results: list[dict[str, object]] = []
    candidate_found = False
    for path in args.inputs:
        result = scan_file(path, args.candidate_dir, args.progress_every)
        results.append(result)
        candidate_found = result["candidate"] is not None
        partial = {
            "schema": "erdos64-canonical-cubic-scan-v1",
            "algorithm": {
                "hamiltonicity": "perfect matchings with connected complementary 2-factor",
                "dyadic_core": "one seed dyadic cycle plus per-edge avoiding-cycle existence search",
                "mersenne_filter": "alternate simple path through each marked edge",
            },
            "inputs": results,
            "candidate_found": candidate_found,
            "complete": False,
            "seconds": round(time.monotonic() - started, 6),
        }
        args.summary_out.write_text(json.dumps(partial, indent=2) + "\n", encoding="utf-8")
        if candidate_found or not result["complete"]:
            break

    complete = len(results) == len(args.inputs) and all(result["complete"] for result in results)
    summary = {
        "schema": "erdos64-canonical-cubic-scan-v1",
        "algorithm": {
            "hamiltonicity": "perfect matchings with connected complementary 2-factor",
            "dyadic_core": "one seed dyadic cycle plus per-edge avoiding-cycle existence search",
            "mersenne_filter": "alternate simple path through each marked edge",
        },
        "known_count_table": KNOWN_CONNECTED_CUBIC_COUNTS,
        "inputs": results,
        "candidate_found": candidate_found,
        "complete": complete and not candidate_found,
        "seconds": round(time.monotonic() - started, 6),
    }
    args.summary_out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 10 if candidate_found else 0 if summary["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
