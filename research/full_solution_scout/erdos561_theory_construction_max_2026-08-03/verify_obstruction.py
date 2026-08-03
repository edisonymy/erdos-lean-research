#!/usr/bin/env python3
"""Independent audit of the eight-edge obstruction and saved near host.

This file does not import either discovery program.  It checks the finite
degree-pattern part of the matching lemma, exhaustively checks the standard
nine-edge upper host over all 512 colourings, and verifies the saved
eight-edge near-host colouring with a separately written star-packing test.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "obstruction_verification.json"
STOCHASTIC = HERE / "stochastic_construction_result.json"


def has_two_star_forest(
    vertices: tuple[int, ...], edges: tuple[tuple[int, int], ...], demands: tuple[int, int]
) -> bool:
    """Independent direct leaf-set test for K_1,p disjoint union K_1,q."""
    adj = {v: set() for v in vertices}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    p, q = demands
    for x in vertices:
        for y in vertices:
            if x == y:
                continue
            x_leaves = adj[x] - {y}
            y_leaves = adj[y] - {x}
            for lx in itertools.combinations(sorted(x_leaves), p):
                blocked = {x, y, *lx}
                if len(y_leaves - blocked) >= q:
                    return True
    return False


def upper_host() -> tuple[tuple[int, ...], tuple[tuple[int, int], ...]]:
    edges = []
    nxt = 0
    for degree in (4, 3, 2):
        centre = nxt
        nxt += 1
        for _ in range(degree):
            edges.append((centre, nxt))
            nxt += 1
    return tuple(range(nxt)), tuple(edges)


def verify_upper_host() -> dict:
    vertices, edges = upper_host()
    failures = []
    red_hits = blue_hits = 0
    for red_mask in range(1 << len(edges)):
        red = tuple(e for i, e in enumerate(edges) if red_mask >> i & 1)
        blue = tuple(e for i, e in enumerate(edges) if not (red_mask >> i & 1))
        r = has_two_star_forest(vertices, red, (3, 2))
        b = has_two_star_forest(vertices, blue, (2, 1))
        red_hits += int(r)
        blue_hits += int(b)
        if not r and not b:
            failures.append(red_mask)
    return {
        "host": "K1,4 disjoint_union K1,3 disjoint_union K1,2",
        "edges": len(edges), "colourings_checked": 1 << len(edges),
        "red_target_hit_colourings": red_hits,
        "blue_target_hit_colourings": blue_hits,
        "avoiding_colourings": failures,
        "status": "VERIFIED" if not failures else "FAILED",
    }


def matchings(edges: tuple[tuple[int, int], ...]):
    for mask in range(1 << len(edges)):
        chosen = []
        used = set()
        ok = True
        for i, e in enumerate(edges):
            if mask >> i & 1:
                if used.intersection(e):
                    ok = False
                    break
                used.update(e)
                chosen.append(e)
        if ok:
            yield tuple(chosen), used


def verify_degree_patterns() -> dict:
    """Enumerate the only nontrivial induced graphs H=G[S], r=4,5."""
    rows = []
    for r in (4, 5):
        universe = tuple(itertools.combinations(range(r), 2))
        checked = eligible = failed = 0
        for mask in range(1 << len(universe)):
            h_edges = tuple(e for i, e in enumerate(universe) if mask >> i & 1)
            deg = [0] * r
            for u, v in h_edges:
                deg[u] += 1
                deg[v] += 1
            if max(deg, default=0) > 3:
                continue
            checked += 1
            # If all r vertices have total degree three in G, the number of
            # G-edges incident with S is 3r-e(H), and may not exceed eight.
            if 3 * r - len(h_edges) > 8:
                continue
            eligible += 1
            if r == 4:
                ok = any(len(used) == 4 for _, used in matchings(h_edges))
            else:
                external_deficit = [3 - d for d in deg]
                special = [v for v, d in enumerate(external_deficit) if d == 1]
                ok = False
                if len(special) == 1 and sum(external_deficit) == 1:
                    v = special[0]
                    remaining = set(range(r)) - {v}
                    ok = any(remaining <= used for _, used in matchings(h_edges))
            failed += int(not ok)
        rows.append({"degree_three_vertices": r, "patterns_checked": checked,
                     "edge_budget_eligible_patterns": eligible,
                     "failed_patterns": failed})
    return {"rows": rows,
            "status": "VERIFIED" if all(x["failed_patterns"] == 0 for x in rows) else "FAILED"}


def verify_saved_near_host() -> dict:
    data = json.loads(STOCHASTIC.read_text(encoding="utf-8"))
    row = data["results"][0]["by_order"][0]
    edges = tuple(tuple(e) for e in row["best_edges"])
    vertices = tuple(sorted({v for e in edges for v in e}))
    red_mask = row["avoiding_red_mask"]
    red = tuple(e for i, e in enumerate(edges) if red_mask >> i & 1)
    blue = tuple(e for i, e in enumerate(edges) if not (red_mask >> i & 1))
    red_hit = has_two_star_forest(vertices, red, (3, 2))
    blue_hit = has_two_star_forest(vertices, blue, (2, 1))
    return {
        "edges": [list(e) for e in edges], "red_mask": red_mask,
        "red_target_present": red_hit, "blue_target_present": blue_hit,
        "status": "VERIFIED_AVOIDING" if not red_hit and not blue_hit else "FAILED",
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = {
        "claim_scope": "independent finite audit; analytic proof remains authoritative",
        "degree_pattern_audit": verify_degree_patterns(),
        "upper_host_audit": verify_upper_host(),
        "saved_near_host_audit": verify_saved_near_host(),
    }
    statuses = [result["degree_pattern_audit"]["status"],
                result["upper_host_audit"]["status"],
                result["saved_near_host_audit"]["status"]]
    result["status"] = "VERIFIED" if statuses == ["VERIFIED", "VERIFIED", "VERIFIED_AVOIDING"] else "FAILED"
    result["inputs"] = {"stochastic_result_sha256": sha256(STOCHASTIC)}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
