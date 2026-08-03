# Root-style adversarial audit: threshold six and the seven-regular order-28 consequence

Date: 2026-08-03

Audited manuscript: `REPORT.md`, SHA-256
`723b53ffdad240cba0aebd8b124f18039f5ee049c556ef799a4fe39472c14bdf`.

This audit was reconstructed from the mathematical definitions and the cited
primary sources.  The discovery scripts and their output were not used as
evidence.  They may remain useful as regression tests, but none of the PASS
verdicts below depends on them.

## Verdict

**Threshold-six theorem: PASS.**  I found no gap in the minimal-core,
signed-link, disconnected-link, six-edge classification, `K4`-link,
Brooks, or pullback arguments.  The result can be stated equivalently as:

> Every graph which arrows `(3,3)` has a vertex contained in at least seven
> triangles.

**Seven-regular order-28 consequence: CONDITIONAL PASS.**  It follows from
the threshold-six theorem and the separately audited regular swap/two-walk
package exactly as stated.  The regularity hypothesis is essential to the
two-sided swap.  The argument does not eliminate mixed degree profiles.

**Priority: PARTIAL COLLISION, not a theorem collision found.**  Bikov's
published marked-neighborhood framework is the same local extension idea,
and Bikov's five-vertex table already contains the bowtie as `N5.1` and the
seven-edge `Djs` graph as `N5.2`.  Thus neither the marked/signed-link idea
nor those small local obstructions should be advertised as new.  I found no
primary source that states the threshold-six theorem or its exact
seven-triangle contrapositive.  That negative search is evidence, not a
priority guarantee.

**Publication readiness: mathematically ready after minor revision, but not
ready for an unqualified novelty announcement.**  A short note may present
the threshold-six statement as a new corollary/synthesis, explicitly credit
Bikov for the marked-neighborhood local analysis and Hell--Zhu for the
adaptable-colouring characterization.  The order-28 corollary should be
presented only with its complete campaign hypotheses or omitted from a
standalone note.  In the current repository it is also subsumed as campaign
progress by the stronger, separate `order28_36.md` package, so it is better
viewed as an alternate structural proof than as the leading frontier claim.

No FAIL verdict below concerns mathematical validity.  The only FAIL is a
priority/wording boundary: claiming the local bridge or the bowtie/Djs
classification as novel would be false.

## Claim-by-claim audit

