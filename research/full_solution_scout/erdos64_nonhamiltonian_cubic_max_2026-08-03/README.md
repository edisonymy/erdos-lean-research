# Erdős problem 64: canonical non-Hamiltonian cubic successor

## Outcome

**Status: `CONTINUE_PACKET`.**

No universal proof or counterexample was found.  This packet makes no
publication, openness, novelty, or priority claim.

**Successor update (2026-08-03):** `FULL_N22_SUCCESSOR.md` supersedes the
order-22 scope below.  A complete canonical census of all 7,319,447 connected
simple cubic graphs of order 22 has now passed both full core replays, with no
survivor.  The exact one-defect consequences are therefore block order 23 in
the nonadjacent-terminal case and block order 25 in the adjacent-terminal
case.  This remains a finite route closure, not a solution of problem 64.

It does close the predeclared exact finite route.  Official nauty `geng`
generated every connected simple cubic graph through order 20: 556,471
isomorphism classes in total.  Exact Hamiltonicity classification found
16,425 non-Hamiltonian classes.  Every graph has empty dyadic edge core, so no
edge can satisfy the marked-edge suppression criterion.  A separately written
graph6 parser and literal cycle-intersection checker replayed the entire
census with the same result.

The hardest external extension also closes: all 148,790 graphs in Flinders
University's independently generated complete order-22 non-Hamiltonian cubic
catalogue have empty dyadic edge core.  The Hamiltonian order-22 graphs were
not scanned.

The inherited target remains immutable at predecessor SHA-256

```text
1944398AE0DB9EB1FB5BCE122BB59306551330B7C3B1D915593EC8EDAF580EFB
```

## Exact counts

| order | connected cubic | Hamiltonian | non-Hamiltonian | empty core |
|---:|---:|---:|---:|---:|
| 4 | 1 | 1 | 0 | 1 |
| 6 | 2 | 2 | 0 | 2 |
| 8 | 5 | 5 | 0 | 5 |
| 10 | 19 | 17 | 2 | 19 |
| 12 | 85 | 80 | 5 | 85 |
| 14 | 509 | 474 | 35 | 509 |
| 16 | 4,060 | 3,841 | 219 | 4,060 |
| 18 | 41,301 | 39,635 | 1,666 | 41,301 |
| 20 | 510,489 | 495,991 | 14,498 | 510,489 |

Every total and Hamiltonian split agrees with the independently published
[Flinders/GENREG graph database](https://sites.flinders.edu.au/flinders-hamiltonian-cycle-project/graph-database/).
Generator sources, build digest, commands, catalogue URLs, and hashes are in
`GENERATOR_PROVENANCE.md` and `CENSUS_SHA256SUMS.txt`.

## What the finite result proves

For a simple cubic graph `H`, let `I(H)` be the intersection of the edge sets
of every simple cycle whose length is a power of two.  Subdividing a marked
edge can produce a dyadic-free exact one-defect block only if that edge lies in
`I(H)`.  Since `I(H)` is empty for every connected cubic graph through order
20:

- no exact one-defect block with nonadjacent terminal neighbours exists
  through block order 21; and
- after the new adjacent-terminal triangle reduction, no exact one-defect
  block with adjacent terminal neighbours exists through block order 23.

The second statement closes the predecessor's simple-multigraph gap.  If the
terminal triangle's two external neighbours coincide or are adjacent, a
square is forced.  Otherwise reducing the triangle yields a smaller simple
cubic marked graph.  Full proof and cycle correspondence are in
`TRIANGLE_TERMINAL_REDUCTION.md`.

## Small certificates

The empty-core conclusion has unusually short finite witnesses.  Across all
556,471 graphs through order 20, 555,727 contain two edge-disjoint dyadic
cycles.  The remaining 744 have no such pair but have a minimum three-cycle
family with empty edge intersection.  No graph requires four cycles.

For the order-22 non-Hamiltonian catalogue, 148,787 graphs have a two-cycle
certificate and exactly three require three cycles.  This is a finite exact
pattern, not a theorem for arbitrary cubic graphs.

## Independent evidence boundary

The primary scanner uses perfect-matchings/complementary 2-factors for exact
Hamiltonicity and per-edge avoiding-cycle searches for the core.  The replay
checker imports none of that code: it uses a distinct graph6 decoder and
literally intersects independently enumerated cycle masks.  It replayed every
primary record and both separate Flinders non-Hamiltonian catalogues.

No candidate directory exists because no graph had a nonempty core.  Thus the
candidate-only requirement for two raw-edge parsers/cycle finders was never
triggered.

## Reproduction

From this directory, after building `nauty2_9_3/geng` as recorded in
`GENERATOR_PROVENANCE.md`:

```powershell
python scan_cubic_census.py cubic_n04.g6 cubic_n06.g6 cubic_n08.g6 cubic_n10.g6 cubic_n12.g6 cubic_n14.g6 cubic_n16.g6 cubic_n18.g6 cubic_n20.g6 --summary-out canonical_scan_through_n20.json --candidate-dir candidates

python verify_cubic_core_independent.py cubic_n04.g6 cubic_n06.g6 cubic_n08.g6 cubic_n10.g6 cubic_n12.g6 cubic_n14.g6 cubic_n16.g6 cubic_n18.g6 cubic_n20.g6 --summary-out canonical_full_census_independent_core_audit.json

python verify_cubic_core_independent.py flinders_22_NH/22_NH.g6 --expected-order 22 --expected-count 148790 --summary-out flinders_n22_nonham_independent_core_audit.json

python dyadic_pair_structure_scan.py flinders_22_NH/22_NH.g6 --expected-order 22 --expected-count 148790 --summary-out flinders_n22_dyadic_pair_structure.json

python verify_triangle_reduction.py cubic_n04.g6 cubic_n06.g6 cubic_n08.g6 cubic_n10.g6 cubic_n12.g6 --output triangle_reduction_finite_audit.json
```

## Next allocation

The strongest next mechanism is theorem-directed: explain the observed
two-or-three-cycle empty-intersection phenomenon in a structural cubic class
(for example via bridges, 2-cuts, or ear decompositions), using the seven
order-20/order-22 width-three exceptions in the non-Hamiltonian catalogues as
the first hostile tests.  A second exact option is a complete published
order-24 non-Hamiltonian catalogue, if one can be obtained with count and hash
provenance.  Do not spend the next cycle repeating the predecessor's stopped
Hamiltonian encodings, SMS/annealing, covers, necklace, line-tree, or Cayley
routes.
