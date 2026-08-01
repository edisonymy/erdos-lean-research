#!/usr/bin/env python3
"""Exhaustive small-model audit of the two general #128 bridge lemmas."""

from __future__ import annotations

import itertools
import json


def pairs(vertices):
    return list(itertools.combinations(vertices, 2))


def adjacent(edges: set[tuple[int, int]], u: int, v: int) -> bool:
    return tuple(sorted((u, v))) in edges


def triangle_free(n: int, edges: set[tuple[int, int]]) -> bool:
    return not any(all(adjacent(edges, u, v) for u, v in pairs(T))
                   for T in itertools.combinations(range(n), 3))


def maximal_triangle_free(n: int, edges: set[tuple[int, int]]) -> bool:
    return triangle_free(n, edges) and all(
        adjacent(edges, u, v) or any(adjacent(edges, u, w) and adjacent(edges, v, w)
                                     for w in range(n) if w not in (u, v))
        for u, v in pairs(range(n)))


def independent(edges: set[tuple[int, int]], S: tuple[int, ...]) -> bool:
    return not any(adjacent(edges, u, v) for u, v in pairs(S))


def audit(limit: int = 6) -> dict[str, int]:
    graphs = triangle_free_graphs = pair_instances = 0
    maximal_graphs = classification_instances = 0
    for n in range(limit + 1):
        es = pairs(range(n))
        for mask in range(1 << len(es)):
            graphs += 1
            edges = {e for j, e in enumerate(es) if mask >> j & 1}
            if not triangle_free(n, edges):
                continue
            triangle_free_graphs += 1
            vertices = tuple(range(n))
            for a in range(n + 1):
                for I in itertools.combinations(vertices, a):
                    if not independent(edges, I):
                        continue
                    Iset = set(I)
                    O = tuple(v for v in vertices if v not in Iset)
                    for x in O:
                        others = tuple(y for y in O if y != x)
                        if not others:
                            continue
                        d = sum(adjacent(edges, i, x) for i in I)
                        q = min(sum(adjacent(edges, u, v)
                                    for u, v in pairs(I + (x, y))) for y in others)
                        if 2 * (q - d) - 1 > a:
                            assert independent(edges, others)
                        pair_instances += 1

            if not maximal_triangle_free(n, edges):
                continue
            maximal_graphs += 1
            for a in range(2, n + 1, 2):
                d = a // 2
                for I in itertools.combinations(vertices, a):
                    if not independent(edges, I):
                        continue
                    Iset = set(I)
                    O = tuple(v for v in vertices if v not in Iset)
                    types = {v: frozenset(i for i in I if adjacent(edges, i, v)) for v in O}
                    if any(len(types[v]) < d for v in O):
                        continue
                    for u, v in pairs(O):
                        expected = len(types[u]) == d and types[v] == Iset - types[u]
                        assert adjacent(edges, u, v) == expected
                    for v in O:
                        if len(types[v]) > d:
                            assert types[v] == Iset
                        else:
                            assert any(types[w] == Iset - types[v] for w in O)
                    classification_instances += 1
    return {"all_labelled_graphs": graphs,
            "triangle_free_graphs": triangle_free_graphs,
            "pair_lemma_instances": pair_instances,
            "maximal_triangle_free_graphs": maximal_graphs,
            "classification_instances": classification_instances}


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
