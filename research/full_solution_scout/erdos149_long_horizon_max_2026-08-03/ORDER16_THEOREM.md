# Certificate-backed bounded theorem through order 16

Date: 2026-08-03

Status: computationally checked bounded theorem; not a full resolution of
Erdős problem #149 and not a public novelty claim.

## Theorem

Every finite simple graph `G` with `|V(G)| <= 16` and `Delta(G) <= 4`
satisfies

`chi(L(G)^2) <= 20`.

## Exhaustive reduction

The order-at-most-15 case is frozen in `ORDER15_THEOREM.md` and
`CERTIFICATION_ORDER15.json`.  If an order-16 counterexample existed, choose
one of smallest order.  It is connected and has minimum degree at least
three.  The degree-three neighbourhood-packing bound leaves exactly three
profiles:

* four degree-three vertices and 30 edges;
* two degree-three vertices and 31 edges;
* no degree-three vertices and 32 edges, hence 4-regular.

`N16_CORE_REDUCTION.md` proves the exact local reductions for the first two
profiles.

## Nonregular profiles

For four degree-three vertices, the remaining twelve vertices induce a
cubic triangle-free graph and the four attachment triples must be independent
in its square.  Among all 94 cubic 12-vertex cores, exactly one admissible
core/partition remains, and it has ten disjoint compatibility pairs.

For two degree-three vertices, their neighbour sets are joined by a matching
of size one, two, or three.  Exact completion of the remaining eight vertices
gives 10,872, 75,552, and 362,348 cases respectively.  All 448,772 cases have
eleven disjoint compatibility pairs.

Both reductions and all finite counts were replayed by an independently
structured `K8` subset / NetworkX-square audit, with no failures.

## The 4-regular profile

Pinned nauty `geng` reports exactly 8,037,418 connected 4-regular graphs on
16 vertices.  To keep disk bounded, the catalogue was never materialized.
Instead, its canonical residue partition

`geng -q -c -d4 -D4 16 32 RESIDUE/16`, for `RESIDUE=0,...,15`,

was streamed directly into two full witness passes.

The primary checker uses a bit-mask graph6 decoder, prebuilds the complete
compatibility graph, and constructs a matching of twelve compatibility
edges.  The 16 shard counts sum exactly to 8,037,418.  Low-first matching
succeeds on 8,030,289 records and high-first on the remaining 7,129; no exact
fallback or candidate occurs.

The independent replay uses a bit-string decoder, neighbour sets, and
reverse on-demand induced-`2K2` tests without constructing the primary
compatibility graph.  It reproduces every shard record count and exact stream
SHA-256.  Reverse matching succeeds on 8,036,737 records; NetworkX blossom
finds a perfect compatibility matching of size 16 in each of the remaining
681.  All 144 evenly spaced NetworkX graph6 parser checks agree and no
candidate occurs.

Twelve compatibility pairs save twelve colours from 32, so every graph in
the regular slice has a strong 20-edge-colouring.

The three profiles exhaust a smallest order-16 counterexample, completing
the bounded theorem.

## Trust and claim boundary

`CERTIFICATION_ORDER16.json` records all theorem dependencies, core search
hashes, generator provenance, primary/replay shard manifests, stream hashes,
counts, and meta-audit results.  No regular catalogue or large proof file is
needed for reproduction.

This theorem excludes only graphs through order 16.  It neither proves the
universal conjecture nor supplies a counterexample, and it must not be
announced as a resolution of Erdős problem #149.
