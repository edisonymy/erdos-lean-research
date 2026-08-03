# Erdős #982: isosceles-pattern / oriented-distance lane

**Date:** 2026-08-03

**Disposition:** stopped at the predeclared kill gate
**Full solution or counterexample:** **none**

## Executive result

This lane attacked the first possible counterexample order, `n=10`: a strictly
convex decagon in which every vertex sees at most four distinct distances.
It used a global-distance edge-colouring CSP with exact convex-order
constraints, followed by a rank-two Euclidean-distance-matrix (EDM) screen,
and an orthogonal exact triangular-lattice candidate search.

No candidate, proof, or certified exhaustive exclusion was obtained.

The strongest sound computational snapshot is:

- a five-global-distance candidate has 13 possible cap-endpoint/global-extreme
  order cases after exact order-consistency pruning;
- a bounded five-second-per-case Boolean SAT sweep found a model in 3 cases
  and returned `UNKNOWN` in the other 10;
- it proved **zero** cases unsatisfiable;
- the three retained models all have four local colours at every vertex and
  pass an independent definition-level checker;
- their numerical rank-two EDM residuals are `0.116283`, `0.191612`, and
  `0.082973`, respectively—none is a near-realization, but these numbers are
  heuristic diagnostics, **not proofs of nonrealizability**;
- an exact triangular-lattice search ranked about 79,932 states from 11,912
  unique seeds and found best local-distance profile
  `(5,7,6,6,7,5,7,6,6,7)`, far from the required all-at-most-four profile.

The hard recommendation is to **kill this equality-pattern lane now**.  Do not
expand it to six or more global colours without a new principled geometric
separator.  #982 itself remains open and may be revisited only with a method
that couples SAT patterns directly to exact rank-two/convex realizability.

## 1. Statement and priority audit

Erdős #982 asks whether every set of `n` points forming the vertices of a
convex polygon has a vertex from which at least `floor(n/2)` distinct distances
occur.  The public database still marked it open on 2026-08-03:

- <https://www.erdosproblems.com/982>

