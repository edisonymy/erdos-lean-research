#!/usr/bin/env python3
"""Certified two-defect exclusion: kissat rounds + DRAT + block audit.

Round r solves statics + accumulated C16/C32 blocking clauses with
kissat.  SAT -> decode model, enumerate up to CAP cycles of the first
dyadic length present, append one blocking clause each (negation of the
cycle's incidence set), and re-solve from scratch.  UNSAT -> emit DRAT
for the final formula and verify with drat-trim.

The mathematical theorem then rests on: (i) the statics' faithfulness,
(ii) each blocking clause being justified by an explicit 16/32-cycle
pattern (audited here syntactically: consecutive incidences chain
point-line-point-... and close), and (iii) drat-trim.  Blocks are saved
with their cycles in blocks_twodefect_h{h}.json for independent audit.
"""
import json
import subprocess
import sys
import time

sys.path.insert(0, ".")
import sat_search_linear as sl

DRAT = "/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad/drat-trim/drat-trim"
KISSAT = "/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad/kissat/build/kissat"


def audit_block(h, cyc):
    """cyc = vertex list alternating points (<h) and lines (>=h), even length in {16,32}."""
    L = len(cyc)
    assert L in (16, 32), L
    assert len(set(cyc)) == L, "repeated vertex"
    for i in range(L):
        a, b = cyc[i], cyc[(i + 1) % L]
        assert (a < h) != (b < h), "must alternate point/line"
    return True


def run(h, cap=512, max_rounds=400, time_budget=None):
    pool, X, cls = sl.build(h, h, True, True, defect_pt=0, defect_ln=0)
    blocks = []
    t0 = time.time()
    rnd = 0
    while True:
        rnd += 1
        if time_budget and time.time() - t0 > time_budget:
            print(json.dumps({"h": h, "status": "TIMEOUT", "rounds": rnd,
                              "blocks": len(blocks)}), flush=True)
            return "TIMEOUT"
        cnf = f"td_h{h}_r{rnd}.cnf"
        allcls = cls + [b["clause"] for b in blocks]
        with open(cnf, "w") as f:
            f.write(f"p cnf {pool.top} {len(allcls)}\n")
            for c in allcls:
                f.write(" ".join(map(str, c)) + " 0\n")
        prf = f"td_h{h}_r{rnd}.drat"
        r = subprocess.run([KISSAT, "-q", cnf, prf], capture_output=True, text=True)
        if r.returncode == 20:
            v = subprocess.run([DRAT, cnf, prf], capture_output=True, text=True)
            ok = "s VERIFIED" in v.stdout
            with open(f"blocks_twodefect_h{h}.json", "w") as f:
                json.dump([{"cycle": b["cycle"], "clause": b["clause"]} for b in blocks], f)
            print(json.dumps({"h": h, "status": "UNSAT", "rounds": rnd,
                              "blocks": len(blocks), "drat_verified": ok,
                              "final_cnf": cnf, "final_drat": prf,
                              "seconds": round(time.time() - t0, 1)}), flush=True)
            return "UNSAT"
        assert r.returncode == 10, r.returncode
        # parse v-lines
        model = set()
        for line in r.stdout.splitlines():
            if line.startswith("v"):
                for tok in line.split()[1:]:
                    val = int(tok)
                    if val > 0:
                        model.add(val)
        lines = []
        for j in range(h):
            line = frozenset(p for p in range(h) if X[(p, j)] in model)
            lines.append(line)
        n, adj = sl.graph_of(h, lines)
        bad = []
        for L in (4, 8, 16, 32):
            if L > 2 * h:
                break
            cyc = sl.find_cycles_of_length(adj, n, L, cap=cap)
            if cyc:
                bad = [(L, c) for c in cyc]
                break
        if not bad:
            edges = [(p, h + i) for i, line in enumerate(lines) for p in line]
            fn = f"candidate_certtd_h{h}_{int(time.time())}.json"
            with open(fn, "w") as f:
                json.dump({"h": h, "n": n, "edges": edges,
                           "lines": [sorted(l) for l in lines]}, f, indent=1)
            print(json.dumps({"h": h, "status": "CANDIDATE", "file": fn}), flush=True)
            return "CANDIDATE"
        L0 = bad[0][0]
        if L0 in (4, 8):
            print(json.dumps({"h": h, "status": "STATIC_LEAK", "len": L0,
                              "cycle": bad[0][1]}), flush=True)
            return "STATIC_LEAK"
        for _, cyc in bad:
            audit_block(h, cyc)
            lits = []
            for i in range(len(cyc)):
                a, b = cyc[i], cyc[(i + 1) % len(cyc)]
                p, lv = (a, b) if a < h else (b, a)
                lits.append(-X[(p, lv - h)])
            blocks.append({"cycle": cyc, "clause": lits})
        print(f"h={h} round {rnd}: +{len(bad)} C{L0} blocks (total {len(blocks)})", flush=True)


if __name__ == "__main__":
    h = int(sys.argv[1])
    tb = float(sys.argv[2]) if len(sys.argv) > 2 else None
    run(h, time_budget=tb)
