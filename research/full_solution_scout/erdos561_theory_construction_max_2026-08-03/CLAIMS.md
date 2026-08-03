# Claim ledger — Erdős #561 construction lane

Date: 2026-08-03

## C0. Faithful statement and selected tuple

For descending positive sequences \(a=(a_1,\ldots,a_s)\) and
\(b=(b_1,\ldots,b_t)\), put

\[
F(a)=\bigsqcup_i K_{1,a_i},\qquad
F(b)=\bigsqcup_j K_{1,b_j},\qquad
\ell_k=\max_{i+j=k}(a_i+b_j-1).
\]

Erdős #561 asks for the universal equality

\[
\widehat r(F(a),F(b))=\sum_{k=2}^{s+t}\ell_k.
\]

The construction lane selected

\[
a=(3,2),\qquad b=(2,1),\qquad
(\ell_2,\ell_3,\ell_4)=(4,3,2),
\]

so the conjectured value is 9.  This tuple is nonuniform on both sides.  It
does not meet any of the special-case hypotheses listed in the live problem
page, Cheng's tail-one family, or the current uniform-only 2026 preprint.
That observation is a screening statement, not a definitive novelty claim;
the separate priority audit remains authoritative.

## C1. Exact embedding criterion — proved

Let \(H\) be a graph and let \(d_1,\ldots,d_s\) be positive integers.  Fix
distinct proposed centres \(c_1,\ldots,c_s\).  Then \(H\) contains
vertex-disjoint stars of leaf-degrees \(d_1,\ldots,d_s\) with those centres
if and only if, for every \(I\subseteq[s]\),

\[
\left|\bigcup_{i\in I}\bigl(N_H(c_i)\setminus
\{c_1,\ldots,c_s\}\bigr)\right|
\mathrel{\geq}\sum_{i\in I}d_i.
\]

Proof: replace centre \(c_i\) by \(d_i\) identical demand slots and apply
Hall's marriage theorem to the bipartite graph from these slots to potential
leaves.  This is both necessary and sufficient, because an embedding of a
star forest is not required to be induced.

For two stars of degrees \(p,q\), this reduces to three inequalities for an
ordered pair of distinct centres \(x,y\):

\[
|N(x)\setminus\{y\}|\geq p,\quad
|N(y)\setminus\{x\}|\geq q,\quad
|(N(x)\cup N(y))\setminus\{x,y\}|\geq p+q.
\]

## C2. Eight-edge matching lemma — proved

**Lemma.** If \(G\) is a simple graph with at most eight edges and
\(\Delta(G)\leq3\), then \(G\) has a matching that saturates every
degree-three vertex.

**Proof.** Let \(S\) be the set of degree-three vertices, \(r=|S|\), and
\(H=G[S]\).  Since \(3r\leq2e(G)\leq16\), we have \(r\leq5\).

- For \(r\leq2\), the claim is immediate: use the edge between the two
  vertices if it exists, and otherwise choose distinct incident neighbours.
- For \(r=3\), if \(H\) has an edge, match its endpoints and match the third
  vertex to a neighbour outside those endpoints.  If \(H\) has no edge,
  the three degree-three neighbourhoods satisfy Hall's condition: every one
  has size 3, every pair has union size at least 3, and the union of all
  three has size at least 3.
- For \(r=4\), the number of edges of \(G\) incident with \(S\) is
  \(3r-e(H)=12-e(H)\), so \(e(H)\geq4\).  Any four-edge graph on four
  vertices has a matching of size two: a pairwise-intersecting family of
  edges on four vertices is a star or triangle and has size at most three.
- For \(r=5\), the same count gives \(e(H)\geq7\).  Since
  \(\Delta(H)\leq3\), necessarily \(e(H)=7\), exactly one edge leaves
  \(S\), and the degree sequence of \(H\) is \((3,3,3,3,2)\).  Let \(v\)
  be the degree-two vertex, incident with the unique external edge \(vw\).
  The complement of \(H\) on \(S\) has degree sequence
  \((2,1,1,1,1)\), hence is \(P_3\sqcup K_2\), with \(v\) the centre of
  the \(P_3\).  Therefore \(H-v=K_4-e\) has a perfect matching.  Add
  \(vw\) to it.

In every case the resulting matching saturates \(S\). ∎

## C3. Exact value for one asymmetric tuple — proved, priority pending

\[
\boxed{\widehat r(K_{1,3}\sqcup K_{1,2},
                   K_{1,2}\sqcup K_{1,1})=9.}
\]

**Lower bound.** Let \(e(G)\leq8\).

- If \(\Delta(G)\geq4\), choose a vertex \(v\) of degree at least four,
  color every edge incident with \(v\) blue, and every other edge red.  The
  blue graph is a star, so it has no
  \(K_{1,2}\sqcup K_{1,1}\).  The red graph has at most four edges, so it
  has no \(K_{1,3}\sqcup K_{1,2}\), which needs five edges.
- If \(\Delta(G)\leq3\), use C2 to choose a matching \(M\) saturating all
  degree-three vertices.  Color \(M\) blue and all other edges red.  Blue
  has no \(K_{1,2}\), while the red maximum degree is at most two and hence
  red has no \(K_{1,3}\).

Thus no graph with at most eight edges arrows the ordered pair.

**Upper bound.** The standard formula host

\[
K_{1,4}\sqcup K_{1,3}\sqcup K_{1,2}
\]

has nine edges and arrows the pair.  Directly, if a blue color class avoids
\(K_{1,2}\sqcup K_{1,1}\), then either every component has at most one
blue edge, leaving red stars of degrees at least 3 and 2 in the first two
components, or all blue edges lie in one component, leaving the other two
components completely red.  Either way red contains
\(K_{1,3}\sqcup K_{1,2}\).  The independent checker also tested all 512
colorings.

This is a **single positive special case**, not a full resolution or a
counterexample to Erdős #561.  It must not be announced as new until the
priority audit establishes that the exact tuple is absent from prior work.

## C4. Negative construction evidence — computationally checked

- The named-family sweep generated 180 connected and 1,123 disconnected
  named hosts from complete bi/multipartite graphs, theta graphs, paths,
  cycles, wheels, fans, windmills, clique-plus-leaf graphs, and bounded
  disjoint unions.  Across the first 20 conservatively filtered tuples
  through formula bound 13, it found no below-bound arrowing host.  This was
  not an exhaustive graph catalogue.
- For \((3,2)\) versus \((2,1)\), a fixed-eight-edge stochastic edge-swap
  search evaluated 63,267 labelled hosts of order 10.  Its best graph still
  had eight avoiding colorings out of 256.  The saved avoiding coloring was
  independently checked.

These are null search results, not evidence that the universal conjecture is
true.

## Claims explicitly not made

- No counterexample to Erdős #561 was found.
- No full solution of Erdős #561 is claimed.
- The named-family or stochastic searches are not exhaustive.
- No novelty or priority claim is made for C3 pending the separate audit.
- No conclusion is drawn from SAT/UNSAT outside the exact saved scopes.

