# Independent root audit: order 14

`audit_order14_independent.py` fully traverses all 2,859,237 graphs in the
two order-14 catalogues using a fail-first compatibility-matching algorithm
that differs from both package checkers. It regenerates both catalogues
byte-for-byte with the pinned `geng`. `AUDIT.result.json` records the verified
outcome and exact hashes.

This audits only the bounded theorem through order 14 and makes no claim to
resolve Erdos problem #149.
