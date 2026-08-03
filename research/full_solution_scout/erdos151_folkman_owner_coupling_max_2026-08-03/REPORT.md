# Protected Folkman owners and controlled cross-owner triangles for Erdős #151

**Worker status:** `CONTINUE_PACKET`  
**Date:** 3 August 2026  
**Scope:** long-horizon owner/cross-owner lane only; no global resolution or
novelty claim.

## 0. Outcome first

No counterexample to Erdős #151 was found.  Four materially different attack
cycles did, however, leave sharper and independently replayable boundaries.

1. **Protected K4-free core.**  A finite adaptable-link theorem independently
   rederives the campaign's existing ten-triangle floor **without** Bikov's
   degree-eight link classification.  Its new refinement is that, at the
   `n=50`, `H(50)=11` least-counterexample boundary, every ambient degree-ten
   core vertex has one of only ten exact link types and at most one extrinsic
   triangle.
2. **Retained cross-owner triangles.**  The cyclic 11-vertex Property-B seed
   from the current quasi-Folkman repository was replayed exactly.  Five
   nonarrowing `C11` owners uniquely own all edges, while 88 retained
   cross-owner triangles force a monochromatic triangle.  This is a concrete
   proof that mechanism B is logically real.  Its shadow is `K11`, with
   `beta=10`, `tf_3=2`, and `H(11)=4`, so it is not a #151 candidate.
3. **Signal-sender lift.**  An exhaustive two-solver census found no K4-free
   same- or different-colour triangle signal sender with vertex-disjoint
   signal edges on at most eight vertices.  The standard occurrence-splitting
   lift of the cyclic seed would already require 209 sender copies, so this
   small-gadget route has a quantified blow-up obstruction.
4. **Hermitian random blocks.**  The June 2026 Hermitian-unital construction is
   the correct modern cross-owner route, but its published
   McDiarmid/union-bound certificate is asymptotically incompatible with
   `beta<H`.  The certificate forces edge-retention density
   `p=Omega(s sqrt(log(sq)/q))`, hence degree
   `Omega(s q^(5/2) sqrt(log(sq)))`, whereas
   `H(q^4-q^3+q^2)=O(q^2 sqrt(log q))`.  This closes that *certificate*, not
   finite or deterministic Hermitian subgraphs.

The surviving route is sharply stated: construct either (A) a K4-free
arrowing core satisfying the protected `n=50` interface and then prove the
ambient graph has `beta<=10`, or (B) a sparse controlled cross-owner system
whose retained triangle hypergraph has Property B while accidental K4s and
`beta` are controlled from the original definitions.

## 1. Immutable target and prior-route exclusions

The authoritative target is frozen in [`TARGET_LOCK.md`](TARGET_LOCK.md).  For
an `n`-vertex graph `G`, `beta(G)` is the largest set containing no nontrivial
**ambient maximal clique**, and `H(n)` is the minimum independence number of
an `n`-vertex triangle-free graph.  The conjecture is

```text
beta(G) >= H(n).
```

A counterexample must satisfy `beta(G)<H(n)`.  K4-freeness together with
`tf_3(G)<H(n)` is a sufficient certificate, never an equivalent definition.

The following already-audited routes were treated as exclusions rather than
rerun:

- literal MSV tripartite owners after both deletions;
- Cayley and circulant sweeps;
- one- and two-vertex extensions of the known Ramsey seeds;
- tripartite tuning and generic CEGAR;
- repeated public graph-catalogue scans.

The generalized-owner theorem from the preceding packet is used exactly:
after unique edge ownership and deletion of every extrinsic triangle, the
final graph arrows `(3,3)` iff at least one surviving owner arrows `(3,3)`.
The two live escape mechanisms are therefore a protected arrowing owner or
deliberately retained cross-owner triangles.

## 2. Cycle 1 — protected K4-free owners via adaptable links

### 2.1 An independent ten-triangle theorem

**Computational theorem.**  If `Q` is an inclusion-minimal K4-free graph with
`Q -> (3,3)`, then

```text
t_Q(v) >= 10 for every v in V(Q).                         (2.1)
```

