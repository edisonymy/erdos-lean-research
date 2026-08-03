# Heavy-edge partition alignment and surface normalization

**Status (2026-08-03):** exact structural theorems plus independent finite
audits.  The argument rules out exactly one mismatched heavy edge
analytically, excludes two mismatches by a dual-solver coverage-audited
computation, reduces three mismatches to a 21-vertex projective-plane block,
and gives a finite topology/overlap classification for every `m=4,...,12`.
It does **not** prove that all heavy-edge partitions align, and it does not
construct or exclude the full 24-vertex uniform-type-5 graph.

## 1. Setting

Let `G` be a hypothetical 24-vertex graph with the exact uniform type-5
properties:

- `G` is 9-regular and `K4`-free;
- the codegree-four edges form a perfect matching `H` of twelve **heavy**
  edges;
- every other present edge has codegree two; and
- every vertex link is two `C5`s sharing the heavy mate.

There are 108 edges.  Each link has ten edges, so

```text
3 f_2 = 24*10,       f_2=80.
```

Let `X` be the two-dimensional triangle complex whose faces are all eighty
triangles of `G`.  Every light edge is in two faces and every heavy edge is in
four faces.

Fix a heavy edge `uv`.  Its four common neighbours label its four incident
faces `uvs`.  At `u`, the two `C5` branches pair these four face labels into a
perfect matching `P_u`; similarly `v` gives `P_v`.  Call `uv` **aligned** when
`P_u=P_v` and **mismatched** otherwise.  Write `m` for the number of mismatched
heavy edges.

## 2. Exact resolution theorem

For each heavy edge independently choose a perfect matching `Q` of its four
incident faces.  Replace the heavy edge by two edge copies and glue each
`Q`-pair of face sides along one copy.  Light-edge gluings are unchanged.

At an endpoint `x`, the components of the new vertex link are controlled by
the two-coloured multigraph `P_x union Q` on the four face flags.

- If `Q=P_x`, the union has two two-vertex alternating components.  The two
  old `C5` sectors stay separate, producing two normalized vertices, each
  with link `C5` and degree five.
- If `Q!=P_x`, two distinct perfect matchings on four points have alternating
  union `C4`.  The two old sectors cross-splice into one link `C10`, producing
  one normalized vertex of degree ten.

Thus every choice of the twelve matchings produces a closed triangulated
surface as a two-dimensional delta-complex: every edge is in two faces and,
after separating link components, every vertex link is a cycle.

The surface is simplicial exactly when `Q` agrees with at least one endpoint
partition on every heavy edge.  Indeed, if `Q` disagrees with both endpoint
partitions, neither endpoint splits and the two new heavy-edge copies are
parallel.  If at least one endpoint splits, the two copies have distinct
endpoint pairs.  Light edges cannot create loops or parallel edges because
they came from a single edge between two distinct original labels.

Consequently:

- an aligned heavy edge has one simple choice, `Q=P_u=P_v`;
- a mismatched edge has two simple choices, `Q=P_u` or `Q=P_v`.

There are exactly `2^m` simple resolutions.  In every one of them,

```text
n_5 = 48-2m,    n_10 = m,
f_0 = 48-m,     f_1 = 120,    f_2 = 80,
chi = 8-m.                                             (2.1)
```

More generally, let `a` be the number of endpoint incidences at which
`Q=P_x`.  Then

```text
n_5=2a,   n_10=24-a,   f_0=24+a,   chi=a-16.
```

The exact generating polynomial whose coefficient of `z^a` counts all
`3^12` (possibly non-simplicial) resolutions is

```text
(z^2+2)^(12-m) (2z+1)^m.                               (2.2)
```

The nine local matching cases and every coefficient in (2.2) are replayed by
`audit_partition_surface.py`.

## 3. The normalized surface is flag

Let `S` be any simple resolution and let `pi:S -> X` be the quotient map.
No two preimages of the same original vertex are adjacent.  Hence a clique in
the one-skeleton of `S` projects injectively to a clique of `G`; in particular,
the normalized one-skeleton remains `K4`-free.

It is stronger: every normalized 3-cycle is a face.  Suppose normalized
vertices `x',y',z'` are pairwise adjacent.  Their distinct images `x,y,z`
form a triangle of `G`.  At an original vertex, two adjacent vertices of its
link lie in the same `C5` sector (when one is the heavy mate, the relevant
hub incidence chooses that same sector).  Therefore the three lifted edges
select the same sector copy at all three corners.  They are exactly the lift
of the face `xyz`.

