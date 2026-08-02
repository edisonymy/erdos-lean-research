# Triage record schema

This schema makes agent-generated target rankings auditable.  A score is a
decision aid, not mathematical evidence and not evidence that a problem is
open.

## Required fields

Each JSON output is an array of objects with:

- `number`: Erdős Problems database number.
- `ask`: one-sentence description of the exact question.
- `leverage`, `uncertainty`, `reachability`, `collision`, `verification`:
  integer scores from 0 to 3.  For `collision`, a higher score means **safer /
  less competitive**, not greater collision risk.
- `total`: the exact sum of those five scores.
- `verdict`: `drop`, `watch`, `probe`, or `siege`.
- `probe_sketch`: concrete first experiment, or `none`.
- `stale_suspicion`: Boolean.
- `stale_why`: concise reason; it may be empty only when
  `stale_suspicion` is false.

Rows based on live page inspection additionally require:

- `status_flag`: one of `open_no_collision_found`, `possible_collision`,
  `known_partial`, `known_full_solution`, or `unclear`.
- `checked_utc`: ISO-8601 UTC timestamp.
- `source_urls`: nonempty array including the live problem page and any source
  supporting a status concern.
- `recognition_path`: `true` only when the authoritative statement is precise
  enough to audit and a credible expert/publication route exists.

An existing Lean statement is copied from the deterministic pool metadata. It
is useful evidence and a verification accelerator, not an eligibility gate.

## Promotion rules

- `leverage = 0` means a short finite computation cannot settle the full
  problem.  Such a row can still be promoted only with a specific general-proof
  mechanism.
- Default probe-grade threshold: `total >= 8`, `leverage >= 2`,
  `uncertainty >= 2`, `reachability >= 1`, `verification >= 1`,
  `recognition_path = true`, and no `known_full_solution` flag.  A high
  aggregate score cannot compensate for a believed-true conjecture or an
  inaccessible witness region.
- A `possible_collision`, `known_partial`, or `unclear` status forces a focused
  recency audit before any solver budget.
- Promotion always records a predeclared kill criterion and resource cap.

Run `triage_pipeline.py` to validate coverage, score arithmetic, duplicated
problem numbers, and live-evidence fields before merging an agent wave.
