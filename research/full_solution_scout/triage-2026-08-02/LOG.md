# Target-acquisition sweep log — 2 August 2026

Running log of the first full execution of the
[`target-acquisition.md`](../../target-acquisition.md) funnel.  Appended
in real time; timestamps Europe/London.

## Context

Adopted after the same-day strategic review (dossier §13): portfolio was
over-weighted toward famous believed-true conjectures; this sweep hunts
week-winnable witness targets across the whole unclaimed open pool.

## Infrastructure created earlier today

- `research/target-acquisition.md` — funnel, five-axis rubric, standing
  decision rules (adopted; GPT 5.6 cross-review corrections folded in).
- `research/announcement-template.md` — sub-3-hour witness fast path.
- `research/full_solution_scout/build_pool.py` — deterministic Tier-0
  pool builder over the three local database snapshots.
- Hygiene: fixed-15 `Main.lean` pending-gate fix, README #64 drift fix,
  toolchain-pin clarification, dossier §13 revision note.

## Tier 0 — pool build (~13:00)

`build_pool.py` on snapshots (problems.yaml, vibemathed-live-20260801,
llm-hunter checkout): 1,217 database problems, 607 open, 130 distinct
VibeMathed-claimed, 36 campaign-touched, 676 llm-hunter-attacked
(flagged only).  **Pool: 540 unclaimed open problems** — 271 with
`research open` Formal Conjectures statements, 65 of those in explicit
existential-iff form.  Output: `../pool-2026-08-02.json`.

VibeMathed live refresh (~13:10): 247 → 250 entries since yesterday's
snapshot, but distinct claimed problem numbers unchanged at 130 — **no
pool member was claimed overnight**.  Saved as
`.tmp/vibemathed-live-20260802.json`.

## Tier 1 wave 1 — formalized-open slice (271 problems, ~13:15–13:45)

Four parallel triage agents scored every `research_open` pool member on
the five-axis rubric (leverage / uncertainty / reachability / collision /
verification, stale-suspicion flagged separately).  Full scored rows in
`range_001_238.json`, `range_241_486.json`, `range_495_893.json`,
`range_912_1212.json`.

**Result: zero probe-grade candidates** (probe = total ≥ 8 with
leverage ≥ 2).  Best totals were 7 (one 8 with leverage 1: #727).
Failure modes, by slice:

- 1–238: oldest/most famous problems; the two top scorers (#193, #197)
  need infinite witnesses — no finite certificate ends them.
- 241–486: dominated by irrationality-series questions (Kovač–Tao are
  actively harvesting that lane — stale flags on 243/257/260/263/264)
  and ∀-shaped statements where a witness settles one case only.
- 495–893: asymptotics and infinitude; kill flags include #872 (forum
  already answered part ii), #893 (Kovač–Luca active), #855 (recent
  page edit; witness region ~1e174).
- 912–1212: 66/70 asymptotic/infinitude, leverage 0.  Stale flags:
  #1084 (appears to be Harborth 1974), #1106(i) (may follow from Ono),
  #1209/#1212 (2025–26 outside work already on-page).

**Interpretation:** within the DeepMind-formalized open subset the
honest intersection (witness-endable ∧ genuinely uncertain ∧
CPU-day-reachable) is empty.  This subset is selection-biased toward
legible, well-studied problems, so the result is informative, not
merely disappointing.

## Tier 1 wave 2 — non-formalized-open slice (269 problems, ~13:50–15:30)

Four parallel agents fetched each live problem page
(`erdosproblems.com/<n>`) for the 269 pool members without a
`research open` formal statement (267 have no matching numeric Lean file;
two have files not marked research-open) — the subset the formalization
legibility bias skips —
scoring on the same rubric plus a `status_flag` capturing on-page
evidence of unrecorded solutions (per the standing observation that the
database lags reality in both directions).  Codex resumed the wave from
deterministic batch manifests after installing a schema validator and merger.
One batch initially over-scored finite calculations that could settle only a
case or improve a bound; every one of its 68 rows was therefore re-read under
the strict full-problem leverage gate before validation.

The merged record covers all 269 problems exactly.  Status triage found 87
with no collision on the page-level check, 149 with known partial work, 17
possible collisions, 10 unclear cases, and 6 apparent full resolutions still
shown inside the open pool.  These are leads rather than certified literature
judgments; each collision receives a claim-level audit before any public status
correction.

Only **two provisional candidates** passed all of the week-horizon promotion
gates.  Their identifiers and target-specific artifacts are being retained
locally during the permitted first bounded probe so the public campaign log
does not become a competitor's target list.  The embargo lasts at most 24
hours and ends immediately if a candidate is killed or a full result is
verified.  One candidate has passed recency-lite and entered a capped exact
probe; the other is undergoing independent recency and feasibility review.

## Side check — no fresh problem additions (~13:55)

Diffed `data/problems.yaml` at upstream commit `db551517` (17 Jun 2026)
against the local 31 Jul snapshot: 1,217 problem numbers in both, zero
added.  The "recently added problems are an under-attacked fresh tail"
hypothesis is dead for this window; the old snapshot is retained at
`.tmp/problems-20260617.yaml`.

## Background lanes

- #742 fixed-15 certified sweep continues on local CPU per standing
  decision rule 1: `t=52` CERTIFIED_UNSAT (this morning), `t=62`
  TIMEOUT at 5,400 s (inconclusive, solver-hard: 14.4 M conflicts),
  `t=67` running at last check, `t=72,77` queued.
