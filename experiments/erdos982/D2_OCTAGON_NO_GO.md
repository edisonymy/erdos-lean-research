# No `D2`-symmetric octagon refutes Erdős 982

Consider the four-parameter family

```text
(+/-a,0), (0,+/-c), (+/-b,+/-d),
```

with all parameters positive and all eight points in strictly convex
position.  Every such octagon has a vertex determining at least four
distinct distances.  Thus this family cannot refute Erdős problem 982 at
`n=8`.  The argument is exact and covers arbitrary real parameters.

## Normalization and convexity

Interchanging the coordinate axes if necessary gives `a>=c`; rescale so
`a=1`.  In the displayed angular order, strict convexity is equivalent to

```text
0 < b < 1,
0 < d < c <= 1,
d + bc > c.                                      (1)
```

The first two inequalities are the turns at the axial vertices.  The last is
the turn at `(b,d)`.

## If the horizontal axial vertex has four distances, we are done

The four possible squared distances from `(1,0)` are

```text
X1 = 4,
X2 = 1+c^2,
X3 = (1-b)^2+d^2,
X4 = (1+b)^2+d^2.                                (2)
```

Suppose instead that there are at most three distinct values in (2).  We
show that the only possible collision is `X4=X1`.

We have `X1>X2`, `X1>X3`, and `X3<X4`.  Also `X3=X2` would give

```text
d^2 = c^2+2b-b^2 > c^2,
```

contrary to `d<c`.  If `X4=X2`, then

```text
d^2 = c^2-2b-b^2.                                (3)
```

But (1) gives `d>c(1-b)`.  Squaring and using (3) would imply

```text
2+b < c^2(2-b) <= 2-b,
```

which is impossible.  Therefore a low-distance axial vertex forces

```text
X4=X1,  hence  d^2=3-2b-b^2.                    (4)
```

## Five distances from a diagonal vertex already force four classes

At `(b,d)`, consider only the squared distances to the other three diagonal
vertices and to `(1,0),(-1,0)`.  Divide all five squared distances by `4`.
Using (4), the resulting values are

```text
z1 = b^2,
z2 = 3-2b-b^2,
z3 = 3-2b = z1+z2,
z4 = 1-b,
z5 = 1.                                          (5)
```

Because `0<b<1`, the values `z3>1`, `z5=1`, and `0<z4<1` are three distinct
classes.  If (5) had at most three classes, `z1`, which also lies in `(0,1)`,
would have to equal `z4`.  Hence `b^2=1-b`.  Then

```text
z2 = 2-b > 1.
```

This is unequal to `z4` and `z5`, and it is unequal to `z3=z1+z2` because
`z1>0`.  It supplies a fourth class, a contradiction.

Consequently either `(1,0)` itself has at least four distances, or `(b,d)`
does.  This proves the claim.

The height-1000 C# and independent Node searches retained in this directory
are computational stress tests of the same family, not dependencies of this
proof.
