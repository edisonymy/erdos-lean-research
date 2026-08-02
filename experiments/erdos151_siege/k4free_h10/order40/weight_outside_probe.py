#!/usr/bin/env python3
"""Bounded exact probe for the order-40 K4-free outside/fibre projection.

This is deliberately only a projection of the real graph.  It enumerates
nondecreasing boundary-fibre sizes ``w_x=|B_x|`` and uses a SAT solver for
the graph induced by the ``r`` vertices outside an edge-minimal Ramsey
core.  The encoded necessary conditions are documented in
``research/erdos151/general/k4free_h10/order40/ORDER40_RESIDUAL.md``.

For each feasible row it maximizes the number of outside edges which lie in
no outside triangle.  Such edges are ambient-maximal because different
boundary fibres are disjoint.  Combining this with the largest possible
number of non-core maximal edges incident with the core gives an upper
bound on the total number of ambient-maximal edges.  The probe does *not*
encode the core, arrowing, beta, or marked-link conditions and therefore
cannot prove existence of a counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.examples.rc2 import RC2


def pairs(n: int):
    return itertools.combinations(range(n), 2)


def triples(n: int):
    return itertools.combinations(range(n), 3)


def quadruples(n: int):
    return itertools.combinations(range(n), 4)


def beta_lower_small_order(n: int) -> int:
    """The through-order-39 lower bound needed only for n<=9 here."""
    if n <= 0:
        return 0
    if n <= 2:
        return 1
    if n <= 5:
        return 2
    if n <= 8:
        return 3
    return 4


def solve_outside(weights: tuple[int, ...]) -> dict | None:
    """Return a maximum-L witness, or None when the projection is UNSAT."""
    r = len(weights)
    pool = IDPool()
    edge = {(i, j): pool.id(("e", i, j)) for i, j in pairs(r)}
    lonely = {(i, j): pool.id(("l", i, j)) for i, j in pairs(r)}
    wcnf = WCNF()

    def e(i: int, j: int) -> int:
        return edge[tuple(sorted((i, j)))]

    # K4-freeness of G[R].
    for quad in quadruples(r):
        wcnf.append([-e(i, j) for i, j in itertools.combinations(quad, 2)])

    # Ambient degree floor 4 and ceiling 9.  If w_x>0, the degree-nine
    # core endpoint forces d_G(x)>=8 by the two-walk deficiency bound.
    for i, weight in enumerate(weights):
        incident = [e(i, j) for j in range(r) if j != i]
        lower = (8 if weight else 4) - weight
        upper = 9 - weight
        lower = max(0, lower)
        upper = min(r - 1, upper)
        if lower > upper:
            return None
        if lower:
            card = CardEnc.atleast(
                incident, bound=lower, vpool=pool, encoding=EncType.seqcounter
            )
            wcnf.extend(card.clauses)
        if upper < len(incident):
            card = CardEnc.atmost(
                incident, bound=upper, vpool=pool, encoding=EncType.seqcounter
            )
            wcnf.extend(card.clauses)

    # l_ij iff ij is an edge with no common outside neighbor.  Only the
    # forward implication is needed when l variables have positive weight;
    # maximization makes every eligible l true.
    for i, j in pairs(r):
        lij = lonely[(i, j)]
        wcnf.append([-lij, e(i, j)])
        for k in range(r):
            if k in (i, j):
                continue
            wcnf.append([-lij, -e(i, k), -e(j, k)])
        wcnf.append([lij], weight=1)

    with RC2(wcnf, solver="g4", adapt=False, exhaust=True) as rc2:
        model = rc2.compute()
        if model is None:
            return None
        positives = set(lit for lit in model if lit > 0)
        edges = [[i, j] for i, j in pairs(r) if e(i, j) in positives]
        lonely_edges = [
            [i, j] for i, j in pairs(r) if lonely[(i, j)] in positives
        ]
        return {
            "edges": edges,
            "degrees": [
                sum(e(i, j) in positives for j in range(r) if j != i)
                for i in range(r)
            ],
            "lonely_edges": lonely_edges,
            "lonely_count": len(lonely_edges),
        }


def feasible_weight_rows(r: int):
    q = 40 - r
    for weights in itertools.combinations_with_replacement(range(10), r):
        # B_x union B_y is triangle-free in the core and anticomplete to
        # R-{x,y}.  Combining it with the known small-order admissible set
        # in that remainder sharpens the raw pair cap from 9.
        pair_cap = 9 - beta_lower_small_order(r - 2)
        if r >= 2 and weights[-1] + weights[-2] > pair_cap:
            continue
        c = sum(weights)
        s = sum(weight > 0 for weight in weights)
        for b in range(0, q - c + 1, 2):
            # Core/outside incidence lower bound.
            if r >= 2 and q * (r - 2) + 2 * b > 8 * c:
                continue
            # For one fibre B_x, the relevant incidence set is the union of
            # the eight-vertex open core neighborhoods of its members.  The
            # fibre is independent, so this union is contained in Q-B_x as
            # well as having size at most 8|B_x|.  Summing this sharper
            # per-fibre ceiling retains forced neighborhood overlaps.
            if r >= 2:
                fibre_union_upper = sum(min(8 * weight, q - weight) for weight in weights)
                if q * (r - 2) + 2 * b > fibre_union_upper:
                    continue
            if r == 1 and b > 0 and not weights[0]:
                continue
            # A core-degree-nine vertex sees every outside vertex; if b=0,
            # each core-degree-eight neighborhood still sees r-2 distinct
            # nonempty fibres.
            if b > 0 and s < r:
                continue
            if b == 0 and r >= 2 and s < r - 2:
                continue
            yield weights, b


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r-min", type=int, default=0)
    parser.add_argument("--r-max", type=int, default=10)
    parser.add_argument("--emit", type=Path)
    args = parser.parse_args()

    rows = []
    for r in range(args.r_min, args.r_max + 1):
        q = 40 - r
        best = None
        feasible_count = 0
        outside_cache: dict[tuple[int, ...], dict | None] = {}
        for weights, b in feasible_weight_rows(r):
            if weights not in outside_cache:
                outside_cache[weights] = solve_outside(weights)
            outside = outside_cache[weights]
            if outside is None:
                continue
            feasible_count += 1
            c = sum(weights)
            # If f non-core edges have both endpoints in Q, while c have
            # one endpoint in Q and one in R, then 2f+c<=q-b.
            core_lonely_upper = c + (q - b - c) // 2
            total_lonely_upper = core_lonely_upper + outside["lonely_count"]
            candidate = {
                "r": r,
                "q": q,
                "weights": list(weights),
                "b_core_degree9": b,
                "boundary_endpoints": c,
                "core_incident_lonely_upper": core_lonely_upper,
                "outside": outside,
                "total_lonely_upper": total_lonely_upper,
            }
            key = (
                total_lonely_upper,
                outside["lonely_count"],
                c,
                -b,
                weights,
            )
            if best is None or key > best[0]:
                best = (key, candidate)
        rows.append(
            {
                "r": r,
                "q": q,
                "feasible_weight_core_degree_rows": feasible_count,
                "maximum_lonely_edge_projection": None if best is None else best[1],
            }
        )

    script_path = Path(__file__).resolve()
    result = {
        "status": "CHECKED_PROJECTION_ONLY",
        "scope": (
            "Necessary outside/fibre conditions only; no core graph, "
            "arrowing, beta, or marked-link semantics are encoded."
        ),
        "rows": rows,
        "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.emit:
        args.emit.write_bytes((rendered + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
