# Independent solver-free replay of the surface gluing branches

This directory contains a third implementation of the finite `m=2` gluing
check described in `../surface_gluing_max/SURFACE_GLUING_REPORT.md`.
`audit_m2_exact_cover.py` imports neither NetworkX nor PySAT and does not call
a SAT solver.  It decodes each surface, reconstructs the quotient fibres, and
recursively exhausts the exact covers while checking edge multiplicities,
spurious triangles, and quotient `K4`s directly.

Results:

| block | branches | complete covers | survivors | elapsed | result SHA-256 |
|---:|---:|---:|---:|---:|---|
| 1 | 210 | 0 | 0 | 868.635 s | `a0f461232437900df9c6aaac718602dbeb97b3cb067401e2e2c8127bb891bc0b` |
| 2 | 330 | 0 | 0 | 1439.068 s | `95d9c19b31c11d2cda68bc7cb48beb12d88a46a67a880b4769d78fd1290f29e8` |

Both JSON records report `VERIFIED_COMPLETE_BRANCH_REPLAY`.  The frozen
checker SHA-256 is
`2727b335aabeff008e4fbd27fc56692eec927ec7ca3b3ebb82331b135341b3ca`.

Reproduction from the workspace root:

```powershell
.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_root_audit\audit_m2_exact_cover.py `
  --input research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate1_corrected_cadical195.json `
  --output research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_root_audit\candidate1_corrected_cadical195.independent_replay.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_root_audit\audit_m2_exact_cover.py `
  --input research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_max\marked_candidate2_corrected_cadical195.json `
  --output research\erdos151\n50_protected_core_max_2026-08-03\surface_gluing_root_audit\candidate2_corrected_cadical195.independent_replay.json
```

Claim boundary: this is an independent replay of the already enumerated 540
canonical branches.  It does not prove the symmetry reduction.  That separate
obligation is discharged by `../surface_gluing_max/audit_m2_gluing_coverage.py`,
which reconstructs the automorphism groups, orbits, weighted raw-factor
coverage, and all branch keys.  Together with the two SAT-engine runs, the
solver-free replay gives a coverage-audited computational exclusion of the
`m=2` normalization stratum.  A label-order bug was found in the original
CaDiCaL/Glucose parallel-edge clause helper, so those four historical SAT
termination files are invalid.  The canonical input projections are unchanged,
however, and `../surface_gluing_max/label_order_correction.audit.json` verifies
that fact byte-for-byte.  The solver-free checker does not import or use the
faulty helper.  The table above now records fresh solver-free replays whose
inputs are the corrected CaDiCaL branch files themselves.  Corrected CaDiCaL
and Glucose runs have separately exhausted all 540 branches with no survivor;
their hashes and fresh coverage audits are recorded in
`../surface_gluing_max/SURFACE_GLUING_REPORT.md`.  This is not a
proof-certified UNSAT theorem, an
exclusion of the full uniform-type-5 class, or a solution of Erdos #151.

The two `m=3` scripts are narrower audits of one supplied projective-plane
block.  They do not claim a complete `m=3` census.
