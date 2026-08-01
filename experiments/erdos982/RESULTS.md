# Erdős problem 982: exact noncyclic search

## Outcome

No counterexample was found.  This package is not a solution of problem 982.
It records five genuinely noncocircular or audit results:

1. an exhaustive exact exclusion for integer convex octagons through
   coordinate span 7;
2. an infinite rational noncyclic family attaining the conjectured bound at
   `n=8`;
3. a theorem ruling out every strictly convex polygon made from two
   alternating concentric regular `m`-gons, for every `m>=3`;
4. a proof ruling out a four-parameter real `D2`-symmetric octagon family,
   backed by an independently replayed exact height-1000 search; and
5. a deterministic exact lattice heuristic at uncollided sizes
   `n=8,9,11,13,14`, checked by a separate implementation.

The conjecture asks whether every convex `n`-gon has a vertex determining at
least `floor(n/2)` distinct distances.  The scripts compare integer squared
distances, so no numerical tolerance is involved.

## Why no cyclic experiment is retained

If all vertices lie on one circle, each distance class from a fixed vertex is
the intersection of that circumcircle with a second circle, hence has size at
most two.  Every cyclic polygon therefore has at least

```text
ceil((n-1)/2) = floor(n/2)
```

distinct distances at every vertex.  Cocircular configurations are rejected
algebraically throughout this package.

## Public-status and benchmark audit

`PROVENANCE_AUDIT_2026-08-01.md` records the live audit.  The Erdős Problems
entry and SciNet still show the problem open, with no published investigation
or verification event on SciNet.

The public SkyDiscover repository already contains floating-point benchmarks
for arbitrary convex configurations at `n=10` and `n=12`.  Its performance
notes tabulate the regular-polygon baseline and no better construction for the
`n=10` benchmark; no public run table for the `n=12` #982 benchmark was found
at the pinned commit.  However, both evaluators are scale-dependent: each
evaluator's own `verify_solution` accepts tiny scaled regular polygons with
reported metric `1`, although their exact metrics are `5` and `6`.  The cause
is an absolute tolerance floor in the distance comparison combined with
absolute convexity and coincidence thresholds.
`audit_skydiscover_scale_bug.py` reproduces the
false positive against pinned commit `aac2e79...`; this is a benchmark bug,
not a counterexample.  The heuristic here therefore omits `n=10,12` and uses
exact integer arithmetic at other sizes.

Scott Duke Kominers's 25 July 2026 unverified proof-claim preprint claims the
asymptotic lower bound

```text
(13/36 + 3/5270)n - O(1),
```

improving the previous additive coefficient beyond `13/36`, but it does not
reach the conjectured coefficient `1/2`.  No independent verification,
acceptance, correction, or refutation was found through 1 August.  The PDF
mentions an ancillary certificate script but supplies no public link to it.
The exact PDF bytes audited here have SHA-256
`519c31d5cd1e2443c4528ab665774945e16b173a00f6d6f0589296ffbbf97b2b`;
the source URL is unversioned and may change after this audit.

Sources:

- <https://www.erdosproblems.com/982>
- <https://www.scottkom.com/assets/articles/Kominers_Distinct_Distances_from_a_Vertex.pdf>
- <https://github.com/Open-Galapagos/evolution-fine-tuning/tree/aac2e79be773715ab35b7945f5d9028e46675f02/skydiscover/benchmarks/math/erdos_982_convex_distances>
- <https://github.com/Open-Galapagos/evolution-fine-tuning/tree/aac2e79be773715ab35b7945f5d9028e46675f02/skydiscover/benchmarks/math/erdos_982_convex_n12>
- <https://api.scinet.pub/p/cb372728-ee94-4530-a57b-2c2725158d8b>

## Exhaustive integer-octagon exclusion

`lattice8_exhaustive` enumerates all 8-subsets after the following lossless
normalization: translate so `min x=min y=0`, interchange the coordinate axes
so the x-span is at least the y-span, and enumerate each exact x-span from 2
through 7.  It uses exact cross products for the strict hull, an integer
incircle determinant to discard cyclic sets, and integer squared distances.

