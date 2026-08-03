# Triangle property B and adaptable links: a threshold-six theorem for #151

Date: 2026-08-03

## 1. Scope and outcome

The attack asked whether the special form of the triangle hypergraph of a
graph gives more than a generic property-B bound.  It does.  Deleting one
original graph vertex turns extension of an edge-colouring into an exact
two-colour adaptable-colouring problem on the graph link.  Combining that
bridge with the six-edge obstruction classification proves:

> **Threshold-six theorem.** Every finite simple graph in which each vertex
> belongs to at most six triangles has a red/blue edge-colouring with no
> monochromatic triangle.

This improves the campaign's previous audited threshold from four to six.
It also eliminates the seven-regular order-28 profile.  It does not solve
Erdos #151 because mixed degree profiles at order 28 remain.

## 2. Exact hypergraph and link reformulations

For a graph `G`, define its triangle hypergraph `T(G)` by

```
V(T(G)) = E(G),
E(T(G)) = { {xy,yz,zx} : xyz is a triangle of G }.
```

Thus a two-colouring of `V(T(G))` with no monochromatic hyperedge is
literally a red/blue colouring of `E(G)` with no monochromatic graph
triangle.  This is the exact property-B equivalence, not a relaxation.

Now let `Q` be subgraph-minimal subject to `Q -> (3,3)`, and fix a vertex
`v`.  Minimality gives a good red/blue edge-colouring `c` of `Q-v`.  Write

```
L_v = Q[N_Q(v)].
```

Label each link edge `xy` by `c(xy)`.  A proposed colour for each spoke
`vx` is identified with a proposed colour `f(x)` of the link vertex `x`.
The only newly created monochromatic triangles are `vxy`, and

```
vxy is monochromatic
iff f(x) = f(y) = c(xy).
```

Therefore the colouring of `Q-v` extends if and only if the link has a
vertex two-colouring adapted to its inherited edge two-colouring.  Since
`Q` arrows `(3,3)`, this particular link edge-colouring has no adapted
vertex colouring.  Hence every `L_v` is **not** adaptably 2-colourable.

This bridge is the local form of the marked-neighbourhood idea used in
Bikov's work on minimal `(3,3)`-Ramsey graphs; the adaptable-colouring
language supplies an exact general characterization of the obstruction.

## 3. External adaptable-colouring theorem

Pavol Hell and Xuding Zhu define a vertex colouring `f` to be adapted to an
edge colouring `F` when no edge `xy` satisfies
`F(xy)=f(x)=f(y)`.  Their Theorem 2.1 states that, for a connected graph
`L`, the following are equivalent:

1. `L` is adaptably 2-colourable (every edge two-colouring admits an
   adapted vertex two-colouring);
2. `L` contains neither an odd edge-bicycle nor an odd edge-`K4`;
3. there is an edge `e` such that `L-e` is bipartite.

Source: P. Hell and X. Zhu, *On the adaptable chromatic number of graphs*,
European Journal of Combinatorics 29 (2008), 912--921, Theorem 2.1,
DOI `10.1016/j.ejc.2007.11.015`.

Only equivalence (1) <-> (3) is needed below.

## 4. Minimal Ramsey-core facts, with all inferences explicit

Suppose for contradiction that a graph `G` satisfying the six-triangle
bound arrows `(3,3)`.  Choose an inclusion-minimal arrowing subgraph `Q`.

1. **`Q` is connected.**  If no component arrows, independently good-colour
   every component.  Conversely, if a component arrows, it is a proper
   arrowing subgraph unless it is all of `Q`.

2. **Every edge of `Q` lies in at least two `Q`-triangles.**  For an edge
   `e=xy`, minimality gives a good colouring of `Q-e`.  If `e` lies in no
   triangle, colour it arbitrarily.  If it lies in the unique triangle
   `xyz`, colour `e` opposite to the common colour of `xz,yz` when those
   colours agree, and arbitrarily when they differ.  Either way the
   colouring extends, a contradiction.

