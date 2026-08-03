# Claims ledger: threshold-seven line-graph audit

Date: 2026-08-03

## Main claim

> Every finite simple graph in which every vertex belongs to at most seven
> triangles has a red/blue edge-colouring with no monochromatic triangle.

Equivalent contrapositive: every graph arrowing `(3,3)` has a vertex in at
least eight triangles.

Status: **PROVED**, conditional only on the cited published Hell--Zhu and
Goldberg--Seymour theorems.  A full standalone derivation is in `REPORT.md`.

## Structural claims

1. A minimal `(3,3)`-arrowing core has every edge in at least two triangles,
   and every vertex link is a connected, nonuniversally-adaptable graph of
   minimum degree at least two and at most seven edges.  **PROVED**.

2. The exact possible links are `K4`, bowtie, `Djs`, and two disjoint
   triangles joined by one edge.  **PROVED** using Hell--Zhu plus a hand
   classification; also **COMPUTATIONALLY VERIFIED** independently from the
   adaptable-colouring definition on all 1,618 labelled candidates.

3. `K4` links are impossible under the seven-triangle bound.  **PROVED**.

4. `Djs` links propagate along a degree-three link vertex and force adjacent
   true twins inside `Djs`, which do not exist.  Hence `Djs` is impossible.
   **PROVED**; all local signatures **COMPUTATIONALLY VERIFIED**.

5. If all links are bowties or joined triangles, the collection of all
   `K4`s gives a relaxed Krausz cover.  The direct intersection construction
   realizes the core as `L(H)` for a connected loopless 4-regular
   multigraph `H`.  **PROVED**.

6. Every such root arising here has `Gamma(H)<=5`; the only possible
   three-vertex exception is the doubled triangle, whose line graph is
   `K6` and is excluded.  Goldberg--Seymour then gives `chi'(H)<=5`.
   **PROVED**.

7. Every 5-colourable graph is nonarrowing for `(3,3)` by pullback of the
   red-cycle/blue-complement colouring of `K5`.  **PROVED** and
   **COMPUTATIONALLY VERIFIED** at the finite endpoint.

## Boundaries

This package does not claim a full solution of Erdos #151, priority for the
theorem, a threshold-eight statement, or independent proofs of the two
published external theorems.