The completed run considered **1,517,270,144** normalized subsets.  Of these,
**3,056,752** were strictly convex and **3,056,334** were noncocircular.  No
polygon had maximum distinct-distance count below the threshold 4.

| exact larger span | normalized subsets | strict convex | noncocircular | best maximum | margin |
|---:|---:|---:|---:|---:|---:|
| 2 | 9 | 0 | 0 | — | — |
| 3 | 11,404 | 1 | 0 | — | — |
| 4 | 735,345 | 294 | 293 | 6 | +2 |
| 5 | 15,474,216 | 14,386 | 14,384 | 6 | +2 |
| 6 | 175,091,086 | 268,902 | 268,896 | 4 | 0 |
| 7 | 1,325,958,084 | 2,773,169 | 2,772,761 | 5 | +1 |

The unique normalized margin-zero polygon at span 6 is

```text
(0,3),(1,1),(3,0),(5,1),(6,3),(5,5),(3,6),(1,5).
```

The independent Python checker verifies strict convexity, noncocircularity,
and distance profile `(4,4,4,4,4,4,4,4)` using different predicates.  The raw
enumeration and checker records are `lattice8_span7.json` and
`lattice8_span7_verified.json`.  A second Python program independently
reenumerates spans 2–4 by exact angular sorting about the centroid; it matches
all normalized counts, convex/noncocircular counts, and objective histograms.

## Infinite exact equality family

The span-6 witness is the smallest integer member of

```text
(+/-a,0), (0,+/-a), (+/-b,+/-b),    b < a < 2b.
```

For rational `a,b`, this is strictly convex, never cocircular, and every
vertex determines exactly four distances.  `D4_OCTAGON_FAMILY.md` gives the
complete distance calculation.  The same calculation shows the maximum is
four even at the two exceptional irrational ratios where one vertex type has
a distance collision.  Thus this family reaches, but cannot cross, the target.

## All-order exclusion for alternating two-radius polygons

`TWO_RADIUS_DIHEDRAL_NO_GO.md` proves that the natural all-order extension of
the `D4` equality family cannot cross the bound.  For `theta=pi/m`, take

```text
A_j = r (cos(2j theta), sin(2j theta)),
B_j =     (cos((2j+1) theta), sin((2j+1) theta)).
```

Strict convexity is equivalent to `cos(theta)<r<sec(theta)`.  Exact
interlacing of the within-orbit and cross-orbit squared distances gives an
outer vertex with at least `m` distances, except at one possible ratio when
`m` is odd; at that ratio the inner vertex has `m` distances.  Thus no such
`2m`-gon refutes #982.  The proof covers arbitrary real radii.
`verify_dihedral_algebra.py` checks the symbolic identities used in the sign
argument.

## Exact `D2`-symmetric octagon theorem and search audit

The family

```text
(+/-a,0), (0,+/-c), (+/-b,+/-d)
```

strictly generalizes the `D4` octagons by allowing unequal horizontal and
vertical axis radii and unequal diagonal coordinates.  After an axis swap
and rescaling, take real parameters `a=1>=c`; strict convexity is exactly

```text
1>b, c>d, d+bc>c.
```

`D2_OCTAGON_NO_GO.md` gives a short exact proof over arbitrary real
parameters.  If `(1,0)` has at most three distances, its only possible
distance collision forces `(1+b)^2+d^2=4`.  Five distances from `(b,d)`,
after division by four, then include

```text
b^2, 3-2b-b^2, 3-2b, 1-b, 1,
```

which contain at least four distinct values for `0<b<1`.  Thus either an
axial or a diagonal vertex reaches the target.  `verify_d2_algebra.py` checks
the substitutions.

As a separate stress test, any rational member can be scaled to positive
integer parameters.  The optimized exact search exhausts parameter height
`max(a,b,c,d)<=1000`; its collision reduction is complete over the integers.

