# Final report: Erdős #149 structural/construction lane

Frozen: 2026-08-03

## Outcome

No full solution and no counterexample were found. The lane did produce a
rigorous bounded theorem and a sharply negative construction signal:

* every finite simple graph with maximum degree at most four and order at most
  11 has strong chromatic index at most 20;
* every 4-regular graph of order at most 12 has strong chromatic index at most
  20;
* no candidate occurs in 8,750 labelled one-vertex perturbations of the
  extremal $C_5[2]$, the order-11/12 4-regular circulant pulse, or the complete
  1,544-graph connected 4-regular order-12 catalogue.

These statements do **not** resolve Erdős problem #149.

## Proof route at order 11

The published CGTT theorem rules out 21-edge counterexamples. At
$n=11,m=22$, 4-regularity holds, and needing 21 colours would force the
compatibility graph of induced-$2K_2$ edge pairs to be a nonempty star. The
analytic proof in **N11_ANALYTIC.md** eliminates that star:

1. a local closed-neighbourhood count bounds the star to one, two, or three
   leaves and localizes all triangles;
2. length-three-path and 4-cycle parity eliminates the three-leaf case and
   reduces the triangle-free case to one leaf;
3. common-neighbour moments then force a rank-four perturbation identity for
   the adjacency matrix; commutation with that perturbation contradicts
   4-regularity.

The root campaign independently audited the proof line by line. A separate
lane also produced a checked CaDiCaL DRAT certificate and independently
checked LRAT certificate for the labelled star obstruction, plus an
independent traversal of all 265 connected 4-regular order-11 graphs.

## Exact order-12 regular slice

The public 1,544-record connected 4-regular catalogue has SHA-256
6030d7de5212d195f3872606e947298aa3cfe0f594850f81c0f45105291919ae.
The custom checker found four disjoint compatibility pairs in every graph.
A separate NetworkX blossom replay found maximum compatibility-matching sizes:

| Size | Count |
|---:|---:|
| 9 | 3 |
| 10 | 25 |
| 11 | 124 |
| 12 | 1,392 |

Each matching of size four supplies four two-edge colour classes and saves
four colours from the 24 singleton classes.

Disconnected 4-regular order-12 graphs are also covered without a catalogue:
each component has order at least five and hence at most seven, so each has at
most 14 edges. Colour edges distinctly inside a component and reuse colours
between components.

Nonregular order-12 graphs are outside this computational theorem.

## Decision

Pause this #149 negative-construction lane. The order-12 compatibility
matchings have substantial slack, and the closest $C_5[2]+x$ perturbations are
not close to the exact star obstruction. Do not expand to order 13 without a
new structural signal, a near-candidate from another lane, or specialist
feedback suggesting that the order-11 matrix argument extends.

For precise proofs, source audit, reproduction commands, and all claim
boundaries, see **N11_ANALYTIC.md**, **STRUCTURAL_NOTES.md**,
**PRIORITY_AUDIT.md**, and **README.md**.

