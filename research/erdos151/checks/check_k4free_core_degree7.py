#!/usr/bin/env python3
"""Exhaust the signed triangle-free link lemma on at most seven vertices.

An edge of a link graph is signed 0 (red) or 1 (blue).  A spoke assignment
is safe when no signed edge has both endpoint spokes equal to the edge sign.
The checker proves that every signed triangle-free graph on at most seven
vertices has a safe spoke assignment.

It is enough to enumerate maximal triangle-free graphs on exactly seven
labelled vertices.  Indeed, pad any smaller obstruction with isolated
vertices, extend its underlying graph to a maximal triangle-free graph, and
give every added edge either sign.  A safe assignment for the supergraph
would restrict to one for the alleged obstruction.

Only the Python standard library is used.  The complete run takes roughly
ten seconds on an ordinary desktop.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


N = 7
EXPECTED_MAXIMAL_TRIANGLE_FREE = 1_743
EXPECTED_SIGNINGS = 1_348_032


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    started_utc = utc_now()
    started = time.perf_counter()

    edges = list(itertools.combinations(range(N), 2))
    edge_index = {edge: index for index, edge in enumerate(edges)}
    triangle_masks = []
    for triple in itertools.combinations(range(N), 3):
        mask = 0
        for pair in itertools.combinations(triple, 2):
            mask |= 1 << edge_index[tuple(sorted(pair))]
        triangle_masks.append(mask)

    all_edges_mask = (1 << len(edges)) - 1
    maximal_graph_masks: list[int] = []

    for graph_mask in range(1 << len(edges)):
        if any((graph_mask & triangle) == triangle for triangle in triangle_masks):
            continue

        missing = all_edges_mask ^ graph_mask
        maximal = True
        while missing:
            edge_bit = missing & -missing
            missing ^= edge_bit
            if not any(
                (triangle & edge_bit)
                and (graph_mask & triangle) == (triangle ^ edge_bit)
                for triangle in triangle_masks
            ):
                maximal = False
                break
        if maximal:
            maximal_graph_masks.append(graph_mask)

    # violation_cover[e][c] is the 128-bit set of spoke assignments spoiled
    # by giving edge e sign c.
    violation_cover: list[tuple[int, int]] = []
    for u, v in edges:
        covers = [0, 0]
        for assignment in range(1 << N):
            u_color = (assignment >> u) & 1
            v_color = (assignment >> v) & 1
            if u_color == v_color:
                covers[u_color] |= 1 << assignment
        violation_cover.append((covers[0], covers[1]))

    all_assignments = (1 << (1 << N)) - 1
    signings_checked = 0
    obstruction = None

    for graph_mask in maximal_graph_masks:
        present = [
            edge_id for edge_id in range(len(edges)) if graph_mask & (1 << edge_id)
        ]
        for signing in range(1 << len(present)):
            signings_checked += 1
            spoiled = 0
            for local_id, edge_id in enumerate(present):
                sign = (signing >> local_id) & 1
                spoiled |= violation_cover[edge_id][sign]
            if spoiled == all_assignments:
                obstruction = {
                    "graph_mask": graph_mask,
                    "present_edge_ids": present,
                    "signing_mask": signing,
                }
                break
        if obstruction is not None:
            break

    elapsed = time.perf_counter() - started
    script_path = Path(__file__).resolve()
    script_sha256 = hashlib.sha256(script_path.read_bytes()).hexdigest()
    counts_match = (
        len(maximal_graph_masks) == EXPECTED_MAXIMAL_TRIANGLE_FREE
        and signings_checked == EXPECTED_SIGNINGS
    )
    verified = obstruction is None and counts_match

    result = {
        "check": "signed_triangle_free_link_degree_at_most_7",
        "claim": (
            "Every red/blue edge-signed triangle-free graph on at most seven "
            "vertices has a spoke assignment in which no edge has both "
            "endpoint spokes equal to its sign."
        ),
        "status": "VERIFIED" if verified else "FAILED",
        "method": (
            "Enumerate all labelled maximal triangle-free graphs on seven "
            "vertices, every edge signing, and cover-test all 128 spoke "
            "assignments using Python integer bitsets."
        ),
        "vertices": N,
        "all_labelled_graph_masks_considered": 1 << len(edges),
        "maximal_triangle_free_graphs": len(maximal_graph_masks),
        "expected_maximal_triangle_free_graphs": EXPECTED_MAXIMAL_TRIANGLE_FREE,
        "edge_signings_checked": signings_checked,
        "expected_edge_signings": EXPECTED_SIGNINGS,
        "spoke_assignments_per_signing": 1 << N,
        "obstruction": obstruction,
        "started_utc": started_utc,
        "finished_utc": utc_now(),
        "elapsed_seconds": round(elapsed, 6),
        "python_version": sys.version,
        "platform": platform.platform(),
        "script": str(script_path),
        "script_sha256": script_sha256,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
