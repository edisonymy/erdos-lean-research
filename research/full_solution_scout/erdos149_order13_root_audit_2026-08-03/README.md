# Independent root audit: order 13

`audit_order13_independent.py` fully traverses both order-13 catalogues with a
third matching algorithm. It also regenerates the 300,361-graph slice
byte-for-byte and compares the public 4-regular catalogue with a fresh `geng`
enumeration after canonical labelling. `AUDIT.result.json` records the
verified outcome and exact hashes.

This audits only the bounded theorem through order 13 and makes no claim to
resolve Erdos problem #149.
