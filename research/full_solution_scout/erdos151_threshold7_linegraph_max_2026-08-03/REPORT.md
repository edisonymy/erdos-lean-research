# Adversarial audit: the threshold-seven line-graph theorem

Date: 2026-08-03

## 1. Verdict and scope

I independently reconstructed the proposed argument, tried to break every
transition named in the brief, and found no gap.  The route proves the
following theorem.

> **Threshold-seven theorem.** Let `G` be a finite simple graph.  If every
> vertex of `G` belongs to at most seven triangles, then the edges of `G`
> admit a red/blue colouring with no monochromatic triangle.

Equivalently, if `G -> (3,3)`, then some vertex of `G` belongs to at least
eight triangles.

This is a theorem about triangle-Ramsey graphs.  By itself it is **not** a
full solution of Erdos problem #151, and this audit makes no priority claim.
Its two external inputs are the exact adaptable-colouring characterization
of Hell--Zhu and the Goldberg--Seymour chromatic-index theorem.  The small
link classification was also checked independently from the definition.

## 2. Preliminaries: the minimal core and its links

Assume for a contradiction that `G` satisfies the triangle bound and arrows
`(3,3)`.  Choose an inclusion-minimal arrowing subgraph `Q`.

### 2.1 Minimal-core facts

1. `Q` is connected.  Otherwise either a component arrows, contradicting
   minimality, or every component has a good edge colouring, which can be
   combined componentwise.

2. Every edge of `Q` belongs to at least two triangles of `Q`.  Indeed,
   minimality gives a good colouring of `Q-e`.  If `e` is in no triangle it
   may be coloured arbitrarily.  If it is in one triangle, give it the
   opposite colour when the other two edges agree (and either colour when
   they disagree).  This extends the colouring, a contradiction.

3. For `v in V(Q)`, put `L_v = Q[N_Q(v)]`.  A link vertex `x` has

   ```
   d_{L_v}(x) = number of Q-triangles containing vx >= 2.
   ```

   Also `e(L_v)` is the number of `Q`-triangles through `v`, so
   `e(L_v) <= 7`.

### 2.2 The exact signed-link bridge

Minimality gives a good red/blue colouring `c` of `Q-v`.  Label every link
edge `xy` by `c(xy)`.  Assigning a colour `f(x)` to the spoke `vx` creates a
monochromatic triangle `vxy` exactly when

```
f(x) = f(y) = c(xy).
```

Thus the colouring extends precisely when the inherited edge-labelled link
has an adapted vertex two-colouring.  Since `Q` arrows, this particular
edge labelling has no adapted colouring.  Consequently every `L_v` is not
universally adaptably 2-colourable.

Hell and Zhu prove that a connected graph is universally adaptably
2-colourable if and only if deleting some edge makes it bipartite.  Their
componentwise corollary says the same separately on every connected
component.  This is exactly the convention needed here: their edge
colouring need not be proper, and the forbidden event is equality of the
edge colour with both endpoint colours.

## 3. Exact seven-edge obstruction lemma

> **Link lemma.** A connected simple graph `L` with `delta(L) >= 2` and
> `e(L) <= 7` that is not universally adaptably 2-colourable is isomorphic
> to exactly one of:
>
> 1. `K4` (six edges);
> 2. the bowtie, two triangles sharing one vertex (six edges);
> 3. `Djs`, with edges `01,04,12,13,14,23,34` (seven edges);
> 4. two vertex-disjoint triangles joined by a single bridge (seven edges).

Here is a short hand classification using the Hell--Zhu criterion.  A bad
`L` has no edge meeting every odd cycle.

If `L` has two edge-disjoint odd cycles, the seven-edge budget forces both
to be triangles.  If they share one vertex, their union is the bowtie; the
only possible seventh edge joins the two lobes and produces `Djs`.  If the
triangles are vertex-disjoint, connectedness consumes the seventh edge as a
single bridge and produces the joined-triangles graph.  No extra vertex can
occur because minimum degree two would cost at least two further edges.

