# Root audit of the asymptotic bridge and the finite CEGAR lane

Date: 2026-08-03

This note separates verified consequences from hypotheses and from invalid
certificate routes.  It does not claim a solution of Erdos problem #151.

## Primary-source checks

1. Joret--Micek--Reed--Smid, *Tight Bounds on the Clique Chromatic
   Number*, Theorem 1, states that for every epsilon > 0 and all sufficiently
   large maximum degree Delta,

       chi_c(G) <= (1 + epsilon) Delta / log Delta.

   A clique-colour class contains no nontrivial maximal clique, hence is an
   admissible set in the terminology of #151.  Therefore

       beta(G) >= |V(G)| / chi_c(G).

   The claimed Theta(sqrt(n log n)) lower bound for beta follows after using
   the paper's n-vertex corollary.  This asymptotic bridge is valid.

2. The current preprint *Improving R(3,k) in just two bites*
   (arXiv:2510.19718) states

       R(3,k) >= (1/2 + o(1)) k^2 / log k.

   The April 2026 revision of Radziszowski's *Small Ramsey Numbers* lists
   47 <= R(3,11) <= 50.  Thus H(50) >= 11 is presently certified by a
   published upper bound, independently of the unresolved exact value.

3. If a least counterexample at parameter h has Delta <= h-1, the JMRS
   estimate with constant C gives

       beta >= n log(h-1) / (C(h-1)).

   Combining beta <= h-1 with a Ramsey lower bound
   R(3,h) >= (c_R-o(1))h^2/log h yields the sufficient asymptotic condition
   C < c_R.  With the currently claimed c_R = 1/2 and the general JMRS
   constant C = 1, this is a genuine factor-two gap.  Improving C below 1/2
   only on the structural counterexample class would settle all sufficiently
   large h, but that improvement is not proved here.

Primary sources:

- https://arxiv.org/abs/2006.11353
- https://www.combinatorics.org/ojs/index.php/eljc/article/download/v28i3p51/pdf/
- https://arxiv.org/abs/2510.19718
- https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1

## CEGAR audit

### `cegar_face.py`

The semantic encoding is sound for the K4-free face:

- the oracle's forbidden objects are exactly triangles and graph edges with
  no common neighbour, i.e. the nontrivial maximal cliques in a K4-free
  graph;
- every lazy cut can be satisfied only by an actual such obstruction inside
  the selected h-set;
- after the randomized searches fail, the deterministic recursion is a
  complete existence check for an admissible h-set.

Consequently an independently checked SAT candidate at (50,11) would be a
full counterexample to #151.  An UNSAT result would exclude only the K4-free
face at that order.  The current implementation does not export a final CNF
and proof trace, so a solver return of UNSAT is not yet a certificate: the
final incremental formula must be serialized and independently proof-checked.

### `cegar_face2.py`

Its additional purported consecutive-row lex symmetry breaker is unsound.
The auxiliary variable tracks a prefix of strict coordinatewise `(1,0)`
comparisons, not equality of the preceding coordinates.  More decisively,
exhaustion over all relabellings shows that the four-vertex graph `2K2` is
excluded by these clauses under every labelling.  Reproducer:

    python .research-cache/audit_cegar_face2_sym.py

Therefore:

- an UNSAT result from `cegar_face2.py` has no mathematical meaning;
- the symmetry clauses must be removed, or replaced by a separately proved
  isomorph-free scheme;
- a SAT graph from that run can still be useful, but only after a checker
  ignores the symmetry clauses and verifies K4-freeness, the degree bounds,
  and beta <= 10 directly from the edge list.

The original `cegar_face.py` run remains authoritative.  At the time of this
audit neither n=50 log had reached a terminal status.

The faulty block was removed locally from `cegar_face2.py`.  The repaired
variant reproduces the two controls: `(n,h)=(10,4)` is UNSAT and `(10,5)`
returns a SAT candidate.  These smoke tests check regression behaviour, not
the production instance or an UNSAT-certificate path.

## Strategic decision after the first production stretch

At approximately 15,600 rounds, `cegar_face_n50.log` was still live and was
adding 24 lazy cuts per round.  This is evidence that the process is healthy,
not evidence that it is close to SAT or UNSAT.  CEGAR round counts are not a
sound stopping-time estimator.

The primary `cegar_face.py` run should continue because it is
resolution-capable in one direction: a SAT graph, after independent checks of
K4-freeness, the exact ambient `beta`, and edge-arrowing, would refute #151.
An UNSAT result would exclude only the K4-free face at `n=50`, and is
publishable only after the final CNF and a checkable proof trace are exported.

The already-running old `cegar_face2.py` process may be retained only as a
heuristic SAT hunt.  Its symmetry clauses can remove valid isomorphism
classes, so no negative conclusion can be drawn from it.  Any graph it emits
must be checked from its edge list without those clauses.

The asymptotic work changes the search distribution rather than ending the
problem.  Generic random/process/circulant/MSV-shaped sampling is now strongly
deprioritized.  The live construction targets are crowded quasi-designs and
the protected-core interface; the live proof target is a clique-colouring
improvement on that structural class.  The campaign will reassess #151 on
mathematical progress (candidate margin, a new structural inequality, or a
certified finite exclusion), not on an LLM estimate of human research time.

## Unconditional degree band at the n=50 K4-free face

Assume the audited order-41 K4-free result: every K4-free graph on 41
vertices has `beta >= 10`. Then every K4-free graph `G` on 50 vertices with
`beta(G) <= 10` satisfies

    beta(G) = 10 and 9 <= delta(G) <= Delta(G) <= 10.

The upper degree bound is the elementary open-neighbourhood bound
`beta >= Delta`. For the other assertions, admissibility is monotone under
induced deletion in the needed direction: every admissible set in an induced
subgraph is admissible in the ambient graph, because an ambient maximal
clique contained in the induced subgraph is maximal there as well. Thus any
induced 41-vertex subgraph has beta between 10 and `beta(G)`, proving
`beta(G)=10`.

If a vertex `v` had degree at most eight, its non-neighbourhood would contain
an induced 41-vertex subgraph and hence an ambient-admissible 10-set `S`.
The vertex `v` is anticomplete to `S`, so `S union {v}` is also
ambient-admissible, contradicting `beta(G) <= 10`. Therefore `delta(G)>=9`.

This is an unconditional constraint on every graph sought by the `(50,11)`
CEGAR instance. It justifies a fresh sound run with both degree bounds; it
does not retroactively change the formula in an already-running process.