3. **Every link has minimum degree at least two.**  For `x in N_Q(v)`,
   `d_{L_v}(x)` is the number of `Q`-triangles containing the edge `vx`, so
   item 2 gives `delta(L_v) >= 2`.

4. **Every link is non-adaptably-2-colourable.**  This is the signed-link
   bridge of Section 2, applied to a good colouring of `Q-v`.

5. **Every link has at most six edges.**  The number of triangles of `Q`
   containing `v` is exactly `e(L_v)`, and `Q` is a subgraph of `G`.

6. **The connected theorem may be applied.**  Adapted vertex colourings
   factor independently across connected components.  Thus a non-adaptable
   `L_v` has a non-adaptable connected component `C`.  Every component of
   `L_v` has minimum degree at least two by item 3.  Section 5 shows that a
   non-adaptable such component needs all six available edges and is `K4`
   or a bowtie.  Any second component would itself have at least three
   edges, impossible.  Hence `L_v=C` is connected.

## 5. Hand classification at six edges

We need the following exact lemma.

> **Lemma.** Let `L` be a connected simple graph with `delta(L)>=2` and
> `e(L)<=6`.  If `L` is not adaptably 2-colourable, then `L` is `K4` or the
> bowtie (two triangles sharing exactly one vertex).

By Hell--Zhu, it is enough to classify the connected `delta>=2` graphs for
which no single edge deletion is bipartite.  Since
`2|V(L)| <= 2|E(L)|`, put `n=|V(L)|<=m=|E(L)|<=6`.

- `n=6` forces `m=6` and `L=C6`, which is bipartite.
- For `n=5`, `m=5` gives `C5`, made bipartite by deleting any edge.  If
  `m=6`, the degree excess over two is two.  Degree sequence
  `(4,2,2,2,2)` forces a universal vertex and two disjoint edges on its
  neighbours, namely the bowtie.  Degree sequence `(3,3,2,2,2)` gives a
  theta graph with path-length pattern `(2,2,2)` or `(1,2,3)` (the separate
  dumbbell form needs at least seven edges).  The first is bipartite; in the
  second, deleting an edge of the length-two path leaves an even cycle with
  trees attached.
- For `n=4`, the possibilities at `m=4,5,6` are `C4`, `K4-e`, and `K4` up
  to the irrelevant addition pattern at four edges.  The first is
  bipartite; deleting the edge shared by the two triangles of `K4-e` leaves
  `C4`; `K4` is the obstruction.
- For `n=3`, `L=K3`, and deleting one edge leaves a path.

Thus only `K4` and the bowtie survive.  (The statement for the four-edge
case can alternatively be checked directly: every connected
minimum-degree-two four-vertex graph with four edges is unicyclic and is
made bipartite by deleting an edge of its unique odd cycle.)

Two independent exhaustive programs corroborate this hand classification;
see Section 9.

## 6. Proof of the threshold-six theorem

Apply the lemma to the non-adaptable component of every link `L_v` of `Q`.
The component argument in Section 4.6 shows that it is the whole link.
Thus every link is either `K4` or a bowtie.

### 6.1 A `K4` link is impossible

If `L_v=K4`, then `{v} union N_Q(v)` induces `K5`.  Every vertex `u` of
this `K5` already belongs to the six triangles of the `K5` that contain
`u`.  If `u` had an edge from this `K5` to a vertex outside it, that core
edge would lie in at least two triangles by Section 4.2.  Both triangles
would be additional to the six internal ones, contradicting the global
six-triangle bound.  Hence the `K5` is a component.  Since `Q` is connected,
`Q=K5`.

But `K5` does not arrow `(3,3)`: colour a 5-cycle red and its complementary
5-cycle blue.  Contradiction.

### 6.2 All links are bowties

Every bowtie has five vertices, so every vertex of `Q` has degree five.
Thus `Q` is a connected 5-regular graph.  It is not `K6`, since each vertex
of `K6` belongs to ten triangles (equivalently, its link is `K5`).  Brooks'
theorem therefore gives `chi(Q)<=5`.

