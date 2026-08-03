import sys, subprocess, time
sys.path.insert(0, ".")
import sat_search
KISSAT = "/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad/kissat/build/kissat"
for sigma in (18, 19):
    t0=time.time()
    pool, X, U, M, cls = sat_search.build(sigma, verbose=False, symmetry=True)
    cnf = f"pure_sigma{sigma}.cnf"
    with open(cnf,"w") as f:
        f.write(f"p cnf {pool.top} {len(cls)}\n")
        for c in cls: f.write(" ".join(map(str,c))+" 0\n")
    r = subprocess.run([KISSAT,"-q",cnf,f"pure_sigma{sigma}.drat"],capture_output=True,text=True,timeout=13000)
    print(f"sigma={sigma} exit {r.returncode} (10=SAT 20=UNSAT) {round(time.time()-t0,1)}s", flush=True)
    if r.returncode == 10:
        open(f"pure_sigma{sigma}.SATMODEL","w").write(r.stdout)
        break
