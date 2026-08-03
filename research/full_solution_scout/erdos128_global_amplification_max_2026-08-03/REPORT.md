# Erdős #128: global amplification checkpoint

Date: 2026-08-03

## Verdict

This lane does **not** solve or disprove Erdős Problem #128.  It proves one
arbitrary-block theorem on a natural boundary face, identifies the exact
quotient inequality still needed for the full boundary case, and gives an
explicit obstruction to the hoped-for positive-mass amplification in the
complementary low-type branch.

The allocation decision is therefore **stop/pivot**.  More local counting on
this route is not justified.  Restart only if one can prove the paired-type
quotient inequality stated below, find a counterexample to it, or import a
genuinely applicable proved stability theorem.

## Setup and a general type lemma

Normalize the total vertex weight to one.  Let `I` be a maximum independent
set of weight `x`, and for an outside vertex or twin class `v` write

```text
S_v = N(v) intersect I.
```

In a maximal triangle-free graph, if

```text
d = min_v |S_v| > x/3,
```

then for any two outside vertices `u,v`,

```text
uv is an edge  iff  S_u and S_v are disjoint.                 (T)
```

The forward implication is triangle-freeness.  For the converse, if `u,v`
were a nonedge with disjoint types, maximality would give a common outside
neighbor `w`; its type is disjoint from both, so
`x >= |S_u|+|S_v|+|S_w| > x`, a contradiction.

At the exact complementary-half boundary `d=x/2`, (T) gives the familiar
decomposition of the outside graph into complete bipartite blocks between
complementary half-types, plus full-type isolates.

There are also useful global-alpha inequalities between blocks.  Write the
two side weights of block `i` as `p_i <= q_i`, and choose one half-type
`T_i` for its large side.  If `c=|T_i intersect T_j|` and `h=x/2`, maximum
independence gives

```text
q_i + q_j + c       <= x,
q_i + p_j + h - c   <= x,
p_i + q_j + h - c   <= x.
```

In particular,

```text
2q_i + q_j + p_j <= 3x/2,
q_i + p_i + 2q_j <= 3x/2,
q_i <= x/2.
```

These constraints rule out several naive multi-block profiles, but do not by
themselves prove the sparse-half bound.

## Proved theorem: the balanced, saturated boundary face

Consider any **finite** complementary-half quotient with:

- an independent class `I` of weight `x`;
- full-type outside isolates of total weight `t`;
- arbitrarily many complementary blocks whose two sides both have weight
  `u_i`;
- the outside maximum independent set saturated:
  `t + sum_i u_i = x`.

For `1/3 <= x <= 2/5`, this quotient has a weighted half of edge weight at
most `1/50`.  Equality is possible only for the balanced `C_5` blow-up:

```text
x=2/5,  t=1/5,  one block u_1=1/5,
```

up to zero-weight classes.

### Proof

Put

```text
h=x/2,  r=1/2-x,  P=sum_i u_i,  S2=sum_i u_i^2.
```

The two mass equations give

```text
P=1-2x=2r,  t=3x-1.
```

Sort `u_1 >= u_2 >= ...`.

**Menu 0 (outside only).**  Take all full isolates and one full side of each
block; this has weight `x`.  Put weight `1/2` on every opposite side, whose
total weight is `P=2r`.  The resulting half has edge weight

```text
C0 = S2/2.                                                   (1)
```

**Menu 1 (type oriented).**  Take the same isolates and one side per block,
and add a set `J` of weight `r` from `I`, orienting each block toward the side
whose type has smaller intersection with `J`.  The unoptimized baseline is

```text
B = tr + Pr/2 = r(2x-1/2).                                  (2)
```

Choose `J` inside one half-type of the largest block.  This makes that
block's contribution zero, and hence

```text
C1 <= B - r u_1/2 <= B - S2/4,                              (3)
```

because `S2 <= u_1 P` and `P=2r`.

Combining (1) and (3),

```text
min(C0,C1) <= 2B/3.
```

For `1/3 <= x <= 7/20`,

