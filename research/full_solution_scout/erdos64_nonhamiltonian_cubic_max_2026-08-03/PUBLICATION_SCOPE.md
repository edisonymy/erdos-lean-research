# Public packet scope

This directory records a finite route-closure result for Erdős problem 64.
It does **not** claim a proof, counterexample, novelty, or priority for the
full problem.

## Public claims

- All 556,471 connected simple cubic graphs through order 20 have empty
  dyadic edge core.
- All 148,790 graphs in the independently published complete order-22
  non-Hamiltonian cubic catalogue have empty dyadic edge core.  The
  7,170,657 Hamiltonian order-22 graphs are not included in this statement.
- Consequently the marked-edge subdivision mechanism produces no exact
  one-defect block with nonadjacent terminal neighbours through block order
  21.
- The proved adjacent-terminal triangle reduction extends the corresponding
  exclusion through block order 23.

## Root audit before publication

On 2026-08-03 a fresh process, separate from the producing scan, reran the
independent graph6 decoder and literal cycle-intersection checker on all
556,471 connected cubic graphs through order 20.  It again found 556,471
empty dyadic edge cores and no survivor.  The same checker was rerun on the
148,790-record order-22 non-Hamiltonian catalogue and again found no survivor;
the input SHA-256 was
`C1CB566CB76F9925A6400561F2153796DF1BA5E9A8EED370210CDB7F70949E9A`.

The triangle-reduction checker was also rerun from fresh output.  It compared
213,329 expanded-cycle instances over 1,899 marked edges in 112 base graphs,
and every cycle-length multiset matched the stated correspondence.

## Deliberately omitted bulk data

The public commit contains the theorem note, provenance, hashes, scanners,
independent checkers, and compact result summaries.  Generated graph
catalogues, downloaded archives, nauty source/build trees, binaries, and live
order-22 full-census shards are deliberately omitted.  Their authoritative
source URLs, commands, expected counts, and SHA-256 digests are recorded in
`GENERATOR_PROVENANCE.md` and `CENSUS_SHA256SUMS.txt`.

The whole-directory development manifest is also omitted because it includes
those intentionally unpublished bulk artifacts.  `CONTINUE_PACKET.json` and
`PROGRESS_VECTOR.json` are the compact machine-readable claim boundary.
