# Full-solution scout

This directory contains the deterministic pool builder and schema-checked
triage pipeline used by the one-week full-resolution campaign.  Generated
rankings are decision records, not evidence that a problem is open or solved.

## Reconstruct the 2 August pool

The committed pool records source URLs, exact Git commits, modification times,
SHA-256 digests, and the complete set of Erdős numbers excluded by the
VibeMathed snapshot.  To reconstruct it, clone the three repositories into the
ignored sibling directories named below and check out the commits recorded in
`pool-2026-08-02.json`:

```text
erdosproblems-live     https://github.com/teorth/erdosproblems.git
formal-conjectures-live https://github.com/google-deepmind/formal-conjectures.git
llm-hunter-live        https://github.com/mehmetmars7/Erdosproblems-llm-hunter.git
```

The mutable VibeMathed dataset endpoint is
`https://vibemathed.com/api/dataset`.  Save a refresh under
`.tmp/vibemathed-live-YYYYMMDD.json` at the repository root.  For the committed
run, the exact snapshot hash and its 130 distinct Erdős problem numbers are
embedded in the pool artifact, so future API drift is visible and the
exclusion set remains auditable.

Run from the repository root:

```powershell
python -B research/full_solution_scout/build_pool.py
python -m unittest research.full_solution_scout.test_triage_pipeline -v
```

Validate a complete wave by passing its deterministic pool, scope, output, and
all batch files to `triage_pipeline.py validate`.  Add
`--require-live-evidence` for rows derived from live problem pages.  The command
checks exact scope coverage, duplicate IDs, score arithmetic, required live
page URLs, UTC timestamps, and input hashes before writing a merge.

## Tactical embargo

The `unformalized*.json` triage files are ignored only during the initial
bounded probe of newly promoted targets.  A public non-identifying hash
commitment fixes their exact contents and aggregate counts.  The private rows
are released no later than the stated 24-hour deadline, and immediately when a
probe is killed or a verified full result is announced.
