"""Empirical chi_tf landscape on class-like graphs (Program Alpha A1/A4).

For purified capped-process K4-free pure-3 graphs at growing n, measure:
  - t_max (max triangles per vertex), e_link stats;
  - greedy triangle-free-partition class count k (multi-restart upper
    bound on chi_tf);
  - the empirical constant C_emp = k * ln(Delta) / Delta;
  - the A1 bound k_A1 = ceil(sqrt(3e*t_max)) + 1 for comparison.
C_emp persistently < 1/2 on class-like graphs is evidence for the A4
target; C_emp near 1 would warn the theorem is tight against us.
Usage: python chitf_landscape.py OUT.jsonl
"""
from __future__ import annotations

import json
import math
import random
import sys

from er_race import build_capped_process
from tcg_check import purify


def tri_stats(adj, n):
    tmax = 0
    for v in range(n):
        cnt = 0
        c = adj[v]
        nb = []
        while c:
            w = (c & -c).bit_length() - 1
            c &= c - 1
            nb.append(w)
        for i, a in enumerate(nb):
            for b in nb[i + 1:]:
                if (adj[a] >> b) & 1:
                    cnt += 1
        tmax = max(tmax, cnt)
    return tmax


def greedy_tf_partition(adj, n, rng, restarts):
    best = n
    order = list(range(n))
    for _ in range(restarts):
        rng.shuffle(order)
        classes = []   # list of bitmasks
        for v in order:
            placed = False
            cl_order = list(range(len(classes)))
            rng.shuffle(cl_order)
            for ci in cl_order:
                s = classes[ci]
                common = adj[v] & s
                ok = True
                c = common
                while c:
                    w = (c & -c).bit_length() - 1
                    c &= c - 1
                    if adj[w] & common:
                        ok = False
                        break
                if ok:
                    classes[ci] |= 1 << v
                    placed = True
                    break
            if not placed:
                classes.append(1 << v)
        best = min(best, len(classes))
    return best


def main():
    out = sys.argv[1]
    for n in (200, 400, 800, 1600):
        for seed in (1, 2):
            rng = random.Random(seed)
            cap = max(6, int(1.2 * n ** 0.55))
            adj, deg, m = build_capped_process(n, cap, rng)
            adj = purify(adj, n)
            deg = [bin(x).count("1") for x in adj]
            D = max(deg)
            if D < 3:
                continue
            tmax = tri_stats(adj, n)
            k = greedy_tf_partition(adj, n, rng, 12)
            rec = {"n": n, "seed": seed, "Delta": D,
                   "edges": sum(deg) // 2, "t_max": tmax,
                   "k_greedy": k,
                   "C_emp": round(k * math.log(D) / D, 3),
                   "k_A1": math.ceil(math.sqrt(3 * math.e * tmax)) + 1,
                   "beta_floor_from_k": math.ceil(n / k)}
            print(json.dumps(rec), flush=True)
            with open(out, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()
