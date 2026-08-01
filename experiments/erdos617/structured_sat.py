"""Search for a K_26 balanced 5-coloring extending the affine-plane K_25 construction.

Vertices 0..24 are (x,y) in F_5^2 (vertex = 5*x+y); vertex 25 is new.
Every nonvertical affine edge receives its slope in F_5.  The 50 vertical
affine edges and 25 edges incident with 25 are SAT variables.  We require
every six vertices to see all five colors.

The generated certificate is a 26 by 26 JSON color matrix with entries 0..4
off the diagonal and -1 on the diagonal.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from pysat.solvers import Solver


N = 26
Q = 5


def affine_vertex(x: int, y: int) -> int:
    return Q * x + y


def flexible_edges() -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    # Vertical edges (equal x).
    for x in range(Q):
        for y1 in range(Q):
            for y2 in range(y1 + 1, Q):
                edges.append((affine_vertex(x, y1), affine_vertex(x, y2)))
    # Edges to the new vertex.
    edges.extend((v, 25) for v in range(25))
    return edges


def variable(edge_index: int, color: int) -> int:
    return edge_index * Q + color + 1


def build_solver(name: str) -> tuple[Solver, list[tuple[int, int]], dict[tuple[int, int], int], int]:
    edges = flexible_edges()
    edge_to_index = {e: i for i, e in enumerate(edges)}
    solver = Solver(name=name)

    # Exactly one color per flexible edge.
    for ei in range(len(edges)):
        solver.add_clause([variable(ei, c) for c in range(Q)])
        for c1 in range(Q):
            for c2 in range(c1 + 1, Q):
                solver.add_clause([-variable(ei, c1), -variable(ei, c2)])

    coverage_clauses = 0
    # A six-set wholly inside the affine plane is already covered by the five
    # slope classes.  A set containing vertex 25 is {25} plus five affine
    # points.  For color m, it is automatically covered unless the points
    # lie on five distinct lines y-m*x=b.  Enumerate precisely those cases.
    points = [(x, y) for x in range(Q) for y in range(Q)]
    for m in range(Q):
        lines: list[list[tuple[int, int]]] = [[] for _ in range(Q)]
        for x, y in points:
            lines[(y - m * x) % Q].append((x, y))

        # Select one point on each of the five parallel lines.
        for chosen in itertools.product(*lines):
            verts = [affine_vertex(x, y) for x, y in chosen]
            lits = [variable(edge_to_index[(v, 25)], m) for v in verts]
            # The only flexible affine edges are the vertical ones.
            for a, b in itertools.combinations(chosen, 2):
                if a[0] == b[0]:
                    u, v = sorted((affine_vertex(*a), affine_vertex(*b)))
                    lits.append(variable(edge_to_index[(u, v)], m))
            solver.add_clause(lits)
            coverage_clauses += 1

    return solver, edges, edge_to_index, coverage_clauses


def decode(model: list[int], edges: list[tuple[int, int]]) -> list[list[int]]:
    positive = set(x for x in model if x > 0)
    matrix = [[-1 if u == v else -2 for v in range(N)] for u in range(N)]
    for u in range(25):
        x1, y1 = divmod(u, Q)
        for v in range(u + 1, 25):
            x2, y2 = divmod(v, Q)
            if x1 != x2:
                color = ((y2 - y1) * pow((x2 - x1) % Q, -1, Q)) % Q
                matrix[u][v] = matrix[v][u] = color
    for ei, (u, v) in enumerate(edges):
        colors = [c for c in range(Q) if variable(ei, c) in positive]
        if len(colors) != 1:
            raise RuntimeError(f"edge {(u, v)} has decoded colors {colors}")
        matrix[u][v] = matrix[v][u] = colors[0]
    assert all(matrix[u][v] >= 0 for u in range(N) for v in range(N) if u != v)
    return matrix


def exhaustive_check(matrix: list[list[int]]) -> tuple[bool, int, tuple[int, ...] | None, int | None]:
    checked = 0
    for subset in itertools.combinations(range(N), 6):
        mask = 0
        for u, v in itertools.combinations(subset, 2):
            mask |= 1 << matrix[u][v]
        checked += 1
        if mask != (1 << Q) - 1:
            missing = next(c for c in range(Q) if not (mask >> c) & 1)
            return False, checked, subset, missing
    return True, checked, None, None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("structured_candidate.json"))
    args = parser.parse_args()

    started = time.time()
    solver, edges, _, clauses = build_solver(args.solver)
    print(f"solver={args.solver} flexible_edges={len(edges)} coverage_clauses={clauses}", flush=True)
    sat = solver.solve()
    elapsed = time.time() - started
    print(f"sat={sat} elapsed_seconds={elapsed:.6f}", flush=True)
    if not sat:
        return
    matrix = decode(solver.get_model(), edges)
    good, checked, bad_set, missing = exhaustive_check(matrix)
    print(f"verified={good} six_sets_checked={checked} bad_set={bad_set} missing={missing}", flush=True)
    if not good:
        raise SystemExit(2)
    args.output.write_text(json.dumps({"n": N, "colors": Q, "matrix": matrix}, indent=2) + "\n")
    print(f"wrote={args.output.resolve()}", flush=True)


if __name__ == "__main__":
    main()
