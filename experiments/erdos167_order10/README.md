# Erdős Problem 167 / Tuza through order 10

This directory contains a reproducible, independently replayed computation
showing that every simple graph on at most ten vertices satisfies

\[
  \tau(G) \le 2\nu(G),
\]

where `nu` is the maximum number of pairwise edge-disjoint graph triangles and
`tau` is the minimum number of graph edges meeting every triangle.

This is a **bounded result only**.  It does not solve Tuza's conjecture for
arbitrary finite graphs.  The exact computation handles order ten; every
smaller graph follows by adding isolated vertices, which changes neither its
triangles nor `tau` or `nu`.  The public July 24 through-order-nine computation
is therefore a priority baseline, not a logical dependency.

## Completeness reduction

It is enough to consider exactly ten vertices: pad any smaller graph with
isolated vertices. Puleo proved Tuza's conjecture for every graph with maximum
average degree strictly less than seven. Hence a counterexample `G` on ten vertices would
contain a subgraph `H` of average degree at least seven.  Simplicity forces
`|V(H)|` to be 8, 9, or 10, with respectively

- 28 edges, so `H = K8`;
- at least 32 edges;
- at least 35 edges.

For the complement `C` of an order-ten graph, the residual predicate is
therefore the union of

- `|E(C)| <= 10`;
- `|E(C-v)| <= 4` for some vertex `v`;
- all complement edges are covered by some pair of vertices `{u,v}`.

Brendan McKay's official order-ten catalogue has 12,005,168 non-isomorphic
simple graphs.  Complementation preserves isomorphism, and the exact residual
screen selects 4,769 classes.

## Result

- official catalogue records: **12,005,168**;
- residual isomorphism classes: **4,769**;
- exact violations `tau > 2*nu`: **0**;
- equality cases in the residual: **0**;
- maximum residual gap `tau - 2*nu`: **-4**;
- primary record digest:
  `f57a18bcb2c8c7b821f85f73e02ad768b352416fa17ff4e8fe694ad6dd40c047`.

The seven closest classes have `(nu,tau)=(8,12)`.

## Exact optimizers

`solve_exact.py` uses integer bit masks only.

For packing, selected triangles form an Eulerian edge union whose cardinality
is divisible by three.  A parity/cardinality dynamic program gives an upper
bound.  A greedy packing is the lower witness; when the bounds do not meet, an
exact maximum-clique search on the triangle compatibility graph closes the
instance.

For covering, every vertex cut supplies a triangle-free retained subgraph and
Mantel's theorem on every induced vertex subset supplies a retained-edge upper
bound.  When those bounds do not meet, the exact recurrence branches on the
three edges of an uncovered triangle, with an edge-disjoint triangle packing
as a lower bound.

`independent_verify.py` starts again from NetworkX's graph6 decoder.  It checks
every stored packing and cover witness, then proves that no packing of size
`nu+1` and no cover of size `tau-1` exists.  It closes 4,653 packing instances
by a separately recomputed parity/cardinality bound and 116 by an edge-pivot
decision search; it closes 849 covers by induced Mantel bounds and 3,920 by a
separate bounded hitting decision search.

## Reproduction

Python 3.11+ and Node.js are sufficient; the independent verifier also needs
NetworkX.

```powershell
curl.exe -L -o graph10.g6.gz `
  https://users.cecs.anu.edu.au/~bdm/data/graph10.g6.gz
Get-FileHash graph10.g6.gz -Algorithm SHA256

python screen_catalogue.py graph10.g6.gz residual_complements.g6 screen_summary.json
node independent_screen.js graph10.g6.gz independent_screen_summary.json independent_residual.g6

python solve_exact.py residual_complements.g6 exact_records.replay.jsonl exact_summary.replay.json
python independent_verify.py exact_records.replay.jsonl independent_verify.replay.json
```

Expected catalogue SHA-256:
`a16f47a95e3e174f4b08042fec95dce8b67712b0e465b5097ffd9334dde2faf8`.
Both screeners must report 12,005,168 catalogue records, 4,769 residual
records, and residual SHA-256
`a91c1ad52596a676edae8ff67fcd08490d6da80d757e3d92ebc13c529fafd130`.
Both exact passes must report zero violations, maximum gap `-4`, and record
SHA-256 `f57a18bcb2c8c7b821f85f73e02ad768b352416fa17ff4e8fe694ad6dd40c047`.

See `claim.md` for the proof boundary, `audit.md` for the independent-gate
history, and `sources.md` for sources and the public-priority check.
