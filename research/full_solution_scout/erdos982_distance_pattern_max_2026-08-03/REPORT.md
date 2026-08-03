# Erdős #982 distance-pattern lane — final report

**Date:** 2026-08-03
**Disposition:** stopped at the predeclared kill gate
**Full solution or counterexample:** none

This lane first audited the low-order locally-few-distance literature, then
tested a sparse algebraic extension of the known convex `D4` octagon family,
and finally ran a bounded asymmetric inverse-design search for the first
remaining counterexample target: a strictly convex 10-point set in which every
vertex sees at most four distances.  It did not use the separate `H8`
relaxation lane and did not enumerate raw colourings of `K10`.

## 1. Priority correction: orders 8 and 9 are already settled

The initial `K8` witness-pattern enumeration was stopped as soon as the
following source was checked directly.

Nozaki and Shinohara, *On a generalization of distance sets*,
[arXiv:0906.0199](https://arxiv.org/pdf/0906.0199), Section 4.5,
Proposition 4.18 in arXiv v2 (Proposition 4.3 in v1), states:

1. every eight-point planar set has total local distance count at least 24;
2. equality is unique up to similarity; and
3. every eight-point planar locally three-distance set is that unique
   configuration.

The proposition cites Erdős--Fishburn, *Distinct distances in finite planar
sets*, [Discrete Mathematics 175 (1997), 97--132](https://www.sciencedirect.com/science/article/pii/S0012365X96001458),
and Fishburn's later paper makes the uniqueness statement explicit in its
abstract: *A remarkable eight-point planar configuration*,
[Discrete Mathematics 252 (2002), 103--122](https://www.sciencedirect.com/science/article/pii/S0012365X01001340).
The configuration is `H8`, two concentric squares rotated by 45 degrees with
side ratio `2 cos(15 degrees)`.

In the exact normalization

```text
(+/-R,0), (0,+/-R), (+/-1,+/-1),   R = 1 + sqrt(3),
```

the four inner-square points satisfy `|x|+|y|=2<R`, so they lie strictly
inside the axial diamond.  Thus `H8` is not in convex position.  Consequently
there is no convex order-8 counterexample, and the stated optimality
`LDS_2(3)=8` also rules out any order-9 locally-three-distance counterexample.

Targeted searches for `LDS_2(4)`, “locally four-distance set”, and citations
of the Nozaki--Shinohara terminology did **not** locate a planar local-4
classification.  This is an absence-of-evidence audit, not a proof that no
such result exists.  Global four-distance classifications are different and
do not settle the local condition.

The files `enumerate_witness_patterns.py` and `witness_pattern_smoke.json` are
therefore explicitly **superseded partial telemetry**, not an exhaustive
result and not evidence for a new theorem.

## 2. Exact restricted theorem for the convex `D4` family

Scale the known convex family to

```text
S_r = {(+/-r,0), (0,+/-r), (+/-1,+/-1)},   1 < r < 2.
```

Its axial squared-distance palette is

```text
{4r^2, 2r^2, r^2-2r+2, r^2+2r+2},
```

and its diagonal palette is

```text
{8, 4, r^2-2r+2, r^2+2r+2}.
```

### Exact conclusion

There is no point `x=(u,v)` for any real `1<r<2` whose squared distance to
each of the eight old vertices belongs to that old vertex's displayed
palette.  Therefore there cannot be a two-point extension under the same
old-palette restriction.

### Why the finite reduction is lossless in this scope

If the distances from `x` to `(r,0)` and `(-r,0)` select palette values
`d_E,d_W`, subtraction gives

```text
u = (d_W-d_E)/(4r).
```

There are only 13 distinct rational functions obtained this way.  The same
argument gives 13 possibilities for `v`, so only 169 symbolic coordinate
pairs remain.  For each pair, `d4_two_point_palette.py` forms the eight exact
palette-membership products, clears denominators, computes their gcd in
`QQ[r]`, and checks its real roots in `(1,2)`.  There are zero roots.

An independent checker uses a different enumeration: it selects the four
axial palette assignments (`4^4=256`), derives `u,v`, imposes two axial
placement equations and four diagonal membership products, then uses exact
real-root counting.  It also returns zero roots.  Its compact output is:

```text
assignments                                      256
assignments_with_nonconstant_common_gcd           28
exact_real_roots_in_open_interval_1_2               0
verified_no_extension                            true
```

### Claim boundary

This is **not** a proof for all extensions of the `D4` family and not a result
on Erdős #982 itself.  For generic `r`, every old vertex already sees four
distances, so the old-palette condition is necessary.  At the two collision
ratios

```text
r = (1+sqrt(7))/3,       r = -1+sqrt(7),
```

one orbit of four old vertices sees only three distances and could admit one
new value.  Those minimally relaxed exceptional systems were not covered by
this run.  No statement is made about them.

## 3. Asymmetric order-10 inverse design

The search parameterized ten points by positive polar radii and positive
angular gaps, with rotation and scale normalized away.  At each step it found
the exact least-squares four-clustering of the nine normalized squared
distances at every vertex, then fitted the induced equality equations.
Convexity was measured by the minimum normalized consecutive turn cross
product.  These calculations are candidate generation only.

### Results

- Regular-decagon baseline: maximum within-cluster span `0.0954915`, total
  row SSE `0.0607908`, minimum turn `0.0561285`.
- Twenty strictly convex local alternating starts found no improvement signal;
  the best retained run had span `0.121040`, total SSE `0.0636828`, and turn
  `0.0473932`.
- A weakly penalized global probe reached maximum row SSE `0.000362863`, but
  only after leaving convexity: minimum turn `-0.000249687`.
- Two global runs with a hard positive turn floor `5e-4` improved the regular
  baseline but both pinned to the floor:

```text
run   min turn       max cluster span   total row SSE
0     0.000499989    0.0416963          0.00595051
1     0.000499947    0.0445151          0.00517621
```

- A continuation trace from the best run gave:

```text
imposed floor   attained min turn   max cluster span   total row SSE
0               2.75e-10            0.0416842          0.00591007
5e-4            0.000499999         0.0418220          0.00598019
2e-3            0.002000000         0.0447478          0.00787385
```

The minimum turn follows the imposed floor, the residual does not tend toward
zero even as the floor does, and the inferred partition changes at every
listed margin.  There is no stable equality pattern to extract and no
positive-margin near-solution.

### Allocation decision

This meets the lane's kill criterion.  More restarts would currently optimize
a degenerating boundary family rather than an identifiable algebraic
candidate.  The exact `D4` restricted no-extension result is worth retaining,
but this numerical lane does not earn more compute without a new structural
constraint or seed family.

## 4. Reproduction and hashes

Run from the repository root with the campaign virtual environment:

```powershell
.\.venv\Scripts\python.exe -B research\full_solution_scout\erdos982_distance_pattern_max_2026-08-03\d4_two_point_palette.py --out research\full_solution_scout\erdos982_distance_pattern_max_2026-08-03\d4_two_point_palette.json
.\.venv\Scripts\python.exe -B research\full_solution_scout\erdos982_distance_pattern_max_2026-08-03\independent_check_d4_palette.py --out research\full_solution_scout\erdos982_distance_pattern_max_2026-08-03\d4_palette_independent_check.json
```

Key SHA-256 values:

```text
26802bd4c3357c612f7d0e3c336364729df2d4c32cc045cb0ce8c0ba9c991128  d4_two_point_palette.json
58b024fb1ab60862907a3202c4a95ccc06e3766212206d346962684b9d03857b  d4_palette_independent_check.json
c4f10a7aec2e0137696a4d5c3b00373e9fa4d96c4d146554bb6d8954cc01450d  inverse_design_de_n10_runA.json
12ec99c544e8d480be44ebdba7ec12ff654bd92318e9ea7feaa2566d1da6f0ed  convex_margin_trace_n10.json
```

Approximate active compute in the retained experiments was under four
minutes, plus one deliberately terminated two-minute diagnostic trace.  No
solver, optimizer, or agent remains running from this lane.
