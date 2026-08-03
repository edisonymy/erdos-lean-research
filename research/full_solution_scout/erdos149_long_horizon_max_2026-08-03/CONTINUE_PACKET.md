# Erdős #149 long-horizon continuation packet

Date: 2026-08-03

Status: `BUDGET_CHECKPOINT`

## Locked objective

Find a finite simple graph `G` with `Delta(G) <= 4` and
`chi(L(G)^2) >= 21`.

`TARGET_LOCK.md` is immutable in this lane. Its SHA-256 is
`f623f41a1257bc07e9865c0cca68f80173e2bc6230f0009c0babc947dd82fad8`.

## Strongest verified result

The certificate-backed bounded theorem now covers every finite simple graph
with at most 16 vertices and maximum degree at most four:

`chi(L(G)^2) <= 20`.

The frozen top-level files are:

* `ORDER16_THEOREM.md`, 3421 bytes, SHA-256
  `a4afede980532856009418412076e6cede2a6697412a44000e147bab89e1fecc`;
* `CERTIFICATION_ORDER16.json`, 6312 bytes, SHA-256
  `5f9df83f780624b229ef75592a43120cb0050a6bf75171b3369072c6bf09ed69`;
* `audit_order16_certification.py`, SHA-256
  `98404d70705e7c4c5c8a986bcb72a1854d52a737e28ea6b4132a31a787bd4a9f`;
* `order16_certification_audit.json`, 14069 bytes, SHA-256
  `6e7c40771f04ee2e6365fe16d5c9aaec2e61cf582380cd3b3f6124298ba859e6`,
  status `VERIFIED`.

Do not mutate the frozen theorem/certification packages for orders 12 through
16. This is a bounded theorem only: it is neither a counterexample nor a
universal upper-bound proof, and no public novelty claim is made.

## Order-16 evidence anatomy

The nonregular profiles are reduced structurally by
`MINIMAL_COUNTEREXAMPLE_LOCAL.md` and `N16_CORE_REDUCTION.md`.

* Four defects / 30 edges: all 94 cubic 12-vertex cores were checked; 23 are
  triangle-free, exactly one admissible square-independent four-triple
  partition survives, and it has ten compatibility pairs.
* Two defects / 31 edges: generalized theta cores for cross-matching sizes
  1, 2, and 3 produce 10,872, 75,552, and 362,348 completions. All 448,772
  have eleven compatibility pairs. A separately structured replay agrees.
* Regular / 32 edges: 16 canonical `geng` residue streams contain exactly
  8,037,418 graphs and 184,860,614 bytes. The primary pass finds twelve
  pairs by low-first matching in 8,030,289 cases and high-first matching in
  7,129. The independent replay covers 8,036,737 by reverse on-demand
  matching and the remaining 681 by exact NetworkX blossom, with size 16 in
  every fallback. All stream hashes agree; there are no candidates,
  discrepancies, or parser mismatches.

The incomplete monolithic regular checkpoint is historical only and is not
certificate evidence.

## Exact reproduction commands

Run from this directory with the workspace virtual environment. The regular
scripts pin and verify the bundled `geng.exe` hash before consuming data.

```powershell
..\..\..\.venv\Scripts\python.exe .\n16_t4_core_search.py
..\..\..\.venv\Scripts\python.exe .\n16_t2_core_search.py
..\..\..\.venv\Scripts\python.exe .\audit_n16_cores.py
```

Run the 16 primary shards independently (parallel execution is safe), then
aggregate:

```powershell
0..15 | ForEach-Object { ..\..\..\.venv\Scripts\python.exe .\n16_regular_stream_shard.py $_ 16 }
..\..\..\.venv\Scripts\python.exe .\aggregate_n16_regular_stream_primary.py
```

After every primary shard exists, run the independently implemented replay
and final audits:

```powershell
0..15 | ForEach-Object { ..\..\..\.venv\Scripts\python.exe .\n16_regular_stream_replay_shard.py $_ 16 }
..\..\..\.venv\Scripts\python.exe .\aggregate_n16_regular_stream_replay.py
..\..\..\.venv\Scripts\python.exe .\audit_order16_certification.py
```

The regular passes are long-running. For concurrent reproduction, dispatch
different residues in separate processes and aggregate only after all 16
result JSON files are present.

## Next exact gate: order 17

`N17_CONTINUATION.md` records the derivation. The only possible profiles for
a smallest order-17 counterexample are:

* four degree-three vertices and 32 edges;
* two degree-three vertices and 33 edges;
* no degree-three vertices and 34 edges, hence 4-regular.

Recommended sequence:

1. Four-defect slice: generate the `4^1 3^12` cores, reject triangles, and
   enumerate partitions of twelve vertices into four `H^2`-independent
   attachment triples. Seek twelve compatibility pairs.
2. Two-defect slice: count generalized-theta `K9` W-patterns and residual
   degree buckets for cross-matching sizes `r=0,1,2,3`; choose residual
   backtracking or an exact SAT/f-factor encoding only after those counts.
3. Regular slice: first run only
   `geng -c -d4 -D4 -u 17 34`. Estimate count, stream bytes, and two-pass
   runtime before selecting a residue modulus. Retain the primary-versus-
   independent-replay discipline and exact stream-hash agreement.

No order-17 enumeration or theorem has yet been claimed.

## Route memory

The lane has completed seven mechanism families: certified SAT/LRAT finite
obstructions; degree-three extension and packing; catalogue compatibility
matching; cover/lift exclusion; structured disproof sampling; theta/cubic
core completion; and disk-bounded residue streaming with independent replay.

Before launching a route, compare it with `FAILED_ROUTE_FINGERPRINTS.md`.
In particular, do not treat capped solver outcomes as evidence, do not retry
pure covers of `C5[2]`, and do not rely on a monolithic regular stream.

## Storage and cleanup boundary

Keep all pinned root and triangle-free DRAT/LRAT proofs, canonical theorem
catalogues, frozen theorem/certification JSON, and all order-16 shard
manifests. Inactive nonpinned root proof attempts, stalled order-13 CNFs,
and historical prefix/checkpoint files are cleanup candidates only; delete
nothing without explicit authorization.

No git operation and no public communication was performed in this lane.