So every simple resolution is a disjoint union of simple **flag** triangulated
closed surfaces, with vertex degrees only five and ten.

## 4. Every component has at least twelve vertices

Let `C` be a connected component of a simple resolution.

If `|V(C)|<=10`, degree ten is impossible, so all vertices have degree five.
The surface equations give `f_1=5n/2`, `f_2=5n/3`, and `chi=n/6`; hence
`n` is a positive multiple of six.  The only possibility below twelve is
`n=6`, whose 5-regular simple one-skeleton is `K6`, contradicting
`K4`-freeness.

If `n=11`, let `q` be the number of degree-ten vertices.  Integrality of
`f_1` and `f_2` gives `q` odd and `q=1 (mod 3)`, hence `q` is 1 or 7.  The
case `q=7` contains a `K4`.  In the case `q=1`, the degree-ten vertex is
universal.  The surface has twenty faces, ten incident with that vertex and
ten not incident with it.  Any latter face, together with the universal
vertex, is a `K4`.  This is again impossible.

Thus every component has at least twelve vertices.  If the resolution has
`c` components, then

```text
ceil((8-m)/2) <= c <= floor((48-m)/12)                  (4.1)
```

when `m<=7`; the left inequality uses `chi(C)<=2` for every connected closed
surface.

## 5. Exact consequences for m=0,1,2,3

For a component with `p` degree-five and `q` degree-ten vertices,

```text
6 chi(C) = p-4q.                                        (5.1)
```

### No mismatches

Here `f_0=48`, `chi=8`, so (4.1) forces four components.  Each is all-degree
five.  Equation (5.1) permits either a 6-vertex projective plane or a
12-vertex sphere.  The former has one-skeleton `K6` and is forbidden.  Thus
all four components are 12-vertex 5-regular spheres, necessarily the
icosahedral triangulation.  This recovers the four-icosahedra reduction with
all assumptions explicit.

### One mismatch is impossible

Here `f_0=47` and `chi=7`.  At least four components are needed to carry
Euler characteristic seven, but at most three components of order at least
twelve fit into 47 vertices.  Therefore

```text
m != 1.                                                 (5.2)
```

This is the first unconditional global alignment constraint: if any heavy
edge is mismatched, at least two are.

### Two mismatches

Here `f_0=46`, `chi=6`, and there are exactly three components, each a sphere.
For a spherical component, (5.1) gives

```text
p=4q+12,     |V|=5q+12.
```

The two degree-ten vertices can distribute only as

```text
(q_1,q_2,q_3)=(1,1,0)  or  (2,0,0).
```

The complete order-17 flag-sphere census contains no degree sequence
`(10,5^16)`, eliminating `(1,1,0)`.  The order-22 census contains exactly two
degree sequences `(10^2,5^20)`.  Hence every `m=2` normalization would be

```text
icosahedron + icosahedron + one of two 22-vertex blocks.
```

The two surviving graph6 records are

```text
U|fIJCpCG_a@C@C?b?G[@?_[ABGCKGCWCAW@?{?G
U|fIID@OI?g@W@K?b?G[X?oC@_G@_G?oc?Fo??Fo
```

They are not eliminated by the marked-edge condition alone.  The two blocks
have respectively 465 and 645 marked factors with degree one at every
degree-five vertex, degree two at each degree-ten vertex, and antipodal marked
neighbours in each `C10` link.  The icosahedron has 125 perfect matchings.

The separate `surface_gluing_max` branch exhausts the resulting
symmetry-reduced quotient/fibre problem.  Its independent coverage audits
account for all 540 branch keys, and every branch was replayed UNSAT with both
CaDiCaL 1.9.5 and Glucose 4.2.  Thus `m=2` is excluded computationally.  The
branch UNSAT results do not carry DRAT/LRAT certificates, so this is a
dual-solver, coverage-audited computational exclusion, not a proof-certified
or solver-free theorem.

### Three mismatches

Here `f_0=45`, `chi=5`, and there are exactly three components: two spheres
and one projective plane.  A projective-plane component satisfies

```text
p=4q+6,      |V|=5q+6.
```

