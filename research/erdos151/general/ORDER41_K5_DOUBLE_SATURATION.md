# Order 41, maximum `K5`, row D: double-spoke saturation

**Status (2 August 2026; strengthened after the point-in-time PASS audit).**
The singleton-fibre and degree-budget argument below is **PROVED** under the
standing row-D hypotheses.  A new elementary lemma says that a triangle-free
12-vertex graph with independence number at most five has at least 11 edges.
Consequently row D is excluded conditional only on the already proved,
catalogue-conditional fact that its order-17 residuals are triangle-free;
the repaired 17-core overlap enumeration is no longer needed for the logical
exclusion.  It remains independent finite corroboration.  This is not a
whole-graph search and makes no claim about the full order-41 problem or
Erdos problem #151.  The audit remains a binding of the pre-strengthening
source; the post-audit boundary is recorded in
[`ORDER41_K5_DOUBLE_SATURATION_ADDENDUM.md`](ORDER41_K5_DOUBLE_SATURATION_ADDENDUM.md).

The finite input is the repaired package
[`ORDER41_K5_RESIDUAL_OVERLAP.md`](ORDER41_K5_RESIDUAL_OVERLAP.md), bound by
the PASS-after-repair
[`ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.md`](ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.md).
The immutable original
[`FAIL audit`](ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.md) remains the authority on
the defect that changed the row-D count from 12 to 17.  No file in that
package is altered here.

## 1. Standing row D

Fix the maximum clique

```text
M = {p,q,c_3,c_4,c_5}.
```

The outside vertices split as `U`, a vertex `w`, and five fans:

```text
|U|=12,
N_M(w)={p,q},
|A_p|=|A_q|=4,
|A_c|=5 for c in {c_3,c_4,c_5},
N_M(a)={c} for a in A_c,
N_M(u)=empty for u in U.
```

Every vertex of `M` has degree nine.  Define the five outside spokes

```text
B_p = A_p union {w},
B_q = A_q union {w},
B_c = A_c for c in {c_3,c_4,c_5}.
```

Thus `|B_c|=5`,

```text
N_G(c)=(M-{c}) union B_c,
```

and every `B_c` dominates `U`.  Also `beta(G)=9`, so
`Delta(G)<=9` because every open neighbourhood is admissible.  The five
order-16/order-17 clique residuals have beta five; this will be used only
for the optional unconditional lower bound on `e(U)` in Section 4.

## 2. PROVED: singleton fibres in all five spokes

Fix `c in M` and `a in B_c`, and put

```text
P_c(a) = {u in U : N(u) intersect B_c = {a}}.
```

**Lemma 2.1.**  `|P_c(a)|<=1`.

**Proof.**  Put `S_c=N_G(c)`.  It is an admissible nine-set: every clique
inside it extends by `c`.  Since `beta(G)=9`, it is maximum.

For `u in P_c(a)`, the ten-set `S_c union {u}` must contain an
ambient-maximal nontrivial clique.  Such a clique cannot lie in `S_c`, and
`u` is anticomplete to `M` with unique neighbour `a` in `B_c`.  The witness
is therefore the edge `ua`; in particular, `ua` is ambient-maximal.

If distinct `u,v` belonged to `P_c(a)`, maximality of `ua` would force
`uv` to be absent, since `v` is adjacent to `a`.  Then

```text
(S_c-{a}) union {u,v}
```

would be an admissible ten-set.  Indeed, `u` and `v` are nonadjacent and
anticomplete to `S_c-{a}`, while no clique contained in that latter set is
ambient-maximal because it is already contained in the admissible set
`S_c`.  This contradicts `beta(G)=9`.  QED.

### The shared-`w` cases

No disjoint-spoke assumption is hidden in Lemma 2.1.  For example, if
`c=p` and `a=w`, then `N(u) intersect S_p={w}`: vertices of `U` have no
neighbours in `M`, including `q`.  If two such vertices existed, `uw` would
be ambient-maximal, they would be nonadjacent, and removing `w` from
`N(p)` before inserting them would give the forbidden admissible ten-set.
The edge `qw` inside `N(p)` causes no exception: after `w` is removed, both
inserted vertices are anticomplete to the remaining `M-{p}`.  The argument
at `q` is identical.

A vertex of `U` may be the unique-`w` vertex for both spokes.  That does not
invalidate either pointwise cap or the cut lower bounds below; it matters
only when the two cuts are summed, where the duplicated `U-w` edges are
corrected explicitly.

## 3. PROVED: every five-vertex spoke costs at least 19 edges

Write

```text
e_c = e_G(U,B_c).
```

For fixed `c`, domination gives every one of the twelve vertices of `U` at
least one neighbour in `B_c`.  If `s_c` of them have exactly one, Lemma 2.1
injects those vertices into the five choices of their unique neighbour.
Thus `s_c<=5`, and

```text
e_c >= s_c + 2(12-s_c) = 24-s_c >= 19.             (1)
```

