# Order-15 two-defect theta-core reduction

Date: 2026-08-03

Status: proved finite reduction for the order-15, 29-edge slice; not a full
resolution of Erdős problem #149.

## Setup

Let `G` be a smallest-order subquartic graph with no strong
20-edge-colouring, and suppose `|V(G)|=15` and `|E(G)|=29`.  The degree sum
and `delta(G)>=3` imply that exactly two vertices, call them `a,b`, have
degree three and all other vertices have degree four.

The degree-three extension lemma proves:

* `dist(a,b)>=3`;
* every vertex at distance at most two from `a` or `b` has degree four;
* no triangle or 4-cycle contains `a` or `b`;
* for a neighbour `u` of `a`, the three neighbours of `u` other than `a`
  are pairwise nonadjacent, and similarly at `b`.

## Radius-two balls

Put `U=N(a)`.  Each of the three vertices of `U` has three other neighbours.
No triangle through `a` lets any such neighbour lie in `U`, and no 4-cycle
through `a` lets two vertices of `U` share one.  Hence these are nine distinct
vertices and

`|B_2(a)| = 1+3+9 = 13`.

Likewise `|B_2(b)|=13`.  Since `b` is not in `B_2(a)`, only one further
vertex can lie outside `B_2(a)`.

Let `W=N(b)`.  A vertex of `W` lies in `B_2(a)` exactly when it has a
neighbour in `U`.  At least two of the three vertices of `W` lie in
`B_2(a)`.  Moreover, the edges between `U` and `W` form a matching: two such
edges sharing a vertex would create a 4-cycle through `a` or through `b`.
Consequently the `U-W` edge set is a matching of size

`r in {2,3}`.

After relabelling, write its edges as `u_i w_i` for `i<r`.  Thus `G` contains
`r` internally vertex-disjoint length-three paths

`a-u_i-w_i-b`.

There are seven remaining vertices; call their set `X`.

## Forced incidence blocks

Every matched `u_i` already sees `a,w_i` and therefore has exactly two
neighbours in `X`.  When `r=2`, the unmatched vertex of `U` has three
neighbours in `X`; when `r=3`, every vertex of `U` has two.  The three
`U-X` neighbour blocks are disjoint by the no-4-cycle condition at `a`.
Their sizes are therefore

* `(2,2,3)`, covering all seven vertices of `X`, when `r=2`;
* `(2,2,2)`, covering six vertices of `X`, when `r=3`.

The same statements hold for the three labelled `W-X` blocks.

If `u_iw_i` is a matched core edge, its `U-X` and `W-X` blocks are disjoint;
otherwise a common `x` makes the triangle `u_iw_ix`.  For every `u_i`, its
X-block is independent because the neighbours of `u_i` other than `a` are
pairwise nonadjacent.  Every W-block is independent for the same reason.

By permuting `X`, the U-blocks may be fixed as

* `01 | 23 | 456` in the `r=2` case;
* `01 | 23 | 45`, with `6` omitted, in the `r=3` case.

It remains only to enumerate the labelled W-blocks with their prescribed
sizes and disjointness constraints, then complete the graph induced by `X`
to make every X-vertex degree four while forbidding edges inside any U- or
W-block.

## Exhaustive completion

`n15_theta_core_search.py` enumerates 55 W-block systems for `r=2` and 94
for `r=3`.  Exact residual-degree backtracking yields respectively 492 and
4,764 X-graph completions.  Every one of these 5,256 labelled graphs has nine
disjoint compatibility pairs, which save nine colours from 29.

`audit_n15_theta_core.py` uses a separate enumeration: it scans every
7-edge or 8-edge subset of `K_7`, buckets by the exact degree vector, filters
independently generated W-incidence words, and constructs compatibility
pairs in reverse order on demand.  It reproduces all four counts exactly and
again finds nine pairs in all 5,256 completions.

Thus no order-15, 29-edge smallest counterexample exists.

## Claim boundary

The proof above establishes why the finite completion space is exhaustive;
the two scripts certify that space.  This reduction is specific to the
order-15 two-degree-three slice and makes no claim about larger orders or the
universal conjecture.
