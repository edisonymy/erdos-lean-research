"""A1-plus calibration: empirical Moser-Tardos threshold for
triangle-free partitions at k = c*sqrt(t_max).

For each instance and each c, run MT resampling (recolor the 3 vertices
of a violated triangle) with a resample budget; record convergence.
The empirical critical c* calibrates the entropy-compression target
(A1 proves c* <= sqrt(3e) = 2.86; A1-plus stakes sqrt(2) = 1.41; the
truth may be lower).  Usage: python mt_threshold.py OUT.jsonl
"""
from __future__ import annotations

import json
import math
import random
import sys
import time

from er_race import build_capped_process
from tcg_check import purify
from chitf_landscape import tri_stats
from anchor_pin import build_L785


def mono_triangles(adj, n, color):
    bad = []
    for v in range(n):
        c = adj[v]
        while c:
            w = (c & -c).bit_length() - 1
            c &= c - 1
            if w <= v or color[w] != color[v]:
                continue
            common = adj[v] & adj[w]
            cc = common
            while cc:
                x = (cc & -cc).bit_length() - 1
                cc &= cc - 1
                if x > w and color[x] == color[v]:
                    bad.append((v, w, x))
    return bad


def mt_run(adj, n, k, rng, budget):
    color = [rng.randrange(k) for _ in range(n)]
    steps = 0
    while steps < budget:
        bad = mono_triangles(adj, n, color)
        if not bad:
            return steps
        for (v, w, x) in bad:
            if color[v] == color[w] == color[x]:
                color[v] = rng.randrange(k)
                color[w] = rng.randrange(k)
                color[x] = rng.randrange(k)
                steps += 1
                if steps >= budget:
                    break
    return None


def main():
    out = sys.argv[1]
    rng = random.Random(31)
    t0 = time.time()
    instances = []
    for n, seed in ((400, 1), (800, 1)):
        adj, deg, m = build_capped_process(n, max(6, int(1.2 * n ** .55)),
                                           random.Random(seed))
        adj = purify(adj, n)
        instances.append((f"proc{n}", adj, n))
    adjL, nL = build_L785()
    instances.append(("L785", adjL, nL))
    for name, adj, n in instances:
        tmax = tri_stats(adj, n)
        for c in (2.9, 2.0, 1.4, 1.0, 0.7, 0.5, 0.35, 0.25):
            k = max(2, math.ceil(c * math.sqrt(tmax)))
            res = mt_run(adj, n, k, rng, 300000)
            rec = {"inst": name, "n": n, "t_max": tmax, "c": c, "k": k,
                   "mt_resamples": res,
                   "converged": res is not None,
                   "t": round(time.time() - t0, 1)}
            print(json.dumps(rec), flush=True)
            with open(out, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
            # A budget failure is inconclusive and is not monotone evidence
            # about smaller c, so retain every pre-registered calibration.


if __name__ == "__main__":
    main()
