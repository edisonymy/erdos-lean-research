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
| #128 | finite triangle-free graph census | complete graph catalogues permit exact small-order exclusions and a counterexample is directly checkable | catalogue completeness and UNSAT solver runs are external trust boundaries; the universal problem is far beyond the finite range |
| #167 | finite graph counterexample to Tuza's conjecture | Puleo's theorem reduces order 11 to a tractable residual now closed by independent witness screens | the result is bounded and depends on nauty catalogue completeness; order 12 needs another major reduction |
| #366 | explicit 2-full/3-full consecutive-number witness | a witness would be a tiny checkable certificate | no general witness is known and the public search already reaches `10^22` |
| #488 | universal density inequality | elementary finite-set/divisibility language; faithful corrected Lean statement | substantial 2026 partial work and no known general argument |
| #699 | common large prime divisor of binomial coefficients | strong Mathlib support and exact Kummer reductions | a public computation through `n = 100000` dominates finite search |
| #742 | finite extremal graph counterexample | order 25 is the first case beyond Fan's explicit small-order theorem, and any SAT edge list is directly checkable | the current public CNF searches are computationally large and any UNSAT result needs a proof certificate |
| #982 | finite planar-geometry counterexample | noncocircular rational or integer coordinates give an exact convexity-and-distance certificate | every cyclic polygon automatically satisfies the target; a July 25 unverified partial-proof claim and public floating-point benchmarks must be monitored |

## Next queue

| Problem | Opportunity | Reason not yet primary |
|---|---|---|
| #64 | finite graph counterexample | small cubic/minimum-degree-three ranges now collide with July work; a meaningful continuation needs certificate-backed replication at orders 30/31 or an all-cubic order-32 search including 32-cycles |
| #196 | infinite permutation construction | three Rethlas attempts produced no verified blueprint; finite avoiding prefixes do not address the required infinite bijection |
| #273 | covering system with moduli `p-1` | July repositories already prove `p>877`, exclude period `55440`, and certify all moduli at most `57` as impossible; a construction now needs a genuinely new large-modulus idea |
| #672 | perfect-power product in a long coprime arithmetic progression | structured SAT/valuation search; known work excludes lengths through 34 |
| #677 | interval-LCM inequality | decidable and elementary; uniform statement appears structurally hard |

## Rejected or deprioritized examples

- **#36:** the local Formal Conjectures bound is stale relative to newer reported bounds, so
  proving it would not be novel.
- **#287:** a well-developed formal/computational search has pushed any counterexample far
  beyond naive enumeration.
- **#23:** a June 2026 preprint reports the corresponding finite range through `n=40`, making
  a small direct search redundant.
- **#458:** public computations reported in June 2026 extend beyond `10^20`, so a naive finite
  counterexample sweep has no plausible novelty window.
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
