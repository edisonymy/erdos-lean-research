# Erdős #719 completion-inequality audit

**Cutoff:** 3 August 2026
**Outcome:** no full solution and no counterexample.  The proposed global
completion lemma is a Tuza-hard strengthening of #719 and is not a viable
one-week route.  A conditional order-ten equality reduction survives, but its
needed supersaturation premise was **not** proved.

## 1. Exact definitions and the hardness barrier

Let `G` be an `r`-graph on `V`, `|V|=n`, and put `s=n-r`.  Complement each
`r`-edge to an `s`-set.  If `H` is the family of missing `s`-sets, then

* `h=|H|=binom(n,r)-e(G)`;
* `U(H)` is the family of `(s-1)`-sets contained in no member of `H`;
* the complement of `A in U(H)` is the vertex set of a present
  `K_(r+1)^r` in `G`;
* `rho(U(H))` is exactly the maximum number `nu(G)` of edge-disjoint
  simplices; and
* an `s`-set covering a member of `U(H)` complements to an `r`-edge meeting
  the corresponding simplex.  Therefore `tau_s(U(H))` is exactly the minimum
  simplex-edge transversal number `tau_r(G)`.

Consequently

```text
tau_s(U(H)) <= (n-s) rho(U(H))
```

is exactly

```text
tau_r(G) <= r nu(G).                              (T_r)
```

For `r=2`, `(T_r)` says that the minimum number of graph edges meeting every
triangle is at most twice the maximum number of edge-disjoint triangles.  It
is **exactly Tuza's conjecture**, for every graph, not merely an analogy.
Every graph produces a realizable `U(H)`, so the word “realizable” does not
remove this obstruction.

This priority check agrees with:

