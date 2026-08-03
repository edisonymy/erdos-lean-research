# A line-graph closure at threshold seven

Date: 2026-08-03

## Status and scope

This note strengthens the threshold-six theorem in `REPORT.md`.  A separate
clean-room adversarial reconstruction found no mathematical gap, the finite
local facts have independent checks, and the cited edge-colouring theorem was
verified against its source.  A targeted priority search found no exact
prior statement, but several ingredients are classical and that negative
search is not a categorical priority guarantee.

> **Threshold-seven theorem.**  Every finite simple graph in which each
> vertex belongs to at most seven triangles has a red/blue edge-colouring
> with no monochromatic triangle.

Equivalently, if `G -> (3,3)`, then some vertex of `G` belongs to at least
eight triangles.  This is a structural partial result for Erdos #151, not a
solution of the full problem.

## 1. Minimal arrowing core and exact links

Suppose for contradiction that `G -> (3,3)` while every vertex of `G` is
in at most seven triangles.  Choose an inclusion-minimal arrowing subgraph
`Q`.

The arguments in Sections 2--5 of `REPORT.md` give:

1. `Q` is connected.
2. Every edge of `Q` belongs to at least two `Q`-triangles.
3. Every link `L_v = Q[N_Q(v)]` has minimum degree at least two, has at
   most seven edges, and is not universally adaptably 2-colourable.
4. A non-adaptable component consumes at least six edges, while any other
   link component would consume at least three.  Thus every `L_v` is
   connected.
5. The exact seven-edge classification leaves four possible links:
   `K4`; the bowtie `B`; the graph

   ```
   D: 01,04,12,13,14,23,34;
   ```

   and `J`, consisting of two vertex-disjoint triangles joined by one
   edge.

The classification follows from the Hell--Zhu criterion that a connected
graph is universally adaptably 2-colourable exactly when deleting some
edge makes it bipartite.  It was also checked by two independent exhaustive
programs through seven edges.

## 2. The `K4` link is impossible

If `L_v=K4`, then `N_Q[v]` induces a `K5`.  Each vertex of this `K5` is in
six internal triangles.  If it had a core edge leaving the `K5`, that edge
would lie in at least two triangles, giving its endpoint at least eight
triangles.  Therefore the `K5` is a component of connected `Q`, so `Q=K5`.
But a red 5-cycle and its blue complement give a good colouring of `K5`, a
contradiction.

Hence every link is one of `B,D,J`.

## 3. The `D` link is impossible

For an edge `xy` of `Q`, write `mu(xy)` for the number of triangles of `Q`
containing it.  In a link `L_v`, the degree of `x` is exactly `mu(vx)`.
The degree multisets of the three surviving link types are

```
B: 4,2,2,2,2
D: 4,3,3,2,2
J: 3,3,2,2,2,2.
```

Assume `L_v=D`, and choose a degree-three vertex `x` of this link.  The
three neighbours of `x` within `L_v` induce `P3`.  Since `mu(vx)=3`, the
vertex `v` has degree three in `L_x`.  The link `L_x` cannot be `B`, which
has no degree-three vertex.  It cannot be `J`, because the neighbours of a
degree-three vertex in `J` induce `K2 disjoint_union K1`, not `P3`.
The `K4` case has already been eliminated.  Consequently `L_x=D`.

In `L_x=D`, there is a unique degree-four vertex `y`.  Thus `mu(xy)=4`.
Both endpoints of a multiplicity-four edge have degree five: their links
must be `B` or `D`, since neither `J` nor the eliminated `K4` has the
required combination.  They are adjacent and have four common neighbours,
so their closed neighbourhoods are equal:

```
N_Q[x] = N_Q[y].
```

In particular, `v` is adjacent to `y`.  Intersecting the equal closed
neighbourhoods with `N_Q(v)` makes `x,y` adjacent true twins in `L_v`.
But direct inspection of `D` shows that it has no adjacent true twins.  This
contradiction eliminates `D`.

Therefore every link of `Q` is `B` or `J`.

## 4. A canonical multigraph root

Each of `B` and `J` contains exactly two triangles, and every one of its
vertices lies in at least one of those triangles.  A triangle in `L_v`
corresponds exactly to a `K4` of `Q` containing `v`.  It follows that:

1. every vertex of `Q` lies in exactly two `K4`s; and
2. every edge of `Q` lies in at least one `K4`.