Here `t_Q(v)=e(Q[N_Q(v)])` is the number of core triangles through `v`.
The inequality itself was already available in the campaign by combining
Bikov's minimum-degree/classification theorem with the elementary spoke-cycle
argument.  The contribution here is an independent adaptable-colouring proof
that does not import that classification, plus the exact ten-type extension
in Section 2.2.  It is not logged as a new discovery.

**Reduction to a finite statement.**  Let `L=Q[N_Q(v)]`.  Every core edge lies
in at least two core triangles: otherwise a good colouring of `Q-e` extends
over `e`.  Hence `delta(L)>=2`.  K4-freeness of `Q` makes `L` triangle-free.

Colour `Q-v` without a monochromatic triangle.  Its colours on `E(L)` form an
edge signing.  If the spokes `vx` could be two-coloured so that no link edge
`xy` had

```text
colour(vx)=colour(vy)=colour(xy),
```

the colouring would extend to `Q`, a contradiction.  Thus `L` is not
universally adaptably 2-colourable.  Adaptability factors over components.
Hell--Zhu's exact characterization says a connected graph is universally
adaptably 2-colourable iff deleting some edge makes it bipartite.

It remains only to show that a triangle-free graph of minimum degree at least
two and at most nine edges is universally adaptable.  Since `2n<=2m`, every
such graph has at most nine vertices.  The replay enumerated **all** unlabeled
simple graphs with `delta>=2`, `m<=9`, and no triangle, with disconnected
graphs included.  There are 31:

```text
n:       4  5  6  7  8  9
count:   1  2  6 11  9  2
```

Every graph passed all three checks:

- a custom componentwise edge-deletion/bipartiteness implementation;
- an independent NetworkX implementation of the same characterization;
- the definition itself, enumerating every edge signing and every vertex
  two-colouring.

This proves the finite lemma at the stated computational trust boundary and
hence (2.1).  The exact direct-definition output is
[`k4free_links_through9_direct.result.json`](k4free_links_through9_direct.result.json).

### 2.2 The first obstructions and the `n=50` interface

Extending the same direct-definition census through eleven edges gives 161
graphs and exactly ten obstructions.  The first four occur at ten edges:

```text
edges  link order  number
10     8           3
10     9           1
11     8           2
11     9           3
11     10          1
```

All ten are connected.  Their graph6 strings and the complete census are in
[`k4free_links_through11_direct.result.json`](k4free_links_through11_direct.result.json),
SHA-256
`541141256a6defcc2377e903680f8be800128571b8cb511f0d4fa9367ed2b6a4`.
The three order-eight, ten-edge types coincide numerically with the
ten-edge layer of Bikov's seven classified degree-eight links; completeness of
Bikov's list remains an imported published theorem, not a claim of this
census.

Now specialize conditionally to the case in which the **least** counterexample
has order 50 and is K4-free.  The exact target window has `H(50)=11`, so
`beta(G)<=10`.  Open neighbourhoods are ambient-admissible, hence
`Delta(G)<=10`; least-order minimality, the audited Ramsey-window bound, and
`R(3,10)<=41` give `delta(G)>=9`.  The degree floor is not asserted for an
arbitrary nonminimal 50-vertex witness.

Let `Q` be an edge-minimal arrowing core.  For an ambient degree-ten core
vertex define

```text
kappa(v)=sum_{a in N_G(v)} (10-d_G(a)).
```

The already-audited degree-saturation inequality gives

```text
2 t_G(v)+kappa(v) <= 22.                                 (2.2)
```

Write `x=t_G(v)-t_Q(v)` for its extrinsic triangles.  Combining (2.1) and
(2.2) leaves only

```text
t_Q(v)=10:  2x+kappa(v)<=2;
t_Q(v)=11:  x=0 and kappa(v)=0.                           (2.3)
```

Thus a degree-ten core vertex has at most one extrinsic triangle.  If it has
one, all ten ambient neighbours also have degree ten.  If it has eleven core
triangles, it has no extrinsic triangle and again all neighbours have degree
ten.  Bikov gives `d_Q(v)>=8`, so its link must be one of the ten exact census
types above.  The complete arithmetic replay is
[`n50_protected_core_interface.result.json`](n50_protected_core_interface.result.json).

Ambient degree-nine core vertices remain live; (2.2) applies only when the
ambient degree equals the admissible-set ceiling ten.