* R. Aharoni and S. Zerbib, [*A generalization of Tuza's
  conjecture*](https://arxiv.org/abs/1611.07497), which defines the same
  `m`-set transversal / `m`-overlap packing framework and identifies the
  triangle-family case; and
* M. Krivelevich, [*On a conjecture of Tuza about packing and covering of
  triangles*](https://doi.org/10.1016/0012-365X(93)00228-W), which states the
  still-nontrivial graph inequality and proves restricted/fractional cases.

Thus proving the completion lemma would solve a famous open problem already
on its `r=2` slice.  It is strictly stronger than what #719 needs.

### Correct slack-sensitive target

Write

```text
d(G)     = e(G) - ex_r(n,K_(r+1)^r),
sigma(G) = tau_r(G) - d(G)
         = h + tau_s(U(H)) - C(n,s,s-1) >= 0.
```

Then #719 is exactly the weaker inequality

```text
tau_r(G) - r nu(G) <= sigma(G).                  (S)
```

The proposed completion lemma discards `sigma(G)` and demands that the
left-hand side be nonpositive.  Future global work must use this extremal
slack (or an equivalent direct `h`-sensitive charge); otherwise it is trying
to prove Tuza/generalized Tuza on the way to #719.

Equation `(S)` is an exact algebraic correction, not a newly proved route to
the conjecture.  It identifies the missing ingredient honestly.

## 2. Exhaustive falsification screen

[`exhaustive_small.py`](exhaustive_small.py) computes `U(H)`, `tau_s(U)` and
`rho(U)` exactly with separate set-cover and compatibility-graph recursions.
No violation was found in the following complete spaces:

| `n` | `s` | `r` | all `H` | distinct realizable `U(H)` |
|---:|---:|---:|---:|---:|
| 4 | 2 | 2 | 64 | 12 |
| 5 | 2 | 3 | 1,024 | 27 |
| 5 | 3 | 2 | 1,024 | 187 |
| 6 | 2 | 4 | 32,768 | 58 |
| 6 | 3 | 3 | 1,048,576 | 6,115 |
| 6 | 4 | 2 | 32,768 | 6,115 |

It also found no violation among all `2^10=1,024` arbitrary families for
`(n,s)=(5,3)` or all `2^20=1,048,576` arbitrary families for `(6,4)`.

These are adversarial computational checks, not a proof beyond the enumerated
orders and not evidence that the global statement is easy.  The Tuza
equivalence controls the strategic conclusion.

## 3. The order-ten SQS equality route

For the first unresolved negative target `r=3,n=10`, a full counterexample at
packing number two would have `e(G)=82`, hence 38 missing triples.  Let `q` be
the number of present tetrahedra (clean 4-sets).

An `SQS(10)` exists by H. Hanani, [*On Quadruple
Systems*](https://doi.org/10.4153/CJM-1960-013-3).  It has
`binom(10,3)/4=30` blocks, and its blocks are edge-disjoint tetrahedra.
Randomly relabel a fixed `SQS(10)`.  Each of the 210 four-sets occurs with
probability `30/210=1/7`.  If `nu(G)<=2`, every relabelled system contains at
most two clean blocks, so

```text
q/7 <= 2, hence q <= 14.                         (1)
```

This yields the following rigorous **conditional** reduction:

> If one independently proves that every 82-edge 3-graph on ten vertices has
> at least 14 tetrahedra, then a packing-two counterexample must have exactly
> 14, and **every labelled SQS(10) contains exactly two of them**.

The last assertion follows because the random intersection is an
integer-valued random variable bounded above by two and has expectation two.

### What computation did and did not establish

[`n10_leave_milp.py`](n10_leave_milp.py) found 38 missing triples leaving 14
clean quads.  HiGHS hit its 300-second limit with relative gap
`0.6428571428571344`; it did **not** prove that 14 is minimal.

The retained construction was rebuilt from its missing triples by the
standard-library [`independent_verify_n10_leave.py`](independent_verify_n10_leave.py).
It verifies exactly 14 clean quads and exact packing number **8**, so this is
not remotely a #719 counterexample.  See
[`n10_leave_independent_check.json`](n10_leave_independent_check.json).

An exact SAT query asking for 38 missing triples and at most 13 clean quads
was deliberately terminated under the campaign kill gate after roughly four
minutes.  Its status is **UNKNOWN**.  The CNF is retained as
[`n10_leave_atmost13.cnf`](n10_leave_atmost13.cnf); there is no solver result
or certificate and no supersaturation claim.

### The obvious equality model is unrealizable

For a triple `a`, let `Q_a` be the seven 4-sets containing `a`.  If triples
`a,b` intersect in at most one point, `Q_a union Q_b` has 14 members, packing
number two, and every `SQS(10)` meets it in exactly two blocks (the unique
blocks covering `a` and `b`).  Thus constant SQS intersection alone is not a
contradiction.

However this obvious model cannot be the exact tetrahedron family of any
3-graph:

* if `a={0,1,2}` and `b={3,4,5}`, the forced shadows of the two stars make
  `{0,1,3,4}` a tetrahedron outside the two stars; and
* if `a={0,1,2}` and `b={2,3,4}`, the same happens to `{0,1,3,4}`.

For example, in the disjoint case every triple of `{0,1,3,4}` extends with
the missing centre point to a member of one of the two prescribed stars, so
all four triples are forced present.  The one-point case is identical with
the common centre point.  [`verify_two_star_obstruction.py`](verify_two_star_obstruction.py)
checks all representatives and records every forced extra quad.

No classification of all 14-set families having constant intersection two
with every `SQS(10)` was proved.  That is the honest remaining equality-case
problem, conditional on the unproved 14-tetrahedron lower bound.

## 4. Reproduction

From the repository root:

```powershell
.\.venv\Scripts\python.exe -B research/full_solution_scout/erdos719_completion_inequality_max_2026-08-03/exhaustive_small.py --n 6 --s 3 --out research/full_solution_scout/erdos719_completion_inequality_max_2026-08-03/exhaustive_n6_s3.json
.\.venv\Scripts\python.exe -B research/full_solution_scout/erdos719_completion_inequality_max_2026-08-03/independent_verify_n10_leave.py
.\.venv\Scripts\python.exe -B research/full_solution_scout/erdos719_completion_inequality_max_2026-08-03/verify_two_star_obstruction.py
```

The stopped SAT input can be rebuilt, but running it is not recommended under
the current campaign allocation:

```powershell
.\.venv\Scripts\python.exe -B research/full_solution_scout/erdos719_completion_inequality_max_2026-08-03/n10_leave_sat.py --solver cadical195 --cnf research/full_solution_scout/erdos719_completion_inequality_max_2026-08-03/n10_leave_atmost13.cnf
```

## 5. Allocation decision

**Kill the global completion-inequality lane.**  It is at least Tuza-hard,
and the small checks do not change that.  Do not resume the order-ten
`q<=13` SAT run merely to obtain a bounded positive theorem.

Resume this line only if one of two qualitatively new inputs appears:

1. a direct `h`/extremal-slack inequality addressing `(S)` rather than
   `tau<=r nu`; or
2. an independently certified, cheap proof of the 14-tetrahedron lower bound,
   after which classifying constant-two SQS intersections and testing their
   realizability becomes a sharply bounded equality problem.

Absent either signal, resources should move away from #719 unless the
separate candidate-first n=10 search produces a concrete dual-verifiable
witness.
