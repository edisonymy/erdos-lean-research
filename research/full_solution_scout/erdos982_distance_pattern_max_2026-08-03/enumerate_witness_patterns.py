#!/usr/bin/env python3
"""Enumerate convex-order-compatible local distance partitions for an octagon.

At a vertex p, equal-distance neighbours form blocks.  We retain exactly
three nonempty blocks (a lossless refinement when the true number is <= 3).
Each pair in a block makes p a witness on the perpendicular bisector of that
base.  A line through the midpoint of a chord meets the boundary of a strict
convex polygon at most once on each side, so a base has at most one witness
on each of its two cyclic arcs.

The program solves the resulting eight-variable finite CSP, quotients full
solutions by the dihedral group, and records equality-component statistics.
It deliberately contains no floating geometry optimizer.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from dataclasses import dataclass
from pathlib import Path


N = 8
EDGES = list(itertools.combinations(range(N), 2))
EDGE_ID = {e: i for i, e in enumerate(EDGES)}


def partitions3(items: tuple[int, ...]):
    """Canonical restricted-growth strings with exactly three blocks."""
    labels = [0] * len(items)

    def rec(i: int, maximum: int):
        if i == len(items):
            if maximum == 2:
                blocks = [[] for _ in range(3)]
                for x, label in zip(items, labels):
                    blocks[label].append(x)
                yield tuple(tuple(b) for b in blocks)
            return
        for label in range(min(maximum + 1, 2) + 1):
            labels[i] = label
            yield from rec(i + 1, max(maximum, label))

    labels[0] = 0
    yield from rec(1, 0)


def side_key(p: int, a: int, b: int) -> tuple[int, int, int]:
    if a > b:
        a, b = b, a
    side = 0 if a < p < b else 1
    return a, b, side


@dataclass(frozen=True)
class Option:
    blocks: tuple[tuple[int, ...], ...]
    keys: frozenset[tuple[int, int, int]]
    witness_count: int
    profile: tuple[int, int, int]


def vertex_options(p: int) -> list[Option]:
    others = tuple(x for x in range(N) if x != p)
    out = []
    for blocks in partitions3(others):
        keys = frozenset(
            side_key(p, a, b)
            for block in blocks
            for a, b in itertools.combinations(block, 2)
        )
        profile = tuple(sorted((len(b) for b in blocks), reverse=True))
        out.append(Option(blocks, keys, len(keys), profile))
    assert len(out) == 301
    return out


OPTIONS = [vertex_options(p) for p in range(N)]


def transform_vertex(v: int, shift: int, reflect: bool) -> int:
    return ((-v if reflect else v) + shift) % N


def normalized_blocks(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def transform_pattern(chosen: tuple[Option, ...], shift: int, reflect: bool):
    by_new_vertex = [None] * N
    for old_p, option in enumerate(chosen):
        new_p = transform_vertex(old_p, shift, reflect)
        new_blocks = [
            tuple(transform_vertex(x, shift, reflect) for x in block)
            for block in option.blocks
        ]
        by_new_vertex[new_p] = normalized_blocks(new_blocks)
    return tuple(by_new_vertex)


def canonical_pattern(chosen: tuple[Option, ...]):
    return min(
        transform_pattern(chosen, shift, reflect)
        for shift in range(N)
        for reflect in (False, True)
    )


def equality_components(chosen: tuple[Option, ...]) -> tuple[tuple[int, ...], ...]:
    parent = list(range(len(EDGES)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[b] = a

    for p, option in enumerate(chosen):
        for block in option.blocks:
            edge_ids = [EDGE_ID[tuple(sorted((p, x)))] for x in block]
            for e in edge_ids[1:]:
                union(edge_ids[0], e)
    groups = {}
    for e in range(len(EDGES)):
        groups.setdefault(find(e), []).append(e)
    return tuple(sorted((tuple(v) for v in groups.values()), key=lambda x: (len(x), x)))


def run(max_raw: int, max_seconds: float, retain: int) -> dict:
    started = time.monotonic()
    # Pairwise compatibility bitsets: choosing option o at p restricts q.
    compat = [[None for _ in range(N)] for _ in range(N)]
    fullmask = (1 << 301) - 1
    for p in range(N):
        for q in range(N):
            if p == q:
                continue
            rows = []
            for op in OPTIONS[p]:
                mask = 0
                for j, oq in enumerate(OPTIONS[q]):
                    if op.keys.isdisjoint(oq.keys):
                        mask |= 1 << j
                rows.append(mask)
            compat[p][q] = rows

    raw = 0
    orbit_keys = set()
    retained = []
    component_hist = {}
    profile_hist = {}
    nodes = 0
    stopped = None

    def rec(chosen, domains):
        nonlocal raw, nodes, stopped
        if stopped:
            return
        nodes += 1
        if nodes & 4095 == 0 and time.monotonic() - started > max_seconds:
            stopped = "TIME_CAP"
            return
        if len(chosen) == N:
            ordered = tuple(chosen[p] for p in range(N))
            raw += 1
            key = canonical_pattern(ordered)
            if key not in orbit_keys:
                orbit_keys.add(key)
                comps = equality_components(ordered)
                k = len(comps)
                component_hist[str(k)] = component_hist.get(str(k), 0) + 1
                profiles = tuple(sorted((o.profile for o in ordered)))
                ps = ";".join("".join(map(str, x)) for x in profiles)
                profile_hist[ps] = profile_hist.get(ps, 0) + 1
                if len(retained) < retain:
                    retained.append({
                        "local_blocks": [[list(b) for b in o.blocks] for o in ordered],
                        "profiles": [list(o.profile) for o in ordered],
                        "witness_total": sum(o.witness_count for o in ordered),
                        "global_equality_components": [
                            [list(EDGES[e]) for e in comp] for comp in comps
                        ],
                    })
            if raw >= max_raw:
                stopped = "RAW_SOLUTION_CAP"
            return

        unchosen = [p for p in range(N) if p not in chosen]
        p = min(unchosen, key=lambda x: domains[x].bit_count())
        mask = domains[p]
        while mask and not stopped:
            bit = mask & -mask
            oi = bit.bit_length() - 1
            mask ^= bit
            new_domains = domains[:]
            new_domains[p] = bit
            feasible = True
            for q in unchosen:
                if q == p:
                    continue
                new_domains[q] &= compat[p][q][oi]
                if not new_domains[q]:
                    feasible = False
                    break
            if feasible:
                chosen[p] = OPTIONS[p][oi]
                rec(chosen, new_domains)
                del chosen[p]

    rec({}, [fullmask] * N)
    elapsed = time.monotonic() - started
    return {
        "status": stopped or "EXHAUSTIVE",
        "raw_solution_count": raw,
        "dihedral_orbit_count_seen": len(orbit_keys),
        "search_nodes": nodes,
        "elapsed_seconds": elapsed,
        "max_raw": max_raw,
        "max_seconds": max_seconds,
        "component_count_histogram_over_orbits": component_hist,
        "profile_histogram_over_orbits": profile_hist,
        "retained_orbit_representatives": retained,
        "mathematical_scope": "necessary local equal-distance partitions plus the one-witness-per-chord-side rule; not Euclidean realizability",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-raw", type=int, default=1_000_000)
    ap.add_argument("--max-seconds", type=float, default=300)
    ap.add_argument("--retain", type=int, default=100)
    ap.add_argument("--out", type=Path, default=Path(__file__).with_name("witness_pattern_search.json"))
    args = ap.parse_args()
    result = run(args.max_raw, args.max_seconds, args.retain)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in result if k not in ("retained_orbit_representatives", "profile_histogram_over_orbits")}, sort_keys=True))
    print("out_sha256=" + hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
