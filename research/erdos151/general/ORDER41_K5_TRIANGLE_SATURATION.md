# Order 41, maximum `K5`, row T: triangle-saturation simplifier

**Status (2 August 2026): PROVED under the standing row-T package and the
catalogue-conditional triangle-freeness of `U`.**

This note gives an analytic replacement for the exact `10 -> 0` overlap
enumeration in row T.  It uses the strengthened sparse triangle-free lemma,
four maximum-neighbourhood singleton-fibre cuts, the deficient-fan clique
condition, and a residual maximal-edge transversal.  Conditional on the
published completeness of the pinned seven-record Ramsey `(3,6;17)`
catalogue, it excludes row T without enumerating dominating fan partitions,
common-core isomorphisms, or aligned cross-degree patterns.

It does not edit or invalidate the repaired overlap computation, which
remains independent corroboration.  It makes no claim about rows R or D, the
full order-41 problem, Erdős problem #151, catalogue completeness, Git,
publication, novelty, or priority.

## 1. Standing row T and dependency boundary

Fix a maximum clique `M` of order five.  The row-T profile gives

```text
V(G)=M disjoint-union U disjoint-union A_0 ... disjoint-union A_4,
|U|=12,
|A_0|=4,                  d_G(c_0)=8,
|A_i|=5 for 1<=i<=4,      d_G(c_i)=9,
N_M(u)=empty for u in U,
N_M(a)={c_i} for a in A_i,
beta(G)<=9,
beta(G[U union A_i])=5 for every i.
```

For every full fan `A_i`, `1<=i<=4`, the degree-nine neighbourhood

```text
N_G(c_i)=(M-{c_i}) union A_i
```

is an admissible nine-set and hence forces `beta(G)=9`.  Saturation makes
each full `A_i` dominate `U`.  At the deficient fan put

```text
D_0={u in U:N(u) intersect A_0=empty}.
```

The audited row-T argument proves that `D_0` is a clique.

The only catalogue-dependent input used below is:

```text
G[U] is triangle-free.                                      (T0)
```

The residual package proves (T0) conditional on completeness of the pinned
seven Ramsey `(3,6;17)` records: every full order-17 residual is then a
triangle-free catalogue graph, and `U` is its induced 12-vertex subgraph.
The exact overlap enumeration and its counts `4368`, `786`, and `1963` are
not used.  The exact residual equality `beta=5`, profile data, domination,
and `D_0` clique statement are unconditional under the standing
order-41 `beta<=9`, `omega=5` reduction.

## 2. Four full fans each cost at least 19 edges

Fix a full fan `A_i`, a vertex `a in A_i`, and define

```text
P_i(a)={u in U:N(u) intersect A_i={a}}.
```

**Lemma 2.1.** `|P_i(a)|<=1`.

**Proof.**  Put `S_i=N_G(c_i)`.  Every nontrivial clique in `S_i` extends
by `c_i`, so `S_i` is ambient-admissible; it has order nine and is maximum.
For `u in P_i(a)`, the ten-set `S_i union {u}` is not admissible in `G`.
An ambient-maximal witness cannot lie in `S_i`, and `a` is the only
neighbour of `u` in that set.  Hence the witness is the edge `ua`, which is
an ambient-maximal 2-clique of `G`.

If distinct `u,v` had the same anchor `a`, then `uv` cannot be present,
because the triangle `u,a,v` would extend `ua`.  If `uv` is absent, both
vertices are isolated in

```text
(S_i-{a}) union {u,v},
```

while every remaining clique extends by `c_i`.  This would be an
ambient-admissible ten-set, again impossible.  QED.

Let `s_i` be the number of vertices of `U` with exactly one neighbour in
`A_i`.  Domination and Lemma 2.1 give `s_i<=5`, so

```text
e(U,A_i)>=s_i+2(12-s_i)=24-s_i>=19             (1)
```

for each of the four full fans.

This argument legitimately applies only to the degree-nine full fans.  No
singleton-fibre cap is asserted for `A_0`, because `N(c_0)` has order eight
and is not known to be a maximum admissible set.

## 3. The deficient fan costs at least 10 edges

If distinct `u,v in D_0` were nonadjacent, they would be isolated in

```text
N(c_0) union {u,v}.
```

This is a ten-set: `|N(c_0)|=8`.  Every other clique in it lies in
`N(c_0)` and extends by `c_0`, so the set would be ambient-admissible,
contradicting `beta(G)<=9`.  Thus `D_0` is a clique, as in the residual
package.

By (T0), `U` is triangle-free, so `|D_0|<=2`.  Every vertex outside `D_0`
has at least one neighbour in `A_0`; consequently

```text
e(U,A_0)>=12-|D_0|>=10.                         (2)
```

## 4. Sparse triangle-free rigidity

An independent set in a residual is residual-admissible.  Since `U` is
induced in every beta-five residual,

