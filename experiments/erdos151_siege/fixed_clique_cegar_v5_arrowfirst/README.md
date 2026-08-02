# Fixed-clique CEGAR v5-arrowfirst: F4_N41 successor

This is an isolated schema-5 successor to the audited, read-only v4 bundle.
It source-pins the same read-only v3 dependency and preserves the exact static
CNF, graph statement, global admissibility encoder, arrowing encoder, journal
hash chain, candidate linkage, fresh-run lock, and approved-preset binding.
It neither reads as nor resumes a v4 run; in particular it must not be pointed
at `fixed_clique_cegar_v4/runs/F4_N41_production`.

For the approved F4_N41 preset, the dynamic order is exactly:

1. complete every forbidden K5 in the current outer model;
2. separate an arrowing coloring, when one exists;
3. sweep every fixed-clique vertex `c` for an induced admissible residual
   witness in `Z_c`, translating each valid witness to the exact global
   admissibility cut;
4. run the inherited generic global admissible-10 separator.

The residual translation and its direction are unchanged: an ambient-maximal
clique contained in `Z_c` is maximal in `G[Z_c]`; the converse is not used.
No additional structural exclusion is introduced.  This order is based only on
the bounded in-memory diagnostic in
`fixed_clique_cegar_order_benchmark`; it makes no candidate, exhaustion,
UNSAT, or proof-certificate claim.

## Commands

Run the focused adversarial suite from the repository root:

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\test_v5_arrowfirst.py
```

For a fresh, separately named run only, static metadata verification is:

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\verify_static.py V5_RUN\metadata.json
```

The candidate command is embedded exactly in candidate provenance and includes
the required approved-preset binding, for example:

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v5_arrowfirst\verify_candidate.py CANDIDATE.json --emit-cnf VERIFY_DIR --approved-preset F4_N41
```

Only a fresh v5 run root may be created.  A writer lock is required, and a
resume checks schema 5, `fixed_clique_cegar_v5_arrowfirst`, current source
hashes (or the explicit drift policy), metadata content hash, journal record
hash chain, cut replay, and candidate verifier/source/preset command binding.
