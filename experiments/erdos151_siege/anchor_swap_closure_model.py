#!/usr/bin/env python3
"""Add the proved all-removal-set anchor-swap constraints to stage 3.

This is an adversarial lemma probe at h=8, n=28.  It starts with the exact
stage-3 encoding from ``anchor_model.py`` and lazily enforces the following
necessary condition for a genuine least counterexample.

For R0 contained in the designated maximum admissible set S, let B_R0 be
the outside vertices for which every ambient-maximal S-anchor meets R0.
Then alpha(G[B_R0]) <= |R0|.  Otherwise (S - R0) together with an
independent (|R0|+1)-set in B_R0 would be an admissible h-set.

SAT means that even this stronger, simultaneously imposed anchor-swap
shadow is an abstractly feasible local model; it is NOT a counterexample to
Erdos #151.  UNSAT would show this axiom package infeasible, but could be
used only after an independent proof-certificate or solver audit.

Usage:
    python anchor_swap_closure_model.py OUT.json
"""

from __future__ import annotations

import itertools
import json
import sys
import time

from pysat.solvers import Cadical195

import anchor_model


N, R = anchor_model.N, anchor_model.R
S = tuple(anchor_model.S)
X = tuple(anchor_model.X)


def independent_set_in(adj: dict[int, set[int]], vertices: set[int], size: int):
    """Return an independent set of exactly ``size`` in ``vertices``."""

    def search(candidates: set[int], chosen: list[int]):
        if len(chosen) == size:
            return chosen
        if len(chosen) + len(candidates) < size:
            return None
        if not candidates:
            return None
        vertex = min(candidates, key=lambda v: len(adj[v] & candidates))
        found = search(candidates - adj[vertex] - {vertex}, chosen + [vertex])
        if found is not None:
            return found
        return search(candidates - {vertex}, chosen)

    return search(set(vertices), [])


def actual_anchors(v: int, adj: dict[int, set[int]]):
    """Reconstruct every ambient-maximal anchor of v contained in S."""
    result = []
    neighbors_s = tuple(a for a in S if a in adj[v])
    for size in (1, 2, 3):
        for A in itertools.combinations(neighbors_s, size):
            if not all(b in adj[a] for a, b in itertools.combinations(A, 2)):
                continue
            clique = set(A) | {v}
            if any(
                w not in clique and all(w in adj[u] for u in clique)
                for w in range(N)
            ):
                continue
            result.append(A)
    return result


def anc(pool, v: int, A: tuple[int, ...]):
    return pool.id(f"anc{v}_{'_'.join(map(str, A))}")


def model_graph(model: list[int], edge):
    positive = {literal for literal in model if literal > 0}
    value = {
        (i, j): edge(i, j) in positive
        for i, j in itertools.combinations(range(N), 2)
    }
    adj = {v: set() for v in range(N)}
    for (i, j), present in value.items():
        if present:
            adj[i].add(j)
            adj[j].add(i)
    return value, adj


def first_shadow_violation(adj: dict[int, set[int]]):
    anchors = {v: actual_anchors(v, adj) for v in X}
    assert all(anchors.values())
    for size_r in range(1, R + 1):
        for R0 in itertools.combinations(S, size_r):
            removed = set(R0)
            bad = {
                v for v in X
                if all(removed.intersection(A) for A in anchors[v])
            }
            witness = independent_set_in(adj, bad, size_r + 1)
            if witness is not None:
                return R0, witness, anchors
    return None


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: anchor_swap_closure_model.py OUT.json")
    outpath = sys.argv[1]
    cnf, pool, edge = anchor_model.build(3)
    started = time.time()
    lazy = {"alpha": 0, "omega": 0, "anchor_swap_shadow": 0}

    with Cadical195(bootstrap_with=cnf) as solver:
        while True:
            if not solver.solve():
                result = {
                    "stage": 4,
                    "result": "UNSAT",
                    "axioms": [
                        "anchor_model stage 3",
                        "alpha(B_R0) <= |R0| for every R0 subset S",
                    ],
                    "lazy_blocks": lazy,
                    "elapsed_s": round(time.time() - started, 1),
                }
                break

            model = solver.get_model()
            value, adj = model_graph(model, edge)

            k5 = next(
                (
                    q for q in itertools.combinations(range(N), 5)
                    if all(j in adj[i] for i, j in itertools.combinations(q, 2))
                ),
                None,
            )
            if k5 is not None:
                solver.add_clause(
                    [-edge(i, j) for i, j in itertools.combinations(k5, 2)]
                )
                lazy["omega"] += 1
                continue

            independent8 = anchor_model.independent_set_ge(adj, R + 1)
            if independent8:
                solver.add_clause(
                    [edge(i, j) for i, j in itertools.combinations(sorted(independent8), 2)]
                )
                lazy["alpha"] += 1
                continue

            violation = first_shadow_violation(adj)
            if violation is not None:
                R0, independent, _ = violation
                removed = set(R0)
                clause = [
                    edge(i, j)
                    for i, j in itertools.combinations(sorted(independent), 2)
                ]
                for v in independent:
                    for size_a in (1, 2, 3):
                        for A in itertools.combinations(S, size_a):
                            if removed.isdisjoint(A):
                                clause.append(anc(pool, v, A))
                assert clause
                solver.add_clause(clause)
                lazy["anchor_swap_shadow"] += 1
                continue

            anchors = {v: actual_anchors(v, adj) for v in X}
            edges = sorted([list(pair) for pair, present in value.items() if present])
            c_values = [len(adj[v].intersection(S)) for v in X]
            result = {
                "stage": 4,
                "result": "SAT",
                "scope": (
                    "abstract designated-S model; not an Erdos #151 counterexample"
                ),
                "axioms": [
                    "anchor_model stage 3",
                    "alpha(B_R0) <= |R0| for every R0 subset S",
                ],
                "lazy_blocks": lazy,
                "elapsed_s": round(time.time() - started, 1),
                "edge_count": len(edges),
                "c_distribution": {
                    str(c): c_values.count(c) for c in sorted(set(c_values))
                },
                "degrees_S": [len(adj[a]) for a in S],
                "degrees_X_minmax": [
                    min(len(adj[v]) for v in X),
                    max(len(adj[v]) for v in X),
                ],
                "anchor_count_minmax": [
                    min(map(len, anchors.values())),
                    max(map(len, anchors.values())),
                ],
                "edges": edges,
            }
            break

    with open(outpath, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=1)
        stream.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "edges"}))


if __name__ == "__main__":
    main()
