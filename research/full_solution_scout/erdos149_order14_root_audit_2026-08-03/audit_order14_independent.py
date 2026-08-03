#!/usr/bin/env python3
"""Independent full-catalogue replay of the bounded Erdos #149 order-14 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path


N = 14


def decode(raw: bytes) -> tuple[list[tuple[int, int]], list[int]]:
    data = raw.rstrip(b"\r\n")
    if not data or data[0] != N + 63:
        raise ValueError("expected graph6 on 14 vertices")
    bits = [(byte - 63) >> shift & 1 for byte in data[1:] for shift in range(5, -1, -1)]
    edges: list[tuple[int, int]] = []
    adjacency = [0] * N
    cursor = 0
    for high in range(1, N):
        for low in range(high):
            if bits[cursor]:
                edges.append((low, high))
                adjacency[low] |= 1 << high
                adjacency[high] |= 1 << low
            cursor += 1
    return edges, adjacency


def compatibility(edges: list[tuple[int, int]], adjacency: list[int]) -> list[int]:
    endpoint_masks = [(1 << a) | (1 << b) for a, b in edges]
    result = [0] * len(edges)
    for i, (a, b) in enumerate(edges):
        forbidden = adjacency[a] | adjacency[b] | endpoint_masks[i]
        for j in range(i + 1, len(edges)):
            if not forbidden & endpoint_masks[j]:
                result[i] |= 1 << j
                result[j] |= 1 << i
    return result


def min_degree_greedy(comp: list[int], target: int) -> list[tuple[int, int]] | None:
    """Pair fail-first by current compatibility degree, unlike either source scan."""
    unused = (1 << len(comp)) - 1
    chosen: list[tuple[int, int]] = []
    while unused and len(chosen) < target:
        live = []
        cursor = unused
        while cursor:
            bit = cursor & -cursor
            vertex = bit.bit_length() - 1
            degree = (comp[vertex] & unused).bit_count()
            live.append((degree, -vertex, vertex))
            cursor ^= bit
        degree, _, vertex = min(live)
        neighbours = comp[vertex] & unused
        if degree == 0:
            unused &= ~(1 << vertex)
            continue
        candidates = []
        cursor = neighbours
        while cursor:
            bit = cursor & -cursor
            other = bit.bit_length() - 1
            candidates.append(((comp[other] & unused).bit_count(), -other, other))
            cursor ^= bit
        other = min(candidates)[2]
        chosen.append((vertex, other))
        unused &= ~((1 << vertex) | (1 << other))
    return chosen if len(chosen) == target else None


def bounded_search(comp: list[int], target: int) -> list[tuple[int, int]] | None:
    greedy = min_degree_greedy(comp, target)
    if greedy is not None:
        return greedy

    def recurse(unused: int, need: int) -> list[tuple[int, int]] | None:
        if need == 0:
            return []
        if unused.bit_count() < 2 * need:
            return None
        live = []
        cursor = unused
        while cursor:
            bit = cursor & -cursor
            vertex = bit.bit_length() - 1
            degree = (comp[vertex] & unused).bit_count()
            live.append((degree, -vertex, vertex))
            cursor ^= bit
        _, _, vertex = min(live)
        neighbours = comp[vertex] & unused
        cursor = neighbours
        while cursor:
            bit = cursor & -cursor
            other = bit.bit_length() - 1
            tail = recurse(unused & ~(1 << vertex) & ~bit, need - 1)
            if tail is not None:
                return [(vertex, other), *tail]
            cursor ^= bit
        return recurse(unused & ~(1 << vertex), need)

    return recurse((1 << len(comp)) - 1, target)


def audit_slice(path: Path, edge_count: int) -> dict:
    raw = path.read_bytes()
    records = raw.splitlines()
    expected = [3, 3] + [4] * 12 if edge_count == 27 else [4] * 14
    target = edge_count - 20
    failures: list[dict] = []
    greedy_successes = 0
    fallback_successes = 0
    seen: set[bytes] = set()
    for index, record in enumerate(records):
        seen.add(record)
        edges, adjacency = decode(record)
        comp = compatibility(edges, adjacency)
        witness = min_degree_greedy(comp, target)
        if witness is not None:
            greedy_successes += 1
        else:
            witness = bounded_search(comp, target)
            fallback_successes += int(witness is not None)
        valid = witness is not None and len({v for pair in witness for v in pair}) == 2 * target
        if valid:
            valid = all(comp[a] & (1 << b) for a, b in witness)
        if len(edges) != edge_count or sorted(x.bit_count() for x in adjacency) != expected or not valid:
            failures.append(
                {
                    "index": index,
                    "graph6": record.decode("ascii"),
                    "edges": len(edges),
                    "degrees": sorted(x.bit_count() for x in adjacency),
                    "witness": witness,
                }
            )
            if len(failures) >= 10:
                break
    return {
        "records": len(records),
        "unique_records": len(seen),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "min_degree_greedy_successes": greedy_successes,
        "fallback_successes": fallback_successes,
        "failures": failures,
    }


def regenerate(geng: Path, stored: Path, edge_count: int, temporary_root: Path) -> dict:
    minimum = "3" if edge_count == 27 else "4"
    with tempfile.TemporaryDirectory(prefix=f"order14-m{edge_count}-", dir=temporary_root) as raw_tmp:
        generated = Path(raw_tmp) / f"m{edge_count}.g6"
        subprocess.run(
            [str(geng), "-q", "-c", f"-d{minimum}", "-D4", "14", str(edge_count), str(generated)],
            check=True,
        )
        return {
            "bytes_identical": generated.read_bytes() == stored.read_bytes(),
            "sha256": hashlib.sha256(generated.read_bytes()).hexdigest(),
            "bytes": generated.stat().st_size,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--geng", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    package = args.package.resolve()
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    m27_path = package / "14_m27_min3.g6"
    m28_path = package / "14_m28_4regular.g6"
    m27 = audit_slice(m27_path, 27)
    m28 = audit_slice(m28_path, 28)
    regen27 = regenerate(args.geng.resolve(), m27_path, 27, output_path.parent)
    regen28 = regenerate(args.geng.resolve(), m28_path, 28, output_path.parent)
    structural = [
        {
            "edges": edges,
            "degree_three_vertices": 56 - 2 * edges,
            "packing_holds": 3 * (56 - 2 * edges) <= 14 - (56 - 2 * edges),
        }
        for edges in range(21, 29)
    ]
    assertions = {
        "m27_hash": m27["sha256"] == "2ce9cbfdaeaad95ae2b897aeb589996573175d8ceb89c1e3fabe5020878ae610",
        "m27_count_unique": m27["records"] == m27["unique_records"] == 2771069,
        "m27_all_witnesses": not m27["failures"],
        "m27_regenerated_identically": regen27["bytes_identical"],
        "m28_hash": m28["sha256"] == "0ba93c3c6d8bd00bd0b0fff7513a0873f22c3d68e5160bc04df41e346c5d822c",
        "m28_count_unique": m28["records"] == m28["unique_records"] == 88168,
        "m28_all_witnesses": not m28["failures"],
        "m28_regenerated_identically": regen28["bytes_identical"],
        "structural_survivors": [x["edges"] for x in structural if x["packing_holds"]] == [27, 28],
    }
    result = {
        "schema": "erdos149-order14-independent-root-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "claim": "Every simple graph G with |V(G)| <= 14 and Delta(G) <= 4 has strong chromatic index at most 20.",
        "claim_boundary": "Bounded theorem only; not a resolution of Erdos problem 149.",
        "catalogue_27_edges": m27,
        "catalogue_28_edges": m28,
        "regeneration_27_edges": regen27,
        "regeneration_28_edges": regen28,
        "geng": {
            "path": str(args.geng.resolve()),
            "sha256": hashlib.sha256(args.geng.resolve().read_bytes()).hexdigest(),
        },
        "structural_cases": structural,
        "assertions": assertions,
        "elapsed_seconds": time.perf_counter() - started,
    }
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "assertions": assertions, "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
