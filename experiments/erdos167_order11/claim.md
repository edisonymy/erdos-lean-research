# Claim and proof boundary

## Bounded claim

Assume:

1. Puleo's theorem that every graph of maximum average degree strictly below
   seven satisfies Tuza's inequality;
2. nauty's `geng` output contains one representative of every requested
   simple-graph isomorphism class and `labelg` computes canonical labels.

Then every simple graph `G` with at most eleven vertices satisfies
`tau(G) <= 2 nu(G)`.

## Deduction

Pad `G` with isolated vertices to order eleven. This preserves its triangles,
`tau`, and `nu`. If the padded graph violated Tuza, Puleo's theorem would imply
that some subgraph `H` has average degree at least seven. Replacing `H` by the
induced graph on the same vertices cannot decrease its edge count. Put
`h=|V(H)|`. Simplicity gives `h >= 8`, while
`|E(H)| >= ceil(7h/2)`.

Let `C` be the complement of `G`.

- If `h=11`, then `|E(G)| >= 39`, hence `|E(C)| <= 16`.
- If `h=10`, deleting the outside vertex from `C` leaves at most
  `45-35=10` edges.
- If `h=9`, deleting the two outside vertices leaves at most
  `36-32=4` edges.
- If `h=8`, then `H=K8`, so deleting the three outside vertices from `C`
  leaves no edge.

The constructors in `ResidualTools.cs` exhaust these four cases. For a fixed
deleted set, using one unlabeled representative of the retained graph and all
possible incident edges is complete: an isomorphism to the representative
transports those incident-edge choices. In the three-deletion case the eight
retained vertices are independent; up to their relabeling, their neighborhoods
in the deleted triple are exactly a multiset of eight elements of a set of
eight types. The three possible edges inside the triple are then arbitrary.
Canonical labeling and set union remove repetitions between choices and
families.

For every union representative, `Program.cs` explicitly constructs an
edge-disjoint triangle packing of size `p`. It also enumerates bipartitions and
uses the graph edges internal to the two sides as a cover of size `c`; a
triangle cannot be entirely cross-partition, so this is always a triangle
cover. The computed check `c <= 2p` therefore proves

`tau(G) <= c <= 2p <= 2nu(G)`.

`IndependentVerify.cs` repeats this implication with independent decoding,
packing orders, and cut enumeration.

## What is not claimed

- no result for graphs on twelve or more vertices;
- no proof or disproof of the full Erdos 167 / Tuza conjecture;
- no exact values of `tau` or `nu` for these order-eleven graphs;
- no Lean-checked theorem;
- no unconditional novelty or priority claim beyond the documented public
  searches performed on 2026-08-01.

The finite proof depends on nauty enumeration/canonicalization rather than a
formally verified graph generator. The cross-version byte-identical replay in
`audit.md` is evidence for that trust boundary, not its elimination.
