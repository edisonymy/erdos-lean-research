# Exact-64 complement-hitting formulation

This is a specification only.  No long solve was launched from this audit.

Let

- `E = C([9],3)`, so `|E|=84`;
- `Q = C([9],4)`, so `|Q|=126`;
- `E(B)=C(B,3)` for `B in Q`; and
- `P4` be the unordered four-element subsets `{B1,B2,B3,B4}` of `Q`
  satisfying `|Bi intersect Bj|<=2` for every `i!=j`.

The last condition is exactly edge-disjointness of the four copies of
`K_4^(3)`, because two distinct four-sets share a 3-edge exactly when their
intersection has size three.  Direct enumeration in `audit_check.py` gives

```text
|P4| = 3,321,675.
```

For each triple `e in E`, introduce a binary variable `z_e`, with `z_e=1`
meaning that `e` is missing.  The exact feasibility problem is

```text
sum_{e in E} z_e = 20,

sum_{e in union_{B in P} E(B)} z_e >= 1       for every P in P4,

z_e in {0,1}.
```

Each union in the second line has exactly 16 triples.  Thus the direct SAT
version has an exact-20 cardinality encoding and one positive 16-literal
clause

```text
OR_{e in union_{B in P} E(B)} z_e
```

for each `P in P4`.  The displayed 0-1 inequalities are the identical ILP.

## Exactness proof

If a constraint is violated, all 16 triples in four pairwise edge-disjoint
tetrahedra are present, so the complement graph has packing number at least
four.  Conversely, any packing of four present tetrahedra is a member of
`P4`, its 16-edge union contains no missing triple, and its constraint is
violated.  Therefore feasibility is equivalent to

```text
exactly 64 present triples and nu <= 3.
```

Such a feasible point is a full counterexample to the displayed `r=3,n=9`
instance, since its minimum number of pieces is at least

```text
64 - 3*3 = 55 > ex_3(9,K_4^(3)) = 54.
```

The independently proved window reduction further implies that every feasible
point actually has `nu=3`, but this fact is not needed in the encoding and
must not be assumed by a candidate checker.

## Safe optional symmetry breaking

Define the missing degree of vertex `v` by

```text
d_v = sum_{e contains v} z_e.
```

Because the full formulation is invariant under every permutation of the
nine vertices, the inequalities

```text
d_0 >= d_1 >= ... >= d_8
```

are safe: every orbit has a relabeling with sorted missing degrees.  No
stronger lexicographic symmetry constraint is assumed here.

## Independent candidate check

`verify_exact64.py` accepts either 20 missing triples or 64 present triples.
It reconstructs all 126 possible tetrahedra without importing search code,
exhaustively searches for a four-packing, computes the exact packing number
when it is at most three, and independently recomputes the finite extremal
value 54 from an exact `t_7=12` hitter recursion, two deletion bounds, and a
checked 54-edge construction.

Example command:

```powershell
python research\full_solution_scout\erdos719_window_audit_2026-08-03\verify_exact64.py candidate.json --report candidate.checked.json
```

Exit code zero is reserved for a definition-level verified exact-64
counterexample.  A solver status or model that has not passed this checker is
not a mathematical claim.
