# Erdos #149 long-horizon lane

This directory contains the independently audited completion of the
maximum-degree-four, order-at-most-16 case of the strong edge-colouring
conjecture. The strongest exact statement and reduction are in
`ORDER16_THEOREM.md`; the earlier dependency steps are retained separately.

This is a bounded theorem, not a complete resolution of Erdos problem #149
and not a novelty claim.

## Reproduction

The Git repository stores the generators, independent audits,
machine-readable results, hashes, and theorem documentation. Large proof and
catalogue inputs are distributed separately to avoid repository bloat.

The order-at-most-12 exact CNFs and pinned DRAT certificates are at:

<https://github.com/edisonymy/erdos-lean-research/releases/download/erdos149-order12-2026-08-03/erdos149-order12-cnf-drat.zip>

Extract the archive directly under `research/full_solution_scout/`. Its two
top-level directories merge with
`erdos149_long_horizon_root_2026-08-03/` and
`erdos149_long_horizon_max_2026-08-03/`, placing every proof at the path used
by the audit scripts. Archive and component hashes are recorded in
`RELEASE_ASSETS.json` and `CERTIFICATION.json`. The much larger LRAT files
are deterministic `drat-trim` derivatives of these DRAT certificates; their
hashes and successful native-checker transcripts are retained in
`CERTIFICATION.json`.

Then run, from the repository root:

```powershell
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_long_horizon_max_2026-08-03/audit_root_encodings.py
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_long_horizon_max_2026-08-03/audit_trianglefree_berge.py
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_structural_max_2026-08-03/verify_n12_networkx.py research/full_solution_scout/erdos149_structural_max_2026-08-03/12_4reg.txt --out .tmp/erdos149_n12_catalogue_replay.json
```

With locally generated LRAT files present, the two audit scripts replay them
with the pinned native checker at
`tools/proof_checkers/windows_drat/bin/lrat-check.exe`. The public DRAT files
can first be verified and converted using the pinned toolchain recorded in
`CERTIFICATION.json`.

The five complete catalogues used at orders 13 through 15 are at:

<https://github.com/edisonymy/erdos-lean-research/releases/download/erdos149-order15-2026-08-03/erdos149-order13-15-catalogues.zip>

Extract that archive at the repository root. It installs the catalogues at
the paths hashed in `CERTIFICATION_ORDER13.json` and
`CERTIFICATION_ORDER14.json`. Then run:

```powershell
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_long_horizon_max_2026-08-03/audit_order13_certification.py
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_order13_root_audit_2026-08-03/audit_order13_independent.py --package research/full_solution_scout/erdos149_long_horizon_max_2026-08-03 --geng .tmp/nauty-env/Library/bin/geng.exe --labelg .tmp/nauty-env/Library/bin/labelg.exe --output .tmp/order13-root-replay.json
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_long_horizon_max_2026-08-03/audit_order14_certification.py
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_order14_root_audit_2026-08-03/audit_order14_independent.py --package research/full_solution_scout/erdos149_long_horizon_max_2026-08-03 --geng .tmp/nauty-env/Library/bin/geng.exe --output .tmp/order14-root-replay.json
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_long_horizon_max_2026-08-03/audit_order15_certification.py
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_order15_root_audit_2026-08-03/audit_order15_independent.py --package research/full_solution_scout/erdos149_long_horizon_max_2026-08-03 --geng .tmp/nauty-env/Library/bin/geng.exe --output .tmp/order15-root-replay.json
```

The root replays regenerate the complete catalogues and use third matching
algorithms. `RELEASE_ASSETS_ORDER15.json` records the current archive hash
and size.

## Order 16 streaming certificate

The order-16 regular catalogue is intentionally not stored. Official nauty
`geng` streams its 16 canonical residue classes directly into two full
implementations. The primary and replay manifests record identical stream
hashes and sum to exactly 8,037,418 connected 4-regular graphs. The two
nonregular profiles have separate exact core searches and a fresh audit.

Run the compact certificate audit from the repository root:

```powershell
.\.venv\Scripts\python.exe research/full_solution_scout/erdos149_long_horizon_max_2026-08-03/audit_order16_certification.py
```

The complete regeneration commands, pinned generator information, and
order-17 handoff are in `CONTINUE_PACKET.md`.
