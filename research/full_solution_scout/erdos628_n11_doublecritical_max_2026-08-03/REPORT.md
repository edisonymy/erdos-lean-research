# Erdős #628: order-11 double-critical attack — priority-gate closure

Date: 2026-08-03

## Outcome

**No compute launched.**  The mandatory fresh literature gate found that the
entire proposed `n=11` search was already closed in 2010.  Kawarabayashi,
Pedersen, and Toft explicitly prove that every non-complete double-critical
6-chromatic graph has at least 12 vertices.  Their argument appears on page 8
of *Double-Critical Graphs and Complete Minors*, Electronic Journal of
Combinatorics 17(1), R87, published 2010-06-07.

A later computational cross-check, reported by Kriesell and Pedersen in 2015,
verified the Double-Critical Graph Conjecture for every graph on at most 12
vertices using Sage and `geng`.  Thus even an order-12 generic enumeration
would duplicate public work.  The assigned hard kill (`n=11` only) fires at
the priority gate.

This is a correction to the acquisition note that called 11 the “first
possible order.”  It is the first order left by the initial Gallai
decomposability bound, but it is then eliminated analytically in the same 2010
paper.  It is not the first open order.

## Faithful relation to the `(a,b)=(2,5)` Tihany case

The public Erdős #628 statement says that if a graph `G` has
`chi(G)=k>omega(G)` and `a,b>=2` with `a+b=k+1`, then `G` has two
vertex-disjoint subgraphs of chromatic numbers at least `a` and `b`.

For `(a,b)=(2,5)`, necessarily `k=6`.  The proposed decisive object was a
simple 11-vertex graph satisfying

1. `chi(G)=6`;
2. `omega(G)<6`;
3. for every edge `uv`, `chi(G-u-v)<=4`.

Such an object would rigorously refute the `(2,5)` case:

- Any subgraph of chromatic number at least 2 contains an edge, say `uv`.
- If a vertex-disjoint subgraph of chromatic number at least 5 also existed,
  it would be a subgraph of `G-u-v`.
- This would force `chi(G-u-v)>=5`, contradicting condition 3.

The converse reduction is equally exact.  If a 6-chromatic, `K6`-free graph
fails the `(2,5)` conclusion, then for every edge `uv`, the graph `G-u-v`
cannot be 5-chromatic, or the edge and `G-u-v` would be the required two
subgraphs.  Hence `chi(G-u-v)<=4`.  On the other hand, deleting two vertices
can lower chromatic number by at most two:

`chi(G) <= chi(G-u-v)+2`.

Therefore `chi(G-u-v)=4` for every edge.  The 6-chromatic component is a
non-complete double-critical 6-chromatic graph; any other components must be
isolated, since deleting the endpoints of an edge outside that component would
leave chromatic number 6.  Thus the proposed finite witness is precisely the
double-critical obstruction relevant to `(2,5)`.

## Published order-11 nonexistence argument

The following is a faithful expansion of the concise paragraph on page 8 of
Kawarabayashi--Pedersen--Toft.  It is included to show that the collision is
mathematical, not merely a stale database label.

Let `H` be a non-complete double-critical 6-chromatic graph.

1. A double-critical graph is vertex-critical.  The cited paper establishes
   the stronger local facts `delta(H)>=7`, that no two degree-7 vertices are
   adjacent, and that a non-complete example is 6-connected.
2. Gallai's theorem says that a 6-critical graph on at most `2*6-2=10`
   vertices is decomposable as a complete join.  Proposition 4.1 of the paper
   says the join factors of a double-critical graph are themselves
   double-critical.  Their chromatic numbers sum to 6, so each factor has
   chromatic number at most 5 and is therefore complete by the already solved
   low-chromatic cases.  Their complete join is `K6`, a contradiction.
   Hence a non-complete example has at least 11 vertices.
3. Suppose now that `|V(H)|=11`.  The paper notes that `H` is indecomposable
   and uses the critical-graph degree restriction excluding degree
   `|V(H)|-2=9`.  A universal vertex would also decompose `H`.  Combined with
   `delta(H)>=7`, the prohibition on adjacent degree-7 vertices, and parity,
   this forces a vertex `x` of degree 8.
4. Let `y,z` be the two vertices outside the closed neighbourhood `N[x]`.
   They must be adjacent.  Indeed, the neighbourhood graph `H[N(x)]` is
   3-colourable by the paper's Proposition 3.11.  If `y,z` were nonadjacent,
   then `{x,y,z}` could share a fourth colour, contradicting `chi(H)=6`.
5. Since `yz` is an edge and `H` is double-critical,
   `chi(H-y-z)=4`.  But `H-y-z` is the join of the single vertex `x` and the
   neighbourhood graph `H[N(x)]`, so `chi(H[N(x)])=3`.
6. Colour `H[N(x)]` with three colours, give `x` and `y` a fourth colour
   (they are nonadjacent), and give `z` a fifth.  This is a 5-colouring of
   `H`, contradicting `chi(H)=6`.

Therefore no non-complete double-critical 6-chromatic graph has 11 vertices.
In particular, the decisive object specified for this attack cannot exist.

## Fresh priority audit

- The live #628 page was crawled in June 2026 and remains marked falsifiable;
  its October 2025 discussion points to Song's survey and Longbrake--Tariq's
  newer positive special cases.  No complete resolution is claimed.
- The exact order-11 result is nevertheless old and explicit in the 2010
  primary source.  Database openness refers to the full unbounded Tihany
  conjecture, not to this finite order.
- Longbrake--Tariq, arXiv:2406.15164 (2024-06-21; subsequently published),
  concerns claw-free/special clique cases and does not reopen order 11.
- Kriesell--Pedersen (DMTCS, 2015) state that Sage/`geng` verified the
  Double-Critical Graph Conjecture for all graphs on at most 12 vertices.

Exact URLs and dates are in `SOURCES.md`.

## Compute ledger and hard kill

The predeclared CEGAR/SAT pulse was not started:

- graph models proposed: 0;
- CEGAR iterations: 0;
- colouring separators: 0;
- SAT/UNSAT cases: 0;
- timeouts: 0;
- solver CPU time: 0;
- candidate files: 0.

Reason: the literature gate proves the target set empty and establishes prior
publication.  Running the encoder would add no discovery or priority value.

The hard kill is final for this lane: do not expand to `n=12`, both because the
assignment forbids it and because the published computational check already
covers that order.  Any future #628 attack should begin above the published
finite frontier and only after a fresh structural/literature audit; this
package makes no recommendation to do so within the current one-week campaign.

## Claim boundary

This package makes no new theorem claim and no claim to solving Erdős #628.
It records a priority collision, corrects target selection, and explains why
the proposed object would have been decisive but is already known not to
exist.
