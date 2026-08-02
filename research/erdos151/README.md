# Erdős problem 151: structural reduction and the first live order

**Public status (2 August 2026):** the full Erdős--Gallai--Tuza conjecture
remains open.  This package proves the conjectured inequality for all graphs
on at most 17 vertices and reduces the first possible counterexample to a
strongly constrained graph on 18 vertices.  It does **not** claim a solution
of problem 151.

For a graph `G`, let `tau(G)` be the minimum number of vertices meeting every
inclusion-maximal clique of size at least two.  Let `H(n)` be the minimum
independence number among triangle-free graphs on `n` vertices.  The open
question is

```text
tau(G) <= n - H(n).
```

Define `beta(G)` to be the largest size of a vertex set containing no
nontrivial maximal clique of `G`.  Then `tau(G) = n - beta(G)`.  The key
recurrence found in this campaign is

```text
beta(G) >= |I| + beta(G - N[I])
```

for every independent set `I`.  The maximality direction is important: if a
clique contained in the residual is maximal in `G`, then it is maximal in the
residual; the converse is neither used nor generally true.

Together with `beta(G) >= Delta(G)` and the exact small Ramsey numbers, this
gives a short proof that `beta(G) >= H(n)` for every `n <= 17`.  A smallest
counterexample with `h=H(n)` can exist only when

```text
R(3,h) <= n <= R(3,h-1) + h - 1.
```

The first surviving order is `n=18`.  Any counterexample there must be
connected, have all degrees in `{4,5}`, have clique number at most four, and
satisfy the independent-set closed-neighborhood constraints recorded in
[`proof.md`](proof.md).

## Evidence and audit

- [`proof.md`](proof.md) gives the complete human-readable argument and the
  order-18 consequences.
- [`audit.md`](audit.md) records the independent maximality, induction, Ramsey,
  and computation checks.
- [`result.json`](result.json) records the exact claim, dependency thresholds,
  and the disposition of the superseded order-14 computation.
- A second agent independently checked every use of inclusion-maximality, the
  base cases, the induction, and the Ramsey thresholds before publication.
- As a computational sanity check, two separate implementations exhaustively
  processed all 274,668 unlabeled graphs on nine vertices and found maximum
  `tau=5` and no counterexample.  The analytic proof supersedes this census.

The earlier order-14 SAT hunt was stopped after the structural proof was
verified.  Four proof-free runs produced no candidate and no solver
conclusion; they are recorded as `STOPPED_AFTER_STRUCTURAL_PROOF`, never as
`UNSAT`.  All local artifacts were preserved and nothing was deleted.

## Novelty boundary

The live [Erdős Problems entry](https://www.erdosproblems.com/151) still marks
the full question open.  Targeted searches found no public statement of this
finite-order result or recurrence, but the campaign has not yet completed a
page-by-page comparison with every older clique-transversal paper.  This is a
timestamped, independently derived research note offered for expert review,
not an assertion that every lemma is new to the literature.

AI systems performed the discovery, audit, computation, documentation, and
publication preparation under Edison Yi's direction.  Independent-agent
agreement is a bug-finding measure, not peer review.

## References

- [Erdős problem 151](https://www.erdosproblems.com/151)
- P. Erdős, T. Gallai, and Zs. Tuza,
  [*Covering the cliques of a graph with vertices*](https://doi.org/10.1016/0012-365X(92)90681-5),
  Discrete Mathematics 108 (1992), 279--289.
- S. Radziszowski,
  [*Small Ramsey Numbers*](https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1),
  Dynamic Survey 1, Electronic Journal of Combinatorics.
