# Analytic exclusion of the Ramsey jumps 28 and 36

**Status (2 August 2026): independently reconstructed and verified.**  This
proves the Erdos #151 inequality through order 39, not the full problem.
Three independent adversarial proof passes found no defect, and two finite
coloring inputs were exhaustively checked.  No literature-priority claim is
made.

For a graph `G`, write `beta(G)` for the largest vertex set containing no
nontrivial maximal clique of `G`.  This note uses the campaign's proved
bound through order 27, induced-subgraph monotonicity, the clique-residual
lemma, and the Folkman reduction.  It also uses A. Bikov's published theorem
that a minimal `(3,3)`-Ramsey graph with clique number three has minimum
degree at least eight.  The exact specialization of Bikov's theorem needed
here has also been exhaustively rechecked by a small independent program.

## Two coloring lemmas

### Cone lemma

Let the edges of a graph `L` on at most four vertices be colored red and
blue without a monochromatic triangle.  If `L` is not `K4`, one can assign a
red or blue color to every vertex of `L` so that no edge `xy` of color
`gamma` has both endpoint colors equal to `gamma`.

The vertex colors can be regarded as colors of the spokes from the apex of a
cone over `L`; the conclusion says that the coloring extends over those
spokes without creating a monochromatic triangle.

**Proof.** Repeatedly delete any vertex of degree at most one.  After an
assignment on the smaller graph, the deleted vertex has at most one
forbidden color, so the assignment extends.  The nonempty irreducible graphs
on at most four vertices, other than `K4`, are `C3`, `C4`, and `K4-e`.

- On `C3`, two link edges have one color and the third has the other.  Give
  the common endpoint of the same-colored pair the other vertex color, and
  give the remaining two vertices the first color.
- On `C4`, use opposite vertex colors on its two bipartition classes.
- On `K4-ab`, let the other vertices be `c,d`.  Give `c,d` the color opposite
  to the edge `cd`, and give `a,b` the color of `cd`.

Every link edge is safe in each case.

### Matching-prescription lemma

Any red/blue prescriptions on a matching of the edges of `K4` extend to an
edge-coloring of `K4` with no monochromatic triangle.

**Proof.** For two prescribed opposite edges of the same color, give the
other four edges the opposite color.  If the prescribed edges have different
colors, say `12` is red and `34` is blue, set `13,24` red and `14,23` blue.
Zero or one prescription extends to the same-color two-edge case.

The exhaustive standard-library check `check_order28_36_coloring.py`
independently verifies both finite lemmas; its counts and script hash are in
`check_order28_36_coloring.result.json`.

## Excluding order 28

Assume that `G` is a least-order counterexample on 28 vertices.  Put
`h=H(28)=8`.  The already proved reductions give

- `beta(G)<=7` and `Delta(G)<=7`;
- `omega(G)<=4` by the clique-residual lemma;
- `G -> (3,3)` by the Folkman reduction.

Choose an inclusion-minimal `(3,3)`-Ramsey subgraph `Q` of `G`.  If
`omega(Q)=3`, Bikov's theorem gives `delta(Q)>=8`, contradicting
`Delta(Q)<=Delta(G)<=7`.  Hence `Q`, and therefore `G`, contains a clique

`C={c1,c2,c3,c4}`.

For reproducibility, the Bikov input can be replaced here by the exact finite
check in `checks/check_k4free_core_degree7.py`.  If `Q` were `K4`-free, the
link of any vertex would be triangle-free.  A good coloring of `Q-v`, plus a
safe spoke assignment for its signed link, would extend to a good coloring
of `Q`.  It is enough to check labelled maximal triangle-free graphs on seven
vertices: any smaller triangle-free link, padded with isolated vertices,
extends to one, and a spoke assignment restricts back to the original link.
The checker exhausts all 1,743 such graphs and all 1,348,032 edge signings
and finds no obstruction.

For `i=1,2,3,4`, put

`Ai=N_G(ci) - C`.

Since each `ci` already has three neighbors in `C`, `|Ai|<=4`.

### Boundary inequalities

For distinct `i,j`, the set of the 24 vertices outside `C` anticomplete to
`{ci,cj}` has size `24-|Ai union Aj|`.  If this were at least
`R(3,6)=18`, the through-order-27 theorem would give an admissible six-set
`S` in its induced graph.  Induced monotonicity makes `S` admissible in `G`.
Then `{ci,cj} union S` would be an admissible eight-set: the edge `cicj`
extends in `C`, there is no mixed clique, and `S` contains no ambient maximal
clique.  This is impossible, so

`|Ai union Aj|>=7`.                                      (1)

Similarly, for three distinct indices, a set of at least `R(3,5)=14`
outside vertices anticomplete to the three clique vertices would supply an
admissible five-set.  Combining it with the triple, which extends by the
fourth vertex of `C`, would give an admissible eight-set.  Hence

`|Ai union Aj union Ak|>=11`.                            (2)

Equations (1)--(2) and `|Ai|<=4` completely control the overlaps.  Every
`Ai` has size at least three, at most one has size three, a size-three set is
disjoint from every other `Ai`, and then (2) makes all the other sets
mutually disjoint.  If all four sets have size four, (1) gives pairwise
intersection sizes at most one.  Inclusion-exclusion in (2) shows that any
three sets contain at most one intersecting pair.  Thus in every case

