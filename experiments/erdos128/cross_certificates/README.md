# Retained order-16 LRAT certificates

These three compressed LRAT files certify UNSAT for the exhaustive
cross-degree cases `d=1,2,3` described in `../Z3_CROSS_SEARCH.md`.  Regenerating
the exact CNFs and checking every LRAT closes the remaining order-16 search
conditional on the McKay Ramsey-catalogue completeness premise and the
mathematical reduction documented there.

This is a finite bounded result.  It does **not** prove Erdős problem 128 for
arbitrary order, and the retained native `lrat-check` executable is not a
formally verified checker.

`MANIFEST.json` records the exact CNF, DRAT, LRAT, compressed-artifact, and
proof-tool hashes.  The intermediate DRATs are not retained because the LRATs
are sufficient for direct checking and compress to about 24.8 MB total.

From the repository root, after building the pinned proof tools described in
`../PROOF_PIPELINE.md`, run:

```powershell
powershell -ExecutionPolicy Bypass -File `
  experiments/erdos128/cross_certificates/verify.ps1
```

The verifier rebuilds each CNF, checks its hash, decompresses and hashes the
corresponding LRAT, and requires `lrat-check` to report `c VERIFIED`.