Finally any graph with chromatic number at most five has a good edge
two-colouring: take a proper map `phi:V(Q)->V(K5)`, colour `K5` by a red
5-cycle and blue complementary 5-cycle, and pull the edge colours back
along `phi`.  A triangle of `Q` maps to a triangle of `K5` because its three
proper vertex colours are distinct, so it cannot be monochromatic.

This contradicts `Q -> (3,3)` and proves the theorem.

## 7. Consequence for the seven-regular order-28 profile

This section uses the campaign's separately audited order-28 facts, not just
the threshold-six theorem.  Assume `G` is a seven-regular order-28
counterexample with `beta(G)<=7`.  Existing two-walk and swap arguments give,
for every vertex `v`,

```
t_v <= 7,
l_v != 0,
u_v >= 2 t_v - 2,
u_v <= 6 l_v,
t_v <= binom(7-l_v,2),
```

where `l_v` is the number of isolated vertices of `G[N(v)]` and `u_v` is
the number of non-neighbours `x` having exactly one common neighbour with
`v`.

The Folkman reduction supplies an arrowing subgraph, and the threshold-six
theorem forces a vertex `v` of its minimal arrowing core lying in at least
seven core triangles.  Since `t_v<=7` in `G`, equality holds throughout:
the core link at `v` has seven edges and all `G`-triangles through `v` are
core triangles.

The seven-edge signed-link classification gives four types.  A `K4` link
would create a `K5`, excluded by the audited order-28 clique-residual bound.
A bowtie has only six edges.  If the core link were two triangles joined by
a bridge, then `G[N(v)]` would have that six-vertex graph plus one isolated
vertex, so `l_v=1`; but `u_v>=12>6l_v`.  Therefore

```
G[N(v)] = Djs disjoint_union {a,b},
```

where `a,b` are isolated in the link.  Hence `l_v=2`, and the inequalities
force `u_v=12`.  Equality in the injection proving `u_v<=6l_v` partitions
the twelve unique-common-neighbour vertices into two sets `X_a,X_b`, each
of size six, where every `x in X_a` has `a` as its unique common neighbour
with `v` (and similarly for `b`).  The swap lemma says both edges `va` and
`ax` are triangle-free.  Consequently `X_a` is independent.

Choose any vertex `c` of the `Djs` part.  Then:

- `b` is nonadjacent to `c` because `b` is link-isolated;
- `b` and `c` are nonadjacent to every `x in X_a`, since otherwise they
  would be a second common neighbour of `v,x` besides `a`;
- `X_a` is independent as just noted.

Thus `X_a union {b,c}` is an independent set of size eight.  Every
independent set is admissible for `beta`, contradicting `beta(G)<=7`.

So the seven-regular order-28 profile is impossible.  The mixed profiles do
not have the swap lemma at both endpoints needed for the uniform `t_v<=7`
bound, so this argument must not be overextended to them.

## 8. Exact threshold-seven frontier

Repeating Sections 4--5 with `e(L_v)<=7` gives exactly four link types:

1. `K4` (`m=6`);
2. the bowtie (`m=6`);
3. `Djs`, with edges
   `01,04,12,13,14,23,34` (`m=7`);
4. two disjoint triangles joined by one bridge (`m=7`).

Here too disconnectedness causes no loophole.  Adapted colourings factor by
components, so some component is non-adaptable and therefore consumes six
or seven edges.  Every other component has minimum degree at least two and
hence at least three edges.  Since the whole link has at most seven edges,
there is no other component.

The `K4` case is again impossible: its `K5` contributes six triangles at
each vertex, and any external core edge contributes at least two more,
exceeding seven.  Hence a hypothetical threshold-seven minimal core has
only the last three links.

Let `mu(xy)` be the number of triangles containing an edge `xy`.  Reading
degrees in the links gives the incident multiplicity signatures

```
bowtie:          4,2,2,2,2
Djs:             4,3,3,2,2
joined triangles:3,3,2,2,2,2.
```

