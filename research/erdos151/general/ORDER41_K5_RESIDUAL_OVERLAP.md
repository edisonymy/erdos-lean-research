# Order 41 with a maximum K5: exact residual-overlap reduction

**Status (2 August 2026).**  This note gives a new reduction of the
`omega(G)=5` order-41 lane.  It does **not** settle that lane or Erdos problem
#151.  The elementary statements below are proved without computation.  The
exclusion of one of the three profile rows is conditional on the published
completeness of the pinned seven-graph Ramsey `(3,6;17)` catalogue.  The
remaining two rows are stated exactly rather than hidden behind a heuristic.

The reproducible finite checker is
[`checks/check_order41_k5_overlap.py`](checks/check_order41_k5_overlap.py).
It does not search order-41 graphs and does not use the campaign CEGAR code.

## 1. Hypotheses and notation

Assume that `G` has order 41 and

```text
beta(G) <= 9,  Delta(G) <= 9,  omega(G) = 5.
```

Fix a maximum clique `M` of size five and put `X=V(G)\M`, so `|X|=36`.
For `0<=i<=4`, let `n_i` count the vertices `x in X` having exactly `i`
neighbours in `M`.  Write

```text
W = sum_i i n_i = e(M,X),       t = 25-W >= 0.
```

The number 25 is the total cross-degree capacity of `M`: every vertex of
`M` already has four neighbours in `M` and has total degree at most nine.
For `c in M`, define

```text
Z_c = {x in X : N(x) intersect M is contained in {c}}.
```

Let `U` be the `n_0` class, let `A_c` be the vertices whose unique neighbour
in `M` is `c`, and put `a_c=|A_c|`.  Thus

```text
Z_c = U union A_c,       |Z_c|=n_0+a_c,       sum_c a_c=n_1.
```

The previously audited residual argument gives, pointwise,

```text
beta(G[Z_c]) <= 5,       |Z_c| <= 17.                    (1)
```

Only the through-order-39 theorem and the known Ramsey values through
`R(3,6)=18` enter (1).

## 2. PROVED: exactly three cross-profile rows

Eliminating `n_0` and `n_1` from `sum n_i=36` and
`sum i n_i=25-t` gives the exact identity

```text
sum_c |Z_c| = 80 + 4t + 3n_2 + 7n_3 + 11n_4.            (2)
```

Summing the five pointwise bounds in (1) gives a right side at most 85.
Consequently

```text
4t + 3n_2 + 7n_3 + 11n_4 <= 5.                          (3)
```

There are exactly three nonnegative integer solutions compatible with the
two defining equations:

| row | `(t,n_2,n_3,n_4)` | `(n_0,n_1)` | residual sizes |
|---|---:|---:|---|
| R: rigid | `(0,0,0,0)` | `(11,25)` | `16,16,16,16,16` |
| D: one double neighbour | `(0,1,0,0)` | `(12,23)` | `16,16,17,17,17` |
| T: one unit of cross deficit | `(1,0,0,0)` | `(12,24)` | `16,17,17,17,17` |

The pointwise fan sizes and clique-vertex degrees are also forced.

- In R, all five fans have size five and every vertex of `M` has degree
  nine.
- In D, let `w` be the unique vertex with two neighbours `p,q in M`.
  The fans `A_p,A_q` have size four, the other three fans have size five,
  and every vertex of `M` has degree nine.  The two degree-nine spokes are
  `A_p union {w}` and `A_q union {w}`.
- In T, one fan has size four and four have size five.  The clique vertex at
  the four-fan has degree eight; the other four clique vertices have degree
  nine.

For example, in row D the two endpoints of `w` have remaining cross-degree
capacity four, while the other three clique vertices have capacity five.
Since `sum a_c=23`, every capacity is attained.  The other rows are the same
one-line capacity argument.

Since `H(16)=H(17)=5`, (1) and the through-order theorem imply the exact
residual value

```text
beta(G[Z_c]) = 5                                             (4)
```

for every residual in every row.

## 3. PROVED: every residual is K4-free

This point is stronger than the static `K6` exclusion and is useful even
without the catalogue.

**Lemma 3.1.**  If `F` has order 16 or 17 and `beta(F)<=5`, then `F` is
`K4`-free.

