# Erdos 151: the 24-vertex case

Throughout, a **maximal clique** means
inclusion-maximal, not maximum.  A set is called admissible if it contains no
inclusion-maximal clique of the ambient graph having at least two vertices.
Thus \(\beta(G)\) is the largest cardinality of an admissible set.

## Proposition

Every graph \(G\) of order \(24\) satisfies \(\beta(G)\ge7\).

## Previously established inputs

We use the following earlier results.

1. For every independent set \(I\),
   \[
   \beta(G)\ge |I|+\beta(G-N[I]).                 \tag{R}
   \]
2. The result is already known on every order at most \(22\).
3. \(R(3,5)=14\), \(R(3,6)=18\), \(R(3,7)=23\), and \(R(3,8)=28\).

We first record two elementary facts.  For every vertex \(v\), the open
neighborhood \(N(v)\) is admissible: every clique contained in \(N(v)\)
extends by \(v\), and so is not inclusion-maximal in the ambient graph.
Consequently
\[
                         \beta(Q)\ge\Delta(Q)         \tag{0}
\]
for every graph \(Q\).  Also, beta is additive over components, because the
nontrivial inclusion-maximal cliques of a disjoint union are exactly the
nontrivial inclusion-maximal cliques in its components.

We need one lower bound at order 23 which is weaker than the desired
seven-set statement.

**Lemma 0.** Every graph \(Q\) of order 23 has \(\beta(Q)\ge6\).

**Proof.**  If \(\Delta(Q)\ge6\), use (0).  Otherwise choose any vertex
\(v\).  Since \(d(v)\le5\), the graph \(Q-N[v]\) has between 17 and 22
vertices.  The already proved result through order 22 gives
\(\beta(Q-N[v])\ge5\), and (R) gives
\(\beta(Q)\ge1+5=6\). \(\square\)

This also disposes of disconnected graphs of order 24.  For completeness,
the verified lower bounds through order 22, together with Lemma 0, give the
following coarse table for a nonempty component of order \(m\):
\[
\begin{array}{c|rrrrrr}
m&1\!\!-\!2&3\!\!-\!5&6\!\!-\!8&9\!\!-\!13&14\!\!-\!17&18\!\!-\!23\\
\hline
\text{lower bound on }\beta&1&2&3&4&5&6.
\end{array}                                           \tag{0a}
\]
If a disconnected 24-vertex graph had componentwise lower bounds summing to
at most six, then, using the largest order in each column of (0a), its order
would be at most 19: among partitions of a budget of six into at least two
positive parts, the largest possibility is \(17+2\), corresponding to
\(5+1\).  This is less than 24.  By additivity, every disconnected graph of
order 24 therefore has beta at least seven.

Assume for contradiction that \(G\) is a counterexample of order \(24\).
The preceding paragraph shows that \(G\) is connected.  The exact values
\(R(3,7)=23\) and \(R(3,8)=28\) give \(H(24)=7\), so
\[
\beta(G)\le 6.                                      \tag{1}
\]

## First reductions: regularity, clique size, and bad seven-sets

By (0) and (1), \(\Delta(G)\le6\).  On the other hand, if some vertex \(v\)
had \(d(v)\le5\), then \(G-N[v]\) would have between 18 and 23 vertices.
The verified result through order 22 and Lemma 0 give
\(\beta(G-N[v])\ge6\).  Recurrence (R) would then give
\(\beta(G)\ge1+6=7\), a contradiction.  Therefore \(d(v)\ge6\) for every
\(v\), and
\[
                         G\text{ is 6-regular}.       \tag{2}
\]

In fact
\[
                         \omega(G)\le5.              \tag{2a}
\]
Degree 6 first rules out a clique larger than \(K_7\); if a \(K_7\)
existed, every one of its vertices would use all six incident edges inside
the clique, making it a connected component, contrary to connectedness and
\(|G|=24\).  Now suppose that \(M\cong K_6\), and choose five vertices
\(P\subset M\).  Each member of \(P\) already has five neighbors in \(M\),
so it has at most one neighbor outside \(M\).  Of the 18 vertices outside
\(M\), at least \(18-5=13\) are therefore anticomplete to \(P\).  Two of
those 13 vertices, say \(x,y\), are nonadjacent, since a 13-clique is
incompatible with maximum degree 6.  Then \(P\cup\{x,y\}\) is admissible:
every nontrivial clique it contains lies wholly in \(P\), and hence extends
by the sixth vertex of \(M\).  This contradicts (1), proving (2a).

