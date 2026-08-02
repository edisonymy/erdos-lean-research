# Erdős #719: bounded `r=3,n=9,nu<=1` attack

**Status (2 August 2026): `NO_COUNTEREXAMPLE_IN_DECLARED_SLICE`.**

This is not a solution of Erdős #719. It is a new bounded negative result and
a deliberately terminated diversification attack.

## Exact statement proved in this package

Let `G` be a 3-uniform hypergraph on nine vertices, and let `nu(G)` be the
maximum number of pairwise edge-disjoint copies of `K_4^3` in `G`. If
`nu(G)<=1`, then

`e(G)-3 nu(G) <= 54 = ex_3(9,K_4^3)`.

Consequently no such `G` is a counterexample to the displayed conjecture in
Erdős Problem #719.

## Why this is the correct objective

If a decomposition uses `t` copies of `K_4^3` and `s` singleton triples, then

`e(G)=s+4t` and `number of pieces=s+t=e(G)-3t`.

The exact minimum number of pieces is therefore `e(G)-3nu(G)`. For
`nu(G)=1`, a counterexample at order nine would require at least
`54+3+1=58` edges.

## Short proof

The copies of `K_4^3` correspond to a family `F` of 4-subsets. The condition
`nu(G)<=1` says that any two members of `F` intersect in at least three
vertices.

If `F` is empty, then `G` is `K_4^3`-free and `e(G)<=54`.

Otherwise, a 3-intersecting family of 4-sets has the following elementary
dichotomy.

1. All members contain one common triple; or
2. all members are contained in one fixed five-vertex set `U`.

To see this, take distinct `A,B` and put `S=A intersect B`, `U=A union B`.
Both have sizes three and five. Any further member not containing `S` must
contain the two points of `U-S` and two points of `S`. Once such a member
exists, pairwise 3-intersection forces every member to lie inside `U`.
Otherwise `S` is common. `check_structure.py` also exhausts all 18,900 finite
configurations in this implication.

In the common-triple case, delete that triple. Every `K_4^3` disappears, so

`e(G)-1 <= ex_3(9,K_4^3)=54`, hence `e(G)<=55`.

In the fixed-five case, let `M` be the missing triples of `G`. The family `M`
already hits every 4-set not contained in `U`. Three triples inside `U` suffice
to hit its five internal 4-sets; for `U={0,1,2,3,4}`, one choice is

`012, 034, 123`.

Thus adjoining at most three triples to `M` gives a missing-triple hitter for
all 126 four-sets. Since every `K_4^3`-free 3-graph on nine vertices misses at
least 30 triples, `|M|+3>=30`. Therefore `|M|>=27`, `e(G)<=84-27=57`, and

`e(G)-3nu(G) <= 57-3 = 54`.

This proves the displayed bounded theorem.

## Independent certificate for `ex_3(9,K_4^3)=54`

`check_result.py` uses only the Python standard library. It computes the exact
seven-vertex missing-edge hitting number `t_7=12`. Vertex deletion gives

`5t_8 >= 8t_7`, hence `t_8>=20`,

and a directly checked cyclic `3,3,2` construction has 36 edges, so `t_8=20`.
Deleting a vertex once more gives

`6t_9 >= 9t_8`, hence `t_9>=30`,

while the checked balanced cyclic `3,3,3` construction has 54 edges. Thus
`t_9=30` and `ex_3(9,K_4^3)=84-30=54`.

The checker also independently enumerates every `K_4^3` in the explicit
55-edge lower example, computes its exact edge-disjoint packing number as one,
and reports decomposition value 52, margin `-2`.

The checker status is deliberately `VERIFIED_GRAPH_QUANTITIES`: it validates
the example's schema and packing-one scope and recomputes its graph quantities.
The universal bounded theorem is established by the human-readable proof above,
with `check_structure.py` and the exact extremal computation as finite backstops.

## Solver evidence and near-miss interval

The analytic proof made further optimization unnecessary, but the completed
direct CaDiCaL queries agree with it and sharpen the numerical picture:

| fixed-five query | result | time | status level |
|---|---:|---:|---|
| `e>=58` | UNSAT | 32.063 s | solver result, no proof log |
| `e>=57` | UNSAT | 155.500 s | solver result, no proof log |
| `e>=57`, anchored `K_4^3=0123` | UNSAT | 114.500 s | solver result, no proof log |

The exact analytic argument needs only `e<=57`. The solver output suggests the
fixed-five branch actually has `e<=56`, but this package makes no certified
optimality claim. Together with the independently checked 55-edge common-
triple construction, the overall packing-one maximum is narrowed to `{55,56}`
at the solver-evidence level.

An attempted extension of the prior exact 38-edge `n=8` near miss would need
an 18-edge link graph; its complete 28-variable SAT instance was UNSAT. This
is a construction-specific obstruction, not a universal theorem.

## Reproduction

From the repository root:

```powershell
python experiments/erdos719_n9_k1/check_structure.py
python experiments/erdos719_n9_k1/construct_common_triple.py
python experiments/erdos719_n9_k1/check_result.py `
  experiments/erdos719_n9_k1/lower_55.json `
  --json-out experiments/erdos719_n9_k1/lower_55_checked.json
```

The SAT scripts additionally require the campaign's pinned `python-sat`
installation. Their JSON outputs are retained, so rerunning them is not needed
to check the human argument or the explicit near miss.

## Kill decision

The predeclared positive-margin target is impossible by the short argument,
and no witness appeared. The exact optimizer, the independent Z3 query, and a
threshold-56 sharpening query were stopped once they became irrelevant; no
status is inferred from those interrupted runs. No `n=10`, packing-two, or
other enlargement was attempted. This lane is killed unless a new structural
signal changes the expected value of a larger slice.
