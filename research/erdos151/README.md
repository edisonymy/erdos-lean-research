# Erdős problem 151: verified through order 39

**Public status (2 August 2026):** the full Erdős--Gallai--Tuza conjecture
remains open.  This package proves the conjectured inequality for every graph
on at most 39 vertices.  Earlier files establish the bound through order 27.
The independently audited proof in [`order28_36.md`](order28_36.md) excludes
the next two exact Ramsey jumps, orders 28 and 36; induced-subgraph
monotonicity propagates those exclusions through the intervening plateaus.
It does **not** claim a solution of problem 151.  Since the current published
bounds are `40<=R(3,10)<=41`, the next possible least-counterexample order is
40 or 41.

The independently audited
[`K4`-free order-41 theorem](general/k4free_h10/K4FREE_ORDER41.md) additionally
proves `beta(G)>=10` for every `K4`-free graph on 41 vertices, without assuming
an exact value of `R(3,10)` or clearing order 40 first.  This removes
`omega(G)<=3` from the order-41 frontier.  The independently audited
[`omega=5` theorem](general/ORDER41_K5_EXCLUSION.md) additionally proves
`beta(G)>=10` for every order-41 graph with clique number five, conditional
only on completeness of the published seven-record Ramsey `(3,6;17)`
catalogue.  The local bytes and properties are checked; external catalogue
completeness is not proved here.  Its analytic profile exclusions leave only
`omega(G)=4` at order 41 under that premise.  The separately audited
[`K4`-free order-40 theorem](general/k4free_h10/order40/ORDER40_RESIDUAL.md)
proves `beta(G)>=10` there if `R(3,10)=40`; if `R(3,10)=41`, the required
order-40 bound is nine and follows from the through-order-39 theorem.  Hence
the `K4`-free order-40/41 lane is closed for #151.  If `R(3,10)=40`, the
unrestricted order-40 clique-number-four and clique-number-five cases also
remain.  The full problem and all later Ramsey jumps remain open.

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

The first initially surviving order is `n=18`.  The detailed argument in
[`proof.md`](proof.md) excludes it: mixed degree-4/5 sequences contradict a
local link count, while a 5-regular candidate yields a triangle-free auxiliary
graph whose Ramsey independent six-set avoids every maximal clique.  The
minimal-counterexample interval and parity then exclude orders 19--22.

The separate [`order23.md`](order23.md) argument excludes the only remaining
order below 24.  If a candidate graph were edge-Ramsey for triangles, a
Ramsey-minimal subgraph, exact link counts, Brooks' theorem, and Gallai's
low-vertex theorem would force an impossible 6-critical graph.  If it were
not edge-Ramsey, a two-edge-coloring directly produces the required avoiding
seven-set.

The [`order24.md`](order24.md) argument proves `beta(G)>=7` for every
24-vertex graph.  A putative counterexample is forced to be 6-regular.  Local
two-walk counts show that every vertex lies in at most three triangles; a new
edge-coloring lemma then partitions its edges into two triangle-free classes.
This produces a triangle-free auxiliary graph whose Ramsey independent
seven-set is avoiding.  Strong induction with the recurrence gives
`beta(G)>=7` for every order `n>=24`.  Together the two arguments give
`beta(G)>=7` for every order `n>=23`; since `R(3,8)=28`, this proves the
conjectured bound through order 27.  It does not settle any later Ramsey
interval.

Three structural theorems first sharpened the order-28 attack.  The
[`induced-subgraph monotonicity lemma`](general/INDUCED_MONOTONICITY.md)
reduces every Ramsey plateau to its first order.  The
[`top-window Ramsey-core inequality`](general/TOP_WINDOW_RAMSEY_CORE.md)
shows that an order-30 least counterexample would contain an edge-minimal
`(3,3)`-arrowing core whose degrees are simultaneously at most four and at
least five, a contradiction.  The independently audited
[`clique-residual lemma`](general/CLIQUE_RESIDUAL.md) proves that every least
counterexample at orders 28--30 is `K5`-free, strengthening the working bound
to `omega(G)<=4`.  These ingredients, the Folkman reduction, two elementary
coloring lemmas, and a small exact link check now exclude orders 28 and 36 in
[`order28_36.md`](order28_36.md).  The top-window theorem remains a valid
independent structural result.

