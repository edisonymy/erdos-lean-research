#!/usr/bin/env python3
"""The sigma=19 hunt: pure bipartite statics + C16/C32 kissat rounds.

Any model surviving C16 and C32 blocking is a full counterexample to
Erdős–Gyárfás (cycles <= 38, C4/C8 dead statically).  UNSAT with the
accumulated audited blocks extends the bipartite bound to both sides
>= 20.  Blocks persist in blocks_pure19.jsonl across restarts.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, ".")
import sat_search

KISSAT = "/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad/kissat/build/kissat"
DRAT = "/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad/drat-trim/drat-trim"
SIGMA = 19
BLOCKS = "blocks_pure19.jsonl"


def audit_cycle(cyc, sigma):
    L = len(cyc)
    assert L in (16, 32), L
    assert len(set(cyc)) == L
    for i in range(L):
        a, b = cyc[i], cyc[(i + 1) % L]
        assert (a < sigma) != (b < sigma)
    return True


def main(time_budget, cap=512):
    pool, X, U, M, cls = sat_search.build(SIGMA, verbose=False, symmetry=True)
    blocks = []
    if os.path.exists(BLOCKS):
        with open(BLOCKS) as f:
            for line in f:
                blocks.append(json.loads(line))
        print(f"resumed {len(blocks)} blocks", flush=True)
    bf = open(BLOCKS, "a")
    t0 = time.time()
    rnd = 0
    while True:
        rnd += 1
        if time.time() - t0 > time_budget:
            print(json.dumps({"status": "TIMEOUT", "rounds": rnd, "blocks": len(blocks)}), flush=True)
            return
        cnf = "pure19_cur.cnf"
        allc = cls + [b["clause"] for b in blocks]
        with open(cnf, "w") as f:
            f.write(f"p cnf {pool.top} {len(allc)}\n")
            for c in allc:
                f.write(" ".join(map(str, c)) + " 0\n")
        r = subprocess.run([KISSAT, "-q", cnf, "pure19_cur.drat"],
                           capture_output=True, text=True)
        if r.returncode == 20:
            v = subprocess.run([DRAT, cnf, "pure19_cur.drat"], capture_output=True, text=True)
            ok = "s VERIFIED" in v.stdout
            os.rename(cnf, "pure19_final.cnf")
            os.rename("pure19_cur.drat", "pure19_final.drat")
            print(json.dumps({"status": "UNSAT", "rounds": rnd, "blocks": len(blocks),
                              "drat_verified": ok, "seconds": round(time.time() - t0, 1)}), flush=True)
            return
        assert r.returncode == 10, r.returncode
        model = set()
        for line in r.stdout.splitlines():
            if line.startswith("v"):
                for tok in line.split()[1:]:
                    val = int(tok)
                    if val > 0:
                        model.add(val)
        lines = []
        for j in range(M):
            if U[j] in model:
                lines.append((j, frozenset(p for p in range(SIGMA) if X[(p, j)] in model)))
        n, adj, edges = sat_search.incidence_graph(SIGMA, lines)
        bad = []
        for L in (4, 8, 16, 32):
            if L > 2 * SIGMA:
                break
            cyc = []
            # reuse the batch collector from sat_search_linear-style search
            import sat_search_linear as sl
            cyc = sl.find_cycles_of_length(adj, n, L, cap=cap)
            if cyc:
                bad = [(L, c) for c in cyc]
                break
        if not bad:
            out = {"status": "CANDIDATE", "n": n,
                   "lines": [sorted(line) for _, line in lines], "edges": edges}
            fn = f"CANDIDATE_pure19_{int(time.time())}.json"
            with open(fn, "w") as f:
                json.dump(out, f, indent=1)
            print(json.dumps({"status": "CANDIDATE", "file": fn, "n": n}), flush=True)
            return
        L0 = bad[0][0]
        if L0 in (4, 8):
            print(json.dumps({"status": "STATIC_LEAK", "len": L0}), flush=True)
            return
        for _, cyc in bad:
            audit_cycle(cyc, SIGMA)
            lits = []
            for i in range(len(cyc)):
                a, b = cyc[i], cyc[(i + 1) % len(cyc)]
                p, lv = (a, b) if a < SIGMA else (b, a)
                j = lines[lv - SIGMA][0]
                lits.append(-X[(p, j)])
            rec = {"cycle": cyc, "clause": lits}
            blocks.append(rec)
            bf.write(json.dumps(rec) + "\n")
        bf.flush()
        print(f"round {rnd}: +{len(bad)} C{L0} blocks (total {len(blocks)}) t={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 3600)
