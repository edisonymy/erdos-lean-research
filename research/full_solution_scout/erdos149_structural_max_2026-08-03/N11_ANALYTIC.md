# Erdős #149 at the first possible order: an analytic elimination

Date: 2026-08-03  
Scope: finite simple graphs, maximum degree at most four

## Result

**Theorem.** Every graph $G$ with $\Delta(G)\le 4$ and $|V(G)|\le 11$ has
strong chromatic index at most 20.

This is a finite-order theorem, **not** a solution of Erdős problem #149.
It replaces a bounded order-11 enumeration with a short structural argument.
The only external input is the sharp 1990 theorem of
Chung--Gyárfás--Tuza--Trotter (CGTT): a $2K_2$-free graph of maximum degree
at most four has at most 20 edges.

## 1. Compatibility graph

For a graph $G$, define $J=J(G)$ on vertex set $E(G)$. Two vertices of $J$
are adjacent exactly when their corresponding edges of $G$ are strongly
independent, equivalently when those two edges induce a $2K_2$. A strong
colour class is a clique of $J$, so a strong edge-colouring of $G$ is a
partition of $V(J)$ into cliques.

If $m=|E(G)|\le20$, the all-singleton colouring is enough. If $m=21$, then
needing 21 colours would mean $J$ is empty: any one edge of $J$ saves a
colour. But then $G$ is $2K_2$-free with 21 edges, contradicting CGTT. Thus
**every** subquartic graph with 21 edges is strongly 20-edge-colourable.

It remains only to consider $n=11,m=22$, because $m\le2n$. Equality in the
degree bound makes $G$ 4-regular.

On 22 vertices, a clique partition of $J$ saves two singleton classes if
and only if $J$ contains either a triangle or two vertex-disjoint edges.
Consequently, if $G$ needed more than 20 colours, then $J$ would have
neither. CGTT says $J$ is nonempty. Every nonempty triangle-free graph with
matching number one is a star, so

$$
J=K_{1,t}\mathbin{\dot\cup}(21-t)K_1 \qquad (t\ge1).
$$

Choose a star centre and call its corresponding edge of $G$ the *centre
edge*; the other vertices of that star are its *leaf edges*. (When $t=1$,
either endpoint of the single edge of $J$ may be chosen as centre.)

## 2. A local identity

For an edge $e=uv$, put

$$
R_e=V(G)\setminus(N[u]\cup N[v]),\qquad
c_e=|N(u)\cap N(v)|,\qquad r_e=d_J(e).
$$

An edge is strongly independent from $e$ exactly when both its endpoints lie
in $R_e$. Hence

$$
r_e=e_G(R_e). \tag{1}
$$

Since $G$ is 4-regular on 11 vertices, $|R_e|=3+c_e$. Writing
$S_e=N[u]\cup N[v]$, degree-summing over $R_e$ gives

$$
e_G(S_e,R_e)=4(3+c_e)-2r_e,\qquad
e_G(S_e)=10-4c_e+r_e. \tag{2}
$$

The seven distinct edges incident with $u$ or $v$ lie in $G[S_e]$, so

$$
r_e\ge4c_e-3. \tag{3}
$$

In particular, every isolated vertex of $J$ corresponds to an edge of $G$
lying in no triangle.

The centre edge also lies in no triangle. Indeed, if the centre $uv$ lay in a
triangle $uvw$, the other two triangle edges $uw,vw$ would conflict with the
centre, hence would be isolated vertices of $J$. That contradicts the
preceding paragraph because each lies in a triangle.

For the centre edge, therefore, $c_e=0$, so $|R_e|=3$. By (1), its $t$ leaf
edges are exactly the edges of $G[R_e]$, and consequently

$$
1\le t\le3. \tag{4}
$$

Every triangle of $G$ can use neither an isolated-$J$ edge nor the centre, so
all three of its edges must be leaves. Thus:

* if $t\le2$, $G$ is triangle-free;
* if $t=3$, $G[R_e]=K_3$, and this is the unique triangle of $G$.

## 3. Disjoint-edge counting

