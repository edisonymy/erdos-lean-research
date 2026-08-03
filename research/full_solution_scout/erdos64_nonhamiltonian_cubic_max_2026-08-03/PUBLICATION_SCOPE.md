# Public packet scope

This directory records a finite route-closure result for Erdős problem 64.
It does **not** claim a proof, counterexample, novelty, or priority for the
full problem.

## Public claims

- All 7,319,447 connected simple cubic graphs of order 22, and every connected
  simple cubic graph at each smaller even order, have empty dyadic edge core.
  The order-22 census includes both the 148,790 non-Hamiltonian graphs and all
  7,170,657 Hamiltonian graphs.
- Consequently the marked-edge subdivision mechanism produces no exact
  one-defect block with nonadjacent terminal neighbours through block order
  23.
- The proved adjacent-terminal triangle reduction extends the corresponding
  exclusion through block order 25.

## Root audit before publication

On 2026-08-03 a fresh process, separate from the producing scan, reran the
independent graph6 decoder and literal cycle-intersection checker on all
7,319,447 connected cubic graphs of order 22.  A second complete replay used
the producer's complementary avoiding-cycle formulation.  Both methods
validated all records, found every dyadic core empty, and produced no
candidate.  `N22_ROOT_AUDIT.json` independently rechecks all eight partition
counts, byte sizes, source hashes, completion flags, and null candidate fields.

The triangle-reduction checker was also rerun from fresh output.  It compared
213,329 expanded-cycle instances over 1,899 marked edges in 112 base graphs,
and every cycle-length multiset matched the stated correspondence.

## Deliberately omitted bulk data

The public commit contains the theorem note, provenance, hashes, scanners,
independent checkers, and compact result summaries.  The eight reproducible
order-22 graph6 partitions (300,097,327 bytes), downloaded archives, nauty
source/build trees, and binaries are deliberately omitted.  Their exact
commands, expected counts, byte sizes, and SHA-256 digests are recorded in
`FULL_N22_SUCCESSOR.md` and `N22_PUBLIC_AGGREGATE.json`.

The whole-directory development manifest is also omitted because it includes
those intentionally unpublished bulk artifacts.  `CONTINUE_PACKET.json` and
`PROGRESS_VECTOR.json` are the compact machine-readable claim boundary.
