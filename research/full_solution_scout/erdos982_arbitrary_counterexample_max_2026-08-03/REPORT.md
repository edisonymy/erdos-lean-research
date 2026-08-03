# Erdős #982 arbitrary-geometry / H8-relaxation lane

**Date:** 2026-08-03
**Status:** lane stopped by its predeclared kill criterion
**Full problem status:** **OPEN; no solution or counterexample is claimed here**

## Executive outcome

The priority audit substantially changes the finite-order picture.  The
Harborth--Fishburn eight-point set is not merely a useful computational seed:
published work classifies it as the unique eight-point locally three-distance
set in the plane.  Since it is not in convex position, this settles the
potential counterexample order `n=8`; the same maximum-cardinality result rules
out a locally-three-distance set on nine points.  These are prior-art
consequences, not new campaign results.

The best genuinely new seed found in this lane was the unique minimum-rank
row-space among all `8^8` minimal one-split-per-vertex relaxations of H8 from
three to four local distance classes.  It is an eight-point framework made of
eight equilateral triangles (a triangle decomposition of `K_8` minus a perfect
matching).  Its exact Jacobian has rank 10 on 16 real coordinate variables, so
it has two infinitesimal degrees of freedom beyond similarities.

That promising seed is nevertheless now **closed exactly**.  All `2^8`
orientation branches of its equilateral-triangle equations were classified
over `Q(sqrt(-3))`.  Only two nondegenerate branches remain; they are mirror
images of one complex-parameter family.  Exact orientation identities prove
that neither branch has a strictly convex realization.  Therefore it cannot be
the eight-vertex subset of a convex ten-point counterexample, and there is no
two-point extension to test.  This satisfies kill criterion (a), so this lane
stops rather than expanding into a broader local-four search.

## Exact problem and current external status

Erdős #982 asks whether every set of `n` distinct points forming a strictly
convex polygon has a vertex from which at least `floor(n/2)` distinct distances
occur.  The public database still marked the problem open when checked on
2026-08-03:

- <https://www.erdosproblems.com/982>
- local formal statement:
  `.research-cache/formal-conjectures/FormalConjectures/ErdosProblems/982.lean`

Database status is not treated as proof of novelty or openness.  The campaign
also checked the 25 July 2026 Kominers manuscript and found only a coefficient
improvement, not the `1/2` conjecture.

## Priority audit and citation correction

### Reliable primary / near-primary locations

1. P. C. Fishburn, *A remarkable eight-point planar configuration*,
   **Discrete Mathematics 252** (2002), 103--122,
   DOI <https://doi.org/10.1016/S0012-365X(01)00134-0>.
   The publisher abstract states that H8 is the unique eight-point planar
   configuration in which every point has exactly three local distances, and
   the unique minimizer of the sum of local distance counts.

2. H. Nozaki and M. Shinohara, *On a generalization of distance sets*,
   arXiv:0906.0199v2, **section 4.5, Proposition 4.18**:
   <https://arxiv.org/pdf/0906.0199v2>.
   It records: every eight-point planar set has sum of local distance counts at
   least 24; equality is uniquely the displayed H8 configuration; every
   eight-point locally-three-distance planar set is H8; hence the planar
   locally-three-distance maximum is 8.  It cites the Erdős--Fishburn and
   Fishburn primary papers for the classification.

3. P. Erdős and P. C. Fishburn, *Distinct distances in finite planar sets*,
   **Discrete Mathematics 175** (1997), 97--132,
   DOI <https://doi.org/10.1016/S0012-365X(96)00145-8>.
   Its abstract gives the eight-point sum lower bound `24`.

### Numbering hazard resolved

An initial search extraction exposed the result under the old/preprint label
“Proposition 4.3.”  Checking the full current arXiv version showed that this is
not a stable citation: in **v2** the result is in **section 4.5, Proposition
4.18**.  The final campaign record must use the v2 location above.  Do not cite
an unqualified “Nozaki--Shinohara Proposition 4.3.”

## Prior-art finite-order consequence

Normalize H8 as

```text
A0=( 1+sqrt(3), 0)       A2=(-1-sqrt(3), 0)
A1=( 0, 1+sqrt(3))       A3=(0, -1-sqrt(3))
B0=( 1, 1)  B1=(-1, 1)  B2=(-1,-1)  B3=(1,-1).
```

Its four global squared distances are

```text
4,  8,  8+4sqrt(3),  16+8sqrt(3),
```

but every vertex sees exactly three of them, with incident multiplicities
`(4,2,1)`.  All four `B_i` lie strictly inside the axial diamond because

```text
|x(B_i)| + |y(B_i)| = 2 < 1+sqrt(3).
```

Thus H8 is not in convex position.  Fishburn's uniqueness theorem implies that
there is no convex eight-point locally-three-distance set.  Nozaki--Shinohara's
maximum-cardinality formulation also rules out any nine-point locally-three-
distance planar set.  Consequently #982 holds through `n=9` (the smaller
orders also follow from the classical lower bounds).  This is **prior art plus
an immediate convexity observation**, not a new solution claim.

