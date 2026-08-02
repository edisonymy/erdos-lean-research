# Residual-filter results

## Scope

These are exact results for every minimal `(3,3)`-Ramsey core with independence
number two at orders 12 and 13.  They are not full-order catalogue results:
the unlocated portion consists of 2,917 order-12 cores and 306,622 order-13
cores.  See `CATALOG_AUDIT.md`.

Every derived record was independently checked to arrow `(3,3)`, to cease
arrowing after each edge deletion, and to have independence number two.  There
are no duplicate graph6 records.

## Catalogue verification

| slice | source candidates | derived cores | derived graph6 SHA-256 | max degree distribution |
|---|---:|---:|---|---|
| `q=12, alpha=2` | 116,792 | 124 | `1b1d055477f8d4ea488f6aa4aca405f81d33ed57619453c6b652ebec2022170b` | `8:18, 9:106` |
| `q=13, alpha=2` | 275,086 | 13 | `eb42247b21b234d70fec4fbd9ef0d573bf8514e9bc644dcb2a9c38eca21c1f28` | `9:13` |

Thus every core in both exact slices passes the separate `Delta(Q) <= 9`
induced-embedding check.

## Exhaustive candidate enumeration

A candidate is counted once per distinct clique `P`; the extender-incidence
count additionally counts every common neighbor that could serve as the fixed
extender.

| slice | `k=2` candidates / incidences | `k=3` | `k=4` | `k=5` |
|---|---:|---:|---:|---:|
| `q=12, alpha=2` | 5,647 / 25,350 | 8,342 / 20,060 | 4,163 / 4,925 | 0 / 0 |
| `q=13, alpha=2` | 676 / 3,150 | 1,044 / 2,516 | 471 / 575 | 0 / 0 |

The absence of `k=5` candidates is expected: an extender for a 5-clique would
form a 6-clique.

## Target 40

| slice | eligible | excluded | survivors | graphs qualifying at `k=2,3,4,5` | qualifying candidates at `k=2,3,4,5` |
|---|---:|---:|---:|---|---|
| `q=12, alpha=2` | 124 | 124 | **0** | `33, 124, 124, 0` | `38, 7,731, 4,163, 0` |
| `q=13, alpha=2` | 13 | 13 | **0** | `0, 13, 13, 0` | `0, 983, 471, 0` |

## Target 41

| slice | eligible | excluded | survivors | graphs qualifying at `k=2,3,4,5` | qualifying candidates at `k=2,3,4,5` |
|---|---:|---:|---:|---|---|
| `q=12, alpha=2` | 124 | 124 | **0** | `106, 124, 124, 0` | `660, 8,240, 4,163, 0` |
| `q=13, alpha=2` | 13 | 13 | **0** | `11, 13, 13, 0` | `24, 1,026, 471, 0` |

The deterministic single-witness policy chooses a maximum-margin witness, with
stable tie-breaking.  It chose a `k=4` witness for every excluded graph at both
targets.  The overlap columns above show that many graphs also have qualifying
`k=2` or `k=3` candidates.

## Evidence hashes

| evidence | SHA-256 |
|---|---|
| q12 all-candidate gzip JSONL | `f1c9307404e5da5972174cbb013d7a12b01847beef4c6719a9aa41fd21e5201a` |
| q12 certificate gzip JSONL | `8a973bc11eb4ed8ae3ac86cde9751a452be8134a3872bfab0f331ed4100fc540` |
| q13 all-candidate gzip JSONL | `3ab71b7276190c3d10c475173bab804b8678cdb8236e9b26832733403e636e67` |
| q13 certificate gzip JSONL | `7f8e3abe5c4221f47bb4aca7a21351de97accef2f05c82330b238b06eabfdccb` |

Gzip outputs use timestamp zero and omit the original filename, so identical
inputs and options reproduce these compressed hashes.  All four target-specific
survivor graph6 files are empty and therefore have SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
