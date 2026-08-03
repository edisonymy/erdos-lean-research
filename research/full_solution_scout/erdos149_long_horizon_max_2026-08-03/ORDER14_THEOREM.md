# Certificate-backed bounded theorem through order 14

Date: 2026-08-03

Status: computationally checked bounded theorem; not a full resolution of
Erdős problem #149 and not a public novelty claim.

## Theorem

Every finite simple graph `G` with `|V(G)| <= 14` and `Delta(G) <= 4`
satisfies

`chi(L(G)^2) <= 20`.

## Structural reduction

The order-at-most-13 case is frozen in `ORDER13_THEOREM.md` and
`CERTIFICATION_ORDER13.json`.  Suppose `G` is a smallest-order
counterexample.  Then `G` is connected, has exactly 14 vertices, and the
degree-three extension lemma gives `delta(G) >= 3`.

Let `t` be the number of degree-three vertices.  Distinct degree-three
vertices have distance at least three and all their neighbours have degree
four.  Their three-element neighbourhoods are therefore disjoint subsets of
the `14-t` degree-four vertices, so

`3t <= 14-t`.

The degree sum gives `t=56-2|E(G)|`, hence `t` is even.  The inequality gives
`t<=3`, so `t` is zero or two.  Only two connected slices remain:

* `t=2`, `|E(G)|=27`, degree sequence `4^12 3^2`;
* `t=0`, `|E(G)|=28`, 4-regular.

## Exhaustive slice checks

Pinned nauty `geng` generated the catalogues canonically:

* `geng -q -c -d3 -D4 14 27 14_m27_min3.g6` produced 2,771,069 records,
  52,650,311 bytes, SHA-256
  `2ce9cbfdaeaad95ae2b897aeb589996573175d8ceb89c1e3fabe5020878ae610`;
* `geng -q -c -d4 -D4 14 28 14_m28_4regular.g6` produced 88,168 records,
  1,675,192 bytes, SHA-256
  `0ba93c3c6d8bd00bd0b0fff7513a0873f22c3d68e5160bc04df41e346c5d822c`.

Independent count-only invocations returned the same record counts.

For a graph `G`, let `J(G)` have vertex set `E(G)`, with two vertices
adjacent when the corresponding G-edges induce `2K2`.  A matching of size
`|E(G)|-20` in `J(G)` partitions that many pairs into induced matchings and
leaves 20 colour classes in total.

`verify_n14_slices.py` directly built the compatibility adjacency masks and
found:

* seven disjoint compatibility pairs in all 2,771,069 graphs at 27 edges;
* eight disjoint compatibility pairs in all 88,168 graphs at 28 edges.

The deterministic low-first construction succeeded on every record, so no
fallback solver or inferred optimum is involved.

`audit_n14_slices.py` independently decoded graph6 through bit strings,
tested compatibility with neighbour sets, and constructed the pairs in
reverse edge order on demand, without building the primary checker's
compatibility graph.  It reproduced every witness count, checked connectedness
and the exact degree sequence of every record, matched the independent `geng`
counts, and found zero discrepancies in 257 evenly spaced NetworkX parser
comparisons per slice.

Both exhaustive slices are therefore strongly 20-edge-colourable.  They
exhaust a smallest order-14 counterexample, completing the bounded theorem.

## Trust and claim boundary

`CERTIFICATION_ORDER14.json` records all generator, catalogue, script, result,
and dependency hashes.  Completeness relies on the pinned nauty generator;
the compatibility witnesses were fully replayed by two differently
structured checkers.

This theorem excludes only graphs through order 14.  It neither proves the
universal conjecture nor supplies a counterexample, and it must not be
announced as a resolution of Erdős problem #149.
