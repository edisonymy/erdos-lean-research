# Independent audit record

**Status:** `VERIFIED` through order 27 on 2 August 2026.

The initial through-17 audit was performed by a separate agent before the
order-14 solver portfolio was stopped.  The order-18 extension received a
fresh independent Sol/max audit before the later order-18 portfolio was
stopped.  These audits verify a bounded theorem and structural reduction only,
not the full Erdős problem.

## Checks performed

1. **Definition duality.**  The complement of a clique transversal is exactly
   a set containing no inclusion-maximal clique of size at least two, so
   `tau(G)=|V(G)|-beta(G)`.
2. **Neighborhood lemma.**  Every clique inside `N(v)` extends by `v`, hence
   `beta(G)>=d(v)`.
3. **Recurrence direction.**  For `F=G-N[I]`, a nontrivial clique in
   `I union S` lies in `S`.  If it is maximal in `G`, it is maximal in `F`.
   The proof does not reverse this implication.
4. **Base orders.**  The exceptional maximum-degree-two case with six
   vertices and independence number two is `2 K_3`; it has an avoiding set of
   size four.
5. **Order nine.**  If maximum degree is at most three, odd-order parity
   supplies a vertex of degree at most two; its residual has order 6--8.
6. **Strong induction.**  For orders 10--13 the residual has order at least
   six; for orders 14--17 it has order at least nine.  No order outside the
   established induction range is invoked.
7. **Ramsey dependencies.**  The small-order proof and order-18 reduction use
   `R(3,2)=3`, `R(3,3)=6`, `R(3,4)=9`, `R(3,5)=14`, and `R(3,6)=18`.
8. **Order-18 reduction.**  The independent-set recurrence was reapplied with
   `r=1,2,3,4`; the clique-number argument was checked using maximal rather
   than maximum cliques.
9. **Mixed degree sequences.**  A fresh Sol/max audit independently checked
   the nonbacktracking length-two-walk identity, every multiplicity bound, and
   all 30 admissible `(p,s)` entries in the degree-four link table.  No even
   `p<18` is feasible.
10. **5-regular case.**  The audit checked the second walk count, the exact
    three possible link graphs, the triangle-component classification, and
    every mixture of `L`- and matching-edges in the auxiliary graph.
11. **Ramsey conclusion.**  An independent six-set in the triangle-free
    auxiliary graph avoids maximal edges via `L` and all larger cliques via
    the triangle-hitting matching.  `R(3,7)=23` and odd-degree parity then
    propagate the result through order 22.
12. **Lean recurrence check.**  The definitions of nontrivial
    inclusion-maximal clique and avoiding set, the induced-maximality
    direction, the residual lifting argument, and the finite-cardinality
    recurrence were compiled with Lean 4.27.0/mathlib 4.27.0.  The source is
    sorry-free.  `#print axioms` reports no axioms for the induced-maximality
    lemma and only `propext`, `Classical.choice`, and `Quot.sound` for the
    principal recurrence chain.  This check covers the recurrence only.
13. **Order-24 reduction.**  A fresh Sol/max audit independently checked the
    weak order-23 bound, component additivity/budget argument, regularity,
    `K_6` exclusion, common-neighbor cap, neighborhood-swap lemma, and every
    two-walk and link inequality in [`order24.md`](order24.md).
14. **Triangle-edge coloring.**  The audit reconstructed the deletion
    induction and the classification of a residual core as vertex-disjoint
    `K_4` components.  As a bug-finding cross-check, it also exhaustively
    tested all 2,097,152 graphs on a fixed labeled seven-vertex set; all 1,159,326
    graphs satisfying the lemma's hypothesis admitted the required coloring.
    The human proof, not this finite check, establishes the general lemma.
15. **Ramsey and propagation.**  The audit checked that `J=L union M` is
    triangle-free and that its independent seven-set avoids every ambient
    inclusion-maximal clique.  It also checked the strong induction proving
    `beta(G)>=7` for all orders at least 24.  The conversion to #151 at orders
    24--27 explicitly uses `R(3,8)=28`.
16. **Order-23 Ramsey reduction.**  A separate Sol/max agent reconstructed
    the reduction to a subgraph-minimal `(3,3)`-Ramsey graph, the implication
    `chi>=6`, every use of Brooks' theorem, and the proof that every edge of
    the Ramsey-minimal graph lies in at least two triangles.
