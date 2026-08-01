# Erdos Problem 167 / Tuza through order 11

This directory contains a reproducible, independently replayed computation
showing that every simple graph on at most eleven vertices satisfies

\[
  \tau(G) \le 2\nu(G),
\]

where `nu` is the maximum number of pairwise edge-disjoint triangles and `tau`
is the minimum number of edges meeting every triangle.

This is a **bounded result only**. It does not solve Tuza's conjecture for
arbitrary finite graphs, and it is not a Lean proof. The deduction uses
Puleo's published theorem for graphs of maximum average degree below seven and
the completeness of the non-isomorphic graph generation performed by nauty
`geng`/`labelg`.

## Structural reduction

It is enough to handle graphs on exactly eleven vertices, because isolated
vertices change neither invariant. If an order-eleven graph `G` could violate
Tuza, Puleo's theorem would give a subgraph on `h >= 8` vertices with at least
`ceil(7h/2)` edges. For its complement `C`, at least one condition follows:

- `h=11`: `|E(C)| <= 16`;
- `h=10`: `|E(C-v)| <= 10` for some vertex `v`;
- `h=9`: `|E(C-{u,v})| <= 4` for some pair;
- `h=8`: `C-{u,v,w}` has no edges for some triple.

The four families are generated without scanning the 1,018,997,864-class
order-eleven catalogue:

- `geng 11 0:16` gives 1,850,130 representatives of the first family;
- extend each of the 4,577 representatives from `geng 10 0:10` by one
  arbitrarily adjacent vertex;
- extend each of the 20 representatives from `geng 9 0:4` by two arbitrarily
  adjacent vertices;
- for the last family, enumerate the multiset of the eight independent
  vertices' neighborhoods in the remaining triple, together with its three
  internal edges (51,480 distinguished records).

Canonical labeling and union produce **2,174,357** classes, with normalized
graph6 SHA-256
`5997409f26372eea577b7a6bec6b94e3f26282ba7ba5473ae9f54ab69ad98889`.

## Witness result

For every residual graph the primary screen constructs:

- `p` pairwise edge-disjoint triangles, proving `p <= nu(G)`;
- a bipartition and the `c` graph edges internal to its two sides. Every
  triangle has an internal edge, so these edges form a triangle cover and
  `tau(G) <= c`.

All 2,174,357 classes satisfy `c <= 2p`, directly giving
`tau(G) <= c <= 2p <= 2nu(G)`. This is a witness inequality, not an inference
from an uncertified optimizer.

The primary implementation closed every class with minimum slack `2p-c = 1`.
An independently written verifier uses a separate graph6 decoder, different
greedy packing orders, and a Gray-code maximum-cut implementation; it closed
every class with minimum slack zero and also checked that every retained graph
satisfies the Puleo residual predicate.

## Reproduction

Requirements are .NET 8 and nauty executables `geng` and `labelg`. The full
run needs roughly 450 MB of temporary disk space. From PowerShell:

```powershell
.\run.ps1 `
  -Geng C:\path\to\geng.exe `
  -Labelg C:\path\to\labelg.exe `
  -WorkDirectory C:\temporary\tuza-order11
```

The script builds all three programs, regenerates and canonicalizes all four
families, checks the exact residual count and digest, runs both witness
screens, and writes a tool manifest. `full_summary.json`,
`independent_summary.json`, and `residual_summary.json` retain the audited
results. The empty `full_unresolved.g6` is the primary screen's unresolved
output.

See `claim.md` for the proof boundary, `audit.md` for cross-version and public
claim checks, and `sources.md` for primary sources.
