# Independent audit: Erdős #719 `n=9` all-edge-count reduction

**Date:** 3 August 2026.
**Verdict:** **PASS.** No direction error, hidden integrality assumption, or
rounding bug was found.  The proposed reduction is sound and leaves exactly

```text
(m,nu) = (61,2) and (64,3).
```

This does **not** prove that either surviving class is empty or contains a
counterexample.  No long SAT/ILP solve was launched, and no Fable process or
artifact was touched.

## 1. Statement fidelity and the exact objective

For `r=3`, a `K_3^3` is one triple and a `K_4^3` consists of the four triples
on a four-set.  If `G` has `m` triples and a decomposition uses `t`
edge-disjoint tetrahedra, it has

```text
t + (m-4t) = m-3t
```

pieces.  Conversely, every packing extends to a decomposition by making each
uncovered edge a singleton.  Thus the exact minimum number of pieces is

```text
phi(G) = m - 3 nu(G).
```

The finite extremal certificate gives

```text
ex_3(9,K_4^3) = 54.
```

For completeness, let `t_n` be the minimum number of triples meeting every
four-set.  An exact recurrence gives `t_7=12`.  If `H` is an `n`-vertex
hitter, the triples of `H` avoiding a vertex `v` hit all four-sets avoiding
`v`; summing over vertices gives

```text
(n-3)|H| = sum_v |H-v| >= n t_(n-1).
```

Consequently

```text
t_8 >= ceil(8*12/5) = 20,
t_9 >= ceil(9*20/6) = 30.
```

A directly checked 54-edge `K_4^3`-free construction on nine vertices has 30
missing triples, so `t_9=30` and `84-30=54`.  `verify_exact64.py` recomputes
the recurrence and the construction independently.

Put

```text
h = 84-m,
k = nu(G).
```

A counterexample satisfies

```text
m-3k > 54
iff 84-h-3k >= 55
iff h+3k <= 29.                                      (1)
```

All strict-to-weak conversions here are valid because the quantities are
integers.

## 2. The nonobvious strict packing-one reduction

The claimed `+31` is correct; it is stronger than the elementary hitter bound
`h+4k>=30` and does not follow from that bound alone.

First recall the independently audited packing-one theorem:

```text
nu(J)<=1  =>  e(J)-3nu(J)<=54.
```

A short proof is included to expose every dependency.  If `nu(J)=0`, this is
the definition of the extremal number.  If `nu(J)=1`, the family of present
four-sets is pairwise 3-intersecting.  Such a family either has a common
triple or lies inside a fixed five-set:

- choose distinct `A=S union {a}` and `B=S union {b}`, with `|S|=3`;
- a member not containing `S` must be `(S-{s}) union {a,b}`;
- after such a member exists, a member using a vertex outside `A union B`
  would have to be `S union {x}`, which intersects it in only two vertices.

In the common-triple case, deleting that one edge destroys every tetrahedron,
so `e(J)-1<=54`, hence `e(J)<=55`.  In the fixed-five case, the missing edges
already hit every four-set outside the fixed five-set.  Three triples, for
example `012,034,123`, hit all five internal four-sets.  Since every complete
nine-vertex hitter has at least 30 triples, `J` has at least `30-3=27`
missing edges and hence `e(J)<=57`.  Therefore in both cases
`e(J)-3<=54`.

Now let `P_1,...,P_k` be a maximum packing in a proposed counterexample.
Here `k>=1`, because `k=0` would give `m<=54`.  Delete all four edges of
`P_1,...,P_(k-1)` and call the remaining graph `J`.  It still contains
`P_k`.  It cannot contain two edge-disjoint tetrahedra: those two together
with the `k-1` deleted packing members would be a `(k+1)`-packing in `G`.
Hence `nu(J)=1`, and the packing-one theorem yields

```text
m - 4(k-1) = e(J) <= 57.
```

Rearranging gives the claimed strict inequality

```text
m <= 4k+53
iff h+4k >= 31.                                      (2)
```

There is no assumption that a generic maximum packing union is a minimum
hitter; using only that weaker route would incorrectly produce 30 instead of
31.

## 3. Explicit 18-block packing and its SQS(10) check

On vertices `0,...,8`, take these 18 four-sets:

```text
0134  0158  0167  0235  0247  0268
0378  0456  1236  1245  1278  1357
1468  2348  2567  3467  3568  4578
```

Their 72 constituent triples are all distinct.  The twelve unused triples
are

```text
012  036  048  057  138  147
156  237  246  258  345  678.
```

These are the lines of `AG(2,3)`.  Add a tenth point `9` and the twelve
blocks obtained by adjoining `9` to those lines.  The resulting 30 four-sets
contain each of the `C(10,3)=120` triples exactly once, so they form an
explicit `SQS(10)`.  Deleting point `9` gives exactly the displayed
18-block packing.  `audit_check.py` checks all 120 incidences, not just the
block and edge counts.

Let `q` be the number of present tetrahedra of `G`.  Randomly permute the nine
vertices of the fixed 18-block packing.  Each individual block is uniform on
the 126 four-sets, so linearity of expectation gives