Otherwise every two odd cycles share an edge, while all odd cycles have
empty total edge intersection.  There must be at least three odd cycles.
A 7-cycle leaves no edge for a second cycle.  If a 5-cycle occurs, at most
two edges remain.  One chord leaves a common cycle edge; a two-edge ear
also leaves a common edge on the appropriate arc.  With two chords, chords
sharing an endpoint create two edge-disjoint triangles, while two disjoint
chords are, up to symmetry, `02,13` on `012340`, and deleting `12` leaves a
bipartite graph.  Hence this case has no 5-cycle either.  All odd cycles are
triangles.  Choose two, `abc` and `abd`, sharing `ab`.  A third triangle
that avoids `ab` but shares an edge with each forces the missing edge `cd`;
their union is `K4`.  Simplicity and minimum degree two rule out a seventh
edge or an extra vertex.  This proves the list.

For a disconnected link, adapted colourings factor over components.  A bad
component therefore has six or seven edges by the lemma, while every other
component (also of minimum degree at least two) has at least three edges.
As the whole link has at most seven edges, there is no second component.
Thus every `L_v` itself is one of the four listed graphs.

The independent program `independent_local_audit.py` additionally enumerates
all 1,618 labelled connected simple graphs satisfying `delta>=2`, `m<=7`.
For every graph it checks all edge two-colourings and all vertex
two-colourings directly, checks agreement with edge-deletion
bipartiteness, and identifies bad graphs by brute-force permutation
isomorphism.  It finds 166 labelled obstructions and exactly the four
isomorphism types above, with zero criterion disagreements.

## 4. The `K4` link cannot occur

If `L_v=K4`, then `N_Q[v]` induces a `K5`.  Each vertex of this `K5`
already lies in six internal triangles.  If a `K5` vertex `u` had a core
edge to a vertex outside the `K5`, that edge would lie in at least two core
triangles by Section 2.1.  Those are two additional triangles through `u`,
contradicting the bound seven.  Hence the `K5` is a component of connected
`Q`, so `Q=K5`.

But `K5` is nonarrowing: colour a 5-cycle red and its complementary
5-cycle blue.  Both colour classes are triangle-free.  Contradiction.

Hence links in `Q` have only the bowtie, `Djs`, or joined-triangles types.

## 5. Adversarial audit of the `Djs` elimination

This is the most delicate local step.  Define

```
mu(xy) = number of Q-triangles containing edge xy.
```

Suppose `L_v` is `Djs`.  Its degree sequence is `(4,3,3,2,2)`.  Pick a
degree-three vertex `x` of `L_v`.  Then `mu(vx)=3`, and the graph induced by
the three common neighbours of `v,x` is a `P3`.

Now view `v` as a vertex of `L_x`.  It has degree three there and its three
link-neighbours induce `P3`.  This pins down the type of `L_x`:

* a bowtie has no degree-three vertex;
* in joined triangles, the neighbours of either degree-three vertex induce
  `K2 disjoint_union K1`;
* in `K4`, they induce `K3`;
* in `Djs`, they induce `P3`.

Therefore `L_x` is `Djs`.

There is a unique degree-four vertex `x*` in `L_x`, so `mu(xx*)=4`.  The
link type at `x*` cannot be joined triangles or `K4`, because in those links
the vertex corresponding to `x` would have degree at most three; it is a
bowtie or `Djs`.  In either case both `x` and `x*` have degree five in `Q`.
They are adjacent and have four common neighbours, so

```
N_Q[x] = N_Q[x*].
```

In particular `v` is also adjacent to `x*`.  Restricting the equal closed
neighbourhoods to `N_Q(v)` makes `x,x*` adjacent true twins inside `L_v`.
But direct inspection of the seven displayed `Djs` edges shows that `Djs`
has no adjacent true twins.  Contradiction.

