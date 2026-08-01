# Order-16 native pseudo-Boolean search

Status as of 2026-08-01: both exact decision procedures returned UNSAT in all
three exhaustive cases.  This is a doubly checked, conditional computational
exclusion at order 16, **not** a proof-certificate-backed theorem.

`z3_cross_search.py` is a materially independent encoding of the remaining
order-16 case.  Unlike `cnf_search.py`, it has only the 120 graph-edge
variables at source level and gives the cardinality constraints to Z3 as
native pseudo-Boolean formulas.  It does not reuse PySAT's sequential-counter
encoding.

## Exhaustive reduction

The reduction depends on the McKay `(3,6,16)` catalogue exclusion documented
in `RESULTS.md`.

1. Razborov's theorem shows that a counterexample at order 16 has
   `alpha(G) <= 6`.  The complete catalogue check excludes `alpha(G) <= 5`,
   so a remaining counterexample has an independent six-set `I`.
2. Adding an edge whenever this preserves triangle-freeness cannot destroy
   the counterexample property: every induced edge count only increases.
   Extend to a maximal triangle-free counterexample.  Its independence number
   cannot fall below 6, because that would be a catalogue-excluded
   counterexample.  Thus it still has an independent six-set, relabelled
   `I={0,...,5}`.
3. Every vertex outside `I` has a neighbour in `I`, or it extends `I` to an
   independent seven-set.  Pick an outside vertex of minimum cross-degree
   `d`, label it 6, and relabel `I` so its neighbourhood is `{0,...,d-1}`.
4. We have `1 <= d <= 3`.  If `d >= 4`, every two outside vertices have
   intersecting neighbourhoods in the six-set `I`; triangle-freeness then
   makes all ten outside vertices pairwise nonadjacent, contradicting
   `alpha(G) <= 6`.
5. After vertex 6 and `I` are fixed, the other nine outside vertices remain
   freely permutable.  Sorting their six-bit `I`-neighbourhood codes is a
   lossless symmetry break.

The three commands below are therefore exhaustive, conditional on the
catalogue completeness used in step 1:

```powershell
python experiments/erdos128/z3_cross_search.py 1 --model .tmp/erdos128_z3_d1.json
python experiments/erdos128/z3_cross_search.py 2 --model .tmp/erdos128_z3_d2.json
python experiments/erdos128/z3_cross_search.py 3 --model .tmp/erdos128_z3_d3.json
```

Exit code 10 means SAT, 20 means UNSAT, and 0 means UNKNOWN.  Any SAT output
must be checked separately:

```powershell
python experiments/erdos128/checker.py .tmp/erdos128_z3_d1.json
```

Z3 is an exact solver, so a SAT model can be independently checked.  An UNSAT
answer from this run is **not** a theorem-level certificate: the present
script does not retain a checkable Z3 proof, and the catalogue completeness
is external.  The DRAT/LRAT contingency in `PROOF_PIPELINE.md` remains the
route to a certificate-backed finite exclusion.

## Independent MiniCard cross-check

`minicard_cross_search.py` reconstructs the same three mathematical cases
without importing or calling the Z3 encoder.  It uses PySAT's `CNFPlus`
container and MiniCard's native at-most constraints.  It also deliberately
omits the Z3 sort on the last nine outside vertices, so the two searches do
not share that symmetry assumption.  It can be run with the same three case
arguments.  This is a valuable independent solver/encoding cross-check, but
MiniCard likewise does not emit a retained UNSAT certificate.

## Retained results

| case | Z3 QF_FD | Z3 solve s | MiniCard, no cross sort | MiniCard solve s |
|---:|---|---:|---|---:|
| `d=1` | UNSAT | 64.781 | UNSAT | 0.047 |
| `d=2` | UNSAT | 76.110 | UNSAT | 0.109 |
| `d=3` | UNSAT | 91.813 | UNSAT | 823.094 |