```text
1/50 - 2B/3 = (5x-2)(20x-7)/75 >= 0.                        (4)
```

At `x=7/20`, equality in the displayed estimates would require
`S2=1/25`, `u_1=S2/P=2/15`, and every positive `u_i` equal to `u_1`.
But `P/u_1=9/4` is not an integer.  Thus the finite quotient is strict at
this joining point.

For `7/20 <= x <= 2/5`, refine Menu 1 using the second-largest block.  The
two half-types of block 2 cut the chosen half-type of block 1 into pieces of
weights `c` and `h-c`; one has weight at least `h/2`.  Fill `J` from the
larger piece first.  Since `r>=h/2` on this interval, the block-2
contribution is at most `u_2(r-h/2)`, and therefore

```text
C1 <= B - (r u_1 + (h-r)u_2)/2.                             (5)
```

Suppose both menus had cost greater than `1/50`.  Let

```text
K = 2(B-1/50),  A=u_1,  d=h-r.
```

Then `S2>1/25` and

```text
rA + d u_2 < K.                                              (6)
```

Since every remaining `u_i` is at most `u_2`,

```text
S2 <= A^2 + u_2(P-A).                                       (7)
```

If `A<=K/h`, use `u_2<=A` in (7); if `A>=K/h`, use
`u_2<=(K-rA)/d`.  The latter expression in (7) is convex in `A`, so its
maximum occurs at `A=K/h` or `A=K/r`.  In both cases,

```text
S2 <= max(2rK/h, (K/r)^2) <= 1/25.                           (8)
```

The last inequalities follow from

```text
(1/5)r-K = 4(5x-2)^2/25 >= 0,

1/25 - 2rK/h
  = -(400x^3-500x^2+203x-27)/(25x) >= 0.
```

For the cubic, its derivative has roots `7/20` and `29/60`; it decreases
on the interval in question and its value at `7/20` is `-1/20`.
This contradicts `S2>1/25`.

If equality in the sparse-half bound is possible, the same inequalities are
strict before `x=2/5`.  At `x=2/5`, equality forces
`S2=1/25`, `u_1=1/5`, and `u_2=0`, hence the claimed single-block profile.
It is the balanced `C_5` blow-up.  Its exact half minimum is `1/50`: after
scaling its five equal classes to capacities one, a mass-transfer argument
reduces a minimizer to two full coordinates and one half coordinate, and
enumeration around the 5-cycle gives adjacent-product sum at least `1/2`.

This theorem covers arbitrarily many blocks but only the
`p_i=q_i`, `t+sum q_i=x` face.  It is not a full boundary theorem.

## A tempting symmetrization is false

One might replace every `K(p_i,q_i)` by `K(p_i,p_i)` and move `q_i-p_i` to
the full-type isolates, hoping this can only increase the minimum half
weight.  It can decrease it substantially.

An exact two-block witness is

```text
x  = 1997/5000,       h=x/2,
p1 = 77/1000,         q1 = 687/5000,
p2 = 621/5000,        q2 = 1419/10000,
t  = 1201/10000,
|T1 intersect T2| = 787/10000.
```

The four `I`-atom weights are `[c,h-c,h-c,c]`.  Exact extreme-point
enumeration gives

```text
beta(original)    = 43527/3125000  = 0.01392864,
beta(symmetrized) = 221503/25000000 = 0.00886012.
```

This is not a counterexample to #128; both values are safely below `1/50`.
It only falsifies the monotonicity shortcut.

## Exact missing boundary lemma

The boundary branch would close if the following weighted quotient statement
were proved.

Let `I` have measure `x in (rho_0,2/5)` and put `h=x/2`.  Let there be a
finite family of complementary half-type pairs
`(S_i, I\S_i)`, side weights `p_i<=q_i`, and full-type isolate weight `t`,
with

```text
x + t + sum_i(p_i+q_i) = 1.
```

Impose the complete maximum-independence conditions:

```text
t + sum_i q_i <= x,

sum_{i in J} w_i^(epsilon_i)
  <= measure(union_{i in J} S_i^(epsilon_i))                 (H)
```