By (1), every seven-vertex subset of \(V(G)\) contains an
inclusion-maximal clique of \(G\) of size at least two.  Notice that the
clique is maximal in the ambient graph \(G\), not merely in the induced graph
on the seven-set.  We call this the **bad-seven-set property**.

## Common-neighbor cap

Let \(v,x\) be nonadjacent, and put
\[
c(v,x)=|N(v)\cap N(x)|.
\]
For the independent pair \(I=\{v,x\}\), (R) says
\[
\beta(G)\ge2+\beta(G-N[I]).
\]
If \(|G-N[I]|\ge14=R(3,5)\), the already proved lower-order result (or the
definition of the \(h=5\) threshold) gives
\(\beta(G-N[I])\ge5\), contrary to (1).  Hence
\[
|N[I]|\ge 24-13=11.                                \tag{3}
\]
Because \(G\) is 6-regular and \(v x\notin E(G)\), the two closed
neighborhoods each have size seven and their intersection is precisely
\(N(v)\cap N(x)\).  Thus
\[
|N[I]|=|N[v]\cup N[x]|=14-c(v,x).
\]
Together with (3), this gives
\[
                         c(v,x)\le3                 \tag{4}
\]
for every nonedge \(vx\).

## Swap lemma

**Lemma 1 (neighborhood swap).**  If \(v x\notin E(G)\), then
\(c(v,x)\ge1\).  More precisely, there is an inclusion-maximal clique
\(K\) of \(G\) such that
\[
x\in K\subseteq \{x\}\cup N(v),
\qquad
\varnothing\ne K\setminus\{x\}\subseteq N(v)\cap N(x).              \tag{5}
\]
If \(c(v,x)=1\), with \(N(v)\cap N(x)=\{a\}\), then both edges
\(xa\) and \(va\) are inclusion-maximal two-vertex cliques of \(G\), or,
equivalently, neither edge is contained in a triangle.

**Proof.**  Since \(d(v)=6\),
\[
S=\{x\}\cup N(v)
\]
has seven vertices.  The bad-seven-set property supplies an
inclusion-maximal clique \(K\) of \(G\), of size at least two, contained in
\(S\).  If \(x\notin K\), then \(K\subseteq N(v)\), and adjoining \(v\)
would extend \(K\) to a larger clique of \(G\), a contradiction.  Therefore
\(x\in K\).  Every other vertex of \(K\) is adjacent to both \(x\) and
\(v\), proving (5), including \(c(v,x)\ge1\).

If the common-neighbor set is the singleton \(\{a\}\), (5) forces
\(K=\{x,a\}\), so \(xa\) is an inclusion-maximal edge.  Apply the same
argument with \(v\) and \(x\) interchanged to see that \(va\) is also an
inclusion-maximal edge.  An edge is an inclusion-maximal two-clique exactly
when it has no common neighbor, i.e. exactly when it lies in no triangle.
\(\square\)

In particular, every vertex has eccentricity at most two, but we will use the
stronger last assertion of the lemma.

## Exact two-walk count and the local triangle bound

Let \(L\) be the spanning subgraph of \(G\) whose edges are precisely the
edges contained in no triangle of \(G\).  Thus \(E(L)\) is exactly the set of
inclusion-maximal cliques of size two.  Write
\[
t_v=\#\{\text{triangles of }G\text{ containing }v\}
    =e(G[N(v)]),
\qquad
\ell_v=d_L(v).
\]

Fix \(v\).  It has \(24-1-6=17\) nonneighbors.  Count length-two walks
\(v-a-x\) whose endpoint \(x\) is a nonneighbor of \(v\).  For each
\(a\in N(v)\), there are five choices after excluding the return to \(v\),
except that the neighbors of \(a\) lying in \(N(v)\) end at neighbors of
\(v\), not at nonneighbors.  Therefore
\[
\begin{aligned}
\sum_{x\notin N[v]}c(v,x)
 &=\sum_{a\in N(v)}\bigl(5-d_{G[N(v)]}(a)\bigr)\\
 &=30-2e(G[N(v)])\\
 &=30-2t_v.                                           \tag{6}
\end{aligned}
\]
By Lemma 1 and (4), every summand in (6) is one of \(1,2,3\).  Let
\(u_v,q_v,r_v\) be the numbers of the 17 nonneighbors having respectively
one, two, and three common neighbors with \(v\).  Then
\[
u_v+q_v+r_v=17,
\qquad
u_v+2q_v+3r_v=30-2t_v.
\]
Subtracting and eliminating \(q_v\) gives the exact identity
\[
q_v+2r_v=13-2t_v,
\qquad
u_v=4+2t_v+r_v.                                      \tag{7}
\]
In particular,
\[
u_v\ge4+2t_v.                                        \tag{8}
\]

