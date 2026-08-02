# Independent audit of the order-28 and order-36 exclusions

**Audit status (2 August 2026): VERIFIED.**  This audit supports the bounded
claim that the Erdos #151 inequality holds for graphs of order at most 39.
It does not support a claim that the full conjecture is solved or that the
argument is new to the literature.

## Independent proof passes

The proof in [`order28_36.md`](order28_36.md) was reconstructed independently
in three adversarial passes after the discovery draft was written.

1. One pass checked the order-28 argument from the definitions: the
   least-counterexample reductions, the two boundary inequalities, the set
   overlap classification, and all four types of triangle in the final
   coloring.  It returned `VERIFIED` with no workspace edits.
2. A fresh pass independently derived both the order-28 and order-36
   contradictions and then wrote the separate degree-seven core checker.  It
   returned `VERIFIED`.
3. A final pass concentrated on the order-36 dependency chain.  It checked
   the direct common-neighbor count, the two-sided regular swap, the capacity
   bound, the use of Bikov's theorem, the boundary disjointness, and the
   propagation to order 39.  It returned `VERIFIED` with no workspace edits.

The primary campaign agent then reconstructed the complete proof again,
including the exact maximal-clique direction in every induced lift.  Agent
agreement is a bug-finding measure, not peer review.

## Finite checks

Two standard-library Python programs check the only finite coloring inputs.

- [`check_order28_36_coloring.py`](check_order28_36_coloring.py) exhausts all
  555 good red/blue colored links on at most four vertices relevant to the
  cone lemma, and all 25 matching prescriptions on the edges of `K4`.  It
  finds no obstruction.
- [`checks/check_k4free_core_degree7.py`](checks/check_k4free_core_degree7.py)
  exhausts all 2,097,152 labelled graph masks on seven vertices, identifies
  the 1,743 maximal triangle-free graphs, and checks all 1,348,032 edge
  signings against all 128 spoke assignments.  It finds no obstruction.

The second check gives a finite, citation-independent verification of the
special case needed in the proof: a `K4`-free edge-minimal `(3,3)`-Ramsey
core cannot have maximum degree at most seven.  Checking maximal
triangle-free seven-vertex links is sufficient because every triangle-free
link on at most seven vertices can be padded and extended to one of them,
and any successful spoke assignment restricts to the original link.

Recorded machine-readable outputs are
[`check_order28_36_coloring.result.json`](check_order28_36_coloring.result.json)
and
[`checks/check_k4free_core_degree7.result.json`](checks/check_k4free_core_degree7.result.json).

## Dependency and scope audit

The proof uses the previously audited definitions and results in this
directory, including:

- `beta(G)` is the maximum size of a set containing no nontrivial
  inclusion-maximal clique of the ambient graph;
- the theorem through order 27 and the universal bound `beta(G)>=7` from
  order 23 onward;
- induced-subgraph monotonicity of `beta`;
- the least-counterexample degree floor and ceiling;
- the Folkman reduction from a counterexample to `G -> (3,3)`;
- the clique-residual exclusion `omega(G)<=4` at orders 28 and 36;
- the exact values `R(3,5)=14`, `R(3,6)=18`, `R(3,8)=28`, and
  `R(3,9)=36`, plus the published lower bound `R(3,10)>=40`.

Bikov's published minimum-degree theorem for `K4`-free minimal
`(3,3)`-Ramsey graphs is cited in the human proof, but the independent exact
checker above verifies the entire bounded specialization used here.  The
current published upper bound `R(3,10)<=41` identifies the next jump as 40
or 41; only the lower bound 40 is needed for propagation through order 39.

The resulting claim is exactly:

> Every graph `G` on `n<=39` vertices satisfies
> `tau(G) <= n-H(n)`.

Orders 40 and 41 are not settled, and the universal Erdős--Gallai--Tuza
conjecture remains open.
