# Root hostile audit: the `+7` bound outside a finite window

Date: 2026-08-03

## Verdict

**PASS for the stated scope.**  The argument in
`POSTPUBLICATION_SLACK6_KERNEL_GATE.md` and
`POSTPUBLICATION_PLUS7_FINITE_WINDOW.md` proves, using one named external
theorem, that every lexicographically minimum counterexample satisfies

```text
a <= 2 or a >= 11  ==>  d >= 2a+7.
```

Equivalently, equality in the published `d>=2a+6` theorem can survive only
for `a=3,...,10`, hence only at orders

```text
15, 18, 21, 24, 27, 30, 33, 36.
```

In particular, every hypothetical minimum counterexample of order at least
37 satisfies

```text
d >= ceil((2n+7)/3),       a <= floor((n-7)/3).
```

This is still a necessary condition, not a resolution of Erdős problem #64.

## External source check

The load-bearing source was downloaded directly from arXiv as
`arXiv:2312.09999v1`.  The downloaded PDF has SHA-256

```text
8C2FBD4C6FDC60DF60A3661A4D89A892A6281913E7FAA1530B61E57A0E04C9C0.
```

Theorem 1 in that primary PDF states exactly that an `n`-vertex graph with
more than

```text
floor(19(n-1)/12)
```

edges contains a cycle of length `0 mod 4`.  The paper is E. Győri,
B. Li, N. Salia, C. Tompkins, K. Varga and M. Zhu, *On graphs without
cycles of length 0 modulo 4*, arXiv:2312.09999; the journal record is JCTB
176 (2026), 7--29.  The theorem direction, strict inequality, floor, and
all-`n` quantifier agree with the campaign note.

## Slack-six kernel gate

Under the candidate equality `d=2a+6`, the independently re-derived
identities are

```text
x+y=12,
d_2=2a-6+x+d_0,
q=2a-d_2=6-x-d_0,
d_1=12-x-2d_0.
```

For `a>=6`, the published kernel edge bound gives `q>=5`.  Since `x` is
even, the only possibilities are

```text
q=6: x=0, d_0=0, d_1=12;
q=5: x=0, d_0=1, d_1=10.
```

The deletion propagation was checked component by component:

- a disconnected deficit-five graph has order at most four;
- a deficit-five graph of order at least seven has no degree-one vertex,
  so 2-degeneracy supplies a degree-two deletion preserving deficit five;
- a disconnected deficit-six graph has order at most six;
- after excluding deficit five from order nine upward, a deficit-six graph
  of order at least eleven has no degree-one vertex and similarly deletes.

Thus orders 9 and 11 are valid finite bases.  The external theorem gives
`13>floor(19*8/12)=12` and `16>floor(19*10/12)=15`; the resulting cycles
divisible by four can only have length 4 or 8.  Therefore `q=5` forces
`a<=8`, `q=6` forces `a<=10`, and equality is impossible for `a>=11`.

The separate `geng`/graph6/Held--Karp audit reproduces the two finite-base
consequences.  It is corroboration and is not used above.

## Small-end arithmetic

Under equality,

```text
n=3a+6,       m=5a+9+x/2,
```

with even `x>=0`.  At `a=0,1`, the external theorem forces a `C4` or `C8`
immediately.  At `a=2`, it forces a `C4`, `C8`, or Hamiltonian `C12`; only
the last case needs the twelve-vertex lemma.

## Hostile audit of the Hamiltonian lemma

The proof correctly observes that every non-Hamilton-cycle chord joins two
vertices of the same parity.  An inclusion-minimal chord edge cover in each
parity class is a star forest with component partition

```text
6, 4+2, 3+3, or 2+2+2.
```

I replayed the standard-library enumerator.  It found 15, 150, and 6
minimal edge covers of sizes 3, 4, and 5 respectively, and exactly the six
claimed perfect matchings survive the single-parity `C4/C8` test.  All 36
ordered pairs of surviving even/odd matchings contain a `C4` or `C8`.

I also encoded the eighteen cycles printed in the proof table separately
from the enumerator.  Every row has distinct vertices, length four or eight,
and every edge is either on the fixed Hamilton cycle or in the indicated
pair of matchings: `18/18 PASS`.

## Boundary

No argument here eliminates equality for `a=3,...,10`.  Solver exploration
of the residual 37 kernels is not a premise and currently carries no global
certificate.  A universal `+7` claim therefore remains unavailable.