| ID | Claim | Verdict | Reason |
|---|---|---|---|
| A1 | Triangle-hypergraph property-B equivalence | PASS | The vertices of the 3-uniform hypergraph are exactly the graph edges, and its hyperedges are exactly graph triangles. |
| A2 | A minimal arrowing core is connected and every core edge is in at least two core triangles | PASS | Componentwise good colourings prove connectedness.  A good colouring of `Q-e` extends when `e` is in zero or one triangle. |
| A3 | Signed-link/adaptable-colouring bridge | PASS | For a triangle `vxy`, monochromaticity is exactly `f(x)=f(y)=c(xy)`.  A good colouring of `Q-v` therefore induces a bad adaptable signing of the link. |
| A4 | Use of Hell--Zhu Theorem 2.1 | PASS | The cited theorem says a connected graph is adaptably 2-colourable iff deletion of some edge leaves a bipartite graph.  The manuscript uses exactly this equivalence. |
| A5 | Minimum degree and disconnected-link reduction | PASS | Link degree at `x` counts core triangles on `vx`, hence is at least two.  Adapted colourings factor by components, so a bad component exists; a six-edge bad component exhausts the edge budget. |
| A6 | Six-edge obstruction classification | PASS | The hand enumeration is complete.  The only connected, minimum-degree-two graphs with at most six edges for which no edge deletion is bipartite are `K4` and the bowtie. |
| A7 | `K4` link is impossible | PASS | It induces a `K5`; each of its vertices already lies in six internal triangles.  Any external core edge supplies at least two additional triangles, so connectedness forces `Q=K5`, which is not arrowing. |
| A8 | Bowtie links imply nonarrowing | PASS | Every vertex then has degree five.  Brooks gives `chi(Q)<=5` because the connected 5-regular graph is neither `K6` nor an odd cycle.  Pulling back the standard good colouring of `K5` is valid because a proper vertex colouring maps every triangle to three distinct colours. |
| A9 | Threshold-six theorem | PASS | Follows from A1--A8 without computational evidence. |
| B1 | Seven-regular order-28 pointwise bound `t_v<=7` | CONDITIONAL PASS | Re-derived from the regular swap and two-walk count; details below.  It is not valid under the manuscript's proof for arbitrary mixed degrees. |
| B2 | Threshold six forces equality at one core vertex | PASS | Some core vertex has at least seven core triangles, while every ambient vertex has at most seven; hence both counts equal seven and every ambient triangle through that vertex is a core triangle. |
| B3 | Exact seven-edge signed-link classification | PASS | Independently hand-classified below: the only connected, minimum-degree-two bad links through seven edges are `K4`, bowtie, `Djs`, and two triangles joined by a bridge. |
| B4 | Joined-triangles case is impossible | PASS | Its six core-link vertices plus one ambient isolate give `l_v=1`, whereas `u_v>=12` and `u_v<=6l_v`. |
| B5 | `Djs` equality and injection saturation | PASS | `l_v=2` forces `u_v=12`; equality in the two capacity bounds gives two six-element routed sets and makes all seven incident edges at each routing vertex triangle-free. |
| B6 | Independent eight-set contradiction | PASS | `X_a` is independent; a second isolated link vertex `b` and any `Djs` vertex `c` are nonadjacent to `X_a` and to each other. |
| B7 | Scope boundary | PASS | The manuscript expressly does not infer the mixed-profile or full #151 result. |
| P1 | Signed-link/marked-neighborhood method is new | PRIORITY FAIL if claimed | Bikov Definition 3.3 and Proposition 3.4 already formalize the same nonextendable-neighborhood mechanism.  The manuscript currently acknowledges this, which is correct. |
| P2 | Bowtie/Djs local classification is new | PRIORITY FAIL if claimed | Bikov Figure 12 and Theorem 8.1 already list them as `N5.1` and `N5.2` in the marked-neighborhood setting. |
| P3 | Exact threshold-six theorem is already published | NOT FOUND | Targeted primary-source and exact-phrase searches found no statement of it.  This is not a proof of priority. |

## Independent reconstruction of the threshold-six proof

Let `G` satisfy the six-triangle bound and suppose that it arrows `(3,3)`.
Choose an inclusion-minimal arrowing subgraph `Q`.

### Minimal-core facts

If `Q` were disconnected and no component arrowed, good colourings of the
components would combine.  If one component arrowed, it would be a proper
arrowing subgraph.  Thus `Q` is connected.

For an edge `e`, minimality gives a good colouring of `Q-e`.  If `e` is in
no triangle, colour it arbitrarily.  If it is in one triangle, colour it
opposite to the common colour of the other two edges when they agree, and
arbitrarily otherwise.  Thus every core edge lies in at least two core
triangles.

Fix `v` and a good colouring `c` of `Q-v`.  Put
`L_v=Q[N_Q(v)]`.  Give each link edge `xy` its colour `c(xy)` and identify
the proposed colour of spoke `vx` with a link-vertex colour `f(x)`.  The new
triangle `vxy` is monochromatic exactly when

`f(x)=f(y)=c(xy)`.

Since the colouring cannot extend, this edge signing has no adapted
two-colouring.  Hence `L_v` is not adaptably 2-colourable.  Also
`deg_L(x)` is the number of core triangles on edge `vx`, so every link has
minimum degree at least two.  Finally `e(L_v)` is the number of core
triangles through `v`, and is at most six.

Adapted colourings factor across components.  A nonadaptable link therefore
has a nonadaptable component.  Under minimum degree two, the six-edge
classification below shows that such a component already has six edges;
there can be no second component.

### Six-edge classification

For a connected simple `L` with `delta(L)>=2`, write `n=|V(L)|` and
`m=|E(L)|`.  Then `n<=m<=6`.

- At `n=6`, necessarily `L=C6`.
- At `n=5,m=5`, necessarily `L=C5`, and deleting any edge makes a path.
- At `n=5,m=6`, the degree sequence is either `(4,2,2,2,2)`, which is the
  bowtie, or `(3,3,2,2,2)`, which is a theta graph.  Its path lengths are
  `(2,2,2)` or `(1,2,3)`.  The first graph is bipartite; in the second,
  deleting an edge of the length-two path removes both odd cycles.
- At `n=4`, the cases `m=4,5,6` are `C4`, `K4-e`, and `K4`; deletion of the
  shared edge makes `K4-e` bipartite.
