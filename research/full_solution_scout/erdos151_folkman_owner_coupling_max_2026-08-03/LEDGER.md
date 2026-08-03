# Append-only research ledger

## 2026-08-03 — scope and exclusions

- Frozen exact target: `beta(G)>=H(n)` with ambient maximal cliques; K4-free
  `tf_3<H` is sufficient only.
- Read prior owner, Folkman, threshold-link, catalogue, Cayley, extension,
  random-block, and order-41 artifacts.
- Excluded reruns: tripartite owners, one/two-vertex extensions, Cayley and
  circulant scans, public catalogues, generic CEGAR, and parameter-only MSV
  tuning.
- Priority collision found: Mulrenin--van Overberghe,
  arXiv:2506.14942v4 (18 June 2026), already develops Hermitian cross-owner
  quasi-Folkman triangles and random block replacement.

## Cycle 1 — adaptable K4-free links

- Hypothesis: K4-freeness raises the adaptable-link obstruction threshold
  beyond the prior general seven-edge classification.
- Exact result: all 31 triangle-free `delta>=2`, `m<=9` unlabeled graphs are
  universally adaptable; the definition, custom Hell--Zhu checker, and
  NetworkX checker agree.  First failure is `m=10`.
- Campaign relationship: independently recovers the already-used
  `t_Q(v)>=10` conclusion without Bikov's degree-eight classification.
- Extension: exactly ten obstruction types have `m in {10,11}` and
  `n in {8,9,10}`.  These are the only links of an ambient degree-ten core
  vertex in the order-50 `beta<=10` lane.
- Failure/residual: ambient degree-nine vertices are not controlled by the
  degree-ten saturation inequality.

## Cycle 2 — cyclic retained cross-owner clauses

- Hypothesis: retained extrinsic triangles can force arrowing even if every
  unique edge owner is nonarrowing.
- Exact result: 88 cyclic triangles on 55 edge variables have no Property-B
  colouring; custom NAE, CaDiCaL, and Glucose agree.  No four selected clauses
  are the faces of one K4.
- Owner model: the 55 edges of `K11` partition into five circular-distance
  `C11` owners, and every selected triangle is cross-owner.
- Fidelity limit: this is an abstract post-deletion edge partition, not a
  literal MSV support family; all five cycles span the same vertices.
- Failure/residual: the two-shadow is `K11`, with `beta=10>=H(11)=4`.

## Cycle 3 — K4-free triangle signal senders

- Hypothesis: a small equality/inequality sender could lift the cyclic clauses
  to a K4-free shadow.
- Exact result: no connected K4-free sender with vertex-disjoint signal edges
  exists through order eight.  Complete counts: 642 atlas graphs through order
  seven; 5,606 K4-free connected order-eight graphs from `geng`.
- Independent checks: direct colouring plus Glucose through order seven;
  Glucose and CaDiCaL agree on all 490,354 order-eight parity queries.
- Quantified obstruction: the cyclic seed has 264 occurrences of 55
  variables, requiring 209 tree-linked sender copies in the standard lift.
- Failure/residual: shared or algebraic gadgets and order-nine-or-larger
  senders remain possible.

## Cycle 4 — Hermitian random-block certificate

- Hypothesis: the current Hermitian replacement theorem may scale to the
  `beta<H` degree window.
- Finite gate: a direct strict `maxcut<2m/3` certificate cannot fit inside a
  triangle-free K9 owner because it forces chromatic number at least four, and
  the smallest triangle-free four-chromatic graph has order 11.
- Asymptotic result: positivity of the paper's displayed union bound forces
  `p=Omega(s sqrt(log(sq)/q))`; its Lemma 4.4 event then forces degree
  `Omega(s q^(5/2)sqrt(log(sq)))`, above
  `H(q^4-q^3+q^2)=O(q^2sqrt(log q))`.
- Scoped closure: the displayed McDiarmid/union-bound certificate cannot
  certify a #151 counterexample for large q, even with `F=F_q`.
- Residual: deterministic/global discrepancy at density
  `p=O(sqrt(log q)/q)` and finite `H_3` subgraphs remain open.

## Handoff

- Status: `CONTINUE_PACKET`.
- Preferred next object: an exact ambient solver for the protected order-50
  interface (distinguishing vertices outside the core from vertices outside
  the owner's full support), or a genuinely low-density global cross-owner
  discrepancy lemma.
- Any candidate must be checked by two arrowing encodings and by exact
  ambient `beta`; no candidate exists in this packet.
