#!/usr/bin/env python3
"""Independent cross-check of Theorem 1 by orderly backtracking (no SAT).

Enumerates linear hypergraphs on sigma points, lines as sorted tuples of
size >= 3 added in nondecreasing lexicographic order, maintaining:
  - linearity (each point-pair covered <= 1 time);
  - quadrilateral-freeness (checked incrementally: adding line L, for
    every pair of "outside bridges" ... implemented directly: after
    adding L, verify no incidence C8 exists through L via explicit
    search on the current incidence graph);
  - completability pruning: every point still needing degree must have
    enough remaining pair budget; a point with degree deficit d needs d
    more lines through it, consuming >= 2d pairs at that point (each
    line through p uses >= 2 pairs at p); prune when the point's
    remaining partner supply is insufficient.
Terminates with the number of maximal states reached and whether any
complete (all degrees >= 3) configuration exists.  Shares no code with
sat_search*.py (checker-grade reimplementation).
"""
import sys
import time
from itertools import combinations


def solve(sigma, deadline):
    pairs_used = set()
    lines = []
    deg = [0] * sigma
    found = []
    nodes = [0]

    all_lines = []
    for s in range(3, sigma + 1):
        for comb in combinations(range(sigma), s):
            all_lines.append(comb)
    all_lines.sort()

    # incidence adjacency for quad check: point -> set(line idx), line idx -> tuple
    def creates_quad(newline):
        # C8 through newline: p1 in newline, line A (!=new) with p1, p2 in A,
        # p2 != p1, line B with p2, p3 in B, p3 in ... close via newline: need
        # p1, p4 both in newline with a 3-line path p1 -A- p2 -B- p3 -C- p4,
        # lines A,B,C distinct, != newline, points distinct.
        nl = set(newline)
        for p1 in newline:
            # BFS over alternating structure up to 3 line-steps
            for ai, A in enumerate(lines):
                if p1 not in A:
                    continue
                for p2 in A:
                    if p2 == p1 or p2 in nl:
                        continue
                    for bi, B in enumerate(lines):
                        if bi == ai or p2 not in B:
                            continue
                        for p3 in B:
                            if p3 in (p1, p2) or p3 in nl:
                                continue
                            for ci, C in enumerate(lines):
                                if ci in (ai, bi) or p3 not in C:
                                    continue
                                for p4 in C:
                                    if p4 in (p1, p2, p3):
                                        continue
                                    if p4 in nl:
                                        return True
        return False

    def prune_infeasible():
        # every point p with deficit needs lines; each new line through p
        # pairs p with >= 2 previously-unpaired-with-p points
        for p in range(sigma):
            need = 3 - deg[p]
            if need <= 0:
                continue
            partners = sum(1 for q in range(sigma)
                           if q != p and (min(p, q), max(p, q)) not in pairs_used)
            if partners < 2 * need:
                return True
        return False

    def rec(start_idx):
        if deadline and time.time() > deadline:
            raise TimeoutError
        nodes[0] += 1
        if all(d >= 3 for d in deg):
            found.append([list(l) for l in lines])
            return True
        if prune_infeasible():
            return False
        for idx in range(start_idx, len(all_lines)):
            L = all_lines[idx]
            ps = list(combinations(L, 2))
            if any(pr in pairs_used for pr in ps):
                continue
            if creates_quad(L):
                continue
            lines.append(L)
            for pr in ps:
                pairs_used.add(pr)
            for p in L:
                deg[p] += 1
            if rec(idx + 1):
                return True
            lines.pop()
            for pr in ps:
                pairs_used.discard(pr)
            for p in L:
                deg[p] -= 1
        return False

    try:
        ok = rec(0)
        return ("SAT" if ok else "UNSAT"), nodes[0], found
    except TimeoutError:
        return "TIMEOUT", nodes[0], found


if __name__ == "__main__":
    sigma = int(sys.argv[1])
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    t0 = time.time()
    status, nodes, found = solve(sigma, time.time() + budget)
    print({"sigma": sigma, "status": status, "nodes": nodes,
           "seconds": round(time.time() - t0, 1)})
