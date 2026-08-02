#!/usr/bin/env python3
"""Reproduce the h=8 fractional-count audit for Erdos problem 151.

This is deliberately a count relaxation, not a graph-existence encoding.
It checks exact arithmetic, solves the explicitly documented aggregate LP
(and its integral-count strengthening), and verifies the local 8-vertex
MILP used in the optional second-order overlap calculation.
"""

from __future__ import annotations

import argparse
import itertools
import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp


N = 28
H = 8
R = 7
X_SIZE = N - R


@dataclass(frozen=True)
class Row:
    name: str
    coeffs: dict[str, float]
    lower: float = -np.inf
    upper: float = np.inf


class Model:
    def __init__(self) -> None:
        self.names: list[str] = []
        self.index: dict[str, int] = {}
        self.lower: list[float] = []
        self.upper: list[float] = []
        self.rows: list[Row] = []

    def var(self, name: str, lower: float = 0.0, upper: float = np.inf) -> None:
        assert name not in self.index
        self.index[name] = len(self.names)
        self.names.append(name)
        self.lower.append(lower)
        self.upper.append(upper)

    def row(
        self,
        name: str,
        coeffs: dict[str, float],
        lower: float = -np.inf,
        upper: float = np.inf,
    ) -> None:
        assert all(v in self.index for v in coeffs)
        self.rows.append(Row(name, coeffs, lower, upper))

    def matrix(self) -> np.ndarray:
        a = np.zeros((len(self.rows), len(self.names)))
        for i, row in enumerate(self.rows):
            for name, value in row.coeffs.items():
                a[i, self.index[name]] = value
        return a


def add(dst: dict[str, float], name: str, value: float) -> None:
    dst[name] = dst.get(name, 0.0) + value


