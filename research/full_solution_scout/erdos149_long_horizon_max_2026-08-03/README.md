# Erdos #149 long-horizon lane

This directory contains the independently audited completion of the
maximum-degree-four, order-at-most-12 case of the strong edge-colouring
conjecture. The exact statement and reduction are in `ORDER12_THEOREM.md`.

This is a bounded theorem, not a complete resolution of Erdos problem #149
and not a novelty claim.

## Reproduction

The Git repository stores the generators, independent mapping audits,
machine-readable results, hashes, and theorem documentation. The exact CNF,
DRAT, and derived LRAT files are distributed separately because the six LRAT
files total hundreds of megabytes:

<https://github.com/edisonymy/erdos-lean-research/releases/download/erdos149-order12-2026-08-03/erdos149-order12-all-certificates.zip>

Extract the archive directly under `research/full_solution_scout/`. Its two
top-level directories merge with
`erdos149_long_horizon_root_2026-08-03/` and
`erdos149_long_horizon_max_2026-08-03/`, placing every proof at the path used
by the audit scripts. Archive and component hashes are recorded in
`RELEASE_ASSETS.json` and `CERTIFICATION.json`.

Then run, from the repository root:

```powershell
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_long_horizon_max_2026-08-03/audit_root_encodings.py
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_long_horizon_max_2026-08-03/audit_trianglefree_berge.py
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_structural_max_2026-08-03/verify_n12_networkx.py research/full_solution_scout/erdos149_structural_max_2026-08-03/12_4reg.txt --out .tmp/erdos149_n12_catalogue_replay.json
```

The two audit scripts replay the LRAT certificates with the pinned native
checker at `tools/proof_checkers/windows_drat/bin/lrat-check.exe`.