- At `n=3`, only `K3` occurs and deleting one edge leaves a path.

Hell--Zhu therefore leaves only `K4` and the bowtie as nonadaptable links.

### Global finish

If a link is `K4`, its centre and neighbors induce `K5`.  Each of those five
vertices is already in six internal triangles.  An external core edge would
be in at least two further core triangles, violating the hypothesis.  The
`K5` is therefore a component, and connectedness forces `Q=K5`.  The
red-`C5`/blue-complement-`C5` colouring shows that `K5` is not arrowing.

Every link is consequently a bowtie, so `Q` is connected and 5-regular.
It is not `K6`, and a 5-regular graph is not an odd cycle.  Brooks gives a
proper five-colouring.  Map `Q` properly to `K5`, give `K5` its standard
good two-edge-colouring, and pull the colours back.  The three vertices of
every triangle have distinct proper colours, so their image is a triangle
of `K5` and is not monochromatic.  This contradicts arrowing.

The threshold-six theorem is proved.

## Independent seven-edge classification

This is included because the order-28 consequence should not rely on a
discovery enumeration.  Let `L` be connected, simple, minimum-degree two,
with at most seven edges, and suppose no edge deletion makes it bipartite.
The at-most-six case was just classified.

For `m=7`:

- `n=7` gives `C7`, which becomes bipartite after an edge deletion.
- At `n=6`, the total degree excess above two is two.  The graph is a
  subdivision of a figure-eight, a theta, or a dumbbell.  A seven-edge
  figure-eight has cycle lengths three and four, hence has an edge meeting
  its only odd cycle.  In a theta graph the two odd cycles, when present,
  share one of the three branch paths; deleting an edge of that path leaves
  only the even cycle.  A dumbbell fails the deletion test only when it is
  exactly two triangles joined by one bridge.
- At `n=5`, the complement has three edges and maximum degree at most two.
  Excluding a `K4` in `L`, the complement is one of `P4+K1`, `K3+2K1`, or
  `P3+K2`.  The first gives `Djs`.  In the second all triangles share the
  edge joining the two universal vertices, whose deletion leaves `K2,3`.
  In the third the two triangles share one edge, and deleting it again
  leaves `K2,3`.
- A proper connected extension of `K4` with minimum degree two needs at
  least two new edges, so no seven-edge fifth-vertex case containing `K4`
  was omitted.

Thus the four obstruction types through seven edges are exactly `K4`, the
bowtie, `Djs`, and two triangles joined by a bridge.

## Independent reconstruction of the seven-regular order-28 consequence

Assume the separately audited inputs: `G` has order 28, is 7-regular,
`beta(G)<=7`, and every bad 8-set gives the regular two-sided swap.

Fix `v`, let `t=t_v`, and let `c(v,x)` count common neighbours with a
nonneighbor `x`.  There are 20 nonneighbors, and counting nonbacktracking
two-walks from `v` gives

`sum_x c(v,x)=7*6-2t=42-2t`.

Every nonneighbor has at least one common neighbor.  If `u` of them have
exactly one, the remaining terms are at least two, so

`42-2t >= u+2(20-u)`, hence `u>=2t-2`.

If `x` has unique common neighbor `a` with `v`, the regular two-sided swap
makes both `va` and `ax` triangle-free.  Let `l_v` be the number of isolated
vertices in `G[N(v)]`, equivalently the number of triangle-free edges at
`v`.  Routing each unique pair through its `a` gives

`u <= sum_{a isolated in G[N(v)]}(l_a-1) <= 6l_v`.

All link edges lie among the other `7-l_v` link vertices, so

`t <= binom(7-l_v,2)`.

Combining `2t-2<=u<=6l_v` with this last inequality over
`l_v=0,...,7` yields `t<=7`.

Let `Q` be a minimal arrowing core.  Threshold six gives a core vertex `v`
in at least seven core triangles.  Since ambient `t_v<=7`, its core and
ambient triangle counts are exactly seven, so the ambient link contains
exactly the core-link edges.  The seven-edge classification leaves `Djs`
or joined triangles (the six-edge cases cannot have seven link edges).

Joined triangles use six link vertices, leaving one ambient isolate.  Thus
`l_v=1`, contradicting `u>=12` and `u<=6`.  In the `Djs` case there are two
isolates `a,b`; hence `l_v=2` and all inequalities are equalities:
`u=12`, with six unique-pair vertices routed through each of `a,b`, and
`l_a=l_b=7`.

