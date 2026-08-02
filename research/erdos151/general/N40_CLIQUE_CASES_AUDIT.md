# Independent audit of the order-40 clique ledger

**Date:** 2 August 2026.  **Verdict:** useful order-40 reductions survive,
but the source note is **not sound as written**.  Its opening standing package
misstates the independence-number conclusion, G3 begins with an impossible
Ramsey-subset choice before correcting itself, the claimed multi-adjacency
slopes are wrong, and the claimed handoff to the current exact F4/F5 runs is
false: the active v2 runs have order 41.  The corrected ledger does **not**
prove a contradiction.  This audit makes **no full-solution claim** for
Erdos #151 and does not duplicate the separate K4-free order-40/41 work.

This audit originally examined `N40_CLIQUE_CASES.md` at SHA-256
`5620ec50dff3145ea2ed3fc1d963d68a25716e6014f7ff4f199b17d4efc74e39`
(97 lines).  The source was then preserved verbatim except for an eight-line
audit-failure notice prepended beneath its title; that warned copy has SHA-256
`9096fe29c0a8aecebf0fd2c4d089326a454a684a282bc45eb44dc11631fd9ba2`
and 105 lines.

## Verdict ledger

| source claim | verdict | correction or qualification |
|---|---|---|
| conditional order-40 jump setup | **PASS** | If `R(3,10)=40`, then `H(40)=10`; otherwise order 40 is in the `H=9` plateau and propagates from order 39. |
| standing ``beta = alpha = 9`` | **FAIL** | A least counterexample here has `beta(G)=9` and only `alpha(G)<=9`.  Equality `alpha(G)=9` is not forced. |
| G1 cross-edge ledger | **PASS** | State it for every maximum `s`-clique `M`, where `s=omega(G)`.  Such an `M` is ambient-maximal. |
| G2 lower bounds 15 and 18 | **PASS** | The optima and unique count profiles are correct.  “All-`i=1`” must mean all outside vertices having a positive `M`-degree have degree one into `M`; there are also `n_0=10` or `12` vertices. |
| G2 “machine-checked” provenance | **FAIL (provenance), PASS (result)** | No checker or output artifact for this LP was found in the repository.  An independent exhaustive enumeration gives the stated unique optima, and the algebraic identity below proves them without computation. |
| `H(R(3,11-s))=11-s` for `s=4,5` | **PASS but inapplicable** | Numerically this is `H(18)=6` or `H(23)=7`.  The error is not this H-value; it is the unsupported claim that `Z_c` has 18 or 23 vertices. |
| first part of G3 | **FAIL** | G2 does not supply an `R(3,11-s)`-subset: it would require 18 vertices for `s=5` and 23 for `s=4`, not 15 and 18.  The false preamble should be removed, not retained inside a section labelled PROVED. |
| corrected last part of G3 | **PASS after reformulation** | It yields a maximum admissible 9-set, not a contradiction.  A stronger exact-residual formulation is proved below. |
| order-40 G4 equality profiles | **PASS** | The profiles are correct for a fixed maximum clique, with the quantifiers made explicit below. |
| G4 applicability to current exact runs | **FAIL** | Both active v2 F4/F5 runs and all v2 production presets have `n=41`.  No order-40 v1 run directory exists, and no ledger-specific clauses are implemented in either CEGAR source tree. |
| failed-reduction “slope `3/4`, `4/5` per `i>=2` mass” | **FAIL** | Those are the slopes for one unit of unused cross-edge budget, not for one `n_2` vertex.  The actual minimum increments are `1/2` for `s=4` and `3/5` for `s=5`; higher classes have different weights. |
| claim that positive `n_2+n_3` closes the case | **FAIL as written** | A single `n_2` vertex is insufficient in either case, and the `s=5` statement also omits `n_4`.  Exact sufficient/necessary weighted conditions appear below. |
| maximal cliques “shield” their 10-vertex supersets | **PASS** | Every 10-set containing the ambient-maximal `M` is already bad, so the bad-10-set axiom adds no information on such a superset. |
| prior-art absence claim | **NOT VERIFIED** | Absence from a search is not a mathematical fact and no reproducible search record is attached.  It should remain a research-log statement only. |

## Hypotheses and Ramsey values

Assume throughout this section that `R(3,10)=40` and that `G` is a
least-order counterexample of order 40 with `omega(G)=s in {4,5}`.  From the
through-order-39 theorem and induced monotonicity,

```text
beta(G)=9,  alpha(G)<=9,  Delta(G)<=9,  delta(G)>=4.
```

The clique-residual lemma with `s=6` gives `omega(G)<=5`.  The Ramsey values
used in the ledger are

```text
R(3,5)=14,  R(3,6)=18,  R(3,7)=23,  R(3,8)=28,  R(3,9)=36,
40 <= R(3,10) <= 41.
```

