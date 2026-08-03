# Priority audit: bipartite part-size bounds relevant to Erdős #64

**Audit date:** 2026-08-03 (sources searched through this date)  
**Status:** internal priority report; not a publication claim.  
**Question separated carefully:** for a bipartite graph `G=(X,Y)`, a
*total-order* lower bound on `|X|+|Y|` is not a lower bound on each of
`|X|,|Y|`.

## Target statements

**(A)** Every bipartite graph with minimum degree at least three and no
`C4` or `C8` has `min(|X|,|Y|) >= 19`.

**(B)** Every bipartite graph with minimum degree at least three and no
`C4`, `C8`, or `C16` has `min(|X|,|Y|) >= 20`.

The campaign's current evidence status is deliberately distinguished from
priority:

* (A) has a checked finite-reduction/certificate route in the local packet:
  choosing the smaller class as points turns the other class into a linear
  hypergraph with point degrees and line sizes at least three; an incidence
  `C8` is exactly the relevant four-point quadrangle.  The audited
  `sigma <= 18` exhaustion is therefore evidence for (A), conditional on
  the archived generator/certificates and their independent semantic audit.
* (B) is now **certificate-backed in the campaign**.  The final `sigma=19`
  formula excludes `C16` (on top of the static `C4,C8` constraints) and is
  UNSAT.  This is exactly the finite assertion needed for (B), not merely a
  search timeout or an incremental solver status.  Publication still
  requires the usual independent encoder/priority gates.

Neither status itself establishes novelty.  The literature findings below
are the priority evidence.

## Executive conclusion

I found no source stating (A) or (B), nor an equivalent variable-side-size
theorem for linear hypergraphs of minimum point-degree/rank three avoiding
the indicated incidence cycles.  That makes (A) a **plausibly new
strengthening**, and (B) a **plausibly new stronger strengthening**.  This
is a search-relative conclusion, not a guarantee of priority.  Before any
external release, obtain direct replies from at least Gordon Royle or
Brendan McKay and one configuration specialist.

## Campaign certification record for (B) (not a novelty claim)

The final frozen decision instance and independent reconstruction record:

| item | value |
|---|---|
| DIMACS variables / clauses | `85,498 / 381,858` |
| CNF SHA-256 | `2B78BD846EEF041355834C1A1EEF1D526E9F88F844DA624C9C40E5DF27E3AD02` |
| independently reconstructed base clauses | `381,346` |
| independently audited appended `C16` clauses | `512` |
| appended-block-file SHA-256 | `B0A854F41974C2FE740E5B9B80425D7238C07ADB3B292A32AB50854DCF15D9F1` |
| fresh single CaDiCaL DRAT bytes | `230,688,966` |
| fresh DRAT SHA-256 | `9995B9DC0EE484E525826F18D8D2C17448C466372C9B5C57D34F54E6F0A0F98E` |
| Linux `drat-trim` verdict | `s VERIFIED` |
| checker transcript SHA-256 | `CEF389F9182F86EB26C47B7DA0893ADD2D436D2D47A137E54BE379CD9FADCBE6` |

The reconstruction audit reports an exact clause match: 381,346 statically
generated clauses followed by the 512 independently checked simple-C16
blocking clauses.  The proof checker read the full proof and returned
`s VERIFIED`.  Thus the evidence now supports (B) as a certified finite
theorem.  It should nevertheless be released as a *part-size* result only
after its artifacts are durably archived and its exact statement has passed
the specialist priority queries below.

The minimum **total** order for the `C4,C8` version is already public and
should never be presented as new: it is 38.  The standard 38-vertex graph
is also prior.  Consequently a release must lead with the word
"part-size" (or "one bipartition class"), and explicitly say that it does
not give a counterexample to Erdős--Gyárfás.

## Exact prior results and what they do *not* prove

### 1. Royle's 2009 graph: prior construction, not a part-size theorem

On 2 November 2009, Gordon Royle gave an explicit **38-vertex cubic,
bipartite, vertex-transitive graph with no `C4` and no `C8`** in the
MathOverflow thread "Looking for cubic, bipartite graphs with girth at
least six and no cycles of length 8."

* Gordon Royle, answer of 2 Nov. 2009:
  <https://mathoverflow.net/questions/966/looking-for-cubic-bipartite-graphs-with-girth-at-least-six-and-no-cycles-of-len>

The page contains the full adjacency list.  Tomaž Pisanski's March 2010
answer identifies the graph as the Levi graph of a self-dual,
flag-transitive `19_3` configuration with triangles but no quadrangles.
Thus the construction has sides `19+19`; it gives equality in (A), but
does not prove a lower bound for arbitrary, possibly unbalanced,
minimum-degree-three bipartite graphs.

