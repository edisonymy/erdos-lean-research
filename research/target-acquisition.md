# Target acquisition and allocation protocol

**Adopted:** 2 August 2026, superseding the allocation ranking in
[`campaign-dossier.md`](campaign-dossier.md) §12.  The dossier remains the
historical record; this document directs current work.

## Objective restated

Maximize the probability of being **first** to fully resolve at least one
genuinely open Erdős problem on a days-to-one-week horizon and receiving
public credit for a correct, useful result.  Formalization is one route to
verification and recognition, not an eligibility requirement.  Two working
observations drive everything below:

1. **The under-attacked tail is the best short-horizon hunting ground.**
   This is a strategic hypothesis, not a measured law: famous conjectures
   have formidable negative evidence and active competition, whereas an
   obscure question can remain open because nobody has applied a modern
   method.  AlphaProof Nexus's [reported 9/353 result](https://arxiv.org/abs/2605.22763)
   shows that broad portfolios can find hits, but it is *not* a transportable
   base rate for counterexample hunts: it used formal proof search over an
   existing Lean corpus under a different selection process.
2. **Database status can lag reality, in both directions.**  Six campaign
   targets collided with outside work in six weeks — mostly finite-range
   or partial-result collisions (#23, #699, #993, #273), plus one full
   witness kill (#106) and one fixed-case kill that happened to be the
   campaign's chosen target (#617 `r=5`) — and the claims index grew three
   entries in eight hours on 1–2 August.  An `OPEN` label is a lead; it is
   never evidence.  Conversely, problems are routinely found to be already
   solved in poorly indexed literature, so **collision checking is part of
   scoring, not a post-selection gate.**

## The funnel

Effort is structured as a funnel with explicit promotion gates.  Depth is
**earned by evidence, never chosen a priori.**

### Tier 0 — pool construction (scripted, minutes)

`full_solution_scout/build_pool.py` builds the candidate pool
deterministically from the three local database snapshots:

- `full_solution_scout/erdosproblems-live/data/problems.yaml` — problem
  statuses (`open` required);
- `.tmp/vibemathed-live-*.json` — AI-claim index (any claim excludes,
  matching the survey's 116-problem wholesale exclusion; refresh before
  each sweep — the file is a snapshot, not a feed);
- `full_solution_scout/llm-hunter-live/attacks/erdos/` — LLM attack logs
  (**flag, do not exclude**: most attacks are failed attempts, but a
  flagged problem's attack files must be read during the recency-lite
  check);
- the campaign-touched list (hardcoded in the script; problems already
  active, parked, audited, or scouted here).

### Tier 1 — statement triage (hours, whole pool)

Score every pooled problem on five numeric axes from its statement (Formal
Conjectures docstring or live problem page), then apply the recognition gate
and formalization bonus below.  No solver time.  For collision, a higher
numeric score means safer / less competitive.

| Axis | Question | Weight |
|---|---|---|
| **Leverage** | Does one finite, mechanically checkable object end the *full* problem — not a case, bound, or symmetry class? | Gate: score 0 ⇒ drop |
| **Uncertainty** | Is the answer genuinely uncertain?  Question form ("is it true that…"), recorded doubt by Erdős, no heuristic consensus, false sibling conjectures nearby. | High |
| **Reachability** | Is the plausible witness region searchable within ~1 CPU-day with modern exact methods (SAT/CP, sieves, exact geometry)? | High |
| **Collision risk** | Age and fame, prize size, llm-hunter attack flag, recent page edits, tag fashion.  Obscurity lowers race risk but *raises* stale-status risk — both directions get checked, neither is disqualifying alone. | Medium |
| **Verification cost** | Can a candidate witness be independently double-checked in minutes from first principles? | Medium |
| **Recognition path** | Is the authoritative informal statement precise enough to audit, and is there a credible route to independent expert review and public dissemination? Existing Lean is a bonus, not a gate. | Gate |
| **Formalization readiness** | Does a credible public Lean statement exist, or would formalization be unusually useful and straightforward after discovery? | Bonus |

The classic trap this rubric exists to avoid: **finite falsifiability
applied to believed-true famous conjectures** (#742, #64, #375, #548 in
this campaign).  "A counterexample would be checkable" is worthless when
P(counterexample exists) ≈ 0.  Uncertainty is the scarce ingredient, not
checkability.

### Tier 2 — recency-lite + probes (≤ 1 CPU-day each, 5–10 concurrent)

Before any solver time, each promoted candidate gets a **recency-lite
sweep** (~15 minutes): live problem page including comments and edit
history, live VibeMathed query for the number, the llm-hunter attack files
if flagged, and one targeted web search on the statement's distinctive
terminology.  This is deliberately cheaper than the full
[`recency-audit.md`](recency-audit.md) gate so that it can run on ~20
candidates; the full gate still applies **before compute-heavy work and
again before any publication.**

Probes are exact from the start (the scout discipline is retained: every
hit re-verified by an independently written checker; solver `UNSAT`
without certificate is `UNKNOWN`).  Hard kill criteria are written down
*before* the probe runs — a margin that must shrink, a residual that must
vanish, a count that must appear — with a default kill at one CPU-day.

### Tier 3 — siege (≤ 3 concurrent, entry requires a live signal)

A probe is promoted to concentrated effort only on a live signal: a
near-miss witness with a principled reason the gap can close, an
unexpectedly small residual space, or a structural argument that the
answer is "false" in reachable range.  "The problem is important" and
"the encoding works" are not signals.  Sieges get all available local
compute and a standing kill review every 24 h.

## Standing decision rules

1. **#742 is background consolation work.**  Let the running fixed-15
   sweep (`t=67,72,77`) finish on local CPU; if all close, publish the
   completed symmetry class as a bounded theorem.  For `t=62`, one
   optional no-proof-logging rerun under a hard cap is authorized,
   recorded at E0 — with the expectation set honestly: the case was
   solver-hard (14.4M conflicts inside the 5,400 s cap), not merely
   I/O-bound, so `UNKNOWN` again is the likely outcome and only a SAT
   model would be significant.  No fixed-20 expansion, no
   asymmetric-class work, and no agent tokens on #742 this week.
2. **Verification follows the mathematics.**  A counterexample verified by
   two independently written definition-level checkers is announced promptly
   (E1+E2) with hashes, timestamps, and exact scope.  Lean is added when it
   materially strengthens trust, exposition, or uptake; it is not allowed to
   delay a sound priority-preserving announcement.  A general proof instead
   requires an independently checkable prose proof and expert review, with
   formalization pursued when feasible.
3. **Bounded certification requires justification.**  Any proposed
   E3/E4/E5 work must first answer in writing: *can this computation end
   the problem or produce a general bridge?*  If no, it needs an explicit
   reason to run this week (lesson 10 of the failure ledger, now
   enforced at allocation time).
4. **Announcement latency is a weapon.**  Target under three hours from
   verified witness to public timestamped release, using
   [`announcement-template.md`](announcement-template.md).  The full
   recency gate is re-run inside that window, per the existing rule.
5. **Publication and honesty standards are unchanged.**  Nothing in this
   protocol relaxes the claim hierarchy, scope statements, or the
   research standards in the root README.
6. **Human review is an escalation layer, not free triage capacity.**  The
   user's mathematics-PhD contacts should receive compact, reproducible
   candidate packages only after a result has passed internal adversarial
   checks.  Priority-sensitive material should be timestamped before broad
   circulation unless a specific reviewer has agreed to confidential review.
7. **Publish evidence, not a competitor's roadmap.**  Infrastructure, killed
   probes, and non-sensitive audit corrections may be published continuously.
   A newly promoted target and its live near-miss remain local during the first
   bounded probe (normally no more than 24 hours).  This tactical embargo ends
   immediately on a verified full result, which follows the under-three-hour
   announcement path, or when the probe is killed.  It must never be used to
   hide an error, overstate priority, or postpone a significant result.

## Workspace hygiene ledger (2 August)

- `experiments/erdos742/order5_fixed15/LeanCNF/Main.lean` previously
  asserted all 21 fixed-15 theorems while only 17 had certificates; the
  four pending cases (`t=62,67,72,77`) are now gated behind a clearly
  marked pending block. **Fixed.**
- Root README previously listed #64 as a current campaign while the
  dossier marks it paused. **Fixed.**
- Toolchain pins clarified: `lean4:v4.27.0`/Mathlib applies to the Formal
  Conjectures statement environment; the LRAT-Catcher replay projects
  (fixed-5 and fixed-15) pin `lean4:v4.30.0`. **Documented.**
- `experiments/erdos548_counterexample/search.py` is untracked
  exploratory code that was written but never run;
  `experiments/erdos742_multiorder`'s four solver jobs were deliberately
  stopped during usage conservation and left empty logs.  Both are
  recorded here as **not evidence of anything**; rerun or delete when
  their lanes are next touched.