**Proof.**  An open neighbourhood is admissible, so `Delta(F)<=5`.  Suppose
`C` is a `K4`, choose `c in C`, and put `P=C\{c}`.  Each of the three
vertices in `P` has at most two neighbours outside `C`.  At least

```text
|F|-4-3*2 >= 6
```

vertices outside `C` are therefore anticomplete to `P`.  Choose six of them.
Their induced graph has an admissible 3-set because `H(6)=3`.  Joining that
set to `P` gives an admissible 6-set in `F`: the clique `P` extends by `c`,
there is no mixed clique, and an `F`-maximal clique inside the six-vertex
residual would also be maximal in that induced graph.  This contradicts
`beta(F)<=5`.  QED.

In particular, every triangle in a residual is an inclusion-maximal clique.

## 4. PROVED: domination of the common class

Let `c in M` have degree nine.  Its open neighbourhood `N(c)` is a maximum
admissible 9-set.  For any `u in U`, the ten-set `N(c) union {u}` must contain
a maximal clique.  A clique inside `N(c)` extends by `c`, while `u` is
anticomplete to `M`.  Therefore `u` has a neighbour in the outside part of
`N(c)`.

Thus:

```text
R: every A_c dominates U;
D: every A_c (for c notin {p,q}) dominates U,
   and each A_p union {w}, A_q union {w} dominates U;
T: each of the four size-five fans dominates U.               (5)
```

Combining (5) with `Delta(G[Z_c])<=beta(G[Z_c])=5` gives

```text
Delta(G[U]) <= 4.                                              (6)
```

There is a useful replacement for (5) at the unique degree-eight clique
vertex in row T.  Let its four-fan be `A_0`, and let

```text
D_0 = {u in U : N(u) intersect A_0 is empty}.
```

Then `D_0` is a clique.  Indeed, if distinct `u,v in D_0` were nonadjacent,
the ten-set `N(c_0) union {u,v}` would be admissible: every clique in
`N(c_0)` extends by `c_0`, and `u,v` are isolated inside this ten-set.
This contradicts `beta(G)<=9`.

## 5. CATALOGUE-CONDITIONAL: an order-17 residual is triangle-free

The next lemma is a theorem conditional on completeness of the pinned
Ramsey catalogue, not an unlabelled experimental observation.

**Lemma 5.1.**  Assume the seven records in the complete Ramsey
`(3,6;17)` catalogue exhaust the triangle-free order-17 graphs with
independence number at most five.  If `|F|=17` and `beta(F)<=5`, then `F` is
triangle-free.

**Proof.**  By Lemma 3.1, `F` is `K4`-free, and `Delta(F)<=5`.  Suppose `abc`
is a triangle.  For the edge `ab`, the union of the outside-`abc`
neighbourhoods of `a,b` has size at most six.  If it had size at most five,
at least nine outside vertices would be anticomplete to `{a,b}`.  Since
`H(9)=4`, adjoining an admissible 4-set there to `{a,b}` would give an
admissible 6-set.  Hence equality holds: `a,b` both have degree five and
their three-element outside neighbourhoods are disjoint.  Applying this to
all triangle edges shows that every edge of every triangle lies in exactly
one triangle.  In particular, distinct triangles are edge-disjoint.

Let `q>=1` be the number of triangles, let `L` be the edges lying in no
triangle, and choose exactly one edge from each triangle.  Put `J` equal to
`L` together with the chosen edges.  Edge-disjointness makes `J`
triangle-free.  It also meets every nontrivial maximal clique of `F`:
maximal 2-cliques lie in `L`, and, because `F` is `K4`-free, all larger
maximal cliques are triangles.  Therefore every independent set of `J` is
admissible in `F`, so `alpha(J)<=5`.

The pinned complete catalogue says every such `J` has at least 40 edges and
minimum degree at least four.  On the other hand,

```text
|E(J)| = |E(F)|-2q <= 42-2q.
```

It follows that `q=1`, `|E(F)|=42`, and `|E(J)|=40`.  The degree sequence of
`F` is then one 4 and sixteen 5s.  All three vertices of its unique triangle
have degree five.  Retaining one triangle edge in `J` and deleting the other
two gives `J` a vertex of degree three (the endpoint common to the two
deleted edges), contradicting the catalogue's minimum-degree-four check.
QED.

The exact catalogue dependency is:

```text
experiments/erdos128/r36_17.g6
SHA-256 3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361
7 records; edge histogram {40:2, 41:3, 42:2}; minimum degree >=4.
```

Completeness is attributed in `experiments/erdos128/MANIFEST.json` to
Brendan McKay's Ramsey catalogue.  The checker verifies the local hash,
record count, triangle-freeness, `alpha<=5`, edge histogram, and degree
sequences; it cannot itself prove that an external catalogue is complete.

Consequently every size-17 residual in rows D and T is literally a Ramsey
`(3,6;17)` graph.  In particular, their common graph `G[U]` is triangle-free.

## 6. CATALOGUE-CONDITIONAL: exact overlap enumeration

For a size-17 residual `F=G[U union A_c]`, the five-vertex fan `A_c`
dominates `U` by (5).  The checker performs the following finite operation.

1. In each of the seven catalogue graphs, enumerate all five-subsets `A`
   that dominate their twelve-vertex complement `U`.
2. This gives exactly 4,368 `(F,A,U)` records.
3. Group the induced `U` graphs by exact VF2 isomorphism.  Every isomorphism,
   including every automorphic alignment, transports the twelve cross
   degrees `d_A(u)`.  There are exactly 786 common-`U` isomorphism classes
   carrying 1,963 distinct automorphism-closed aligned degree patterns.
4. Add three or four aligned cross-degree vectors and enforce the global
   degree-nine budget at every vertex of `U`.

No nonedge is inferred from a hash: color refinement is used only as a
coarse bucket, and exact isomorphism decides every class and alignment.

### Row T is excluded

Only ten of the 786 classes can carry four aligned size-17 residuals within
the degree budget.  In every alignment in all ten classes, at least three
vertices of `U` already have total degree nine before the four-fan `A_0` is
attached.  Those vertices cannot meet `A_0`, so they lie in `D_0`.

But `U` is triangle-free, whereas Section 4 proved that `D_0` is a clique.
Thus `|D_0|<=2`, a contradiction.  The checker finds exactly

```text
10 classes before the D_0 condition, 0 afterward.
```

Therefore **row T cannot occur**, conditional on the catalogue-completeness
premise.

### Row D reduces to seventeen common cores

For row D, three full fans give size-17 catalogue residuals.  After their
cross degrees are added, reserve degree for the two overlapping spokes
`A_p union {w}` and `A_q union {w}`.

For a vertex `u in U`:

- if `uw` is absent, at least one neighbour in each of `A_p,A_q` is needed,
  costing at least two degree units;
- if `uw` is present, that one edge dominates both spokes;
- a vertex with only one remaining degree unit is therefore forced to meet
  `w`; and
- at most seven vertices of `U` can meet `w`, since `w` already has its two
  neighbours `p,q in M` and `Delta(G)<=9`.

Exactly 17 common-`U` isomorphism classes survive these necessary
conditions.  Their graph6 representatives, degrees, independence numbers,
and all aligned-pattern counts are emitted by the checker.  They have

```text
e(U) in {20,21,22},   alpha(U) in {4,5},   Delta(U)=4.
```

This is a sharp finite reduction, not an exclusion.  The two order-16
residuals and the edges between different fans still have to be imposed.

The five cores omitted by the pre-remediation enumeration are:

```text
K`_PYYCE@BGQ
K??P`XMUCKyG
K`_PYWWOkHCI
K@?JKhheagT?
K@hWOHacbAqK
```

The immutable audit in `ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.md` records why
the earlier `1920 / 6 -> 0 / 12` output failed: the first record creating a
new exact-isomorphism class contributed only its seed alignment, rather than
the entire automorphism orbit of that seed.  The repaired checker closes new
seeds under every automorphism and hard-checks the corrected
`1963 / 10 -> 0 / 17` totals.  Exact post-repair hashes and the audit binding
are in `ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.json`.

## 7. COMPUTATIONALLY FALSIFIED: order 16 need not be triangle-free

It is essential not to apply Lemma 5.1 to the size-16 residuals.  The
following exact counterexample was obtained by adding edge `(1,3)` to one
record of the pinned Ramsey `(3,6;16)` catalogue:

```text
base graph6:       O@?ACEIDXHDooFUQLgC{?
candidate graph6:  OB?ACEIDXHDooFUQLgC{?
```

The candidate has

```text
n=16, e=39, degree sequence (4,4,5^14), one triangle,
omega=3, alpha=5, beta=5.
```

Two independent exact-beta engines agree:

- NetworkX maximal cliques plus RC2 MaxSAT returns `beta=5` and the
  admissible witness `{0,6,9,13,14}`;
- the separate graph6 parser, bitset Bron--Kerbosch implementation, and
  branch-and-bound minimum hitting-set engine also returns `beta=5`.

The checker verifies the compressed and decoded hashes of the 2,576-record
order-16 catalogue before locating the base graph and reconstructing the
candidate.  This counterexample closes the tempting shortcut "all five
residuals are triangle-free."

There is nevertheless a sound catalogue reduction at order 16.

**Lemma 7.1.**  Every order-16 graph `F` with `beta(F)<=5` contains a
spanning triangle-free subgraph `J` with `alpha(J)<=5`.  Consequently,
conditional on completeness of the pinned Ramsey `(3,6;16)` catalogue, `F`
is a supergraph of one of its 2,576 records.

**Proof.**  Lemma 3.1 makes `F` `K4`-free.  The published bound
`F_e(3,3;4)>19` says that a `K4`-free graph on 16 vertices does not arrow
`(3,3)`.  Fix a red/blue edge-colouring of `F` with no monochromatic
triangle.  Let `L` be the maximal 2-cliques of `F`, and let `J` be `L`
together with one colour class.  The Folkman-reduction proof shows that `J`
is triangle-free and every `J`-independent set is admissible in `F`.
Therefore `alpha(J)<=beta(F)<=5`.  QED.

This lemma applies to all five residuals in row R and to the two size-16
residuals in row D.  It does **not** say that `F` itself is triangle-free;
the displayed witness is a one-edge illustration of exactly that gap.

## 8. Exact remaining frontier

The `omega=5`, order-41 lane is now reduced to two rows.

### R: rigid row

```text
|U|=11; five disjoint fans A_c of size 5;
every c in M has degree 9;
every A_c dominates U;
Delta(G[U])<=4;
each G[U union A_c] is K4-free and has beta exactly 5.
```

No size-17 catalogue residual is available here.  The order-16 witness in
Section 7 shows why triangle-freeness cannot be assumed.

### D: one-double-neighbour row

```text
|U|=12; one w with N_M(w)={p,q};
|A_p|=|A_q|=4 and the other three fans have size 5;
all M vertices have degree 9;
the three full residuals are Ramsey (3,6;17) graphs;
U is one of 17 explicit graph6 cores after aligned degree filtering;
the two size-16 residuals are K4-free and have beta exactly 5.
```

The exact missing finite lemma for D is:

> None of the 17 common cores and its surviving three-fan alignments admits
> two order-16 `beta=5` extensions on four new vertices, together with a
> shared vertex `w`, the two spoke-domination conditions, the global degree
> budget, and the order-41 admissibility condition.

This lemma is deliberately not claimed.  Lemma 7.1 makes a finite
catalogue-supergraph attack plausible: the pinned catalogue has 2,576
records and degree at most five leaves few supergraph edges.  That
observation describes the next exact exhaustion; it is not itself the
exhaustion.

The corresponding missing structural lemma for R must couple five
supergraphs of the order-16 catalogue through the same `U`.  Per-residual
beta and domination alone are not enough; the remaining information is
global: edges between different fans, simultaneous saturation of every
maximum admissible 9-set, and the necessary arrowing condition
`G -> (3,3)`.

## 9. Reproduction and claim boundary

From the repository root:

```powershell
.\.venv\Scripts\python.exe research\erdos151\general\checks\check_order41_k5_overlap.py
```

The checked output is `status: VERIFIED`, with counts `4368`, `786`, `1963`
aligned patterns, `10 -> 0`, and `17`, and agreement `beta_A=beta_B=5` on the order-16
counterexample.

The safe conclusions are:

1. the three-row profile split, residual `K4` exclusion, domination facts,
   and exact residual beta values are unconditional under the standing
   order-41 hypotheses;
2. row T is impossible conditional on completeness of the pinned
   `(3,6;17)` catalogue;
3. row D is reduced to 17 common cores, not solved;
4. row R remains open; and
5. no SAT/UNSAT result, full order-41 theorem, or solution of Erdos #151 is
   claimed here.