The component lower bound excludes `q=0,1`, so it contains at least two of
the three degree-ten vertices.  If it contains two, the remaining degree-ten
vertex lies on a 17-vertex sphere, which the census excludes.  Therefore the
only surviving topology is

```text
icosahedron + icosahedron
  + a 21-vertex flag projective plane with (10^3,5^18).  (5.3)
```

## 6. Independent flag-sphere census

The installed generator was official `plantri` 5.8 (2026-03-04), executable
SHA-256

```text
6ea6eb87427fb40c62670698b406e2e9729da1f3b0024b34b76d4ceecf8e0f39.
```

From the workspace root the exact commands were:

```powershell
& 'C:\tmp\plantri58-msys2\ucrt64\bin\plantri.exe' -m5c4 -g 17 `
  'research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\plantri17_m5c4.g6'

& 'C:\tmp\plantri58-msys2\ucrt64\bin\plantri.exe' -m5c4 -g 22 `
  'research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\plantri22_m5c4.g6'
```

`-c4` is exact here because a simple spherical triangulation is flag exactly
when it has no nonfacial triangle, equivalently when its one-skeleton is
4-connected.  The streams are:

| order | records | stream SHA-256 | target hits |
|---:|---:|---|---:|
| 17 | 4 | `785714919d6cea16bcca7d49bbe621f54660e9475d32eb0ba8c52e70668a29d4` | 0 |
| 22 | 649 | `cce12d2f31dcbae5b16319fa22986deb00a9f83c8dabd11be788de8c045047de` | 2 |

`audit_plantri_surface_blocks.py` uses its own graph6 decoder and independently
checks order, edge counts, minimum degrees, target degree sequences, triangle
counts, `K4` counts, and the `C10` links of every target.  The marked-factor
counts are independently replayed by `audit_m2_marked_blocks.py`.

## 7. Surftri target-filter audit for (5.3)

The new projective-plane generator setup in `C:\tmp\surftri-0.989` was
inspected without touching its running shards.

- The downloaded archive `C:\tmp\surftri.0.989.tgz` has SHA-256
  `8d9fe2a046453a62ff225fc7f0c1ac9e0031f54b2274e9d50ea85543919e94e8`.
  Despite its suffix it is a plain tar archive.  Its `surftri.c` member and the
  extracted source agree byte-for-byte, SHA-256
  `cca54726c2330c94744135535790cd0e8b4aec029937599702013bcc47052113`.
- `target_degree_filter.c` has SHA-256
  `63ec55e2c587baa62db7ebe05dcf831e6238496aaf4c62f92cfa0af03e694839`.
  It accepts exactly when `nv==21`, every degree is 5 or 10, and the counts are
  `n5=18,n10=3`.  No other degree value can pass.
- The modified source has SHA-256
  `80be1a02f09fb4fc06cfce336bc09e3e38cd3685ee08fd54e1e4937d3c7eb9ae`.
  Its only difference from official `surftri.c` is replacing the generic
  plugin include guard by `#include "target_degree_filter.c"`.
- `FILTER` is called in the final `gotone` path before output and counters.
  The built `surftri_target` has SHA-256
  `9a519d31eb8b28784bfd941c35ff412a4692685f7c736e48a48cdff5b41d039f`.
- The intended complete split is
  `./surftri_target -v -g -m5 -n 21 1 r/8` for every `r=0,...,7`.
  Here `-n ... 1` selects the nonorientable genus-one surface, i.e. the
  projective plane.  At this audit time the target enumeration was still in
  progress, so no completeness or emptiness statement is made.

For every emitted graph6 record, an independent post-filter must check:

1. order 21, simplicity, connectedness, degree multiset `(10^3,5^18)`,
   60 edges, and 40 triangles;
2. every present edge has graph codegree exactly two;
3. every degree-five link is an induced `C5` and every degree-ten link is an
   induced `C10` (this is the direct flag/surface check);
4. clique number at most three;
5. `21-60+40=1`, independently identifying the connected closed surface as
   the projective plane; and
6. graph6 and isomorphism deduplication across all eight shards, plus a
   manifest of shard commands, exit statuses, record counts, and SHA-256s.

