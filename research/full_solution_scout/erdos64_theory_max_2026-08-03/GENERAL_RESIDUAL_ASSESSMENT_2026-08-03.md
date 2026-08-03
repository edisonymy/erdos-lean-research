# Adversarial assessment: induced-boundary closure versus the equality window

Date: 2026-08-03

Status: **SCOPE AUDIT COMPLETE**.

## Verdict

The all-three-seed induced-boundary closure does **not**, by itself or by
combination with the finite equality window, imply a general residual theorem.
There is no sound reduction from every incidence-kernel equality graph to the
computed seed family.  The three-seed result remains valuable as a model for
finite boundary signatures, but its quantified graph class and its forbidden
objects differ from the equality problem in several essential ways.

The new `a=10` residual exclusion in
`POSTPUBLICATION_PLUS7_A10_GATE_2026-08-03.md` does give a genuine structural
jump.  It is derived directly from the equality-kernel topology and uses none
of the seed closure as a premise.

## Exact scope comparison

| Feature | Three-seed induced-boundary closure | Slack-six equality residual |
|---|---|---|
| Ambient object | one marked cubic graph of order 28, plus two marked-isomorphic copies | a minimum counterexample with `a` vertices of degree at least four |
| Actual seed diversity | one marked-isomorphism class | all eligible incidence kernels and all residual realizations |
| Modified region | one fixed 12-vertex witness union plus immediate boundary | all of `R=G[D]`, with no preselected witness basin |
| Boundary condition | every outside and crossing edge fixed to the seed | fixed `A-D` incidence skeleton, but arbitrary residual topology |
| Degree condition | cubic degree restoration inside the chosen set | `D2,D1,D0` residual degrees `1,2,3` |
| Forbidden internal objects | `C4,C8,C16` | all dyadic cycles present at the relevant order |
| Additional forbidden objects | marked paths of lengths `2,6,14` | none; open paths are not forbidden in `G` |
| Exhaustiveness | exact only inside that fixed-boundary rewire family | must cover every equality graph in the finite window |

## Why the transfer fails

### 1. The orders and degree categories do not match

Equality has

```text
n=3a+6 in {15,18,21,24,27,30,33,36}
```

before the new `a=10` exclusion.  For `a>=3` these graphs are not cubic: they
contain the nonempty independent high-degree set `A`.  The computed object is
a marked cubic graph of order 28.  No contraction, splitting, or bridge-block
operation has been proved to send every equality graph to that object while
preserving the relevant cycle prohibition.

### 2. “All three seeds” is not a census

The three frontier states are explicitly marked-isomorphic.  The transfer
certificate says that the state-0 fixed-boundary computation applies
bijectively to states 1 and 2; it does not say that every order-28 cubic graph,
every near miss, or every equality kernel belongs to that class.  The source
reports themselves explicitly disclaim an order-28 census.

### 3. The boundary is frozen in a way equality does not force

The induced rewire holds every edge outside the 12-vertex set, and every edge
crossing its boundary, fixed.  An equality residual can change its endpoint
pairing and colored words globally across `R`.  Nothing in the incidence
arithmetic selects the seed's two `C4` witnesses, its four immediate-boundary
vertices, or its exact crossing-edge pattern.

### 4. Marked-path pruning is not sound for equality graphs

The seed search rejects marked paths of lengths `2,6,14` because they close to
dyadic cycles only after the contemplated bridge-block construction.  An open
path of one of those lengths is legal in a minimum counterexample unless a
separate return path is proved.  The fixed-boundary certificate aggregates
cycle and marked-path prunes; it therefore cannot be reinterpreted as a
cycle-only obstruction for equality residuals.

## The missing reduction theorem

To use the seed closure in a proof, one would need a theorem of roughly the
following form:

> Every slack-six equality graph contains an induced 12-vertex set whose
> residual degree vector, fixed crossing edges, marked edge, witness family,
> and terminal-path semantics are isomorphic to the computed seed boundary.

None of the proved incidence, low-cut, bridge, or modular-cycle results gives
this.  Several demanded conclusions (cubic ambient degree, order 28, two
specific `C4` witnesses) are incompatible with the literal equality setup.
Thus this is not merely an unfilled technical step; it is the wrong target
reduction.

## What does transfer: the method, not the certificate

The reusable idea is to quotient a residual graph by a finite boundary
signature and enumerate exact degree realizations with monotone necessary
cycle constraints.  Applied to the actual equality decomposition, this gives:

1. a kernel `J` and its subdivided fixed incidence skeleton;
2. a topology quotient of `R` into colored paths/cycles (and, in the `q=5`
   branch, one trivalent component);
3. exact terminal types given by kernel-edge labels and `D1` colors; and
4. the one-segment closure rule: an `R` segment plus a fixed-skeleton path may
   not have dyadic total length.

That directly relevant signature system is what excludes `a=10`.  It is also
the correct candidate for the remaining `a=3,...,9` window.  The order-28 seed
closure is supporting design evidence only and should not be cited as a premise
of any equality theorem.

## Final audit label

```text
Seed closure + finite window: no valid general inference.
Direct equality boundary signatures: valid and already yield the a=10 gate.
```