### 2.3 What protection through the two owner deletions forces

Suppose an owner contains a protected arrowing core `Q` and every edge of `Q`
must survive.

1. **First deletion.**  Every other owner support meets `V(Q)` in an
   independent set of `Q`.  Otherwise the endpoints of a protected core edge
   co-belong to two supports, so the first deletion removes that edge.
2. **Second deletion.**  In the final graph, every vertex outside the
   protected owner's **full support** has an independent neighbourhood in
   `Q`.  If such a vertex were adjacent to both ends of a core edge, that edge
   and the two boundary edges would be a surviving extrinsic triangle.  A
   vertex lying in the same owner support but outside `V(Q)` is not covered by
   this conclusion: its triangle may be intrinsic.  The stronger statement for
   every vertex outside `V(Q)` therefore requires the representation to take
   the protected core itself as the full support (or separately make it
   triangle-closed).
3. **Degree capacity at `n=50`.**  Bikov gives `d_Q(v)>=8`, while the target
   gives `d_G(v)<=10`; consequently

   ```text
   e_G(V(Q),V(G)-V(Q)) <= sum_{v in Q}(10-d_Q(v)) <= 2|Q|. (2.4)
   ```

   In the least-counterexample order-50 case, `delta(G)>=9`, so a degree-eight
   core vertex needs one or two boundary neighbours, a degree-nine core vertex
   needs zero or one, and a degree-ten core vertex has none.  Without that
   minimal-order hypothesis, only the upper-capacity half of (2.4) remains.

The current Folkman lower bound gives `|Q|>=21`.  These conditions do not yet
contradict `beta(G)<=10`: edges outside the core, including other-owned edges
between core vertices, can change independence and ambient maximal cliques.
Thus neither `alpha(Q)<=10` nor an exact-beta conclusion may be inferred for
the core alone, and replacing `beta` by `tf_3` here would be an invalid
shortcut.  The live finite object is therefore a K4-free arrowing core of
order `21..50` and maximum degree ten, together with ambient padding satisfying
(2.3)--(2.4) and an **exact** ambient-beta check.

## 3. Cycle 2 — an exact controlled cross-owner escape

The current repository accompanying Mulrenin--van Overberghe's
quasi-Folkman work contains the following eight triples on `Z_11`:

```text
(0,1,2) (0,1,3) (0,1,5) (0,1,6)
(0,2,4) (0,2,7) (0,3,6) (0,3,7).
```

Closing them under all eleven translations gives 88 distinct selected
triangles.  The exact replay found:

- their two-shadow is all of `K11` (55 edge variables);
- no four selected triangles are the four faces of a `K4`;
- the selected triangle hypergraph lacks Property B: every red--blue edge
  colouring makes a selected triangle monochromatic;
- edge-variable occurrence counts are four on 11 edges and five on 44 edges.

Property B was checked independently by a custom propagating NAE backtracker
(1,521 search nodes), CaDiCaL 1.9.5, and Glucose 4.2.  All three returned
UNSAT for the 176-clause CNF.

There is also an exact unique-owner description.  Assign an edge `uv` to its
circular distance

```text
min((u-v) mod 11,(v-u) mod 11) in {1,2,3,4,5}.
```

Each of the five owner graphs is a Hamilton `C11`, hence triangle-free and
nonarrowing.  Every selected triangle uses at least two owners.  Therefore
retaining the selected extrinsic triangles produces global arrowing even
though no owner arrows.  This directly exhibits the logical escape from the
generalized-owner theorem when its extrinsic-triangle-deletion hypothesis is
removed.

This is an abstract **post-deletion edge-owner partition**, not a faithful
instance of the literal MSV first deletion: all five cycles span the same 11
vertices, so support co-membership would delete their edges.  Its role is to
certify mechanism B and motivate a new representation, not to evade the
already-proved MSV obstruction by relabelling the same supports.

This is not a #151 witness.  Its shadow is `K11`; the only nontrivial ambient
maximal clique is the whole graph, so `beta(K11)=10`, while `H(11)=4`.
Also `tf_3(K11)=2`.  The full triangle list, owner checks, and solver results
are in [`cross_owner_propertyb.result.json`](cross_owner_propertyb.result.json).