> the pairs `ij` for which `Ai intersect Aj` is nonempty form a matching,
> and every such intersection is a singleton.            (3)

### Coloring the minimal Ramsey core

By minimality, `Q-C` has a red/blue edge-coloring with no monochromatic
triangle.  Put `Si=N_Q(ci)-C`, so `Si` is a subset of `Ai` and `|Si|<=4`.
For each `i`, apply the cone lemma to the inherited coloring of `Q[Si]` and
color the spokes from `ci`.  The exceptional link `K4` cannot occur, since
`ci` together with that link would be a `K5` in `Q`.  This colors every
triangle containing exactly one vertex of `C` safely.

A triangle containing exactly two vertices `ci,cj` of `C` uses a vertex in
`Si intersect Sj`.  By (3), the internal edges `cicj` for which this can
happen form a matching, and there is at most one such outside vertex per
edge.  If its two spoke colors agree, prescribe the opposite color on
`cicj`; if they differ, impose no prescription.  The matching-prescription
lemma extends all these prescriptions to a good coloring of the internal
`K4`.

Triangles with zero, one, two, and three vertices in `C` are now all
nonmonochromatic.  This is a good coloring of `Q`, contradicting
`Q -> (3,3)`.  Therefore no order-28 counterexample exists.  Together with
the through-order-27 theorem and induced monotonicity, this proves the
conjecture through order 35.

## Excluding order 36

Now suppose `G` is a least-order counterexample on 36 vertices.  Since the
conjecture is proved through 35, `h=H(36)=9`.  The degree floor and ceiling
make `G` 8-regular.  The clique-residual lemma again gives `omega(G)<=4`.
Choose a minimal Ramsey core `Q`.

We first derive the core-degree ceiling directly.  Every edge of a minimal
Ramsey graph lies in at least two core triangles: otherwise a good coloring
of `Q-e` can be extended over `e`.  Thus, for `v in V(Q)`, the link of `v`
in `Q` has minimum degree at least two.  Writing `d=d_Q(v)`, this gives
`t_Q(v)>=d`, where `t_Q(v)` is the number of core triangles on `v`.

In the ambient 8-regular graph, the common-neighbor sum over the 27
nonneighbors of `v` is

`sum_x c_G(v,x)=56-2t_G(v)`.

Every summand is positive.  Indeed, for a nonneighbor `x`, the bad nine-set
`N_G(v) union {x}` must contain a nontrivial ambient maximal clique.  It must
contain `x`, since every clique inside `N_G(v)` extends by `v`, and hence
`v,x` have a common neighbor.  If `u` of the 27 summands equal one, then
`u>=2t_G(v)-2>=2d-2`.

Suppose the common neighbor is uniquely `a`.  The same bad-set argument
shows that `xa` is an ambient maximal edge.  Because `G` is regular, it also
applies with `v` and `x` interchanged, and shows that `va` is an ambient
maximal edge.  In particular `va` lies in no ambient triangle.  Hence `a` is
not in `N_Q(v)`, because every core edge lies in at least two core triangles.
The unique pairs are therefore routed through the `8-d` vertices of
`N_G(v)-N_Q(v)`, with capacity at most seven each.  Consequently

`2d-2 <= u <= 7(8-d)`,

so `9d<=58` and `Delta(Q)<=6`.  Bikov's theorem again forces a `K4`
`C={c1,c2,c3,c4}` in `Q`.  This time every ambient boundary set
`Ai=N_G(ci)-C` has size exactly five.

For a pair `ci,cj`, the outside vertices anticomplete to the pair number
`32-|Ai union Aj|`.  If this were at least 23, take an induced 23-vertex
subgraph.  The established universal bound `beta>=7` from order 23 supplies
an ambient-admissible seven-set; together with the pair it would be an
admissible nine-set.  Therefore

`|Ai union Aj|>=10`.

Since both sets have size five, all four `Ai` are pairwise disjoint.
Moreover `|Si|=d_Q(ci)-3<=3`.  Color `Q-C` well, apply the cone lemma at
each `ci`, and note that pairwise disjointness leaves no triangle with
exactly two vertices in `C`.  Finish with any good coloring of the internal
`K4`.  This again gives a good coloring of `Q`, a contradiction.

Thus order 36 is also excluded.  Since the current published Ramsey bounds
give `40<=R(3,10)<=41`, induced monotonicity proves the Erdos #151 inequality
for every graph on at most 39 vertices.

## Scope and references

This is a finite-order advance only.  It does not settle order 40 or 41 and
does not resolve the full conjecture.

- A. Bikov, *Small minimal (3,3)-Ramsey graphs*, Theorem 8.2:
  <https://arxiv.org/abs/1604.03716>.
- Independent exact check of the degree-seven specialization:
  [`checks/check_k4free_core_degree7.py`](checks/check_k4free_core_degree7.py),
  with recorded result
  [`checks/check_k4free_core_degree7.result.json`](checks/check_k4free_core_degree7.result.json).
- V. Angeltveit, *R(3,10) <= 41*:
  <https://doi.org/10.37236/12936>.
- Current problem statement and status:
  <https://www.erdosproblems.com/151>.