Consequently `H(15)=5` and `H(18)=6`.  The direct contradiction thresholds
are 18 for a maximum K5 and 23 for a maximum K4.  These values agree with
Radziszowski's April 2026 dynamic survey, and the current upper bound is the
published result of Angeltveit:

- [Small Ramsey Numbers, revision 18](https://www.combinatorics.org/ojs/index.php/eljc/article/download/DS1/pdf/), Table Ia;
- [V. Angeltveit, `R(3,10) <= 41`](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v32i4p30).

## G1 and G2: proof and exact equality characterization

Fix a maximum `s`-clique `M`.  For `x notin M`, let
`i=d_M(x)=|N(x) intersect M|`, and let `n_i` count the vertices with that
value.  Since `M` is maximum, `0<=i<=s-1`.  Put

```text
N = 40-s,
B = s(10-s),
W = sum_i i n_i = e(M,V(G)\M),
t = B-W >= 0.
```

Thus `(N,B)=(35,25)` for `s=5` and `(36,24)` for `s=4`.  For `c in M`, put

```text
Z_c = {x notin M : N(x) intersect M is contained in {c}}.
```

If `a_c` counts vertices whose `M`-neighborhood is exactly `{c}`, then
`|Z_c|=n_0+a_c`, `sum_c a_c=n_1`, and hence

```text
sum_c |Z_c| = s n_0+n_1.                         (1)
```

Eliminating `n_0,n_1` gives the following exact identity, not merely an LP
bound:

```text
sum_c |Z_c|
 = sN-(s-1)B +(s-1)t
   + sum_{i=2}^{s-1} (((s-1)(i-1))-1) n_i.       (2)
```

In the two cases this is

```text
s=5:  sum_c |Z_c| = 75 + 4t + 3n_2 + 7n_3 + 11n_4;
s=4:  sum_c |Z_c| = 72 + 3t + 2n_2 + 5n_3.       (3)
```

All correction terms are nonnegative.  Therefore some `Z_c` has size at
least 15 for `s=5` and at least 18 for `s=4`.  Equality of the average forces
`t=0` and every `n_i=0` for `i>=2`, so the unique count profiles are

```text
s=5: (n_0,n_1,n_2,n_3,n_4)=(10,25,0,0,0);
s=4: (n_0,n_1,n_2,n_3)=(12,24,0,0).
```

For a fixed `M`, absence of a `Z_c` of size 16 (respectively 19) further
forces every `|Z_c|` to equal 15 (respectively 18).  Hence every fan has size
5 (respectively 6), every vertex of `M` has degree 9, and the outside fans
are disjoint.  In the K4 case, `n_2=n_3=0` also proves that each edge of `M`
lies in exactly the two triangles contained in `M` and in no outside
triangle.

The exact pointwise quantifier needed by a fixed-labelled-clique solver is

```text
for every maximum clique M:
  (there exists c in M with |Z_c(M)|>=16) or Rigid_5(M),
```

and analogously with threshold 19 and `Rigid_4(M)`.  A global version is
`(there exists M,c with a large Z_c) or (every maximum M is rigid)`, but that
weaker global disjunction is not itself a pruning clause about a designated
labelled clique.

## Corrected and strengthened G3

The clean statement uses the whole residual and avoids the false
`R(3,11-s)` subset choice.

**Residual-beta bound.**  For every `c in M`,

```text
beta(G[Z_c]) <= 10-s.                             (4)
```

Indeed, put `P_c=M\{c}` and take any set `S` admissible in the induced graph
`G[Z_c]`.  The set `P_c union S` is admissible in `G`: a nontrivial clique in
`P_c` extends by `c`; no mixed clique exists because `P_c` is anticomplete to
`Z_c`; and a `G`-maximal clique contained in `S` would also be maximal in
`G[Z_c]`.  This is exactly the valid ambient-to-induced direction of
maximality.  Since `beta(G)=9`, (4) follows.

Least-order minimality also gives
`beta(G[Z_c])>=H(|Z_c|)`.  Therefore every maximum clique satisfies the
pointwise upper bounds

```text
s=5: |Z_c|<=17 for every c in M;
s=4: |Z_c|<=22 for every c in M.                 (5)
```

Choose `c` attaining the G2 lower bound.  Equations (4), (5), and the exact
Ramsey values then give

```text
s=5: 15<=|Z_c|<=17 and beta(G[Z_c])=5;
s=4: 18<=|Z_c|<=22 and beta(G[Z_c])=6.           (6)
```

Thus a maximum residual-admissible `S` combined with `P_c` is a maximum
admissible 9-set in `G`, containing a K4 when `s=5` and a triangle when
`s=4`.  This proves the intended corrected G3 and no more.

There is one additional sound saturation consequence.  For such an `S`,
every `x in Z_c\S` has a nonempty clique anchor `A subseteq S` for which
`A union {x}` is an ambient-maximal clique of `G`.  This follows because
`P_c union S` is maximum admissible, while `x` is anticomplete to `P_c`.
In particular, `S` dominates `Z_c\S`.  This is a valid future oracle clause,
not a contradiction.

## Sound strengthened clauses for a future order-40 solver

For each fixed labelled maximum clique, (5) can be encoded directly as
at-most cardinality constraints on the literals

```text
z_{x,c} <=> every edge xp with p in M\{c} is absent.
```

The bounds are `sum_x z_{x,c}<=17` in F5_N40 and `<=22` in F4_N40, for
every `c` in the fixed clique.  They are consequences of the already proved
lower-order theorem and ambient-maximal semantics; they are not heuristic
cuts.

Summing these per-`c` bounds and using (3) gives the cheaper necessary
aggregate cuts

```text
F5_N40: 4t + 3n_2 + 7n_3 + 11n_4 <= 10;         (7)
F4_N40: 3t + 2n_2 + 5n_3 <= 16.                  (8)
```

For example, (7) forces `n_4=0`, `n_3<=1`, `n_2<=3`, and `t<=2` (with
stronger tradeoffs when more than one term is positive).  These are rigorous
necessary conditions for a counterexample, not a solution.

Conversely, the sharp aggregate sufficient ledger-only contradiction
conditions are

```text
F5_N40: 4t + 3n_2 + 7n_3 + 11n_4 >= 11;
F4_N40: 3t + 2n_2 + 5n_3 >= 17.                  (9)
```

They force the average high enough that some residual reaches 18 or 23.
This corrects the source note's slope claim.  A single `n_2` vertex does not
close either case.  Explicit ledger-feasible profiles demonstrating the gap
are

```text
s=5: (n_0,n_1,n_2,n_3,n_4)=(11,23,1,0,0), max |Z_c|=16;
s=4: (n_0,n_1,n_2,n_3)=(13,22,1,0),       max |Z_c|=19,
```

where the unique-neighbor fans can be distributed as `(5,5,5,4,4)` with
the double-neighbor vertex on the two size-4 fans, and `(6,6,5,5)` with it
on the two size-5 fans.  These assignments also respect each `M`-vertex's
out-degree ceiling.  Thus positive multi-adjacency alone is insufficient.

## Exact-run applicability: order 40 does not transfer to the active runs

The v2 `cases.json`, README, and both active run metadata files identify the
current runs as `F4_N41` and `F5_N41`, with `n=41` and degree interval
`[5,9]`.  The older v1 tree contains N40 presets, but its only production run
directories are also N41.  Searches of both source trees found no
ledger-specific clause implementation.  Therefore:

1. none of (5), (7), or (8) was used by any exact run inspected here;
2. an active hash-chained N41 journal must not be described as checking an
   N40 clause package;
3. adding these constraints would require a fresh, separately audited solver
   revision and fresh run directory.

The original order-40 G4 disjunctions are particularly unhelpful at order
41.  Replacing `N=40-s` by `N=41-s` makes their first arms automatic:

```text
n=41, s=5: some |Z_c|>=16;
n=41, s=4: some |Z_c|>=19.
```

So the original N40 disjunction is true but vacuous on the active presets; it
does not force the N40 rigid profile.  A valid order-41 analogue must be
re-derived.  For reference only, the exact identities become

```text
s=5: sum_c |Z_c| = 80 + 4t + 3n_2 + 7n_3 + 11n_4;
s=4: sum_c |Z_c| = 76 + 3t + 2n_2 + 5n_3.
```

Together with the same pointwise upper bounds (the residuals have fewer than
40 vertices), they imply

```text
F5_N41: 4t+3n_2+7n_3+11n_4<=5,
         and either some |Z_c|>=17 or
         (n_0,n_1)=(11,25) with five equal size-5 fans;
F4_N41: 3t+2n_2+5n_3<=12,
         and either some |Z_c|>=20 or
         (n_0,n_1)=(13,24) with four equal size-6 fans.
```

These N41 statements are mathematically sound re-derivations, but they are
not present in the current solver and this audit makes no claim about what a
new run using them would conclude.

## Final audit boundary

The surviving result is a family of local, necessary fixed-clique clauses
plus exact residual-beta structure.  The ledger alone remains feasible in
both clique cases and supplies no order-40 contradiction.  Any use in an
exact search must preserve the quantifier “for every designated maximum
clique” and the order parameter from which `N=40-s` or `41-s` was derived.
No terminal SAT/UNSAT, exhaustion, counterexample, or proof of Erdos #151 is
claimed here.
