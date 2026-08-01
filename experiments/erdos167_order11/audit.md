# Audit log

## Public-claim checkpoint (2026-08-01)

The live Erdos Problems page marked Problem 167 open and warned that the
database status is not a substitute for a literature search. Web, arXiv, and
authenticated GitHub searches were therefore performed separately for full,
order-eleven, and order-ten claims.

The closest public bounded computation found was the 24 July 2026 report
through order nine. Its independent audit explicitly limits the conclusion to
that order. A 26 July feasibility note discusses order ten but reports no
closure. The existing package in `../erdos167_order10` independently closes
order ten.

A large public Lean/Aristotle Tuza repository, last updated 24 June 2026, was
also checked. Its own status document says that the full conjecture remains
unproved and describes verified small-packing-number cases, weaker bounds,
conditional arguments, and counterexamples to attempted reductions. It does
not report an order-eleven theorem. The public draft Lean statement in
`ryantuck/erdos-ai` still ends in `sorry`.

No public order-eleven closure or full proof was found. This is a priority
screen, not proof that no unindexed or unpublished result exists.

## Enumeration replay

The first full construction used conda-forge's Windows nauty package, which
reports `Nauty&Traces version 2.6040`:

- `geng.exe` SHA-256
  `64fa2d95bdaff155ce0fc748d4cba83a50e5ffb03e3acc5f41d86581c0bba7ef`;
- `labelg.exe` SHA-256
  `99d7cd21c70a10bf60f7e5291dc9c7b87f2e8e58b39adbdf91f9e3186c10bd88`.

It generated raw family counts 1,850,130, 4,686,848, 10,485,760, and
51,480. Canonical union gave 2,174,357 LF-normalized records with digest
`5997409f26372eea577b7a6bec6b94e3f26282ba7ba5473ae9f54ab69ad98889`.

For a version-independent replay, the official current nauty 2.9.3 source was
downloaded and compiled separately under Linux:

- official tarball SHA-256
  `9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b`;
- built `geng` SHA-256
  `f8462cb6d8e0e09d22be9de7a5bc3fe06143bcee845cd2668cab8b4963a0d305`;
- built `labelg` SHA-256
  `b2dd747a7a655f18f3ef88bc7645a78a41325875fb3cc54c9a0471e07e609112`.

The base counts were again exactly 1,850,130 (`n=11,m<=16`), 4,577
(`n=10,m<=10`), and 20 (`n=9,m<=4`). After the independently built
canonicalizer processed the expansions, the ordinal union was byte-identical:
2,174,357 records and the same `599740...98889` digest.

An early manifest recorded the Windows CRLF byte hash while the independent
verifier deliberately normalized records to LF. The union writer was hardened
to emit LF explicitly; both implementations and both operating systems now
name the same exact byte digest.

An adversarial histogram review then found that the first union had passed the
raw `geng` representatives for family A directly to the set union, while
families B--D had first passed through `labelg`. A `geng` representative is
unique up to isomorphism but is not promised to equal `labelg`'s chosen
canonical byte string. This left duplicate isomorphism classes in the first
union (the counts for complements with one through four edges were visibly
doubled). The witness screens had therefore checked a harmless superset, but
the claimed unique-class count was wrong. The pipeline was corrected to run
**all four** families through `labelg`; both nauty versions then independently
produced the corrected 2,174,357-record, `599740...98889` union used here.

## Independent witness gate

The primary screen reports:

- residual records: 2,174,357;
- closed by packing/cover witnesses: 2,174,357;
- unresolved: 0;
- minimum primary slack `2p-c`: 1.

The independent verifier was written without sharing the graph6 decoder or
cut code. It uses affine vertex orders for its packings and Gray-code cut
updates rather than the primary subset recurrence. It checked strict canonical
ordering, the exact residual digest, and membership in the four-family Puleo
predicate, then reported:

- records: 2,174,357;
- outside the residual predicate: 0;
- unresolved: 0;
- minimum independent slack `2p-c`: 0.

The two screens need not construct identical witnesses; either complete pass
is sufficient for the bounded inequality. Their agreement supplies an
independent implementation gate without asserting exact optimization.
