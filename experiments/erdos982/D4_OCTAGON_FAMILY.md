# Exact noncyclic equality family for n = 8

Let `a,b` be positive rational numbers with

```text
b < a < 2b,
```

and take the eight vertices

```text
(+/-a,0), (0,+/-a), (+/-b,+/-b).
```

The inequalities are exactly what is needed for these points, in angular
order, to be the vertices of a strictly convex octagon.  They are never
cocircular over the rationals: the axial vertices have squared radius `a^2`
and the diagonal vertices have squared radius `2b^2`, while `a/b = sqrt(2)`
has no positive rational solution.

At an axial vertex the four possible squared distances are

```text
4a^2,
2a^2,
a^2 - 2ab + 2b^2,
a^2 + 2ab + 2b^2.
```

At a diagonal vertex they are

```text
8b^2,
4b^2,
a^2 - 2ab + 2b^2,
a^2 + 2ab + 2b^2.
```

Each listed value occurs either once or twice as dictated by reflection
symmetry.  Put `r=a/b`.  Comparing every pair shows that a collision in the
axial list with `1<r<2` would require

```text
r = (1+sqrt(7))/3,
```

and a collision in the diagonal list in that interval would require

```text
r = -1+sqrt(7).
```

(All other positive roots lie outside the convexity interval.)  In
particular, neither collision is possible for rational `r`.  Thus every
vertex has exactly four distinct distances.  This is an infinite family of
genuinely noncyclic rational polygons attaining the conjectured lower bound
`floor(8/2)=4`; it supplies no counterexample.

For real `r`, one of the two vertex types can have a collision at one of the
two displayed irrational ratios, but those ratios differ.  Hence the maximum
over all vertices is still four throughout the strictly convex family.

The smallest integer member is `a=3,b=2`, independently verified in the
noncyclic exact search output.
