# Order-16 nonregular core reductions

Date: 2026-08-03

Status: proved reductions with two independently checked finite completion
spaces; not a full universal result.

## Degree profiles

Let `G` be a smallest-order subquartic graph with no strong
20-edge-colouring and suppose `|V(G)|=16`.  The degree-three extension lemma
gives `delta(G)>=3`.  If `t` vertices have degree three, their three-element
neighbourhoods are disjoint subsets of the `16-t` degree-four vertices, so

`3t <= 16-t`.

Also `t=64-2|E(G)|` is even.  Thus only `t=4,2,0` are possible, with 30, 31,
32 edges respectively.

## Four degree-three vertices

Let `D` be the four degree-three vertices and `R` the twelve degree-four
vertices.  Vertices of `D` are pairwise at distance at least three.  Their
four disjoint neighbourhoods each have size three and together exhaust `R`.
Every vertex of `R` therefore has one neighbour in `D` and three in `R`, so
`H=G[R]` is cubic.

For a vertex `u` of `R`, the three H-neighbours of `u` are pairwise
nonadjacent by the local equality lemma at its unique neighbour in `D`.
Hence `H` is triangle-free.  For each `d` in `D`, no triangle or 4-cycle
through `d` means that the three vertices of `N(d)` are pairwise at distance
at least three in `H`; equivalently, each attachment triple is independent in
`H^2`.

All 94 cubic graphs on 12 vertices were generated.  Seventy-one contain a
triangle.  Among the 23 triangle-free cores, exactly one admits a partition
of its vertices into four `H^2`-independent triples.  Its associated
30-edge graph has ten disjoint compatibility pairs.

`n16_t4_core_search.py` performs the primary bit-mask check.
`audit_n16_cores.py` reparses the cores with NetworkX, constructs `H^2`
directly, and independently reproduces all counts and the ten-pair witness.

## Two degree-three vertices

Call the degree-three vertices `a,b`, with `U=N(a)` and `W=N(b)`.  The local
equality lemma gives `|B_2(a)|=|B_2(b)|=13`.  Since `b` and only two further
vertices can lie outside `B_2(a)`, at least one vertex of `W` has a neighbour
in `U`.  As in the order-15 reduction, the `U-W` edges form a matching, now
of size `r in {1,2,3}`.

There are eight remaining vertices, called `X`.  A U-vertex incident with a
core matching edge has two X-neighbours; an unmatched U-vertex has three.
These U-blocks are disjoint, with sizes

* `(2,3,3)` when `r=1`;
* `(2,2,3)` when `r=2`;
* `(2,2,2)` when `r=3`.

They cover respectively 8, 7, or 6 vertices of `X`; the W-blocks satisfy the
same rules.  Matched U- and W-blocks are disjoint, and every block is
independent.  Since all X-vertices have degree four, the remaining graph on
`X` is determined by exact residual degrees subject to these forbidden
within-block edges.

The primary residual-degree enumeration found:

* `r=1`: 300 W-patterns and 10,872 completions;
* `r=2`: 524 W-patterns and 75,552 completions;
* `r=3`: 475 W-patterns and 362,348 completions.

Every one of the 448,772 completions has eleven disjoint compatibility
pairs.  The fresh audit independently enumerates all relevant 8-, 9-, and
10-edge subsets of `K8`, buckets them by degree vector, and reproduces every
incidence, completion, and matching count.

Thus neither nonregular degree profile can contain a smallest order-16
counterexample.

## Claim boundary

This document proves the finite reductions used by the two nonregular
checks.  It does not cover the 4-regular slice; that slice is handled by the
separate streaming catalogue passes in the order-16 certification package.
