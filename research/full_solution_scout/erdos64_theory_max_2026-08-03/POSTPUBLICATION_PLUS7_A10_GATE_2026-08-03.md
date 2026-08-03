# Excluding the top order of the slack-six equality window

Date: 2026-08-03

Status: **PROVED WITH ONE NAMED EXTERNAL THEOREM AND AN EXACT FINITE
CERTIFICATE**.  The certificate has an independent standard-library replay;
the Z3 producer is corroboration only.

This note is independent of the order-28 marked-cubic seed computations.  It
uses the incidence-kernel equality decomposition and excludes `a=10` from the
finite equality window.

## 1. Statement

Let `G` be the lexicographically minimum counterexample and retain the notation
of the published incidence-kernel packet.  Then

```text
d=2a+6  ==>  a<=9.                                    (1.1)
```

Together with the already proved exclusion for `a<=2`, equality can survive
only for

```text
3<=a<=9,
n=3a+6 in {15,18,21,24,27,30,33}.                    (1.2)
```

Consequently every hypothetical minimum counterexample of order `n>=34`
satisfies

```text
d>=2a+7,
d>=ceil((2n+7)/3),
a<=floor((n-7)/3).                                    (1.3)
```

The named external input remains Theorem 1 of Gyori, Li, Salia, Tompkins,
Varga and Zhu, *On graphs without cycles of length 0 modulo 4*, JCTB 176
(2026), 7--29, as quoted and audited in the preceding finite-window packet.

## 2. Equality arithmetic at `a=10`

Under `d=2a+6`, put

```text
q=2a-|E(J)|.
```

The proved equality collapse for `a>=6` leaves only

```text
q=5: d0=1, d1=10;
q=6: d0=0, d1=12.                                    (2.1)
```

The deficit-five kernel theorem gives `|V(J)|<=8`, so the first line is
impossible when `a=10`.  Hence necessarily

```text
q=6, |V(J)|=10, |E(J)|=14,
d0=0, d1=12, d2=14.                                  (2.2)
```

Every high vertex has degree exactly four.  Thus `Delta(J)<=4`, and the
number of `D1` vertices colored by `v in V(J)` is exactly

```text
c(v)=4-deg_J(v).                                      (2.3)
```

The proved deficit argument makes `J` connected.  It also has minimum degree
at least two: a degree-one vertex could be deleted to leave a nine-vertex,
thirteen-edge deficit-five kernel, already excluded by the divisible-by-four
extremal theorem.  Finally, `J` is 2-degenerate and has no `C4` or `C8`.

## 3. Exact derivation of the four kernels

The independent auditor asks nauty `geng` for precisely the connected simple
graphs with

```text
n=10, m=14, 2<=delta<=Delta<=4.                       (3.1)
```

It independently parses graph6, peels for 2-degeneracy, and searches for
literal `C4` and `C8`.  The exact filter counts are

```text
raw geng records                         4,502
2-degenerate                             4,427
then C4-free                               124
then C8-free                                 4.       (3.2)
```

The four canonical graph6 records are