The remaining construction problem is exactly the accidental-K4 gap: realize
a non-Property-B selected triangle system in a K4-free sparse shadow, or delete
the accidental K4s while preserving the Property-B clauses and the exact
ambient-beta inequality.

## 4. Cycle 3 — signal-sender replacement gate

A classical way to attack the accidental-K4 gap is to split repeated edge
variables into separate clause occurrences and tie equal-colour occurrences
together with K4-free triangle signal senders.  This materially changes the
representation from owner deletion to a constraint-gadget lift.

The small-gadget gate was exhaustively checked.  A sender here is a K4-free
graph with two vertex-disjoint distinguished edges whose colours have forced
equal or forced opposite parity in every good edge colouring.

- NetworkX's complete graph atlas supplied all connected unlabeled K4-free
  graphs through order seven: `2,5,17,82,536` at orders `3,...,7`.  Direct
  enumeration of every good edge colouring agreed with 27,872 independent
  Glucose assumption queries.  No sender exists.
- `geng` supplied all 11,117 connected unlabeled graphs of order eight; 5,606
  are K4-free.  Glucose and CaDiCaL agreed on all 490,354 same/different
  parity assumption queries.  Again no sender exists.

Connected enumeration is complete for this purpose.  If the two signal edges
are in different components, swapping all colours in one component destroys
any forced relation; if they are in one component, that component alone is a
sender.  Hence every such K4-free sender has at least nine vertices.

For the cyclic seed, the 88 clauses contain 264 variable occurrences across
55 variables.  Tying the occurrences of each variable by a tree needs

```text
sum_e (occurrences(e)-1) = 264-55 = 209
```

sender copies.  Under the standard internally-disjoint gluing, an order-nine
sender with four terminal vertices contributes at least five internal
vertices, already exceeding 1,045 new internal vertices before other
separation requirements.  This does not rule out shared or algebraic gadgets,
but it closes the hoped-for tiny-sender lift of this seed.

Artifacts:

- [`signal_sender_atlas.result.json`](signal_sender_atlas.result.json)
- [`signal_sender_order8.result.json`](signal_sender_order8.result.json)

## 5. Cycle 4 — Hermitian owners and a density/certificate mismatch

Mulrenin and van Overberghe's 18 June 2026 preprint is a direct priority
collision with the broad cross-owner idea and supplies the right modern
baseline.  Their Hermitian intersection graph `H_q` has

```text
N=q^4-q^3+q^2,                 d=(q+1)(q^2-1),
q^3+1 unique edge owners,      each owner a K_{q^2}.
```

The nondegenerate (cross-owner) triangles contain no four faces spanning a
`K4`, yet force a monochromatic triangle.  Replacing every owner clique by a
random blowup of a triangle-free graph `F` with
`maxcut(F)<2e(F)/3` yields a K4-free arrowing graph for sufficiently large
`q`.

### 5.1 Finite `q=3` block obstruction

At `q=3`, `H_3` has 63 vertices, degree 32, 1,008 edges, 28 unique `K9`
owners, and 3,024 nondegenerate triangles.  A direct per-owner maximum-cut
certificate cannot occur on a `K9` owner.  Indeed, if a graph is properly
three-coloured, the three cuts isolating one colour class contain every edge
twice, so one cut has at least `2m/3` edges.  Thus
`maxcut(F)<2m/3` forces `chi(F)>=4`.  Chvátal's minimality theorem says the
smallest triangle-free four-chromatic graph has 11 vertices.

This does not refute the paper's global finite experiments or its asymptotic
proof: the random block argument uses concentration across many owners, not an
independent `K9` certificate.  It explains why any successful `H_3` subgraph
must exploit genuinely global cross-owner coupling.

### 5.2 The published union-bound certificate cannot meet #151 asymptotically

Let `s=|V(F)|`, `m=e(F)`, and `p=2m/s^2`, the survival probability of a base
edge.  Equation (8) of the preprint lower-bounds the desired event probability
by

```text
1 - 2 exp(-(8 delta^2 m^2/(3s^6))q + 7 log(sq)).          (5.1)
```

For this displayed lower bound to be positive it is necessary that

```text
(2 delta^2/3) q p^2/s^2 > 7 log(sq)+log 2,
```

and hence

