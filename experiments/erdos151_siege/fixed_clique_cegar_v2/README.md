# Erdős #151 fixed-clique CEGAR v2

This is an isolated, schema-v2 successor to
`../fixed_clique_cegar` at commit
`a167ff8453bd605985d7d743e80529e04c70d652`.  The audited directory and its
active runs are read-only dependencies: v2 verifies their four source hashes
before loading them and includes both upstream and v2 hashes in every run.
No v1 journal is accepted as a v2 journal.

## Scope

The production-dimension presets all have order 41, degrees in `[5,9]`, and
target-set size 10.

| preset | fixed labelled clique | forbidden clique | policy |
|---|---:|---:|---|
| `F3_N41` | K3 on `0..2` | K4 | complete lazy K4 batches; up to 8 admissibility cuts |
| `F3_N41_EAGER` | K3 on `0..2` | K4 | all 101,270 K4 clauses static |
| `F4_N41` | K4 on `0..3` | K5 | complete lazy K5 batches; up to 8 admissibility cuts |
| `F4_N41_EAGER` | K4 on `0..3` | K5 | all 749,398 K5 clauses static |
| `F5_N41` | K5 on `0..4` | K6 | complete lazy K6 batches; up to 8 admissibility cuts |

F3 is symmetry-safe for the missing `omega(G)=3` lane.  If an arrowing graph
contains a triangle, choose one and relabel its vertices to `0,1,2`; graph
properties invariant under relabelling are unchanged.  An `omega(G)<=2` graph
is triangle-free, so every red/blue coloring of its present edges vacuously
avoids a monochromatic present triangle.  Such a graph cannot arrow `(3,3)`
and therefore cannot be a counterexample of the searched kind.  F3 plus the
existing F4/F5 decomposition covers clique numbers 3, 4, and 5 under the
stated order and degree assumptions; it does not remove those assumptions or
make a claim about any other lane.

## Batched cuts and soundness

For a lazy candidate, v2 exactly enumerates **every** forbidden Kt and commits
all corresponding all-negative clauses in one candidate record.  Audit
re-enumerates the candidate and requires the stored ordered list to be the
complete list, not merely a valid subset.

The admissibility oracle uses one SAT instance to return up to eight distinct
admissible 10-sets.  After a set `S` is returned it adds
`OR(v not selected for v in S)`.  Returned sets are exactly size 10, and
admissibility is downward closed, so this blocks only that 10-set among
target-size witnesses.  Every item receives its own witness hash, auxiliary
variable interval, clause count, and clause-stream hash.  Its CNF is the same
exact projected encoding as v1: after existentially projecting auxiliaries,
it holds exactly when the ambient graph has a nontrivial inclusion-maximal
clique contained in that set.  A batch is simply the conjunction of these
independently replayable exact cuts.

The arrowing cut, deterministic absent-pair extension, edge projection,
candidate verifier, atomic files, exclusive writer lock, source drift checks,
hash-chained journal, crash-tail handling, replay, result linkage, and DIMACS
export are inherited from the pinned audited implementation.  V2 adds a new
schema, per-item batch integrity checks, exact logical-cut count validation,
and verifier-source binding.  A valid terminal `result.json` left just ahead
of a stale nonterminal `progress.json` by a crash is recovered only under the
exclusive writer lock and only after complete result/candidate validation.
The independent candidate verifier rejects non-v2 artifacts, imports no
search code, records both wrapper and pinned-verifier hashes, and uses its
separate local-subset maximal-clique enumeration plus Glucose.

Eager mode is also exact: it places the all-negative clause for every vertex
Kt in the static formula.  It changes only when the Kt-free constraint is
materialized, not the projected graph semantics.

## Tests

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v2\test_v2.py
```

The 17-test suite exhaustively checks all 1,024 graphs on five vertices against brute
force for every clique size and for complete admissible-set enumeration.  It
also exhausts the small projected batch encodings, checks eager semantics on
every five-vertex graph, exercises forbidden and admissibility batch replay,
rejects semantically incomplete batches and logical-count tampering, checks
crash-tail and terminal-checkpoint recovery, rejects a second writer and
non-finite limits, and passes a K6 candidate through the independent verifier
and CNF exporter.  These are software checks, not production exhaustion.

## Safe commands

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v2\cegar.py list-cases

.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar_v2\cegar.py run `
  --case F4_N41 `
  --run-dir experiments\erdos151_siege\fixed_clique_cegar_v2\runs\F4_N41_trial1 `
  --max-iterations 1
```

Do not use those run commands until the migration checklist below is
explicitly completed.  `--max-iterations 0` remains deliberately unbounded.

## Migration after the current pulses stop

1. Stop the pulse launchers and wait until both old `.cegar-write.lock` files
   are absent.  Check the recorded PIDs before removing any stale lock.
2. Run the **v1** `audit` command on each old run and archive its audit JSON,
   metadata hash, journal head, whole-journal hash, progress hash, and exact
   source hashes.  Do not use `--allow-code-drift` for this handoff.
3. Leave the old source and run directories immutable.  Do not copy, rewrite,
   concatenate, or translate their journals: one v1 record means one logical
   cut, while one v2 record means one candidate batch.
4. Re-run `test_v2.py`, record the four current v2 production hashes below,
   and choose fresh empty directories under `fixed_clique_cegar_v2/runs/`.
5. Start fresh bounded v2 invocations for `F3_N41`, `F4_N41`, and `F5_N41`.
   The measured default recommendation is lazy batching.  Keep the eager
   presets as controlled comparison lanes, not the initial migration target.
6. Audit each new directory after its first pulse and verify metadata says
   schema 2, engine `fixed_clique_cegar_v2`, upstream commit a167ff8, and the
   expected static policy.  Only then enable the next bounded pulse.

Current production source hashes (SHA-256):

```text
dee49428a884562771b6456438e1a9241e92bc55d6bbb23cd7ad8ea2905b4cdf  v2/cegar.py
ec20e5b15bf692226e3099020d199a9df31ee9eff100ad403db87e8475a19bcd  v2/verify_candidate.py
3b191005e97dcf97fab6e9e74512aa2f91b8906a7c01cbba5b58ffe7d7420977  v2/cases.json
63022582ca3ae3a45911331f74428edb2b38f471c15ceda82bac4dbe9377865a  v2/requirements.txt
```

## Proof caveats

Incremental UNSAT remains `OUTER_UNSAT_NO_PROOF_CERTIFICATE`.  Export and
independently check a proof before any exhaustion claim.  Candidate oracle
UNSAT answers from CaDiCaL and Glucose are not proof certificates.  These
fixed-clique searches are conditional on their exact preset scope, including
the degree interval; neither a bounded benchmark nor an unfinished journal is
a mathematical exhaustion.  The wall-clock limit is checked between outer
models, so one outer or oracle SAT call may overrun it.  `--max-iterations 0`
with a zero time limit is deliberately unbounded.  The fixed-clique symmetry
reduction, the degree/clique-number reductions feeding these presets, and all
claims that connect a certified run back to Erdős #151 still require their
separate mathematical audit.
