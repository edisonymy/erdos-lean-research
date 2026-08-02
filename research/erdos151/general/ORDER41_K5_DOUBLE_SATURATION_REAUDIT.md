# Independent re-audit of the strengthened order-41 `omega=5` row-D proof

**Date:** 2 August 2026. **Verdict: PASS.**

The post-audit strengthening is sound.  Independently of the supplied
component-profile checker, an exhaustive spanning-tree-extension enumerator
finds that every triangle-free graph `H` on 12 vertices with
`alpha(H)<=5` has at least 11 edges, and that equality has the unique
isomorphism type

```text
C5 disjoint-union C5 disjoint-union K2.
```

The equality classification is correct but is not needed for row D.  The
needed lower bound `e(U)>=11` contradicts the already independently audited
row-D saturation bound `e(U)<=10`.

The exclusion remains conditional on one external premise: completeness of
the pinned seven-record Ramsey `(3,6;17)` catalogue.  More precisely, the
seven pinned records must exhaust, up to isomorphism, all triangle-free
17-vertex graphs with independence number at most five.  The repository and
this re-audit verify the pinned bytes and all local record properties used by
the residual lemma, but do not prove that no eighth isomorphism type exists.
The strengthened proof no longer uses the repaired 17-core overlap
enumeration.

This PASS is not a whole-graph UNSAT result, a full order-41 theorem, or a
solution of Erdos problem #151.  No source or prior audit was edited.

## Audited inputs and bindings

| artifact | SHA-256 |
|---|---|
| strengthened `ORDER41_K5_DOUBLE_SATURATION.md` | `8353be6fde22d8e6edeb455187169b5eae4f6093ae971debcae353e7debddebd` |
| `ORDER41_K5_DOUBLE_SATURATION_ADDENDUM.md` | `96af57c9754f8b8be871c89787845b7ec1146c91863793df42dba6a63d7ae4d4` |
| point-in-time `ORDER41_K5_DOUBLE_SATURATION_AUDIT.md` | `760a2a904e6416e907fac2c569298704a41f216f2a3b53e5321820f3163d6d4d` |
| point-in-time `ORDER41_K5_DOUBLE_SATURATION_AUDIT.json` | `e4895962c37fd6ce32636717ba0afb6b041068267542ecc118632db0c0e2656b` |
| supplied profile checker | `68a73ad39d1a4f3857b512b23bb85b90b3cfc73a58784f4c82d5a5e53eb1a325` |
| independent re-audit enumerator | `d67ea28044f9ca66816eb94d8a92148a7a34ed6146dafc941c31f3d7201cf691` |
| residual source containing the order-17 lemma | `880b2de61369c2539218ec027b9757b9f8da5b98dd8243a9e06c11e0a09d07ca` |
| pinned `experiments/erdos128/r36_17.g6` | `3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361` |

The companion JSON binds this Markdown after the Markdown hash is known and
intentionally omits its own hash.

## 1. Fresh derivation of the 12-vertex lemma

Let `H` be triangle-free on 12 vertices with `alpha(H)<=5`, let `m=e(H)`,
and let `k` be its number of components.

### Component count

A triangle-free component with independence number one has at most two
vertices.  A triangle-free component with independence number two has at
most five vertices by `R(3,3)=6`.  If `k=4`, the component independence
numbers are bounded by a permutation of `(2,1,1,1)`, so the graph has at
most `5+2+2+2=11` vertices.  If `k=5`, it has at most ten vertices, and
`k>=6` already gives an independent six-set.  Therefore `k<=3`.

### No graph with at most ten edges

The total cyclomatic number is

```text
mu = m-12+k.
```

- If `k=1`, connectedness forces `m>=11`.
- If `k=2` and `m<=10`, both components are trees.  A tree of order `s`
  has independence number at least `ceil(s/2)`, so the two components give
  an independent six-set.
- If `k=3` and `m<=10`, the total cycle rank is at most one.  Thus all three
  components are trees, or one is unicyclic and two are trees.  A connected
  unicyclic graph of order `s` has independence number at least
  `floor(s/2)`: delete one cycle vertex and take the larger side of the
  resulting forest.  Hence

  ```text
  alpha(H) >= floor(s/2)+ceil(t_1/2)+ceil(t_2/2) >= 6.
  ```

  The final inequality follows directly from the parity of
  `s+t_1+t_2=12`.

Every case contradicts `alpha(H)<=5`.  Therefore `m>=11`.

### Equality

Suppose `m=11`.  One component is a tree and two components consist of one
unicyclic component and one tree; the same floor/ceiling bounds give
independence number at least six.  Thus `k=3` and total cycle rank two.

If one component is bicyclic and the other two are trees, classify the
bicyclic 2-core as a theta, figure-eight, or dumbbell.  Except when a
dumbbell has two vertex-disjoint odd cycles, one vertex meets every odd
cycle.  Deleting that vertex leaves a bipartite graph and gives the
bicyclic component of order `s` an independent set of size at least
`floor(s/2)`; the two tree bounds again total at least six.  In the remaining
dumbbell case, triangle-freeness makes both odd cycles have length at least
five.  The two other components are nonempty, so orders force a ten-vertex
bicyclic component made from two 5-cycles joined by one edge and two
isolated tree components.  Two independent vertices can be chosen on each
cycle while avoiding the joining endpoints; adding the two isolated
vertices again gives six.

