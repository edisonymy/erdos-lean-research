"""Heuristic search for a valid L(785,53) triangle-free partition.

Every reported upper bound is checked before output.  A found large
triangle-free set is recorded only as a lower bound on alpha_tf; it does not
give a lower bound on chi_tf.
Usage: python anchor_pin.py OUT.json
"""
from __future__ import annotations

import json
import math
import random
import sys
import time


def build_L785():
    n = 785
    S = set()
    x = 1
    while True:
        x = (x * 53) % n
        S.add(x)
        S.add((n - x) % n)
        if x == 1:
            break
    S.discard(0)
    adj = [0] * n
    for d in S:
        for v in range(n):
            adj[v] |= 1 << ((v + d) % n)
    for v in range(n):
        adj[v] &= ~(1 << v)
    return adj, n


def tf_ok(adj, v, s):
    common = adj[v] & s
    c = common
    while c:
        w = (c & -c).bit_length() - 1
        c &= c - 1
        if adj[w] & common:
            return False
    return True


def greedy_partition(adj, n, rng):
    order = list(range(n))
    rng.shuffle(order)
    classes = []
    for v in order:
        idxs = list(range(len(classes)))
        rng.shuffle(idxs)
        for ci in idxs:
            if tf_ok(adj, v, classes[ci]):
                classes[ci] |= 1 << v
                break
        else:
            classes.append(1 << v)
    return classes


def try_eliminate(adj, n, classes, rng, iters):
    """Try to empty the smallest class by moving its vertices elsewhere
    (with random ejection repair)."""
    classes = sorted(classes, key=lambda s: bin(s).count("1"))
    small = classes[0]
    rest = classes[1:]
    pend = [v for v in range(n) if (small >> v) & 1]
    for _ in range(iters):
        if not pend:
            return rest, True
        v = pend.pop(rng.randrange(len(pend)))
        placed = False
        idxs = list(range(len(rest)))
        rng.shuffle(idxs)
        for ci in idxs:
            if tf_ok(adj, v, rest[ci]):
                rest[ci] |= 1 << v
                placed = True
                break
        if not placed:
            # A one-vertex ejection is legal only if it removes *every*
            # triangle created by inserting v.  The retired implementation
            # removed one arbitrary blocker and could leave other triangles.
            for ci in idxs:
                s = rest[ci]
                common = adj[v] & s
                blockers = []
                c = common
                while c:
                    w = (c & -c).bit_length() - 1
                    c &= c - 1
                    if adj[w] & common:
                        blockers.append(w)
                rng.shuffle(blockers)
                for w in blockers:
                    candidate = s & ~(1 << w)
                    if tf_ok(adj, v, candidate):
                        rest[ci] = candidate | (1 << v)
                        pend.append(w)
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                return rest, False
    return (rest, True) if not pend else (rest, False)


def triangle_count(adj, s):
    count = 0
    c = s
    while c:
        u = (c & -c).bit_length() - 1
        c &= c - 1
        nbrs = adj[u] & s
        d = nbrs
        while d:
            v = (d & -d).bit_length() - 1
            d &= d - 1
            if v <= u:
                continue
            count += (adj[v] & nbrs & ~((1 << (v + 1)) - 1)).bit_count()
    return count


def partition_valid(adj, n, classes):
    union = 0
    for s in classes:
        if union & s or triangle_count(adj, s):
            return False
        union |= s
    return union == (1 << n) - 1


def greedy_tf_set(adj, n, rng, restarts):
    best = 0
    order = list(range(n))
    for _ in range(restarts):
        rng.shuffle(order)
        s = 0
        cnt = 0
        for v in order:
            if tf_ok(adj, v, s):
                s |= 1 << v
                cnt += 1
        best = max(best, cnt)
    return best


def main():
    out = sys.argv[1]
    adj, n = build_L785()
    D = 156
    rng = random.Random(99)
    t0 = time.time()
    best_k = n + 1
    best_classes = None
    for r in range(60):
        classes = greedy_partition(adj, n, rng)
        # iterative elimination
        while True:
            res = try_eliminate(adj, n, classes, rng, 4000)
            if isinstance(res, tuple) and res[1] is True:
                classes = res[0]
            else:
                break
        k = len(classes)
        if not partition_valid(adj, n, classes):
            raise RuntimeError("internal error: invalid triangle-free partition")
        if k < best_k:
            best_k = k
            best_classes = list(classes)
            print(f"[restart {r}] k={k} C={k*math.log(D)/D:.3f} "
                  f"{time.time()-t0:.0f}s", flush=True)
    tf_lb = greedy_tf_set(adj, n, rng, 120)
    res = {"family": "L(785,53)", "n": n, "Delta": D,
           "chi_tf_upper": best_k,
           "partition_classes_hex": [hex(s) for s in best_classes],
           "partition_verified": partition_valid(adj, n, best_classes),
           "C_upper": round(best_k * math.log(D) / D, 3),
           "alpha_tf_lower": tf_lb,
           "chi_tf_lower": None,
           "chi_tf_lower_status": "not implied by alpha_tf_lower",
           "elapsed_s": round(time.time() - t0, 1)}
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    print(json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
