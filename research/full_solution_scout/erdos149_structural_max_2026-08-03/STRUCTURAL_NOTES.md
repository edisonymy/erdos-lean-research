# Structural and construction notes for Erdős #149, Δ=4

Date: 2026-08-03

## A. Exact small-edge reformulation

Let $J(G)$ be the compatibility graph on $E(G)$: its cliques are induced
matchings of $G$. Define

$$
s(J)=\max\sum_i(|C_i|-1),
$$

where the maximum is over vertex-disjoint cliques $C_i$ of $J$, each of size
at least two. Filling unused vertices with singleton classes shows the exact
identity

$$
\chi'_s(G)=|E(G)|-s(J(G)). \tag{A1}
$$

Thus a negative witness at Δ=4 is exactly a graph for which
$s(J)\le |E(G)|-21$. At the first few edge counts this becomes:

* $m=21$: $J$ must be empty. CGTT rules this out.
* $m=22$: $J$ must have no triangle and no matching of size two; since it is
  nonempty, it must be a star plus isolated vertices.
* $m=23$: $J$ must have no $K_4$, no triangle disjoint from an edge, and no
  matching of size three.
* $m=24$: $J$ must have none of the savings-four profiles

  $$
  5;\quad4+2;\quad3+3;\quad3+2+2;\quad2+2+2+2.
  $$

These are exact pruning conditions, not heuristics.

## B. Connector localization at 22 edges

Suppose $m=22$ and the obstruction shape
$J=K_{1,t}\mathbin{\dot\cup}K_1$'s holds, with centre edge $e_0=uv$. Put
$F=G-e_0$. CGTT guarantees that $F$, which has 21 edges, contains an induced
$2K_2$. No two non-centre edges are compatible in $G$, so every induced
$2K_2$ of $F$ must have $e_0$ as its sole missing cross-connector.
Consequently every such pair consists of one edge incident with $u$ and one
edge incident with $v$. There are at most $3\cdot3=9$ possible pairs.

This is a useful exact separation oracle for any future search: after deleting
the proposed centre, every induced $2K_2$ must lie in that fixed
$3\times3$ rectangle. It is also the precise point at which a naive
application of CGTT to $G-e_0$ fails: deleting the centre can create
compatibility pairs.

## C. Regularization: why a negative search may focus on 4-regular graphs

Every finite simple graph of maximum degree at most four is a subgraph of a
finite simple 4-regular graph. Take six disjoint copies of the graph. For each
original vertex $v$ with deficiency $d_v=4-d(v)$, join its six copies
according to any simple $d_v$-regular graph on six vertices. Such graphs exist
for every $d_v\in\{0,1,2,3,4\}$ (use the empty graph, a perfect matching, a
6-cycle, its union with a disjoint perfect matching, or $K_6$ minus a perfect
matching). These added edges lie only between copies and fill every
deficiency.

Strong chromatic index is monotone under taking subgraphs, so any
counterexample to #149 yields a 4-regular counterexample, although this
construction need not preserve order. This justifies regular/Cayley/lift
searches for a negative witness; it does **not** justify assuming that a
smallest-order counterexample is regular.

## D. Perturbing the extremal $C_5[2]$

Let $B=C_5[2]$, the balanced blow-up with five independent parts of size two
and all edges between consecutive parts. It is 4-regular on 10 vertices, has
20 edges, and $J(B)$ is empty.

Add a new vertex $x$, delete $r$ old edges, and give $x$ degree $d$. For 22
total edges, $d-r=2$. Since every old vertex is saturated and one deleted edge
frees at most two distinct endpoints, the only possibility is $d=4,r=2$,
with the deleted edges disjoint and $N(x)$ equal to their four endpoints.
There are

$$
\binom{20}{2}-10\binom42=130
$$

labelled choices. All 130 were checked. Every compatibility graph has a
matching of size two (hence an explicit 20-colouring); their compatibility
edge counts range from 14 to 25. Thus even the closest perturbation is far
from the required star shape.

For 21 edges, the complete one-new-vertex perturbation cases
$(d,r)=(2,1),(3,2),(4,3)$ comprise respectively 20, 580, and 8,020 distinct
labelled graphs in the script. Every graph contains a compatibility edge, as
CGTT predicts.

## E. Bounded algebraic and catalogue pulse

The ten connection-set instances
$\operatorname{Cay}(\mathbb Z_{11},\{\pm a,\pm b\})$ and the ten analogous
instances at order 12 produced no candidate. At order 11 every $J$ has the
required matching of size two; at order 12 every $J$ has a matching of size
four.

The public catalogue of all 1,544 connected 4-regular graphs on 12 vertices
was then checked. Every compatibility graph has a matching of size at least
four. In fact, an independent NetworkX blossom computation found matching
sizes:

| Maximum matching size in $J$ | Graph count |
|---:|---:|
| 9 | 3 |
| 10 | 25 |
| 11 | 124 |
| 12 | 1,392 |

So this family is not close to the obstruction boundary: all 1,544 graphs
have four explicit two-edge colour classes, and hence strong 20-colourings.
For completeness, a disconnected 4-regular simple graph on 12 vertices has
components of order at least five, so every component has order at most seven.
A component on $r\le7$ vertices has exactly $2r\le14$ edges; colour those
edges distinctly inside the component and reuse the same palette in every
component. Thus every disconnected case uses at most 14 colours. Therefore
every 4-regular graph of order at most 12 satisfies the conjectured bound.

This catalogue conclusion does not cover nonregular graphs of order 12.

## F. Critical-conflict constraint

Let $H=L(G)^2$. If $\chi(H)=21$, take a 21-critical induced subgraph $H[S]$
on $k$ edge-vertices. Standard critical-graph theory gives
$\delta(H[S])\ge20$, hence every edge in $S$ is strongly independent from at
most $k-21$ other edges of $S$. This is sound even though edges outside $S$
may be the connectors that create adjacencies in $H[S]$. One must not replace
$H[S]$ by $L(G[S])^2$: deleting connector edges can create new induced
$2K_2$'s.

That connector caveat is essential for future encodings and invalidates a
tempting but false shortcut from a $K_{21}$ in $H$ to a 21-edge
$2K_2$-free subgraph of $G$.