This is the multigraph form of Krausz's line-graph characterization.  The
exact formulation appears, for example, as Theorem B in Z. Ryjacek and
P. Vrana, *A closure for 1-Hamilton-connectedness in claw-free graphs*,
where it is attributed to J. Krausz (1943).  The following direct
construction avoids any ambiguity about parallel edges.  Make one
vertex of a multigraph `H` for every `K4` of `Q`.  A vertex `z` of `Q` lies
in two distinct `K4`s, so make an edge `e_z` of `H` between the corresponding
two vertices.  Different vertices of `Q` may give parallel edges of `H`,
but no loop occurs.

If `z,w` are adjacent in `Q`, some `K4` contains both, so `e_z,e_w` share
an endpoint in `H`.  Conversely, if `e_z,e_w` share an endpoint, then
`z,w` lie in the corresponding `K4` and are adjacent in `Q`.  Hence

```
Q = L(H).
```

Every root vertex corresponds to a four-vertex clique and therefore has
degree four in `H`, counting parallel edges with multiplicity.  Since `Q`
is connected, `H` is connected after discarding irrelevant isolated
vertices.  Thus `H` is a connected loopless 4-regular multigraph.

Also `Q` has no `K5`: a vertex of a `K5` would have a `K4` in its link,
whereas neither `B` nor `J` contains a `K4`.  In particular, `Q` is not
`K6`.

## 5. Goldberg--Seymour gives a five-edge-colouring

For a loopless multigraph `H`, define

```
Gamma(H) = max 2|E(H[S])|/(|S|-1),
```

where the maximum is over odd vertex sets `S` of size at least three.
The Goldberg--Seymour theorem gives

```
chi'(H) <= max { Delta(H)+1, ceil(Gamma(H)) }.
```

Here `Delta(H)=4`.  If `|S|>=5`, then

```
2|E(H[S])| <= 4|S| <= 5(|S|-1).
```

If `|S|=3` and `|E(H[S])|>=6`, 4-regularity forces equality throughout:
all twelve incident degree units are internal and no edge leaves `S`.
Connectedness then gives `V(H)=S`.  The three degree equations force each
pair of vertices to be joined by two parallel edges.  Thus `H` is the
doubled triangle and `L(H)=K6`, already excluded.  Therefore every
three-vertex set spans at most five edges as well.  Hence `Gamma(H)<=5`, so

```
chi'(H) <= 5.
```

The degree-four case needed here already follows from the published theorem
that Goldberg--Seymour holds for multigraphs of maximum degree at most 39:

G. Chen and G. Jing, *Structural properties of edge-chromatic critical
multigraphs*, Journal of Combinatorial Theory, Series B 139 (2019),
128--162, DOI `10.1016/j.jctb.2019.03.004`.  In particular, they prove the
Goldberg conjecture for multigraphs of maximum degree at most 39.

Alternatively, the full conjecture is now Theorem 1.1 of G. Chen, G. Jing,
and W. Zang, *Proof of the Goldberg--Seymour conjecture on edge-colorings of
multigraphs*, Journal of Combinatorial Optimization 50, article 23 (2025),
DOI `10.1007/s10878-025-01348-6`.

## 6. Pullback and contradiction

A proper five-edge-colouring of `H` is a proper five-vertex-colouring of
`Q=L(H)`.  Colour the edges of `K5` by taking a red 5-cycle and its blue
complement, and pull this edge colouring back along the proper vertex map
`Q -> K5`.  The three vertices of every triangle of `Q` receive three
distinct colours, so the triangle maps to a triangle of `K5`, which is not
monochromatic.  This gives a good red/blue edge-colouring of `Q`, contrary
to `Q -> (3,3)`.

The threshold-seven theorem follows.

## 7. Audit and publication boundary

Completed internal checks include an independent proof audit of the
elimination of `D`, an independent reconstruction of the multigraph root and
density argument, source verification for the edge-colouring theorem, and a
targeted priority search around minimal `(3,3)`-Ramsey graphs and adaptable
colourings.  The exact audit boundary is in `ROOT-STYLE_AUDIT.md` and the
independent threshold-seven audit package.

The exhaustive order-at-most-12 scan in the companion threshold-seven
package is independent supporting evidence: its four local cores are the
line graphs of the doubled cycles of lengths 4, 5, and 6, and of two
triangles joined by a doubled perfect matching.  It is not used as a proof
of the general line-graph step.

Before an unqualified novelty claim, the theorem should still receive human
graph-theory review and a broader citation search, especially in older and
non-English minimal-Ramsey literature.  The defensible present wording is
that the marked-neighbourhood/adaptable-colouring analysis, Krausz
characterization, and a small-degree Goldberg theorem combine to give the
eight-triangle necessary condition.
