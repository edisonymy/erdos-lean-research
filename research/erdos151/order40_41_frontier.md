# Erdős #151: order-40/41 frontier

**Status: active investigation, 2 August 2026.  No full solution is claimed.**
The verified theorem through order 39 reduces the next possible least
counterexample to order 40 or 41.  This note records the exact state of the
three current order-40/41 attacks and their audit boundaries.

## Standing consequences

For a least counterexample `G` at the `h=10` jump:

- `beta(G)=9`, `Delta(G)<=9`, `alpha(G)<=9`, and `omega(G)<=5`;
- `delta(G)>=4` at order 40 and `delta(G)>=5` at order 41;
- `G` arrows `(3,3)` and therefore contains an edge-minimal Ramsey core.

The degree floors and clique ceiling use least-order minimality plus the
through-order-39 theorem.  A graph of order 41 with `beta<=9` is an
unconditional counterexample because `R(3,10)<=41`.  At order 40,
`beta<=9` is a counterexample only if `R(3,10)=40`; `beta<=8` would be
unconditional.

## Saturation and exchange

The corrected and independently reconstructed package is in
[`general/SATURATION_EXCHANGE.md`](general/SATURATION_EXCHANGE.md) and
[`general/SATURATION_AUDIT.md`](general/SATURATION_AUDIT.md).  Its strongest
current consequences are:

- exact-neighborhood fibers `P_A` are independent and satisfy
  `|P_A|<=|A|`;
- for every `Y` outside a maximum admissible set `S`,
  `beta(G[Y])<=|N_S(Y)|`, yielding Ramsey-sized Hall bounds by
  least-order minimality;
- choosing `S` to minimize its internal edge count gives
  `e(G[S])<=11` at order 40 and `<=10` at order 41;
- if `B_R` is the set of outside vertices whose every `S`-anchor meets
  `R⊆S`, then `alpha(G[B_R])<=|R|`;
- the remaining exact-two-neighbor, two-maximal-spoke class has size at
  most 28.

These restrictions do not yet contradict orders 40 or 41.  The stage-1 to
stage-3 SAT witnesses in `experiments/erdos151_siege/runs/` show only that
the explicitly encoded **local** axiom packages are feasible.  The
independent checker also exhibits an admissible 8-set in every witness, so
none enforces the global `beta<=7` condition.  They are not counterexamples
to problem 151.

An all-removal-set anchor-shadow probe at `h=8` tested the additional valid
constraints `alpha(G[B_R])<=|R|`.  Its first bounded run was stopped after
approximately one CPU-hour with no result file.  It has status
`STOPPED_NO_CONCLUSION`, not SAT or UNSAT; exact times, source hashes, and
empty-log hashes are preserved in `anchor_stage4.stopped.json`.

## Ramsey-core exclusions

The residual-clique certificate says that a core `Q` is impossible whenever
it contains a proper clique `P` with a fixed extender and enough degree
inside `Q` that at least `R(3,10-|P|)` outside vertices remain anticomplete
to `P`.  This analytically excludes all minimal `(3,3)`-Ramsey cores through
order 11, the named regular order-13 core, `K8-C5`, and every minimum-order
K5-free core.

The reproducible public-catalogue lane is documented in
[`../../experiments/erdos151_siege/core_catalog/RESULTS.md`](../../experiments/erdos151_siege/core_catalog/RESULTS.md).
It reconstructs and independently checks the public `alpha=2` slices:

- all 124 order-12 cores are excluded at both orders 40 and 41;
- all 13 order-13 cores are excluded at both orders 40 and 41;
- every exclusion has a deterministic extendable-`K4` certificate.

This is an exact result for the public slices only.  No public full graph6
catalogue was located for Bikov's 3,041 order-12 or 306,635 order-13 cores,
and order 14 is not fully classified.  The missing catalogues therefore
remain a real boundary, not silently treated as exhausted.

## Unconditional K4-free theorem at order 41

The independently audited theorem in
[`general/k4free_h10/K4FREE_ORDER41.md`](general/k4free_h10/K4FREE_ORDER41.md)
proves

```text
|V(G)|=41 and omega(G)<=3  ==>  beta(G)>=10.
```

