"""Exact SAT search for a balanced 5-coloring of K_26.

This supports a lazy cutting-plane mode (add every violated six-set/color
clause in the current model) and a full mode (materialize all 1,151,150
coverage clauses before solving).  A timeout returns UNKNOWN, never UNSAT.
"""

from __future__ import annotations

import argparse
import itertools
import json
import threading
import time
from pathlib import Path

from pysat.solvers import Solver


N = 26
COLORS = 5
EDGES = [(u, v) for u in range(N) for v in range(u + 1, N)]
EDGE_INDEX = {e: i for i, e in enumerate(EDGES)}


def var(e: int, c: int) -> int:
    return e * COLORS + c + 1


def sixsets():
    for verts in itertools.combinations(range(N), 6):
        yield tuple(EDGE_INDEX[(u, v)] for u, v in itertools.combinations(verts, 2))


def affine_phase() -> list[int]:
    phase = []
    for e, (u, v) in enumerate(EDGES):
        if v == 25:
            c = u % COLORS
        else:
            x1, y1 = divmod(u, 5)
            x2, y2 = divmod(v, 5)
            if x1 == x2:
                c = (y1 + y2 + x1) % 5
            else:
                c = ((y2 - y1) * pow((x2 - x1) % 5, -1, 5)) % 5
        phase.extend(var(e, d) if d == c else -var(e, d) for d in range(COLORS))
    return phase


def base_solver(name: str, symmetry: bool) -> Solver:
    solver = Solver(name=name)
    for e in range(len(EDGES)):
        solver.add_clause([var(e, c) for c in range(COLORS)])
        for c, d in itertools.combinations(range(COLORS), 2):
            solver.add_clause([-var(e, c), -var(e, d)])

    if symmetry:
        # Relabel vertices 1..25 so the colors on edges from vertex 0 are
        # nondecreasing.  Then relabel colors so the first block is color 0.
        # This is sound even when one or more colors do not occur at vertex 0.
        star = [EDGE_INDEX[(0, v)] for v in range(1, N)]
        solver.add_clause([var(star[0], 0)])
        for left, right in zip(star, star[1:]):
            for c in range(COLORS):
                for d in range(c):
                    solver.add_clause([-var(left, c), -var(right, d)])
    solver.set_phases(affine_phase())
    return solver


def decode(model: list[int]) -> tuple[list[int], list[list[int]]]:
    pos = {x for x in model if x > 0}
    edge_colors = []
    for e in range(len(EDGES)):
        cs = [c for c in range(COLORS) if var(e, c) in pos]
        if len(cs) != 1:
            raise RuntimeError((e, cs))
        edge_colors.append(cs[0])
    matrix = [[-1 if u == v else -2 for v in range(N)] for u in range(N)]
    for e, (u, v) in enumerate(EDGES):
        matrix[u][v] = matrix[v][u] = edge_colors[e]
    return edge_colors, matrix


def solve_with_timeout(solver: Solver, timeout: float | None) -> bool | None:
    if timeout is None:
        return solver.solve()
    timer = threading.Timer(timeout, solver.interrupt)
    timer.start()
    try:
        return solver.solve_limited(expect_interrupt=True)
    finally:
        timer.cancel()
        try:
            solver.clear_interrupt()
        except NotImplementedError:
            # CaDiCaL's PySAT wrapper accepts interrupt-driven limited solves
            # but does not expose a separate clear operation.
            pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--mode", choices=("lazy", "full"), default="lazy")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--no-symmetry", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("full_sat_candidate.json"))
    args = parser.parse_args()

    start = time.monotonic()
    deadline = start + args.timeout if args.timeout > 0 else None
    solver = base_solver(args.solver, not args.no_symmetry)
    added = 0
    iteration = 0

    if args.mode == "full":
        for es in sixsets():
            for c in range(COLORS):
                solver.add_clause([var(e, c) for e in es])
                added += 1
        print(f"full_encoding coverage_clauses={added} build_seconds={time.monotonic()-start:.3f}", flush=True)

    while True:
        remaining = None if deadline is None else max(0.001, deadline - time.monotonic())
        result = solve_with_timeout(solver, remaining)
        iteration += 1
        elapsed = time.monotonic() - start
        stats = solver.accum_stats()
        print(f"iteration={iteration} result={result} clauses_added={added} elapsed={elapsed:.3f} stats={stats}", flush=True)
        if result is None:
            print("UNKNOWN timeout", flush=True)
            return
        if result is False:
            print("UNSAT", flush=True)
            return

        edge_colors, matrix = decode(solver.get_model())
        violations: list[tuple[tuple[int, ...], int]] = []
        for es in sixsets():
            mask = 0
            for e in es:
                mask |= 1 << edge_colors[e]
            if mask != 31:
                for c in range(COLORS):
                    if not (mask >> c) & 1:
                        violations.append((es, c))
        print(f"iteration={iteration} violations={len(violations)}", flush=True)
        if not violations:
            payload = {"n": N, "colors": COLORS, "matrix": matrix,
                       "solver": args.solver, "mode": args.mode}
            args.output.write_text(json.dumps(payload, indent=2) + "\n")
            print(f"FOUND verified_six_sets=230230 output={args.output.resolve()}", flush=True)
            return
        if args.mode == "full":
            raise RuntimeError("full encoding returned a violating model")
        for es, c in violations:
            solver.add_clause([var(e, c) for e in es])
            added += 1


if __name__ == "__main__":
    main()
