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
| #273 | finite covering certificate | low visible collision risk; CRT/covering motif matches prior AI successes | certificate may require an enormous period or a new structural idea |
| #488 | universal density inequality | elementary finite-set/divisibility language; faithful corrected Lean statement | substantial 2026 partial work and no known general argument |
| #617 | finite edge-colouring certificate | first open case has 230,230 local six-set constraints, suitable for SAT/local search | a certificate may not exist at the first attempted parameter or may resist symmetry reduction |

## Next queue

| Problem | Opportunity | Reason not yet primary |
|---|---|---|
| #196 | monotone four-term AP in every permutation of `ℕ` | compact combinatorics, but intrinsically infinite |
| #128 | finite triangle-free graph counterexample search | promising certificate; theorem had a recently fixed quantifier bug and needs extra fidelity scrutiny |
| #366 | explicit 2-full/3-full consecutive-number witness | tiny eventual Lean certificate; no known witness below a very large range |
| #672 | perfect-power product in a long coprime arithmetic progression | structured SAT/valuation search; known work excludes lengths through 34 |
| #677 | interval-LCM inequality | decidable and elementary; uniform statement appears structurally hard |
| #699 | common large prime divisor of two binomial coefficients | excellent Mathlib support; negative computation through `n = 100000` weakens brute-force prospects |

## Rejected or deprioritized examples

- **#36:** the local Formal Conjectures bound is stale relative to newer reported bounds, so
  proving it would not be novel.
- **#287:** a well-developed formal/computational search has pushed any counterexample far
  beyond naive enumeration.
- **#307:** a formal barrier requires any reciprocal-prime-set solution to be very large.
- **#647:** current work excludes an enormous finite interval.
- **#1041:** recent AI proof claims have reported topology gaps, and the Lean length notion
  raises a material fidelity issue.
- **#409/#319:** exact-answer formulations risk proving a tautological optimizer identity
  without resolving the intended asymptotic question.

## Claim discipline

No item above is a claimed solution or proof of novelty. Open labels and absence from
VibeMathed are only screening evidence. Every promoted target still requires current literature,
forum, repository-history, and statement-provenance review.