It uses an edge-minimal `(3,3)`-Ramsey core, Bikov's classified degree-eight
links, an ambient unique-common-neighbor injection, and a Brooks-coloring
component count.  The result is unconditional on the unresolved value
`R(3,10) in {40,41}`.  Its separate adversarial audit and primary-source
check are in
[`general/k4free_h10/INDEPENDENT_AUDIT.md`](general/k4free_h10/INDEPENDENT_AUDIT.md).
The companion order-40 theorem below closes that residual case.

## Conditional strong K4-free theorem at order 40

The independently audited proof in
[`general/k4free_h10/order40/ORDER40_RESIDUAL.md`](general/k4free_h10/order40/ORDER40_RESIDUAL.md)
establishes

```text
R(3,10)=40, |V(G)|=40, and omega(G)<=3  ==>  beta(G)>=10.
```

Its separate audit is
[`general/k4free_h10/order40/INDEPENDENT_AUDIT.md`](general/k4free_h10/order40/INDEPENDENT_AUDIT.md).
If instead `R(3,10)=41`, the order-40 target is only `beta(G)>=9`, inherited
from the verified order-39 theorem.  Together with the unconditional
order-41 theorem, this closes the `K4`-free lane at the unresolved `h=10`
jump.  It does not settle clique numbers four or five, later jumps, or full
Erdős #151.

## Fixed-clique double CEGAR

The candidate-first implementation is in
[`../../experiments/erdos151_siege/fixed_clique_cegar/README.md`](../../experiments/erdos151_siege/fixed_clique_cegar/README.md).
It searches four exact ambient cases:

- `F5_N40`, `F5_N41`: a fixed `K5`, no `K6`;
- `F4_N40`, `F4_N41`: a fixed `K4`, no `K5`.

The outer graph solver is separated from two semantic oracles.  An
admissibility oracle either finds an admissible 10-set or proves none to the
inner solver; a coloring oracle either finds a red/blue triangle-avoiding
edge coloring or proves none to the inner solver.  Their projected cuts were
exhaustively checked on all small test instances.  Hash-chained journals,
exclusive writer locks, preset binding, and cross-linked candidate/result
provenance passed 14 regression tests.

The cases cover ambient clique numbers 4 and 5 only; the theorem above now
settles the complementary `omega<=3` lane at order 41.  Bare inner or outer UNSAT is not
proof-grade: any terminal UNSAT requires proof-producing reruns and an
independent certificate checker.  Any candidate requires the separate
definition-level verifier and checked certificates for both semantic UNSAT
formulas.

The first bounded v1 production pulses used `F5_N41` and `F4_N41`, because an
order-41 hit is an unconditional counterexample.  They stopped at their time
limits with respectively 5,577 and 10,368 audited exact cuts, no candidate,
and no terminal result.  These prefixes are `AUDIT_OK` but are not exhaustion
claims.  The audited batched v2 successor and frozen migration hashes are in
`experiments/erdos151_siege/fixed_clique_cegar_v2/`.

## Fractional aggregation audit

F1 (the triangle-free-edge graph bridge) and F4 (the edge-minimizing swap
potential) survive audit.  F2's displayed `L`-independent union bound is
algebraically the ordinary first-order coverage inequality, not a
strengthening.  The proposed `L=empty`, 7-regular, `omega=3` corner is
already impossible from the earlier two-walk inequalities; the reported
`59..65` and refined `64..65` ranges are correct only in a weakened
projection that discards those inequalities.

The executable audit in
[`../../experiments/erdos151_siege/fractional_lp/README.md`](../../experiments/erdos151_siege/fractional_lp/README.md)
also shows that an LP using only attachment-size and degree-class marginals
is feasible over both real and integral counts.  A meaningful next LP would
need anchor-fibre adjacency, edge-degree mixing, and rebasing correlations;
the coarse marginal program is retired.

## Honest remaining frontier

The highest-value live actions are:

1. continue the checkpointed `F5_N41` candidate hunt, then `F4_N41`;
2. obtain the missing full order-12/13 Ramsey-core catalogues from their
   authors or reconstruct only the degree-compatible slices reproducibly;
3. develop an `L≠empty` aggregation that counts `L`-independent 10-sets
   sharply while retaining anchor/exchange correlations;
4. attack the unresolved `omega in {4,5}` cases analytically at order 40 and
   by the independently auditable fixed-clique search at order 41.
