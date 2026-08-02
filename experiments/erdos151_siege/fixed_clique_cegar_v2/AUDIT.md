# Independent adversarial audit of fixed-clique CEGAR v2

Date: 2026-08-02

## Verdict

After the corrections recorded below, the v2 search is semantically sound for
its **exact presets** and is suitable for fresh bounded pilot runs after the v1
migration checklist is completed.  I found no counterexample to the batched
cut semantics, eager forbidden-clique semantics, replay, or F3 relabelling
scope.  This verdict does not certify an Erdős #151 result, an unfinished run,
or an unproved solver UNSAT answer.

No production run was started during this audit.  No v1 source or active v1
run directory was edited.

## Defects found and fixed

1. **Terminal crash window.**  The inherited terminal path writes
   `result.json` and then `progress.json`.  A crash between those atomic writes
   left a valid result paired with stale nonterminal progress and made the run
   non-resumable.  V2 now recovers that exact state only under the exclusive
   writer lock, only without code drift, and only after the result passes the
   complete base validator against the full journal and candidate linkage.
   Read-only audit still refuses and does not mutate the stale pair.
2. **Candidate schema acceptance.**  The pinned v1 verifier did not inspect the
   candidate's schema field.  The v2 wrapper now rejects every non-schema-2
   artifact before invoking the independent encoding.
3. **Logical-cut artifact binding.**  Batched record counts were reported but
   not independently checked in every progress/result artifact.  V2 now
   recomputes them for the exact journal prefix and rejects mismatches.
4. **Verifier provenance.**  Candidate linkage now binds the independent
   wrapper hash to the run's source map and checks the expected approved-preset
   command.  Verification reports and emitted CNF manifests record the v2
   wrapper, pinned a167ff8 verifier, cases, and requirements hashes.
5. **Record source maps.**  Journal replay now requires the exact source-key
   set and valid SHA-256 syntax; without `--allow-code-drift`, every record must
   equal the current pinned source map.
6. **Non-finite limits.**  `NaN` and infinite wall-clock limits previously
   evaded the nonnegative check.  They are now rejected.
7. **Runtime requirement.**  The environment specification now pins the
   exercised `python-sat` version, `1.9.dev7`, instead of accepting an
   arbitrary future release.
8. **Artifact hygiene.**  V2 now ignores run directories, solver logs, and
   test temporary directories so large or uncertified artifacts are not
   accidentally staged as source.

## Semantic audit

### Forbidden-clique batching

`enumerate_cliques_exact` lists each fixed-size clique once in lexicographic
order.  The lazy separator commits the complete list present in the candidate,
and replay recomputes and requires exact ordered equality.  Every item adds the
standard all-negative edge clause, so the batch is precisely their
conjunction.  The eager policy adds the corresponding clause for every vertex
subset statically.  Exhaustive comparison with brute force passed for all
1,024 graphs on five vertices and every clique size 2 through 5.  A targeted
falsifier deleting one clique while repairing the stored logical count was
rejected as semantically incomplete.

### Admissibility projection and batching

Each item reuses the pinned v1 exact existential projection: after eliminating
auxiliaries, it is true exactly when the selected target set contains a
nontrivial ambient-maximal clique.  Auxiliary intervals and clause streams are
disjoint and reproduced item by item, so a batch is a conjunction of exact
cuts, not a shared-auxiliary approximation.

The oracle's blocking clause excludes the returned target set and its
supersets.  This loses no other target-size witness: admissibility is downward
closed, and any other target-size witness has a model selecting exactly its
own vertices.  Full enumeration matched brute force on all five-vertex graphs.
The projected two-item conjunction was exhausted on all four-vertex graphs.
A falsely `enumeration_exhausted` batch with one real witness omitted was
rejected by the replay SAT check.

The implementation intentionally uses **nontrivial** maximal cliques.  This is
the campaign's definition of `beta`; in the production presets, degree at
least five also rules out isolated singleton maximal cliques.

### F3 scope

