import json, subprocess, time, hashlib, sys
sys.path.insert(0, ".")
import sat_search
DRAT = "/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad/drat-trim/drat-trim"
KISSAT = "/tmp/claude-0/-home-user-erdos-lean-research/3d6d83c9-04a3-54c9-b9c5-5eace99795c5/scratchpad/kissat/build/kissat"
def sha(p):
    h = hashlib.sha256()
    with open(p,'rb') as f:
        for ch in iter(lambda: f.read(1<<20), b''): h.update(ch)
    return h.hexdigest()
for sigma in range(9, 16):
    t0 = time.time()
    pool, X, U, M, cls = sat_search.build(sigma, verbose=False, symmetry=False)
    cnf = f"pure_nosym_sigma{sigma}.cnf"; prf = f"pure_nosym_sigma{sigma}.drat"
    with open(cnf,'w') as f:
        f.write(f"p cnf {pool.top} {len(cls)}\n")
        for c in cls: f.write(" ".join(map(str,c))+" 0\n")
    r1 = subprocess.run([KISSAT,"-q",cnf,prf],capture_output=True,text=True)
    assert r1.returncode == 20, (sigma, r1.returncode)
    r2 = subprocess.run([DRAT,cnf,prf],capture_output=True,text=True)
    print(json.dumps({"sigma":sigma,"drat_verified":"s VERIFIED" in r2.stdout,
        "cnf_sha256":sha(cnf),"drat_sha256":sha(prf),"seconds":round(time.time()-t0,2)}), flush=True)