Call the six vertices routed through `a` the set `X_a`.  All edges from `a`
to `X_a` are triangle-free, so `X_a` is independent.  Choose a vertex `c`
of the `Djs` component.  The isolate `b` is nonadjacent to `c`.  Neither
`b` nor `c` is adjacent to a vertex `x` of `X_a`, since either would be a
second common neighbour of `v,x` in addition to `a`.  Therefore

`X_a union {b,c}`

is an independent eight-set, contradicting `beta(G)<=7`.

The inference uses regularity twice: first to make both swap edges
triangle-free, and then to cap each routing capacity by six.  The manuscript
correctly refuses to apply it to mixed degree profiles.

## Priority audit and exact sources

### Direct source checks

1. **Hell--Zhu.** Pavol Hell and Xuding Zhu, *On the adaptable chromatic
   number of graphs*, European Journal of Combinatorics 29 (2008), 912--921,
   DOI <https://doi.org/10.1016/j.ejc.2007.11.015>.  The publisher's full
   text states Theorem 2.1: for connected `L`, adaptable 2-colourability is
   equivalent to the existence of an edge whose deletion leaves `L`
   bipartite; Corollary 2.1 gives the componentwise form.  This exactly
   supports Sections 3--5 of the manuscript.

2. **Bikov.** Aleksandar Bikov, *Small minimal (3,3)-Ramsey graphs*, Ann.
   Univ. Sofia Fac. Math. Inform. 103 (2016), 123--147; primary preprint
   <https://arxiv.org/abs/1604.03716>.  Definition 3.3 and Proposition 3.4
   (paper pp. 6--7) introduce marked vertex sets and show that every
   neighborhood of a vertex in a minimal Ramsey graph is marked.  Figure 12
   and Theorem 8.1 (paper p. 18; PDF page 18) give the three five-vertex
   `K4`-free marked graphs.  Visual edge inspection identifies `N5.1` as the
   bowtie and `N5.2` as `Djs`.  This is a direct priority collision for the
   local framework and small obstruction identities, though not for the
   global threshold-six statement.

3. **Bikov thesis.** Aleksandar Bikov, *Computation and Bounding of Folkman
   Numbers*, PhD thesis (2018), primary preprint
   <https://arxiv.org/abs/1806.09601>.  Section 8.7, Theorem 8.37 and Figure
   8.10 repeat the five-vertex marked-neighborhood classification and say it
   was published in the 2016 paper.  No threshold-six or seven-triangle
   theorem appears in the searchable thesis text.

4. **Brooks.** R. L. Brooks, *On colouring the nodes of a network*, Proc.
   Cambridge Philos. Soc. 37 (1941), 194--197, DOI
   <https://doi.org/10.1017/S030500410002168X>.  Its classical theorem gives
   the exact chromatic bound used in Section 6.2.

5. **Recent Folkman boundary.** Z. R. Hassan, S. Radziszowski, and S. Van
   Overberghe, *On Small Folkman Graphs Arrowing K2 or K3*, primary preprint
   <https://arxiv.org/abs/2605.16542> (submitted 15 May 2026).  The
   introduction observes that `J4`-free graphs cannot edge-arrow `(3,3)`
   because each edge is in at most one triangle, and its Theorem 2 again
   records that a minimal witness has every edge in at least two triangles.
   It does not state the vertex-at-most-six threshold.

### Search result and novelty boundary

Targeted searches on 3 August 2026 covered exact variants of
"every vertex lies/belongs in at most six triangles", "every `(3,3)`-Ramsey
graph has a vertex in seven triangles", minimal-Ramsey marked neighborhoods,
and adaptable-colouring applications to Ramsey triangle arrowing.  Searches
also inspected Bikov's 2016 paper and 2018 thesis, Hell--Zhu's publisher full
text, and the May 2026 Folkman preprint above.  No exact threshold-six
statement was found.

The defensible novelty wording is therefore:

> Combining the marked-neighborhood viewpoint for minimal `(3,3)`-Ramsey
> graphs with the Hell--Zhu characterization yields the following short
> corollary: an edge-arrowing graph has a vertex in at least seven triangles.