## Exact H8 audit

`check_harborth_field.py` is dependency-free and works entirely in
`Q(sqrt(3))`.  It verifies:

- all 28 squared distances and their four global classes;
- exactly three local distances at all eight vertices;
- local multiplicities `(4,2,1)`;
- alternating turn signs and the strict interior inequality above;
- the centered Euclidean distance matrix has Gram rank 2;
- the full four-global-class equality Jacobian has rank 12 on 16 coordinates;
- more importantly, the equivalence relation generated **only by collisions
  at a common vertex** has class sizes `(12,12,1,1,1,1)` and still has exact
  Jacobian rank 12.

The final item corrects an initially over-strong rigidity interpretation: the
four diameter edges are singleton local classes and are not required to equal
their disjoint partners.  Removing those two global equalities does not produce
an infinitesimal flex; the nullity remains exactly the four similarity motions.

`check_harborth_extension.py` independently exhausts the 27 circle choices at
three noncollinear H8 centers and finds no ninth point preserving all eight old
three-distance palettes.  This is consistent with, but subsumed by, the
published maximum-cardinality theorem.

## H8 to local-four: exhaustive infinitesimal relaxation

At each H8 vertex the old incident class sizes are `(4,2,1)`.  Introducing one
additional local class minimally means exactly one of the following eight
partitions:

- split the 2-class into `1+1` (one option);
- split the 4-class into `1+3` (four options);
- split the 4-class into `2+2` (three options).

`search_h8_local4_relaxations.py` covers all `8^8` choices by dynamic
programming on canonical Jacobian row spaces over `GF(1000151)`, where
`sqrt(3)=766206`.  It then rechecks a minimum-rank witness exactly in
`Q(sqrt(3))`.

The 13 distinct final row spaces have distribution

```text
rank 10: 1 row space
rank 11: 11 row spaces
rank 12: 1 row space.
```

The rank-10 witness splits every 4-class into `2+2`.  Its non-singleton global
classes are the edge sets of these eight equilateral triangles:

```text
(A0,B0,B3)  (A0,A1,B2)  (A0,B1,A3)  (B0,A1,B1)
(B0,A2,A3)  (A1,A2,B3)  (B1,A2,B2)  (B2,A3,B3).
```

The four omitted edges form the perfect matching

```text
(A0,A2), (B0,B2), (A1,A3), (B1,B3).
```

Rank 10 gives real nullity 6: four similarity motions and two genuine
infinitesimal flex directions.

## Complete branch classification of the rank-10 seed

For an oriented equilateral triangle `(a,b,c)`, write

```text
z_c-z_a = rho (z_b-z_a),
rho in {(1+i sqrt(3))/2, (1-i sqrt(3))/2}.
```

Once the orientation of each of the eight triangles is fixed, all realization
equations are complex-linear over `Q(sqrt(-3))`.  The dependency-free scripts
enumerate all 256 sign patterns exactly and normalize `z_A0=0`, `z_B0=1`.

The complete result is:

- 212 patterns make that gauge inconsistent.  Any distinct realization would
  have `z_A0 != z_B0` and could be normalized, so these patterns force a
  collision.
- 42 patterns give a zero-parameter normalized branch, and every one has
  coincident vertices (18 have six duplicate pairs; 24 have seven).
- exactly two nondegenerate branches remain.  All eight signs are `+` or all
  eight are `-`; the branches are mirror images.

On the `+` branch, with

```text
omega=(1+i sqrt(3))/2, q=conjugate(omega), t arbitrary complex,
```

the complete normalized family is

```text
A0=0                  B0=1
A1=omega(1-t)         B1=q t
A2=omega+q t          B2=q(t-1)
A3=t                  B3=omega.
```

It is centrally symmetric for every `t`:

```text
A0+A2 = B0+B2 = A1+A3 = B1+B3 = omega+q t.
```

In a strictly convex centrally symmetric octagon, opposite vertices occur four
positions apart.  Requiring the eight `+`-oriented equilateral triples leaves
exactly six possible cyclic orders (with `A0` fixed first).  For each order,
`prove_equilateral_relaxation_nonconvex.py` exhibits two triples which the
order requires to have positive orientation, while their exact orientation
polynomials are `f(x,y)` and `-f(x,y)`.  Strict positivity is impossible.  The
mirror branch follows by reflection.

This is a complete semialgebraic obstruction for all complex parameters, not a
dense-grid inference.

## Claim scope and stop decision

### Proved / exactly checked in this lane

- The exact H8 metric, nonconvexity, EDM rank, and minimal-local-collision
  Jacobian rank.
- Exhaustive infinitesimal classification of the `8^8` one-split H8
  relaxations at the H8 point.
- Complete realization-branch classification and global nonconvexity of the
  unique rank-10/eight-equilateral-triangle relaxation.
- Elementary auxiliary obstruction: a finite vertex-transitive noncollinear
  planar point set is cocircular (its symmetry group fixes the centroid and
  transitivity gives a common radius), so a counterexample cannot come from a
  homogeneous planar association scheme.
