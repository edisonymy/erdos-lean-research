# Hostile audit: stopped n=50 CEGAR states and checkpoint successor

Date: 2026-08-03 (Europe/London)

Scope: the three stopped n=50 CEGAR lanes under
`research/erdos151/fable_symbolic_h_2026-08-03`, followed by an independent
review of the hash-frozen matching-3 + TCG-3 checkpoint successor.  No source
outside this audit directory was edited by this lane.

## Verdict

1. **The three stopped solver states are not recoverable.**  Their learned
   clauses existed only in process memory.  Stdout sampled counts every ten
   rounds but did not record any admissible sets or TCG-3 partitions, and no
   result JSON was written.  Re-running from round zero may rediscover useful
   cuts, but it is not a resume.
2. **The stopped matching-3 + TCG-3 blob had a latent candidate-loss bug.**
   `partition` was assigned only when a triangle-free two-partition was found,
   then read precisely on the desired opposite branch.  If both exact oracles
   returned no obstruction, the code raised `UnboundLocalError` instead of
   preserving the SAT candidate.
3. **The frozen successor is approved for a new single-writer production run,
   subject to its stated boundary:** ordinary process/AppX interruption, not
   sudden power loss.  It reconstructs the exact committed input formula,
   restores the Python RNG state, rejects formula drift, repairs only a torn
   final record, rejects middle corruption, holds an OS-level writer lock, and
   exports the exact terminal CNF.
4. **An in-memory or independently repeated UNSAT is still not a theorem.**
   The exported n=50 CNF must be solved by a pinned proof-producing solver and
   its DRAT/LRAT certificate checked before any mathematical exclusion claim.

The root successor receives **CONDITIONAL PASS** rather than an unconditional
result-grade PASS only because proof generation is intentionally downstream
and sudden-power-loss durability is explicitly out of scope.  No n=50 SAT or
UNSAT result exists in this packet.

## 1. Forensics on the stopped states

The exact stopped source blobs were read from commit
`26c37d7041e9c422e0f8606af2c105b617708968`, because the shared worktree
already contained a successor under development.

| lane | pinned script SHA-256 | last sampled round | stdout SHA-256 | recoverable semantic cuts |
|---|---|---:|---|---|
| inherited degree-9 | `331da93ec645f6015988ddc96817a9b4c651786bd3053e2f40bb418bb092c358` | 22,360 | `35018b195fecc7fd6aa610af073639335695e1aa8d9518f1fff38c6e8d52ebdc` | none |
| matching-3 | `f50becfa7bb5fc6934ded04769b3b5f5b326084889998a02c927dcaa57663ead` | 6,480 | `d124e1a37118fc0439f393a3f28eddb5f0015b55e1a70cf67a333ef4b7707895` | none |
| matching-3 + TCG-3 | `2fc09b1f1101d9f6d38b66f91b1f555c74edab06365abd7eeda0231c9b55813e` | 1,100 | `ea29a15964ea01354169c80c482a096e73f485774722f5153346c8f2b4f9c63a` | none |

All three stderr files were empty and all three intended result files were
absent.  A sampled line such as `cuts+=24` proves only that that sampled round
added 24 clauses; it does not identify their literals.  The lazy triangle
variables were allocated in discovery order, so even their numeric mapping
cannot be reconstructed from the counts.

The combined stopped blob's abstract-syntax inventory was:

- only assignment to local `partition`: line 395;
- candidate-condition read of `partition`: line 489;
- assignment occurred only under `raw_partition is not None`;
- candidate condition required `not sets_found` and evaluated
  `partition is None`.

Thus the actual candidate state, `raw_partition is None` and
`sets_found == []`, reached an unbound local.  The successor correctly tests
`raw_partition is None` instead.

Machine-readable evidence is in `audit_existing_runs.result.json`.

## 2. Independent cut-soundness check

The checkpoint should store semantic objects, not unexplained DIMACS literal
lists.  The two learned schemas are independently checkable.

### Admissible-set cut

For a sorted h-set `W`, add

`OR_{t in C(W,3)} y_t  OR  OR_{uv in C(W,2)} m_uv`.

Here `y_t -> all three edges of t` and `m_uv -> uv is an edge with no common
neighbour`.  If `W` is admissible, every literal is forced false.  Conversely,
every target graph with beta at most `h-1` must have a triangle or an ambient
maximal edge in every h-set, and its obstruction can set the corresponding
one-way witness true.  Therefore *any* well-formed h-set gives a valid target
clause; replay does not need to trust the historical model or oracle.

### TCG-3 cut

For a full partition `V=A disjoint-union B`, add

`OR_{t in C(A,3) union C(B,3)} y_t`.

Every graph in the edge-arrowing target class has a triangle in one side of
every two-partition.  Again, the partition alone is a positive, independently
checkable certificate for the clause.  This cut depends on the audited
Folkman/arrowing reduction for the n=50 target; that theorem dependency must
travel with any published final CNF.

The matching-of-three gate is static rather than learned.  Its soundness rests
on the separately audited maximal-edge matching theorem and must likewise be
included in the final soundness packet.

## 3. Frozen successor review

Exact reviewed hashes:

| file | SHA-256 |
|---|---|
| `cegar_checkpoint.py` | `0862f5f4ca6719c4a211133379619d3777387f79d9ed6024e87e00bf0d2fdc09` |
| `cegar_face_matching3_tcg3.py` | `e9f69347eee7d077421188bfcccf20f0173dc3e1767c3b1e643d7f0942be9bf7` |
| `audit_cegar_checkpoint.py` | `db41581d8026a5939bc8de1e21b4f871471ff90f61facd149ccb27c50097a5d5` |

