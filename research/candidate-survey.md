# Candidate survey — 2026-08-01 snapshot

## Scope and filtering

The survey inspected the actual Erdős files in Google DeepMind's Formal Conjectures repository
at commit `735aee074327b8e78b0d92bb1ee8ea00937c3f51`. At that snapshot, 352 Erdős files still
contained at least one `research open` declaration.

The live VibeMathed dataset listed 116 distinct numbered Erdős problems with an AI-involved
result or claim. Every one of those problem numbers was excluded from the initial target pool,
including entries labelled partial, candidate, variant, contested, or retracted. This is a
collision/priority filter, not an endorsement of every claim.

## Empirical lessons

AlphaProof Nexus reported 9 successful formal statements among 353 attempted open Erdős
statements. Successful cases disproportionately involved explicit constructions, elementary
divisibility, CRT or covering arguments, finite combinatorics, and mature Mathlib APIs.

The Erdős-focused Rethlas campaign provides an equally important negative result: roughly 352
attempts produced 74 verifier-accepted informal blueprints, but only about five were judged
genuinely new. Many accepted blueprints proved a smaller statement, and some still contained
errors. Therefore an informal verifier is useful for triage and repair, but cannot replace an
exact statement-equivalence audit or Lean's kernel.

Formal Conjectures itself reports hundreds of corrected formalization defects. Common hazards
include wrong quantifier order, omitted nonzero hypotheses, induced/subgraph confusion,
incorrect density conventions, and `answer(sorry)` propositions whose answer was never
resolved.

## Active targets

| Problem | Shape | Why active | Principal risk |
|---|---|---|---|
| #128 | finite triangle-free graph census | complete graph catalogues permit exact small-order exclusions | catalogue completeness is an external trust boundary; the universal problem is far beyond the finite range |
| #196 | infinite permutation construction | compact combinatorics and an empty July 2026 repository claim rather than a published result | intrinsically infinite; finite avoidance data cannot resolve it |
| #366 | explicit 2-full/3-full consecutive-number witness | a witness would be a tiny checkable certificate | no general witness is known and the public search already reaches `10^22` |
| #488 | universal density inequality | elementary finite-set/divisibility language; faithful corrected Lean statement | substantial 2026 partial work and no known general argument |
| #699 | common large prime divisor of binomial coefficients | strong Mathlib support and exact Kummer reductions | a public computation through `n = 100000` dominates finite search |

## Next queue

| Problem | Opportunity | Reason not yet primary |
|---|---|---|
| #273 | covering system with moduli `p-1` | July repositories already prove `p>877`, exclude period `55440`, and certify all moduli at most `57` as impossible; a construction now needs a genuinely new large-modulus idea |
| #672 | perfect-power product in a long coprime arithmetic progression | structured SAT/valuation search; known work excludes lengths through 34 |
| #677 | interval-LCM inequality | decidable and elementary; uniform statement appears structurally hard |

## Rejected or deprioritized examples

- **#36:** the local Formal Conjectures bound is stale relative to newer reported bounds, so
  proving it would not be novel.
- **#287:** a well-developed formal/computational search has pushed any counterexample far
  beyond naive enumeration.
- **#307:** a formal barrier requires any reciprocal-prime-set solution to be very large.
- **#647:** current work excludes an enormous finite interval.
- **#1041:** recent AI proof claims have reported topology gaps, and the Lean length notion
  raises a material fidelity issue.
- **#617 at `r=5`:** withdrawn as a target. Zenodo DOI
  [`10.5281/zenodo.21535386`](https://doi.org/10.5281/zenodo.21535386), deposited
  24 July 2026, archives an independent Lean verification of Robert Sneiderman's proof.
  The database page was stale; the all-`r` conjecture remains open.
- **#409/#319:** exact-answer formulations risk proving a tautological optimizer identity
  without resolving the intended asymptotic question.

## Claim discipline

No item above is a claimed solution or proof of novelty. Open labels and absence from
VibeMathed are only screening evidence. Every promoted target must pass the multi-source,
announcement-level protocol in [`recency-audit.md`](recency-audit.md), followed by a
statement-provenance review.