```text
alpha(U)<=5.                                             (3)
```

We use the following exact sparse lemma, independently reconstructed here.

**Lemma 4.1.**  If `H` is triangle-free, has order 12, and
`alpha(H)<=5`, then `e(H)>=11`.  Equality holds only for

```text
C5 disjoint-union C5 disjoint-union K2.                  (4)
```

**Proof.**  Let `k` be the number of components.  A triangle-free component
with independence number one has at most two vertices; one with independence
number two has at most five vertices by `R(3,3)=6`.  Component independence
numbers are positive and sum to at most five.  Four components therefore
have at most `5+2+2+2=11` vertices and five have at most ten, so `k<=3`.

Write `mu=e(H)-12+k` for the total cyclomatic number.  A tree of order `s`
has independence number at least `ceil(s/2)`.  A connected unicyclic graph
of order `s` has independence number at least `floor(s/2)`: delete one
cycle vertex and take a larger bipartition class of the remaining forest.

If `e(H)<=10`, then `k=1` already requires at least 11 edges; for `k=2`,
both components are trees; and for `k=3`, the graph is a forest or has one
unicyclic component and two trees.  In the latter case, for component orders
`s,t_1,t_2` summing to 12,

```text
alpha(H)>=floor(s/2)+ceil(t_1/2)+ceil(t_2/2)>=6,
```

with the final unit supplied by parity.  The forest cases are at least as
strong.  This proves `e(H)>=11`.

Now suppose `e(H)=11`.  One component is a 12-vertex tree and two components
have one unicyclic component plus one tree; both cases have an independent
six-set.  Hence `k=3` and `mu=2`.

If the cycle-rank distribution is `(2,0,0)`, the bicyclic component has a
theta, figure-eight, or dumbbell 2-core.  Except when a dumbbell has two
vertex-disjoint odd cycles, one vertex meets every odd cycle; deleting it
makes the component bipartite and gives an independent set of order at least
`floor(s/2)`.  The two tree bounds and parity then give an independent
six-set.  In the exceptional dumbbell, triangle-freeness makes both odd
cycles have order at least five.  The two other components are nonempty and
the total order is 12, so the bicyclic component consists of two 5-cycles
joined by an edge and the two trees are isolated vertices.  Two independent
vertices can be chosen in each cycle while avoiding the joining endpoints;
together with the isolates this again gives six.  Thus `(2,0,0)` is
impossible.

The remaining distribution is `(1,1,0)`.  The floor/ceiling bound can be
only five precisely when both unicyclic orders are odd and the tree order is
even.  Each unicyclic component must also be non-bipartite, or its
bipartition supplies the missing unit.  Its odd cycle has order at least
five, while the nonempty even tree has order at least two.  The orders must
therefore be `5,5,2`, forcing exactly `C5,C5,K2`.  This graph has 11 edges
and independence number five.  QED.

Applying Lemma 4.1 to `U` using (T0) and (3) gives

```text
e(U)>=11.                                               (5)
```

## 5. Equality forces `U=C5+C5+K2`

Vertices of `U` are anticomplete to `M`, and row T has no double-neighbour
vertex.  Their exact global degree sum is therefore

```text
sum_{u in U}d_G(u)
 =2e(U)+e(U,A_0)+sum_{i=1}^4 e(U,A_i)
 <=12*9=108.                                           (6)
```

The independent lower bounds (1), (2), and (5) give

```text
2*11+10+4*19=108.                                      (7)
```

Thus every inequality in (6)–(7) is equality.  In particular,

```text
e(U)=11,
e(U,A_0)=10,
e(U,A_i)=19 for 1<=i<=4,
d_G(u)=9 for every u in U.
```

The equality case of Lemma 4.1 now forces

```text
G[U]=C5 disjoint-union C5 disjoint-union K2.            (8)
```

## 6. Residual maximal-edge transversal

Fix any vertex `a` in any full fan `A_i` and put

```text
F=G[U union A_i],
E_a={u in U:{a,u} is an inclusion-maximal 2-clique of F}.
```

This definition is deliberately residual: `beta(F)` concerns maximal
cliques of `F`, not ambient maximal cliques of `G`.

**Lemma 6.1.** `E_a` is independent in `G[U]`.

**Proof.**  If adjacent `u,v` both belonged to `E_a`, then membership gives
the edges `au,av`, so `a,u,v` is a triangle of `F`.  Neither incident edge
could then be an inclusion-maximal 2-clique of `F`.  QED.

**Lemma 6.2.**  Every independent `E subseteq V(C5 disjoint-union C5
disjoint-union K2)` is disjoint from some maximum independent 5-set.

**Proof.**  In each `C5`, `E` uses at most two vertices.  If it uses at most
one, the remaining graph plainly has an independent 2-set; if it uses two,
the remaining three vertices do not form a triangle and hence contain a
nonadjacent pair.  In the `K2`, independence lets `E` use at most one
endpoint, so choose the other.  The two pairs and one endpoint form the
required independent 5-set.  QED.

