# v5 F4_N41 candidate fast-path

`verify_candidate_fastpath.py` is an isolated, read-only screening checker for a
possible order-41, omega-4 candidate emitted by
`fixed_clique_cegar_v5_arrowfirst`.  It imports no CEGAR/search/verifier source
and never opens a run directory, lock, journal, or metadata file.

It independently validates the schema-5 content hash, F4_N41 configuration,
packed edge vector, raw sorted edge list, graph hash, edge count, degrees, and
the fixed K4 on `0,1,2,3`.  It reconstructs every ambient inclusion-maximal
clique via bounded higher-neighborhood subset enumeration (at most `41*2^9` at
the stated degree cap).  Thus no K5 plus the fixed K4 means omega exactly 4.

The decision checks are independent implementations:

- alpha <= 9: exhaustive bitset independent-10 search;
- beta <= 9: exact branch-and-bound clique-transversal test for a transversal
  of size at most 31 (equivalently an admissible 10-set);
- edge-arrowing (3,3): a fresh DPLL decision procedure for the two triangle
  clauses per graph triangle.

When `python-sat` is installed, the beta and arrowing decisions are also checked
with separately built sequential-cardinality/Glucose formulas.  A disagreement,
or an exhausted node guard, is never signed off.

## Claim boundary

`SIGNED_OFF_SCREENING` means this implementation exhaustively finished its
bounded decisions and both optional semantic cross-checks agree.  It is not a
proof-grade computational certificate: the fast-path does not emit DRAT/LRAT
proofs.  A semantic failure or malformed artifact is a rejection, not evidence
about the broader CEGAR campaign.

## Commands

Run the exhaustive small-order and tamper suite:

```powershell
.\.venv\Scripts\python.exe research\erdos151\general\checks\candidate_fastpath\selftest.py
```

Run the read-only smoke adapter.  Its supplied schema-5 object is intentionally
not a candidate and must be rejected at the degree gate:

```powershell
.\.venv\Scripts\python.exe research\erdos151\general\checks\candidate_fastpath\verify_candidate_fastpath.py research\erdos151\general\checks\candidate_fastpath\smoke_noncandidate_v5.json --report $env:TEMP\erdos151-fastpath-smoke-report.json
```

For an actual v5 F4_N41 candidate, copy the candidate JSON to an explicit
read-only location and invoke the same command.  No production candidate was
run while preparing this directory.
