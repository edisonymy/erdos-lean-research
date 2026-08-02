# Erdős #151: fixed-clique double CEGAR at `N=40,41`

This directory contains a sound, resumable SAT search for four **fixed-clique
ambient cases**.  It has not been used for a large exhaustion.

| case | order | fixed labelled clique | forbidden clique | degree interval |
|---|---:|---:|---:|---:|
| `F5_N40` | 40 | `K5` on `0..4` | `K6` | `[4,9]` |
| `F5_N41` | 41 | `K5` on `0..4` | `K6` | `[5,9]` |
| `F4_N40` | 40 | `K4` on `0..3` | `K5` | `[4,9]` |
| `F4_N41` | 41 | `K4` on `0..3` | `K5` | `[5,9]` |

The presets live in [`cases.json`](cases.json).  Fixing the labelled clique
loses no graph *that contains such a clique*, because one may relabel a chosen
clique onto the fixed vertices.  Thus F5 covers the `omega=5` ambient case and
F4 covers the `omega=4` ambient case.  **F4 is not a search of K4-free graphs.**
Neither lane covers `omega<=3`, and these runs by themselves do not constitute
a full order-40/41 exhaustion.  The imposed degree interval is also an input
assumption whose justification must accompany any eventual mathematical use.

## Target and outer model

There is one outer Boolean `e_uv` for every unordered vertex pair.  Static CNF
fixes the chosen clique and enforces

```text
N - 36 <= degree(v) <= 9.
```

The forbidden `K6`/`K5` condition is separated lazily rather than materializing
millions of clique clauses.  A witnessed forbidden clique `Q` adds

```text
OR_{uv in E(Q)} not e_uv.
```

Within the stated case, a desired candidate must satisfy both:

1. every 10-set contains a nontrivial inclusion-maximal clique of the
   **ambient graph** (equivalently `beta(G) <= 9`); and
2. `G -> (3,3)`, meaning no total red/blue coloring of its present edges avoids
   monochromatic present triangles.

The search checks these with two exact separation oracles.

## Exact admissibility cut

The first oracle independently enumerates all ambient maximal cliques with a
bitset Bron--Kerbosch routine, then solves the maximal-clique hypergraph
instance for an admissible set of size at least 10.  A larger SAT selection is
trimmed to 10; admissibility is downward closed.

For a violating 10-set `S`, the outer cut existentially selects vertices
`z_v` of a clique `K subseteq S`, requires at least two selectors, and adds

```text
z_u and z_v  =>  e_uv.
```

For every ambient vertex `w` not selected, an auxiliary `d_wv` must certify a
selected `v` with `not e_wv`.  Hence no `w` extends `K`, so `K` is ambient
maximal.  Conversely, an actual ambient-maximal `K subseteq S` supplies all
selector and non-neighbor witnesses.  The CNF is therefore **exact after
projection onto the edge variables**, for arbitrary graphs; it does not rely
on the F4/F5 clique bound.

## Sound arrowing cut

The coloring oracle gives every present edge a red/blue variable and, for each
present triangle, forbids all-red and all-blue.  SAT is exactly a total
triangle-avoiding coloring of `E(G)`.

Absent pairs are then colored by a deterministic SHA-256 rule, producing one
fixed total coloring of *all* vertex pairs.  The outer cut selects exactly
three vertices and a color, and requires their three graph edges to be present
and their three fixed pair colors to equal the selected color.  This CNF is
exactly the statement

> the graph contains a monochromatic triangle under this fixed total pair
> coloring.

Every arrowing graph must satisfy that statement for every total pair
coloring.  The current nonarrowing graph violates it.  Thus the cut is sound,
blocks the current model, and generally blocks more than a one-model no-good.

## Checkpoint and integrity model

Each run directory contains:

- `metadata.json`: immutable configuration, runtime versions, source hashes,
  and a hash of the static clause stream;
- `cuts.jsonl`: append-only cut records, each embedding the violating graph,
  witness, implementation source hashes, regenerated-clause hash,
  previous-record hash, and its own hash;
- `progress.json`: atomic status snapshot bound to the metadata run/config,
  static/source hashes, journal prefix head, and journal-prefix file hash;
- `result.json`, and a raw-edge candidate JSON if a candidate is reached.

On resume, [`cegar.py`](cegar.py) reconstructs the static CNF, verifies the
metadata content hash, checks the journal hash chain, reconstructs every stored
candidate, rechecks every violation witness, regenerates every cut in order,
and compares its exact clause hash before solving.  A crash-truncated final
journal fragment is preserved as `cuts.jsonl.recovered-tail-*.bin` and the
valid prefix is resumed.  Non-tail corruption is fatal.  Source drift is also
fatal unless `--allow-code-drift` is explicitly supplied; even then all CNF
hash reproduction checks remain active.

