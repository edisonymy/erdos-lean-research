# Erdős problem full-resolution campaign

This repository records an AI-assisted attempt to identify and, if realistically possible,
be first to solve a genuinely open Erdős problem.  On the current approximately one-month horizon,
the controlling objective is the probability of a novel, publicly creditable **full
resolution**.  Lean remains a preferred verification and communication tool when it
materially improves confidence, but an existing formalization is no longer a target gate.

> **Status: active research. No open problem is claimed solved.**

The central record of the campaign—its strategy, active and paused problems,
claim hierarchy, failures, publication history, and exact current frontier—is
[`research/campaign-dossier.md`](research/campaign-dossier.md).  Since
2 August 2026 the operating allocation strategy is
[`research/target-acquisition.md`](research/target-acquisition.md): a
tiered target-acquisition funnel optimizing for full resolutions, with
bounded-certificate work demoted to justified background lanes.

To avoid turning a public research log into a target list for a fast-moving
priority race, newly promoted probes may remain local for at most their first
24-hour compute budget.  This is an embargo/resource rule, not a predicted limit
on mathematical reasoning.  Verified full results are published immediately; stopped probes
and their lessons are then added to the public record.

The project prioritizes statement fidelity, novelty checks, reproducible computation,
independent verification, and expert review over producing a dramatic claim. A successful
Lean compilation will not be treated as a solution unless the formal theorem is independently
audited against the original mathematical problem; conversely, a result is not excluded merely
because the original problem lacked a public Lean statement.

## Current campaigns

- **Erdős #151 (maintenance):** independently audited analytic arguments prove the
  conjectured clique-transversal bound for every graph on at most 39
  vertices.  A sorry-free Lean file verifies the foundational recurrence
  alone.  Induced-subgraph monotonicity reduces each Ramsey plateau to its
  jump order, and new Folkman-core coloring arguments exclude the jumps at
  28 and 36.  A separately audited theorem now proves `beta(G)>=10` for every
  `K4`-free graph on 41 vertices, unconditionally removing clique numbers at
  most three from the order-41 frontier.  A new independently audited theorem
  also proves `beta(G)>=10` at order 41 when `omega(G)=5`, conditional only on
  completeness of the published seven-record Ramsey `(3,6;17)` catalogue.
  Its final proof uses analytic saturation arguments; the repaired exact
  residual-overlap computation is retained as corroboration, not a theorem
  premise.  A second independently audited
  theorem proves the corresponding strong order-40 statement conditional on
  `R(3,10)=40`; if the Ramsey number is 41, the required order-40 bound follows
  from monotonicity.  Thus the `K4`-free order-40/41 lane is closed and,
  subject to the stated catalogue premise, only `omega=4` remains at order 41.
  The unrestricted order-40 case when `R(3,10)=40`, and all later Ramsey
  jumps, remain.  This is substantial
  finite-order progress, not a solution of the full problem.  See
  [`research/erdos151/`](research/erdos151/).  The final bounded global
  search cycle reached its written reallocation gate.  A later Folkman audit
  proves that every counterexample must vertex-arrow `(3,3)`, so it cannot be
  obtained by adding only one or two vertices to a triangle-free graph; the
  remaining global routes require unresolved Erdős--Rogers constants or a
  new sparse Folkman construction.  Two subsequent exact construction audits
  exhausted selected Cayley families and the most concrete 2026 House of
  Graphs Folkman seeds; their best exact `beta` gaps are still 2--16 above the
  required ceilings.  A separately audited triangle-hypergraph/property-B
  theorem now proves that every graph arrowing `(3,3)` has a vertex in at
  least eight triangles, via adaptable links, a forced Krausz multigraph
  root, and a Goldberg--Seymour edge-colouring bound.  This is a uniform
  necessary condition, not a solution of #151.  Routine construction
  expansion and the bounded global CEGAR siege remain stopped.
- **Erdős #64:** the exact one-defect cubic-block route has now been
  independently exhausted through block order 23 for nonadjacent terminal
  neighbours and through order 25 for adjacent terminal neighbours.  An
  official-nauty census covers all 7,319,447 connected cubic graphs of order
  22, in addition to every smaller even order; two complete implementations
  find empty dyadic edge core in every case.  The triangle-terminal reduction
  closes the adjacent case, with a separate 213,329-instance correspondence
  audit.  This eliminates a natural counterexample mechanism but is not a
  solution: arbitrary minimum-degree-three graphs remain outside this finite
  result.  See
  [`research/full_solution_scout/erdos64_nonhamiltonian_cubic_max_2026-08-03/`](research/full_solution_scout/erdos64_nonhamiltonian_cubic_max_2026-08-03/).
