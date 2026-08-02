# Independent audit of the order-41 `omega=5` rigid-row attack

**Date:** 2 August 2026. **Verdict: PASS.**

The claimed exclusion of row R is sound under the standing row-R
hypotheses.  Every maximal-clique direction used in the singleton-fibre and
terminal arguments is valid, the two possible adjacency cases for a pair in
one fibre are both covered, and the numerical squeeze is exact.  Independent
finite searches found no falsifier and, in two places, verified statements
strictly stronger than the checker shipped with the note.

This verdict is only for the row-R implication.  It is not an order-41
theorem, an Erdős problem #151 solution, a catalogue-completeness claim, an
UNSAT certificate, or a Git, publication, novelty, or priority claim.  No
source note or checker was edited during this audit.

## Audited inputs

The files were read at these exact SHA-256 values:

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_RIGID_ATTACK.md` | `9e3803fcb92234c8c75d9c687347bb82e92e7ae30262460d68dc38483c592ab3` |
| `checks/rigid_attack/check_rigid_attack.py` | `0f76e55bb1c28bda2c34dafa3952bf373f86877593e96f1302e650bf0ba46cd7` |
| `../README.md` | `e64f809c3d98bad75cce6d471515aa03d2f97a162d1761eb5d7ed76ae03df741` |
| `GENERAL.md` | `bc5503b15bff283ecd23aec8fd9d38496a4a8f108079cc5d5b4d50eefaab8a16` |
| `N40_CLIQUE_CASES_AUDIT.md` | `fce032ea2724c22bb2527624c737377f47461616a7707f518e0c1ea845bb132b` |
| `ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.md` | `bde66a3d221f5e1762e218cc7b40de70ca690e019c3c99c93a1b0cd1d2120567` |
| current repaired `ORDER41_K5_RESIDUAL_OVERLAP.md` | `880b2de61369c2539218ec027b9757b9f8da5b98dd8243a9e06c11e0a09d07ca` |

The authoritative definition is that an admissible vertex set contains no
inclusion-maximal clique of the ambient graph having at least two vertices.
Singleton maximal cliques are therefore irrelevant.

## Reconstruction of the standing package

For row R, the audited profile calculation gives a maximum clique `M` of
order five, eleven vertices `U` anticomplete to `M`, and five disjoint fans
`A_c` of order five whose vertices have `M`-neighbourhood exactly `{c}`.
There are no other vertices.  Every `c in M` has degree nine, every `A_c`
dominates `U`, and

```text
F_c = G[U union A_c],       beta(F_c)=5.
```

The equality `beta(G)=9` is part of the standing counterexample package (and
also follows from `beta(G)<=9` together with the through-order-39 lower
bound).  Every open neighbourhood is ambient-admissible, so
`Delta(G)<=beta(G)=9`.  None of these row-R facts depends on the Ramsey
catalogue whose old overlap enumeration required repair.

## Claim-by-claim audit

### 1. `S_c=N(c)` is maximum admissible — PASS

The row-R partition gives the exact set identity

```text
S_c=N_G(c)=(M-{c}) union A_c,       |S_c|=4+5=9.
```

Every nontrivial clique contained in `N(c)` extends by `c`; hence none is an
ambient-maximal clique.  Thus `S_c` is ambient-admissible.  Its order equals
`beta(G)`, so it is maximum admissible.  This uses maximality in the correct
ambient direction and does not assume that a clique maximal in an induced
subgraph is ambient-maximal.

### 2. Exact singleton fibres — PASS

Fix `a in A_c` and

```text
P_c(a)={u in U:N(u) intersect A_c={a}}.
```

For `u in P_c(a)`, the ten-set `S_c union {u}` is not admissible.  A
witnessing ambient-maximal nontrivial clique cannot be contained in `S_c`,
because every such clique extends by `c`.  It must contain `u`.  The exact
fibre condition and `U`'s anticompleteness to `M` say that `a` is the only
neighbour of `u` in `S_c`.  Consequently the witness can only be the edge
`ua`, and `ua` is an ambient-maximal 2-clique.

If distinct `u,v` were in the same fibre, there are exactly two cases:

- If `uv` is present, then `u,a,v` is a triangle because both fibre
  vertices meet `a`.  This extends `ua`, contradicting its ambient
  maximality.
- If `uv` is absent, then in
  `(S_c-{a}) union {u,v}` both inserted vertices are isolated.  Every
  remaining nontrivial clique lies in `S_c-{a}` and extends by `c`.
  Therefore this is an ambient-admissible ten-set, contradicting
  `beta(G)=9`.

This proves `|P_c(a)|<=1`.  The second case also explicitly covers isolated
vertices: they create no prohibited nontrivial clique.

### 3. Each residual cut has at least 17 edges — PASS

For a fixed fan, domination assigns each of the eleven vertices of `U` a
nonempty subset of `A_c`.  If `s_c` vertices have a singleton subset, the
five fibre caps give `s_c<=5`.  Hence

```text
e(U,A_c) >= s_c+2(11-s_c)=22-s_c>=17.
```

An independent dynamic program exhausted the 31 possible nonempty
neighbour sets for each of eleven labelled `U` vertices while tracking which
of the five singleton labels had already been used.  Its minimum total
incidence was 17.  Equality occurs only with five distinctly labelled
singletons and six 2-subsets; the labelled equality count was
`C(11,5)*5!*C(5,2)^6 = 55,440,000,000`.

### 4. `alpha(U)<=5` and the Turán extremum — PASS

An independent set in `F_c` is admissible in `F_c`.  Since `U` is induced
in `F_c` and `beta(F_c)=5`,

```text
alpha(U)<=alpha(F_c)<=beta(F_c)=5.
```

Thus the complement of `G[U]` is `K6`-free.  Turán's theorem gives

```text
ex(11,K6)=e(T_5(11))=48,
e(U)>=C(11,2)-48=7.
```

Equality in Turán's theorem uniquely gives the balanced complete
five-partite complement with part sizes `3,2,2,2,2`.  Complementing yields

```text
G[U] = K3 disjoint-union 4K2.
```

As a separate exhaustive check, a SAT encoding used one Boolean variable
for each of the 55 possible `U`-edges and one clause for every 6-subset
requiring it to contain an edge.  At most six edges was UNSAT.  With exactly
seven edges, projection enumeration found 17,325 labelled graphs, precisely

```text
11! / (3! (2!)^4 4!),
```

and every one had component type `K3 disjoint-union 4K2`.  This independently
checks both the extremal value and its equality rigidity.

### 5. Global `U`-degree budget and equality consequences — PASS

The row-R partition and `U`'s anticompleteness to `M` give the exact identity

```text
sum_{u in U} d_G(u)=2e(U)+sum_c e(U,A_c).
```

The degree-nine ceiling makes the left side at most 99.  Combining the five
cut bounds with `e(U)>=7` gives the reverse lower bound

```text
2*7+5*17=99.
```

Therefore every inequality is equality: `e(U)=7`, every cut has 17 edges,
and every vertex of `U` has degree nine.  The Turán equality case then gives
the component structure above.  Cut equality additionally forces exactly
five singleton vertices (one per fan label) and six vertices of fan-degree
two, as stated in the source note.

### 6. Terminal transversal lemma — PASS

Let `W=C_1 disjoint-union ... disjoint-union C_q` be induced in `F`, with
each `C_i` a clique of order at least two, and fix `a outside W`.  Define

```text
L_a={u in W: au is an F-maximal 2-clique}.
```

Membership implies that `au` is an edge.  If adjacent `u,v in W` both lay
in `L_a`, then `a,u,v` would be a triangle, so neither incident edge could
be maximal as a 2-clique.  Thus `L_a` is independent and contains at most
one vertex of each `C_i`.  Select `x_i in C_i-L_a`.  The transversal
`I={x_1,...,x_q}` is independent.

Every nontrivial clique in `I union {a}` is an edge `ax_i`.  If the edge is
absent there is nothing to check; if present, `x_i notin L_a` says exactly
that the 2-clique is not `F`-maximal.  No larger clique can be contained,
because `I` is independent.  Hence `I union {a}` is `F`-admissible.  If `a`
is isolated then `L_a` is empty and the same conclusion holds; its maximal
singleton is excluded by definition.  Other fan vertices and larger
cliques extending an incident edge only make that edge nonmaximal and do
not create a clique contained in the selected set.

For `F_c`, the five components of `G[U]=K3+4K2` give `q=5`, and any of the
five vertices `a in A_c` supplies the outside vertex.  Thus
`beta(F_c)>=6`, contradicting `beta(F_c)=5`.

An independent direct graph check went further.  For all `2^11=2,048`
possible neighbourhoods of one outside vertex `a` in `K3+4K2`, it
exhaustively listed ambient maximal cliques and all `2^12` vertex subsets.
The minimum beta of the induced graph `W union {a}` was 7, with histogram

```text
beta 7: 1404,  beta 8: 486,  beta 9: 138,
beta 10: 19,   beta 11: 1.
```

An admissible set in this induced graph remains admissible in any larger
`F`: an `F`-maximal clique contained in it would also be maximal in the
induced graph.  Thus the source lemma's weaker bound of six has ample room
and includes the isolated-vertex case.

## Shipped checker replay and coverage

The checker replayed in a fresh `-B` process and printed

```text
status: CHECKED
arithmetic_states: 1
forced_state: e(U)=7, cut_sizes=(17,17,17,17,17)
maximum_independent_transversals: 48
independent_sets_in_U: 324
independent_sets_hitting_all_transversals: 0
```

Its finite statements are correct.  The 324 independent sets include the
empty set, so the abstract `L_a` test includes an isolated `a`; checking all
independent `L_a`, even ones not realizable by a fan, is conservative.

The checker intentionally does not verify the row-R profile, the
ambient-maximality directions, domination, the singleton-fibre lemma, the
derivation of the 17-edge cut, `alpha(U)<=5`, Turán's theorem, or equality
rigidity.  It assumes the cut and Turán conclusions before checking the
arithmetic/transversal residue.  It also has no source-hash binding or
checked-output JSON.  These are coverage limitations, not blockers, because
the note describes the script only as an isolated sanity check and the
omitted implications have been independently proved and tested above.

## Final verdict and blockers

**PASS.**  No logical, computational, provenance, or claim-boundary blocker
was found for the analytic exclusion of row R under its standing
hypotheses.  The exact blocker list is empty.
