# Erdős 151: the 23-vertex case

Throughout, a **maximal clique** means inclusion-maximal, not maximum.  A set
is called admissible if it contains no inclusion-maximal clique of the
ambient graph having at least two vertices.  Thus

\[
\beta(G)=\max\{|S|:S\subseteq V(G)\text{ is admissible}\}.
\]

## Proposition

Every graph \(G\) of order \(23\) satisfies \(\beta(G)\ge 7\).

## Previously established inputs

We use the following earlier results.

1. For every independent set \(I\),
   \[
   \beta(G)\ge |I|+\beta(G-N[I]).                 \tag{R}
   \]
2. The target inequality is already proved through order \(22\).
3. \(R(3,6)=18\), \(R(3,7)=23\), and \(R(3,8)=28\).
4. A smallest counterexample is connected.  This follows from the
   additivity of \(\beta\) over components and the subadditivity of \(H\), as
   proved in the main [proof note](proof.md).

Assume for a contradiction that a 23-vertex graph \(G\) has
\(\beta(G)\le6\).  The two consecutive Ramsey values give \(H(23)=7\), so
this would be the first possible counterexample after the verified result
through order 22.  Hence \(G\) is connected by input 4.

For every vertex \(v\), its open neighborhood \(N(v)\) is admissible: every
clique contained in \(N(v)\) extends by \(v\).  Hence
\(\beta(G)\ge\Delta(G)\), and therefore \(\Delta(G)\le6\).  If some vertex
had degree at most four, then \(G-N[v]\) would have between 18 and 22
vertices.  The established lower-order result would give
\(\beta(G-N[v])\ge6\), and (R) would give \(\beta(G)\ge7\).  Consequently

\[
                         5\le d(v)\le6             \tag{1}
\]

for every vertex \(v\).

Moreover,

\[
                         \omega(G)\le5.             \tag{2}
\]

A \(K_7\) would be a component because every one of its vertices would use
all six incident edges inside the clique.  If \(M\cong K_6\), choose five
vertices \(P\subset M\).  Each member of \(P\) has at most one neighbor
outside \(M\), so at least 12 of the 17 outside vertices are anticomplete to
\(P\).  Two of those 12 are nonadjacent, since the maximum degree is six.
Together with \(P\), they form an admissible seven-set: every clique in
\(P\) extends by the omitted member of \(M\), and there is no nontrivial
mixed clique.  This contradicts \(\beta(G)\le6\), proving (2).

The assumption \(\beta(G)\le6\) also has the following useful form:

> **Bad-seven-set property.** Every seven-vertex subset contains a
> nontrivial inclusion-maximal clique of the ambient graph \(G\).

## The neighborhood-swap fact

For nonadjacent vertices \(v,x\), write

\[
c(v,x)=|N(v)\cap N(x)|.
\]

**Lemma 1.** If \(d(v)=6\) and \(vx\notin E(G)\), then \(c(v,x)\ge1\).  If
\(c(v,x)=1\), with unique common neighbor \(a\), then \(xa\) is an ambient
maximal edge, equivalently an edge lying in no triangle.  If \(d(x)=6\) as
well, then \(va\) is also an ambient maximal edge.

**Proof.** The set \(N(v)\cup\{x\}\) has seven vertices.  A nontrivial
ambient maximal clique inside it cannot lie wholly in \(N(v)\), because
\(v\) would extend it.  It must therefore contain \(x\), and every other
member is a common neighbor of \(v\) and \(x\).  This proves
\(c(v,x)\ge1\).  If \(a\) is the unique common neighbor, the supplied
maximal clique can only be the edge \(xa\).  When \(x\) also has degree six,
interchanging \(v\) and \(x\) proves that \(va\) is maximal as well.
\(\square\)

The last interchange is used only when both endpoints have degree six.

## Reduction to a Ramsey-minimal subgraph

It is enough to find a red-blue coloring of \(E(G)\) with no monochromatic
triangle.  Indeed, let \(L\) consist of the edges of \(G\) which lie in no
triangle, let \(M\) be the graph of red edges, and put

\[
J=L\cup M.
\]

The graph \(J\) is triangle-free.  A triangle in \(J\) would be a triangle
of \(G\), so none of its edges could belong to \(L\); all three would then
be red.  Since \(|J|=23=R(3,7)\), the graph \(J\) has an independent
seven-set \(S\).  The set \(S\) contains no ambient maximal edge, because
all such edges belong to \(L\).  It contains no clique of size at least
three, because every triangle has a red edge.  Thus \(S\) is admissible,
contrary to \(\beta(G)\le6\).