- **Erdős #128 (paused):** exact finite census of the triangle-free sparse-half condition.
  Two independent native-cardinality encodings exclude the three remaining order-16 cases
  conditional on the Ramsey catalogue and reduction; retained LRAT certificates for all
  three cases pass a separate checker.  A subsequent all-order structural lane proves the
  target inequality on the balanced, saturated complementary-type boundary, but an exact
  weighted Chvátal family shows that the hoped-for low-type positive-mass amplification
  cannot follow from the current local constraints.  The full unbalanced Hall/discrepancy
  inequality remains open, so this lane is stopped rather than presented as a solution.
  See [`REPORT.md`](research/full_solution_scout/erdos128_global_amplification_max_2026-08-03/REPORT.md).
- **Erdős #167:** exact independently replayed exclusion through order 11 for Tuza's
  triangle covering/packing conjecture, conditional on Puleo's reduction and nauty
  catalogue completeness; this is a bounded result only.
- **Erdős #719:** the complete `r=3`, order-nine instance of the
  Erdős--Sauer decomposition conjecture is certified.  Every 64-edge
  3-graph on nine vertices has at least four edge-disjoint tetrahedra, and
  every 61-edge 3-graph has at least three; together with
  `ex_3(9,K4^3)=54`, this proves `phi(G)<=54` for every nine-vertex
  3-graph.  Thirteen orbit cases were checked by two independent SAT
  encodings and retained DRAT/LRAT certificates.  This is a bounded theorem,
  not a solution of #719.
- **Erdős #196:** an audited negative Rethlas attempt on monotone four-term progressions in
  permutations of the naturals; no proof, counterexample, or verified blueprint resulted.
- **Erdős #203 (stopped after bounded four-angle attack):** a complete
  image-order-at-most-1000 census expands the audited affine-fibre pool to 281
  maps, but fixed-vector validation still leaves about 11% of sampled exponent
  pairs uncovered.  Capell's theorem exactly classifies all perfect-power
  factorisation cells, and an exact rational checker rules out the natural
  common-shear lift of a one-dimensional Sierpiński cover for this pool
  (maximum compatible density `0.6724974471192757`).  These are reusable exact
  results and route-specific negative evidence, not a solution.  A final
  structural audit proves finite fixed-divisor variants collapse to affine
  fibres and gives a checked Lucas certificate showing that Vela's public
  partial-cover modulus has a prime term at `(k,l)=(1,8)`.  Further #203 work
  is stopped; see the [dated claim ledger](research/full_solution_scout/ERDOS203_2026-08-03.md).
- **Erdős #274:** an exact GAP/Python search excludes distinct-index right-coset
  partitions for 25 explicitly listed solvable non-supersolvable groups of order 1440.
  This is an easiest-first finite batch, not an exhaustive order-1440 result, and it
  relies on GAP data and the audited search implementation rather than proof certificates.
- **Erdős #366:** exact exclusion of the restricted families `n+1=x^3` and
  `n+1=x^4` for `2 <= x <= 2^32-1`; no unrestricted witness or proof.
- **Erdős #488:** attack the density-doubling inequality for unions of multiples.
- **Erdős #699:** faithful Lean reductions for common prime divisors of binomial
  coefficients.
- **Erdős #742:** candidate-first order-25 SAT searches for a Murty--Simon
  counterexample. Independently replayed LRAT certificates exclude counterexamples
  having an order-five automorphism of cycle type `1^5 5^4` or `1^10 5^3`, conditional
  on the cited published reductions. The fixed-15 class is split into 21 cases;
  18 have checked native certificates, while exactly `t=62,67,72` remain unresolved
  after 5,400-second timeouts. These are bounded symmetry-class results, not a solution.
- **Erdős #982 (paused):** prior work classifies the unique
  eight-point locally-three-distance planar set; its nonconvexity, together with
  `LDS_2(3)=8`, rules out counterexamples at orders 8 and 9.  The first possible order is
  therefore 10.  Exact campaign checks eliminate old-palette extensions of the convex
  `D4` octagon and prove that the strongest minimal H8-to-local-four relaxation has no
  strictly convex realization.  Continuous inverse design showed only boundary collapse.
  The orthogonal equality-pattern, triangular-lattice, and bounded SAT probes produced no
  candidate or rigorous obstruction and reached their stop rules.  The general problem
  remains open, with no active campaign compute.  See the
  [H8-relaxation report](research/full_solution_scout/erdos982_arbitrary_counterexample_max_2026-08-03/REPORT.md)
  and [distance-pattern report](research/full_solution_scout/erdos982_distance_pattern_max_2026-08-03/REPORT.md).

