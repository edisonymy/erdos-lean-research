# Target and priority freeze

Freeze time: 2026-08-03, Europe/London.

## Immutable mathematical target

The authoritative predecessor target is
`../erdos64_long_horizon_max_2026-08-03/TARGET_LOCK.json`, whose verified
SHA-256 is

```text
1944398AE0DB9EB1FB5BCE122BB59306551330B7C3B1D915593EC8EDAF580EFB
```

Its exact universal claim is:

> For every finite simple undirected graph G, if the minimum degree delta(G)
> is at least 3, then there exists an integer k >= 2 and a simple cycle C in G
> with |V(C)| = 2^k.

A disproof therefore requires a finite simple undirected graph of minimum
degree at least three with no simple cycle of length `2^k` for any `k >= 2`
up to its order.  No weaker object or cycle convention is admissible.

## Priority boundary

The predecessor literature audit dated 2026-08-03 found no independently
verified proof or counterexample.  This is search-relative evidence only.  It
does not establish openness, novelty, or publication priority.  The campaign
status at this freeze is `CONTINUE_PACKET`.

## Predeclared successor gate

Route ID: `S-NONHAM-CUBIC-CANONICAL`.

Generate exactly one representative of every connected simple cubic graph at
each even order `n = 4,6,...,20`, using a canonical generator with independently
validated census counts.  Discard Hamiltonian graphs only after an exact
Hamiltonicity decision.  For every retained non-Hamiltonian graph `H`, compute

```text
I(H) = intersection of the edge sets of all simple cycles whose length is a
       power of two.
```

If `I(H)` is nonempty, test each edge in it against all simple cycles of length
`2^k-1`.  A surviving edge must be dumped immediately as a raw edge list,
subdivided into a one-defect block, bridge-composed with a second copy, and
checked by two independent parsers/cycle-finders before any candidate claim.

Precommitted prediction: every connected cubic graph through order 20 has
empty `I(H)`.  If exact coverage validates this, then the suppression lemma
excludes every non-triangular exact `(2,3,...,3)` one-defect bridge block
through order 21.  Any exhaustion claim is conditional on exact generator
coverage, recorded generator/source hashes, known census counts, output
hashes, and independent replay.

This route is materially distinct from the predecessor's Hamiltonian matching
encodings, random cubic sampling, SAT/SMS, cover, necklace, line-tree, and
Cayley scans.