for every subfamily `J` and every choice of one oriented side from each pair.
Construct the corresponding quotient: `I` is independent; each outside side
is joined to its type; complementary sides of the same pair are complete to
one another; different blocks have no outside edges; full-type isolates are
joined to all of `I`.

**Missing lemma.**  Every such quotient has weighted-half minimum at most
`1/50`, with equality only for the balanced `C_5` quotient.

Condition (H) is exactly what says that adding the vertices of `I` outside
the union of the chosen neighbor types cannot create an independent set
heavier than `x`.  The balanced-saturated theorem proves one face of this
lemma.  The unbalanced/nonsaturated case requires a new inequality coupling
the outside-only lower-tail cost, orientations of the half-types, and all of
the Hall-type union constraints (H).  Scalar pair constraints and second
moments did not suffice.

## Low-type aggregation fails from local structure

The complementary branch contains a vertex with `|S_v|<=x/3`.  Conditioning
on one such vertex changes the usual half expectation by only `O(n)`, not
`Theta(n^2)`.  A possible rescue would be to prove that low-type vertices
have positive total mass.  This is **false** using maximality, the alpha
window, and the smallest-counterexample minimum-degree bound alone.

Take the Chvátal graph on vertices `0,...,11` with edge set

```text
01 04 06 09 12 15 17 23 26 28 34 37
39 45 48 5A 5B 6A 6B 78 7B 8A 9A 9B,
```

where `A=10`, `B=11`.  It is triangle-free and has diameter two, hence is
maximal triangle-free.  Fix

```text
I={0,2,5,7},  x=19/50,
```

and give each vertex of `I` weight `19/200`.  For any
`0<epsilon<1/20`, assign the outside weights

```text
w1 = 1/20-epsilon,   w3 = epsilon,
w4 = 19/100-epsilon, w6 = 19/200,
w8 = 19/100-epsilon, w9 = epsilon,
w10= epsilon,        w11=19/200.
```

All weights are positive and sum to one.  Exact enumeration of all
independent vertex sets shows their weight is at most `19/50`, while `I`
has exactly that weight.  Thus `I` is maximum.

Relative to `I`, vertices 9 and 10 have one `I`-neighbor and hence type
weight

```text
19/200 = x/4 <= x/3.
```

They are the only low types.  Their total vertex mass is `2epsilon`, which
tends to zero.  Every other outside type has weight `x/2` or `x`.  The
minimum weighted degree is strictly greater than `19/100`, much stronger
than the asymptotic `2/25` bound inherited from minimality.

This family is not claimed to satisfy the dense-half premise and is not a
counterexample.  It proves that a positive-mass amplification cannot follow
from the current local structural constraints.  Any such amplification must
use the dense-half condition globally, which returns us to the missing
stability/discrepancy input above.

## Reproduction

From the repository root:

```powershell
& .\.venv\Scripts\python.exe research/full_solution_scout/erdos128_global_amplification_max_2026-08-03/audit_report.py
```

The checker uses exact rational arithmetic.  It verifies the symbolic
identities in the balanced theorem, the balanced `C_5` minimum, both exact
two-block beta values, and the Chvátal construction (triangle-free,
diameter two, alpha bound, type profile, and degree bound).

## Source and priority boundary

The exact public page was checked on 2026-08-03 and still marked #128 open.
Razborov's 2022 paper proves the conjecture in several regimes but explicitly
leaves the general extension open.  Targeted 2025--2026 searches found no
announcement resolving #128.  This is a priority check, not a novelty claim.
The local source copy used for theorem-number verification is
`razborov_2104.09406.pdf` (SHA-256
`C9FFC6B1ECA473BBE2B405488B60D03369D0160D9FD25533A5DC17616D28D734`).

## Allocation gate

Stop this lane now.  Resume only on one of these events:

1. a proof or counterexample for the full paired-type quotient inequality;
2. a proved stability theorem that supplies its missing global coupling;
3. a construction that passes an exact sparse-half checker.

Do not resume merely to sharpen constants, extend the finite census, or add
another local type lemma.