The independent local audit checks all four distinguishing induced
neighbourhood signatures and the absence of adjacent true twins in `Djs`
directly.  This step uses neither an unproved propagation assumption nor a
degree inference from only one endpoint.

## 6. Constructing the root multigraph directly

Only bowtie and joined-triangles links remain.  Each of these graphs has
exactly two triangles, and its two triangles cover every link vertex.

Let `K` be the set (duplicates removed) of all `K4` subgraphs of `Q`.

* A `K4` containing `v` is exactly `{v}` plus a triangle of `L_v`.
  Therefore every vertex of `Q` lies in exactly two **distinct** members of
  `K`.  Distinctness is explicit: the two link triangles are distinct.
* If `xy` is an edge of `Q`, the link vertex `y` belongs to one of the two
  triangles covering `L_x`.  Adding `x` gives a member of `K` containing
  both `x,y`.  Thus every edge of `Q` is covered by at least one member of
  `K`.

This is the relaxed Krausz characterization for line graphs of
multigraphs, but no black-box direction is required.  Construct `H`
directly:

* vertices of `H` are members of `K`;
* for each vertex `z` of `Q`, put one edge `e_z` between the two members of
  `K` containing `z`.

The endpoints are distinct, so `H` has no loops.  Different `Q` vertices
may produce the same endpoint pair, which is exactly why parallel edges are
allowed.  Two vertices `z,w` are adjacent in `Q` if and only if some
`K4 in K` contains both, if and only if root edges `e_z,e_w` have a common
endpoint.  Hence `Q=L(H)` exactly; there are no missing or spurious line
graph edges.

Every member of `K` contains four `Q` vertices, so the corresponding root
vertex has degree four, counting multiplicity.  Thus `H` is loopless and
4-regular.  Since `Q` is connected and every root vertex has positive
degree, `H` is connected.

This construction also audits a common Krausz pitfall: edges of `Q` need
not be covered exactly once.  A bowtie link creates overlapping `K4`s; the
double coverage becomes a pair of parallel root edges and is permitted by
the multigraph characterization.  The exact published characterization
indeed says “every edge ... in at least one clique,” not exactly one.

## 7. The root has chromatic index at most five

For a loopless multigraph `H`, define

```
Gamma(H) = max 2 e(H[S])/(|S|-1),
```

where the maximum is over odd vertex sets `S` of size at least three.
The Goldberg--Seymour theorem gives

```
chi'(H) <= max{ Delta(H)+1, ceil(Gamma(H)) }.
```

Here `Delta(H)=4`.  If `|S|>=5`, regularity gives

```
2 e(H[S]) <= sum_{s in S} d_H(s) = 4|S| <= 5(|S|-1),
```

so the density is at most five.

If `|S|=3` and its density exceeds five, integrality gives
`e(H[S])>=6`.  But the total degrees of the three vertices sum to 12, so
`e(H[S])=6` and there is no edge from `S` to its complement.  Connectedness
then forces `V(H)=S`.  Writing the three pair multiplicities as `a,b,c`,
4-regularity gives

```
a+b = a+c = b+c = 4,
```

and hence `a=b=c=2`: `H` is the doubled triangle.  Its six edges are
pairwise incident, so `L(H)=K6`.  This is impossible because every vertex
link of `Q` is a bowtie or joined triangles, whereas a `K6` link is `K5`.

Therefore `Gamma(H)<=5`, and Goldberg--Seymour yields `chi'(H)<=5`.
Equivalently, `Q=L(H)` has a proper vertex colouring with at most five
colours.

Notice that no bound on the maximum parallel-edge multiplicity was used.
The three-vertex extremal case is derived from the degree equations rather
than silently assuming multiplicity at most two.

## 8. Pulling back the good `K5` edge colouring