For two disjoint edges, let $k$ be the number of cross-edges joining their two
pairs of endpoints, and let $q_k$ count such unordered pairs.

There are

$$
\binom{22}{2}-11\binom42=165 \tag{5}
$$

pairs of disjoint edges. Also, each edge $xy$ is the middle edge of
$3\cdot3=9$ choices of outer edges. When $G$ is triangle-free all those outer
pairs are disjoint, so

$$
\sum q_k=165,\qquad \sum kq_k=22\cdot9=198. \tag{6}
$$

Triangle-freeness forces $k\le2$, and for $k=2$ the two cross-edges form a
matching. Such $k=2$ pairs occur in fixed-point-free partners: the two
opposite-edge pairs of the same 4-cycle. Hence $q_2$ is even. Since
$q_0=|E(J)|=t$, (6) gives $q_2=33+t$.

Therefore the case $t\le2$ forces $t=1$.

Suppose instead $t=3$. There is exactly one triangle. The three invalid
outer-edge choices in the $22\cdot9$ count are the three choices whose outer
edges meet at the third vertex of that triangle. Thus

$$
q_0+q_1+q_2=165,\qquad q_1+2q_2=195,
$$

and $q_0=3$ gives $q_2=33$. Exactly six of these $k=2$ pairs have their two
cross-edges meeting: choose one of the three triangle vertices and one of its
two external incident edges. All other $k=2$ pairs have matching cross-edges
and again occur in fixed-point-free opposite pairs. Their number would be
$33-6=27$, an impossibility. Hence $t=3$ is eliminated.

## 4. The last case $t=1$

We are left with a triangle-free 4-regular graph on 11 vertices for which $J$
has exactly one edge. The count above gives $q_2=34$, hence exactly 17
four-cycles.

For a nonadjacent vertex pair $\{x,y\}$, let
$\mu_{xy}=|N(x)\cap N(y)|$. There are 33 nonedges. Counting length-two paths
and opposite pairs on four-cycles gives

$$
\sum_{xy\notin E(G)}\mu_{xy}=11\binom42=66,\qquad
\sum_{xy\notin E(G)}\binom{\mu_{xy}}2=2\cdot17=34.
$$

Therefore

$$
\sum_{xy\notin E(G)}(\mu_{xy}-2)^2=2,\qquad
\sum_{xy\notin E(G)}(\mu_{xy}-2)=0.
$$

All terms are integral, so there is exactly one nonedge $p=\{a,b\}$ with
$\mu_p=1$, exactly one nonedge $q=\{c,d\}$ with $\mu_q=3$, and every other
nonedge has two common neighbours.

Let $A$ be the adjacency matrix of $G$, let $\mathbf J$ be the all-ones
matrix, and for a pair $xy$ let $B_{xy}$ have ones only in positions
$(x,y),(y,x)$. The common-neighbour data are precisely

$$
A^2=2\mathbf J+2I-2A+B_q-B_p. \tag{7}
$$

Because $G$ is regular, $A$ commutes with $\mathbf J$; it plainly commutes
with $I,A,A^2$. Equation (7) therefore forces

$$
A(B_q-B_p)=(B_q-B_p)A. \tag{8}
$$

This is impossible. If $p,q$ are disjoint, compare rows indexed outside their
four endpoints in (8): none of the four endpoints can have a neighbour
outside those endpoints. Each endpoint is nonadjacent to its partner, so it
would have degree at most two. If $p,q$ share one endpoint, say
$p=ab,q=ac$, then rows outside $\{a,b,c\}$ show that $a$ has no outside
neighbour; since $ab,ac$ are nonedges, $a$ has degree zero. Both cases
contradict 4-regularity.

This eliminates $t=1$, completing the theorem.

## Audit boundary

The proof uses only:

1. the published CGTT edge bound at $\Delta=4$;
2. elementary clique-partition facts for a 22-vertex compatibility graph;
3. degree, path, four-cycle, and adjacency-matrix counts written above.

It does not rely on the public order-11 catalogue or on a SAT solver. Those
two independent computational routes agree with the conclusion and are useful
audits, but they are not dependencies of this proof.

