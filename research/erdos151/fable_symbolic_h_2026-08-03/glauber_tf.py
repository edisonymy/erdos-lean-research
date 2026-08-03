"""Heuristic occupancy calibration for triangle-free induced sets.

Measures a finite single-chain mean density on: the L(785,53)
anchor, a purified capped-process graph, and a synthetic locally-CBU
instance.  There is no mixing or error certificate.  Mean density alone
does not certify a fractional cover on a non-transitive graph; that requires
a uniform lower bound on every vertex marginal.
Insert move at v is legal iff S ∩ N(v) is edge-free (the local
triangle constraint).  Usage: python glauber_tf.py OUT.jsonl
"""
from __future__ import annotations

import json
import math
import random
import sys
import time

from er_race import build_capped_process
from tcg_check import purify
from anchor_pin import build_L785, tf_ok


def cbu_instance(rounds=6, copies=10, l=30, rng=None):
    """Synthetic locally-CBU-ish graph: `rounds` random partitions of
    [n] into `copies` tripartite copies of size l (n = copies*l), edges
    within copies only, cross-copy triangles removed by construction
    order (approximation: keep all; measure what we get)."""
    n = copies * l
    adj = [0] * n
    for _ in range(rounds):
        perm = list(range(n))
        rng.shuffle(perm)
        for c in range(copies):
            verts = perm[c * l:(c + 1) * l]
            t = l // 3
            parts = [verts[:t], verts[t:2 * t], verts[2 * t:]]
            for i in range(3):
                for j in range(i + 1, 3):
                    for u in parts[i]:
                        for v in parts[j]:
                            adj[u] |= 1 << v
                            adj[v] |= 1 << u
    # crude K4 cleanup: delete an edge from each K4 found (few expected)
    import itertools
    changed = True
    while changed:
        changed = False
        for u in range(n):
            c = adj[u]
            while c:
                v = (c & -c).bit_length() - 1
                c &= c - 1
                if v <= u:
                    continue
                common = adj[u] & adj[v]
                cc = common
                brk = False
                while cc:
                    w = (cc & -cc).bit_length() - 1
                    cc &= cc - 1
                    if adj[w] & common:
                        adj[u] &= ~(1 << v)
                        adj[v] &= ~(1 << u)
                        changed = True
                        brk = True
                        break
                if brk:
                    break
    return adj, n


def glauber(adj, n, lam, steps, rng):
    s = 0
    size = 0
    acc = 0
    samples = 0
    p_ins = lam / (1 + lam)
    for t in range(steps):
        v = rng.randrange(n)
        if (s >> v) & 1:
            if rng.random() > p_ins:
                s &= ~(1 << v)
                size -= 1
        else:
            if rng.random() < p_ins and tf_ok(adj, v, s):
                s |= 1 << v
                size += 1
        if t > steps // 3 and t % 50 == 0:
            acc += size
            samples += 1
    return acc / samples / n


def main():
    out = sys.argv[1]
    rng = random.Random(77)
    t0 = time.time()
    insts = []
    adjL, nL = build_L785()
    insts.append(("L785", adjL, nL))
    a, d, m = build_capped_process(800, 47, random.Random(1))
    insts.append(("proc800", purify(a, 800), 800))
    a, n = cbu_instance(rng=random.Random(9))
    insts.append(("cbu300", a, n))
    for name, adj, n in insts:
        D = max(bin(x).count("1") for x in adj)
        for lam in (0.5, 1.0, 2.0, 4.0, 8.0):
            dens = glauber(adj, n, lam, 400000, rng)
            rec = {"inst": name, "n": n, "Delta": D, "lambda": lam,
                   "finite_chain_mean_density": round(dens, 4),
                   "reciprocal_mean_density_diagnostic": round(1 / max(dens, 1e-9), 2),
                   "C_diagnostic": round(math.log(D) / D / max(dens, 1e-9), 3),
                   "certified_stationary": False,
                   "certified_fractional_cover": False,
                   "t": round(time.time() - t0, 1)}
            print(json.dumps(rec), flush=True)
            with open(out, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()
