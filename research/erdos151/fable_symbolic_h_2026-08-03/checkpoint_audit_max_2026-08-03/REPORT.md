# n=50 CEGAR checkpoint audit — concise handoff

Date: 2026-08-03

## Verdict: CONDITIONAL PASS

The frozen matching-3 + TCG-3 successor is approved for a **new,
single-writer production run** under its stated recovery scope: ordinary
process death or AppX teardown, **not sudden power loss**.  This is an
infrastructure verdict, not an n=50 SAT/UNSAT result.

Exact reviewed hashes:

| file | SHA-256 |
|---|---|
| `cegar_checkpoint.py` | `0862f5f4ca6719c4a211133379619d3777387f79d9ed6024e87e00bf0d2fdc09` |
| `cegar_face_matching3_tcg3.py` | `e9f69347eee7d077421188bfcccf20f0173dc3e1767c3b1e643d7f0942be9bf7` |
| `audit_cegar_checkpoint.py` | `db41581d8026a5939bc8de1e21b4f871471ff90f61facd149ccb27c50097a5d5` |

The successor passed independent checks of exact formula replay, RNG restore,
hash-chain and middle-corruption rejection, torn-tail recovery, concurrent
writer rejection and post-exit lock reacquisition, malformed-but-rehashed cut
rejection, the repaired SAT-candidate terminal path, and final-CNF clause
count/file hash/clause-stream hash.  Separate Glucose replay confirmed only
the small n=10 control CNFs.

## Stopped-run finding

None of the three prior n=50 states is recoverable: learned h-sets and TCG-3
partitions existed only in memory, stdout recorded counts rather than clauses,
and no terminal JSON was written.  The stopped combined blob also would have
raised `UnboundLocalError` exactly when both exact oracles first accepted a SAT
candidate; the frozen successor fixes this by testing `raw_partition is None`.

## Required live-reader restriction

`CutJournal._load()` is a **mutating recovery loader**.  If it sees a partial
last line, it quarantines the fragment and rewrites the journal to its complete
prefix.  Therefore:

- never instantiate `CutJournal` or run journal repair/audit while the
  production writer is live;
- monitor only stdout and the atomically replaced `.state.json`; or
- acquire the same OS writer lock before opening the journal through that
  loader.

The OS-held lock makes the production writer single-owner and is released by
the kernel on process death.

## Proof-certificate gap

An in-memory UNSAT, or even an independent solver's UNSAT on the exported CNF,
is not publication-grade.  A real n=50 UNSAT must still pass this chain:

1. freeze and hash the final CNF and semantic journal;
2. independently rebuild/audit the encoding;
3. solve from scratch with a pinned proof-producing solver;
4. verify DRAT and convert it to LRAT with pinned `drat-trim`;
5. verify LRAT with both pinned Linux and independent native Windows checkers.

Until then the strongest allowed wording is `UNSAT observed; certification
pending`.  A SAT candidate likewise requires independent exact graph, beta,
K4, degree, maximal-edge-matching, and arrowing checks.

Full evidence and design rationale are in `CHECKPOINT_RESUME_AUDIT.md`,
`audit_existing_runs.result.json`, `audit_root_successor.result.json`, and
`MANIFEST.json`.
