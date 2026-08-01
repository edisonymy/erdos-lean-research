# Audit log

## Independent gate

The first Python screen reported 4,749 residual classes.  An independently
written Node.js parser reported 4,769.  The exact twenty-class difference was
isolated before promotion: in the Python two-vertex-cover test, the indicator
for the edge joining the two cover vertices was converted to its bit value
instead of Boolean `0/1`.  This omitted exactly twenty complements whose
two-vertex cover includes that joining edge.

After changing the expression to `int(bool(...))`, both screeners reproduced:

- 12,005,168 catalogue records;
- uncompressed catalogue SHA-256
  `923cabf28082cba3ee296251d23eee21b32056b36cf4952e42958d468357df36`;
- 4,769 residual records;
- residual SHA-256
  `a91c1ad52596a676edae8ff67fcd08490d6da80d757e3d92ebc13c529fafd130`.

The corrected primary exact pass generated 4,769 witness records with digest
`f57a18bcb2c8c7b821f85f73e02ad768b352416fa17ff4e8fe694ad6dd40c047`.
It found zero violations and maximum gap `-4`.

The independent verifier then:

- decoded every graph again with NetworkX;
- checked every graph mask and triangle count;
- checked every packing witness for existence and edge-disjointness;
- checked every cover witness for existence and complete triangle hitting;
- independently ruled out every packing of size `nu+1`;
- independently ruled out every cover of size `tau-1`.

It reproduced the same 4,769-record digest, zero violations, and maximum gap
`-4` in 111.87 seconds on the audit machine.

## Fresh-agent replay

A separate adversarial audit reran the package after it was assembled. It
independently re-derived the `h=8,9,10` Puleo reduction and the safety of the
`|E(C)|>17` early rejection, then obtained:

- primary Python catalogue screen: 12,005,168 inputs, 4,769 residuals, exact
  residual digest `a91c1ad5…fd130` (207.8 seconds);
- independent Node screen: a byte-identical 4,769-line residual (11.1 seconds);
- primary optimizer: record digest `f57a18bc…0c047`, zero violations, maximum
  gap `-4`, and the same full value distribution (91.9 seconds);
- independent verifier: all 4,769 records, digest `f57a18bc…0c047`, zero
  violations, maximum gap `-4` (48.2 seconds).

The auditor also recreated the original Boolean/bit-value defect and confirmed
that it omits exactly the documented twenty classes. Its reporting connection
failed after these artifacts were written, but the complete replay summaries
and hashes were inspected locally. No mathematical or implementation defect
was found in the corrected package.

As a non-mathematical hardening, the auditor removed the primary screener's
early return for the global-density family. The emitted family field now records
all applicable residual bits, including overlaps (`3`, `5`, and `7`), rather
than a priority classification. A fresh 12,005,168-record screen gave counts
`1:3710, 2:142, 3:743, 4:36, 5:4, 6:14, 7:120` with the same 4,769 records and
the same residual digest. This changes only diagnostic metadata.

## Public-priority checkpoint

The July 24 public report proves only the through-order-nine result and
explicitly disclaims consequences for order ten and above.  A July 26 public
feasibility note considers a naive order-ten extension impractical because it
counts 4,346,814,276 labeled complements with at most ten missing edges; it
does not exploit the official 12,005,168-class unlabeled catalogue and does not
report an order-ten computation.

Authenticated GitHub code searches on 2026-08-01 for `Tuza "order 10"`,
`Tuza "order ten"`, and related terms found those public planning/report files
but no independently posted order-ten closure.  Current arXiv and the live
Erdős Problems page still list the general conjecture as open.  This is a
reasonable priority screen, not a proof that no unpublished or unindexed
bounded computation exists.