- Elementary offset-pairing obstruction: an equilateral convex polygon with
  `|p_i-p_{i-2}|=|p_i-p_{i+2}|` at every vertex has period-two exterior angles;
  for odd order it is regular, and for even order it is two interlaced
  concentric regular orbits.  This recovers the already-excluded alternating-
  radius family.

### Not proved

- No assertion is made about every locally-four-distance eight-point set.
- The rank-11 and rank-12 H8 relaxation row spaces were not globally
  classified; infinitesimal rigidity at H8 does not exclude remote branches.
- No assertion is made that a ten-point counterexample cannot exist.
- No improvement to the general coefficient bound is claimed.
- No full or negative resolution of Erdős #982 is claimed.

### Why the lane stops

The declared stopping rule was to stop if the strongest H8-relaxation seed had
no strictly convex real branch, or if all convex branches failed exact
two-point extension.  The first condition has now been proved.  Because every
subset of the vertices of a strictly convex polygon is itself in strictly
convex position, a nonconvex eight-point framework cannot be the chosen old
subset of a convex ten-point construction.  Two-point extension is therefore
moot, and further work would broaden into a different search lane rather than
continue this one.

## Isosceles-transfer diagnostic

If a counterexample has `n=2m`, then at each vertex `2m-1` incident edges are
split among at most `m-1` distance classes.  Convexity of `binom(s,2)` gives at
least `m+1` apex-isosceles pairs (class sizes `3,2,...,2`).  For `n=2m+1` and
`m>=3`, the analogous minimum is `m+3` (class sizes `3,3,2,...,2`).

This translation is exact, but current global upper bounds on apex-isosceles
triangles are much too weak to contradict it.  Nivasch--Pach--Pinchasi--Zerbib
also give constructions with roughly `3n^2/4` such incidences, showing why a
pure total-count argument cannot reach the desired `n/2` threshold.  Any future
general attack needs distributional/convex-order information, not just the
total isosceles count.

Primary source: G. Nivasch, J. Pach, R. Pinchasi, S. Zerbib,
*The number of distinct distances from a vertex of a convex polygon*,
<https://arxiv.org/abs/1207.1266>.

## Reproduction

Run from this directory:

```powershell
python .\check_harborth_field.py
python .\check_harborth_extension.py
python .\search_h8_local4_relaxations.py
python .\enumerate_equilateral_h8_relaxation.py
python .\prove_equilateral_relaxation_nonconvex.py
```

The first, second, fourth, and fifth scripts use only the Python standard
library.  The relaxation search imports only the dependency-free H8 checker.

Expected terminal statuses are respectively:

```text
VERIFIED
VERIFIED_NO_EXTENSION
VERIFIED
VERIFIED
VERIFIED_NONCONVEX
```

### SHA-256 hashes

```text
0BB4E0CA03A28506970EA5C67D915F44C9D8B37DDD33518CA36416156169FD5A  check_harborth_extension.py
B1D3B23203B2A4D05C9EF782B8C5C1A3650BBE0D8BC4495EDEDADB219D2FCA79  check_harborth_extension_groebner.py
DBCE494284911B4AF0805B6957C8B81284408CCF412F0901A60C8B575ACCB19F  check_harborth_field.py
6D8CE83D6DF07BE49D44C16F3AB82E45EE5472D1AFD7AB978996A0ED7C20EDF7  check_harborth_sympy.py
BA90DD5D3BEC88D68ADABC0E477A3D42430F9E4C2643F85FA299137E81B6FE0A  enumerate_equilateral_h8_relaxation.py
417621AD6AB7AA53A7402AB55EB1E8F78D36A6D7509C77366C29D6163F4CD709  prove_equilateral_relaxation_nonconvex.py
076C6BD9B4632696009D764412D094C751B621FAECF4AC65F9B5D46B20DF7596  search_h8_local4_relaxations.py
```

## Independent-checker caveat

`check_harborth_sympy.py` and `check_harborth_extension_groebner.py` passed
under an elevated execution using a project-local SymPy 1.14 installation.
However, that installation was created with an ACL granting access only to
SYSTEM/Administrators/Owner.  In the ordinary sandbox it imports as an empty
namespace and `sp.sqrt` is unavailable.  A root-agent replay therefore failed.

An attempted recursive ACL expansion was rejected by the safety reviewer and
**was not performed**.  Accordingly:

- do not describe the current SymPy scripts as unprivileged/replayable
  independent verification;
- count their output only as a secondary local audit;
- use the dependency-free scripts above for the reproducible core result;
- if a second public checker is desired later, reinstall SymPy under a normal
  user-owned environment or implement the small field/linear-algebra audit in a
  separately maintained language.  Do not silently alter ACLs.

The decisive nonconvexity result itself does not depend on SymPy: the 256-branch
linear solve and all six opposite-polynomial certificates are checked in
`prove_equilateral_relaxation_nonconvex.py` using exact rational quadratic-field
arithmetic.

## Repository / publication actions

None.  No git operation, issue update, public post, or solution claim was made
from this lane.
