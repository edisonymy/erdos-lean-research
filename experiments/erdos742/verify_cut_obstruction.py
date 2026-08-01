"""Verify the retained obstruction to a tempting maximum-cut lemma."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from verify_graph import verify_diameter2_critical


def matching_exists(
    n: int, edges: set[tuple[int, int]], cut_mask: int
) -> tuple[bool, dict[tuple[int, int], set[tuple[int, int]]]]:
    neighbours = [set() for _ in range(n)]
    for u, v in edges:
        neighbours[u].add(v)
        neighbours[v].add(u)
    internal = [
        edge for edge in edges if ((cut_mask >> edge[0]) ^ (cut_mask >> edge[1])) & 1 == 0
    ]
    cross_nonedges = {
        (u, v)
        for u, v in itertools.combinations(range(n), 2)
        if ((cut_mask >> u) ^ (cut_mask >> v)) & 1 and (u, v) not in edges
    }
    options: dict[tuple[int, int], set[tuple[int, int]]] = {}
    for edge in internal:
        choices = set()
        for a, b in cross_nonedges:
            common = neighbours[a] & neighbours[b]
            if len(common) != 1:
                continue
            w = next(iter(common))
            incident = {tuple(sorted((a, w))), tuple(sorted((b, w)))}
            if edge in incident:
                choices.add((a, b))
        options[edge] = choices

    owner: dict[tuple[int, int], tuple[int, int]] = {}

    def augment(edge: tuple[int, int], seen: set[tuple[int, int]]) -> bool:
        for nonedge in options[edge]:
            if nonedge in seen:
                continue
            seen.add(nonedge)
            if nonedge not in owner or augment(owner[nonedge], seen):
                owner[nonedge] = edge
                return True
        return False

    return all(augment(edge, set()) for edge in sorted(internal)), options


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    data = json.loads(args.certificate.read_text(encoding="utf-8"))
    n = int(data["n"])
    edges = {tuple(sorted(map(int, edge))) for edge in data["edges"]}
    graph_check = verify_diameter2_critical(n, edges)
    if not graph_check["valid"]:
        raise SystemExit("the retained graph is not diameter-2-critical")

    best = -1
    best_masks = []
    for tail in range(1 << (n - 1)):
        mask = 1 | (tail << 1)
        crossing = sum(((mask >> u) ^ (mask >> v)) & 1 for u, v in edges)
        if crossing > best:
            best, best_masks = crossing, [mask]
        elif crossing == best:
            best_masks.append(mask)
    claimed_side = set(map(int, data["maximum_cut_side_containing_zero"]))
    claimed_mask = sum(1 << vertex for vertex in claimed_side)
    if best != int(data["maximum_cut_size"]) or best_masks != [claimed_mask]:
        raise SystemExit("maximum-cut claim failed")
    has_matching, options = matching_exists(n, edges, claimed_mask)
    bad_edge = tuple(sorted(map(int, data["unmatchable_internal_edge"])))
    if has_matching or options.get(bad_edge) != set():
        raise SystemExit("matching obstruction claim failed")
    print(
        json.dumps(
            {
                "graph_valid": True,
                "maximum_cut_size": best,
                "maximum_cuts_up_to_complement": len(best_masks),
                "matching_exists": has_matching,
                "unmatchable_internal_edge": list(bad_edge),
                "options_for_edge": [],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