17. **Order-23 link count.**  The audit checked both spoke-coloring
    extensions for a six-edge link (`C_6` and `2C_3`), the exact walk identity,
    the equality case `t=7`, the direction of the neighborhood-swap lemma,
    and the proof that the Ramsey-minimal graph has a unique degree-six
    vertex.  An independent ternary link enumerator was used only as a sanity
    check; the published proof is analytic.
18. **Critical-graph finish.**  The audit checked the existence and exact
    degree pattern of the 6-critical subgraph and the application of Gallai's
    low-vertex theorem.  Leaf blocks, cut vertices, disconnected components,
    odd-cycle blocks, and clique blocks are all explicitly accounted for.
    The resulting degree-four vertex count is impossible.
19. **Fresh citation/proof audit.**  A further independent Sol/max pass caught
    and corrected a pre-publication bibliographic error: Gallai's low-vertex
    theorem is Satz E.1 of *Kritische Graphen, I*, not part II.  It then
    reconstructed the corrected proof from scratch and returned `VERIFIED`.

## Computational cross-check

Before the analytic proof was found, two independent implementations checked
all 274,668 unlabeled graphs of order nine generated by nauty `geng`:

```text
counterexamples: 0
maximum tau:      5
graph6 SHA-256:   a9c1a5a0a15d21986a1e1525eaa14b6864e867c2825bb5b7315b2285fc81c11a
geng SHA-256:     64fa2d95bdaff155ce0fc748d4cba83a50e5ffb03e3acc5f41d86581c0bba7ef
```

One implementation enumerated maximal cliques and optimized `beta`; the other
searched every submask of every four-set with a separate graph6 parser.
All graph counts, edge histograms, hashes, and counterexample counts agreed.
This computation is only a sanity check because the public proof is analytic.

## Superseded order-14 search

The exact CNF had 3,549 variables and 62,335 clauses, with SHA-256
`c90e3e3e5f11e004a1a401f7269c53f5a5cb3832de16aa1ca2ec28af7d18eeb2`.
An independent clause audit found no missing, extra, duplicate, or out-of-range
clauses.  Four proof-free SAT runs were stopped after 1,024.859 wall seconds
once this proof audit succeeded.  They had found zero candidates and produced
no SAT/UNSAT conclusion.  Their exact status is
`STOPPED_AFTER_STRUCTURAL_PROOF`; all CNF, source, metadata, and log artifacts
remain preserved locally, and no file was deleted.

## Superseded order-18 search

Before the analytic order-18 contradiction was found, direct candidate CNFs
were built for degree-four counts `q=0,2,4`.  An independent clause-multiset
auditor reconstructed every semantic clause and verified all three instances:

```text
q=0: 371,229 clauses, SHA-256 7743cdb0016c3637627e6b9b5c7e835e4ba7c3f491740115ec14d4469658b1e1
q=2: 355,453 clauses, SHA-256 44e7e22569ef763c0790f21bc61f8133335e372e3e2febbd4e9f569afb7074e8
q=4: 339,677 clauses, SHA-256 2305301e0d74c7696b5082c613ee3991e4991152c1bf995b6251ba5093b2aea2
```

The three proof-free CaDiCaL workers were identity-checked and stopped after
the fresh analytic audit succeeded.  None had emitted a candidate, result, or
solver conclusion.  Their status is `STOPPED_AFTER_STRUCTURAL_PROOF`, with
`unsat_claim=false`; all artifacts were preserved and nothing was deleted.

## Superseded order-23/24 design

A private candidate-first SAT encoding was designed, smoke-tested on small
semantics, and size-estimated.  The analytic proofs arrived before any large
CNF was materialized or any solver was launched.  It produced no candidate,
SAT/UNSAT status, certificate, or computational claim and is not used by the
proofs.

## Remaining trust boundary

The recurrence is kernel-checked, but the clique-transversal duality, Ramsey
inputs, order-18, order-23, and order-24 arguments, and finite-order
conclusions are not yet formalized, and the complete proof has not received
human peer review.  The `beta` duality is prior art (Bhat--Bhat--Bhat, 2023);
the search for prior occurrences of the recurrence and through-27 result is targeted rather than
exhaustive.  Those boundaries affect novelty and uptake, not the internal
validity of the elementary argument recorded in [`proof.md`](proof.md).
