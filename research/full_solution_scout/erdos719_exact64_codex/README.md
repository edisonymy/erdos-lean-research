# Erdős #719 exact-64 counterexample probe

This isolated probe targets a 3-uniform hypergraph on nine vertices with
exactly 64 edges and maximum edge-disjoint tetrahedron packing number at most
three.  Such a graph would require at least `64 - 3*3 = 55` decomposition
pieces, exceeding the independently audited value
`ex_3(9, K_4^(3)) = 54`, and would therefore be a candidate counterexample to
Erdős #719.

`search_exact64.py` works in the 20-edge complement.  It imposes exactly 20
missing triples, finds four edge-disjoint present tetrahedra, and adds the
sound hitting clause saying that at least one of their 16 triples must be
missing.  A hash-chained journal makes bounded runs resumable.  The current
incremental solver does not emit an UNSAT proof: `UNSAT_NO_CERTIFICATE` is not
a mathematical claim.  Any candidate must pass a separate, implementation-
independent exact packing checker plus renewed statement and priority audits.

Run the bounded self-test:

```powershell
.\.venv\Scripts\python.exe -B research\full_solution_scout\erdos719_exact64_codex\search_exact64.py self-test
```

Create or resume a bounded run:

```powershell
.\.venv\Scripts\python.exe -B research\full_solution_scout\erdos719_exact64_codex\search_exact64.py run `
  --run-dir research\full_solution_scout\erdos719_exact64_codex\runs\probe `
  --max-iterations 1000 --time-limit-seconds 600
```

The independent audit in
`../erdos719_window_audit_2026-08-03/AUDIT.md` proves that the only remaining
counterexample windows at order nine are `(m, nu) = (61, 2)` and `(64, 3)`.
Its separate read-only code audit also verifies the exact-64 clause polarity,
packing oracle, and restart logic.  Production runs must remain bounded and
must preserve their source hash and journal; an incremental UNSAT answer is
not publishable without a separately checked proof certificate.
