# Hostile audit: X1, TCG, A4.1, M1, and V1

Date: 2026-08-03 (Europe/London)

Scope: an independent audit of the claims requested in `RESEARCH_LOG.md`
sections 11--13 and `PROGRAM_ALPHA.md` section A4'.  The source logs were
treated as hostile and were not edited.  This is a theorem-and-consequence
audit, not a novelty audit and not a claim to resolve Erdos problem #151.

## Frozen inputs

```text
cffb3122af03a21a00f5fa6156f7882584ae0a4cd40b2fab121fe64ed214bc34  RESEARCH_LOG.md
6442504b1b41bc9fd5ba14c9b225bec49e75ff84f27c138223434fd7ea3d3406  PROGRAM_ALPHA.md
9519a676ee381f02f03269c22e3f101162b2fdcc9d432e4103cb1192fdff91bc  ejcram18.pdf
```

The last file was downloaded from the author's official URL for revision 18
(24 April 2026) of *Small Ramsey Numbers*.  Tables Ia and IIa were checked both
by text extraction and by rendering pages 6 and 10.

## Verdicts

| Item | Verdict | Exact qualification |
|---|---|---|
| X1 | **PASS** | The Lovasz quantifiers used in the log are exact; the Brooks exceptions are handled correctly. |
| TCG theorem | **PASS** | The theorem and its rounding are correct. |
| TCG at `(50,11)` and `(59,12)` | **PASS** | These are genuine #151 order parameters: `H(50)=11` and `H(59)=12`. |
| TCG at `(87,15)` and `(98,16)` | **FAIL as unconditional #151 consequences** | `H(87)` can be 15 or 16, and `H(98)` can be 16 or 17.  The corrected `RESEARCH_LOG.md` already withdraws these claims, but `NOTE_TO_56SOL_2026-08-03.md` and the relayed note remain stale. |
| TCG "all `n` above about 200" | **FALSE** | The gate becomes asymptotically vacuous, not automatic.  The corrected research log already says this. |
| Stronger `3(Delta+2)/4` consequence | **FAIL for `h=14`** | Even granting the cited chromatic theorem, it closes `h=13` only.  At `h=14` the threshold is 71 while the rigorous Ramsey lower bound is only 67; comparing 71 with the upper bound 77 reverses the required direction. |
| A4.1 | **PASS after an explicit nonempty-graph boundary** | For `n>0` the averaging proof is exact.  As written for "any" graph, the empty graph gives `chi_tf^f=0`, so `n/chi_tf^f` is undefined. |
| M1 | **PASS WITH PROOF REPAIR** | Both conclusions are true.  The phrase "`G-M` is pure-3, so by TCG" is not a valid invocation of TCG because `beta(G-M)<=h-1` need not hold.  A direct degree argument repairs the proof. |
| V1 | **PASS** | The cut-edge parity argument is exact for every graph. |

## 1. X1: exact reconstruction

The needed form of Lovasz's decomposition theorem is:

> If `d_1,...,d_k` are nonnegative integers and
> `sum_i (d_i+1) >= Delta(G)+1`, then `V(G)` has a partition
> `V_1 union ... union V_k` with `Delta(G[V_i]) <= d_i` for every `i`.

The quantifiers can be checked without trusting a secondary formulation.
Among all labelled `k`-partitions minimize

```text
Phi = sum_i e(G[V_i])/(d_i+1).
```

If a vertex `v in V_i` has at least `d_i+1` neighbours in `V_i`, then
`deg(v)<=Delta(G)<=sum_j(d_j+1)-1` implies that some `j != i` has at most
`d_j` neighbours in `V_j`.  Moving `v` from `V_i` to `V_j` changes `Phi` by
at most

```text
-(d_i+1)/(d_i+1) + d_j/(d_j+1) < 0,
```

contradicting minimality.  This proves exactly the form used in X1.

Take every `d_i=3` and `k=ceil((Delta+1)/4)`.  Each induced part is
`K4`-free and has maximum degree at most three.  Componentwise Brooks gives
three colours: a degree-three complete exception would be `K4` and is
excluded; an odd-cycle exception has chromatic number exactly three; complete
graphs of order at most three also use at most three colours.  Giving the
parts disjoint palettes proves

```text
chi(G) <= 3 ceil((Delta(G)+1)/4).
```

Thus X1 is valid also at small maximum degree (including odd cycles).  The
statement is a standard consequence of Lovasz plus Brooks and should not be
presented as novel.

## 2. TCG: theorem and exact Ramsey use

