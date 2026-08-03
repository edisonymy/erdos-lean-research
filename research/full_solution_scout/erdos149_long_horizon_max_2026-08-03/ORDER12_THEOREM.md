# Certificate-backed bounded theorem through order 12

Date: 2026-08-03

Status: computationally checked bounded theorem; not a full resolution of
Erdős problem #149 and not a public novelty claim.

## Theorem

Every finite simple graph `G` with `|V(G)| <= 12` and `Delta(G) <= 4`
satisfies

`chi(L(G)^2) <= 20`.

## Exact reduction

Let `J(G)` be the graph on `E(G)` in which two vertices are adjacent exactly
when the corresponding two edges of `G` induce `2K2`. Its cliques are the
induced matchings of `G`. If

`s(J) = max sum_i (|C_i|-1)`,

where the maximum is over vertex-disjoint nontrivial cliques of `J`, then

`chi(L(G)^2) = |E(G)| - s(J)`.

Indeed, a clique partition of `J` is exactly a strong edge-colouring, and
unused vertices can be filled with singleton classes.

Put `m=|E(G)|`. The handshake bound gives `m <= 24`.

### `m <= 21`

For `m <= 20`, singleton colours suffice. For `m=21`, the
Chung–Gyárfás–Tuza–Trotter theorem says that a subquartic `2K2`-free graph has
at most 20 edges. Thus `J` contains an edge, which saves one colour.

### `m=22`

If 20 colours were impossible, then `s(J) <= 1`. CGTT makes `J` nonempty, so
`s(J)=1`; consequently `J` has neither a triangle nor a matching of size two.
Every nonempty triangle-free graph with matching number one is a star plus
isolates. Relabel its centre edge as `01` and one leaf edge as `23`. These
G-edges are disjoint, so this symmetry fixing is always possible.

The root `m22_cert.cnf` is exactly this fixed star obstruction on 12 labelled
vertices. Padding a smaller graph with isolated vertices shows that the
formula covers every order at most 12. Its pinned LRAT certificate replays,
and `audit_root_encodings.py` independently reconstructed the clauses and
cardinality semantics. Hence this case is impossible.

### `m=23`

Here a counterexample has `s(J) <= 2`.

If `J` contains a triangle `T`, then any saving of three contains one of four
minimal forms relative to `T`: an edge disjoint from `T`; a `K4` containing
`T`; an alternate triangle using two vertices of `T` plus a disjoint edge; or
a matching of size three. Exhaustion of all 4,096 abstract six-vertex graphs
containing `T` found no omitted form. The root `m23_triangle.cnf` forbids
exactly these forms. Its LRAT certificate and fresh mapping audit verify UNSAT.

Suppose `J` is triangle-free. Then `s(J)=nu(J)`, so `nu(J) <= 2`; CGTT gives
`nu(J) >= 1`.

* If `nu(J)=1`, `J` is a nonempty star. The independently encoded `star.cnf`
  is UNSAT with replayed DRAT/LRAT certificates.
* If `nu(J)=2`, fix a maximum matching `M` of two J-edges. The four underlying
  G-edges split into exactly three endpoint-overlap types. Each compatible
  pair consists of two disjoint G-edges and forbids all four cross-connectors;
  therefore the cross-pair endpoint-intersection graph is itself a matching,
  of size 0, 1, or 2. These are `overlap0`, `overlap1`, and `overlap2`.
* For each type, unmatched vertices of `J` are constrained to be independent,
  and every alternating augmenting path relative to `M` of length 3 or 5 is
  forbidden. There are no longer simple augmenting paths because `M` has only
  two edges. Berge's theorem therefore makes `M` maximum. All three CNFs are
  UNSAT with replayed DRAT/LRAT certificates.

The fresh checker exhaustively tested the Berge equivalence on all 8,192
six-vertex graphs containing the fixed matching, enumerated all 99 admissible
fixed endpoint configurations, checked 95,040 truth assignments for the
exact compatibility indicators, reconstructed all clause multisets, and
replayed all four LRATs. Thus `m=23` is impossible.

### `m=24`

Equality in the handshake bound forces a 4-regular graph on 12 vertices. The
connected case is covered by the public catalogue of all 1,544 connected
4-regular graphs on 12 vertices, SHA-256
`6030d7de5212d195f3872606e947298aa3cfe0f594850f81c0f45105291919ae`.
A fresh NetworkX 3.5 blossom replay found compatibility matching numbers 9,
10, 11, and 12 with multiplicities 3, 25, 124, and 1,392, respectively. Four
disjoint compatibility edges already save four colours.

If the 4-regular graph is disconnected, every component has at least five
vertices, hence every component has at most seven vertices and at most 14
edges. Colour each component's edges distinctly and reuse the palette between
components, using at most 14 colours.

This completes the bounded theorem.

## Trust and claim boundary

The exact CNFs, proof hashes, independent LRAT output, mapping audits, and
catalogue recheck are recorded in `CERTIFICATION.json`. This theorem excludes
only graphs through order 12. It neither proves the universal 20-colour bound
nor supplies a counterexample, and must not be announced as a resolution of
Erdős problem #149.