The link check in item 3 implies that all graph triangles are surface faces;
checking both it and exact edge codegree makes the post-filter deliberately
redundant.  Surftri enumerates embedded maps, so abstract-graph isomorphism
deduplication remains necessary even if raw graph6 lines are distinct.

## 8. Marked components, 3-connectivity, and all m>=4

### 8.1 Exact marked-component parameterization

Mark every surface edge that is a normalized copy of an original heavy edge.
On a component `C`, let `q` be its number of degree-ten vertices.  Every such
vertex is the unsplit endpoint of one mismatched heavy edge.  Its two marked
neighbours are degree-five vertices, are antipodal in its `C10` link, and are
the two preimages of its heavy mate.  Thus these three vertices form a marked
`P3`.  The `q` marked `P3`s are disjoint.

Every remaining degree-five vertex has marked degree one, so the rest of the
marked graph is a disjoint union of `K2`s.  If `a` is their number, then

```text
p-2q=2a,       p=4q+6 chi,

a=q+3 chi,     p=2(q+a),
n=3q+2a,       chi=(a-q)/3.                         (8.1)
```

In particular, `a>=0` and `a=q (mod 3)`.  Globally,

```text
sum q=m,       sum a=24-2m=2(12-m).
```

The `a` marked `K2`s are exactly the individual surface copies of aligned
heavy edges; they must be paired two at a time when the surface is quotiented.

### 8.2 The quotient graph is 3-connected

First, `G` is connected.  Every graph component is 9-regular, hence has even
order at least ten.  A 10-vertex component would be `K10`.  A 12-vertex
component has 2-regular complement, whose independence number is at least
four, again giving a `K4` in `G`.  The only possible partitions of 24 into
even parts at least ten are `10+14` and `12+12`, so neither is possible.

Every vertex neighbourhood is the connected `C5`-vee-`C5` link, so `G` has no
cut vertex.  Any minimal two-vertex cut `{u,v}` must then have `uv` present:
each cut component must meet both neighbourhoods, while a connected
neighbourhood not containing the other cut vertex could lie in only one cut
component.

No adjacent pair is a cut:

- If `uv` is light, deleting the non-hub vertex `v` from `L_u` leaves a
  connected graph, so all neighbours of `u` other than `v` remain in one
  component.
- If `uv` is heavy and mismatched, the four branch-end flags are connected by
  `P_u union P_v=C4`; hence all four `P4` branches in `L_u-v` and `L_v-u`
  lie in one component.
- If `uv` is heavy and aligned, a disconnection would have exactly two sides,
  one for each common branch pair.  Each side `A` has exactly four neighbours
  of `u` and four of `v`, hence exactly eight cut edges.  Therefore
  `9|A|=2e(A)+8`.  It follows that `|A|` is even, while Turan's
  `K4`-free bound `e(A)<=floor(|A|^2/3)` forces `|A|>=14`.  Two such sides
  cannot fit into the 22 vertices outside `{u,v}`.

Thus `G` is 3-connected.

Make an overlap multigraph `B` whose vertices are normalized surface
components.  Pairing two aligned marked `K2`s in different components gives
an edge of `B`; pairing them in one component gives a loop.  These are the
only identifications between different components.  Connectedness of `G`
makes the non-loop part of `B` connected.  Moreover `B` has no bridge: a
bridge labelled by heavy edge `uv` would make `{u,v}` a two-vertex cut of
`G`.  Consequently, if there is more than one normalized component, its
cross-component aligned-edge multigraph must be connected and bridgeless,
with component token-degrees congruent to the corresponding `a` values
modulo two.

### 8.3 Two small component exclusions

For a face `xyz` of a simple flag surface, adjacent pairs have exactly two
common neighbours and there is no common neighbour of all three.  Hence

```text
n >= |N(x) union N(y) union N(z)|
  = deg(x)+deg(y)+deg(z)-6.                         (8.2)
```

If `n<=18`, no two degree-ten vertices can be adjacent, since a face through
such an edge would make (8.2) at least 19.  If the degree-ten vertices are
independent, exactly `10q` faces contain one of them, while the total face
count from (8.1) is `10(q+chi)`.  Thus there are exactly `10 chi` all-degree-
five faces.  This is impossible for `chi<0`.  When `chi=0`, every face has
exactly one degree-ten vertex; at any degree-five vertex its `C5` link would
then alternate high and low neighbours, making an odd cycle bipartite.  This
is also impossible.