This conclusion is unconditional under the standing row-D saturation
package; no Ramsey catalogue is used.

## 4. PROVED: exact accounting of the shared spoke

Put

```text
e_U = e(G[U]),       r = |N_G(w) intersect U|.
```

Since `w` already has the two neighbours `p,q` and `Delta(G)<=9`,

```text
r<=7.                                                       (2)
```

Let `f_c=e(U,A_c)`.  The two spokes containing `w` satisfy

```text
e_p=f_p+r,       e_q=f_q+r,
```

while `e_c=f_c` for the other three.  Therefore

```text
sum_c e_c = sum_c f_c + 2r.                                (3)
```

The actual sum of the global degrees of vertices in `U` counts every
`U-w` edge only once.  Hence (3) gives the exact identity

```text
sum_{u in U} d_G(u)
  = 2e_U + sum_c f_c + r
  = 2e_U + sum_c e_c - r.                                  (4)
```

Combining the twelve degree-nine budgets, (1), and (2),

```text
108 >= 2e_U + sum_c e_c-r
    >= 2e_U + 5*19-7
     = 2e_U+88.
```

Thus the simultaneous five-spoke saturation has the sharp consequence

```text
e(U)<=10.                                                    (5)
```

For context, the residual equality `beta=5` gives `alpha(U)<=5`.  Turan's
theorem applied to the `K6`-free complement of this 12-vertex graph yields

```text
e(U) >= C(12,2)-ex(12,K6) = 66-57 = 9.
```

So the analytic row-D package alone narrows the common core to

```text
e(U) in {9,10}.                                              (6)
```

The upper bound (5) is used both in the short triangle-free finish below and
in the independent corrected-overlap corroboration.

## 5. PROVED: the exact sparse triangle-free lemma

**Lemma 5.1.**  If `H` is triangle-free, has order 12, and
`alpha(H)<=5`, then

```text
e(H)>=11.                                                    (7)
```

Equality holds if and only if

```text
H is C5 disjoint-union C5 disjoint-union K2.                 (8)
```

**Proof of the lower bound.**  Let `k` be the number of components.  A
triangle-free component with independence number one has order at most two;
one with independence number two has order at most five, by `R(3,3)=6`.
Since component independence numbers are positive and sum to at most five,
four components have total order at most `5+2+2+2=11`, and five components
have total order at most ten.  Hence `k<=3`.

Write

```text
mu = e(H)-12+k
```

for the total cyclomatic number.  A tree of order `s` has an independent
set of order at least `ceil(s/2)`.  A connected unicyclic graph of order
`s` has an independent set of order at least `floor(s/2)`: delete one cycle
vertex and take a larger bipartition class of the resulting forest.

Suppose `e(H)<=10`.

- If `k=1`, connectedness already gives `e(H)>=11`.
- If `k=2`, then `mu<=0`, so both components are trees and their union has
  an independent six-set.
- If `k=3`, then `mu<=1`.  If `mu=0`, the graph is a forest.  If `mu=1`,
  exactly one component is unicyclic and the other two are trees.  For
  component orders `s,t_1,t_2` summing to 12,

  ```text
  alpha(H) >= floor(s/2)+ceil(t_1/2)+ceil(t_2/2) >= 6.
  ```

  The last inequality is just parity: if `s` is odd, at least one of
  `t_1,t_2` is odd and its ceiling compensates for the floor; if `s` is
  even, there is no loss.

Every case contradicts `alpha(H)<=5`, proving (7).

**Equality.**  Now let `e(H)=11`.  The same bounds exclude one component
(a tree) and two components (one unicyclic component plus one tree).  Thus
`k=3` and `mu=2`.

First suppose one component is bicyclic and the other two are trees.  The
2-core of a connected bicyclic graph is a theta, a figure-eight, or a
dumbbell.  In the first two types, and in a dumbbell with at most one odd
core cycle, one vertex meets every odd cycle.  Removing it leaves a
bipartite graph, so the bicyclic component of order `s` has independence
number at least `floor(s/2)`; the two tree bounds and the same parity
argument give an independent six-set.  In the remaining dumbbell case
there are two vertex-disjoint odd cycles.  Triangle-freeness makes each
cycle have order at least five.  Since two nonempty tree components also
exist and the total order is 12, the bicyclic component has order ten, the
two trees are isolated vertices, and its core consists of two 5-cycles
joined by one edge.  Choosing two vertices from each cycle while avoiding
the joining endpoints, then adding the two isolated vertices, again gives
an independent six-set.  The bicyclic distribution is impossible.

The remaining distribution is two unicyclic components and one tree.  The
floor/ceiling bound can be five only when both unicyclic component orders
are odd and the tree order is even.  Equality also requires each unicyclic
component to be non-bipartite; otherwise its bipartition gives the missing
extra vertex.  Each therefore contains an odd cycle, of order at least five
by triangle-freeness.  The nonempty even-order tree has order at least two.
The three orders sum to 12, so they are exactly `5,5,2`.  The components are
therefore `C5,C5,K2`, which directly has 11 edges and independence number
five.  QED.

