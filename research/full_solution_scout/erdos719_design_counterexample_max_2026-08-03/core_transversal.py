#!/usr/bin/env python3
"""Classify three-tetrahedron packing cores and solve their transversal LP.

This is deliberately independent of the missing-edge CEGAR search.  A core is
three pairwise edge-disjoint tetrahedra.  If it is a maximum packing, every
tetrahedron edge-disjoint from the core must contain a missing triple.  The
script computes the minimum number of missing triples needed for that local
condition for every core isomorphism type.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from pysat.formula import WCNF
from pysat.examples.rc2 import RC2

V = tuple(range(9))
TRIPLES = tuple(itertools.combinations(V, 3))
TID = {e: i for i, e in enumerate(TRIPLES)}
BLOCKS = tuple(itertools.combinations(V, 4))


def edges(block: tuple[int, ...]) -> frozenset[int]:
    return frozenset(TID[e] for e in itertools.combinations(block, 3))


BEDGES = tuple(edges(b) for b in BLOCKS)


def compatible(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    return len(set(a) & set(b)) <= 2


def core_key(core: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    """Complete isomorphism invariant for three unlabeled subsets.

    Membership-pattern cell sizes classify a family of three labeled sets up
    to ground-set permutation.  Taking the minimum over S_3 removes the block
    labels.  The 000 cell is included so isolated vertices remain visible.
    """
    out = []
    for perm in itertools.permutations(range(3)):
        counts = []
        for pat in range(8):
            counts.append(
                sum(
                    all(((v in core[perm[j]]) == bool(pat & (1 << j))) for j in range(3))
                    for v in V
                )
            )
        out.append(tuple(counts))
    return min(out)


def representatives() -> dict[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    reps: dict[tuple[int, ...], tuple[tuple[int, ...], ...]] = {}
    for ids in itertools.combinations(range(len(BLOCKS)), 3):
        core = tuple(BLOCKS[i] for i in ids)
        if all(compatible(core[i], core[j]) for i, j in itertools.combinations(range(3), 2)):
            reps.setdefault(core_key(core), core)
    return reps


def min_local_transversal(core: tuple[tuple[int, ...], ...]) -> dict:
    union = frozenset().union(*(edges(b) for b in core))
    family = [
        (b, be)
        for b, be in zip(BLOCKS, BEDGES)
        if all(compatible(b, c) for c in core)
    ]
    # Compatible blocks are edge-disjoint from the core, so all clause
    # variables are automatically outside its 12 present triples.
    wcnf = WCNF()
    for _, be in family:
        assert be.isdisjoint(union)
        wcnf.append([e + 1 for e in sorted(be)])
    for e in range(len(TRIPLES)):
        if e not in union:
            wcnf.append([-(e + 1)], weight=1)
    # Core triples are forced present / not chosen as missing.
    for e in sorted(union):
        wcnf.append([-(e + 1)])
    with RC2(wcnf, solver="g4", adapt=True, exhaust=True, incr=False, verbose=0) as rc2:
        model = rc2.compute()
        assert model is not None
        chosen = sorted(e - 1 for e in model if 0 < e <= len(TRIPLES) and (e - 1) not in union)
        optimum = rc2.cost
    assert len(chosen) == optimum
    assert all(any(e in chosen for e in be) for _, be in family)
    return {
        "core": [list(b) for b in core],
        "core_key": list(core_key(core)),
        "compatible_blocks": len(family),
        "minimum_local_transversal": optimum,
        "one_transversal": [list(TRIPLES[e]) for e in chosen],
    }


def min_clean_blocks_at_twenty(core: tuple[tuple[int, ...], ...]) -> dict:
    """Minimize the total number of clean tetrahedra with exactly 20 misses.

    The local core-extension constraints are hard.  Each of the 126 clauses
    saying that a tetrahedron is dirty is soft with unit weight.  RC2's cost
    is therefore exactly the number of clean tetrahedra, not a proxy.
    """
    union = frozenset().union(*(edges(b) for b in core))
    local_family = [be for b, be in zip(BLOCKS, BEDGES) if all(compatible(b, c) for c in core)]
    # Binary variables are z_e (84 missing indicators), followed by c_B (126
    # clean-block indicators).  Minimization and c_B + sum_{e in B} z_e >= 1
    # make c_B exactly the cleanliness indicator at optimum.
    nz, nb = len(TRIPLES), len(BLOCKS)
    nvars = nz + nb
    rows: list[np.ndarray] = []
    lower: list[float] = []
    upper: list[float] = []
    row = np.zeros(nvars)
    row[:nz] = 1
    rows.append(row)
    lower.append(20)
    upper.append(20)
    for be in local_family:
        row = np.zeros(nvars)
        row[list(be)] = 1
        rows.append(row)
        lower.append(1)
        upper.append(np.inf)
    for bi, be in enumerate(BEDGES):
        row = np.zeros(nvars)
        row[list(be)] = 1
        row[nz + bi] = 1
        rows.append(row)
        lower.append(1)
        upper.append(np.inf)
    lb = np.zeros(nvars)
    ub = np.ones(nvars)
    ub[list(union)] = 0
    objective = np.zeros(nvars)
    objective[nz:] = 1
    result = milp(
        objective,
        integrality=np.ones(nvars),
        bounds=Bounds(lb, ub),
        constraints=LinearConstraint(np.asarray(rows), lower, upper),
        options={"mip_rel_gap": 0.0},
    )
    if result.x is None:
        return {"exact_twenty_feasible": False, "milp_status": int(result.status), "milp_message": result.message}
    assert result.status == 0, result.message
    chosen = sorted(e for e in range(nz) if result.x[e] > 0.5)
    cost = round(float(result.fun))
    assert len(chosen) == 20
    assert union.isdisjoint(chosen)
    clean = [i for i, be in enumerate(BEDGES) if be.isdisjoint(chosen)]
    assert len(clean) == cost
    assert all(any(e in chosen for e in be) for be in local_family)
    return {
        "exact_twenty_feasible": True,
        "minimum_clean_blocks": cost,
        "milp_status": int(result.status),
        "milp_gap": float(result.mip_gap),
        "milp_nodes": int(result.mip_node_count),
        "one_missing_set": [list(TRIPLES[e]) for e in chosen],
        "one_clean_family": [list(BLOCKS[i]) for i in clean],
    }


def run(output: Path) -> None:
    reps = representatives()
    rows = []
    for i, k in enumerate(sorted(reps), 1):
        row = min_local_transversal(reps[k])
        if row["minimum_local_transversal"] <= 20:
            row.update(min_clean_blocks_at_twenty(reps[k]))
        else:
            row["exact_twenty_feasible"] = False
        rows.append(row)
        print(f"type {i}/{len(reps)}: tau={row['minimum_local_transversal']}, qmin={row.get('minimum_clean_blocks')}", flush=True)
    payload = {
        "status": "COMPLETE_CORE_TYPE_ENUMERATION",
        "vertices": 9,
        "core_size": 3,
        "core_isomorphism_types": len(rows),
        "rows": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "types": len(rows),
        "minima_distribution": {
            str(x): sum(r["minimum_local_transversal"] == x for r in rows)
            for x in sorted({r["minimum_local_transversal"] for r in rows})
        },
        "max_minimum": max(r["minimum_local_transversal"] for r in rows),
        "clean_minima_distribution": {
            str(x): sum(r.get("minimum_clean_blocks") == x for r in rows)
            for x in sorted({r.get("minimum_clean_blocks") for r in rows if "minimum_clean_blocks" in r})
        },
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("core_transversal_results.json"))
    args = parser.parse_args()
    run(args.output)
