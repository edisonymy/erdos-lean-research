# Erdős 151 finite core-catalogue lane

This directory contains a standard-library-only graph6 audit, exact derivation
of the publicly recoverable independence-two slices, and an exhaustive
proper-clique residual filter for target orders 40 and 41.

The full Bikov order-12/order-13 catalogue was not publicly located, so the
current numerical results are deliberately labelled as exact **slices**, not
full-catalogue results.  See `CATALOG_AUDIT.md` for sources, hashes, search scope,
negative controls, and the precise blocker.

Both exact independence-two slices have zero survivors at target order 40 and
zero survivors at target order 41.  See `RESULTS.md` and the hash-bearing JSON
summaries under `results/` for the complete counts.

## Programs

- `fetch_sources.py`: download and verify pinned McKay graph6 inputs;
- `catalog_lib.py`: graph6 codec, complements, triangle NAE-SAT solver, and
  independent `(3,3)`-Ramsey/minimality tests;
- `derive_catalog.py`: checkpointed derivation from public supersets;
- `verify_catalog.py`: count/hash/invariant/minimality verification;
- `filter_core_catalog.py`: exhaustive residual filter and certificates;
- `selftest.py`: codec, SAT-vs-brute-force, K5/K6, and clique-enumeration tests;
- `RESULTS.md`: exact slice counts, output hashes, and scope limitations;
- `check_results.py`: replay hashes, candidate transcripts, witnesses, and survivor
  counts across the committed result bundles.

All vertex indices in certificates are zero-based.

## Reproduce

From this directory:

```powershell
python selftest.py
python fetch_sources.py source_cache --only r36_12.g6.gz r36_13.g6.gz

python derive_catalog.py source_cache/r36_12.g6.gz derived/minimal_ramsey_q12_alpha2.g6 `
  --mode complement-minimal --expected-input-count 116792 --expected-output-count 124 `
  --source-url https://users.cecs.anu.edu.au/~bdm/data/ramsey/r36_12.g6.gz `
  --progress-every 5000

python derive_catalog.py source_cache/r36_13.g6.gz derived/minimal_ramsey_q13_alpha2.g6 `
  --mode complement-minimal --expected-input-count 275086 --expected-output-count 13 `
  --source-url https://users.cecs.anu.edu.au/~bdm/data/ramsey/r36_13.g6.gz `
  --progress-every 10000

python verify_catalog.py derived/minimal_ramsey_q12_alpha2.g6 `
  --expected-count 124 --expected-order 12 --expected-alpha 2 --verify-minimal
python verify_catalog.py derived/minimal_ramsey_q13_alpha2.g6 `
  --expected-count 13 --expected-order 13 --expected-alpha 2 --verify-minimal

python filter_core_catalog.py derived/minimal_ramsey_q12_alpha2.g6 `
  --output-dir results/q12_alpha2 --targets 40 41 --expected-count 124 `
  --write-all-candidates
python filter_core_catalog.py derived/minimal_ramsey_q13_alpha2.g6 `
  --output-dir results/q13_alpha2 --targets 40 41 --expected-count 13 `
  --write-all-candidates

python check_results.py
```

An interrupted derivation can be resumed with the identical command plus
`--resume`.  At each progress checkpoint the temporary graph6 output is flushed
and synchronized before the JSON checkpoint advances.

## Residual obstruction implemented

For every clique `P` in the core `Q`, for every `k = |P|` from 2 through 5, the
filter first requires a fixed extender in `Q-P`, i.e. a common neighbor of every
vertex of `P`.  It then computes

```text
L(n,Q,P) = n - |Q| - sum(9 - d_Q(v) for v in P).
```

The core is excluded at target order `n` if at least one candidate `P` has

```text
L(n,Q,P) >= t_(10-k),
t_8 = 28, t_7 = 23, t_6 = 18, t_5 = 14.
```

Why this is sound: under the ambient `Delta(G) <= 9` hypothesis, each `v` in
`P` has at most `9-d_Q(v)` neighbors outside the induced core.  At least
`L(n,Q,P)` outside vertices are therefore anticomplete to `P`.  The corresponding
Ramsey threshold supplies the residual clique/independent-set object, and the
fixed common neighbor in `Q-P` extends every clique already contained in `P`.

`Delta(Q) <= 9` is a separate induced-embedding feasibility check.  A core that
fails it is excluded directly and its residual status is marked not evaluated;
the summaries report degree-cap and residual counts separately.

## Certificates

For every input graph the gzip JSONL certificate records:

- graph6 text, degrees, and degree-cap feasibility;
- the number of candidate cliques by size;
- a SHA-256 digest of the complete deterministic candidate enumeration;
- one deterministic exclusion witness per target, when excluded;
- otherwise, a maximum-LHS candidate for every clique size, which certifies that
  no candidate reaches the threshold.

With `--write-all-candidates`, a second gzip JSONL file records every candidate
clique, all of its extenders, and its target-40/41 inequalities.  Survivor graph6
files and a hash-bearing summary JSON are also written for each target.
