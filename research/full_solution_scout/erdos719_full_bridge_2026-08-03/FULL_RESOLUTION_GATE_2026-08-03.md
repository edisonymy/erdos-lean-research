# Full-resolution gate: Erdős #719

**Cutoff:** 3 August 2026, 04:02 BST.

## Decision

This lane did **not** produce a full counterexample, a proof of the universal
conjecture, or a quantitatively one-step near-witness.  Under the campaign's
strict full-resolution gate, the recommendation is therefore to **pivot
compute and research attention away from #719**.  The already certified
`r=3,n=9` result remains worth publishing as a finite theorem, but another
finite positive window is not the campaign objective.

Renew this lane only on one of the following triggers:

1. an independently checked `n=10,m=82,nu=2` candidate (or another full
   counterexample window);
2. a proof of the realizable completion inequality isolated below; or
3. a new structural lemma that provably removes the one-edge-per-core gap.

No public-result claim follows from this note.

## Proved all-parameter reductions

The complete proofs are in `COMPLEMENT_BRIDGE.md`; the conclusions were
audited again at this cutoff.

### Exact complement-cover bridge

Put `s=n-r`.  Complementing the `r`-edges of `G` gives an `s`-graph whose
missing sets are `H`, with `h=|H|`.  A present simplex corresponds exactly to
an uncovered `(s-1)`-set.  Two such simplices are edge-disjoint exactly when
the corresponding `(s-1)`-sets intersect in at most `s-3` points.  If
`rho(U(H))` is the largest subfamily with those pairwise intersections, #719
is precisely

```text
h + (n-s) rho(U(H)) >= C(n,s,s-1).
```

Here `C(n,s,s-1)` is the covering number.  Consequently the following
realizable-family completion inequality would settle #719 in full:

```text
tau_s(U(H)) <= (n-s) rho(U(H)).
```

It remains conjectural.  The restriction `U=U(H)` is essential; no claim is
made for arbitrary set families.

### Packing number zero or one

The conjecture holds whenever `nu(G)<=1`.  For `nu=1`, the vertex sets of all
present simplices are pairwise `r`-intersecting `(r+1)`-sets.  Such a family
either has a common `r`-set or lies in one fixed `(r+2)`-set.  In the first
case one edge hits every simplex.  In the second, an edge cover on the omitted
pairs uses at most `ceil((r+2)/2)<=r` hyperedges.  Deleting the hitting edges
makes the graph simplex-free.

Deleting all but one member of a maximum `k`-packing then gives

```text
|G| <= ex_r(n,K_{r+1}^r) + (r+1)k - 1.
```

A counterexample needs `|G| >= ex + rk + 1`; the exact universal barrier is
therefore a saving of one more edge for each packing core.

## Smallest counterexample target

The primary-source and priority audit is in `PRIORITY_AND_TARGET_AUDIT.md`.
The live database still marked #719 open on 3 August 2026, but database status
is not a substitute for a renewed literature and expert priority check before
any announcement.

For `r=3,n=10`, the published exact covering value `T(10,4,3)=45` gives

```text
ex_3(10,K4^3) = 120-45 = 75.
```

Thus an 82-edge graph with packing number two would have decomposition number
`82-3*2=76>75` and would disprove #719 outright.  Equivalently, in the
complement it needs exactly 38 missing triples and no three edge-disjoint
clean tetrahedra, while retaining two.

## Proved obstruction to perturbing the standard extremal construction

Take parts of sizes `(3,3,4)` and the standard 75-edge construction with edge
types `ABC`, `AAB`, `BBC`, and `CCA`.  Direct exhaustive counting shows:

* it has 45 missing triples;
* 35 missing triples are the unique missing edge of three tetrahedra each;
* the other 10 are the unique missing edge of four tetrahedra each; and
* the tetrahedra by original number of missing edges have distribution
  `{1:145, 2:45, 4:20}`.

Therefore adding any `t` missing triples creates at least `3t` distinct clean
tetrahedra.  If the resulting graph were a counterexample with packing number
`k`, then `t>=3k+1`.  A Steiner quadruple system on ten points exists; random
relabeling gives `q<=7k` for the total number `q` of clean tetrahedra.  But

