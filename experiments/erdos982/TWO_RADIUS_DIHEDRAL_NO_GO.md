# Two-radius dihedral polygons cannot refute Erdős 982

This note rules out, for every order, the most direct generalization of the
noncyclic `D4` equality octagons.  It is a negative structural result, not a
solution of Erdős problem 982.

## The family and the claim

Fix `m >= 3`, put `theta = pi/m`, and take two interlaced regular `m`-gons

```text
A_j = r (cos(2j theta), sin(2j theta)),
B_j =     (cos((2j+1) theta), sin((2j+1) theta)),   0 <= j < m.
```

The resulting `2m` points form a strictly convex polygon exactly when

```text
cos(theta) < r < sec(theta).
```

Every polygon in this strictly convex family has a vertex that determines at
least `m` distinct distances.  Thus no member is a counterexample to #982.
The statement includes arbitrary real radii, not merely rational or integer
ones.

The two turn determinants, apart from their positive common factors, are

```text
at B_j:  2 r sin(theta) (1 - r cos(theta)),
at A_j:  2   sin(theta) (r - cos(theta)),
```

which proves the convexity interval.  Exchanging the two orbits and rescaling
replaces `r` by `1/r`, so it is enough to consider `1 <= r < sec(theta)`.
The case `r=1` is the regular cyclic `2m`-gon, so assume `r>1` below.

## Exact distance sets

Write `h=floor(m/2)`.  Squared distances within the outer orbit are

```text
R_j = 4 r^2 sin^2(j theta),                 1 <= j <= h,
```

and the common set of squared cross-orbit distances is

```text
C_k = (r-1)^2 + 4r sin^2((k+1/2)theta),    0 <= k < ceil(m/2).
```

The inner-orbit distances are `W_j=4 sin^2(j theta)`, `1<=j<=h`.

### Interlacing lemma

For `0 <= k < h`, with `R_0=0`,

```text
R_k < C_k < R_(k+1).                       (1)
```

Here is a self-contained verification.  Put `q=k theta` and
`u=(2k+1)theta`.  The first difference in (1) is

```text
F(r) = C_k-R_k
     = (2 cos(2q)-1)r^2 - 2 cos(u)r + 1.
```

At the endpoints of `1 <= r <= sec(theta)`,

```text
F(1) > 0,
F(sec(theta)) cos^2(theta)
  = sin(theta)(2 sin(u)-sin(theta)) > 0.
```

Let `alpha=2cos(2q)-1`.  If `alpha<=0`, `F` is concave and its minimum on
the interval is at an endpoint.  Suppose `alpha>0`.  If
`alpha<=cos(u)cos(theta)`, then `F'(sec(theta))<=0`, hence `F` decreases on
the whole interval.  Otherwise, if `cos(u)<=0`, then `F'>0`; and if
`cos(u)>0`, then `cos(u)<=cos(theta)` gives

```text
alpha > cos(u)cos(theta) >= cos^2(u),
```

so the quadratic discriminant is negative.  These cases prove `F>0`.

For the second difference in (1),

```text
G(r) = R_(k+1)-C_k
     = (4 sin^2(q+theta)-1)r^2 + 2 cos(u)r - 1.
```

Again `G(1)>0`, while

```text
G(sec(theta)) cos^2(theta)
  = sin(theta)(2 sin(u)+sin(theta)) > 0.
```

If the quadratic coefficient is nonpositive, concavity reduces the claim to
the endpoints.  If it is positive, the constant term `-1` means that `G`
has exactly one positive root; `G(1)>0` places that root below `1`.  Hence
`G(r)>0` throughout the required interval.  This proves (1).

## Even `m`

When `m` is even, (1) covers every cross-distance class.  The `m/2`
outer-orbit classes and `m/2` cross classes are disjoint, so every outer
vertex already determines `m` distances.

## Odd `m` and the only exceptional radius

Let `m=2h+1`.  The only cross class not covered by (1) is the antipodal one

```text
C_h = (r+1)^2.
```

The largest outer-orbit class is

```text
R_h = 4r^2 cos^2(theta/2).
```

The ordering in (1), together with monotonicity of `C_k`, shows that `C_h`
can meet the outer set only at `R_h`.  Equality occurs at the unique ratio

```text
r_0 = 1/(2 cos(theta/2)-1),
```

which lies strictly between `1` and `sec(theta)`.  At every other ratio the
outer vertex has `m` distinct distances.

At `r=r_0`, the inner vertex has `m` distances.  For `k<h`, monotonicity in
`r` gives `W_k<C_k`.  To prove `C_k<W_(k+1)`, put
`u=(2k+1)theta` and

```text
H(u) = W_(k+1)-C_k
     = 1-r_0^2 + 2(r_0-cos(theta))cos(u) + 2sin(theta)sin(u).
```

On `theta <= u <= pi-2theta`, the nonconstant part of `H` has a unique
critical point and it is a maximum, so the minimum is at an endpoint.  With
`x=cos(theta/2)` and `d=2x-1`, direct factorization gives

```text
d^2 H(theta)
  = -8x^2(x-1)(8x^3-6x+1) > 0,

d^2 H(pi-2theta)
  = -16x^2(x-1)(2x^2-1) > 0.
```

Indeed `sqrt(3)/2 <= x < 1`; both final polynomial factors are positive
(the first equals `1` at `sqrt(3)/2` and is increasing).  Finally,
`C_h=(r_0+1)^2>4>W_h`.  Thus the `h+1` cross classes and `h` inner classes
are disjoint, giving exactly `m` or more distinct distances from an inner
vertex.

`verify_dihedral_algebra.py` checks all displayed symbolic identities.  The
argument above supplies the sign and ordering proof; the script is an audit
aid rather than a substitute for it.