Let `G` be pure-3: it is `K4`-free and every edge lies in a triangle.  Its
nontrivial ambient maximal cliques are exactly its triangles.  Every open
neighbourhood is admissible, because every clique contained in `N(v)` extends
by `v`.  Therefore

```text
Delta(G) <= beta(G) <= h-1.
```

X1 supplies a proper colouring with at most
`q=3 ceil(h/4)` colours (pad with empty classes if necessary).  If the class
sizes are nonincreasing, the sum of the two largest is at least
`ceil(2n/q)`.  Their union is bipartite, hence triangle-free, and therefore
admissible in a pure-3 graph.  Consequently

```text
ceil(2n/q) <= beta(G) <= h-1,
n <= (h-1)q/2,
B(h) := floor((h-1) 3 ceil(h/4)/2).
```

There is no rounding gap in the displayed `B(h)`.

For the Ramsey interpretation, directly from the definitions,

```text
H(n) >= h  iff  n >= R(3,h),
H(n) <= h  iff  n <  R(3,h+1).
```

Thus the exact possible pure-3 counterexample strip in the `H(n)=h` layer is

```text
[ R(3,h), min(B(h), R(3,h+1)-1) ].
```

Using only revision 18's rigorous bounds gives the following audit table.

| `h` | `q` | `B(h)` | rigorous `R(3,h)` interval | consequence |
|---:|---:|---:|---:|---|
| 11 | 9 | 45 | 47--50 | the entire `h=11` layer is excluded |
| 12 | 9 | 49 | 53--59 | the entire `h=12` layer is excluded |
| 13 | 12 | 72 | 61--68 | not excluded; rigorous outer strip 61--72 |
| 14 | 12 | 78 | 67--77 | not excluded; rigorous outer strip 67--78 |
| 15 | 12 | 84 | 74--87 | not excluded; rigorous outer strip 74--84 |
| 16 | 12 | 90 | 82--97 | not excluded; rigorous outer strip 82--90 |

In particular:

* `R(3,11)<=50<R(3,12)` proves `H(50)=11`; TCG excludes a pure-3
  `beta<=10` graph on 50 vertices.
* `R(3,12)<=59<R(3,13)` proves `H(59)=12`; TCG excludes a pure-3
  `beta<=11` graph on 59 vertices.
* The current bounds imply only `H(87) in {15,16}`.  TCG excludes the
  `H(87)=15` branch (`87>B(15)=84`) but not the possible `H(87)=16` branch
  (`87<=B(16)=90`).
* The current bounds imply only `H(98) in {16,17}`.  TCG excludes the
  `H(98)=16` branch but not the possible `H(98)=17` branch
  (`B(17)=120`).  The current survey upper bound is `R(3,16)<=97`, not 98.

The direction needed at a jump is a **lower** bound
`R(3,h)>B(h)`.  An upper bound above `B(h)` proves nothing of that kind.
Accordingly, even if one grants the stronger classical inequality

```text
chi(G) <= floor(3(Delta(G)+2)/4),
```

the derived thresholds are

```text
h=13: B*(13)=12*10/2=60, and R(3,13)>=61 closes the layer;
h=14: B*(14)=floor(13*11/2)=71, but only R(3,14)>=67 is known.
```

So that refinement closes `h=13`, not `h=14`.  The stale note's comparison
`71.5<77` uses the Ramsey **upper** bound in the wrong direction.

Finally, there is no tail.  The classical theorem
`R(3,h)=Theta(h^2/log h)` is equivalent on inversion to
`H(n)=Theta(sqrt(n log n))`.  Hence

```text
B(H(n))/n = Theta(log n) -> infinity.
```

The necessary counterexample inequality `n<=B(H(n))` therefore becomes
easier, not harder, at large order.  TCG is a finite band gate.

## 3. A4.1: fractional averaging

Assume `G` is a nonempty finite graph and define `chi_tf^f(G)` by the finite
linear program

```text
minimize W = sum_S x_S
subject to x_S >= 0 for triangle-free vertex sets S,
           sum_{S contains v} x_S >= 1 for every vertex v.
```

For any feasible solution,

```text
sum_S x_S |S|
  = sum_v sum_{S contains v} x_S
 >= n.
```

Since `W>0`, some supported `S` has `|S|>=n/W`; otherwise the weighted sum
would be less than `n`.  The finite LP attains its minimum, so some
triangle-free set has size at least `n/chi_tf^f(G)`.  In a pure-3 graph every
triangle-free set is admissible, proving

```text
beta(G) >= n/chi_tf^f(G).
```