This human proof excludes the component types

```text
(q,a;chi,n)=(4,1;-1,14), (3,3;0,15), (6,0;-2,18).
```

The remaining small positive-curvature type `(2,5;1,16)` was checked by a
complete targeted `surftri` projective-plane run.  The exact degree filter
emitted one map, graph6 `O~fzgkPCGo``@@@W_EW?|`; its abstract graph has forty
triangles, eleven `K4`s, noncyclic induced links, and edge codegrees larger
than two.  Hence it is not flag, and there is no 16-vertex flag projective
plane with degree multiset `(10^2,5^14)`.  This last exclusion is
computational, not a standalone human proof.

As an adversarial replay of the direct `(3,3)` proof, the same filter emitted
four torus maps and four Klein-bottle maps of order 15.  All eight independently
fail flagness; none is a normalization block.  The three stream hashes and
post-checks are in `audit_surftri_small_census.result.json`.

### 8.4 Finite topology table

Write a component as `(q,a;chi,n)`.  Applying (8.1), the twelve-vertex lower
bound, the no-`q=1` result, the human exclusions above, the 16-vertex census,
and the connected-bridgeless overlap condition leaves exactly:

| `m` | surviving normalized component multisets |
|---:|---|
| 4 | `(0,6;2,12)+(4,10;2,32)`; `(2,8;2,22)+(2,8;2,22)`; `(0,6;2,12)+(0,6;2,12)+(4,4;0,20)` |
| 5 | `(0,6;2,12)+(5,8;1,31)`; `(2,8;2,22)+(3,6;1,21)`; `(0,6;2,12)+(0,6;2,12)+(5,2;-1,19)` |
| 6 | `(6,12;2,42)`; `(0,6;2,12)+(6,6;0,30)`; `(2,8;2,22)+(4,4;0,20)`; `(3,6;1,21)+(3,6;1,21)` |
| 7 | `(7,10;1,41)`; `(0,6;2,12)+(7,4;-1,29)`; `(2,8;2,22)+(5,2;-1,19)`; `(3,6;1,21)+(4,4;0,20)` |
| 8 | `(8,8;0,40)`; `(0,6;2,12)+(8,2;-2,28)`; `(3,6;1,21)+(5,2;-1,19)`; `(4,4;0,20)+(4,4;0,20)` |
| 9 | `(9,6;-1,39)`; `(4,4;0,20)+(5,2;-1,19)` |
| 10 | `(10,4;-2,38)`; `(5,2;-1,19)+(5,2;-1,19)` |
| 11 | `(11,2;-3,37)` |
| 12 | `(12,0;-4,36)` |

The audit records the successive counts

```text
m                     4       5       6       7       8       9      10      11      12
raw arithmetic        6       7      10       9      10       7       5       3       2
human local lemmas    4       4       5       5       5       4       2       1       1
small census          3       3       4       4       4       3       2       1       1
plus overlap          3       3       4       4       4       2       2       1       1
```

No row is an existence assertion.  In particular, `m=11` and `m=12` are now
forced to be connected surfaces, but neither surface nor its inverse quotient
has been constructed or excluded.

### 8.5 Admissible contractions and the provisional RP2 block

