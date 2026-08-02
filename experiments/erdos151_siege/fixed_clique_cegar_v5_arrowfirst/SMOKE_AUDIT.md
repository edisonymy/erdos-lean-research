# Schema-5 arrowing-first smoke audit

Date: 2026-08-02 (Europe/London)

Verdict: **READY for isolated bounded F4_N41 work only.**  This verdict is an
implementation/readiness verdict, not a candidate, exhaustion, UNSAT, or proof
certificate claim.  No v4 source or run was changed, and
`fixed_clique_cegar_v4/runs/F4_N41_production` was not read, resumed, locked,
stopped, or modified.

## Binding

The successor engine is `fixed_clique_cegar_v5_arrowfirst`, schema 5.  Its
runtime source map uses a distinct `v5-arrowfirst/` namespace and records:

| artifact | SHA-256 |
|---|---|
| `cegar.py` | `d94bdaa3d5eceec833010ddf0afc15deafe6fc3456f76485e4d210769db6ca09` |
| `cases.json` | `91c04de8867c54884104656c2faaf0c868ba0954879b121eccf6998fba54bd1c` |
| `verify_candidate.py` | `b3aa7b6d090bdbe97780e962168c9a1aaa909f55b13418c6a2be425ee9913b65` |
| `verify_static.py` | `64dee5f735a857a1f461476d1b2fff026050e503b62cc03ad57cd1509d258ef1` |

`HASHES.sha256` pins all successor source, test, and documentation bytes.
The inherited v3 dependency is still byte-pinned by v4's audited values.

## Checks performed

```powershell
.\.venv\Scripts\python.exe -m py_compile experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\cegar.py experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\verify_static.py experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\verify_candidate.py experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\test_v5_arrowfirst.py
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\test_v5_arrowfirst.py
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\cegar.py run --case F4_N41 --run-dir experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\runs\F4_N41_v5_arrowfirst_smoke_20260802 --max-iterations 1 --time-limit-seconds 5
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\cegar.py audit --run-dir experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\runs\F4_N41_v5_arrowfirst_smoke_20260802
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\verify_static.py experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\runs\F4_N41_v5_arrowfirst_smoke_20260802\metadata.json
```

Results: compilation passed; the adversarial suite passed 18 tests in 1.855 s;
the one-model fresh run paused normally after one arrowing cut; replay returned
`AUDIT_OK`; and the independent static adapter returned
`STATIC_CLAUSE_STREAM_VERIFIED`.  The unchanged F4 static stream has 40,110
clauses and SHA-256 `58c3e5add5949ea566cc0dacb848286adf2e0e3fe9b3bdd9273ac2df4d5434f3`.

The smoke run's exact file hashes are metadata
`bf4da51b03d665a9000338b97c1270ab8cd6c0912d11bd7d56dea867694cf05f`,
cuts `cfa5b3587ef1e2012714b4e58670d527bb1988e692e663d179fc405299f61252`,
and progress `bf0076240372027ca7d520e72b4e0f678cc5e9514be8ed4a78c6b1dfc5159eeb`.
Its journal head is
`4b23f4b1ff471f813c6785988bd342adb02e504d5f42a3119035e6dfa5f0e40f`.

The adversarial suite covers complete-forbidden then arrowing-first order,
residual/global cut validation, rehashed residual and source/schema tampering,
pause/resume journal replay, generic fallback, stale candidate verifier preset
command rejection, and static source binding.  Candidate provenance requires
the exact `verify_candidate.py` path/hash and `--approved-preset F4_N41` (or
F5_N41) command field.  Fresh-run writer locking remains inherited and is
exercised by the run/session tests.