Suppose, then, that \(G\) has no such edge-coloring, and choose a
subgraph-minimal \((3,3)\)-Ramsey graph \(Q\subseteq G\).  Thus every proper
subgraph of \(Q\) does have a red-blue coloring with no monochromatic
triangle.

We use Brooks' theorem in its standard exact form: if a connected simple
graph \(A\) has maximum degree \(D\), then \(\chi(A)\le D\), unless \(A\)
is a complete graph or an odd cycle.  The original reference is R. L.
Brooks, “On colouring the nodes of a network,” *Proceedings of the Cambridge
Philosophical Society* 37 (1941), 194–197,
[doi:10.1017/S030500410002168X](https://doi.org/10.1017/S030500410002168X).

Every \((3,3)\)-Ramsey graph has chromatic number at least six.  Otherwise,
pull back along a proper five-coloring the red-blue coloring of \(K_5\) in
which a five-cycle is red and its complementary five-cycle is blue.  Every
triangle maps to three distinct colors and hence is nonmonochromatic.

The graph \(Q\) is connected.  If it were disconnected, either one component
would be a proper Ramsey subgraph, or valid colorings of all components could
be combined.  Brooks' theorem, (1), and (2) now give

\[
                         \chi(Q)=6,\qquad\Delta(Q)=6.                \tag{3}
\]

Indeed, \(\Delta(Q)\le5\) would make \(Q\) five-colorable; the relevant
complete exception would be the forbidden \(K_6\), and an odd cycle is not
six-chromatic.  Conversely, Brooks gives \(\chi(Q)\le6\), since \(K_7\) is
forbidden.

Every edge of \(Q\) lies in at least two triangles of \(Q\).  Otherwise,
color \(Q-e\) without a monochromatic triangle.  If \(e\) lies in no
triangle, color it arbitrarily.  If it lies in one triangle, color it
opposite to the common color of the other two edges when those colors agree,
and arbitrarily when they differ.  This extends the coloring to \(Q\), a
contradiction.

Choose \(v\) with \(d_Q(v)=6\).  Since \(Q\subseteq G\) and
\(\Delta(G)=6\), all six edges incident with \(v\) in \(G\) belong to
\(Q\).  For each \(a\in N_Q(v)\), the edge \(va\) lies in at least two
\(Q\)-triangles.  Consequently the six-vertex link \(Q[N_Q(v)]\) has
minimum degree at least two.

**Lemma 2.** The link \(Q[N_Q(v)]\) has at least seven edges.  Equivalently,
\(v\) lies in at least seven triangles of \(Q\).

**Proof.** If the link had at most six edges, minimum degree two would force
it to have exactly six edges and to be 2-regular.  It would be either
\(C_6\) or \(2C_3\).  Color \(Q-v\) without a monochromatic triangle.

If the link is \(C_6\), color the six spokes at \(v\) alternately red and
blue.  Every triangle through \(v\) then has differently colored spokes.

If the link is \(2C_3\), consider each component separately.  Its three
link edges are not monochromatic.  When two are red and one is blue, color
the spoke to the common endpoint of the two red edges blue, and color the
other two spokes red.  All three new triangles are nonmonochromatic.  Reverse
the colors when two link edges are blue.  The two components have no link
edges between them, so these choices combine.

Either construction extends the coloring to \(Q\), a contradiction.
\(\square\)

## Exact two-walk equality

Let

\[
s=|N_G(v)\cap V_6|,
\qquad
t=e(G[N_G(v)]),
\]

where \(V_6\) is the set of degree-six vertices of \(G\).  The vertex \(v\)
has 16 nonneighbors.  Counting nonbacktracking length-two walks from \(v\)
gives

\[
\begin{aligned}
\sum_{x\notin N_G[v]}c(v,x)
  &=\sum_{a\in N_G(v)}(d_G(a)-1)-2e(G[N_G(v)])\\
  &=24+s-2t.                                         \tag{4}
\end{aligned}
\]

By Lemma 1, all 16 summands are at least one.  Lemma 2 gives \(t\ge7\),
while \(s\le6\).  Thus equality holds throughout:

\[
t=7,\qquad s=6,\qquad
c(v,x)=1\quad\text{for every }x\notin N_G[v].       \tag{5}
\]

All six neighbors of \(v\) therefore have degree six.  There is no
degree-six nonneighbor \(x\).  If there were one, let \(a\) be its unique
common neighbor with \(v\).  Lemma 1, applied with \(x\) as the degree-six
root, would make \(va\) an ambient maximal edge.  But \(va\in E(Q)\), and
every edge of \(Q\) lies in at least two \(Q\)-triangles.  This is
impossible.  Hence the degree-six vertices of \(G\) are exactly

\[
                         N_G[v],                    \tag{6}
\]

a set of seven vertices.

Furthermore, \(v\) is the unique degree-six vertex of \(Q\).  If another
vertex \(w\) had \(d_Q(w)=6\), the same argument centered at \(w\) would
show that its six \(G\)-neighbors are the other six degree-six vertices.
Since \(w\in N_G(v)\), it would have degree five in the link
\(G[N_G(v)]\).  Each of the other five vertices of that link has link degree
at least two, because every edge incident with \(v\) in \(Q\) lies in at
least two triangles.  The link degree sum would be at least

\[
5+5\cdot2=15,
\]

contradicting (5), which says that the link has seven edges and degree sum
14.

## Critical-graph finish

Choose a 6-critical subgraph \(H\subseteq Q\): \(\chi(H)=6\), and every
proper subgraph is five-colorable.  In particular \(\delta(H)\ge5\).  Since
\(v\) is the only degree-six vertex of \(Q\), Brooks' theorem forces
\(v\in V(H)\) and \(d_H(v)=6\).  Otherwise \(\Delta(H)\le5\), which would
make \(H\) five-colorable unless it were a \(K_6\), forbidden by (2).  Every
other vertex of \(H\) consequently has degree exactly five.

We use Gallai's low-vertex theorem in the following exact form:

> In a \(k\)-critical graph, the subgraph induced by the vertices of degree
> \(k-1\) is a Gallai forest: every block is a complete graph or an odd
> cycle.

Here \(k\)-critical means that the chromatic number is \(k\) and every
proper subgraph has smaller chromatic number; bridges count as \(K_2\)
blocks.  The source is Satz E.1 of T. Gallai, “Kritische Graphen, I,”
*A Magyar Tudományos Akadémia Matematikai Kutató Intézetének Közleményei*
8(1--2) (1963), 165–192,
[repository record](https://real.mtak.hu/201435/).

Apply the theorem with \(k=6\).  The degree-five vertices induce

\[
F=H-v.
\]

Let \(X=N_H(v)\).  The six members of \(X\) have degree four in \(F\), and
every other vertex of \(F\) has degree five.  Therefore

\[
\delta(F)\ge4,\qquad |X|=6,\qquad\omega(F)\le5.     \tag{7}
\]

Consider a connected component of the Gallai forest \(F\).  If it has more
than one block, its block-cut tree has at least two leaf blocks.  A leaf
block cannot be an odd cycle, because each of its non-cut vertices would
have degree two in \(F\).  If it is a complete graph \(K_r\), a non-cut
vertex has degree \(r-1\) in \(F\); (7) forces \(r\ge5\), while
\(\omega(F)\le5\) forces \(r=5\).  Thus every leaf block is a \(K_5\), and
its four non-cut vertices all have degree four in \(F\), hence belong to
\(X\).  Two distinct leaf blocks contribute eight distinct members of
\(X\), contradicting \(|X|=6\).  No component can have more than one block.

Each component is therefore a single block.  It cannot be an odd cycle by
\(\delta(F)\ge4\), and the same degree and clique bounds make it a \(K_5\).
Every component contributes exactly five degree-four vertices, all in
\(X\), which is impossible because \(|X|=6\) is not a multiple of five.

This contradiction proves that \(G\) has a red-blue edge-coloring without a
monochromatic triangle.  The Ramsey reduction then supplies an admissible
seven-set, contradicting \(\beta(G)\le6\).  Therefore every graph of order
23 has beta at least seven. \(\blacksquare\)

## Consequence and scope

The strong-induction corollary in the separately proved
[24-vertex case](order24.md) establishes \(\beta(G)\ge7\) for every graph of
order at least 24.  Together with the proposition above, this gives

\[
\boxed{\ \beta(G)\ge7\text{ for every graph of order }n\ge23.\ }
\]

In particular, since \(R(3,8)=28\), the Erdős 151 inequality holds through
order 27.  This is not a full solution of Erdős 151: for larger orders the
target \(H(n)\) eventually exceeds seven.

The proof of the 23-vertex proposition is analytic.  It uses no SAT result
or finite graph enumeration; its external graph-theoretic inputs are stated
above.
