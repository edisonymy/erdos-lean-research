"""Adversarial axiom-subset probe for the saturation-exchange lemma.

Encodes a labeled graph on S (r vertices) + X (n-r vertices) at a
Ramsey jump n = R(3,h), with a chosen SUBSET of the proved structural
axioms, and asks CaDiCaL for a model:

  A1   Delta <= r                       (cardinality, eager)
  A3   S admissible: every S-edge and S-triangle has an ambient
       extender; K4 inside S forbidden (omega<=4 regime, h=8)
  A4   every v in X has an anchor A ⊆ N(v)∩S, |A| in {1,2,3},
       with A ∪ {v} ambient-maximal   (selector auxiliaries + clauses)
  W    omega <= 4 globally             (lazy K5 blocking)
  A2   alpha <= r                      (lazy independent-(r+1) blocking)
  A1f  degree floor delta >= n - R(3,r) (cardinality, eager)

SAT at a stage = explicit abstract configuration witnessing that the
axioms so far do NOT force a contradiction (counterexample to that
counting-lemma candidate); the witness and its anchor statistics are
dumped.  UNSAT at a stage identifies which added condition carries the
contradiction.  h=8 only in this version: n=28, r=7.

Usage: python anchor_model.py STAGE OUT.json   (STAGE in 1,2,3)
"""

from __future__ import annotations

import itertools
import json
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195

N, R = 28, 7
S = list(range(7))
X = list(range(7, 28))
FLOOR = 5  # n - R(3,7) = 28 - 23


def build(stage):
    pool = IDPool()
    E = {}
    for i, j in itertools.combinations(range(N), 2):
        E[(i, j)] = pool.id(f"e{i}_{j}")
    def e(i, j):
        return E[(min(i, j), max(i, j))]
    cnf = []
    # A1 (+A1f at stage 3)
    for v in range(N):
        inc = [e(v, w) for w in range(N) if w != v]
        cnf += CardEnc.atmost(lits=inc, bound=R, vpool=pool,
                              encoding=EncType.seqcounter).clauses
        if stage >= 3:
            cnf += CardEnc.atleast(lits=inc, bound=FLOOR, vpool=pool,
                                   encoding=EncType.seqcounter).clauses
    # A3
    for a, b in itertools.combinations(S, 2):
        ors = []
        for w in range(N):
            if w in (a, b):
                continue
            y = pool.id(f"y{a}_{b}_{w}")
            cnf += [[-y, e(a, w)], [-y, e(b, w)]]
            ors.append(y)
        cnf.append([-e(a, b)] + ors)
    for a, b, c in itertools.combinations(S, 3):
        ors = []
        for w in range(N):
            if w in (a, b, c):
                continue
            z = pool.id(f"z{a}_{b}_{c}_{w}")
            cnf += [[-z, e(a, w)], [-z, e(b, w)], [-z, e(c, w)]]
            ors.append(z)
        cnf.append([-e(a, b), -e(a, c), -e(b, c)] + ors)
    for q in itertools.combinations(S, 4):
        cnf.append([-e(i, j) for i, j in itertools.combinations(q, 2)])
    # A4: anchors, direct encoding
    for v in X:
        ors = []
        for size in (1, 2, 3):
            for A in itertools.combinations(S, size):
                u = pool.id(f"anc{v}_{'_'.join(map(str, A))}")
                for a in A:
                    cnf.append([-u, e(v, a)])
                for a, b in itertools.combinations(A, 2):
                    cnf.append([-u, e(a, b)])
                for w in range(N):
                    if w == v or w in A:
                        continue
                    cnf.append([-u, -e(v, w)] +
                               [])
                    # u -> not (w adjacent to all of A ∪ {v})
                    cnf[-1] = [-u] + [-e(x, w) for x in A + (v,)]
                ors.append(u)
        cnf.append(ors)
    return cnf, pool, e


def independent_set_ge(adj, k):
    """Return an independent set of size k if one exists (simple BB)."""
    best = []

    def bb(P, cur):
        if len(best) >= k:
            return
        if len(cur) == k:
            best[:] = cur
            return
        if len(cur) + len(P) < k:
            return
        Pl = sorted(P, key=lambda x: len(adj[x] & P))
        v = Pl[0]
        bb(P - adj[v] - {v}, cur + [v])
        if not best:
            bb(P - {v}, cur)
    bb(set(range(N)), [])
    return best if len(best) >= k else None


def main():
    stage, outpath = int(sys.argv[1]), sys.argv[2]
    cnf, pool, e = build(stage)
    t0 = time.time()
    lazy_blocks = {"alpha": 0, "omega": 0}
    with Cadical195(bootstrap_with=cnf) as s:
        while True:
            if not s.solve():
                res = {"stage": stage, "result": "UNSAT",
                       "lazy_blocks": lazy_blocks,
                       "elapsed_s": round(time.time() - t0, 1)}
                break
            m = s.get_model()
            val = {(i, j): m[e(i, j) - 1] > 0
                   for i, j in itertools.combinations(range(N), 2)}
            adj = {v: set() for v in range(N)}
            for (i, j), b in val.items():
                if b:
                    adj[i].add(j)
                    adj[j].add(i)
            # lazy W: omega <= 4
            k5 = None
            for q in itertools.combinations(range(N), 5):
                if all(x in adj[y] for x, y in itertools.combinations(q, 2)):
                    k5 = q
                    break
            if k5:
                s.add_clause([-e(i, j)
                              for i, j in itertools.combinations(k5, 2)])
                lazy_blocks["omega"] += 1
                continue
            # lazy A2 at stage >= 2
            if stage >= 2:
                I = independent_set_ge(adj, R + 1)
                if I:
                    s.add_clause([e(i, j)
                                  for i, j in itertools.combinations(sorted(I), 2)])
                    lazy_blocks["alpha"] += 1
                    continue
            edges = sorted([list(p) for p, b in val.items() if b])
            cs = {v: len(adj[v] & set(S)) for v in X}
            res = {"stage": stage, "result": "SAT",
                   "lazy_blocks": lazy_blocks,
                   "elapsed_s": round(time.time() - t0, 1),
                   "edge_count": len(edges),
                   "c_distribution": {str(c): list(cs.values()).count(c)
                                      for c in sorted(set(cs.values()))},
                   "degrees_S": [len(adj[a]) for a in S],
                   "degrees_X_minmax": [min(len(adj[v]) for v in X),
                                        max(len(adj[v]) for v in X)],
                   "edges": edges}
            break
    json.dump(res, open(outpath, "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "edges"}))


if __name__ == "__main__":
    main()