def build_aggregate_model() -> Model:
    """Build the single-base marginal projection P8 documented in README."""
    m = Model()
    x_names: list[tuple[int, int, str]] = []
    for d in range(5, 8):
        for c in range(1, d + 1):
            name = f"x_c{c}_d{d}"
            m.var(name, 0, X_SIZE)
            x_names.append((c, d, name))
    for d in range(5, 8):
        m.var(f"s_d{d}", 0, R)
    m.var("p", 0, 16)       # edges of G[S]; S is K4-free
    m.var("q", 0, math.comb(X_SIZE, 2))  # edges of G[X]
    m.var("z", 0, R)        # isolated vertices of G[S]
    m.var("u", 0, 12)       # triangles of G[S]; Zykov bound
    m.var("T", 0, 100)      # all ambient triangles
    for k in range(1, 4):
        m.var(f"a{k}", 0, 200)  # fixed-S anchor incidences of size k
    m.var("N2", 0, 98)
    m.var("N3", 0, 200)
    m.var("N4", 0, 200)

    # Cardinalities and the two degree handshakes.
    m.row("X has 21 vertices", {name: 1 for _, _, name in x_names}, X_SIZE, X_SIZE)
    m.row("S has 7 vertices", {f"s_d{d}": 1 for d in range(5, 8)}, R, R)
    row: dict[str, float] = {"p": 2}
    for c, _, name in x_names:
        add(row, name, c)
    for d in range(5, 8):
        add(row, f"s_d{d}", -d)
    m.row("S-X edge handshake (E5 exactly)", row, 0, 0)
    row = {"q": 2}
    for c, d, name in x_names:
        add(row, name, -(d - c))
    m.row("X internal-degree handshake", row, 0, 0)

    # Necessary alpha(G[X]) <= 7 consequences.
    row = {}
    for c, d, name in x_names:
        add(row, name, 1 / (d - c + 1))
    m.row("Caro-Wei on X", row, upper=R)
    m.row("Turan on X", {"q": 1}, lower=21)

    # F4 plus the proved exact-fibre lemma for c=1, and elementary z-p bounds.
    row = {"z": -1}
    for c, _, name in x_names:
        if c == 1:
            add(row, name, 1)
    m.row("exact c=1 fibres use distinct isolated S vertices", row, upper=0)
    m.row("nonisolated S vertices meet an S-edge", {"p": 2, "z": 1}, lower=R)
    m.row("isolated S vertices contribute no S-degree", {"p": 2, "z": 6}, upper=42)
    m.row("each S-triangle uses three edges", {"u": 3, "p": -5}, upper=0)

    # One anchor per outside vertex, with anchor size at most min(c,3).
    x_by_c: dict[int, list[str]] = {c: [] for c in range(1, 8)}
    for c, _, name in x_names:
        x_by_c[c].append(name)
    m.row(
        "c=1 vertices need singleton anchors",
        {**{name: 1 for name in x_by_c[1]}, "a1": -1},
        upper=0,
    )
    row = {"a1": -1, "a2": -1}
    for c in (1, 2):
        for name in x_by_c[c]:
            add(row, name, 1)
    m.row("c<=2 vertices need anchors of size <=2", row, upper=0)
    m.row("E1 anchor coverage", {"a1": 1, "a2": 1, "a3": 1}, lower=X_SIZE)

    # There cannot be more size-k anchors than k-subsets in S-neighbourhoods.
    for k in range(1, 4):
        row = {f"a{k}": 1}
        for c, _, name in x_names:
            if c >= k:
                add(row, name, -math.comb(c, k))
        m.row(f"available size-{k} attachment subsets", row, upper=0)

    # E2: at most alpha(G)<=7 vertices per fixed anchor clique.
    m.row("E2 singleton-anchor capacity", {"a1": 1}, upper=49)
    m.row("E2 edge-anchor capacity", {"a2": 1, "p": -7}, upper=0)
    m.row("E2 triangle-anchor capacity", {"a3": 1, "u": -7}, upper=0)

    # For fixed S, an anchor incidence injects into an ambient maximal clique.
    for k in range(1, 4):
        m.row(
            f"size-{k} anchors inject into N{k + 1}",
            {f"a{k}": 1, f"N{k + 1}": -1},
            upper=0,
        )

    # F2.  With omega<=4 this is both the ordinary and the stated L-union count.
    cover = {
        "N2": math.comb(26, 6),
        "N3": math.comb(25, 5),
        "N4": math.comb(24, 4),
    }
    m.row("F2 h-set coverage", cover, lower=math.comb(28, 8))

    # The audited order-28 reduction forces an ambient-maximal K4.
    m.row("order28_36 K4 consequence", {"N4": 1}, lower=1)

    # Elementary global clique/triangle supply constraints.
    total_edges: dict[str, float] = {"p": 1, "q": 1}
    for c, _, name in x_names:
        add(total_edges, name, c)
    row = dict(total_edges)
    add(row, "N2", -1)
    m.row("maximal edges are edges", row, lower=0)  # E - N2 >= 0
    row = dict(total_edges)
    add(row, "N2", -1)
    add(row, "N3", -3)
    add(row, "N4", -6)
    m.row("every edge extends to a maximal clique", row, upper=0)
    row = dict(total_edges)
    add(row, "N2", -1)
    add(row, "T", -3)
    m.row("every non-L edge lies in a triangle", row, upper=0)

    m.row("maximal triangles are triangles", {"N3": 1, "T": -1}, upper=0)
    m.row(
        "nonmaximal triangles lie in K4s",
        {"T": 1, "N3": -1, "N4": -4},
        upper=0,
    )
    m.row(
        "a triangle extends to at most five K4s",
        {"N4": 4, "T": -5, "N3": 5},
        upper=0,
    )

    # Local total-triangle caps: ex(d,K4) for d=5,6, and the audited raw
    # two-walk cap 11 for degree-seven vertices in a mixed profile.
    triangle_cap = {5: 8, 6: 12, 7: 11}
    row = {"T": 3}
    for d in range(5, 8):
        add(row, f"s_d{d}", -triangle_cap[d])
    for _, d, name in x_names:
        add(row, name, -triangle_cap[d])
    m.row("sum of local triangle caps", row, upper=0)

    # K4s through a vertex are triangles in its K4-free link.  Zykov gives
    # 4, 8, 12 such triangles for link orders 5, 6, 7 respectively.
    k4_cap = {5: 4, 6: 8, 7: 12}
    row = {"N4": 4}
    for d in range(5, 8):
        add(row, f"s_d{d}", -k4_cap[d])
    for _, d, name in x_names:
        add(row, name, -k4_cap[d])
    m.row("sum of local K4 caps", row, upper=0)
    return m