This genuinely avoids an integral-colouring rounding loss.  The only needed
quantifier correction is `n>0`: on the empty graph the optimum is zero and
the displayed quotient is undefined.  Also, a probabilistic occupancy
argument yields the advertised fractional cover only when it provides a
uniform per-vertex lower bound (as the stated Master Inequality targets), not
merely an average occupancy bound.

## 4. M1: true conclusion, repaired proof

Let `M` be the graph of ambient maximal edges of a `K4`-free graph `G`, and
put `F=G-M`.

* `M` is triangle-free: three `M`-edges forming a triangle would each lie in
  that triangle.
* Every `F`-edge lies in an `F`-triangle.  If an edge is not in `M`, it lies
  in a triangle of `G`, and the other two edges of that triangle also cannot
  lie in `M`.
* Removing `M` changes no triangle, so
  `tf_3(F)=tf_3(G)`.

The log's next phrase, "`F` is pure-3, so by TCG", skips a hypothesis: TCG
as stated assumes `beta(F)<=h-1`, and edge deletion need not preserve this.
For example, deleting the sole maximal edge of `K2` changes `beta` from one
to two.

The desired conclusion nevertheless has a short direct repair.  For every
vertex `v`, `N_F(v)` is an ambient-admissible set in `G`: any ambient clique
contained there extends by `v`.  Hence

```text
Delta(F) <= beta(G) <= h-1.
```

Apply X1 to `F`, take the two largest proper colour classes, and use the fact
that `F` and `G` have the same triangles.  This proves

```text
tf_3(G)=tf_3(F) >= ceil(2n/(3 ceil(h/4))).
```

For the burden inequality, let `S` be any triangle-free induced vertex set
of `G` and let `C` be a minimum vertex cover of `M[S]`.  The set `S-C`
contains neither a triangle nor a maximal edge.  Since a nontrivial maximal
clique in a `K4`-free graph is an edge or a triangle, `S-C` is
ambient-admissible.  Therefore

```text
|S|-tau(M[S]) <= beta(G) <= h-1,
tau(M[S]) >= |S|-(h-1).
```

The direction in the deletion argument is correct.  At `(n,h)=(50,11)` the
first bound gives a triangle-free set of size at least
`ceil(100/9)=12`, and every triangle-free 12-set has
`tau(M[S])>=2`.  In particular `M` is nonempty.  This is a sound finite
search constraint, not a full result for #151.

## 5. V1 and the structured cut

Suppose `V(G)=A union B` and both induced subgraphs `G[A]` and `G[B]` are
triangle-free.  Colour every cut edge red and every edge internal to a part
blue.  A triangle has either zero or two cut edges, so it cannot be all red.
An all-blue triangle would lie wholly in `A` or wholly in `B`, which is also
impossible.  Thus this is a two-edge-colouring with no monochromatic
triangle.  Contrapositively,

```text
G ->_e (3,3)  implies  G ->_v (3,3).
```

V1 is valid without a `K4`-free hypothesis.  For a SAT encoding in which a
positive `y_t` literal forces all three edges of `t`, the proposed clause

```text
OR_{t subset A, |t|=3} y_t  OR  OR_{t subset B, |t|=3} y_t
```

is sound: every satisfying assignment must create a triangle within one
side.  The reverse implication "triangle implies `y_t`" is unnecessary for
cut soundness.

## Primary sources

* L. Lovasz, *On decomposition of graphs*, Studia Scientiarum
  Mathematicarum Hungarica 1 (1966), 237--238, MR 0202630.
* R. L. Brooks, *On colouring the nodes of a network*, Proceedings of the
  Cambridge Philosophical Society 37 (1941), 194--197,
  <https://doi.org/10.1017/S030500410002168X>.
* S. P. Radziszowski, *Small Ramsey Numbers*, revision 18, 24 April 2026,
  <https://doi.org/10.37236/21>, author copy
  <https://www.cs.rit.edu/~spr/ElJC/ejcram18.pdf>.
* J. H. Kim, *The Ramsey number R(3,t) has order of magnitude
  t^2/log t*, Random Structures & Algorithms 7 (1995), 173--207,
  <https://doi.org/10.1002/rsa.3240070302>.

## Publication boundary

Safe reusable statements are X1, TCG itself, the corrected `h=11,12`
Ramsey consequences, A4.1 with `n>0`, repaired M1, and V1.  Unsafe statements
are the unconditional order-87/order-98 conclusions, an eventual TCG tail,
and closure of `h=14` from the stronger chromatic bound.  None of the passing
items constitutes a complete resolution of #151.
