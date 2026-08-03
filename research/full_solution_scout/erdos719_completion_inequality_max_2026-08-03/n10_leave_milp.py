#!/usr/bin/env python3
"""Optimize the uncovered 4-set leave of 38 triples on ten vertices.

This is a hypothesis generator only: SciPy/HiGHS status is not treated as a
proof certificate.  The emitted construction is independently checkable.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


def main() -> None:
    triples = list(itertools.combinations(range(10), 3))
    quads = list(itertools.combinations(range(10), 4))
    tid = {e: i for i, e in enumerate(triples)}
    # x_e=1 for a missing triple; u_Q=1 when Q is uncovered by x.
    nv = len(triples) + len(quads)
    c = np.zeros(nv)
    c[len(triples):] = 1
    rows = 1 + len(quads)
    A = lil_matrix((rows, nv), dtype=float)
    lo = np.full(rows, -np.inf)
    hi = np.full(rows, np.inf)
    for i in range(len(triples)):
        A[0, i] = 1
    lo[0] = hi[0] = 38
    for qi, Q in enumerate(quads):
        row = 1 + qi
        # u_Q + sum_{e subset Q} x_e >= 1.
        for e in itertools.combinations(Q, 3):
            A[row, tid[e]] = 1
        A[row, len(triples) + qi] = 1
        lo[row] = 1
    res = milp(
        c,
        integrality=np.ones(nv),
        bounds=Bounds(np.zeros(nv), np.ones(nv)),
        constraints=LinearConstraint(A.tocsr(), lo, hi),
        options={"time_limit": 300, "mip_rel_gap": 0.0},
    )
    x = np.rint(res.x).astype(int) if res.x is not None else None
    payload = {
        "status": int(res.status),
        "message": res.message,
        "objective": float(res.fun) if res.fun is not None else None,
        "mip_gap": getattr(res, "mip_gap", None),
        "mip_node_count": getattr(res, "mip_node_count", None),
        "missing_triples": [list(triples[i]) for i in range(len(triples)) if x is not None and x[i]],
        "uncovered_quads": [list(quads[i]) for i in range(len(quads)) if x is not None and x[len(triples) + i]],
    }
    Path(__file__).with_name("n10_leave_milp_result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: payload[k] for k in ("status", "message", "objective", "mip_gap", "mip_node_count")}, sort_keys=True))


if __name__ == "__main__":
    main()