## 6. CATALOGUE-CONDITIONAL PROVED: row D is impossible without D17

The pinned catalogue is used here only through the previously proved
Lemma 5.1 of
[`ORDER41_K5_RESIDUAL_OVERLAP.md`](ORDER41_K5_RESIDUAL_OVERLAP.md):
conditional on completeness of the seven Ramsey `(3,6;17)` records, every
order-17 residual with beta at most five is triangle-free.

Row D has three such full residuals `G[U union A_c]`.  Hence `G[U]` is
triangle-free.  It also has `alpha(U)<=5`, because it is induced in a
residual of beta five.  Lemma 5.1 gives

```text
e(U)>=11,
```

contradicting the unconditional saturation bound `e(U)<=10` in (5).

**Theorem 6.1.**  Conditional on completeness of the pinned Ramsey
`(3,6;17)` catalogue, row D does not occur.  No dominating-partition,
common-core, automorphism, or 17-survivor enumeration enters this proof.

The exact external dependency remains

```text
experiments/erdos128/r36_17.g6
SHA-256 3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361
7 records
```

The repository verifies these bytes and the catalogue properties used in
the order-17 residual lemma.  It does not itself prove external catalogue
completeness.

## 7. CATALOGUE-CONDITIONAL CHECKED: independent D17 corroboration

The repaired overlap calculation uses the three full order-17 residuals.
Conditional on the premise that the pinned seven-record Ramsey `(3,6;17)`
catalogue is complete, those residuals are catalogue graphs.  After all
dominating five-subsets, exact common-`U` isomorphisms, automorphisms, aligned
cross-degree patterns, and the necessary capacity for the two remaining
spokes are imposed, exactly 17 common-core classes survive.  Every one has

```text
e(U) in {20,21,22}.                                         (7)
```

The pinned catalogue dependency is

```text
experiments/erdos128/r36_17.g6
SHA-256 3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361
7 records
```

The finite repaired enumeration is bound by
`ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.json`; its relevant corrected
totals are `1963` automorphism-closed patterns and `17` row-D cores.  The
repository checks the file, hashes, graph properties, and enumeration.  It
does not itself prove the external completeness premise.

Equations (5) and (7) are incompatible.  Equivalently, even the most
favourable catalogue core and the largest possible shared correction give

```text
sum_{u in U} d_G(u) >= 2*20 + 5*19 - 7 = 128 > 108.
```

This reproduces the same row-D contradiction by a logically independent
finite route.  It is retained as corroboration, not as a premise of Theorem
6.1.

## 8. CHECKED: isolated finite guards

The standard-library script
[`checks/double_saturation/check_double_saturation.py`](checks/double_saturation/check_double_saturation.py)
checks the shared-`w` identity on 16,384 dummy integer states and checks the
final bounds for every `e_U in {20,21,22}` and `0<=r<=7`.  It reports

```text
status: CHECKED
minimum U-degree sums: e20 -> 128, e21 -> 130, e22 -> 132
available U-degree budget: 108
feasible states: 0
```

Reproduce from the repository root with

```powershell
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\double_saturation\check_double_saturation.py
```

This is an arithmetic and double-counting sanity check, not a graph search,
catalogue-completeness proof, or UNSAT certificate.

The standard-library component-profile checker
[`checks/double_saturation_trianglefree/check_trianglefree_12_profile.py`](checks/double_saturation_trianglefree/check_trianglefree_12_profile.py)
exhausts the component-order, cyclomatic-number, and parity profiles in
Lemma 5.1 and directly checks the equality construction.  It reports

```text
status: CHECKED
sparse component profiles checked: 150
sparse profiles with alpha at most 5: 0
equality order profile: (2,5,5)
equality graph: C5 disjoint-union C5 disjoint-union K2
equality graph invariants: n=12, e=11, triangles=0, alpha=5
```

Reproduce it with

```powershell
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\double_saturation_trianglefree\check_trianglefree_12_profile.py
```

This is an exhaustive guard for the finite proof profiles, not an
enumeration of all labelled or unlabelled 12-vertex graphs.  The bicyclic
2-core dichotomy remains an analytic proof step.

## 9. CONJECTURAL / claim boundary

There is no conjectural combinatorial step after accepting the explicitly
stated catalogue-completeness premise.  Unconditionally, this note proves
the singleton-fibre bound, the five cut bounds, `e(U)<=10`, and the exact
12-vertex triangle-free lemma.  Conditional only on the previously proved
catalogue-dependent triangle-freeness of the size-17 residuals, it excludes
row D.  The repaired D17 route remains independent corroboration but is no
longer a dependency of the exclusion.

The point-in-time PASS audit binds the earlier source hash and is not edited;
the strengthening and new hashes are recorded in the addendum.  This note
does not alter the overlap package, run whole-graph CEGAR, or make any Git,
publication, priority, full order-41, or full-solution claim.
