#!/usr/bin/env python3
"""DRAT-certified replay of the pure-bipartite small-side UNSATs.

For each sigma, rebuild the static formula of sat_search.py (linearity,
quadrilateral clauses, degree/size cards, symmetry breaking), emit DIMACS,
solve with proof logging, and verify the DRAT proof with drat-trim.

The static formula does NOT include any C16 constraint, so UNSAT proves
the stronger statement: no linear hypergraph on sigma points with line
sizes >= 3 and point degrees >= 3 has a quadrilateral-free incidence
graph.  Equivalently: every bipartite graph with minimum degree >= 3,
no C4 and no C8 has both sides of size >= sigma+1.
"""
import hashlib
import json
import subprocess
import sys
import time

from pysat.solvers import Cadical195

sys.path.insert(0, ".")
import sat_search  # noqa: E402

DRAT = "/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad/drat-trim/drat-trim"
KISSAT = "/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad/kissat/build/kissat"


def write_dimacs(path, nvars, clauses):
    with open(path, "w") as f:
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(sigmas):
    results = []
    for sigma in sigmas:
        t0 = time.time()
        M_cap = (sigma * (sigma - 1) // 2) // 3
        if M_cap < 3:
            rec = {"sigma": sigma, "M": M_cap, "status": "HAND_UNSAT",
                   "reason": "every point needs >=3 distinct lines but the "
                             "linearity pair budget allows at most M<3 lines"}
            print(json.dumps(rec), flush=True)
            results.append(rec)
            continue
        pool, X, U, M, cls = sat_search.build(sigma, exact3=False, verbose=False)
        cnf_path = f"pure_sigma{sigma}.cnf"
        proof_path = f"pure_sigma{sigma}.drat"
        write_dimacs(cnf_path, pool.top, cls)
        r1 = subprocess.run([KISSAT, "-q", cnf_path, proof_path],
                            capture_output=True, text=True)
        assert r1.returncode == 20, f"sigma={sigma}: kissat exit {r1.returncode}"
        r = subprocess.run([DRAT, cnf_path, proof_path], capture_output=True, text=True)
        verified = "s VERIFIED" in r.stdout
        rec = {
            "sigma": sigma, "M": M, "nvars": pool.top, "nclauses": len(cls),
            "solver": "kissat-4.0.4", "sat": False,
            "drat_verified": verified,
            "cnf_sha256": sha(cnf_path), "drat_sha256": sha(proof_path),
            "seconds": round(time.time() - t0, 2),
        }
        print(json.dumps(rec), flush=True)
        if not verified:
            print(r.stdout[-2000:])
        results.append(rec)
    with open("certify_pure_results.json", "w") as f:
        json.dump(results, f, indent=1)


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or list(range(4, 16)))
