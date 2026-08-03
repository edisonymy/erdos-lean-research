#!/usr/bin/env python3
"""Independent root replay of the bounded Erdos #149 theorem through order 15."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import tempfile
import time
from collections import Counter
from pathlib import Path


N = 15
A, B = 0, 1
U, W = (2, 3, 4), (5, 6, 7)
X = tuple(range(8, 15))


def decode_graph6(raw: bytes) -> tuple[list[tuple[int, int]], list[int]]:
    data = raw.rstrip(b"\r\n")
    if not data or data[0] != N + 63:
        raise ValueError("expected graph6 on 15 vertices")
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


def fail_first_matching(comp: list[int], target: int) -> list[tuple[int, int]] | None:
    unused = (1 << len(comp)) - 1
    chosen: list[tuple[int, int]] = []
    while unused and len(chosen) < target:
        live = []
        cursor = unused
        while cursor:
            bit = cursor & -cursor
            vertex = bit.bit_length() - 1
            live.append(((comp[vertex] & unused).bit_count(), -vertex, vertex))
            cursor ^= bit
        degree, _, vertex = min(live)
        neighbours = comp[vertex] & unused
        if degree == 0:
            unused &= ~(1 << vertex)
            continue
        partner_options = []
        cursor = neighbours
        while cursor:
            bit = cursor & -cursor
            other = bit.bit_length() - 1
            partner_options.append(((comp[other] & unused).bit_count(), -other, other))
            cursor ^= bit
        other = min(partner_options)[2]
        chosen.append((vertex, other))
        unused &= ~((1 << vertex) | (1 << other))
    return chosen if len(chosen) == target else None


def exact_target_matching(comp: list[int], target: int) -> list[tuple[int, int]] | None:
    greedy = fail_first_matching(comp, target)
    if greedy is not None:
        return greedy

    def recurse(unused: int, need: int) -> list[tuple[int, int]] | None:
        if need == 0:
            return []
        if unused.bit_count() < 2 * need:
            return None
        vertices = []
        cursor = unused
        while cursor:
            bit = cursor & -cursor
            v = bit.bit_length() - 1
            vertices.append(((comp[v] & unused).bit_count(), -v, v))
            cursor ^= bit
        _, _, v = min(vertices)
        neighbours = comp[v] & unused
        cursor = neighbours
        while cursor:
            bit = cursor & -cursor
            w = bit.bit_length() - 1
            tail = recurse(unused & ~(1 << v) & ~bit, need - 1)
            if tail is not None:
                return [(v, w), *tail]
            cursor ^= bit
        return recurse(unused & ~(1 << v), need)

    return recurse((1 << len(comp)) - 1, target)


def residual_graphs(degrees: tuple[int, ...], forbidden: set[tuple[int, int]]):
    residual = list(degrees)
    chosen: list[tuple[int, int]] = []

    def search(vertex: int):
        while vertex < 7 and residual[vertex] == 0:
            vertex += 1
        if vertex == 7:
            if not any(residual):
                yield tuple(chosen)
            return
        options = [
            other
            for other in range(vertex + 1, 7)
            if residual[other] and (vertex, other) not in forbidden
        ]
        need = residual[vertex]
        for neighbours in itertools.combinations(options, need):
            residual[vertex] = 0
            for other in neighbours:
                residual[other] -= 1
                chosen.append((vertex, other))
            if min(residual) >= 0 and sum(residual) % 2 == 0:
                yield from search(vertex + 1)
            for _ in neighbours:
                chosen.pop()
            for other in neighbours:
                residual[other] += 1
            residual[vertex] = need

    yield from search(0)


def ordered_w_blocks(r: int, u_blocks: tuple[tuple[int, ...], ...]):
    sizes = (2, 2, 3) if r == 2 else (2, 2, 2)
    omitted_choices: tuple[int | None, ...] = (None,) if r == 2 else tuple(range(7))
    for omitted in omitted_choices:
        available = tuple(i for i in range(7) if i != omitted)
        for first in itertools.combinations(available, sizes[0]):
            if 0 < r and set(first) & set(u_blocks[0]):
                continue
            remainder1 = tuple(i for i in available if i not in first)
            for second in itertools.combinations(remainder1, sizes[1]):
                if 1 < r and set(second) & set(u_blocks[1]):
                    continue
                third = tuple(i for i in remainder1 if i not in second)
                if len(third) != sizes[2] or (2 < r and set(third) & set(u_blocks[2])):
                    continue
                yield (tuple(first), tuple(second), third)


def theta_graph(r: int, u_blocks, w_blocks, internal):
    edges = [(A, u) for u in U] + [(B, w) for w in W]
    edges += [(U[i], W[i]) for i in range(r)]
    for u, block in zip(U, u_blocks):
        edges += [(u, X[i]) for i in block]
    for w, block in zip(W, w_blocks):
        edges += [(w, X[i]) for i in block]
    edges += [(X[i], X[j]) for i, j in internal]
    edges = sorted(tuple(sorted(edge)) for edge in edges)
    adjacency = [0] * N
    for a, b in edges:
        adjacency[a] |= 1 << b
        adjacency[b] |= 1 << a
    return edges, adjacency


def audit_theta() -> dict:
    counts = Counter()
    failures = []
    greedy_successes = 0
    fallback_successes = 0
    for r in (2, 3):
        u_blocks = ((0, 1), (2, 3), (4, 5, 6)) if r == 2 else ((0, 1), (2, 3), (4, 5))
        for w_blocks in ordered_w_blocks(r, u_blocks):
            counts[f"r{r}_w_partitions"] += 1
            u_incidence = [int(any(i in block for block in u_blocks)) for i in range(7)]
            w_incidence = [int(any(i in block for block in w_blocks)) for i in range(7)]
            degrees = tuple(4 - u_incidence[i] - w_incidence[i] for i in range(7))
            forbidden: set[tuple[int, int]] = set()
            for block in (*u_blocks, *w_blocks):
                forbidden.update(tuple(sorted(pair)) for pair in itertools.combinations(block, 2))
            for internal in residual_graphs(degrees, forbidden):
                counts[f"r{r}_internal_completions"] += 1
                edges, adjacency = theta_graph(r, u_blocks, w_blocks, internal)
                witness = fail_first_matching(compatibility(edges, adjacency), 9)
                if witness is not None:
                    greedy_successes += 1
                else:
                    witness = exact_target_matching(compatibility(edges, adjacency), 9)
                    fallback_successes += int(witness is not None)
                if (
                    len(edges) != 29
                    or sorted(x.bit_count() for x in adjacency) != [3, 3] + [4] * 13
                    or witness is None
                ):
                    failures.append({"r": r, "u_blocks": u_blocks, "w_blocks": w_blocks, "internal": internal})
    return {
        "counts": dict(sorted(counts.items())),
        "fail_first_successes": greedy_successes,
        "fallback_successes": fallback_successes,
        "failures": failures,
    }


def audit_regular(path: Path) -> dict:
    raw = path.read_bytes()
    records = raw.splitlines()
    seen: set[bytes] = set()
    failures = []
    greedy_successes = 0
    fallback_successes = 0
    for index, record in enumerate(records):
        seen.add(record)
        edges, adjacency = decode_graph6(record)
        comp = compatibility(edges, adjacency)
        witness = fail_first_matching(comp, 10)
        if witness is not None:
            greedy_successes += 1
        else:
            witness = exact_target_matching(comp, 10)
            fallback_successes += int(witness is not None)
        if len(edges) != 30 or [x.bit_count() for x in adjacency] != [4] * 15 or witness is None:
            failures.append({"index": index, "graph6": record.decode("ascii")})
            if len(failures) >= 10:
                break
    return {
        "records": len(records),
        "unique_records": len(seen),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "fail_first_successes": greedy_successes,
        "fallback_successes": fallback_successes,
        "failures": failures,
    }


def regenerate_regular(geng: Path, stored: Path, temporary_root: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="order15-regular-", dir=temporary_root) as raw_tmp:
        generated = Path(raw_tmp) / "m30.g6"
        subprocess.run(
            [str(geng), "-q", "-c", "-d4", "-D4", "15", "30", str(generated)],
            check=True,
        )
        raw = generated.read_bytes()
        return {
            "bytes_identical": raw == stored.read_bytes(),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--geng", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    package = args.package.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    theta = audit_theta()
    regular_path = package / "15_m30_4regular.g6"
    regular = audit_regular(regular_path)
    regenerated = regenerate_regular(args.geng.resolve(), regular_path, output.parent)
    structural = [
        {
            "edges": edges,
            "degree_three_vertices": 60 - 2 * edges,
            "packing_holds": 3 * (60 - 2 * edges) <= 15 - (60 - 2 * edges),
        }
        for edges in range(23, 31)
    ]
    expected_theta = {
        "r2_internal_completions": 492,
        "r2_w_partitions": 55,
        "r3_internal_completions": 4764,
        "r3_w_partitions": 94,
    }
    assertions = {
        "theta_counts": theta["counts"] == expected_theta,
        "theta_all_witnesses": not theta["failures"],
        "regular_hash": regular["sha256"] == "801cbd1a228a91dc994fab3cc6e90f6e9cf36e21b6b2c581ad79250378622545",
        "regular_count_unique": regular["records"] == regular["unique_records"] == 805491,
        "regular_all_witnesses": not regular["failures"],
        "regular_regenerated_identically": regenerated["bytes_identical"],
        "structural_survivors": [x["edges"] for x in structural if x["packing_holds"]] == [29, 30],
    }
    result = {
        "schema": "erdos149-order15-independent-root-audit-v1",
        "status": "VERIFIED" if all(assertions.values()) else "AUDIT_FAILURE",
        "claim": "Every simple graph G with |V(G)| <= 15 and Delta(G) <= 4 has strong chromatic index at most 20.",
        "claim_boundary": "Bounded theorem only; not a resolution of Erdos problem 149.",
        "theta_core": theta,
        "regular_catalogue": regular,
        "regular_regeneration": regenerated,
        "geng": {
            "path": str(args.geng.resolve()),
            "sha256": hashlib.sha256(args.geng.resolve().read_bytes()).hexdigest(),
        },
        "structural_cases": structural,
        "assertions": assertions,
        "elapsed_seconds": time.perf_counter() - started,
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "assertions": assertions, "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))


if __name__ == "__main__":
    main()
