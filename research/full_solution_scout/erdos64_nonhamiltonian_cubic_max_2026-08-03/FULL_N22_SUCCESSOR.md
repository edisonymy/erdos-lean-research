# Full canonical cubic order-22 successor result

Date: 2026-08-03

This file is a successor record. It deliberately does not rewrite the frozen
order-20 packet while that packet is being independently replayed.

## Exact result

Every one of the **7,319,447** connected simple cubic graphs of order 22 has
empty dyadic edge core. Here the dyadic edge core is the intersection of the
edge sets of all simple cycles whose lengths are powers of two; at order 22 the
relevant lengths are 4, 8, and 16. No graph with no dyadic cycle and no graph
with a surviving marked edge was found.

Together with the already completed even orders 4 through 20, this proves the
finite census statement:

> Every connected simple cubic graph of order at most 22 has empty dyadic edge
> core.

This is a finite computational theorem, not a resolution of Erdos problem 64.

## Canonical coverage

The official nauty 2.9.3 `geng` binary was run with connectedness and exact
degree three, split into all eight canonical residue classes `0/8` through
`7/8`. The archive SHA-256 is
`9FC4EDAE04F88A0F5883985BE3B39CF7F898FD6CC96E96B9EE25452743CC1B5B`;
the compiled `geng` SHA-256 is
`54905DF2D5262992CE80ABABA785FF5A41B223A2A6B03C1274D5A9BE4A9A181A`;
and the local image digest is
`sha256:c9de640c09ecd5223afa907847a97a7397f11a5b45970095c967c4bb99f40b5c`.

| residue | records | bytes | graph6 SHA-256 |
|---:|---:|---:|:---|
| 0/8 | 518,580 | 21,261,780 | `995C0FA902B3AEF0F2CBE2CAEA5861C98AD208634CBC6F792C85AD9AE9DE84C3` |
| 1/8 | 670,736 | 27,500,176 | `4F53504C0F28841844766DE869DBA10C3B386A6394631F1DC0F6DF9F5325C081` |
| 2/8 | 982,556 | 40,284,796 | `4B2F1F67B8552297CA1C23DBA1467A108692A097D71B55CDC5958ED1DE7E48CE` |
| 3/8 | 1,068,280 | 43,799,480 | `98CE6135DAD2DDFC54C0A9D3ECD0E973A7225A9335BD3BC386500C61CAFF1FF6` |
| 4/8 | 1,569,040 | 64,330,640 | `1E392F748B9C3365A94707ECABB0DC92EC38318A5F964F3C1958BEE431DEFE3B` |
| 5/8 | 879,959 | 36,078,319 | `F04D9CD2693B2CE19AD1E1F9B033B7AF1E54975C28F58FF54E03FE77AEF6BA9F` |
| 6/8 | 978,267 | 40,108,947 | `928E9C7A3052BF79F709731692E9A432BFDF82EE2D23AEB481029C0EAD38F6A9` |
| 7/8 | 652,029 | 26,733,189 | `2F53F9C4960194E9E58AC441F16CFC5BDE028E544AA7DA53114B6708E2CF7AB0` |
| **total** | **7,319,447** | **300,097,327** | -- |

Every order-22 graph6 record has 40 data bytes plus one LF byte, so each file
also satisfies `bytes = 41 * records`. The residue counts sum exactly to the
independently published connected-cubic total 7,319,447.

## Two complete core replays

1. `verify_cubic_core_independent.py` is code-independent of the producer. It
   has its own graph6 decoder and literally intersects edge masks of enumerated
   dyadic cycles. Across the eight partitions it validated 7,319,447 connected
   simple cubic graphs, found 7,319,447 empty cores, enumerated 18,515,894
   dyadic cycles before the respective empty-intersection decisions, and
   returned no first survivor. All eight completion flags are true.

2. `scan_cubic_n22_partition.py` is a separate partition-safe driver around
   the frozen producer's avoiding-cycle primitives. It tests the complementary
   formulation edge by edge and has an immediate raw-candidate dump path. It
   independently validated the same 7,319,447 records, found 7,319,447 empty
   cores, returned `candidate: null` and `complete: true` in all eight
   summaries, and never created `candidates_n22/`.

