# Schema-5 terminal proof export

`proof_export.py` is an isolated, read-only adapter. It does not modify the
schema-5 engine, take its writer lock, repair a journal, checkpoint a run, or
invoke the outer solver. It accepts only a run whose fully validated
`result.json` has status `OUTER_UNSAT_NO_PROOF_CERTIFICATE`.

It executes the same reconstruction path twice for the exact static CNF and
all committed dynamic journal cuts, compares the two DIMACS byte streams
before writing anything, and then writes a fresh directory containing
`formula.cnf` and hash-bound `manifest.json`. This catches nondeterministic
export drift; it is not an independent implementation of the CNF semantics.

```powershell
python .\proof_export.py export --run-dir PATH_TO_TERMINAL_RUN --output-dir PATH_TO_NEW_EXPORT
```

The current bundled proof binaries are Linux executables. From Linux or WSL,
print the exact local paths and suggested proof/check commands with:

```powershell
python .\proof_export.py solver-instructions
```

The manifest binds the formula to metadata/progress/result content and file
hashes, journal hash/head/count, static-encoding manifest, original and
replayed source maps, plus exporter and engine hashes. Record hashes of a
solver proof and independent checker log alongside it. A solver UNSAT message,
or the existence of this export, is not a theorem or UNSAT claim; only a
successfully checked proof can support that next step.