```text
p = Omega(s sqrt(log(sq)/q)).                             (5.2)
```

The final Goodman inequality also requires

```text
(1-alpha)(1-delta)^2 > (1/3)(1+delta)^2,
```

where `alpha=maxcut(F)/m>=1/2`.  Necessarily
`delta<0.101021`, so `1-delta` is bounded below by `0.898979`.

The paper's Lemma 4.4 event itself forces high degree.  Each surviving
neighbour of a vertex belongs to exactly `q` of the `q^3-q` spanning cliques
in its neighbourhood.  Summing the lemma's lower cell bounds therefore gives

```text
d_{H_q^*}(v) >= (1-delta)p(q+1)(q^2-1).                  (5.3)
```

Combining (5.2)--(5.3), every graph in the event certified by (5.1) has

```text
Delta(H_q^*) = Omega(s q^(5/2) sqrt(log(sq))).            (5.4)
```

But every open neighbourhood is ambient-admissible, so `beta>=Delta`, while
the standard Ramsey asymptotic gives

```text
H(N)=O(sqrt(N log N))=O(q^2 sqrt(log q)).                 (5.5)
```

The ratio of (5.4) to (5.5) grows at least as `Omega(s sqrt(q))`.  Therefore
no sufficiently large parameter choice certified by the paper's displayed
McDiarmid/union-bound event can satisfy `beta<H(N)`, even if `F` is allowed to
vary with `q`.

This is a scoped certificate closure.  It does **not** exclude a deterministic
Hermitian construction, a sharper concentration/discrepancy argument at the
much lower density `p=O(sqrt(log q)/q)`, or the finite open `H_3` problem.
The arithmetic replay is
[`hermitian_certificate_gate.result.json`](hermitian_certificate_gate.result.json).

## 6. Mechanism fingerprints and cycle audit

| cycle | family / representation | central lemma | search object and checker | observed obstruction |
|---|---|---|---|---|
| 1 | protected K4-free owner; minimal Ramsey core | triangle-free nonadaptable links need at least ten edges | complete `geng` link census; two criteria plus direct definition | degree-ten vertices collapse to ten link types, but degree-nine vertices and exact ambient `beta` remain |
| 2 | retained cross-owner triangle hypergraph | Property B can replace owner-local arrowing | cyclic 88-clause seed; custom NAE + two SAT engines | Property B succeeds, but its shadow is `K11` |
| 3 | signal-sender occurrence lift | forced edge-colour parity copies variables | complete connected K4-free census through order eight; two SAT engines | no sender through order eight; standard lift needs 209 copies |
| 4 | Hermitian random-block geometry | small owner maxcut plus concentration | proof-level replay of Theorem 1.2 and equation (8) | certificate density forces degree above the #151 scale |

These are four substantive cycles across local structural theory, hypergraph
Property B, constraint gadgets, and finite geometry/probability.  Cycles 1 and
4 are proof-directed; cycles 2 and 3 pursue the counterexample direction.

## 7. Claim ledger

### PROVED (ordinary mathematical dependencies stated)

- Protecting every edge of an owner core forces all other owner-support
  intersections to be independent; final neighbourhoods in the core are
  independent for vertices outside the protected owner's full support.
- Equations (2.2)--(2.4) and the listed `n=50` integer cases.
- The cyclic distance decomposition uniquely partitions `E(K11)` into five
  triangle-free `C11` owners.
- A triangle-free graph with maximum cut strictly below `2m/3` is not
  three-colourable.
- The implication chain (5.1)--(5.5), conditional on the displayed event and
  the standard Ramsey asymptotic.

### COMPUTATIONALLY CHECKED

- All 31 triangle-free `delta>=2`, `m<=9` link graphs are universally
  adaptable by the definition; first obstructions occur at ten edges.
- The exact ten obstruction types through eleven edges.
- The cyclic 88-triangle family has Property B, no selected `K4`, and complete
  shadow `K11`; three independent UNSAT checks agree.
- No K4-free disjoint-edge triangle signal sender exists through order eight;
  the order-eight negative is independently reproduced by Glucose and
  CaDiCaL on every parity query.

### OPEN / CONJECTURAL

- Existence of a protected K4-free arrowing core compatible with all `n=50`
  degree, link, independence, and exact-beta constraints.