```text
q >= 3t >= 9k+3 > 7k.
```

Hence **no counterexample at `n=10` can be obtained by adding edges to this
standard extremal graph**, in any excess window.  This is a family
obstruction, not a proof for arbitrary 3-graphs.

The deterministic audit is `audit_n10_families.py`.

## Exact obstruction to a restricted two-star ansatz

Another deliberately structured ansatz prescribes the clean tetrahedra to be
exactly the union of the two stars containing either of two fixed triples.
The three center-intersection types are exhaustive for this ansatz only:

| center intersection | intended clean blocks | forced-present triples | result |
|---:|---:|---:|---|
| 0 | 14 | 44 | 9 unintended blocks are already forced clean |
| 1 | 14 | 40 | 1 unintended block is already forced clean |
| 2 | 13 | 34 | exact realization needs at least 48 missing triples |

The last optimum is an exact binary hitting-set solve.  Since the 82-edge
target has only 38 missing triples, all three structured types fail.  This
does **not** exhaust arbitrary packing-number-two graphs.

## Computational evidence, with claim boundaries

### Heuristic search

Three independent 120-second annealing runs at exactly 38 missing triples
all reached the necessary clean-block count `q=14`, but still had respectively
232, 216, and 216 forbidden three-packings.  Their JSON records are under
`anneal/`.  These are not close to a one-step repair: the number of packing
violations remains in the hundreds.

A separate 60-second HiGHS relaxation/search found an incumbent with `q=14`,
but did not prove optimality (reported relative gap `0.7857`); its clean-block
packing number was eight.  It is search telemetry only and is not used in any
theorem.

### Core-fixed CEGAR

`search_n10_exact82.py` fixes a clean two-tetrahedron core.  The three runs for
core vertex-intersection `0,1,2` cover the isomorphism types of an
edge-disjoint pair.  Static clauses require exactly 38 missing triples, keep
the core present, and make every tetrahedron compatible with both core blocks
dirty.  A definition-level separator then blocks arbitrary three-packings.

The final capped probes used Glucose4, batches of 256 packing cuts, a nominal
per-solve conflict budget of 1,000,000, and a 300-second wall-clock parameter.
Because the solver call did not return control to the Python wall-clock check,
the three tasks were manually terminated after about seven minutes without a
first model or a completed `summary.json`.  One child worker survived the
cell shutdown and was explicitly stopped by PID.  The only sound status is:

```text
TERMINATED_UNKNOWN — no candidate, no UNSAT certificate, no exhaustion claim.
```

The absence of a first model indicates substantial static SAT pressure but is
not mathematical evidence of nonexistence.

If a future run emits `candidate.json`, `verify_n10_exact82.py` independently
checks all 82 triples and exhaustively checks packing number exactly two before
the published Turán value is invoked.

## Reproducibility

Run the deterministic structured-family audit with the repository virtual
environment:

```powershell
& .\.venv\Scripts\python.exe research/full_solution_scout/erdos719_full_bridge_2026-08-03/audit_n10_families.py
```

All four Python files pass `py_compile`.  SHA-256 at the cutoff:

```text
3B9967DAEEEF0E2CE82A2B52E95AF13FE88C81E47241D887FA90E082916C2776  anneal_n10_exact82.py
6F6BC2C8816B099E88EA03B0B2EADE6E0B2278FDE26D8BF9B0EBC7D71E35604B  audit_n10_families.py
F80ED4EF5D1940A2B26346B12525C3EA66D677B758F5B72CC3001F40EEF09552  search_n10_exact82.py
E6B21B0993A289DFCEEBF40F3F651D486C4B0444D48B3C31DE1D6F03BE0E208A  verify_n10_exact82.py
```

## Resource-allocation conclusion

The strongest new insight is conceptual: #719 is a realizable covering
completion problem with a precise one-edge-per-core deficit.  The smallest
counterexample window is crisp, but the tested natural families are excluded
and unconstrained `q=14` configurations still have packing number far above
two.  The exact SAT formulation also failed to yield a first model cheaply.

That combination is momentum, but not near-solution momentum.  Continuing by
adding compute or proving another finite positive case has lower expected
one-week value than reallocating to a lane with a live candidate, a sharp
near-contradiction, or a tractable global lemma.