The local `sigma19_model.json` was independently checked to be isomorphic
to this graph.  It has `C16` and `C32`, so it is not an Erdős--Gyárfás
counterexample and supplies no obstruction to (B).

### 2. McKay--Afzaly exact extremal data: total order 38 is already implied

The public McKay--Afzaly *Combinatorial Data* table labels entries without
a `>=` sign as exact and tabulates extremal graphs for
`H={C_odd,C4,C8}`, i.e. bipartite graphs avoiding `C4` and `C8`.  It gives

| total order | maximum edges | number of extremals |
|---:|---:|---:|
| 37 | 54 | 1 |
| 38 | 57 | 1 |

Source: Brendan McKay and Narjess Afzaly, *Combinatorial Data*, section
`H={C_odd,C4,C8}`:
<https://users.cecs.anu.edu.au/~bdm/data/extremal.html>

Since `delta(G)>=3` forces `e(G)>=ceil(3|V(G)|/2)`, order 37 would require
at least 56 edges; the order-38 extremal is cubic.  Hence the table already
implies that the least **total order** is exactly 38.  It has no control on
the split `|X|+|Y|`: it cannot prove (A), because a graph with one class
at most 18 could have arbitrarily larger total order.

### 3. Configuration literature identifies the equality object, not the
variable-side theorem

Erskine--Griggs--Širáň study the Foster-census symmetric configuration
`F038A` and identify its cyclic `19_3` configuration (generated by
`{0,1,8}` modulo 19):

* Grahame Erskine, Terry Griggs, Jozef Širáň, "Colouring problems for
  symmetric configurations with block size 3," *Journal of Combinatorial
  Designs* **29** (2021), 397--423,
  <https://doi.org/10.1002/jcd.21773>.
  Open version: <https://oro.open.ac.uk/75716/14/75716VOR.pdf>.

This is important prior art for terminology and attribution.  It treats
the regular `19_3` equality object; it does not state the non-regular
minimum-part-size assertion (A), as far as the primary paper and its
searchable text show.

Pisanski et al., "The 10-cages and derived configurations," *Information
Processing Letters* **89** (2004), 77--81,
<https://doi.org/10.1016/S0020-0190(03)00110-9>, concerns the much
stronger triangle-*and*-quadrangle-free / girth-ten setting.  Its
70-vertex cubic cages are adjacent background only: a girth-ten result
must not be confused with forbidding only `C4` and `C8`.

### 4. Previously published Erdős--Gyárfás lower bounds are total-order
bounds

The 2011 workshop report by P. Salehi Nowbandegani and H. Esfandiari
advertised a bipartite counterexample lower bound.  Its accessible version
states at least 30 vertices, while the later peer-reviewed claw-free paper
cites their result as **at least 32 vertices** for a bipartite
counterexample:

* P. Salehi Nowbandegani and H. Esfandiari, "An experimental result on the
  Erdős--Gyárfás conjecture in bipartite graphs," CID 2011 workshop.
* P. Salehi Nowbandegani, H. Esfandiari, M. H. Shirdareh Haghighi, and
  K. Bibak, "On the Erdős--Gyárfás conjecture in claw-free graphs,"
  *Discussiones Mathematicae Graph Theory* **34** (2014), 635--640;
  <https://doi.org/10.7151/dmgt.1732>.