Do not claim that marked neighborhoods, signed-link extension, the bowtie,
or `Djs` are new.  Before an arXiv priority claim, a human expert should also
search citation descendants of Bikov 2016 and non-English minimal-Ramsey
literature; the present search cannot rule out an obscure equivalent
corollary.

## Required manuscript revisions before circulation

1. In Section 5, replace "`C4`, `K4-e`, and `K4` up to the irrelevant
   addition pattern at four edges" with the unambiguous statement that the
   connected minimum-degree-two four-vertex, four-edge graph is exactly
   `C4`.

2. Add the hand seven-edge proof above, or cite it as a lemma, if the
   order-28 consequence remains.  The present sentence "the seven-edge
   signed-link classification gives four types" should not rest on a
   discovery enumeration in a public proof.

3. Strengthen the attribution paragraph: explicitly say that Bikov's
   `N5.1` is the bowtie and `N5.2` is `Djs`, and that the signed-link bridge
   is an adaptable-colouring restatement of his marked-neighborhood
   extension condition.

4. State Brooks' odd-cycle exception explicitly, then dismiss it because
   `Q` is 5-regular.  The current inference is correct, but one sentence
   would make the black-box application complete.

5. Keep the order-28 claim visibly conditional on the regular swap/two-walk
   package.  Cite the audited input snapshot, for example
   `research/erdos151/general/AUDIT.md` at SHA-256
   `7be768c800ce6c8903a7e2090f90c2f7e19dfe5865c0388cbd0a44266146a6ee`.

6. Do not market the seven-regular order-28 corollary as the campaign's
   strongest current order-28 result: the repository contains a later,
   separate full order-28 exclusion package.  This does not affect the
   correctness of the corollary.

Subject to these changes and an expert priority check, the threshold-six
theorem is suitable for a short public research note.  It is significant
partial progress, not a solution of Erdos #151.

## Threshold-seven literature and source appendix (3 August 2026)

This appendix audits only the literature and exact black-box sources for
`THRESHOLD7_LINE_GRAPH.md`.  It does not replace the separate adversarial
proof audit of that note.

### Goldberg--Seymour: exact formulation and a citation correction

The black box used in Section 5 is source-exact.  The version of record is

G. Chen, G. Jing, and W. Zang, *Proof of the Goldberg--Seymour conjecture on
edge-colorings of multigraphs*, Journal of Combinatorial Optimization 50,
article 23 (2025), DOI
<https://doi.org/10.1007/s10878-025-01348-6>.

The publisher states, for every multigraph `H`,

`chi'(H) <= max{Delta(H)+1, ceil(Gamma(H))}`,

where `Gamma(H)` is the maximum of
`2|E(H[S])|/(|S|-1)` over odd vertex sets `S` of order at least three.  This
is exactly the density definition and inequality used in the candidate
proof.  The article was published on 26 September 2025 and has a publisher
correction, DOI <https://doi.org/10.1007/s10878-025-01372-6>, published on
19 December 2025 as Journal of Combinatorial Optimization 51, article 1
(2026).  The correction says that the original PDF had formatting errors,
replaces it with a corrected PDF, repairs the subject index, and corrects a
footnote on page 13; it does not alter Theorem 1.1.  A public manuscript
should cite the corrected version of the original article and may mention
the correction.

There is one definite bibliographic error in `THRESHOLD7_LINE_GRAPH.md`:
the first author is **Guantao Chen**, so `J. Chen` must be replaced by
`G. Chen`.

The full 2025 theorem is stronger than this application needs.  Guantao
Chen and Guangming Jing, *Structural properties of edge-chromatic critical
multigraphs*, Journal of Combinatorial Theory, Series B 139 (2019),
128--162, DOI <https://doi.org/10.1016/j.jctb.2019.03.004>, proves the
Goldberg conjecture whenever `Delta(H)<=39` (or the root has at most 39
vertices).  The later Goldberg--Seymour paper explicitly records this
consequence.  Since the candidate root has `Delta(H)=4`, that 2019 result
already gives the required conclusion: if `chi'(H)>=6=Delta(H)+2`, the
small-degree Goldberg theorem forces the chromatic index to be the density,
contradicting `ceil(Gamma(H))<=5`.  Thus `chi'(H)<=5`.  Citing the general
2025 theorem is correct; citing the 2019 small-degree theorem as the
actually sufficient input gives an older and narrower dependency.

