# Certificate-backed bounded theorem through order 13

Date: 2026-08-03

Status: computationally checked bounded theorem; not a full resolution of
Erdős problem #149 and not a public novelty claim.

## Theorem

Every finite simple graph `G` with `|V(G)| <= 13` and `Delta(G) <= 4`
satisfies

`chi(L(G)^2) <= 20`.

## Reduction to two catalogues

The order-at-most-12 case is proved in `ORDER12_THEOREM.md` and certified by
`CERTIFICATION.json`.  Suppose, for a contradiction, that `G` is a
smallest-order counterexample.  It therefore has exactly 13 vertices.  It is
connected, since otherwise a counterexample component would have at most 12
vertices.

The degree-three extension lemma in `MINIMAL_COUNTEREXAMPLE_LOCAL.md` gives
`delta(G) >= 3`.  It also says that distinct degree-three vertices have
distance at least three and that all their neighbours have degree four.  If
`t` vertices have degree three, their three-element neighbourhoods are
pairwise disjoint subsets of the `13-t` degree-four vertices.  Consequently

`3t <= 13-t`.

Since every degree is three or four, the degree sum gives

`t = 52 - 2|E(G)|`.

Thus `t` is even and at most three, so `t` is zero or two.  Every possible
counterexample is therefore in exactly one of these slices:

* `t=2`, `|E(G)|=25`, degree sequence `4^11 3^2`;
* `t=0`, `|E(G)|=26`, 4-regular.

This structural step eliminates the stalled order-13 edge-count 22, 23 and
24 SAT gates without drawing any conclusion from their timeouts.

## The 25-edge slice

Pinned nauty `geng` generated every connected unlabeled graph satisfying the
slice constraints with

`geng -q -c -d3 -D4 13 25 13_m25_min3.g6`.

The catalogue has 300,361 records, 4,805,776 bytes, and SHA-256
`fb25f684d2d15d3cb6a77a796d1f8fe487d545d72f92251b4a3ef0437c456f1c`.
An independent count-only invocation reported the same 300,361 graphs, and
all stored records are distinct.

For each graph, `verify_n13_almost_regular.py` directly constructed the
compatibility graph on `E(G)` and found five vertex-disjoint compatibility
edges.  All 300,361 deterministic first-fit searches succeeded, so no exact
matching fallback was needed.  Pairing the ten corresponding G-edges into
five induced matchings and colouring the remaining 15 edges singly gives a
strong 20-edge-colouring.

`audit_n13_almost_regular.py` is a separately structured replay.  It uses a
different graph6 decoder, set-based compatibility tests, and reverse-order
greedy matchings.  It again found five pairs in every one of the 300,361
graphs, rechecked the `geng` count, and found zero mismatches in 257
evenly-spaced NetworkX graph6 parser comparisons.

## The 26-edge slice

The public catalogue of all 10,778 connected 4-regular graphs on 13 vertices
has SHA-256
`bce601e43bf1f6274c6d550c112196ff1c5f5c167ca8aa40eabb4e779da168cd`.
The exact NetworkX blossom replay found compatibility matching numbers 10,
11, 12 and 13 with multiplicities 1, 18, 108 and 10,651.  Six pairs suffice
to save six colours from 26.

A fresh reverse-order greedy checker independently found six disjoint
compatibility pairs in all 10,778 records, with no failures.  The two result
files are `n13_4regular_result.json` and
`n13_4regular_fresh_audit.json`.

The two slices exhaust a smallest order-13 counterexample, so none exists.
Together with the order-at-most-12 theorem, this proves the stated bounded
result.

## Trust and claim boundary

The machine-readable dependency hashes and audit outcomes are recorded in
`CERTIFICATION_ORDER13.json`.  Completeness of the two finite slices relies
on their catalogue generators; compatibility and matching claims have two
independently structured replays in each relevant slice.

This theorem excludes only graphs through order 13.  It neither proves the
universal 20-colour bound nor supplies a counterexample, and it must not be
announced as a resolution of Erdős problem #149.
