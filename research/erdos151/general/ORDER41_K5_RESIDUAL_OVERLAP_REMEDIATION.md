# Order-41 omega=5 overlap package: audit remediation

Date: 2026-08-02

Status: **PASS after repair of the audited enumeration defect.**  This
remediation verifies only the stated finite reduction.  It does not close
order 41 or Erdos problem 151, and it does not exclude either the rigid row
or the one-double-neighbour row.

## Defect and repair

The immutable audit `ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.md` correctly marked
the original package **FAIL**.  When an input record matched an existing
exact-isomorphism class, the checker transported its cross-degree vector
through every representative-to-record isomorphism.  When a record created
a new class, however, the checker stored only one seed vector.  Thus the new
class was not closed under every automorphism of its representative.

The repaired `exact_common_core_classes` enumerates every automorphism of a
new representative and stores the full orbit of its seed vector.  It also
hard-fails unless the corrected totals are reproduced:

```text
dominating partitions                    4368
exact common-U isomorphism classes        786
automorphism-closed aligned patterns     1963
row T before / after D_0                 10 / 0
row D surviving common-U cores             17
```

This replaces the defective `1920 / 6 -> 0 / 12` output.  The five restored
row-D cores are:

```text
K`_PYYCE@BGQ
K??P`XMUCKyG
K`_PYWWOkHCI
K@?JKhheagT?
K@hWOHacbAqK
```

## Binding

The machine-readable binding is
`ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.json`.  Its repaired-artifact
hashes are:

```text
ORDER41_K5_RESIDUAL_OVERLAP.md
  880b2de61369c2539218ec027b9757b9f8da5b98dd8243a9e06c11e0a09d07ca
ORDER41_K5_RESIDUAL_OVERLAP_RESULT.json
  02452b459e79c672b79089c550fd48b1f0eba7cf6257b90c0e891f01efc9d987
checks/check_order41_k5_overlap.py
  d4eee390c83862f5b166b9bbd6c71415929d0bf428e7f62aeec2817ba3cc3d95
checks/order16_beta5_triangle_witness.json
  b3778f99571afed723c088143df118e00ab36515083167445b37f024a6e5ad36
```

The original FAIL audit remains unchanged at SHA-256
`bde66a3d221f5e1762e218cc7b40de70ca690e019c3c99c93a1b0cd1d2120567`
for the Markdown and
`6f3411401846cc7304264c0025da252f4421467c15190a19572b94b270a19165`
for its JSON binding.

## Corrected claim boundary

Conditional on completeness of the pinned Ramsey `(3,6;17)` catalogue, row
T is excluded and row D is reduced to 17 common cores.  Row D is not
excluded, row R remains open, and no survivor search or full order-41 claim
is part of this remediation.