The only remaining cycle-rank distribution is `(1,1,0)`.  The
floor/ceiling sum can fall to five only when both unicyclic components have
odd order and are non-bipartite and the tree has even order.  Each
triangle-free non-bipartite unicyclic component contains an odd cycle of
length at least five.  The orders therefore force `(5,5,2)`, and the
components are exactly `C5,C5,K2`.  This graph directly has 11 edges,
independence number five, and no triangle.

This independently reproduces both claims in Lemma 5.1.  In particular,
the delicate bicyclic branch contains no missing core type.

## 2. Independent exhaustive counterexample hunt

The new checker
[`checks/double_saturation_reaudit/check_trianglefree_12_enumerator.py`](checks/double_saturation_reaudit/check_trianglefree_12_enumerator.py)
does not import or invoke the supplied profile checker.  It uses NetworkX
3.5 only for one representative of each unlabelled tree and uses separate
bitset code for edge addition, triangle tests, exact independence numbers,
graph6 decoding, and invariant checks.

Every connected unicyclic graph is obtained by adding one nonedge to a
spanning tree; every connected bicyclic graph is obtained by adding two.
Therefore adding every one- and two-nonedge set to every unlabelled tree
representative is exhaustive up to isomorphism, although it intentionally
contains duplicates.  The tree counts through order 12 are

```text
1,1,1,2,3,6,11,23,47,106,235,551,
```

which independently guards the generator coverage.  The run examined

```text
16,440 raw unicyclic spanning-tree extensions,
10,588 triangle-free unicyclic extensions,
90,852 raw bicyclic spanning-tree extensions,
31,513 triangle-free bicyclic extensions.
```

It also brute-forced all `2^15=32,768` labelled six-vertex graphs: 5,789
were triangle-free and none had independence number at most two, independently
checking the `R(3,3)<=6` input.  The exact component aggregation found

```text
150 edge-at-most-10 profiles; 0 with alpha<=5,
109 edge-equal-11 profiles; unique normalized survivor
  orders (2,5,5), cycle ranks (0,1,1), alpha 5.
```

At order five, every minimum-alpha triangle-free unicyclic survivor has
degree sequence `(2,2,2,2,2)`, so it is `C5`; the order-two tree is uniquely
`K2`.  Thus the exact search confirms both the lower bound and equality
uniqueness without using the supplied proof checker.

Reproduce from the repository root with

```powershell
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\double_saturation_reaudit\check_trianglefree_12_enumerator.py
```

The command exited zero and printed `status: VERIFIED`.

## 3. Combination with the audited saturation bound

I rechecked the short dependency chain rather than treating `e(U)<=10` as
an opaque input.  Under the standing row-D hypotheses:

1. For each of the five size-five spokes `B_c`, domination of the 12
   vertices of `U` and the singleton-fibre cap give
   `e(U,B_c)>=19`.
2. If `r=e(U,{w})`, then `r<=7` because `w` already has its two clique
   neighbours and `Delta(G)<=9`.
3. The two spokes containing `w` count every `U-w` edge twice, whereas the
   actual `U` degree sum counts it once.  Hence

   ```text
   sum_{u in U} d_G(u) = 2e(U)+sum_c e(U,B_c)-r.
   ```

4. The twelve degree-nine budgets give

   ```text
   108 >= 2e(U)+5*19-7 = 2e(U)+88,
   ```

   and therefore `e(U)<=10`.

The shared-`w` correction has the correct sign, and the lower bound uses the
largest permitted `r`, so no hidden disjoint-spoke assumption is introduced.
This agrees with the preserved point-in-time independent PASS audit.

## 4. Exact remaining catalogue conditionality

Row D has three residuals `F=G[U union A_c]` of order 17 and beta five.
Lemma 5.1 of `ORDER41_K5_RESIDUAL_OVERLAP.md` proves that each is
triangle-free conditional on completeness of the pinned Ramsey
`(3,6;17)` catalogue.  It follows that the induced common core `G[U]` is
triangle-free.  Also `alpha(U)<=5`, since every independent set is
admissible and `U` is induced in a beta-five residual.  The independently
verified sparse lemma gives `e(U)>=11`, contradicting `e(U)<=10`.

The independent graph6 decoder in the re-audit checker verifies the exact
pinned SHA-256, seven records, order 17, triangle-freeness, independence
number five for every record, edge histogram `{40:2,41:3,42:2}`, and minimum
degree four for every record.  These are the local catalogue properties used
by the residual lemma.  What remains external is **completeness**: that the
seven records exhaust all Ramsey `(3,6;17)` graphs up to isomorphism.

No dominating-partition enumeration, common-core isomorphism calculation,
automorphism closure, aligned cross-degree pattern, 17-survivor list, or
order-16 catalogue is used in this strengthened route.  The repaired D17
enumeration remains independent corroboration only.

## 5. Verdict and minor observation

**PASS.**  There is no analytic or computational counterexample to the
strengthened lemma, its equality statement, or its use in row D.  The source
states the external premise and claim boundary accurately.

One purely editorial issue is nonblocking: the strengthened source uses the
display label `(7)` once for the sparse lower bound and again in the later
D17-corroboration section.  No argument refers ambiguously to the duplicated
number, so this does not affect the verdict or require a source edit for the
bound audit here.
