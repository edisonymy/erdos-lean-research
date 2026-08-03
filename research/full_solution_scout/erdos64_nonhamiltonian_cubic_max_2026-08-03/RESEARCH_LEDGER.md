# Erdos problem 64 successor research ledger

Entries distinguish `PROVED`, `COMPUTATIONALLY CHECKED`, `HEURISTIC`, and
`FAILED`.  This packet inherits the immutable predecessor target hash
`1944398AE0DB9EB1FB5BCE122BB59306551330B7C3B1D915593EC8EDAF580EFB`.

## Entry 000 - target, priority, and route freeze

- Status: `PROVED` at the definition level; priority remains search-relative.
- Action: froze the exact finite-simple-graph statement and the
  `S-NONHAM-CUBIC-CANONICAL` route before computation.
- Precommit: every connected cubic graph through order 20 would have empty
  dyadic edge core; any survivor would be dumped immediately and checked by
  two independent parsers/cycle finders.
- Artifact: `TARGET_PRIORITY_FREEZE.md`, `ROUTE_FINGERPRINT.md`.

## Entry 001 - canonical generator acquisition and count validation

- Status: `COMPUTATIONALLY CHECKED` exact finite generation.
- Action: downloaded official nauty 2.9.3 source, recorded archive and source
  hashes, compiled `geng` in a digest-identified local Linux container, and
  generated connected simple cubic graph6 streams at every even order 4--20.
- Counts: `1,2,5,19,85,509,4060,41301,510489`, totaling 556,471.
- Independent boundary: every count and Hamiltonian split matches the
  separately published Flinders/GENREG table.
- Artifact: `GENERATOR_PROVENANCE.md`, `CENSUS_SHA256SUMS.txt`, `cubic_n*.g6`.

## Entry 002 - exact Hamiltonicity and marked-edge scan

- Status: `COMPUTATIONALLY CHECKED`, complete through cubic order 20.
- Hamiltonicity language: enumerate perfect matchings; a cubic graph is
  Hamiltonian exactly when some complementary 2-factor is connected.
- Non-Hamiltonian counts: `0,0,0,2,5,35,219,1666,14498`, totaling 16,425.
- Core language: find one dyadic cycle, then for each of its edges search for
  a dyadic cycle avoiding that edge.  This is exactly the literal full-cycle
  intersection test.
- Result: all 556,471 cores are empty.  No graph lacks dyadic cycles, no core
  edge survives, and no candidate file was emitted.
- Prediction: confirmed at the predeclared order-20 gate.
- Artifact: `canonical_scan_through_n20.json`.

## Entry 003 - independent full replay and separate catalogue replay

- Status: `COMPUTATIONALLY CHECKED` by a separately written parser and cycle
  algorithm.
- Independent language: decode graph6 through a materialized bit string and
  literally intersect enumerated dyadic-cycle edge masks; import no producer
  code.
- Result A: all 556,471 primary census records independently have empty core.
- Result B: all 14,498 graphs in Flinders' separate order-20 non-Hamiltonian
  GENREG catalogue have empty core.
- Result C: all 148,790 graphs in Flinders' complete order-22
  non-Hamiltonian catalogue have empty core.
- Scope: Result C says nothing about the 7,170,657 Hamiltonian order-22
  graphs.
- Artifacts: `canonical_full_census_independent_core_audit.json`,
  `flinders_n20_nonham_independent_core_audit.json`, and
  `flinders_n22_nonham_independent_core_audit.json`.

## Entry 004 - small empty-intersection certificate structure

- Status: `COMPUTATIONALLY CHECKED`; generalization is `CONJECTURAL`.
- Mechanism: search first for two edge-disjoint dyadic cycles.  For exceptions,
  enumerate every dyadic cycle mask and use breadth-first intersection search
  to determine the exact minimum certificate size.
- Full through order 20: 555,727 graphs have a two-cycle certificate and 744
  require exactly three; none require four.
- Non-Hamiltonian order 20: 14,494 have width two and four have width three.
- Non-Hamiltonian order 22: 148,787 have width two and three have width three.
- Interpretation: this sharply compresses the finite exclusions but does not
  prove a universal width-three theorem.
- Artifacts: `cubic_n*_dyadic_pair_structure.json`,
  `flinders_n20_dyadic_pair_structure.json`, and
  `flinders_n22_dyadic_pair_structure.json`.

## Entry 005 - adjacent-terminal triangle reduction

- Status: `PROVED`; finite audit `COMPUTATIONALLY CHECKED`.
- Mechanism: in an exact one-defect block whose terminal neighbours are
  adjacent, their external neighbours being equal or adjacent forces a square.
  Otherwise delete the terminal triangle and add one marked edge, obtaining a
  smaller simple cubic graph.
- Cycle map: base cycles avoiding the marked edge retain length; a marked
  length-`L` cycle expands to one cycle of length `L+2` and one of length
  `L+3`; the gadget also supplies a triangle.
- Criterion: the marked edge must meet every dyadic cycle and avoid every
  cycle of length `2^k-2` or `2^k-3`.
- Exact consequence: empty cubic cores through order 20 exclude this formerly
  uncovered adjacent-terminal block case through block order 23.
- Independent finite audit: 1,899 marked edges in 112 cubic graphs, comparing
  213,329 expanded cycle instances, all match the proved multiset map.
- Artifacts: `TRIANGLE_TERMINAL_REDUCTION.md`,
  `triangle_reduction_finite_audit.json`.

## Entry 006 - checkpoint

- Status: `CONTINUE_PACKET`.
- No universal proof, counterexample, or unverified candidate exists.
- Closed finite subfamily: all connected simple cubic marked-edge suppressions
  through order 20; the non-Hamiltonian order-22 slice; nonadjacent exact
  blocks through order 21; adjacent exact blocks through order 23.
- Next: seek a structural proof of empty dyadic core or of the observed
  width-three certificate bound in a graph class wider than the finite census,
  or obtain a count-validated order-24 non-Hamiltonian catalogue.  Do not
  revert to Hamiltonian encodings, generic SMS, covers, necklace searches,
  line-tree/apex, or Cayley scans.