Thus the two methods agree on every canonical graph. The first is a genuinely
independent parser and cycle/core implementation; the second is a redundant
full replay using the producer implementation, not a claim of code
independence from that producer.

## Exact one-defect block consequences

The order shifts in the two terminal cases are different and must not be
conflated.

* If the degree-two terminal has nonadjacent neighbours, suppression lowers
  the block order by one. Cubic exhaustion through order 22 therefore excludes
  this exact one-defect block case through **block order 23**.
* If the degree-two terminal has adjacent neighbours, the triangle-terminal
  reduction lowers the block order by three. Cubic exhaustion through order 22
  therefore excludes this exact one-defect block case through **block order
  25**.

These are the audited asymmetric bounds **23/25**. They apply to the exact
`(2,3,...,3)` block normal form under the corresponding suppression/reduction
hypotheses; they are not a reduction of arbitrary minimum-degree-three graphs
to cubic graphs.

## Replay artifacts

* Sources: `cubic_n22_part0.g6` through `cubic_n22_part7.g6`
* Generator logs: `cubic_n22_part0.log` through `cubic_n22_part7.log`
* Literal audit: `cubic_n22_part0_independent_core_audit.json` through
  `cubic_n22_part7_independent_core_audit.json`
* Avoiding-cycle audit: `cubic_n22_part0_avoiding_core_audit.json` through
  `cubic_n22_part7_avoiding_core_audit.json`
* Machine-readable aggregate: `FULL_N22_SUCCESSOR.json`

## Minimal public packet

Commit only the following small provenance, code, log, and result artifacts for
this successor result:

* `FULL_N22_SUCCESSOR.md`
* `N22_PUBLIC_AGGREGATE.json`
* `GENERATOR_PROVENANCE.md`
* `verify_cubic_core_independent.py`
* `scan_cubic_n22_partition.py`
* `scan_cubic_census.py`
* `cubic_n22_part0.log` through `cubic_n22_part7.log`
* `cubic_n22_part0_independent_core_audit.json` through
  `cubic_n22_part7_independent_core_audit.json`
* `cubic_n22_part0_avoiding_core_audit.json` through
  `cubic_n22_part7_avoiding_core_audit.json`

Do **not** add `cubic_n22_part*.g6` to Git. Those eight reproducible bulk files
occupy 300,097,327 bytes. Their exact counts, byte sizes, and SHA-256 values are
frozen in `N22_PUBLIC_AGGREGATE.json`.

## Reproduction commands

Run generation in the pinned Linux nauty environment. The following Bash loop
recreates all eight disjoint canonical residue classes:

```bash
counts=(518580 670736 982556 1068280 1569040 879959 978267 652029)
for i in {0..7}; do
  ./nauty2_9_3/geng -c -d3 -D3 22 33 "$i/8" \
    > "cubic_n22_part${i}.g6" \
    2> "cubic_n22_part${i}.log"
  test "$(wc -l < "cubic_n22_part${i}.g6")" -eq "${counts[$i]}"
done
sha256sum cubic_n22_part{0..7}.g6
```

Then run both complete core methods:

```bash
counts=(518580 670736 982556 1068280 1569040 879959 978267 652029)
for i in {0..7}; do
  python verify_cubic_core_independent.py "cubic_n22_part${i}.g6" \
    --expected-order 22 \
    --expected-count "${counts[$i]}" \
    --summary-out "cubic_n22_part${i}_independent_core_audit.json" \
    --progress-every 100000

  python scan_cubic_n22_partition.py "cubic_n22_part${i}.g6" \
    --partition "$i" --modulus 8 \
    --expected-count "${counts[$i]}" \
    --summary-out "cubic_n22_part${i}_avoiding_core_audit.json" \
    --candidate-dir candidates_n22 \
    --progress-every 100000
done
```

Success requires all 16 summaries to be complete, every validated and
empty-core count to equal its partition count, every candidate/survivor field
to be null, the aggregate to equal 7,319,447, and `candidates_n22/` not to
exist.
