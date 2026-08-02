# Erdős #719 exact-61 audit bundle

This directory freezes the **single corrected bounded probe** used by
`OUTSIDE_FULL_RESOLUTION_REFRESH_2026-08-02.md`. It searches for a 3-uniform
hypergraph on nine vertices with exactly 61 edges and no three edge-disjoint
copies of (K_4^{(3)}). Such a graph would have

\[
e-3\nu\geq61-6=55>
\operatorname{ex}_3(9,K_4^{(3)})=54
\]

and hence would refute the full Erdős–Sauer conjecture in #719.

The frozen run ended `CONFLICT_CAP_UNKNOWN`. It is diagnostic evidence only:
it is neither a witness nor a nonexistence proof.

## Deterministic model

- Vertices: `0..8`.
- Edge variables: the 84 triples in lexicographic
  `itertools.combinations(range(9), 3)` order, numbered `1..84`.
- Tetrahedra: the 126 four-sets in lexicographic
  `itertools.combinations(range(9), 4)` order, numbered `1..126`.
- Cardinality: PySAT `CardEnc.equals(..., bound=61,
  encoding=EncType.seqcounter)`. The frozen DIMACS has 2,890 total variables
  and 5,612 clauses.
- Lazy cut: for each triple of pairwise edge-disjoint present tetrahedra, negate
  the sorted union of its 12 edge variables. Cuts are added in lexicographic
  tetrahedron-combination order, once per distinct 12-edge union.
- Solver: PySAT 1.9.dev7 `cadical195`, 20,000 conflicts per solve, at most 20
  rounds. The recorded environment used Python 3.12.4.

All inputs are frozen in `probe_config.json`; the complete variable incidence
map is in `raw/model_definition.json`; the exact base formula is
`raw/base_exact61.cnf`; and all 18,403 cuts are in
`raw/packing3_cuts.jsonl`.

## Exact replay commands

Run from the repository root with the checked-in virtual environment:

```powershell
.\.venv\Scripts\python.exe research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\probe_exact61.py --config research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\probe_config.json --model-out research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\model_definition.json --cnf-out research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\base_exact61.cnf --trace-out research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\probe_trace.json --cuts-out research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\packing3_cuts.jsonl
```

Generate the independent finite extremal certificate:

```powershell
.\.venv\Scripts\python.exe research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\certify_ex54.py --json-out research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\ex54_certificate.json
```

Replay every structural check and adversarial self-test:

```powershell
.\.venv\Scripts\python.exe research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\audit_replay.py --config research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\probe_config.json --model research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\model_definition.json --cnf research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\base_exact61.cnf --trace research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\probe_trace.json --cuts research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\packing3_cuts.jsonl --ex54-certificate research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\ex54_certificate.json --json-out research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\raw\audit_result.json
```

Verify the complete hash manifest:

```powershell
.\.venv\Scripts\python.exe research\full_solution_scout\triage-2026-08-02\erdos719_exact61_audit\verify_hashes.py
```

## What the replay verifies

`audit_replay.py` checks that:

1. the model has exactly 84 edge variables and 126 correctly incident
   tetrahedra;
2. the stored DIMACS is byte-for-byte the regenerated exact-61 sequential
   counter, exercises all 85 cardinalities plus shifted boundary assignments,
   and every recorded model has exactly 61 edges;
3. each of the 18,403 cuts comes from three pairwise edge-disjoint tetrahedra,
   is the correct negative 12-edge clause, was violated by its source model,
   and the cut file is complete in the frozen generation order;
4. the raw seven-round signature replays exactly; and
5. deliberate model-count, cardinality, cut, and extremal-certificate
   corruptions are rejected.

## Self-contained certificate for the value 54

`certify_ex54.py` does not assume the unresolved asymptotic Turán problem and
uses only the Python standard library. Let (t_n) be the minimum number of
triples meeting every four-set. It exhaustively computes (t_7=12) with the
recurrence “select an uncovered four-set and branch on its four triples.” The
deletion identity

\[
(n-3)t_n\geq n t_{n-1}
\]

then gives (t_8\geq20) and (t_9\geq30). Explicit cyclic `3,3,2` and
`3,3,3` constructions are enumerated and checked against every four-set; their
complements have respectively 20 and 30 triples. Thus (t_9=30) and

\[
\operatorname{ex}_3(9,K_4^{(3)})={9\choose3}-30=84-30=54.
\]

The full recurrence result, optimal (t_7) hitter, explicit constructions,
and checked complements are stored in `raw/ex54_certificate.json`.

## Files and integrity

`SHA256SUMS.json` pins every source, input, and raw output in this directory
except the hash manifest itself. Regenerating the probe may be sensitive to
solver/library versions; the audit checks semantics independently of merely
matching the solver's status line.