[Bibby--Odesky--Wang--Wang--Zhang--Zheng, Lemma 4.1](https://arxiv.org/abs/1909.03303)
observes that every edge of a vertex-minimal flag surface lies in an induced
four-cycle; equivalently, an edge in no induced four-cycle is available for an
admissible flag contraction.

The provisional 21-vertex record

```text
TAheJ@peD?WWMKgRW?D[?GABOObG?S?PP??j
```

was independently decoded and checked: it has 21 vertices, 60 edges, 40
triangles, degrees `(10^3,5^18)`, graph codegree two on every edge, induced
links `C10` and `C5`, no `K4`, and Euler characteristic one.  Thus it is a
genuine flag projective-plane block, independently of its still-pending
complete `surftri` provenance.

The quotient-local marked condition is stronger than merely choosing
antipodal leaves.  Requiring each paired leaf set to have the degree-ten centre
as its **only** common neighbour leaves exactly four marked factors; each has a
unique residual perfect matching.  The graph has twelve induced four-cycles
but 36 edges in none.  In every one of the four factors, all six marked `K2`
edges are admissibly contractible.  Therefore contraction theory supplies
useful simplifications, but the contraction does not preserve the prescribed
degree `(5,10)` pattern or the inverse fibre pairing.  No exclusion follows
from Lemma 4.1 alone.

### 8.6 Constant-fibre face balance and the fixed-`K4` question

For any quotient-essential marked factor in a `(10^3,5^18)` block, let `C`
be the nine surface vertices in the six constant fibres (three singleton
centres and three paired-leaf fibres), and let `R` be the other twelve
degree-five vertices.  Let `s` be the number of non-designated quotient
adjacencies among the six constant fibres.  Fibre simplicity makes each such
adjacency a single surface edge, whereas the three designated centre/leaf-pair
adjacencies each have two preimages.  Therefore

```text
e(C)=6+s.
```

Both `C` and `R` have degree sum sixty.  The two handshake equations give

```text
e(R)=6+s,       e(C,R)=48-2s.                         (8.3)
```

Let `a,b,c,d` count surface faces containing respectively `3,2,1,0` vertices
of `C`.  Counting incidences with internal and crossing edges gives

```text
3a+b=12+2s,     b+c=48-2s,     c+3d=12+2s,
```

and hence

```text
b=12+2s-3a,     c=36-4s+3a,     d=2s-8-a.             (8.4)
```

In particular,

```text
s>=4,           a<=2s-8.                              (8.5)
```

There is also a quotient-visible lower bound on `a`.  For each ordered pair
`i!=j`, the two quotient edges `H_i H_j` and `H_j A_i`, together with the
designated double adjacency `H_i A_i`, force a distinct surface triangle
through one leaf of `A_i`.  Its count must be at most `2s-8`.  Together with
the earlier face-union exclusion of the triangle `H_0 H_1 H_2`, these are
human combinatorial necessary conditions.

For an independent exact test of the stronger conjecture that the six
constant fibres must contain a quotient `K4`, the retained SAT encoding uses
21 vertices, exact degrees `(10^3,5^18)`, ambient `K4`-freeness, conditional
edge codegree two, explicit induced `C10` high links, the complete marked
factor, simple constant-fibre crossings, and the fifteen clauses excluding a
`K4` on the six fibres.  Pinning the audited projective-plane record is SAT
and reproduces its quotient `K4` on fibres `[2,3,4,5]`; this is a positive
encoding control.  The avoidance CNF has 23,514 variables, 108,453 clauses,
and SHA-256

```text
a0ac8943b528b995a7e2fb700f51a462472e793f135d5e93bb20190df9d69bae.
```

Both a CaDiCaL 1.9.5 run and a Glucose 4.2 run reached a 600-second wrapper
cap without a verdict.  They are recorded as `TIMEOUT_NO_EVIDENCE`.

The quotient-pattern decomposition is exact: the twelve optional adjacencies
have 2,827 labelled `K4`-free assignments, forming exactly 515 orbits under
simultaneous `S3` permutation of `(H_i,A_i)`.  The face-balance conditions
remove successively 61, 35, and 40 representatives, or 299, 176, and 234 raw
assignments.  Thus 379 representatives covering 2,118 raw assignments remain.
A shallow bounded Glucose pass returned 39 representative UNSAT results and
476 `UNKNOWN`s; every one of those 39 is already among the analytic
rejections above.  One stronger bounded pass returned 45 UNSAT and 470
`UNKNOWN`.  Forty-three of the 45 are analytic rejections; the other two are
representatives 203 and 244, covering twelve raw assignments.  Those two
results are single-solver and uncertified.

A separate solver-free local-core audit exhausts all 37,852 ways to lift the
379 analytically surviving quotient patterns to edges on the nine actual
surface vertices of `C`.  It requires ambient `K4`-freeness, at most two
common `C`-neighbours on every present `C`-edge, the exact face-balance
nonnegativity conditions, and induced embeddability of every partial `C`-link
in the required `C10` or `C5`, with the marked leaves antipodal in `C10`.
The known projective-plane candidate passes as a positive control.  Exactly
15 of 379 representatives, covering 87 of 2,118 raw assignments, have no
admissible local lift.  Thus this exhaustive local audit leaves exactly

```text
364 representatives covering 2,031 raw assignments.               (8.6)
```

The two extra single-solver exclusions are not among those fifteen; accepting
them provisionally would leave 362/2,019.  They are not used in (8.6).
Because the exact local-lift audit removes only about 4.1% of the analytic raw
remainder, this branch was stopped for low yield and was not recursively
refined.  No general fixed-`K4` theorem or counterconfiguration is claimed.

## 9. Reproduction

```powershell
.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_partition_surface.py `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_partition_surface.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_plantri_surface_blocks.py `
  --order17 research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\plantri17_m5c4.g6 `
  --order22 research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\plantri22_m5c4.g6 `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_plantri_surface_blocks.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_m2_marked_blocks.py `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_m2_marked_blocks.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_high_mismatch_topologies.py `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_high_mismatch_topologies.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_rp2_candidate_and_contractions.py `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_rp2_candidate_and_contractions.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_surftri_small_census.py `
  --directory research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_surftri_small_census.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_surftri_filter_setup.py `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_surftri_filter_setup.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_k4_sat.py `
  --allow-constant-k4 --candidate-control-assumptions `
  --cnf research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_k4_control.cnf `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_k4_control.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_pattern_orbits.py `
  --audit-only `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_pattern_orbits.audit.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_pattern_bounded.py `
  --solver glucose42 --conflict-budget 5000 `
  --cnf research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_pattern_bounded_5k.base.cnf `
  --progress research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_pattern_bounded_5k.progress.json `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_pattern_bounded_5k.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_constant_fibre_face_balance.py `
  --orbit-audit research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_pattern_orbits.audit.json `
  --bounded-result research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_pattern_bounded_5k.result.json `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_constant_fibre_face_balance_5k.result.json

.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_constant_fibre_core_lifts.py `
  --orbit-audit research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_pattern_orbits.audit.json `
  --analytic-audit research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_constant_fibre_face_balance.result.json `
  --control-result research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\rp2_constant_fibre_k4_control.result.json `
  --output research\erdos151\n50_protected_core_max_2026-08-03\partition_alignment_max\audit_constant_fibre_core_lifts.result.json
```

## 10. Claim boundary

Proved here:

- the exact degree-five/degree-ten normalization theorem and resolution
  polynomial;
- the flag property and the twelve-vertex component lower bound;
- the marked `(q,a)` component parameterization and 3-connectivity of `G`;
- the connected-bridgeless aligned-edge overlap constraint;
- the face-union and small-component exclusions in Section 8.3;
- the constant-fibre face-balance identities and necessary conditions
  (8.3)--(8.5);
- `m!=1`;
- the exact topological reductions for `m=0,2,3`;
- the finite topology table for `m=4,...,12`; and
- the complete order-17/order-22 flag-sphere census and marked-factor counts.

Computationally established, with retained audit artifacts:

- every one of the 540 symmetry-reduced `m=2` quotient/fibre branches is
  UNSAT in both CaDiCaL 1.9.5 and Glucose 4.2, with independent input, orbit,
  factor, fibre, and branch-key coverage audits (no DRAT/LRAT certificates);
- no flag `(10^2,5^14)` projective-plane block exists;
- all eight order-15 degree-pattern torus/Klein map hits are nonflag; and
- the supplied order-21 projective-plane graph is a valid local flag block
  with exactly four quotient-locally admissible marked factors;
- the fixed-candidate SAT control reproduces its constant-fibre quotient `K4`;
  and
- the 2,827 constant-fibre `K4`-free adjacency assignments form exactly 515
  audited simultaneous-`S3` orbits; and
- the 37,852 endpoint lifts of the 379 analytic survivors have been exhausted,
  excluding exactly 15 representatives/87 raw assignments and leaving
  364/2,031 under the stated necessary local checks.

Not proved here:

- `P_u=P_v` for every heavy edge;
- exclusion of `m=3` (the surftri census and then quotient/fibre checks remain);
- the general claim that every `(10^3,5^18)` quotient-essential marked block
  has a `K4` on its six constant fibres (364 audited pattern orbits remain
  after the solver-free local-lift filter; two more have only single-solver
  UNSAT evidence);
- exclusion of any one of `m=4,...,12` (the table is a reduction, not an
  emptiness proof);
- existence or nonexistence of the full 24-vertex uniform-type-5 graph; or
- any arrowing, ambient-completion, or Erdős-151 conclusion.
