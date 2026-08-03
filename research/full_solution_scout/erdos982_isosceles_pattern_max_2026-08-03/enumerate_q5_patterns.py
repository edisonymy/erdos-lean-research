#!/usr/bin/env python3
"""Enumerate global five-distance colour patterns for a convex decagon.

This is a necessary-condition search, not a Euclidean realization checker.
Vertices 0,...,9 are in cyclic order.  An edge colour represents a global
distance.  Every vertex must see exactly four colours.  We additionally use
only elementary, exact consequences of strict convexity:

* a base chord has at most one equal-distance witness on either cyclic arc;
* no four planar points are pairwise equidistant;
* the shortest-distance edges do not cross;
* disjoint longest-distance edges must cross (the diameter-thrackle lemma);
* some five consecutive vertices form a cap, so after a dihedral relabelling
  distances 01<02<03<04 and 43<42<41<40 are strictly increasing.

The last item follows from the standard smallest-enclosing-circle cap
decomposition.  We fix that cap to 0,1,2,3,4 and enumerate the possible
shortest/longest colours and the two endpoint colour orders.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

import z3


N = 10
Q = 5
VERTICES = range(N)
EDGES = tuple(itertools.combinations(VERTICES, 2))


def edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def crosses(e: tuple[int, int], f: tuple[int, int]) -> bool:
    """Whether two vertex-disjoint chords cross in the fixed cyclic order."""
    a, b = e
    c, d = f
    if len({a, b, c, d}) < 4:
        return False
    return (a < c < b < d) or (c < a < d < b)


def cyclic_side(base: tuple[int, int], apex: int) -> int:
    a, b = base
    return 0 if a < apex < b else 1


def canonical_relabel(colours: tuple[int, ...]) -> tuple[int, ...]:
    """Canonicalize colour names by first occurrence in lexicographic edges."""
    mapping: dict[int, int] = {}
    answer = []
    for colour in colours:
        if colour not in mapping:
            mapping[colour] = len(mapping)
        answer.append(mapping[colour])
    return tuple(answer)


def dihedral_edge_pattern(colours: tuple[int, ...], shift: int, reflect: bool) -> tuple[int, ...]:
    by_edge = dict(zip(EDGES, colours))

    def tv(v: int) -> int:
        return ((-v if reflect else v) + shift) % N

    transformed = {}
    for (a, b), colour in by_edge.items():
        transformed[edge(tv(a), tv(b))] = colour
    return canonical_relabel(tuple(transformed[e] for e in EDGES))


def canonical_dihedral(colours: tuple[int, ...]) -> tuple[int, ...]:
    return min(
        dihedral_edge_pattern(colours, shift, reflect)
        for shift in VERTICES
        for reflect in (False, True)
    )


def build_solver(shortest: int, longest: int, order0: tuple[int, ...], order4: tuple[int, ...]):
    assert shortest != longest
    solver = z3.Solver()
    colour = {e: z3.Int(f"c_{e[0]}_{e[1]}") for e in EDGES}
    for value in colour.values():
        solver.add(0 <= value, value < Q)

    # Exactly four global distances are visible at each vertex.
    used = {}
    for v in VERTICES:
        for c in range(Q):
            flag = z3.Bool(f"u_{v}_{c}")
            incident = [colour[edge(v, w)] == c for w in VERTICES if w != v]
            solver.add(flag == z3.Or(incident))
            used[v, c] = flag
        solver.add(z3.PbEq([(used[v, c], 1) for c in range(Q)], 4))

    # Each named global distance actually occurs.
    for c in range(Q):
        solver.add(z3.Or([value == c for value in colour.values()]))

    # A five-vertex cap, with its two endpoint distance orders fixed.
    cap0 = (edge(0, 1), edge(0, 2), edge(0, 3), edge(0, 4))
    cap4 = (edge(4, 3), edge(4, 2), edge(4, 1), edge(4, 0))
    for e, c in zip(cap0, order0):
        solver.add(colour[e] == c)
    for e, c in zip(cap4, order4):
        solver.add(colour[e] == c)

    # At most one witness on each open cyclic side of every base chord.
    for base in EDGES:
        others = [v for v in VERTICES if v not in base]
        for side in (0, 1):
            apices = [v for v in others if cyclic_side(base, v) == side]
            witnesses = [
                colour[edge(v, base[0])] == colour[edge(v, base[1])]
                for v in apices
            ]
            if len(witnesses) > 1:
                solver.add(z3.PbLe([(w, 1) for w in witnesses], 1))

    # Four pairwise equal distances are impossible in the Euclidean plane.
    for quad in itertools.combinations(VERTICES, 4):
        qedges = [colour[e] for e in itertools.combinations(quad, 2)]
        solver.add(z3.Not(z3.And([qedges[i] == qedges[0] for i in range(1, 6)])))

    # The shortest distance graph is noncrossing.
    # The diameter graph is a convex geometric thrackle.
    for e, f in itertools.combinations(EDGES, 2):
        if crosses(e, f):
            solver.add(z3.Or(colour[e] != shortest, colour[f] != shortest))
        elif len(set(e + f)) == 4:
            solver.add(z3.Or(colour[e] != longest, colour[f] != longest))

    return solver, colour


def model_record(model, colour, shortest, longest, order0, order4):
    values = tuple(model.eval(colour[e]).as_long() for e in EDGES)
    edge_counts = [values.count(c) for c in range(Q)]
    supports = []
    degree_profiles = []
    for c in range(Q):
        degrees = [sum(values[EDGES.index(edge(v, w))] == c for w in VERTICES if w != v) for v in VERTICES]
        supports.append(sum(d > 0 for d in degrees))
        degree_profiles.append(sorted((d for d in degrees if d), reverse=True))
    return {
        "edge_colours": list(values),
        "edge_counts": edge_counts,
        "support_sizes": supports,
        "degree_profiles": degree_profiles,
        "shortest_colour": shortest,
        "longest_colour": longest,
        "cap_order_at_0": list(order0),
        "cap_order_at_4": list(order4),
        "canonical_dihedral": list(canonical_dihedral(values)),
    }


def run(max_models: int, seconds: float, retain: int) -> dict:
    started = time.monotonic()
    records = []
    canonical_seen = set()
    raw = 0
    cases_started = 0
    sat_cases = 0
    stopped = "EXHAUSTIVE"

    # Fix the colour names at vertex 0.  Its four strictly increasing cap
    # distances are 0,1,2,3; colour 4 is the unique missing colour there.
    order0 = (0, 1, 2, 3)
    # Vertex 4 also sees four distinct cap distances.  Its order is an
    # injection into five colours containing c(04)=3 in the final position.
    order4s = [p + (3,) for p in itertools.permutations((0, 1, 2, 4), 3)]

    for order4 in order4s:
        if len(set(order4)) != 4:
            continue
        for shortest in range(Q):
            for longest in range(Q):
                if shortest == longest:
                    continue
                # Cap endpoint orders immediately identify the shortest and
                # longest colours whenever the relevant global extrema occur
                # among these four values.  Even without that assumption, the
                # strict order forbids inversions with known global extrema.
                if shortest in order0 and order0.index(shortest) != 0:
                    continue
                if longest in order0 and order0.index(longest) != 3:
                    continue
                if shortest in order4 and order4.index(shortest) != 0:
                    continue
                if longest in order4 and order4.index(longest) != 3:
                    continue

                if time.monotonic() - started >= seconds:
                    stopped = "TIME_CAP"
                    break
                cases_started += 1
                solver, colour = build_solver(shortest, longest, order0, order4)
                while raw < max_models and time.monotonic() - started < seconds:
                    status = solver.check()
                    if status != z3.sat:
                        break
                    if raw == 0 or (raw and raw % 100 == 0):
                        pass
                    sat_cases += int(raw == 0)
                    model = solver.model()
                    raw += 1
                    record = model_record(model, colour, shortest, longest, order0, order4)
                    key = tuple(record["canonical_dihedral"])
                    if key not in canonical_seen:
                        canonical_seen.add(key)
                        if len(records) < retain:
                            records.append(record)
                    block = z3.Or([
                        colour[e] != model.eval(colour[e]).as_long() for e in EDGES
                    ])
                    solver.add(block)
                if raw >= max_models:
                    stopped = "MODEL_CAP"
                    break
                if time.monotonic() - started >= seconds:
                    stopped = "TIME_CAP"
                    break
            if stopped != "EXHAUSTIVE":
                break
        if stopped != "EXHAUSTIVE":
            break

    elapsed = time.monotonic() - started
    return {
        "status": stopped,
        "n": N,
        "global_distance_colours": Q,
        "raw_models": raw,
        "dihedral_colour_orbits_seen": len(canonical_seen),
        "cases_started": cases_started,
        "elapsed_seconds": elapsed,
        "max_models": max_models,
        "seconds": seconds,
        "retained": records,
        "scope": "necessary global-five-distance colour patterns with cap, witness-side, shortest and diameter constraints; not Euclidean realizability",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-models", type=int, default=10_000)
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--retain", type=int, default=1_000)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("q5_patterns.json"))
    args = parser.parse_args()
    payload = run(args.max_models, args.seconds, args.retain)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "retained"}, sort_keys=True))
    print("sha256", hashlib.sha256(args.out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