```text
E[number of present packed blocks] = 18*q/126 = q/7.
```

Every relabeled set of 18 blocks remains edge-disjoint, so it contains at
most `k=nu(G)` present blocks.  Therefore

```text
q <= 7k.                                             (3)
```

No independence between the 18 random block indicators is used.

## 4. Excluding every `m>=68`

Each missing triple belongs to exactly six four-sets.  A non-present
tetrahedron must contain a missing triple, so the union bound gives

```text
q >= 126-6h.                                         (4)
```

From (1), `k<=floor((29-h)/3)`.  For `h=3a+r`, where `r` is `0,1,2`, this
upper bound is `9-a`, and

```text
(126-6h) - 7(9-a) = 63-11a-6r.
```

For `h<=16`, the smallest value in each residue class occurs at `h=15,16,14`
respectively and is `8,2,7`.  Thus (4) is strictly greater than `7k` in every
case, contradicting (3).  Hence every counterexample has

```text
h>=17, or equivalently m<=67.                        (5)
```

The strict comparison at the closest endpoint is `q>=30>28>=7k` for `h=16`.

## 5. Integer window before the overlap improvement

Enumerating the integer solutions of (1), (2), and (5) gives exactly

| `h` | `m=84-h` | `k` |
|---:|---:|---:|
| 17 | 67 | 4 |
| 19 | 65 | 3 |
| 20 | 64 | 3 |
| 23 | 61 | 2 |

For example, the lower and upper bounds are

```text
ceil((31-h)/4) <= k <= floor((29-h)/3).
```

Checking `h=17,...,26` yields the four rows above and no others.

## 6. Overlap/pair-energy lemma

Let `H` be the `h` missing triples.  For each of the 36 vertex-pairs `p`, let
`d_p` be the number of missing triples containing `p`, and define

```text
E = sum_p C(d_p,2).
```

Because `sum_p d_p=3h` and `x -> C(x,2)` is discretely convex, `E` is
minimized when the 36 codegrees differ by at most one.

For each four-set `Q`, let `j_Q` be its number of missing triples and let
`a_j` count the four-sets with `j_Q=j`.  Two distinct triples in a four-set
share exactly one vertex-pair, and two missing triples sharing a vertex-pair
have a unique four-set as their union.  Hence

```text
E = sum_Q C(j_Q,2) = sum_j C(j,2)a_j.                (6)
```

Also, each missing triple lies in six four-sets, so

```text
q = a_0
  = 126 - 6h + sum_{j=2}^4 (j-1)a_j.                (7)
```

For `j=2,3,4`,

```text
j-1 >= C(j,2)/2.
```

Equations (6) and (7), with the integrality of the correction term, give

```text
q >= 126 - 6h + ceil(E/2).                           (8)
```

Now apply the balanced-codegree lower bound:

- `h=17`: `3h=51=21*1+15*2`, so `E>=15` and
  `q>=126-102+ceil(15/2)=32`.  But `k=4` and (3) give `q<=28`.
- `h=19`: `3h=57=15*1+21*2`, so `E>=21` and
  `q>=126-114+ceil(21/2)=23`.  But `k=3` and (3) give `q<=21`.

Thus `(m,k)=(67,4)` and `(65,3)` are impossible.  Both ceilings are necessary
and were applied in the correct direction.

## 7. Final proved window

The only surviving possibilities for a nine-vertex counterexample are

```text
(m,nu) = (64,3) or (61,2).
```

Accordingly, an exact-61-only attack is not exhaustive for `n=9`; a separate
exact-64 complement-hitting feasibility attack is mathematically warranted.
Its exact SAT/ILP specification and independent checker are in
`EXACT64_FORMULATION.md` and `verify_exact64.py`.

## 8. Evidence ledger and claim boundary

### Proved from the displayed arguments

- `phi(G)=m-3nu(G)` and the counterexample inequality `h+3k<=29`.
- The packing-one reduction `h+4k>=31`.
- The 18-packing averaging inequality `q<=7k`.
- The dense exclusion `h>=17`.
- The pair-energy lower bound and the exclusion of `(67,4)` and `(65,3)`.
- The final two-case window, conditional only on the finite value
  `ex_3(9,K_4^3)=54` and the packing-one theorem, both independently audited.

### Mechanically checked in this directory

- All 120 triple incidences in the explicit SQS(10).
- The 72 distinct covered triples and twelve exact uncovered affine lines.
- Every integer and rounding calculation in the window.
- The pair-energy minima and numerical contradiction gaps.
- The count `3,321,675` of four-packing constraints for exact 64.
- A from-scratch `t_7=12` recurrence and a checked 54-edge extremal
  construction in the candidate verifier.

Reproduction:

```powershell
python research\full_solution_scout\erdos719_window_audit_2026-08-03\audit_check.py
```

Expected final status: `PASS`.

### Conjectural / not established here

- Existence or nonexistence of an exact-61 graph with `nu<=2`.
- Existence or nonexistence of an exact-64 graph with `nu<=3`.
- Any resolution of Erdős #719 beyond a future independently checked witness.
- Solver performance, UNSAT, or priority claims for either surviving class.