The latter explicitly describes the 32-vertex result as a bipartite
counterexample bound.  It is a total-order result and does not state a
lower bound for each bipartition class.  The local campaign must cite the
stronger 32 (not the workshop abstract's 30) when comparing its future
counterexample-only consequences.

### 5. Recent work checked

Searches through 2026-08-03 covered current arXiv/preprint pages, the
House of Graphs cubic-bipartite catalogues, and recent papers on restricted
Erdős--Gyárfás classes.  None returned (A) or (B).  In particular:

* Avery Carr, "Every Minimal Counterexample to the Erdős--Gyárfás
  Conjecture is Predominantly Cubic," arXiv:2605.22844 (13 May 2026),
  gives degree-structure restrictions for a globally minimal
  counterexample, not the bipartite part-size statements.
* Jonas Jakob Gebendorfer, February/March 2026 census work on cubic
  bipartite vertex-transitive girth-six graphs, checks a restricted family
  up to a catalogue limit and is not an all-bipartite part-size theorem.
  It should be cited only after checking the archived version and scope:
  <https://doi.org/10.5281/zenodo.18407849>.
* House of Graphs lists exhaustive counts of cubic bipartite graphs by
  order and girth.  Its girth condition excludes `C6` as well, so it is
  not a substitute for the present `C4,C8` or `C4,C8,C16` questions:
  <https://houseofgraphs.org/Cubic>.

The phrase "bipartite Erdős--Gyárfás function" in recent papers refers to
an edge-colouring parameter, not to cycles in minimum-degree-three
bipartite graphs; it is irrelevant to the priority of (A)/(B).

After the certificate for (B) completed, I repeated exact-phrase searches
for `C4,C8,C16` together with "bipartite", "minimum degree 3", "both
sides", and "Erdős--Gyárfás counterexample".  They returned no prior
mathematical statement of (B); the only potentially related hit was a
heuristic (non-exhaustive) 2025 AlphaEvolve experiment through order 40,
which neither proves a lower bound nor gives the variable-part-size result.

## Why the two target statements are not covered by the standard records

Let `S` be the smaller class.  Regard every vertex on the other side as a
hyperedge equal to its neighbourhood in `S`.  The assumptions give:

* every hyperedge has size at least three;
* every point has degree at least three;
* no `C4` makes the hypergraph linear; and
* no bipartite `C8` forbids a four-edge quadrangle in this incidence
  structure.

Statement (A) is exactly the claim that such a variable-rank,
variable-degree incidence structure needs at least 19 points.  The usual
`19_3` literature handles a highly symmetric equality case, while standard
girth/cage results also forbid the 6-cycles (configuration triangles) that
the present problem permits.  This is the genuine distinction to state in
any priority query.

For (B), a `C16` prohibition adds a longer incidence-cycle constraint.
No source found gave the exact threshold 20 in this variable-side setting.
The final formula is already UNSAT after the 512 independently audited
`C16` blocks, so no `C32` blocks are needed for statement (B) or for its
Erdős--Gyárfás corollary.  A hypothetical side-19 counterexample would have
to avoid both `C16` and `C32`, and has already been ruled out by the stronger
fact that no side-19 structure survives the `C16` prohibition alone.

## Recommended specialist priority queries

Ask a narrow yes/no question, supply the exact formulation, and ask for
both paper references and unpublished catalogue results.  Best first
contacts:

1. **Brendan McKay** (McKay--Afzaly exact extremal tables; the table page
   lists `brendan.mckay@anu.edu.au`).  Ask whether their generation/data
   already determines the *minimum smaller part* for `C4,C8`-free
   minimum-degree-three bipartite graphs.
2. **Gordon Royle** (the 2009 equality graph) and **Tomaž Pisanski**
   (configuration interpretation).  Ask whether the variable-rank,
   variable-line-size condition has a configuration-theory name or known
   minimum.
3. **Grahame Erskine, Terry Griggs, Jozef Širáň**, authors of the 2021
   `F038A` configuration paper.  Ask specifically whether a theorem
   exists beyond symmetric `v_3` configurations.
4. **Klas Markström** and the authors of the 2011/2014
   Erdős--Gyárfás computational lower bounds, for the historical
   counterexample-search line and its possible unarchived data.

Suggested text:

> Is the following exact statement known?  If `G=(X,Y)` is bipartite,
> `delta(G)>=3`, and `G` has no `C4` or `C8`, must `min(|X|,|Y|)>=19`?
> We know the balanced 19+19 equality object (Royle/F038A) and the
> minimum *total* order 38 from the McKay--Afzaly table.  We are asking
> about arbitrary, possibly unbalanced, bipartitions.  A related possible
> extension additionally forbids `C16` and asks for threshold 20.

## Publication framing if priority is cleared

Use one of these precise formulations:

* For (A): "A certificate-backed part-size strengthening of the known
  order-38 threshold for bipartite `C4,C8`-free graphs of minimum degree
  three." 
* For (B): "A certified extension of the bipartite Erdős--Gyárfás search
  frontier: any bipartite counterexample has both bipartition classes of
  size at least 20." 

Avoid all of the following:

* "new 38-vertex graph" or "first 38-vertex example";
* "new minimum order 38";
* claiming novelty for (B) before the direct specialist priority replies,
  durable artifact archive, and independent candidate/encoding audit are
  complete; or
* saying either result resolves Erdős problem #64.

## Search limitations

This audit used exact-phrase searches, cited-paper backtracking, current
arXiv/preprint results, the MathOverflow thread, McKay--Afzaly data,
configuration/cage terminology, and catalogue pages.  It did not search
paywalled full texts exhaustively or private computational catalogues.  A
negative search result is therefore not proof of novelty; the specialist
queries above are a required release gate.
