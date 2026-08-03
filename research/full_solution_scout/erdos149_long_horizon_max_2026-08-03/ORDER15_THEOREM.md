# Certificate-backed bounded theorem through order 15

Date: 2026-08-03

Status: computationally checked bounded theorem; not a full resolution of
Erdős problem #149 and not a public novelty claim.

## Theorem

Every finite simple graph `G` with `|V(G)| <= 15` and `Delta(G) <= 4`
satisfies

`chi(L(G)^2) <= 20`.

## Structural reduction

The order-at-most-14 case is frozen in `ORDER14_THEOREM.md` and
`CERTIFICATION_ORDER14.json`.  Let `G` be a smallest-order counterexample.
It is connected and has 15 vertices.  The degree-three extension lemma gives
`delta(G)>=3` and, if `t` is the number of degree-three vertices,

`3t <= 15-t`.

Also `t=60-2|E(G)|` is even.  Hence `t` is zero or two, leaving only:

* 29 edges with degree sequence `4^13 3^2`;
* 30 edges and 4-regular.

## The 29-edge slice

`N15_THETA_CORE_REDUCTION.md` proves that the radius-two equality structure
at the two degree-three vertices forces a theta core: their two
three-element neighbour sets are joined by a matching of size two or three.
After symmetry fixing, only seven vertices remain to be completed.

The primary exact enumeration has 55 incidence patterns and 492 completions
when the core matching has size two, and 94 patterns and 4,764 completions
when it has size three.  All 5,256 completions have nine disjoint
compatibility pairs, giving a strong 20-edge-colouring.

The fresh audit independently enumerates 7-edge and 8-edge subgraphs of
`K_7` by degree vector and reverse-order incidence words.  It reproduces the
counts exactly and again constructs nine pairs in every completion.

This structural enumeration replaces a canonical catalogue of 27,618,606
connected degree-sequence graphs; only the count-only `geng` measurement was
retained, avoiding a redundant roughly half-gigabyte artifact.

## The 30-edge slice

Pinned nauty `geng` generated all 805,491 connected 4-regular graphs on 15
vertices in `15_m30_4regular.g6`.  The catalogue has 16,915,311 bytes and
SHA-256

`801cbd1a228a91dc994fab3cc6e90f6e9cf36e21b6b2c581ad79250378622545`.

`verify_n15_regular.py` constructed ten disjoint compatibility pairs in all
805,491 records.  Low-first greedy matching succeeded in 805,490 graphs and
high-first succeeded in the remaining graph; no blossom fallback was needed.

`audit_n15_regular.py` uses a different graph6 decoder, set-based
compatibility, and reverse on-demand matching.  It independently recounted
805,491 graphs with `geng`, checked 257 evenly spaced records against the
NetworkX parser, and found ten pairs in every record with zero failures.

The two slices exhaust a smallest order-15 counterexample, so none exists.
Together with the frozen order-at-most-14 theorem, this proves the claim.

## Trust and claim boundary

`CERTIFICATION_ORDER15.json` records the dependency, generator, catalogue,
script, result, and audit hashes.  The 29-edge conclusion rests on a proved
local reduction plus two differently structured finite enumerations; the
30-edge conclusion rests on canonical generation plus two differently
structured full witness passes.

This theorem excludes only graphs through order 15.  It neither proves the
universal conjecture nor supplies a counterexample, and it must not be
announced as a resolution of Erdős problem #149.
