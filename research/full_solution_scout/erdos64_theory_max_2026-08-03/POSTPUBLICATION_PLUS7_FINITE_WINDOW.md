# The next abundance constant outside a finite equality window

Date: 2026-08-03

Status: **PROVED WITH ONE NAMED EXTERNAL THEOREM**.

Let `G` be a lexicographically minimum counterexample, and use the published
notation `a=|A|`, `d=|D|`.  The published theorem gives `d>=2a+6`.  This note
proves that equality can occur only for eight explicit values of `a`.

The one external input is Theorem 1 of Győri, Li, Salia, Tompkins, Varga and
Zhu, *On graphs without cycles of length 0 modulo 4*, JCTB 176 (2026), 7--29:

```text
e(H) > floor(19(|V(H)|-1)/12)
    ==> H has a cycle of length divisible by four.
```

Primary source: <https://arxiv.org/abs/2312.09999>.

## 1. A twelve-vertex Hamiltonian lemma

### Lemma

Every Hamiltonian graph on twelve vertices with minimum degree at least three
contains a `C4` or a `C8`.

### Proof

Fix a Hamilton cycle and write its vertices cyclically as

```text
E_0,O_0,E_1,O_1,...,E_5,O_5,E_0,                     (1.1)
```

with subscripts modulo six.  Suppose there is no `C4` or `C8`.

A chord whose endpoints cut the Hamilton cycle into arcs of lengths `t` and
`12-t` creates cycles of lengths `t+1` and `13-t`.  Hence a chord cannot have
cyclic distance `3,5,7`, or `9`.  Distances one and eleven are Hamilton-cycle
edges, so every chord joins vertices of the same parity.

Every vertex needs a chord because its degree is at least three.  The even
chords therefore form an edge cover of `{E_0,...,E_5}`, and the odd chords
form an edge cover of `{O_0,...,O_5}`.  From each choose an inclusion-minimal
edge cover.

An inclusion-minimal edge cover is a star forest: every retained edge needs a
private degree-one endpoint.  Its component-order partition is consequently
one of

```text
6,   4+2,   3+3,   2+2+2.                             (1.2)
```

Checking the two Hamilton-cycle arcs between the endpoints of two retained
chords gives the following tiny classification.  The first three partitions
in (1.2) already make a `C4` or `C8`.  In the last partition, precisely these
six perfect matchings can survive within one parity class:

```text
M_0 = 01|23|45,             M_1 = 01|25|34,
M_2 = 03|12|45,             M_3 = 03|14|25,
M_4 = 05|12|34,             M_5 = 05|14|23.           (1.3)
```

Here, for example, `01` denotes the chord `E_0E_1` in the even class or
`O_0O_1` in the odd class.  For completeness, the classification check is as
follows.  Two chords incident with one center, whose other endpoints are at
cyclic distance one or three in `Z_6`, close through (1.1) to a `C4` or `C8`.
Applying this to each star component and then to the two disjoint components
eliminates the partitions `6`, `4+2`, and `3+3`.  Of the fifteen perfect
matchings on six cyclic positions, direct comparison of the two pairs of
intervening arcs eliminates the other nine and leaves exactly (1.3).

It remains to combine an even matching and an odd matching from (1.3).  The
dihedral group of the six positions has three orbits on this list:

```text
{M_0,M_4},   {M_1,M_2,M_5},   {M_3}.
```

Thus it is enough to take the even matching to be `M_0`, `M_1`, or `M_3`.
The following table gives an explicit `C4` or `C8` for every possible odd
matching.  A string lists the cycle in order; its closing edge is implicit.

```text
even | odd M_0                    | odd M_1         | odd M_2
-----+----------------------------+-----------------+-----------------------------
M_0  | E0 O0 O1 E1               | E0 O0 O1 E1    | O1 E2 E3 O2
M_1  | E0 O0 O1 E1               | E0 O0 O1 E1    | E0 O0 E1 O1 E2 E5 O4 O5
M_3  | E0 O0 E1 O1 E2 O2 O3 E3  | E0 E3 O2 O5    | E0 O0 O3 E3

even | odd M_3                    | odd M_4                     | odd M_5
-----+----------------------------+-----------------------------+-----------------
M_0  | E0 O0 E1 O1 E2 E3 O2 O5  | E0 E1 O0 O5                | E0 E1 O0 O5
M_1  | O1 E2 E5 O4               | E0 E1 O0 O5                | E0 E1 O0 O5
M_3  | E0 O0 O3 E3               | E0 O0 E1 O1 O2 E2 E5 O5  | E1 O1 O4 E4
```

Every listed edge is either on (1.1) or belongs to the indicated two
matchings.  This exhausts the cases and contradicts the assumption that both
dyadic lengths are absent.  The lemma follows.  ∎

`audit_hamilton12_lemma.py` independently enumerates the minimal edge covers
and checks the displayed witnesses using only the Python standard library.
It is corroboration, not a premise of the proof.

## 2. Excluding equality for `a=0,1,2`

Assume

```text
d=2a+6.                                                (2.1)
```

Let `x=sum_{v in A}(deg_G(v)-4)`, which is nonnegative.  Then

```text
n=|V(G)|=3a+6,
m=|E(G)|=5a+9+x/2.                                    (2.2)
```

The incidence parity calculation makes `x` even.

- If `a=0`, then `(n,m)=(6,9)`, while the external bound is seven.  A cycle
  divisible by four has length four at this order, contradiction.
- If `a=1`, then `n=9,m>=14`, while the external bound is twelve.  The forced
  divisible-by-four cycle has length four or eight, contradiction.
- If `a=2`, then `n=12,m>=19`, while the external bound is seventeen.  If the
  forced cycle has length four or eight we are done.  The only other option is
  a Hamilton `C12`, and the lemma then again supplies a `C4` or `C8`.

Thus (2.1) is impossible for `a<=2`.

## 3. Combining the small and large ends

`POSTPUBLICATION_SLACK6_KERNEL_GATE.md` proves, from the same named external
theorem plus the incidence-kernel deletion argument, that (2.1) is impossible
for `a>=11`.  Therefore every minimum counterexample satisfies

```text
a<=2 or a>=11  ==>  d>=2a+7.                          (3.1)
```

Equivalently, equality in the published `+6` bound can survive only at

```text
(a,d,n) = (a, 2a+6, 3a+6),   3<=a<=10,               (3.2)
```

namely the eight orders

```text
n in {15,18,21,24,27,30,33,36}.                       (3.3)
```

In particular, for every hypothetical minimum counterexample of order
`n>=37`,

```text
d >= ceil((2n+7)/3),
a <= floor((n-7)/3).                                  (3.4)
```

The remaining obstacle to a universal `+7` theorem is now a finite structural
window, not an unbounded kernel family.  The exploratory exact solvers have
already eliminated the equality cases through `a=2` and all three residual
kernels at `a=6`, but those solver outcomes are not used anywhere in this
proof.
