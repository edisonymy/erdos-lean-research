# Claims ledger: triangle-hypergraph / adaptable-link attack on Erdos #151

Date: 2026-08-03

This file separates proved statements, exact computational checks, and open
frontiers.  It does **not** claim a solution of Erdos problem #151.

## Proved

### P1. Exact property-B formulation

For a graph `G`, let `T(G)` be the 3-uniform hypergraph with vertex set
`E(G)` and one hyperedge `{xy, yz, zx}` for every triangle `xyz` of `G`.
Then `G` has a red/blue edge-colouring with no monochromatic triangle if
and only if `T(G)` has property B (a two-colouring of its vertices with no
monochromatic hyperedge).

### P2. Signed-link / adaptable-colouring bridge

Let `Q` be subgraph-minimal with `Q -> (3,3)`, fix `v in V(Q)`, and take a
red/blue edge-colouring of `Q-v` with no monochromatic triangle.  Label each
edge `xy` of the link `L_v = Q[N_Q(v)]` by the colour of `xy`.  Assigning a
colour to the spoke `vx` is the same as assigning a colour to the link
vertex `x`.  The colouring extends over `v` exactly when no link edge `xy`
has the same colour as both `x` and `y`.  Thus the inherited link labelling
has no adapted two-colouring, and `L_v` is not adaptably 2-colourable.

### P3. Threshold-six theorem

**Theorem.** If every vertex of a finite simple graph `G` lies in at most
six triangles, then `E(G)` has a red/blue colouring with no monochromatic
triangle.

Equivalently, every graph that arrows `(3,3)` has a vertex in at least seven
triangles.

The complete proof is in `REPORT.md`.  Its only external inputs are:

1. Hell--Zhu's exact characterization of connected adaptably
   2-colourable graphs;
2. Brooks' theorem.

The six-edge link classification used in the proof also has an elementary
hand proof in `REPORT.md` and two independent exhaustive checks.

### P4. Seven-regular order-28 profile is impossible

Conditional only on the campaign's already audited order-28 structural
package (`beta(G) <= 7`, seven-regularity for this profile, the swap lemma,
and the two-walk bounds), the new threshold-six theorem eliminates the
seven-regular profile at order 28.

Indeed, the old bounds give `t_v <= 7` at every vertex.  An arrowing core
and P3 force equality `t_v = 7` somewhere.  The exact link analysis and the
old equality bounds force

`G[N(v)] = Djs disjoint_union 2 K1`.

The two isolated link vertices and equality in the unique-common-neighbour
count then yield an independent set of eight vertices, contradicting
`beta(G) <= 7`.  Details are in `REPORT.md`.

This does not eliminate the mixed degree-5/6/7 profiles at order 28.

### P5. Threshold-seven theorem

**Theorem.** If every vertex of a finite simple graph `G` lies in at most
seven triangles, then `E(G)` has a red/blue colouring with no monochromatic
triangle.

Equivalently, every graph that arrows `(3,3)` has a vertex in at least eight
triangles.  The complete proof and source boundary are in
`THRESHOLD7_LINE_GRAPH.md`; a separate clean-room audit returned `PASS`.

The proof first uses the exact link classification to reduce a minimal
arrowing core to bowtie, `Djs`, and joined-triangle links.  A local
true-twin argument eliminates `Djs`.  The bowtie and joined-triangle links
then make the core the line graph of a connected loopless 4-regular
multigraph.  Krausz's classical multigraph line-graph construction and the
small-degree Goldberg theorem give a proper five-colouring of the core,
whose pullback from the standard good edge-colouring of `K5` contradicts
arrowing.

This is a uniform structural theorem, but it does not solve Erdos #151.

## Exactly checked by computation

### C1. Primary tiny-link enumeration

`signed_link_obstructions.py` independently enumerates every edge signing
and every link-vertex colouring for every connected unlabeled graph with
minimum degree at least two and at most seven edges.  It also compares the
answer with the Hell--Zhu edge-deletion criterion.

It checks 18 isomorphism types.  There are no obstructions with at most five
edges, exactly `K4` and the bowtie with six edges, and exactly two additional
minimal types with seven edges (`Djs` and two triangles joined by a bridge).

### C2. Independent threshold-six audit

`root_independent_threshold6_audit.py` uses nauty `geng`, a separate graph6
decoder, separate bipartiteness code, and a separate exhaustive
signing/colouring implementation.  It checks the nine connected
minimum-degree-two types with at most six edges and again finds exactly
`K4` and the bowtie.  Status: `VERIFIED`.

### C3. Threshold-seven local-structure audit

`threshold7_local_structure_audit.py` checks directly that the two
degree-three neighbourhoods of `Djs` induce `P3`, those of the joined-
triangles graph induce `K2 disjoint_union K1`, `Djs` has no adjacent true
twins, and the two triangles in each surviving bowtie/joined-triangles link
cover every link vertex.  Its saved result matches a fresh replay and has
status `VERIFIED`.

### C4. Independent finite local-core evidence

The companion `erdos151_threshold7_local_core_max_2026-08-03` package uses
two independent exhaustive enumerators to scan every connected degree-5/6
graph through order 12 (10,814,685 graphs in the unpruned audit).  Exactly
four local cores survive; independent CaDiCaL and Z3 colourings show that
none arrows `(3,3)`.  All four are line graphs of loopless 4-regular
multigraphs.  This is independent evidence for P5, not a premise of its
general proof.

## Open / not claimed

### O1. Full Erdos #151

The campaign separately proves the conjecture through order 39 and has
partial order-40/41 theorems.  P5 is a new all-order necessary condition on
an arrowing counterexample; it does not close the surviving order-40/41
cases or later Ramsey jumps.  No full solution or counterexample is claimed.

### O2. Priority

Targeted searches found no exact prior threshold-seven/eight-triangle
theorem.  This is evidence, not a categorical priority guarantee.  The
marked-neighbourhood framework and the bowtie/`Djs` local obstructions occur
in Bikov's work; Krausz's root construction and the edge-colouring theorem
are classical/published ingredients.  Any novelty claim must be limited to
their Ramsey-local-structure synthesis.
