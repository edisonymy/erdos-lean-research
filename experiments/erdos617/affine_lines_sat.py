"""SAT search in an affine-line monochromatic construction family.

The 25 finite vertices are F_5^2.  Each of the 30 affine lines is assigned
one color, and every finite edge takes the color of its unique line.  The 25
edges to an extra vertex are independently colored.  This strictly contains
the usual parallel-class construction while retaining useful geometry.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


Q = 5
N = 26
C = 5


def pt(x: int, y: int) -> int:
    return 5 * x + y


# Lines are (direction, intercept). Directions 0..4 have y=m*x+b;
# direction 5 is x=b.
LINES = [(d, b) for d in range(6) for b in range(5)]
LINE_INDEX = {line: i for i, line in enumerate(LINES)}
STAR_OFFSET = len(LINES)


def line_of(u: int, v: int) -> int:
    x1, y1 = divmod(u, 5)
    x2, y2 = divmod(v, 5)
    if x1 == x2:
        return LINE_INDEX[(5, x1)]
    m = ((y2 - y1) * pow((x2 - x1) % 5, -1, 5)) % 5
    b = (y1 - m * x1) % 5
    return LINE_INDEX[(m, b)]


def var(obj: int, color: int) -> int:
    return obj * C + color + 1


def edge_object(u: int, v: int) -> int:
    if v == 25:
        return STAR_OFFSET + u
    return line_of(u, v)


def decode(model: list[int]) -> list[list[int]]:
    positive = {x for x in model if x > 0}
    object_color = []
    for obj in range(55):
        cs = [c for c in range(C) if var(obj, c) in positive]
        assert len(cs) == 1
        object_color.append(cs[0])
    matrix = [[-1 if u == v else -2 for v in range(N)] for u in range(N)]
    for u in range(N):
        for v in range(u + 1, N):
            matrix[u][v] = matrix[v][u] = object_color[edge_object(u, v)]
    return matrix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--six-lines-per-color", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("affine_lines_candidate.json"))
    args = parser.parse_args()
    start = time.monotonic()
    solver = Solver(name=args.solver)
    for obj in range(55):
        solver.add_clause([var(obj, c) for c in range(C)])
        for c, d in itertools.combinations(range(C), 2):
            solver.add_clause([-var(obj, c), -var(obj, d)])
    # Global color symmetry.
    solver.add_clause([var(0, 0)])
    top_id = 55 * C
    if args.six_lines_per_color:
        for c in range(C):
            card = CardEnc.equals([var(line, c) for line in range(30)], bound=6,
                                  top_id=top_id, encoding=EncType.seqcounter)
            solver.append_formula(card.clauses)
            top_id = card.nv
    phase = []
    for obj in range(55):
        chosen = (LINES[obj][0] % 5) if obj < 30 else ((obj - 30) % 5)
        phase.extend(var(obj, c) if c == chosen else -var(obj, c) for c in range(C))
    solver.set_phases(phase)

    added: set[tuple[int, ...]] = set()
    iteration = 0
    while solver.solve():
        iteration += 1
        matrix = decode(solver.get_model())
        violations = 0
        new_clauses = 0
        for subset in itertools.combinations(range(N), 6):
            seen = {matrix[u][v] for u, v in itertools.combinations(subset, 2)}
            for c in range(C):
                if c not in seen:
                    violations += 1
                    objects = sorted({edge_object(u, v) for u, v in itertools.combinations(subset, 2)})
                    clause = tuple(var(obj, c) for obj in objects)
                    if clause not in added:
                        added.add(clause)
                        solver.add_clause(list(clause))
                        new_clauses += 1
        print(f"iteration={iteration} violations={violations} new_clauses={new_clauses} "
              f"total_clauses={len(added)} elapsed={time.monotonic()-start:.3f}", flush=True)
        if violations == 0:
            args.output.write_text(json.dumps({"n": N, "colors": C, "matrix": matrix}, indent=2) + "\n")
            print(f"FOUND output={args.output.resolve()}")
            return
        if new_clauses == 0:
            raise RuntimeError("violations produced no new clauses")
    print(f"UNSAT iterations={iteration} unique_coverage_clauses={len(added)} "
          f"elapsed={time.monotonic()-start:.3f}")


if __name__ == "__main__":
    main()