Apply Lemma 6.2 to `E_a` and choose a maximum independent set `I` of `U`
with `I intersect E_a=empty`.  The six-set `I union {a}` is admissible in
`F`.  Indeed, `I` is independent, so every nontrivial clique contained in
the six-set is an edge `au` with `u in I`.  If that edge is present,
`u notin E_a` says exactly that it is not an `F`-maximal 2-clique.  No larger
clique can be contained because `I` is independent.  Therefore

```text
beta(F)>=6,
```

contradicting the standing `beta(F)=5`.

There is no ambient/residual maximality reversal here.  Section 2 uses
ambient maximality in `G` to derive the full-fan cut.  Section 6 separately
uses maximality in `F`, exactly the graph whose beta value supplies the
contradiction.  It never infers that an `F`-maximal edge is ambient-maximal,
or conversely.

## 7. The conditional row-T theorem

**Theorem 7.1.**  Under the standing row-T hypotheses and (T0), row T is
impossible.  Consequently, conditional on completeness of the pinned seven
Ramsey `(3,6;17)` records, row T is excluded without the exact residual
overlap enumeration.

The catalogue premise enters only through (T0).  The following are not
premises of this proof:

- enumeration of 4,368 dominating partitions;
- classification into 786 common-`U` isomorphism classes;
- closure of 1,963 aligned patterns under automorphisms; or
- the old or repaired `10 -> 0` finite T count.

Those computations remain valid, repaired, independently re-audited
corroboration.

## 8. Isolated finite checker

The standard-library checker
[`checks/triangle_saturation/check_triangle_saturation.py`](checks/triangle_saturation/check_triangle_saturation.py)
has SHA-256

```text
a495e66dff787f81fe00a5f4f6ad789010ba32efdcb5b5a210cd3c6d557423be
```

and replays with

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\triangle_saturation\check_triangle_saturation.py
```

It prints

```text
status: CHECKED
full_fan_cut_minimum: 19
full_fan_equality_assignments: 950400000000
arithmetic_states: 1
forced_state: e(U)=11, full_cuts=(19,19,19,19), deficient_cut=10
U_type: C5 disjoint-union C5 disjoint-union K2
U_invariants: e=11, triangles=0, alpha=5
D0_cliques: 24, maximum_D0: 2
independent_sets_in_U: 363
maximum_independent_5_sets: 50
independent_sets_hitting_all_maximum_sets: 0
```

The checker exhausts the full-fan set system, scalar equality state, every
independent endpoint set, and every maximum independent set of the forced
`U`.  It does not enumerate all triangle-free graphs of order 12, prove the
bicyclic 2-core classification, verify the row-T reduction, or prove
catalogue completeness.  Those are analytic or explicit external-premise
steps above.

For comparison, the separate sparse-profile guard
`checks/double_saturation_trianglefree/check_trianglefree_12_profile.py` at
SHA-256
`68a73ad39d1a4f3857b512b23bb85b90b3cfc73a58784f4c82d5a5e53eb1a325`
checks the component-order and parity profiles of Lemma 4.1.  It is
corroboration, not an all-graph enumeration.

## 9. Exact dependency hashes

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_RESIDUAL_OVERLAP.md` | `880b2de61369c2539218ec027b9757b9f8da5b98dd8243a9e06c11e0a09d07ca` |
| immutable `ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.md` | `bde66a3d221f5e1762e218cc7b40de70ca690e019c3c99c93a1b0cd1d2120567` |
| immutable `ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.json` | `6f3411401846cc7304264c0025da252f4421467c15190a19572b94b270a19165` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REAUDIT.md` | `05152283f4377073664d2d8e33a922c6cd49ed7aa32ce69a2d07a25bdaee97a9` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REAUDIT.json` | `e5e35724f2d031e78b130f20fc022cc530675aac716cbcca4696b70bcdee7d3c` |
| strengthened `ORDER41_K5_DOUBLE_SATURATION.md` | `8353be6fde22d8e6edeb455187169b5eae4f6093ae971debcae353e7debddebd` |
| `ORDER41_K5_DOUBLE_SATURATION_ADDENDUM.md` | `96af57c9754f8b8be871c89787845b7ec1146c91863793df42dba6a63d7ae4d4` |
| sparse-profile checker | `68a73ad39d1a4f3857b512b23bb85b90b3cfc73a58784f4c82d5a5e53eb1a325` |
| isolated checker for this note | `a495e66dff787f81fe00a5f4f6ad789010ba32efdcb5b5a210cd3c6d557423be` |
| `experiments/erdos128/r36_17.g6` | `3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361` |

The pinned file has seven records and the stated hash, but local hash and
property checks do not prove the external published completeness premise.
