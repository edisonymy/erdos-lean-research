# Matching>=3 + TCG-3 combined successor audit

Date: 2026-08-03

Status: **PASS.**  The combined successor is implemented separately and was
not launched at order 50.  Neither live run was changed, stopped, or resumed.

## Implementation

`cegar_face_matching3_tcg3.py` preserves the audited matching>=3 static
formula and adds one exact TCG-3 query per decoded model.  When the triangle
hypergraph is two-colorable, it greedily reduces the partition imbalance and
adds the sound inherited-witness clause

```text
OR { y_t : t is internal to one partition side }.
```

Every output serializes the static formula, final formula, cumulative oracle
and cut telemetry, and per-round oracle phases.  The main SAT formula receives
no static TCG-3 variables or clauses; the external oracle uses 50 variables
and at most 39,200 clauses at order 50.

The order-50 static accounting exactly matches the audited matching3 metadata:
47,241 variables and 379,713 clauses, comprising 305,200 graph/degree clauses,
60,025 maximal-witness clauses, and 14,488 matching-gate clauses.

## Validation

The exhaustive rebalance audit screened all 32,768 labeled order-6 graphs.
All 3,640 graphs admitted by the matching3 gate were TCG-3 partitionable; all
3,640 returned partitions remained full and triangle-free, and the cut length
never increased.  It decreased strictly in 3,430 cases.

Matched `n=10, h=4`, 24-cuts-per-round regressions were:

| Seed | matching3 rounds | combined rounds | TCG-3 hits/queries |
|---:|---:|---:|---:|
| 2026 | 18 | 4 | 4/4 |
| 2027 | 21 | 4 | 4/4 |
| 2028 | 18 | 3 | 3/3 |

Both variants returned operational UNSAT in every matched control.  These are
regressions, not proof-certified theorem results.  On the separate order-6
semantic control, matching3-only returned its known SAT candidate, an exact
TCG-3 partition was found, and the combined successor excluded the class in
two rounds.

## Scheduler decision

**Choose the combined successor for the next production slot, but do not
launch it before authorization.**

This decision is based on formulation and oracle phase, not elapsed human
time:

1. On edge-variable projections, the combined static formula is a strict,
   target-valid strengthening of the inherited static formula by the audited
   matching>=3 theorem.
2. The inherited live log's latest 25 samples, through sampled round 21,780,
   all report `cuts+=24`, `y=19600`, and `m=1225`.  This is the randomized
   full-batch discovery branch, not the deterministic complete-miss branch.
   It therefore has no unique terminal-oracle phase that a scheduler must
   preserve.
3. The combined loop retains the same admissible-set oracle and adds a sound
   global separator.  The matched controls show that separator active on every
   tested combined model.

Important caveat: a fresh combined formula and the *current* inherited live
formula are logically incomparable.  The fresh process lacks the inherited
run's accumulated model-specific cuts; the inherited process lacks the
matching gate and TCG-3 cuts.  No order-50 TCG-3 hit rate has been measured, so
the scheduler choice is an informed formulation/phase decision rather than a
production-speed claim.

The matching3 live snapshot was also read-only: its latest 25 samples were in
the same randomized full-batch phase, with actual maximal matching sizes
24--25, far above the required three.  This is diagnostic telemetry only.

## Claim boundary

Any production UNSAT requires final-formula serialization and independent
proof certification.  Any SAT candidate requires independent exact beta, K4,
and edge-arrowing validation.