### Properties that survive hostile review

- `ExclusiveRunLock` holds a Windows byte-range lock (or POSIX `flock`) for
  the entire run.  A second writer is rejected and the kernel releases the
  lock after process death.
- The journal header pins the complete configuration and the deterministic
  static clause-stream digest.
- Each record has a sequence number, predecessor digest, and self-digest.
  Missing/reordered/middle-corrupt records are fatal.
- A non-newline final fragment is quarantined by its SHA-256 and only the
  verified complete prefix is retained.
- Replay validates vertex ranges, sorted uniqueness, exact h-set cardinality,
  and that stored TCG-3 sides form a full disjoint partition.
- Replaying each record must reproduce its exact post-round clause-stream
  digest.  This catches variable-allocation, clause-order, encoder, or source
  drift.  Lazy triangle witnesses are therefore reconstructed exactly despite
  not being preallocated.
- The RNG state after every committed round is restored.  CaDiCaL's private
  learned clauses and branching state are not restored, so the future model
  sequence may diverge.  This is formula-exact resumption, not trajectory
  identity, and the code states that boundary honestly.
- The fixed SAT condition writes a candidate atomically.  A mocked regression
  forced exactly the old failure state and obtained `SAT-CANDIDATE` with zero
  completed cut rounds.
- On in-memory UNSAT, every input clause is exported.  An independent parser
  reproduced the recorded clause count and clause-stream SHA-256, and a
  separate Glucose solver confirmed the small n=10 control CNF UNSAT.
- The journal is appended and `fsync`ed once per completed round.  Cuts are
  currently applied to memory immediately before the append, but no next
  `solve()` occurs before the append returns.  A crash in that narrow interval
  loses at most that uncommitted round and cannot make the resumed formula
  unsound.

### Operational caveat

`CutJournal._load()` is a **mutating recovery loader**, not a safe live reader:
if it sees a non-newline tail it quarantines the fragment and replaces the
journal with the complete prefix.  Do not instantiate `CutJournal`, run a
repair audit, or otherwise invoke that path while the production writer is
live.  Live monitoring should read only stdout and the atomically replaced
`.state.json`, or acquire the same OS lock first.  Raw read-only copies are
acceptable if the copier treats a trailing fragment as uncommitted and never
writes the source.

The implementation deliberately does not promise survival of sudden power
loss.  Its temporary-file `fsync` plus same-volume `os.replace` protects
ordinary process interruption and prevents a partially written final JSON
from appearing as complete, but it does not explicitly issue a Windows
write-through rename for directory metadata.  This is acceptable only because
the narrower claim is explicit.

Independent results are in `audit_root_successor.result.json`; the root audit
was also rerun from the frozen hashes as `root_regression_replay.result.json`.

## 4. Reference protocol and stronger publication design

`checkpoint_protocol.py` is a solver-independent reference checker, not a
replacement wired into production.  It demonstrates the stricter durable
format recommended for future campaigns:

- one immutable run manifest pins the actual static CNF, variable map, source
  bundle, environment lock, and mathematical soundness packet;
- every round is an immutable content-addressed object linked to its
  predecessor;
- only the two semantic cut schemas are accepted;
- publication uses same-directory atomic no-replace rename, with
  `MoveFileExW(..., MOVEFILE_WRITE_THROUGH)` on Windows;
- partial `.tmp` objects are ignored and reported, while corruption of any
  committed object is fatal;
- forks and index gaps are fatal rather than guessed around.

Its adversarial suite passed clean replay, committed-bit-flip rejection,
same-index fork rejection, torn-temporary handling, exact h-set validation,
partition canonicalization, and partition-coverage validation.  This design
costs one file per round; a high-throughput successor could use framed,
hash-chained segments while retaining the same persist/verify semantics.

## 5. Production and terminal gates

Before launching n=50:

1. Commit or otherwise freeze the exact three successor hashes above and the
   Python/PySAT/CaDiCaL environment.
2. Use unique result, journal, state, stdout, stderr, and lock paths.
3. Do not launch two processes against the same result/journal pair.
4. Preserve the separately audited matching theorem, TCG-3 reduction, static
   formula audit, and their hashes beside the run metadata.
5. Monitor `.state.json`/stdout only; do not run journal recovery live.

On SAT candidate:

1. Freeze the atomic result, journal head, source/environment hashes, edge
   list, and graph6 form.
2. Independently check K4-freeness, degree band, exact beta at most 10,
   maximal-edge matching, and edge-arrowing `(3,3)` using independently
   implemented parsers/oracles.
3. Publish only after the graph itself—not the original solver model—passes
   both verification paths.

On in-memory UNSAT:

1. Freeze and hash the exported final CNF and journal.
2. Rebuild the CNF independently from the semantic journal and compare the
   exact clause stream or at minimum a checked clause multiset plus variable
   map.
3. Solve the frozen CNF from scratch with pinned CaDiCaL 1.9.5 (or another
   pinned proof-producing solver) and retain its DRAT proof.
4. Run pinned `drat-trim` to verify DRAT and emit LRAT.
5. Verify the LRAT with the pinned Linux checker and the independent native
   Windows `lrat-check`; require their explicit VERIFIED markers.
6. Publish the CNF/proof/checker/source hashes and the encoding/soundness audit.
   Until all six steps pass, report only `UNSAT observed; certification
   pending`.

## Claim boundary

This audit establishes recoverability and formula integrity for a future run
under its stated crash model.  It does not establish SAT, UNSAT, convergence,
coverage, or proximity for n=50, and it does not resolve any part of Erdős
#151 by itself.
