# Independent root audit: order 15

`audit_order15_independent.py` independently reconstructs the complete
two-defect theta-core completion space and checks all 805,491 connected
4-regular graphs with a third fail-first compatibility matcher. It also
regenerates the regular catalogue byte-for-byte with the pinned `geng`.
`AUDIT.result.json` records the verified outcome and exact hashes.

This audits only the bounded theorem through order 15 and makes no claim to
resolve Erdos problem #149.