An edge \(va\) belongs to \(L\) exactly when \(v\) and \(a\) have no
common neighbor, which is equivalent to \(a\) being isolated in
\(G[N(v)]\).  Thus \(\ell_v\) is exactly the number of isolated vertices in
the six-vertex graph \(G[N(v)]\).  All \(t_v\) edges of that graph lie among
the other \(6-\ell_v\) vertices, so
\[
t_v\le {6-\ell_v\choose2}.                          \tag{9}
\]

If \(x\) is counted by \(u_v\), let \(a\) be the unique common neighbor of
\(v\) and \(x\).  Lemma 1, in both directions, gives
\(va,ax\in E(L)\).  For a fixed \(a\in N_L(v)\), there are at most
\(\ell_a-1\le5\) possible vertices \(x\in N_L(a)\setminus\{v\}\).
The unique middle vertex makes this assignment injective for the vertices
counted by \(u_v\).  Hence
\[
u_v\le\sum_{a\in N_L(v)}(\ell_a-1)\le5\ell_v.        \tag{10}
\]
Combining (8)--(10),
\[
4+2t_v\le5\ell_v,
\qquad
t_v\le {6-\ell_v\choose2}.                          \tag{11}
\]

We now enumerate the integer \(\ell_v\in\{0,1,\ldots,6\}\).

* \(\ell_v=0\) is impossible by the first inequality in (11).
* If \(\ell_v=1\), the first inequality gives \(t_v=0\); but then all six
  vertices of \(G[N(v)]\) are isolated, so actually \(\ell_v=6\).  Thus
  \(\ell_v=1\) is impossible.
* If \(\ell_v=2\), the first inequality gives \(t_v\le3\).
* If \(\ell_v=3\), the second inequality gives \(t_v\le{3\choose2}=3\).
* If \(\ell_v=4\), the second inequality gives \(t_v\le{2\choose2}=1\).
* If \(\ell_v=5\), the second inequality gives \(t_v=0\), again forcing
  \(\ell_v=6\).
* If \(\ell_v=6\), the second inequality gives \(t_v=0\).

We have proved the key local conclusion
\[
             \boxed{\ t_v\le3\text{ for every }v\in V(G).\ }         \tag{12}
\]

## A triangle-edge-coloring lemma

The following lemma is stated for an arbitrary finite simple graph; it does
not use regularity.

**Lemma 2.**  Let \(Q\) be a finite simple graph in which every vertex lies
in at most three triangles.  Then \(E(Q)\) has a red-blue coloring for which
no triangle of \(Q\) is monochromatic.

**Proof.**  We induct on \(|E(Q)|\).  The edgeless case is immediate.

First suppose that some edge \(e\) of \(Q\) lies in at most one triangle.
The graph \(Q-e\) still satisfies the hypothesis, so color it by induction.
If \(e\) lies in no triangle, give it either color.  If it lies in the unique
triangle whose other two edges are \(f,g\), then, when \(f,g\) have the same
color, color \(e\) with the opposite color; when they have different colors,
give \(e\) either color.  This creates no monochromatic triangle.  This is a
direct induction on the current graph, so there is no issue about an edge
leaving a triangle-support core during repeated deletions.

It remains to treat the case in which every edge of \(Q\) lies in at least
two triangles.  We claim every nontrivial connected component is \(K_4\).
Choose any edge and then a triangle \(abc\) containing it.  Because \(ab\)
lies in a second triangle, there is a vertex \(d\ne c\) such that \(abd\) is
a triangle.  Because \(ac\) lies in a second triangle, there is a vertex
\(e\ne b\) such that \(ace\) is a triangle.  The three triangles
\[
abc,\quad abd,\quad ace
\]
are distinct and all contain \(a\); hence these are all the triangles through
\(a\).

