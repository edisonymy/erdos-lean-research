#!/usr/bin/env python3
"""Exhaustive row-space DP for one-split-per-vertex relaxations of H8.

At each H8 vertex the seven incident old edges have class sizes (4,2,1).
A minimal locally-four-distance relaxation splits exactly one of the two
non-singleton classes into two classes.  There are eight such partitions:
split the pair; isolate one of four edges from the 4-class; or split the
4-class into one of three 2+2 partitions.

This script considers all 8^8 choices without enumerating them naively.  It
keeps the distinct Jacobian row spaces over a verification prime, then checks
minimum-rank witnesses exactly over Q(sqrt(3)).
"""

from __future__ import annotations

from collections import defaultdict
import json

from check_harborth_field import NAMES, POINTS, Q3, ZERO, dist2, edge_gradient, matrix_rank


P = 1_000_151
SQRT3_MOD_P = 766_206
assert SQRT3_MOD_P * SQRT3_MOD_P % P == 3


def q3_mod(x):
    def fraction_mod(q):
        return (q.numerator % P) * pow(q.denominator % P, P - 2, P) % P

    return (fraction_mod(x.a) + fraction_mod(x.b) * SQRT3_MOD_P) % P


def canonical_span(rows):
    """Canonical RREF tuple over GF(P)."""
    basis = {}
    for source in rows:
        row = [v % P for v in source]
        for pivot in sorted(basis):
            if row[pivot]:
                factor = row[pivot]
                row = [(a - factor * b) % P for a, b in zip(row, basis[pivot])]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        inv = pow(row[pivot], P - 2, P)
        row = [value * inv % P for value in row]
        for old_pivot, old_row in list(basis.items()):
            if old_row[pivot]:
                factor = old_row[pivot]
                basis[old_pivot] = [(a - factor * b) % P for a, b in zip(old_row, row)]
        basis[pivot] = row
    return tuple(tuple(basis[pivot]) for pivot in sorted(basis))


def merge_span(span, rows):
    return canonical_span(list(span) + rows)


def subgroup_rows(edges):
    if len(edges) <= 1:
        return []
    base = edge_gradient(*edges[0])
    rows = []
    for edge in edges[1:]:
        grad = edge_gradient(*edge)
        rows.append([q3_mod(x - y) for x, y in zip(grad, base)])
    return rows


def exact_rows(partitions):
    rows = []
    for vertex, option_index in enumerate(partitions):
        for subgroup in OPTIONS[vertex][option_index][1]:
            if len(subgroup) <= 1:
                continue
            base = edge_gradient(*subgroup[0])
            for edge in subgroup[1:]:
                grad = edge_gradient(*edge)
                rows.append([x - y for x, y in zip(grad, base)])
    return rows


def vertex_options(vertex):
    groups = defaultdict(list)
    for other in range(8):
        if vertex == other:
            continue
        edge = tuple(sorted((vertex, other)))
        groups[dist2(POINTS[vertex], POINTS[other])].append(edge)
    big = next(edges for edges in groups.values() if len(edges) == 4)
    pair = next(edges for edges in groups.values() if len(edges) == 2)
    big, pair = sorted(big), sorted(pair)
    options = []
    options.append(("split_pair", [big, [pair[0]], [pair[1]]]))
    for edge in big:
        rest = [e for e in big if e != edge]
        options.append(("big_1+3:" + "-".join(map(str, edge)), [[edge], rest, pair]))
    a = big[0]
    for partner in big[1:]:
        other_pair = [e for e in big if e not in (a, partner)]
        options.append(("big_2+2:" + "-".join(map(str, a)) + ":" + "-".join(map(str, partner)), [[a, partner], other_pair, pair]))
    assert len(options) == 8
    enriched = []
    for label, subgroups in options:
        rows = []
        for subgroup in subgroups:
            rows.extend(subgroup_rows(subgroup))
        assert len(rows) == 3
        enriched.append((label, subgroups, rows))
    return enriched


OPTIONS = [vertex_options(v) for v in range(8)]


def main():
    states = {tuple(): tuple()}
    state_counts = [1]
    rank_ranges = []
    for vertex in range(8):
        next_states = {}
        for span, witness in states.items():
            for option_index, (_, _, rows) in enumerate(OPTIONS[vertex]):
                new_span = merge_span(span, rows)
                next_states.setdefault(new_span, witness + (option_index,))
        states = next_states
        state_counts.append(len(states))
        ranks = [len(span) for span in states]
        rank_ranges.append([min(ranks), max(ranks)])

    final_ranks = defaultdict(int)
    witnesses = {}
    for span, witness in states.items():
        rank = len(span)
        final_ranks[rank] += 1
        witnesses.setdefault(rank, witness)
    minimum_rank = min(final_ranks)
    minimum_witness = witnesses[minimum_rank]
    exact_rank = matrix_rank(exact_rows(minimum_witness))
    assert exact_rank == minimum_rank

    result = {
        "search": "all 8^8 minimal one-split-per-vertex H8 local-4 relaxations",
        "verification_field": f"GF({P}), sqrt(3)={SQRT3_MOD_P}",
        "distinct_row_space_counts_after_each_vertex": state_counts,
        "rank_range_after_each_added_vertex": rank_ranges,
        "final_row_space_rank_distribution": dict(sorted(final_ranks.items())),
        "minimum_modular_rank": minimum_rank,
        "minimum_witness_exact_rank_Qsqrt3": exact_rank,
        "minimum_witness": {
            NAMES[v]: OPTIONS[v][option][0] for v, option in enumerate(minimum_witness)
        },
        "interpretation": (
            "rank 12 means only the four similarity motions remain at H8; "
            "rank below 12 identifies an infinitesimal relaxation direction"
        ),
        "status": "VERIFIED",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