def solve_aggregate(integral: bool) -> tuple[Model, np.ndarray]:
    m = build_aggregate_model()
    a = m.matrix()
    objective = np.zeros(len(m.names))
    for name in ("N2", "N3", "N4"):
        objective[m.index[name]] = 1

    if integral:
        constraints = LinearConstraint(
            a,
            np.array([r.lower for r in m.rows]),
            np.array([r.upper for r in m.rows]),
        )
        result = milp(
            objective,
            integrality=np.ones(len(m.names)),
            bounds=Bounds(np.array(m.lower), np.array(m.upper)),
            constraints=constraints,
            options={"time_limit": 30},
        )
    else:
        a_ub: list[np.ndarray] = []
        b_ub: list[float] = []
        a_eq: list[np.ndarray] = []
        b_eq: list[float] = []
        for vector, row in zip(a, m.rows):
            if row.lower == row.upper:
                a_eq.append(vector)
                b_eq.append(row.lower)
            else:
                if np.isfinite(row.upper):
                    a_ub.append(vector)
                    b_ub.append(row.upper)
                if np.isfinite(row.lower):
                    a_ub.append(-vector)
                    b_ub.append(-row.lower)
        result = linprog(
            objective,
            A_ub=np.array(a_ub),
            b_ub=np.array(b_ub),
            A_eq=np.array(a_eq),
            b_eq=np.array(b_eq),
            bounds=list(zip(m.lower, m.upper)),
            method="highs",
        )
    if not result.success:
        raise RuntimeError(f"aggregate {'MILP' if integral else 'LP'} failed: {result.message}")
    return m, result.x


def verify_solution(m: Model, values: np.ndarray, tolerance: float = 1e-6) -> None:
    assert np.all(values >= np.array(m.lower) - tolerance)
    assert np.all(values <= np.array(m.upper) + tolerance)
    lhs = m.matrix() @ values
    for value, row in zip(lhs, m.rows):
        assert value >= row.lower - tolerance, (row.name, value, row.lower)
        assert value <= row.upper + tolerance, (row.name, value, row.upper)


def print_solution(label: str, m: Model, values: np.ndarray) -> None:
    verify_solution(m, values)
    print(f"\n{label}: FEASIBLE")
    for name, value in zip(m.names, values):
        if abs(value) > 1e-7:
            rounded = round(value)
            shown = str(rounded) if abs(value - rounded) < 1e-7 else f"{value:.8g}"
            print(f"  {name} = {shown}")


def exact_corner_and_overlap_table(local_max: int) -> None:
    universe = math.comb(28, 8)
    c2 = math.comb(26, 6)
    c3 = math.comb(25, 5)
    c4 = math.comb(24, 4)
    print("Exact normalized F2 coefficients:")
    print(f"  edge:     {c2}/{universe} = 1/{universe / c2:g}")
    print(f"  triangle: {c3}/{universe} = 1/{universe / c3:g}")
    print(f"  K4:       {c4}/{universe} = 1/{universe / c4:g}")
    lo = math.ceil(universe / c3)
    hi = math.floor(28 * 7 / 3)
    print(f"F3 projected integer window (coverage plus t_v<=7 only): {lo} <= N3 <= {hi}")
    # The full audited two-walk argument also retains ell_v, the number of
    # isolated link vertices.  It gives t_v <= 3*ell_v+1, while exactly
    # 7-ell_v link vertices must be covered by the t_v link edges.  At
    # ell_v=0 (i.e. L is empty) these say t_v<=1 and t_v>=4.
    ell = 0
    lower_t = math.ceil((7 - ell) / 2)
    upper_t = min(3 * ell + 1, math.comb(7 - ell, 2))
    assert lower_t == 4 and upper_t == 1
    print(
        "Full two-walk/L check at L=empty: "
        f"t_v >= {lower_t} from the link, but t_v <= {upper_t}; INFEASIBLE"
    )

    factor = local_max / 2
    print(
        f"\nCounterfactual second-order projection using m_W <= {local_max} "
        f"(factor {factor:g}):"
    )
    print("N3  D=I-U   A_min  V_min   P_min    P_min/factor   contradiction")
    for n3 in range(lo, hi + 1):
        total_t = 3 * n3
        base, remainder = divmod(total_t, 28)
        v_min = (28 - remainder) * math.comb(base, 2) + remainder * math.comb(base + 1, 2)
        a_min = 3 * n3 - 98
        p_min = 7315 * a_min + 1540 * v_min + 231 * math.comb(n3, 2)
        d = n3 * c3 - universe
        rhs = p_min / factor
        print(
            f"{n3:2d}  {d:7d}  {a_min:5d}  {v_min:5d}  {p_min:7d}"
            f"  {rhs:12.3f}   {'YES' if d + 1e-9 < rhs else 'no'}"
        )