An existing `result.json` is never trusted merely because its own content hash
is valid.  Resume and audit require its run id, exact config, metadata hash,
static/source hashes, cut counts, journal head, and whole-journal hash to match
the current run.  A terminal result must match terminal `progress.json`; a
candidate result must additionally match the candidate filename, candidate
file hash, graph hash, graph order, and the candidate's embedded run linkage.
This rejects intact artifacts copied from another run.

The journal is the authoritative checkpoint.  `progress.json` may safely lag
one committed journal record after a crash: writable resume accepts a
cryptographically valid prefix and replaces it with a current checkpoint.
Read-only `audit` requires progress to be current rather than silently
reporting a stale prefix as a complete audit.

## Safe usage

Use the repository virtual environment from the workspace root:

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar\cegar.py list-cases

.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar\cegar.py run `
  --case F5_N40 `
  --run-dir experiments\erdos151_siege\fixed_clique_cegar\runs\F5_N40_trial1
```

`run` processes **one outer model by default** and then checkpoints.  Repeating
the same command resumes.  Set a deliberate finite bound with
`--max-iterations K`.  `--max-iterations 0` removes that safety bound and
should not be used casually.  `--time-limit-seconds` is checked between outer
models; it cannot interrupt one long SAT call.

The `run` command holds `.cegar-write.lock`, created atomically with exclusive
filesystem creation, across metadata/journal/progress/result writes.  A second
writer fails immediately.  A process crash deliberately leaves the lock and
its hashed PID/host/time record for operator inspection; remove it only after
establishing that the recorded writer is dead.  Writable `SearchSession` use
from Python also requires an active `RunDirectoryLock`, so bypassing the CLI
does not bypass the concurrency guard.

Audit and export the current accumulated outer CNF with:

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar\cegar.py audit `
  --run-dir RUN_DIR

.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar\cegar.py export `
  --run-dir RUN_DIR --cnf RUN_DIR\outer-current.cnf
```

The exported CNF is the current relaxation containing all committed cuts.
Forbidden cliques not encountered yet remain lazy.  If an incremental run
eventually returns outer UNSAT, that result is deliberately labelled
`OUTER_UNSAT_NO_PROOF_CERTIFICATE`; rebuild/export and obtain an independently
checked proof before making an exhaustion claim.

## Candidate handling and independent hooks

Only when neither exact oracle finds a violation does the driver dump a
candidate.  The artifact includes the raw edge list, packed edge vector, graph
hash, degrees, triangle count, journal linkage, and the exact independent
verification command.

[`verify_candidate.py`](verify_candidate.py) imports no search code.  It:

- reconstructs every graph field and hash;
- requires the graph object's `n` to equal the embedded config's `n`;
- checks the degree/fixed/forbidden-clique conditions;
- enumerates ambient maximal cliques by a different local-neighborhood subset
  method (at most `2^9` subsets per root under the degree cap);
- rebuilds the admissible-set and coloring SAT instances independently; and
- uses Glucose rather than the searcher's CaDiCaL.

It can also emit two portable CNFs and a hash manifest:

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar\verify_candidate.py `
  RUN_DIR\candidate-HASH.json --emit-cnf RUN_DIR\independent_verify `
  --approved-preset F5_N40 `
  --report RUN_DIR\independent_verify\report.json
```

`--approved-preset` is optional for deliberately custom smoke artifacts, but
when supplied it requires exact equality with that entry in `cases.json` and
records the binding in the report and CNF manifest.  Production candidates
automatically embed a verification command with their approved preset.

These CNFs are hooks for proof-producing solvers.  Two bare solver UNSAT
answers, even from different encodings/solvers, are not represented as formal
certificates.

## Smoke tests

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fixed_clique_cegar\test_smoke.py
```

The suite does no production search.  It exhaustively checks all 1,024 graphs
on five vertices for maximal-clique enumeration, exhaustively checks the
projection semantics of both lazy encodings on small orders, cross-checks the
admissibility oracle against brute force, checks the coloring oracle on small
graphs and `K6`, exercises a hash-chained pause/resume, rejects journal
tampering, recovers a preserved crash fragment, and sends a known `K6` smoke
candidate through the independent verifier and CNF exporter.  Regression
tests also reject a cross-run result, mismatched progress, a graph/config order
mismatch, a relabelled K6 passed off as an approved production preset, and a
second concurrent writer lock.

## Files

- [`cegar.py`](cegar.py) — search, journal replay/audit, and CNF export.
- [`verify_candidate.py`](verify_candidate.py) — independent checker/exporter.
- [`test_smoke.py`](test_smoke.py) — exhaustive small analogues and persistence
  tests.
- [`cases.json`](cases.json) — exactly the four production presets.
- [`requirements.txt`](requirements.txt) — Python SAT dependency.