The edge \(ad\) lies in a second triangle \(adz\ne abd\).  Since every
triangle through \(a\) is in the displayed list, \(adz\) must be \(abc\) or
\(ace\).  It cannot be \(abc\), because \(d\notin\{a,b,c\}\).  Therefore it
is \(ace\), forcing \(e=d\) and giving the triangle \(acd\).  At this point
\(a,b,c,d\) induce a \(K_4\) except that we have not yet explicitly invoked
the triangle \(bcd\).

The edge \(bc\) has a second triangle \(bcx\ne abc\), and the edge \(bd\)
has a second triangle \(bdy\ne abd\).  Besides \(abc\) and \(abd\), the two
triangles \(bcx\) and \(bdy\) are triangles through \(b\).  Since \(b\) lies
in at most three triangles, they must be the same triangle.  Equality of
their vertex sets forces \(x=d\) and \(y=c\), so \(bcd\) is a triangle.
Thus all four triangles of the \(K_4\) on \(\{a,b,c,d\}\) occur.

Each of \(a,b,c,d\) already lies in exactly three triangles, all internal to
this \(K_4\).  No triangle can therefore contain one of these vertices and a
vertex outside the \(K_4\).  Moreover, an edge from the \(K_4\) to an outside
vertex would, by the standing case assumption, have to lie in at least two
triangles, which is impossible.  Hence this \(K_4\) is an entire connected
component.  Repeating proves that \(Q\) is a disjoint union of \(K_4\)'s
(and isolated vertices).

Color each \(K_4\) by coloring a perfect matching red and its complementary
four-cycle blue.  Every triangle in that \(K_4\) has exactly one red edge and
two blue edges.  This gives the desired coloring in the remaining case and
completes the induction. \(\square\)

## Ramsey finish

Apply Lemma 2 to \(G\), using (12).  Fix a red-blue coloring of \(E(G)\) with
no monochromatic triangle, and let \(M\) be the spanning graph consisting of
the red edges.  Then

1. \(M\) is triangle-free; and
2. every triangle of \(G\) contains at least one edge of \(M\), because no
   triangle is all blue.

Recall that \(L\) consists of the edges of \(G\) lying in no triangle, and
put
\[
J=L\cup M.
\]
The graph \(J\) is triangle-free.  Indeed, a triangle of \(J\) would also be
a triangle of \(G\).  No edge of a \(G\)-triangle belongs to \(L\), so all
three of its edges would have to belong to \(M\), contrary to the
triangle-freeness of \(M\).

Since \(|J|=24\ge R(3,7)=23\) and \(J\) is triangle-free, \(J\) has an
independent set \(S\) of size seven.  We finally verify admissibility in the
ambient graph \(G\).

* If an inclusion-maximal clique of \(G\) has size two, its edge lies in no
  triangle and therefore belongs to \(L\subseteq J\).  It cannot be contained
  in the \(J\)-independent set \(S\).
* Every clique of size at least three contains a triangle.  Every triangle of
  \(G\) contains an edge of \(M\subseteq J\), so no such triangle, and hence
  no such clique, can be contained in \(S\).

Thus \(S\) contains no inclusion-maximal clique of \(G\) of size at least
two.  It is an admissible seven-set, contradicting \(\beta(G)\le6\).
Therefore no 24-vertex counterexample exists, and every graph of order 24
has beta at least seven. \(\blacksquare\)

## Strong-induction corollary

**Corollary.** Every graph \(Q\) of order at least 24 satisfies
\(\beta(Q)\ge7\).

**Proof.**  The proposition is the base case.  Let \(|Q|=n\ge25\), and
assume the assertion for orders from 24 through \(n-1\).  If
\(\Delta(Q)\ge7\), then the open-neighborhood bound (0) gives
\(\beta(Q)\ge7\).  Otherwise choose any vertex \(v\).  Since \(d(v)\le6\),
the residual graph \(Q-N[v]\) has order at least \(n-7\ge18\).  If its order
is between 18 and 22, the previously verified theorem gives beta at least
six; if its order is 23, Lemma 0 gives beta at least six; and if its order is
at least 24, the induction hypothesis gives beta at least seven.  In every
case \(\beta(Q-N[v])\ge6\).  Recurrence (R) therefore yields
\[
\beta(Q)\ge1+\beta(Q-N[v])\ge7.
\]
This completes the strong induction. \(\square\)

In particular, because \(R(3,8)=28\), the Erdos 151 target is seven on
orders 24, 25, 26, and 27, so the conjectured inequality holds throughout
that interval.