Let `phi:V(Q)->{0,1,2,3,4}` be a proper colouring.  Colour the edges of
`K5` red on a 5-cycle and blue on its complementary 5-cycle, then colour
`xy in E(Q)` by the colour of `phi(x)phi(y)`.

On any triangle `xyz` of `Q`, properness makes the three values
`phi(x),phi(y),phi(z)` distinct.  Its three edge colours are therefore the
colours of a genuine triangle of the coloured `K5`.  Neither colour class
of `K5` contains a triangle, so the triangle in `Q` is not monochromatic.
This contradicts `Q -> (3,3)` and completes the proof.

## 9. Independent computation

Two scripts in this directory use no campaign modules.

`independent_local_audit.py`:

* enumerates all 1,618 labelled connected simple graphs with `delta>=2`
  and at most seven edges;
* checks all edge signings against all vertex two-colourings;
* independently checks the Hell--Zhu edge-deletion criterion;
* finds exactly `K4`, bowtie, `Djs`, and joined triangles;
* checks the `Djs` degree-three neighbourhoods and true-twin claim;
* checks that the bowtie and joined-triangles links each have two triangles
  covering every vertex.

`independent_global_audit.py`:

* solves the three-vertex 4-regular multiplicity equations exhaustively;
* checks that the doubled triangle has line graph `K6`;
* checks the odd-density arithmetic;
* checks every triangle of the standard coloured `K5`;
* checks 1,080,465 proper-colouring pullback instances through order five.

Both result files report `VERIFIED`.

## 10. Exact external sources

1. P. Hell and X. Zhu, *On the adaptable chromatic number of graphs*,
   European Journal of Combinatorics 29 (2008), 912--921, Theorem 2.1 and
   Corollary 2.1, DOI `10.1016/j.ejc.2007.11.015`.
   Publisher page:
   <https://www.sciencedirect.com/science/article/pii/S0195669807002065>.

2. G. Chen, G. Jing, and W. Zang, *Proof of the Goldberg--Seymour
   conjecture on edge-colorings of multigraphs*, Journal of Combinatorial
   Optimization 50 (2025), article 23, Theorem 1.1, DOI
   `10.1007/s10878-025-01348-6`.  The publisher page records its later
   publisher correction and current updated text:
   <https://link.springer.com/article/10.1007/s10878-025-01348-6>.

3. For the exact relaxed Krausz statement (not needed as a black box after
   the direct construction), Theorem B in Z. Ryjacek and P. Vrana,
   *A closure for 1-Hamilton-connectedness in claw-free graphs* states that
   a graph is a line graph of a multigraph exactly when its vertices are
   covered by cliques, every vertex is in exactly two, and every graph edge
   is in at least one:
   <https://home.zcu.cz/~ryjacek/publications/files/082.pdf>.

4. A. Bikov, *Small minimal (3,3)-Ramsey graphs*, Ann. Univ. Sofia Fac.
   Math. Inform. 103 (2016), 123--147, Theorem 8.1, computationally
   classifies the three five-vertex `K4`-free marked neighbourhoods of a
   degree-five vertex.  This is close prior art for the bowtie/`Djs` local
   stage, although it does not supply the global `Djs` elimination, the
   multigraph root, or the threshold-seven conclusion:
   <https://arxiv.org/abs/1604.03716>.

## 11. Claim boundary

### Proved

* the threshold-seven theorem;
* every minimal arrowing core under the bound would have only bowtie and
  joined-triangles links;
* such a core is the line graph of a connected loopless 4-regular
  multigraph and is 5-colourable;
* hence such a core cannot exist.

### Computationally checked

* the complete seven-edge link classification from definitions;
* all finite local invariants used in the `Djs` elimination;
* the doubled-triangle, density-arithmetic, and `K5` pullback endpoints.

### Not claimed

* a full resolution of Erdos #151;
* priority or novelty of the threshold-seven theorem;
* any threshold-eight analogue;
* an independent reproof of Hell--Zhu or Goldberg--Seymour.
