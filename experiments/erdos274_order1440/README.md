# Erdos 274: exact order-1440 batch-25 frontier

## Precise result

For each of the following 25 GAP groups

`SmallGroup(1440,gid)`, with

`gid = 655, 659, 2641, 2642, 267, 657, 265, 255, 2666, 2667, 74, 654, 1881, 4109, 1624, 4108, 2549, 2522, 1625, 1629, 1628, 2547, 2524, 256, 2542`,

the exact search found no partition by more than one right coset of subgroups
whose indices are pairwise distinct. These are the next 25 smallest viable
solvable non-supersolvable order-1440 SmallGroups by exported coset-instance
size after the previously checked IDs 946, 947, 948, and 660.

This does **not** check every group of order 1440, extend the unconditional
all-orders frontier, or solve the Herzog--Schonheim conjecture / Erdos 274.
It is a negative result for 25 explicitly identified finite groups.

## Selection rule

This was deliberately an easiest-first batch, not an exhaustive order-1440
census. `solvable_subgroup_stats.g` enumerates the solvable,
non-supersolvable SmallGroups of order 1440. `analyze_spectra.py` keeps only
groups whose subgroup-index spectra survive the reciprocal-sum, pairwise-gcd,
and Proposition 4.2 necessary conditions. Survivors are ranked by total coset
instance size (then number of unblocked patterns and GAP ID). The list above
is the first 25 not already covered by the earlier pilot IDs 946, 947, 948,
and 660. No conclusion is drawn about any unselected order-1440 group.

## Completeness and trust boundary

Every admissible distinct-index reciprocal pattern was exhausted with zero
per-pattern caps. Groups 1628 and 256 were completed over two disjoint pattern
ranges after the ordinary 600-second group deadline. Group 1625 was initially
completed over three disjoint ranges and then independently replayed cleanly
from pattern 1 with only the wall deadline raised; the clean replay returned:

```json
{"status":"COMPLETE_UNSAT","group":1625,"patterns":5402,"total_patterns":5402,"fixed_cases":5427,"nodes":3004731,"max_pattern_nodes":9793,"cap_patterns":0}
```

One earlier four-way wrapper run for 1625, 1628, 2547, and 2524 was killed by
an outer 620-second timeout before returning child JSON. It is discarded and
contributes nothing to the result.

The computation trusts GAP's SmallGroups data and subgroup/coset enumeration,
the exported TSVs, and the Python exact-search implementation. The negative
outputs are exhaustive traversals, not proof certificates from a formally
verified checker.

## Why normalization is lossless

Given a putative partition containing a right coset `H g`, globally multiply
the partition on the right by `g^-1`; the selected coset becomes `H` and all
other selected sets remain right cosets. An inner automorphism then carries
`H` to the chosen representative of its subgroup conjugacy class while
preserving the form of every right coset. The solver branches over one actual
subgroup from every conjugacy class at the selected fixed index. Thus fixing
an identity-containing representative does not discard a partition.

The pre-search pruning uses necessary conditions only: indices exceed two,
their reciprocal sizes sum to one, every pair of indices has gcd greater than
one, and the Margolis--Schnabel Proposition 4.2 forbidden even-index triple is
excluded.

## Provenance

- Repository HEAD at final audit: `678645d4351966834227d281b0019594b6b868b7`.
- The search ran from ignored `.research-cache/hs274` inputs. This compact
  package is the public record. The large generated coset TSVs are not copied
  here; their row counts and SHA-256 hashes are locked in
  `batch25_results.json`.
- Python 3.12.4.
- GAP 4.10.2 in image `gapsystem/gap-container:latest`, local digest
  `sha256:b93bd242335adf5d0fc575e8e9d1bda840e711ff133b528722deb8b43f9fc66a`.
- Full source, input, result, and per-group TSV hashes are in
  `batch25_results.json`.

## Replay

To regenerate the subgroup statistics and the 25 coset TSVs, mount this
directory as `/work` in the recorded GAP image and run:

```powershell
docker run --rm -v "${PWD}/experiments/erdos274_order1440:/work" gapsystem/gap-container:latest gap -q /work/solvable_subgroup_stats.g
docker run --rm -v "${PWD}/experiments/erdos274_order1440:/work" gapsystem/gap-container:latest gap -q /work/export_batch.g
```

Then, from the repository root:

```powershell
& .\.venv\Scripts\python.exe experiments\erdos274_order1440\search_batch_exact.py 655
& .\.venv\Scripts\python.exe experiments\erdos274_order1440\search_batch_exact.py 1628
& .\.venv\Scripts\python.exe experiments\erdos274_order1440\search_batch_exact.py 256
```

Repeat for every `selection_order` entry in `batch25_results.json`. If the
ordinary deadline returns `TIMEOUT` after `p` completed patterns, resume with
start pattern `p+1`; the completed ranges must be disjoint and cover the full
`1..total_patterns` interval, and every segment must report zero caps.

For a clean full replay of the slow group 1625 with the same engine and only a
larger wall allowance:

```powershell
& .\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, r'experiments\erdos274_order1440'); import search_batch_exact as s; s.GROUP_SECONDS=3600; sys.argv=['search_batch_exact.py','1625']; s.main()"
```

Expected final line is the JSON shown above. Any future `SAT` result must be
replayed independently from the selected TSV rows by checking distinct
indices, pairwise-disjoint element sets, and union equal to all 1440 elements,
then reconstructed directly in GAP from the subgroup and right-coset data.