## Evidence and audit

- [`proof.md`](proof.md) gives the complete human-readable argument through
  order 22.
- [`order23.md`](order23.md) gives the independently audited order-23 proof.
- [`order24.md`](order24.md) gives the independently audited order-24 proof
  and its `beta>=7` propagation corollary.
- [`order28_36.md`](order28_36.md) gives the independently reconstructed
  analytic exclusions of the Ramsey jumps at 28 and 36 and the resulting
  theorem through order 39.
- [`order40_41_frontier.md`](order40_41_frontier.md) records the current
  audited saturation, Ramsey-core, fixed-clique CEGAR, and fractional
  aggregation attacks at the next jump, including the audited unconditional
  `K4`-free order-41 theorem and the exact computation boundaries.  It does
  not claim the full order-40/41 frontier is settled.
- [`general/k4free_h10/K4FREE_ORDER41.md`](general/k4free_h10/K4FREE_ORDER41.md)
  proves `beta(G)>=10` for every `K4`-free graph of order 41; its independent
  quantifier, citation, and arithmetic audit is in
  [`INDEPENDENT_AUDIT.md`](general/k4free_h10/INDEPENDENT_AUDIT.md).
- [`general/ORDER41_K5_EXCLUSION.md`](general/ORDER41_K5_EXCLUSION.md)
  gives the independently audited conditional theorem for clique number five.
  Its sole external premise is completeness of the pinned seven-record Ramsey
  `(3,6;17)` catalogue; the row proofs, finite guards, failed first overlap
  audit, repair, and post-repair audits are retained beside it.
- [`ALLOCATION_CHECKPOINT.md`](ALLOCATION_CHECKPOINT.md) records the explicit
  evidence-based rule for continuing or reducing the #151 siege after the
  first genuinely global `omega=4` run.
- [`audit_order28_36.md`](audit_order28_36.md) records three adversarial proof
  passes, the exact dependency boundary, and two exhaustive finite checks.
- [`general/TOP_WINDOW_RAMSEY_CORE.md`](general/TOP_WINDOW_RAMSEY_CORE.md)
  gives the twice-audited top-window core inequality that first reduced
  orders 28--30 to orders 28--29.
- [`general/INDUCED_MONOTONICITY.md`](general/INDUCED_MONOTONICITY.md) gives
  the twice-audited reduction from an entire Ramsey plateau to its jump order;
  it then reduced that plateau to order 28, which `order28_36.md` now excludes.
- [`general/CLIQUE_RESIDUAL.md`](general/CLIQUE_RESIDUAL.md) gives the
  twice-audited `omega<=4` reduction for the first open interval.
- [`audit.md`](audit.md) records the independent maximality, induction, Ramsey,
  and computation checks.
- [`literature.md`](literature.md) records the current priority search and the
  exact boundary between known parameter prior art and the present proof method.
- [`result.json`](result.json) records the exact through-order-39 claim,
  dependency thresholds, hashes, and the disposition of superseded searches.
- [`lean/Erdos151Recurrence.lean`](lean/Erdos151Recurrence.lean) is a
  sorry-free Lean 4/mathlib verification of the independent-set recurrence
  alone.  It does not formalize the Ramsey inputs, the order-18 argument, or
  the through-order-22 theorem; see its [scope note](lean/README.md).
- A second agent independently checked every use of inclusion-maximality, the
  base cases, the induction, and the Ramsey thresholds before publication.
- A fresh Sol/max agent adversarially reconstructed the order-24 argument;
  it also exhaustively checked all labeled graphs on seven vertices against
  the proof's triangle-edge-coloring lemma.