- Existence of a sparse K4-free realization of the cyclic or Hermitian
  cross-owner Property-B mechanism at the #151 `beta` scale.
- Novelty of the adaptable-colouring proof and the ten-type `n=50` refinement.
  The ten-triangle conclusion itself was already present in the campaign, and
  this packet makes no novelty claim for any part of the refinement.

### FAILED OR SCOPED CLOSED

- Tiny (`<=8`-vertex) K4-free signal senders.
- Direct independent maxcut certification inside the `K9` owners of `H_3`.
- The published Hermitian McDiarmid/union-bound certificate as an asymptotic
  #151 counterexample certificate.

## 8. Progress vector and successor packet

```text
verified local dependency/refinement gates:   3
exact cross-owner escape witnesses replayed:  1
small sender orders completely excluded:      <=8
n=50 saturated link types remaining:          10
actual #151 candidates:                        0
exact beta/tf3 candidate audits required:      none (no candidate)
priority confidence:                          high for June-2026 Hermitian collision
novelty confidence on new local theorem:       unclaimed / needs dedicated search
```

The next cycle should not repeat owner catalogues, random block sampling, or
generic CEGAR.  It should take one of these two sharper objects:

1. **Finite protected-core incidence solver.**  Variables are a K4-free
   minimal arrowing core with degrees `8..10`, the ten permitted links at every
   ambient degree-ten vertex, independent D1 support intersections, the
   support-qualified boundary-neighbourhood condition above, and the five
   cases in (2.3).  Independence and maximal-clique constraints belong to the
   ambient graph, not to the non-induced core.  The evaluator must include two
   independent arrowing solvers and an exact ambient `beta` checker; `tf_3` is
   only an optional sufficient certificate.
2. **Low-density Hermitian discrepancy lemma.**  Replace the cellwise
   McDiarmid event with a global arrowing argument that works at
   `p=O(sqrt(log q)/q)`.  Any proposed lemma must be tested first against the
   11-variable cyclic seed and then against the exact degree lower bound
   `beta>=Delta`.

Status remains `CONTINUE_PACKET`, not a global unresolved or exhausted verdict.

## 9. Reproduction

From the workspace root:

```powershell
.\.venv\Scripts\python.exe research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\threshold8_links.py --triangle-free --max-edges 11 --direct-limit 11 --output research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\k4free_links_through11_direct.result.json

.\.venv\Scripts\python.exe research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\n50_protected_core_interface.py --census research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\k4free_links_through11_direct.result.json --output research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\n50_protected_core_interface.result.json

.\.venv\Scripts\python.exe research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\cross_owner_propertyb.py --output research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\cross_owner_propertyb.result.json

.\.venv\Scripts\python.exe research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\signal_sender_atlas.py --output research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\signal_sender_atlas.result.json

.\.venv\Scripts\python.exe research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\signal_sender_order8.py --geng .tmp\nauty-env\Library\bin\geng.exe --output research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\signal_sender_order8.result.json

.\.venv\Scripts\python.exe research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\hermitian_certificate_gate.py --output research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\hermitian_certificate_gate.result.json
```

No git operation, publication, deletion, external message, or claim of a full
solution was made.

## 10. Primary sources

1. P. Hell and X. Zhu, *On the adaptable chromatic number of graphs*, European
   Journal of Combinatorics 29 (2008), 912--921, Theorem 2.1 and Corollary
   2.1, [publisher page](https://www.sciencedirect.com/science/article/pii/S0195669807002065).
2. A. Bikov, *Small minimal (3,3)-Ramsey graphs*, Theorem 8.2 and Figure 13,
   [arXiv:1604.03716](https://arxiv.org/abs/1604.03716).
3. E. Mulrenin and S. van Overberghe, *Some remarks on Folkman graphs for
   triangles*, version 4, 18 June 2026,
   [arXiv:2506.14942v4](https://arxiv.org/abs/2506.14942v4), plus the authors'
   [`quasiFolkman` repository](https://github.com/Steven-VO/quasiFolkman).
4. V. Chvátal, *The minimality of the Mycielski graph*, Lecture Notes in
   Mathematics 406 (1974), 243--246,
   [DOI 10.1007/BFb0066446](https://doi.org/10.1007/BFb0066446).
