# Folkman/counterexample lane report

## Outcome

No order-41 counterexample candidate passed the priority checks in this lane.
The useful output is instead an exact, quantified obstruction for the smallest
degree-preserving perturbation family around the pinned order-39 Ramsey graph.

For every labelled graph `B'` obtained from that base by one valid old-old
2-switch, no graph obtained by adding two vertices and arbitrary incident
edges can satisfy both `Delta <= 9` and `alpha <= 9`.

This is strictly local to the pinned base plus one switch.  It does not settle
Erdos #151 and does not rule out larger perturbations or unrelated order-41
families.

## Exact evidence

- The base has 39 vertices, 167 edges, degree distribution `6^1 8^14 9^24`,
  `alpha = 9`, and exactly 4,511 independent 9-sets.  NetworkX complement
  enumeration and a direct CaDiCaL cardinality enumeration agree exactly.
- Two structurally independent switch enumerators agree on all 16,694 valid
  old-old 2-switches; their common catalogue hash is
  `567affe3444c454ccebbb134e1b9c61b1e4d6d94e2f047f2667d5049f9bfe370`.
- Old attachment capacity under `Delta <= 9` is 16: fourteen degree-8
  vertices can receive one new edge each, and the unique degree-6 vertex can
  meet both new vertices.
- If both new old-neighbourhoods have size at least 8, capacity forces one of
  1,716 unordered balanced partitions.  None passes even the surviving-base
  necessary test across 28,646,904 switch/partition pairs.  The nearest case
  still leaves 77 independent 9-sets unhit.
- The only smaller exact transversals are eleven switch/transversal pairs of
  size 6 and 363 of size 7.  Every one of the 374 branch-search UNSAT results
  was independently rechecked with CaDiCaL.
- Of those 374 cases, 331 are already impossible because the switched base
  has an explicit independent 10-set.  In each of the remaining 43, even the
  largest old-degree-compatible support for the other new vertex misses an
  explicitly recorded independent 9-set.  Hence no compatible pair exists.

The executable audit is `audit_one_switch_extensions.py`; its complete
machine-readable result is `one_switch_extension_audit.json`.

## Whole-graph switch probe

The separate stochastic 2-switch engine retained exact `alpha <= 9` on a
41-vertex degree-sequence `9^40,8^1` seed and quickly reached `omega = 4`.
Its terminal state has 99 triangles and passes the alpha/degree/clique gates,
but two independent validators exhibit both an admissible 10-set and a
triangle-avoiding edge 2-colouring, so it fails `beta <= 9` and edge-arrowing.
This trajectory is negative search evidence only, not an exhaustive result.

## Honest stopping point

The one-switch neighborhood has now been exhausted exactly.  The next local
family is two or more compatible old-old switches, where the state space and
new independent-set bookkeeping grow substantially.  Nothing found here
justifies treating that larger family as impossible, but the present evidence
also gives no screened candidate signal: the exact one-switch family fails
before beta or arrowing, and the unrestricted stochastic near-miss remains far
from both of those gates.