It follows by symmetry of `mu(xy)` that:

- multiplicity-4 edges form a perfect matching on all degree-5 vertices;
  the endpoints of each such edge have the same four other neighbours and
  are adjacent true twins;
- multiplicity-3 edges form a 2-regular graph (a disjoint union of cycles)
  on the `Djs` and degree-6 vertices;
- every neighbourhood is covered by two triangles, so the core is
  quasi-line, with `Delta<=6`, `omega<=4`, and `chi>=6`.

The sharp published local Reed theorem for quasi-line graphs gives only

```
chi(Q) <= max_v ceil((d(v)+1+omega(v))/2) <= 6.
```

It is tight at a degree-6 joined-triangles vertex and therefore does not
prove the needed `chi(Q)<=5`.  No global example satisfying all three local
link types and arrowing `(3,3)` was found, but neither was the following
precise structural lemma proved:

> Every connected graph whose links all belong to
> `{bowtie, Djs, joined-triangles}` is 5-colourable.

That is the exact threshold-seven frontier.  Pursuing generic quasi-line
colouring without using the matching/cycle multiplicity structure would
mostly reproduce a difficult literature, so this lane stops here rather
than present a conjectural closure.

## 9. Computational checks and hashes

### Primary enumerator

`signed_link_obstructions.py` uses the NetworkX graph atlas, direct
enumeration of every edge signing, and direct enumeration of every vertex
two-colouring.  Since `delta>=2` and `m<=7` imply `n<=7`, the atlas through
seven vertices is complete for the stated scope.  It checks 18 connected
isomorphism types and finds counts by edge number

```
m<=5: 0
m=6:  2  (K4, bowtie)
m=7:  2 additional types (Djs, joined triangles)
```

It independently checks agreement with the Hell--Zhu edge-deletion
criterion for every graph.

### Independent audit

`root_independent_threshold6_audit.py` instead uses nauty `geng`, a custom
graph6 parser, custom bipartiteness code, and a separate exhaustive adapted
colouring implementation.  It checks nine connected minimum-degree-two
types with at most six edges and finds exactly `K4` and the bowtie.  Its
result status is `VERIFIED`.

Pinned SHA-256 values before this report was written:

```
signed_link_obstructions.py
  d00bda938f60936aeb2a589143c562564d90fe9c5b28635b9b021a3dca14112e
signed_link_obstructions.result.json
  4d7affac81b273f2ff5e1044029ca7cc627692e96c137819ca48927f17a6f4e5
root_independent_threshold6_audit.py
  e0b7c4bbee111fba1628a55cc6eda47f2d7824480fc67758783d3fe6de32f7f9
root_independent_threshold6_audit.result.json
  4573ddba2bc2a3054db44a4bbefb5f8c06e8da3797d1b6463c549ad3f75a3fd9
```

The independent audit pins nauty `geng.exe` at
`64fa2d95bdaff155ce0fc748d4cba83a50e5ffb03e3acc5f41d86581c0bba7ef`.

## 10. Priority and publication boundary

Relevant prior sources found in the targeted search:

- P. Hell and X. Zhu, *On the adaptable chromatic number of graphs*, EJC
  29 (2008), 912--921, DOI `10.1016/j.ejc.2007.11.015`.
- A. Bikov, *Small minimal (3,3)-Ramsey graphs*, arXiv:1604.03716.  In
  particular, its marked-neighbourhood framework and finite degree-5 link
  analysis are closely adjacent to the present bridge.
- M. Chudnovsky, A. D. King, M. Plumettaz, and P. Seymour, *A local
  strengthening of Reed's omega, Delta, chi conjecture for quasi-line
  graphs*, arXiv:1109.2112, Theorem 4.

Targeted exact-phrase and concept searches did not locate the threshold-six
corollary, but that is not a proof of priority.  Before public novelty claims,
the theorem should receive an independent human graph-theory audit and a
broader citation search around marked vertex sets in minimal Ramsey graphs.
