# Erdős #149: order-12, 22-edge obstruction

**Date:** 3 August 2026

**Status:** certificate-backed bounded result, pending an independent
definition-level audit of the mathematical-to-CNF mapping

**Full Erdős #149 solution:** no

## Exact bounded claim

Every finite simple graph on 12 vertices with maximum degree at most four and
exactly 22 edges has strong chromatic index at most 20.

This closes the 22-edge slice of the previously uncovered nonregular order-12
case.  A second checked certificate also closes the part of the 23-edge slice
whose compatibility graph contains a triangle.  The remaining order-12 case
has 23 edges and a triangle-free compatibility graph with matching number
exactly two.  The completed 4-regular catalogue already covers 24 edges, and
the CGTT extremal theorem handles 21 edges.

## Reduction

For a graph `G`, let `J(G)` have one vertex for every edge of `G`; two vertices
of `J(G)` are adjacent exactly when their two `G`-edges form an induced
matching.  Cliques of `J(G)` are precisely strong-edge-colour classes.

Assume `G` has 22 edges, maximum degree at most four, and needs at least 21
strong colours.

1. `J(G)` is nonempty.  Otherwise `G` is a subquartic `2K2`-free graph with 22
   edges, contradicting the Chung--Gyárfás--Tuza--Trotter upper bound of 20.
2. `J(G)` has no triangle: a compatible triple, with the other 19 graph edges
   coloured singly, gives 20 colours.
3. `J(G)` has no matching of size two: two disjoint compatible pairs, with the
   other 18 graph edges coloured singly, also give 20 colours.
4. Every nonempty triangle-free graph with matching number at most one is a
   star.  Relabel its centre graph-edge as `01` and one leaf graph-edge as
   `23`.

The exact CNF enforces a simple graph on 12 labelled vertices, maximum degree
four, exactly 22 edges, compatibility of `01` and `23`, and the requirement
that every compatibility edge involves `01`.  This symmetry-fixed formula is
therefore satisfiable if and only if the bounded obstruction exists.

## Exact computation

The formula has 2,338 variables and 6,026 clauses.  CaDiCaL 1.9.5 at pinned
commit `146207318796f094dcded87349a64f0c6927309e` returned UNSAT and emitted a
binary DRAT certificate.  The independently pinned `drat-trim` build reported
`s VERIFIED` and converted the proof to LRAT.  A separately compiled native
Windows `lrat-check` then reported `c VERIFIED`:

```text
c parsed a formula with 2338 variables and 6026 clauses
c VERIFIED
c Added clauses = 336139. Deleted clauses = 336063. Max live clauses = 9858
```

Hashes, byte counts, checker identities, and the exact scope boundary are in
[`CERTIFICATION.json`](CERTIFICATION.json).

## The 23-edge triangle-containing slice

For 23 edges, needing at least 21 colours is equivalent to the maximum total
clique-packing saving in `J(G)` being at most two.  If `J(G)` contains a
triangle, relabel its three graph-edges as the induced matching
`T={01,23,45}`.  Any saving of three then has one of the following forms:

- a compatibility edge disjoint from `T`;
- a `K4` containing `T`;
- another triangle using one outside vertex and two vertices of `T`, together
  with a disjoint compatibility edge; or
- a matching of size three.

The second exact CNF forbids precisely these patterns while enforcing 12
vertices, 23 edges, and maximum degree four.  It has 2,509 variables and
86,313 clauses.  Pinned CaDiCaL returned UNSAT; pinned `drat-trim` reported
`s VERIFIED`, and native `lrat-check` independently reported:

```text
c parsed a formula with 2509 variables and 86313 clauses
c VERIFIED
c Added clauses = 392988. Deleted clauses = 392865. Max live clauses = 86313
```

## Trust boundary and next work

The two certificate replays prove the exact DIMACS formula UNSAT.  They do not
by themselves prove that the formula faithfully represents the mathematical
star obstruction.  Before any public bounded-theorem update, a fresh reviewer
must independently audit the cardinality encodings, the compatibility
clauses, the symmetry reduction, and the CGTT hypothesis mapping.

The next full-resolution-facing slice is the triangle-free 23-edge case.
Repeated application of the CGTT edge bound forces its compatibility graph to
have a matching of size two, while a counterexample forces it to have no
matching of size three.  The next encoding should exploit a fixed maximum
matching and Berge augmenting-path constraints rather than enumerate all
subquartic graphs blindly.