The completed run considered **333,333,000** normalized `(a,b,c)` triples,
**557,329** square candidates, and **107,825** strictly convex candidates.
There were zero cases in which both axial vertex orbits had at most three
distances, hence zero counterexamples.  A separate Node implementation
replayed the full height-1000 reduction and matched every count and the best
record.  A third Python implementation brute-forced every normalized tuple
through height 40 and matched the optimized search there.

The theorem is an exclusion only for the displayed symmetry family.  It is
not a finite-order proof for arbitrary octagons.

## Exact heuristic outside the collided sizes

`noncyclic_exact_search.py` seeds a beam with hulls of bounded-lattice samples
and with bounded-lattice intersections of positive-definite quadratic
sublevel sets, then
applies one- and two-vertex integer mutations.  Every accepted polygon is
strictly convex and noncocircular by exact tests.

The retained deterministic run used `[-8,8]^2`, primitive quadratic
coefficients at most 6, 15,000 random samples, 48 beam states, 30 generations,
and 12,000 mutations per generation.  It formed 8,527 unique seed polygons.

| n | best maximum | `floor(n/2)` | margin |
|---:|---:|---:|---:|
| 8 | 4 | 4 | 0 |
| 9 | 7 | 4 | +3 |
| 11 | 9 | 5 | +4 |
| 13 | 11 | 6 | +5 |
| 14 | 12 | 7 | +5 |

These heuristic rows are search diagnostics, not finite exclusions.  The weak
odd-order margins indicate that blind coordinate mutation destroys useful
distance equalities; the structured/exhaustive `n=8` result is the meaningful
outcome.

## Reproduce

From the workspace root:

```powershell
dotnet run --project experiments/erdos982/lattice8_exhaustive/Lattice8Exhaustive.csproj -c Release -- --max-side 7 --threads 16 --output experiments/erdos982/lattice8_span7.json
python experiments/erdos982/independent_verify_noncyclic.py experiments/erdos982/lattice8_span7.json --output experiments/erdos982/lattice8_span7_verified.json
python experiments/erdos982/independent_small_span_audit.py experiments/erdos982/lattice8_span7.json --max-side 4
python experiments/erdos982/noncyclic_exact_search.py --targets 8 9 11 13 14 --box 8 --quadratic-coefficients 6 --random-seeds 15000 --beam 48 --generations 30 --mutations 12000 --seed 9822026 --output experiments/erdos982/noncyclic_exact_run.json
python experiments/erdos982/independent_verify_noncyclic.py experiments/erdos982/noncyclic_exact_run.json --output experiments/erdos982/noncyclic_exact_run_verified.json
python experiments/erdos982/verify_dihedral_algebra.py
python experiments/erdos982/verify_d2_algebra.py
dotnet run --project experiments/erdos982/d2_octagon_exhaustive/D2OctagonExhaustive.csproj -c Release -- --bound 1000 --threads 8 --output experiments/erdos982/d2_octagon_bound1000.json
node experiments/erdos982/independent_d2_candidate_audit.mjs experiments/erdos982/d2_octagon_bound1000.json experiments/erdos982/independent_d2_bound1000_verified.json
dotnet run --project experiments/erdos982/d2_octagon_exhaustive/D2OctagonExhaustive.csproj -c Release -- --bound 40 --threads 8 --output experiments/erdos982/d2_octagon_bound40.json
python experiments/erdos982/independent_d2_audit.py experiments/erdos982/d2_octagon_bound40.json --output experiments/erdos982/d2_octagon_bound40_verified.json
uv run --with numpy --with scipy python experiments/erdos982/audit_skydiscover_scale_bug.py .research-cache/evolution-fine-tuning --output experiments/erdos982/skydiscover_scale_bug.json
```

The exhaustive span-7 run took about five minutes on the exploration machine;
the heuristic took about one minute.

## Limitations

The lattice-exhaustive result concerns only `n=8` integer-coordinate polygons
with larger coordinate span at most 7.  The `D2` theorem concerns only the
displayed four-parameter family; the other all-order theorem concerns only
two alternating regular orbits.  A counterexample need not be integral,
rational, symmetric, small, or of order 8.  The heuristic is not exhaustive.
No resolution of the open problem is claimed.
