# Readiness audit — v5 F4_N41 candidate fast-path

Date: 2026-08-03

This directory is isolated from the active search: it imports no
`fixed_clique_cegar_*` module, does not read run roots, locks, journals, or
metadata, and contains no production candidate or search output.

## Checked commands

```powershell
.\.venv\Scripts\python.exe research\erdos151\general\checks\candidate_fastpath\selftest.py
```

Observed result: exit `0`, `PASS`.  The test exhaustively covers every labelled
graph through order 5, compares ambient maximal-clique enumeration, beta
thresholds, and triangle-colorability against direct brute force, then runs K4,
K6, v5-envelope tamper cases, and the synthetic n=41 smoke adapter.

```powershell
.\.venv\Scripts\python.exe research\erdos151\general\checks\candidate_fastpath\verify_candidate_fastpath.py research\erdos151\general\checks\candidate_fastpath\smoke_noncandidate_v5.json --report $env:TEMP\erdos151-fastpath-smoke-report.json
```

Observed result: expected exit `1`, `REJECTED_STRUCTURE`: the validly encoded
synthetic K4 has degrees 3/0 and is deliberately not a candidate.  No semantic
decision was run for it.

```powershell
.\.venv\Scripts\python.exe -m py_compile research\erdos151\general\checks\candidate_fastpath\verify_candidate_fastpath.py research\erdos151\general\checks\candidate_fastpath\selftest.py
```

Observed result: exit `0`.

## Readiness hashes

| File | SHA-256 |
| --- | --- |
| `verify_candidate_fastpath.py` | `49d943715f7d0b21bea8d4e938dd2f28e5b8cfc97beb5c61f79b082d8d8152fe` |
| `selftest.py` | `8b432274b86a8bbf414bf14f70cc0a25b4464d54e9d690f2d48b2314f17d026d` |
| `smoke_noncandidate_v5.json` | `ae75d4f71ce4e1035743bc64adc902d2161e6762f417791c356561a7349c6c56` |

## Claim boundary

Only `SIGNED_OFF_SCREENING` represents a successful fast-path result.  It means
the candidate envelope and both graph representations agree; the F4 structural
gate passes; omega is exactly four; and each exact decision completes under the
chosen node guard.  The custom beta/transversal and triangle-DPLL decisions are
additionally compared with separately constructed Glucose formulas when
`python-sat` is available.  This is still not a proof-grade computational claim:
the checker emits no DRAT/LRAT certificate.  A malformed, rejected, or
node-limited result must not be elevated to a campaign conclusion.
