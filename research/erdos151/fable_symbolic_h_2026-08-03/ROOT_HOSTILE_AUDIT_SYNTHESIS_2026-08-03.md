# Root synthesis of the 2026-08-03 Fable hostile audit

This is the authoritative status summary for the requested seven-item audit.
It does not claim a solution of Erdos problem #151.

## Verdict matrix

| Item | Verdict | Safe carry-forward |
|---|---|---|
| X1 | PASS | `chi(G) <= 3 ceil((Delta+1)/4)` for K4-free `G`; standard Lovasz plus Brooks. |
| TCG | PASS, consequences narrowed | Pure-3 jumps `h=11,12` are excluded; the stronger classical chromatic bound also closes `h=13`, not `h=14`.  No order-87/order-98 or eventual-tail conclusion. |
| A4.1 | PASS for nonempty pure-3 graphs | `beta >= n/chi_tf^f`; it does not cover maximal-edge witnesses. |
| A1/A1.1 | PASS with boundary/notation repairs | Split off `t_max=0`; forced coefficient is `c^2/(3e)`, hence `1/(12e)` from the proved Ramsey coefficient `1/2`. |
| M1 | PASS with proof repair | Bound `Delta(G-M)` by ambient `beta(G)` and run the colouring argument directly; do not invoke TCG on `G-M`. |
| V1 | PASS | Edge-arrowing `(3,3)` forbids a partition into two triangle-free vertex sets. |
| Source ledger | Mixed | HHKP, MSV and JMRS inputs pass.  Use a proved coefficient/liminf, not an assumed Ramsey limit.  JMRS is order-tight, not known coefficient-1 sharp. |
| Data hygiene | FAIL with material corrections | Anchor partitions/brackets withdrawn; MT failures and Glauber averages are diagnostics only; four of eight landscape rows are not below `1/2`. |

## Material corrections

1. Program Alpha is presently a **pure-3** asymptotic subprogram.  Its
   fractional triangle-free covers do not handle ambient-maximal edges.  Full
   #151 needs genuine clique colouring, fractional covers by admissible sets,
   or a quantitative maximal-edge bridge.
2. `anchor_pin.py`'s deterministic ten-class replay contains 3,227
   monochromatic triangles.  `anchor_pin2` has no replayable partition.
   Also, a lower bound on the maximum triangle-free set does not give the
   claimed lower bound on `chi_tf`.  Every `[6,9]`/`[6,10]` anchor bracket is
   withdrawn.  A repaired generator plus independent checker instead records
   a valid 13-class partition, giving only `chi_tf<=13` (`C_upper=0.421`).
3. The order statement `min beta = Theta(sqrt(n log n))` predates this
   campaign in the public 21 April 2026 note
   [*A note on the clique-transversal number*](https://www.ulam.ai/research/erdos610.pdf).
   It carries no campaign priority claim.
4. Current published bounds are `21 <= F_e(3,3;4) <= 786`.  A checked
   `(50,11)` K4-free counterexample would still imply `F_e(3,3;4)<=50`.

## Strategic consequence

Keep the finite `(50,11)` counterexample/exclusion lanes and the audited
maximal-edge matching constraints.  Retain A1, X1, TCG, A4.1 and V1 as
structural tools.  Reframe the general lane around admissible-set fractional
covers or an explicit maximal-edge payment; do not allocate proof effort to
improving the invalid anchor interpretation.  No audited item resolves #151.

## Frozen supporting audits

- `FABLE_X1_TCG_A4_M1_V1_HOSTILE_AUDIT_2026-08-03.md`
- `audit_lll_fractional_max_2026-08-03/AUDIT_REPORT.md`
- `audit_sources_data_2026-08-03/AUDIT_REPORT.md`

Each supporting packet freezes the original `RESEARCH_LOG.md` and
`PROGRAM_ALPHA.md` hashes before these corrections were applied.
