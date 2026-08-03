# Strict #719 candidate-screening readiness note

`codex_verify719_strict.py` is a new, standalone reader for a raw JSON object
with an `edges` list.  It requires exactly 61 distinct, canonical triples from
`{0,...,8}` before doing any packing work.  It reconstructs all triples and
tetrahedra locally and computes the exact maximum edge-disjoint tetrahedron
packing with its own bitmask branch-and-bound routine; it imports neither
`attack719.py` nor its constants.

Run the bounded adversarial suite:

```powershell
.\.venv\Scripts\python.exe research\full_solution_scout\fable_long_horizon_2026-08-03\codex_verify719_strict_test.py
```

Use on an explicit candidate only:

```powershell
.\.venv\Scripts\python.exe research\full_solution_scout\fable_long_horizon_2026-08-03\codex_verify719_strict.py CANDIDATE.json --report REPORT.json
```

`SCREENED_NU_LE_2` is only a hash-bound screening result.  It is not a proof
certificate and makes no claim that Erdős #719 is open, resolved, high-priority,
or refuted.  Invalid input, a packing above two, or a node-limit outcome is not
a positive result.

Readiness hashes after the bounded suite:

| File | SHA-256 |
| --- | --- |
| `codex_verify719_strict.py` | `d8fd44cc4206747861a652000560fb008ca49621747ed2073eba7f9d070a4efa` |
| `codex_verify719_strict_test.py` | `366e06f65d10f3bec045ee7b6b307c56735c7688fc6a77c4a9fb1512c3763b60` |