```text
I?`D@`keO
I?`D@pScg
I?`DCdcMG
I?`@dEWR_                                            (3.3)
```

All four have degree sequence

```text
2,2,2,2,3,3,3,3,4,4.                                (3.4)
```

The raw graph6 stream has SHA-256

```text
90CE9D2B9ECDD374594F91D5DEAC93B2BFE6C73CB6DE3DB1547BEC512621EE0F.
```

The `geng.exe` used has SHA-256

```text
64FA2D95BDAFF155CE0FC748D4CBA83A50E5FFB03E3ACC5F41D86581C0BBA7EF.
```

This independently reproduces the four `a=10,q=6` records in the earlier
37-kernel table.

## 4. The residual topology quotient

Put `R=G[D]`.  In the present branch, every `D2` vertex has degree one in
`R`, every `D1` vertex has degree two, and there is no `D0` vertex.  Therefore
`R` is a disjoint union of paths and cycles.  Every path has two `D2`
endpoints and only `D1` internal vertices; every cycle consists only of
`D1` vertices.  Since there are fourteen `D2` vertices, there are exactly
seven path components.

Write

```text
lambda_1<=...<=lambda_7
```

for the numbers of internal `D1` vertices on the seven paths, and write
`mu_1<=...<=mu_s` for the lengths of the `D1`-only cycles.  Simplicity gives
`mu_j>=3`, while `mu_j=4,8` is already forbidden.  The complete topology set
is therefore

```text
lambda_i>=0,
mu_j in {3,5,6,7,9,10,11,12},
sum_i lambda_i + sum_j mu_j = 12.                     (4.1)
```

Independent enumeration gives exactly 166 topologies.  Their canonical JSON
SHA-256 is

```text
A12E2D3EC56B46898D04335ED3F60418908C71269AAE8F1CFC16F3D56D426FC2.
```

The Z3 producer and the independent combinations-with-replacement/partition
enumerator give the same count and hash.

## 5. One-segment closure lemma

Form the fixed incidence skeleton `K` on `A union D2`: each kernel edge is
subdivided by its assigned `D2` vertex.  When a `D1` endpoint of color `v` is
under discussion, include its fixed leaf edge to `v`.

### Lemma 5.1

Let `Q` be any subpath of an `R` component whose endpoints lie in
`D1 union D2` and whose internal vertices lie in `D1`.  Let `P` be a simple
path in the corresponding fixed skeleton between the same endpoints.  Then

```text
|E(P)|+|E(Q)| notin {4,8,16,32}.                      (5.1)
```

### Proof

The internal vertices of `Q` are all in `D1`.  The internal vertices of `P`
are in `A union D2`; endpoint leaf vertices are used only as the endpoints of
`P`.  Thus `P` and `Q` are internally vertex-disjoint.  This remains true if
`P` passes through a `D2` endpoint belonging to some other portion or component
of `R`, because that vertex is not internal to `Q`.  If both endpoints of `Q`
are `D2`, simplicity of `P` keeps them out of its interior.  Hence `P union Q`
is a simple cycle of length `|E(P)|+|E(Q)|` in `G`.  At order 36 the relevant
dyadic lengths are exactly `4,8,16,32`, proving (5.1).  QED

This lemma is only a necessary condition, but that is enough: the certificate
shows that even this relaxation has no assignment.

## 6. Exact CSP semantics

For a topology (4.1), an assignment consists of

1. a bijection from the fourteen kernel edges / `D2` labels to the fourteen
   oriented path-end slots; and
2. a color on each of the twelve internal/cyclic `D1` positions, with exact
   multiplicities (2.3).

These data construct `R` uniquely after harmless labels are assigned to the
`D1` vertices.  Conversely, orienting and ordering the components of any
actual `R` produces such an assignment.  Thus every actual equality residual
appears in the assignment space.

For each pair of positions on one `R` segment, the certificate independently
enumerates every simple path between their endpoint types in the literal
subdivided skeleton `K`.  It rejects the endpoint/color pair exactly when one
of those fixed paths, together with the `R` segment, has a length in
`{4,8,16,32}`.  By Lemma 5.1 every rejection is necessary for an actual
dyadic-free equality graph.

The independent replay does not use Z3.  It summarizes each locally legal
component by

```text
(set of D2 endpoint labels, color-count vector),      (6.1)
```

then performs exact set-packing dynamic programming: endpoint sets must be
disjoint and cover all fourteen labels, while the color-count vectors must sum
to (2.3).  Collapsing a component to (6.1) is exact because different `R`
components have no shared segment constraint.

## 7. Finite certificate

For kernels 0 and 1 in (3.3), the numbers of component signatures are

```text
path internal D1 count:    0    1    2    3,...,12
number of signatures:     91    8   25         0
every allowed cycle length:                         0. (7.1)
```

For kernels 2 and 3 they are

```text
path internal D1 count:    0    1    2    3,...,12
number of signatures:     91    0   20         0
every allowed cycle length:                         0. (7.2)
```

Thus all 166 topologies reduce immediately to the following packing cases:

```text
kernels 0,1: (0,2,2,2,2,2,2) or (1,1,2,2,2,2,2);
kernels 2,3: (0,2,2,2,2,2,2) only.                  (7.3)
```

There is a short transparent final obstruction.  For kernel 0 every legal
length-one path uses the same two `D2` endpoint labels `{0,13}`; for kernel 1
the corresponding pair is `{1,9}`.  Hence two vertex-disjoint length-one paths
cannot occur, eliminating the second topology in (7.3).  Kernels 2 and 3 have
no legal length-one signature at all.

It remains only `(0,2,2,2,2,2,2)`.  But the color supports of all legal
length-two signatures are

```text
kernel 0: {0,1,2,4,5,7}, missing required colors {3,6};
kernel 1: {0,1,3,5,6,7}, missing required colors {2,4};
kernel 2: {0,1,2,5,6,7}, missing required colors {3,4};
kernel 3: {0,1,4,5,7,8}, missing required colors {2,3}. (7.4)
```

Every displayed missing color has positive multiplicity in (2.3), while all
twelve `D1` vertices of the remaining topology would lie on length-two paths.
This is impossible.  The exact set-packing DP independently reaches the same
conclusion; its numbers of replayed transitions are respectively

```text
1,672, 1,672, 960, 960.                              (7.5)
```

The independent output status is

```text
VERIFIED_COMPLETE_NO_ASSIGNMENT.                     (7.6)
```

The producer checked all `4*166=664` kernel-topology cases; every result is
`UNSAT`, and the maximum number of lazy full-cycle iterations is zero.  In
other words, the independently audited one-segment clauses alone prove the
exclusion.

## 8. Artifacts and reproducibility

The authoritative replay is

```text
audit_a10_residual_gate_2026-08-03.py
  58C9CD0A105D593D9007D062617A48313E823380512F7942E6782E91F2DB42E5

audit_a10_residual_gate_2026-08-03.json
  F3E39B881120A2B0FFDD7BCFE76E6778FDD2A38D2D3F66AE59745367E4767A25
```

The JSON output is byte-reproducible on consecutive replays.  Its four
component-signature hashes bind the exact local tables.  The exploratory Z3
producer is `residual_topology_cegar_2026-08-03.py`; it is not a premise of
the theorem.

Reproduction command (PowerShell):

```powershell
python audit_a10_residual_gate_2026-08-03.py `
  --geng 'C:\path\to\geng.exe' `
  --output audit_a10_residual_gate_2026-08-03.json
```

## 9. Scope

This is an exact exclusion of the `a=10` equality layer, not a universal
`+7` theorem.  The remaining equality window is `3<=a<=9`.  No conclusion
from the marked order-28 induced-boundary closure is used here.