### The clique cover to multigraph step is classical Krausz

The structural step in Section 4 is exactly the classical multigraph form
of Krausz's characterization, not merely reminiscent of it.  A convenient
source stating the exact form is Theorem B of Z. Ryjacek and P. Vrana,
*A closure for 1-Hamilton-connectedness in claw-free graphs* (2013
preprint): a graph is the line graph of a multigraph if and only if it has a
system of cliques in which every vertex lies in exactly two cliques and
every edge lies in at least one clique.  That source also gives the same
intersection-multigraph construction and attributes the theorem to

J. Krausz, *Demonstration nouvelle d'un theoreme de Whitney sur les
reseaux*, Mat. Fiz. Lapok 50 (1943), 75--85.

The candidate's direct construction is still preferable in the proof: it
makes parallel edges and the absence of loops explicit.  Priority wording
must nevertheless credit Krausz and should not describe the line-graph
recognition or root construction itself as new.  The potentially new step
is deriving the required Krausz clique system from the two surviving local
link types in a minimal `(3,3)`-Ramsey core.

### Searches in minimal-Ramsey and neighboring literature

Targeted searches covered combinations of `minimal (3,3)-Ramsey`, edge
Folkman, line graph, Krausz, chromatic index, Goldberg--Seymour, marked
neighborhoods, and the exact formulations "at most seven triangles" and
"at least eight triangles".  The following closest sources were inspected.

1. Bikov's 2016 paper source contains no use of `line graph`, `Krausz`,
   `chromatic index`, `Goldberg`, or `Seymour`.  Its marked-neighborhood
   framework and the bowtie/`Djs` local obstructions remain a genuine
   component-level priority collision, as recorded above, but it does not
   perform the `B/J -> Krausz root -> edge-colouring` closure.

2. Hassan--Radziszowski--Van Overberghe, arXiv:2605.16542 (15 May 2026),
   proves again that every edge in a minimal relevant arrowing graph belongs
   to at least two triangles.  Its searchable full text contains no `line
   graph`, `Krausz`, `chromatic index`, or `Goldberg` occurrence and no
   threshold-seven theorem.

3. The closest line-graph/Ramsey papers concern **clique colouring**, a
   different property.  In particular, G. Bacso, Z. Ryjacek, and Z. Tuza,
   *Coloring the cliques of line graphs*, Discrete Mathematics 340 (2017),
   2641--2649, DOI <https://doi.org/10.1016/j.disc.2016.11.011>, relates
   clique chromatic indices of line graphs to Ramsey numbers.  Clique
   colouring only requires each maximal clique to be nonmonochromatic; it
   does not supply the proper five-colouring of `Q=L(H)` used here and does
   not ensure that every triangle of `Q` is nonmonochromatic.  It is useful
   adjacent literature, not an overlap with the candidate theorem.

4. General structural papers on graphs with every edge in a triangle do
   produce line multigraphs in low-degree classifications, for example
   J. Pfender and G. F. Royle, *Quartic graphs with every edge in a
   triangle*, arXiv:1308.0081.  Their quartic classification is not the
   candidate's degree-five/six Ramsey core argument or its 4-regular root.

No source found in this sweep states that every `(3,3)`-Ramsey graph has a
vertex in at least eight triangles, or derives the same threshold-seven
conclusion through a 4-regular multigraph root.  As with the threshold-six
search, this is evidence of priority, not proof that no obscure equivalent
appears in non-indexed or non-English literature.

### Defensible priority boundary and required edits

If the separate proof audit passes, the defensible claim is:

> Combining the marked-neighborhood/adaptable-colouring analysis of a
> minimal `(3,3)`-Ramsey core with Krausz's line-graph characterization and
> a small-degree case of the Goldberg conjecture yields that an
> edge-arrowing graph has a vertex in at least eight triangles.

Do not claim novelty for Krausz's construction, the identity
`chi(L(H))=chi'(H)`, Goldberg--Seymour, the `K5` pullback, or the local
marked-neighborhood method.  Before circulation, Section 5 should (i)
change `J. Chen` to `G. Chen`, (ii) cite the publisher correction, or instead
use the already sufficient Chen--Jing 2019 theorem, and Section 4 should
(iii) cite Krausz's exact multigraph characterization.  The priority status
is **no exact threshold-seven theorem found; several ingredients are
classical and the local framework is partially pre-existing**.