def local_triangle_milp() -> tuple[int, list[tuple[int, int]], list[int]]:
    """Max triangles in a K4-free 8-vertex graph with t_v <= 7."""
    vertices = range(8)
    edges = list(itertools.combinations(vertices, 2))
    triangles = list(itertools.combinations(vertices, 3))
    edge_index = {e: i for i, e in enumerate(edges)}
    tri_offset = len(edges)
    size = len(edges) + len(triangles)
    rows: list[np.ndarray] = []
    lower: list[float] = []
    upper: list[float] = []

    def edge_id(a: int, b: int) -> int:
        return edge_index[tuple(sorted((a, b)))]

    # y_abc is exactly the conjunction of its three edge variables.
    for j, tri in enumerate(triangles):
        y = tri_offset + j
        tri_edges = [edge_id(a, b) for a, b in itertools.combinations(tri, 2)]
        for e in tri_edges:
            row = np.zeros(size)
            row[y] = 1
            row[e] = -1
            rows.append(row)
            lower.append(-np.inf)
            upper.append(0)
        row = np.zeros(size)
        row[y] = 1
        for e in tri_edges:
            row[e] -= 1
        rows.append(row)
        lower.append(-2)
        upper.append(np.inf)

    # K4-free and at most seven triangles through each vertex.
    for four in itertools.combinations(vertices, 4):
        row = np.zeros(size)
        for a, b in itertools.combinations(four, 2):
            row[edge_id(a, b)] = 1
        rows.append(row)
        lower.append(-np.inf)
        upper.append(5)
    for v in vertices:
        row = np.zeros(size)
        for j, tri in enumerate(triangles):
            if v in tri:
                row[tri_offset + j] = 1
        rows.append(row)
        lower.append(-np.inf)
        upper.append(7)

    objective = np.zeros(size)
    objective[tri_offset:] = -1
    result = milp(
        objective,
        integrality=np.ones(size),
        bounds=Bounds(np.zeros(size), np.ones(size)),
        constraints=LinearConstraint(np.array(rows), np.array(lower), np.array(upper)),
        options={"time_limit": 30},
    )
    if not result.success:
        raise RuntimeError(f"local triangle MILP failed: {result.message}")
    chosen_edges = [edge for edge, value in zip(edges, result.x[:tri_offset]) if value > 0.5]
    chosen = set(chosen_edges)
    actual_triangles = [
        tri
        for tri in triangles
        if all(tuple(sorted(edge)) in chosen for edge in itertools.combinations(tri, 2))
    ]
    assert not any(
        all(tuple(sorted(edge)) in chosen for edge in itertools.combinations(four, 2))
        for four in itertools.combinations(vertices, 4)
    )
    t_v = [sum(v in tri for tri in actual_triangles) for v in vertices]
    assert max(t_v, default=0) <= 7
    optimum = len(actual_triangles)
    assert abs(-result.fun - optimum) < 1e-6
    return optimum, chosen_edges, t_v


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-local-milp",
        action="store_true",
        help="skip the 8-vertex exact local optimization",
    )
    args = parser.parse_args()

    local_max = 18
    if not args.skip_local_milp:
        local_max, edges, t_v = local_triangle_milp()
        print(f"Local K4-free/t_v<=7 optimum: {local_max} triangles")
        print(f"  t_v = {t_v}")
        print(f"  witness edges = {edges}")

    exact_corner_and_overlap_table(local_max)
    lp_model, lp_values = solve_aggregate(integral=False)
    print_solution("Single-base aggregate LP", lp_model, lp_values)
    mip_model, mip_values = solve_aggregate(integral=True)
    print_solution("Integral-count strengthening", mip_model, mip_values)
    print("\nConclusion: these marginal constraints are feasible; they are not a contradiction.")


if __name__ == "__main__":
    main()
