#!/usr/bin/env python3
"""Audit the finite arithmetic used in K4FREE_ORDER41.md.

This standard-library checker verifies the seven displayed degree-eight
links numerically and checks the order-40/41 arithmetic.  Completeness of
the seven-link list is Bikov's Theorem 8.2 and is intentionally not claimed
by this program.
"""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path


LINK_CODES = (
    "G?`F`w",
    "G?bF`w",
    "G?rF`w",
    "G?q`qg",
    "GCQb`o",
    "GCR`r_",
    "GCrb`o",
)
EXPECTED_EDGES = (10, 11, 12, 10, 10, 11, 12)


def decode_graph6(code: str) -> tuple[int, list[tuple[int, int]]]:
    """Decode the one-byte-order graph6 format (enough for n=8 here)."""
    data = [ord(ch) - 63 for ch in code.strip()]
    n = data[0]
    bits: list[int] = []
    for value in data[1:]:
        bits.extend((value >> shift) & 1 for shift in range(5, -1, -1))
    edges: list[tuple[int, int]] = []
    cursor = 0
    # graph6 uses upper triangle in column-major order.
    for v in range(1, n):
        for u in range(v):
            if bits[cursor]:
                edges.append((u, v))
            cursor += 1
    return n, edges


def triangle_free(n: int, edges: list[tuple[int, int]]) -> bool:
    eset = {tuple(sorted(edge)) for edge in edges}
    return not any(
        (a, b) in eset and (a, c) in eset and (b, c) in eset
        for a, b, c in combinations(range(n), 3)
    )


def obstructing_signing(
    n: int, edges: list[tuple[int, int]]
) -> int | None:
    """Return a signing for which no safe apex-spoke coloring exists.

    Sign 0/1 is the edge color.  A spoke assignment is spoiled when some
    signed edge has both endpoint spokes equal to its sign.
    """
    violation: list[tuple[int, int]] = []
    for u, v in edges:
        masks = [0, 0]
        for assignment in range(1 << n):
            cu = (assignment >> u) & 1
            cv = (assignment >> v) & 1
            if cu == cv:
                masks[cu] |= 1 << assignment
        violation.append((masks[0], masks[1]))

    all_assignments = (1 << (1 << n)) - 1
    for signing in range(1 << len(edges)):
        spoiled = 0
        for edge_id, masks in enumerate(violation):
            spoiled |= masks[(signing >> edge_id) & 1]
        if spoiled == all_assignments:
            return signing
    return None


def even_floor(value: int) -> int:
    return value if value % 2 == 0 else value - 1


def main() -> int:
    link_rows = []
    for code, expected in zip(LINK_CODES, EXPECTED_EDGES, strict=True):
        n, edges = decode_graph6(code)
        degrees = [0] * n
        for u, v in edges:
            degrees[u] += 1
            degrees[v] += 1
        witness = obstructing_signing(n, edges)
        row = {
            "graph6": code,
            "vertices": n,
            "edges": len(edges),
            "degrees": sorted(degrees),
            "triangle_free": triangle_free(n, edges),
            "obstructing_signing": witness,
        }
        assert n == 8
        assert len(edges) == expected
        assert min(degrees) >= 2
        assert row["triangle_free"]
        assert witness is not None
        link_rows.append(row)

    # For an ambient degree-nine vertex with t triangles, the two-walk
    # argument gives u >= 2*t + 2*n - 92, while the swap argument gives u<=9.
    unique_lower = {
        str(n): 2 * 10 + 2 * n - 92 for n in (40, 41)
    }
    assert unique_lower == {"40": 8, "41": 10}
    assert unique_lower["41"] > 9

    # Pairwise unions of eight color classes give q <= 4*beta(Q).  Check
    # every component-size case in the audited completion.  For an outside
    # graph R, beta(R)>=0,1,2 according as |R| is 0, 1--2, or at least 3.
    component_cases = []
    for r in range(0, 11):
        q = 41 - r
        beta_r_lower = 0 if r == 0 else (1 if r <= 2 else 2)
        beta_q_upper = 9 - beta_r_lower
        brooks_q_upper = 4 * beta_q_upper
        assert q > brooks_q_upper
        component_cases.append(
            {
                "outside_r": r,
                "core_q": q,
                "beta_R_lower": beta_r_lower,
                "beta_Q_upper": beta_q_upper,
                "brooks_core_order_upper": brooks_q_upper,
            }
        )

    # Order-40 core-degree table: 10b <= (10-r)(40-r), and b is even.
    table = []
    expected_even_max = {10: 0, 9: 2, 8: 6, 7: 8, 6: 12,
                         5: 16, 4: 20, 3: 24, 2: 30}
    for r in range(10, 1, -1):
        q = 40 - r
        bound = ((10 - r) * q) // 10
        bmax = even_floor(bound)
        assert bmax == expected_even_max[r]
        table.append({"outside_r": r, "core_q": q, "max_even_degree9_core": bmax})
    r = 1
    q = 40 - r
    bmax = even_floor((8 * q) // 9)
    assert bmax == 34
    table.append({"outside_r": r, "core_q": q, "max_even_degree9_core": bmax})
    table.append({"outside_r": 0, "core_q": 40, "max_even_degree9_core": 40})

    script_path = Path(__file__).resolve()
    result = {
        "status": "VERIFIED",
        "scope": (
            "Finite link properties and arithmetic only; completeness of "
            "Bikov's seven-link classification is citation-dependent."
        ),
        "links": link_rows,
        "unique_common_neighbor_lower_at_t10": unique_lower,
        "unique_common_neighbor_upper": 9,
        "order41_component_cases": component_cases,
        "order40_core_table": table,
        "script_sha256": hashlib.sha256(script_path.read_bytes()).hexdigest(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
