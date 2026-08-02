# Erdős–Lean research campaign

This repository records an AI-assisted attempt to identify and, if realistically possible,
solve a genuinely open Erdős problem with a kernel-checked Lean 4 proof.

> **Status: active research. No open problem is claimed solved.**

The central record of the campaign—its strategy, active and paused problems,
claim hierarchy, failures, publication history, and exact current frontier—is
[`research/campaign-dossier.md`](research/campaign-dossier.md).

The project prioritizes statement fidelity, novelty checks, reproducible computation, and
formal verification over producing a dramatic claim. A successful Lean compilation will not
be treated as a solution unless the formal theorem is independently audited against the
original mathematical problem.

## Current campaigns

- **Erdős #64:** counterexample-first search for minimum-degree-three graphs without
  power-of-two cycles, currently focused beyond the reported public order-31 frontier.
  An exact SMS/Glasgow computation excludes three documented Carr-structured
  order-32 degree families (`h = 8, 10, 12`); `h = 4, 6` and the unrestricted
  case remain unknown, and these trusted-solver results are not LRAT-certified.
- **Erdős #128:** exact finite census of the triangle-free sparse-half condition. Two
  independent native-cardinality encodings exclude the three remaining order-16 cases
  conditional on the Ramsey catalogue and reduction; retained LRAT certificates for all
  three cases pass a separate checker.  This remains a bounded result only.
- **Erdős #167:** exact independently replayed exclusion through order 11 for Tuza's
  triangle covering/packing conjecture, conditional on Puleo's reduction and nauty
  catalogue completeness; this is a bounded result only.
- **Erdős #196:** an audited negative Rethlas attempt on monotone four-term progressions in
  permutations of the naturals; no proof, counterexample, or verified blueprint resulted.
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
  17 have checked native certificates, while `t=62,67,72,77` remain unresolved
  at the dossier snapshot. These are bounded symmetry-class results, not a solution.
- **Erdős #982:** two unconditional arguments exclude all `D2`-symmetric octagons and
  all alternating two-radius dihedral polygons; independent exact searches found no
  counterexample, and the general problem remains open.

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

1. an unchanged or explicitly audited public theorem statement;
2. evidence that the exact informal problem was open before the work;
3. a fresh literature and priority search;
4. a sorry-free Lean proof in the pinned environment;
5. complete axiom output and unfinished-proof scans;
6. concrete tests of the formal definitions and hypotheses;
7. an independent human-readable proof; and
8. a clear account of AI and computational involvement.

Before compute-intensive work begins, the target must also pass the announcement-level
recency gate in [`research/recency-audit.md`](research/recency-audit.md); a database `OPEN`
label is not sufficient evidence.

The current candidate survey is in
[`research/candidate-survey.md`](research/candidate-survey.md).