- **Erdős #149 (bounded theorem, paused):** every subquartic graph on at most
  16 vertices has strong chromatic index at most 20.  At order 16, the two
  nonregular minimum-counterexample profiles are closed by exact core
  reductions, while all 8,037,418 connected 4-regular graphs are streamed
  through two complete implementations with identical shard counts and
  hashes and no candidate.  The package has a separate hash-and-count
  meta-audit.  This is not a solution of #149; order 17 and the universal
  conjecture remain open.  See [public issue #6](https://github.com/edisonymy/erdos-lean-research/issues/6).
- **Erdős #701 (closed priority collision):** a bounded order-eight
  counterexample search found no candidate and an exact equality extremizer
  with `|F|=225` and maximum intersecting family = maximum star = 105.  The
  lane was stopped when Leon Eifler's public 2025 dissertation was found to
  claim an exact-SCIP proof through ground-set size eight.  The thesis did not
  emit the projected >1 TB VIPR certificate, but it removes first-credit value
  from this finite case.
- **Erdős #561 (three exact finite cases; full lane stopped):** complete
  small-host catalogues and independently checked avoiding colourings prove
  the conjectured values 8, 9, and 10 for three previously uncovered
  two-component target pairs.  The value-9 case also has a short analytic
  lower-bound proof using a matching that saturates every cubic vertex in an
  at-most-eight-edge subcubic graph.  No below-formula host was found, so this
  does not resolve #561.  Novelty is plausible but remains subject to
  specialist review because a withdrawn 2026 preprint version briefly claimed
  the full conjecture.  See the [exact-case report](research/full_solution_scout/erdos561_nonuniform_counterexample_max_2026-08-03/REPORT.md)
  and [analytic proof](research/full_solution_scout/erdos561_theory_construction_max_2026-08-03/CLAIMS.md).

The earlier #617 `r = 5` campaign is stopped and retained only as an explicitly
superseded audit. A 24 July 2026 Zenodo preprint records Robert Sneiderman's proof and
Ramazan Kara's independent Lean verification of exactly that fixed case. The all-`r`
problem remains open. See [`research/recency-audit.md`](research/recency-audit.md).

The source programs and retained search logs live in [`experiments/`](experiments/). Results
are provisional until independently checked and summarized in the research notes.

The strongest new bounded result in this wave is documented in
[`experiments/erdos167_order11/`](experiments/erdos167_order11/): Puleo's
published maximum-average-degree theorem reduces the order-11 case to a
2,174,357-class complement residual. Two independent packing/cover witness
screens close every class, and two nauty versions reproduce the exact residual.
This does not resolve the universal conjecture.

The active portfolio is deliberately counterexample-first when the conjecture is finitely
falsifiable. A candidate is promoted only after an independent exact checker accepts a small
certificate, the formal statement is audited, and the announcement-level recency search is
repeated. Solver output without a checkable proof or witness remains exploratory evidence.

## Pinned upstream inputs

- Google DeepMind Formal Conjectures:
  `735aee074327b8e78b0d92bb1ee8ea00937c3f51`
- Erdős-focused Rethlas runner:
  `622bc663d4212333ade4c4802af1db3da92262c0`
- Lean toolchain: `leanprover/lean4:v4.27.0`
- Mathlib: `v4.27.0`

The large upstream checkouts, Lean caches, virtual environments, and compiled search binaries
are intentionally excluded from Git. See [`research/environment.md`](research/environment.md)
for the reproducible setup.

## Research standards

Any eventual solution package must include all of the following:

1. an exact, explicitly audited mathematical statement with authoritative provenance;
2. evidence that the exact informal problem was open before the work;
3. a fresh literature and priority search;
4. reproducible independent verification proportionate to the result (for a finite
   witness, two definition-level checkers; for a proof, line-by-line mathematical review);
5. a sorry-free Lean proof and axiom audit when Lean is used;
6. an independent human-readable proof or verification account;
7. a clear expert-review and dissemination path; and
8. a clear account of AI and computational involvement.

Before compute-intensive work begins, the target must also pass the announcement-level
recency gate in [`research/recency-audit.md`](research/recency-audit.md); a database `OPEN`
label is not sufficient evidence.

The current candidate survey is in
[`research/candidate-survey.md`](research/candidate-survey.md).
