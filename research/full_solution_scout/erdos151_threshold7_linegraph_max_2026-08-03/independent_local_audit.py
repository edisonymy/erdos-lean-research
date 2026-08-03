#!/usr/bin/env python3
"""Independent finite audit for the threshold-seven link argument.

This program intentionally does not import campaign code or NetworkX.  It
enumerates every labelled simple graph with minimum degree at least two and
at most seven edges (the hypotheses force n <= 7), checks universal adaptable
2-colourability both from the definition and by the Hell--Zhu edge-deletion
criterion, and identifies every obstruction by brute-force isomorphism.

It also checks the local facts used to eliminate the Djs link and to build
the Krausz K4 cover.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent


def norm_edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def adjacencies(n: int, edges: tuple[tuple[int, int], ...]) -> list[set[int]]:
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def connected(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    adj = adjacencies(n, edges)
    seen = {0}
    todo = [0]
    while todo:
        v = todo.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                todo.append(w)
    return len(seen) == n


def bipartite(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    adj = adjacencies(n, edges)
    colors = [-1] * n
    for root in range(n):
        if colors[root] != -1:
            continue
        colors[root] = 0
        todo = deque([root])
        while todo:
            v = todo.popleft()
            for w in adj[v]:
                if colors[w] == -1:
                    colors[w] = 1 - colors[v]
                    todo.append(w)
                elif colors[w] == colors[v]:
                    return False
    return True


def deletion_criterion(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    """Return True iff deleting some edge leaves a bipartite graph."""
    return any(bipartite(n, edges[:i] + edges[i + 1 :]) for i in range(len(edges)))


def signing_has_adapted_coloring(
    n: int, edges: tuple[tuple[int, int], ...], signing: int
) -> bool:
    for vertex_colors in range(1 << n):
        okay = True
        for i, (a, b) in enumerate(edges):
            edge_color = (signing >> i) & 1
            if ((vertex_colors >> a) & 1) == edge_color and ((vertex_colors >> b) & 1) == edge_color:
                okay = False
                break
        if okay:
            return True
    return False


def universally_adaptable(n: int, edges: tuple[tuple[int, int], ...]) -> bool:
    return all(
        signing_has_adapted_coloring(n, edges, signing)
        for signing in range(1 << len(edges))
    )


def isomorphic(
    n: int,
    edges: tuple[tuple[int, int], ...],
    rn: int,
    redges: tuple[tuple[int, int], ...],
) -> bool:
    if n != rn or len(edges) != len(redges):
        return False
    target = set(redges)
    for perm in itertools.permutations(range(n)):
        image = {norm_edge(perm[a], perm[b]) for a, b in edges}
        if image == target:
            return True
    return False


REPRESENTATIVES: dict[str, tuple[int, tuple[tuple[int, int], ...]]] = {
    "K4": (4, tuple(itertools.combinations(range(4), 2))),
    "bowtie": (5, ((0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4))),
    "Djs": (5, ((0, 1), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (3, 4))),
    "joined_triangles": (
        6,
        ((0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)),
    ),
}


def identify(n: int, edges: tuple[tuple[int, int], ...]) -> str | None:
    hits = [
        name
        for name, (rn, redges) in REPRESENTATIVES.items()
        if isomorphic(n, edges, rn, redges)
    ]
    if len(hits) > 1:
        raise AssertionError(f"representatives overlap: {hits}")
    return hits[0] if hits else None


def triangles(n: int, edges: tuple[tuple[int, int], ...]) -> list[tuple[int, int, int]]:
    eset = set(edges)
    return [
        (a, b, c)
        for a, b, c in itertools.combinations(range(n), 3)
        if norm_edge(a, b) in eset and norm_edge(a, c) in eset and norm_edge(b, c) in eset
    ]


def induced_signature(vertices: set[int], edges: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    deg = Counter()
    for a, b in edges:
        if a in vertices and b in vertices:
            deg[a] += 1
            deg[b] += 1
    return tuple(sorted((deg[v] for v in vertices), reverse=True))


def adjacent_true_twins(n: int, edges: tuple[tuple[int, int], ...]) -> list[tuple[int, int]]:
    adj = adjacencies(n, edges)
    closed = [{v} | adj[v] for v in range(n)]
    return [(a, b) for a, b in edges if closed[a] == closed[b]]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    labelled_candidates = 0
    labelled_obstructions = 0
    candidates_by_nm: Counter[tuple[int, int]] = Counter()
    obstructions_by_type: Counter[str] = Counter()
    obstruction_type_sets_by_nm: dict[tuple[int, int], set[str]] = defaultdict(set)
    theorem_disagreements: list[dict[str, object]] = []
    unknown_obstructions: list[dict[str, object]] = []

    for n in range(3, 8):
        possible = tuple(itertools.combinations(range(n), 2))
        for m in range(n, min(7, len(possible)) + 1):
            for choice in itertools.combinations(possible, m):
                adj = adjacencies(n, choice)
                if min(map(len, adj)) < 2 or not connected(n, choice):
                    continue
                labelled_candidates += 1
                candidates_by_nm[(n, m)] += 1
                direct = universally_adaptable(n, choice)
                deletion = deletion_criterion(n, choice)
                if direct != deletion:
                    theorem_disagreements.append(
                        {"n": n, "edges": choice, "direct": direct, "deletion": deletion}
                    )
                if not direct:
                    labelled_obstructions += 1
                    kind = identify(n, choice)
                    if kind is None:
                        unknown_obstructions.append({"n": n, "edges": choice})
                    else:
                        obstructions_by_type[kind] += 1
                        obstruction_type_sets_by_nm[(n, m)].add(kind)

    local: dict[str, object] = {}
    for name, (n, edges) in REPRESENTATIVES.items():
        adj = adjacencies(n, edges)
        tris = triangles(n, edges)
        local[name] = {
            "n": n,
            "m": len(edges),
            "degree_sequence": sorted((len(x) for x in adj), reverse=True),
            "triangles": tris,
            "triangles_cover_all_vertices": set().union(*map(set, tris)) == set(range(n)),
            "adjacent_true_twins": adjacent_true_twins(n, edges),
            "degree3_neighbor_induced_signatures": [
                induced_signature(adj[v], edges) for v in range(n) if len(adj[v]) == 3
            ],
            "universally_adaptable": universally_adaptable(n, edges),
            "edge_deletion_bipartite": deletion_criterion(n, edges),
        }

    # Facts used in the analytic argument.
    assert not theorem_disagreements
    assert not unknown_obstructions
    assert set(obstructions_by_type) == set(REPRESENTATIVES)
    assert local["Djs"]["degree3_neighbor_induced_signatures"] == [(2, 1, 1), (2, 1, 1)]
    assert local["Djs"]["adjacent_true_twins"] == []
    assert local["K4"]["degree3_neighbor_induced_signatures"] == [(2, 2, 2)] * 4
    assert local["bowtie"]["degree3_neighbor_induced_signatures"] == []
    assert local["joined_triangles"]["degree3_neighbor_induced_signatures"] == [
        (1, 1, 0),
        (1, 1, 0),
    ]
    for name in ("bowtie", "joined_triangles"):
        assert len(local[name]["triangles"]) == 2
        assert local[name]["triangles_cover_all_vertices"]

    result = {
        "status": "VERIFIED",
        "scope": "all connected labelled simple graphs with delta>=2 and m<=7",
        "labelled_candidates": labelled_candidates,
        "labelled_obstructions": labelled_obstructions,
        "candidates_by_n_m": {
            f"{n},{m}": candidates_by_nm[(n, m)] for n, m in sorted(candidates_by_nm)
        },
        "obstruction_labelled_counts": dict(sorted(obstructions_by_type.items())),
        "obstruction_isomorphism_types_by_n_m": {
            f"{n},{m}": sorted(kinds)
            for (n, m), kinds in sorted(obstruction_type_sets_by_nm.items())
        },
        "hell_zhu_criterion_disagreements": theorem_disagreements,
        "unknown_obstructions": unknown_obstructions,
        "local_type_facts": local,
    }
    out = HERE / "independent_local_audit.result.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"result_sha256={sha256(out)}")


if __name__ == "__main__":
    main()