The exact JSON-lines outputs, including solver statistics, are in
`cross_results/`.  `cross_results/SHA256SUMS` locks the two sources, the audit
source, and all seven result artifacts.  The run used Python 3.12.4,
`z3-solver==5.0.0.0`, and `python-sat==1.9.dev7` on Windows.  Install the
pinned packages with:

```powershell
python -m pip install -r experiments/erdos128/requirements-search.txt
```

The exact commands used were:

```powershell
python experiments/erdos128/z3_cross_search.py 1 --model .tmp/erdos128_z3_d1.json
python experiments/erdos128/z3_cross_search.py 2 --model .tmp/erdos128_z3_d2.json
python experiments/erdos128/z3_cross_search.py 3 --model .tmp/erdos128_z3_d3.json
python experiments/erdos128/minicard_cross_search.py 1 --model .tmp/erdos128_minicard_d1.json
python experiments/erdos128/minicard_cross_search.py 2 --model .tmp/erdos128_minicard_d2.json
python experiments/erdos128/minicard_cross_search.py 3 --model .tmp/erdos128_minicard_d3.json
python experiments/erdos128/audit_cross_reduction.py
```

No model file was written because every solver call returned UNSAT.

## Independent reduction and encoding audit

`audit_cross_reduction.py` passed all of the following checks; the full output
is retained as `cross_results/audit.json`.

- It evaluated Z3 `PbGe` and MiniCard's negated-literal `AtMost` form on every
  assignment of one through six variables at every bound: 1,536 comparisons.
- It exhaustively compared the MiniCard common-neighbour witness CNF with the
  direct maximality predicate on every graph of orders 2 through 5: 1,098
  graphs.
- It enumerated all 33,868 labelled graphs through order 6.  For all 6,229
  triangle-free graphs, deterministic maximal extension preserved
  triangle-freeness, increased every induced subset edge count, and did not
  increase independence number.  It normalized all 15,226 maximum
  independent sets and checked the prefix and cross-code symmetries after an
  explicit isomorphic relabelling.
- It repeated the normalization for all 30 maximum independent sets in the
  three complete Ramsey `(3,4,8)` graphs.  These are a small exact analogue of
  the `|O| > alpha` situation: every normalized minimum cross-degree was 1,
  as the general `d <= floor(alpha/2)` argument requires.
- A deterministic order-16 maximal triangle-free fixture (seed 0, 44 edges,
  exact independence number 6) was explicitly lifted into the Z3 normal form:
  `d=1`, sorted cross codes
  `[6,14,25,38,49,56,62,62,63]`.  Its minimum half count is 2, so this fixture
  tests model lifting without pretending to be a counterexample.

These tests are designed to catch a false symmetry break or a reversed native
cardinality constraint.  They do not certify the order-16 UNSAT answers.

## Public-status audit through 2026-08-01

The live check was performed before this search:

- The [problem page](https://www.erdosproblems.com/128) still marks #128 open.
  Its discussion page reported six comments and zero claimed proofs.  The
  newest comment, by Cormundus on 2026-07-26, reports a computational search
  with no counterexample.
- The linked public repository
  [`cormundus/erdos-128-census`](https://github.com/cormundus/erdos-128-census),
  commit `52e43ab4a6e9bc9a56951e113c823b340d706fe6`, exactly checks named
  triangle-free strongly regular graphs and reports heuristic raw-graph
  searches for even orders through 26.  It makes no exact order-16 exclusion.
- McKay's current [Ramsey catalogue](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html)
  still lists exactly 2,576 Ramsey `(3,6,16)` graphs; this is the external
  completeness input used here.
- Searches of current public GitHub repositories, arXiv, Zenodo, the Erdős
  forum, and the public AI-contributions index found no prior exact order-16
  closure or full proof claim.  Search non-discovery is not evidence of
  novelty, so none is claimed.

The problem may have private or unindexed work.  This audit only establishes
what was publicly discoverable on the stated date.