The low-order locally-few-distance literature changes the starting order.
Nozaki--Shinohara, *On a generalization of distance sets*,
[arXiv:0906.0199v2, §4.5, Proposition 4.18](https://arxiv.org/pdf/0906.0199v2),
records that the maximum planar locally-three-distance set has eight points
and that the unique eight-point example is the nonconvex Fishburn `H8`
configuration.  Thus orders 8 and 9 cannot refute #982; order 10 is the first
possible target.

Erdős--Fishburn, *Maximum planar sets that determine k distances*,
[Discrete Mathematics 160 (1996), 115--125](https://doi.org/10.1016/0012-365X(95)00153-N),
determines the maximum size of a global four-distance planar set to be nine.
Consequently any ten-point counterexample has at least five global distances.
The present CSP studies the first global branch, exactly five distances.  It
does **not** cover counterexamples with six or more global distances.

Targeted searches located no classification of planar locally-four-distance
sets.  That is absence-of-evidence only, not a novelty or openness proof.

## 2. Exact necessary constraints

Label the decagon vertices `0,...,9` in cyclic order and colour each edge by
its global distance.  The production CNF enforces the following necessary
conditions.

1. **At most four local colours.** Every vertex is incident with at most four
   of the five global colours.  All five colours occur globally.
2. **One witness per chord side.** If `p` is an equal-distance witness for
   base `{a,b}`, then `p` lies on the perpendicular bisector of `ab`.  Strict
   convexity permits at most one such hull vertex on either cyclic arc between
   `a` and `b`.
3. **No monochromatic `K4`.** Four pairwise equidistant points do not exist in
   the Euclidean plane.
4. **Shortest graph noncrossing.** Two crossing chords cannot both be globally
   shortest: in their convex quadrilateral at least one side is shorter.
5. **Diameter graph is a convex thrackle.** Two vertex-disjoint diameter
   chords must cross; otherwise a diagonal of their convex quadrilateral is
   longer than one of them.
6. **A five-vertex cap.** The smallest-enclosing-circle decomposition splits a
   convex polygon into at most three caps meeting at endpoints.  Their total
   sizes are `n+3`, so for `n=10` some consecutive cap has at least five
   vertices.  Relabel it `0,1,2,3,4`.  Standard cap monotonicity gives

   ```text
   d(0,1)<d(0,2)<d(0,3)<d(0,4),
   d(4,3)<d(4,2)<d(4,1)<d(4,0).
   ```

   See Nivasch--Pach--Pinchasi--Zerbib,
   [*The number of distinct distances from a vertex of a convex polygon*](https://arxiv.org/abs/1207.1266),
   §2, for this cap framework.
7. **Global order consistency.** The two cap endpoint orders and the named
   shortest/longest colours must extend to one strict total order on the five
   squared lengths.  This exact check reduces 26 initially generated cases to
   13.

These conditions are necessary, not sufficient for Euclidean realization.

## 3. SAT scope and exact counts

### Lossless five-global-distance sweep

`q5_atmost4_case_sweep.json` is the final sound bounded sweep.  It uses:

```text
solver                         Glucose 4.2 through PySAT
Boolean variables              275
CNF clauses per case           23,698
order-consistent cases         13
wall limit per SAT call        5 seconds
models requested per case      1
```

Exact outcome:

```text
cases with one sampled SAT model       3
cases returning UNKNOWN               10
cases proved UNSAT                     0
raw retained models                    3
dihedral colour orbits                 3
```

`UNKNOWN` means the solver was interrupted at the stated wall limit.  It is
not evidence of satisfiability or unsatisfiability.  Cases labelled
`SAMPLE_CAP` yielded one model but were not searched for further models and
were not exhausted.  Therefore this run is **not** a q=5 exclusion.

All three sampled models happen to have exactly four incident colours at every
vertex.  This is an observed property of the sample, not an imposed condition
in the final sweep.

### Diagnostic exactly-four sub-branch

An earlier stricter diagnostic imposed exactly four local colours everywhere.
In one case it found 18 raw models, 13 dihedral colour orbits, before a
124.906-second time cap.  An independent Z3 implementation found one model;
its canonical orbit occurs among the Boolean SAT models.  This cross-check is
useful implementation evidence, but the exactly-four condition is not
lossless for the original problem and the run was not exhaustive.

The old `q5_cases_glucose_valid.json` stores another bounded survivor sample.
Its historical top-level string `"status": "EXHAUSTIVE"` is superseded and
must not be quoted: 11 solver calls returned `UNKNOWN`, and the per-case model
cap also prevented enumeration.  The authoritative status accounting is in
`q5_atmost4_case_sweep.json` and this report.

## 4. Rank-two EDM screen: numerical evidence only

For a retained five-colouring, assign squared lengths `s_0,...,s_4` and form
the complete squared-distance matrix `D(s)`.  A planar realization requires

```text
B(s) = -1/2 J D(s) J
```

to be positive semidefinite of rank at most two.  The screen parameterizes all
strict total length orders compatible with the cap orders, normalizes the
shortest squared length to one, and minimizes the squared norm of all Gram
eigenvalues below the largest two.

For the final three lossless-CSP survivors, the best normalized residuals were

```text
0.0829729963
0.1162832139
0.1916122205
```

For the 13 retained exactly-four diagnostic orbits, the best residual was
`0.0392774264`; the others ranged up to `0.301914759`.

None is a near-zero signal.  However, differential evolution and
least-squares do not certify a global positive lower bound.  No survivor is
proved nonrealizable, and no numerical result here may be cited as an
exclusion.

## 5. Exact triangular-lattice candidate search

`triangular_lattice_decagon_search.py` represents lattice points by axial
integer coordinates `(x,y)` with exact squared distance

```text
dx^2 + dx*dy + dy^2.
```

Orientation signs are exact integer determinants.  The bounded run used axial
box `[-10,10]^2`, 20,000 random samples, positive-definite quadratic sublevel
seeds of coefficient height at most 7, beam width 80, 40 generations, and
30,000 attempted mutations per generation.

It produced 9,530 quadratic seeds and 2,382 random seeds, 11,912 unique seeds
in total, and ranked approximately 79,932 states.  The best exact profile was

```text
(5,7,6,6,7,5,7,6,6,7),  maximum = 7.
```

The independent checker rederived every squared-distance set and every turn
determinant.  No candidate was found.  This is a heuristic search result, not
an exclusion of triangular-lattice decagons.

## 6. Independent verification

`independent_verify.py` imports none of the search modules.  From serialized
edge colours it independently checks:

- all five colours occur;
- every local colour count is at most four;
- both cap endpoint orders and a compatible strict global total order;
- one witness per cyclic side;
- absence of monochromatic `K4`;
- shortest-edge noncrossing and diameter-thrackle conditions;
- recorded edge counts.

It checked 13 diagnostic patterns, the precise one-model case audit, and all
three final lossless-CSP models.  It independently checked the exact lattice
best record.  `independent_verification.json` ends with `status: VERIFIED`.

This verifies the stated finite artifacts, not Euclidean realizability and not
the Erdős conjecture.

## 7. Kill decision

The lane meets its predeclared stopping condition:

- no exact or numerical near-candidate exists;
- the sound combinatorial q=5 relaxation still leaves ten of thirteen cases
  unresolved at the small SAT budget and has sampled satisfiable branches;
- numerical EDM screening supplies no proof-producing separator;
- q>=6 would strictly expand the colour-pattern space;
- the exact lattice candidate family remains far from the target.

**Recommendation:** stop allocating agents or generic compute to this lane.
Continue #982 only after acquiring one of:

1. an exact rank-two/PSD separator integrated into constraint generation;
2. a theorem forcing any `n=10` counterexample into the q=5 branch and a
   certificate-producing exhaustive solver for that branch; or
3. a concrete equality pattern with a genuinely near-zero, positive-convexity
   realization that can be reconstructed algebraically.

Otherwise redeploy to another Erdős target.  This recommendation kills the
method, not the open problem.

## 8. Reproduction

From the repository root:

```powershell
.\.venv\Scripts\python.exe -B research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\enumerate_q5_patterns_sat.py --max-models 100 --per-case 1 --conflict-budget -1 --wall-seconds-per-solve 5 --seconds 120 --retain 100 --solver glucose42 --out research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\q5_atmost4_case_sweep.json
.\.venv\Scripts\python.exe -B research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\realize_q5_patterns.py research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\q5_atmost4_case_sweep.json --limit 100 --seeds 10 --maxiter 2000 --out research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\q5_atmost4_edm_screen.json
.\.venv\Scripts\python.exe -B research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\triangular_lattice_decagon_search.py --bound 10 --random-attempts 20000 --coefficient-bound 7 --beam 80 --generations 40 --mutations 30000 --seconds 150 --out research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\triangular_lattice_n10.json
.\.venv\Scripts\python.exe -B research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\independent_verify.py --patterns research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\q5_sat_smoke.json research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\q5_case_audit.json research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\q5_atmost4_case_sweep.json --lattice research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\triangular_lattice_n10.json --out research\full_solution_scout\erdos982_isosceles_pattern_max_2026-08-03\independent_verification.json
```

No git operation, issue update, or public claim was made from this lane.