- A different Sol/max agent independently reconstructed every step of the
  order-23 proof, including both coloring extensions and the Gallai-forest
  block count, before publication.
- Three independent adversarial passes reconstructed the new order-28/36
  proof.  The two finite coloring inputs were also exhaustively checked by
  separate programs using only the Python standard library.
- [`checks/marked_neighborhood6.py`](checks/marked_neighborhood6.py) is a
  small optional exhaustive sanity check for the six-vertex link lemma.  The
  analytic proof does not depend on it.
- As a computational sanity check, two separate implementations exhaustively
  processed all 274,668 unlabeled graphs on nine vertices and found maximum
  `tau=5` and no counterexample.  The analytic proof supersedes this census.

The earlier order-14 SAT hunt was stopped after the first structural proof was
verified.  A later order-18 q=0/2/4 portfolio was likewise stopped when the
analytic order-18 contradiction passed a fresh Sol/max audit.  These
proof-free runs produced no solver conclusion; they are recorded as
`STOPPED_AFTER_STRUCTURAL_PROOF`, never as `UNSAT`.  All local artifacts were
preserved and nothing was deleted.

A candidate-first SAT encoding was designed privately for orders 23 and 24,
but the analytic proofs arrived before any DIMACS instance was materialized
or any solver was launched.  The design therefore produced no candidate,
SAT/UNSAT status, certificate, or computational claim.

## Novelty boundary

The live [Erdős Problems entry](https://www.erdosproblems.com/151) still marks
the full question open.  Bhat, Bhat, and Bhat (2023) already define the same
`beta` parameter (under the name clique-free number) and prove its duality
with the clique-transversal number; McDiarmid, Mitsche, and Prałat (2019) use
the equivalent maximal-clique-free parameter in random graphs.  Targeted
searches have not found the independent-set recurrence,
minimal-counterexample interval, or through-27 result, but the older-literature
comparison is not exhaustive.  This is a timestamped, independently derived
research note offered for expert review, not an assertion that every lemma is
new to the literature.

AI systems performed the discovery, audit, computation, documentation, and
publication preparation under Edison Yi's direction.  Independent-agent
agreement is a bug-finding measure, not peer review.

## References

- [Erdős problem 151](https://www.erdosproblems.com/151)
- P. Erdős,
  [*Problems and results in combinatorial analysis and graph theory*](https://doi.org/10.1016/0012-365X(88)90196-3),
  Discrete Mathematics 72 (1988), 81--92, p. 82.
- P. Erdős, T. Gallai, and Zs. Tuza,
  [*Covering the cliques of a graph with vertices*](https://doi.org/10.1016/0012-365X(92)90681-5),
  Discrete Mathematics 108 (1992), 279--289.
- S. Radziszowski,
  [*Small Ramsey Numbers*](https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1),
  Dynamic Survey 1, Electronic Journal of Combinatorics.
- B. D. McKay and Zhang Ke Min,
  [*The value of the Ramsey number R(3,8)*](https://doi.org/10.1002/jgt.3190160111),
  Journal of Graph Theory 16 (1992), 99--105.
- R. L. Brooks,
  [*On colouring the nodes of a network*](https://doi.org/10.1017/S030500410002168X),
  Proceedings of the Cambridge Philosophical Society 37 (1941), 194--197.
- T. Gallai,
  [*Kritische Graphen, I*](https://real.mtak.hu/201435/),
  A Magyar Tudományos Akadémia Matematikai Kutató Intézetének Közleményei
  8(1--2) (1963), 165--192.
- S. R. Bhat, R. Bhat, and S. G. Bhat,
  [*Clique Free Number of a Graph*](https://www.engineeringletters.com/issues_v31/issue_4/EL_31_4_55.pdf),
  Engineering Letters 31(4) (2023), 1832--1836.
- C. McDiarmid, D. Mitsche, and P. Prałat,
  [*Clique coloring of binomial random graphs*](https://arxiv.org/abs/1611.01782),
  Random Structures & Algorithms 54(4) (2019), 589--614.