The labelled fixed-K3 reduction is symmetry-safe for the `omega(G)=3` lane:
choose any triangle and relabel it to vertices `0,1,2`.  Relabelling preserves
degree bounds, beta, K4-freeness, and arrowing.  An `omega(G)<=2` graph has no
triangle and therefore cannot arrow `(3,3)`.  Thus, conditional on the separate
Folkman reduction that any #151 counterexample must arrow `(3,3)`, F3 covers
the missing K4-free lane.  F4 and F5 analogously cover clique numbers four and
five.  The harness itself does not prove the Folkman reduction, the degree
window `[5,9]`, or `omega(G)<=5`.

### Replay, hashes, and crash behavior

V2 loads a byte-pinned a167ff8 v1 implementation into a private module and
hashes four v2 plus four upstream files into metadata and every committed
artifact.  Schema-1 journals are rejected.  Batch item hashes, record hashes,
the journal chain, candidate graph hashes, regenerated clause-stream hashes,
static CNF, progress prefixes, results, and candidate files are all checked on
replay.

The inherited append order is crash-safe: a complete journal record is fsynced
before its clauses are installed or progress advances.  A partial final line
is refused by read-only audit and, under a writer lock, preserved in a
timestamped recovery file before truncation.  A crash after the complete
record but before progress merely leaves a valid stale prefix and is repaired
on writable resume.  The v2-specific terminal crash window is now handled as
described above.  A second writer fails atomically; a hard process crash can
leave a stale lock, which must be removed only after checking its recorded PID.

## Checks run

```text
python -m py_compile v2/cegar.py v2/verify_candidate.py       PASS
python v2/test_v2.py                                         17/17 PASS
python v1/test_smoke.py                                      14/14 PASS
```

The v2 suite includes exhaustive small-graph oracle/projection tests and
targeted falsifiers for incomplete forbidden batches, false admissibility
exhaustion, wrong candidate schema, logical-count tampering, a second writer,
non-finite limits, a partial batch-journal tail, and stale terminal progress.
It also sends a K6 candidate through the independent verifier and checks the
provenance-bearing CNF manifest.

Audited production source hashes:

```text
dee49428a884562771b6456438e1a9241e92bc55d6bbb23cd7ad8ea2905b4cdf  v2/cegar.py
ec20e5b15bf692226e3099020d199a9df31ee9eff100ad403db87e8475a19bcd  v2/verify_candidate.py
3b191005e97dcf97fab6e9e74512aa2f91b8906a7c01cbba5b58ffe7d7420977  v2/cases.json
63022582ca3ae3a45911331f74428edb2b38f471c15ceda82bac4dbe9377865a  v2/requirements.txt
```

## Remaining proof caveats

- `OUTER_UNSAT_NO_PROOF_CERTIFICATE` is not proof-grade.  Rebuild/export the
  exact terminal CNF and obtain and independently check a solver certificate
  before claiming exhaustion.  Lazy unseen forbidden constraints do not harm
  the implication: UNSAT of the stored relaxation is stronger, but it still
  needs a checked certificate.
- A dumped candidate is not proof-grade until the independently rebuilt
  admissibility and coloring CNFs both have independently checked UNSAT
  certificates.  The current CaDiCaL/Glucose answers are evidence only.
- Hash chains detect changes relative to a trusted published head; they are not
  signatures.  Any code-drift run also needs every historical source tree
  archived.  Production should not use `--allow-code-drift`.
- The Python dependency is version-pinned and runtime versions are recorded,
  but solver binaries are not themselves proof objects.  Checked CNF proofs
  are the trust-reducing boundary.
- Time limits are checked between outer models.  One outer solve or one batched
  oracle can overrun the nominal wall-clock limit.  `--max-iterations 0` with
  a zero time limit is intentionally unbounded.
- The three fixed-clique lanes are only their stated order-41, degree-`[5,9]`,
  target-10 scopes.  Their union becomes relevant to #151 only through the
  separately audited mathematical reductions.  No bounded pulse or partial
  journal is an exhaustion.
