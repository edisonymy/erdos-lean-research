# Priority search: sigma-19 / C16 exclusion

**Search date:** 2026-08-03 UTC  
**Result:** no exact prior statement found; novelty remains unconfirmed.

## Statement searched

The exact target was:

> Every finite simple bipartite graph of minimum degree at least three with no
> `C4`, `C8`, or `C16` has neither bipartition class of size 19.

Equivalent search forms included a 19-point linear neighborhood hypergraph of
minimum point degree three, edge size at least three, with no incidence
quadrilateral and no simple eight-edge incidence polygon.

## Primary and near-primary sources checked

1. Nowbandegani--Esfandiari, *An Experimental Result on the
   Erdős--Gyárfás Conjecture in Bipartite Graphs* (CID 2011; author-uploaded
   copy):
   <https://www.researchgate.net/publication/312286036_An_Experimental_Result_on_the_Erdos-Gyarfas_Conjecture_in_Bipartite_Graphs>.
   This is the older total-order lower bound, commonly cited as 32; it does not
   state the 19-per-side exclusion.
2. Hu--Shen, *Erdős--Gyárfás Conjecture for P10-free Graphs*, arXiv:2308.05675,
   lines 12--14 of the introduction:
   <https://arxiv.org/abs/2308.05675>.  It cites the 32-vertex bipartite bound
   and contains no stronger part-size result.
3. Arjun Balaji's 2026 general SAT artifact:
   <https://github.com/ArjunBalaji79/erdos-gyarfas-min-degree-3>.  It excludes
   all minimum-degree-3 counterexamples through total order 31 and reports the
   general bound 32; it is not a side-size theorem.
4. Julius Tranquilli's cubic-bipartite artifact and preprint:
   <https://github.com/floor-licker/erdos-gyarfas-cubic-bipartite> and
   <https://doi.org/10.5281/zenodo.21695513>.  It proves that every *cubic*
   bipartite graph through order 58 has a `C4`, `C8`, or `C16`, hence a
   cubic-bipartite counterexample has order at least 60.  It does not cover
   arbitrary minimum-degree-3 graphs with unequal sides.
5. McKay--Afzaly, public exact extremal data for
   `H={C_odd,C4,C8}`:
   <https://users.cecs.anu.edu.au/~bdm/data/extremal.html>.  The table gives
   57, 58, and 60 extremal edges at total orders 38, 39, and 40.  It has no
   `C16`-refined table and no part-size-19 statement.
6. Gordon Royle's 2 November 2009 MathOverflow construction:
   <https://mathoverflow.net/questions/966/>.  It supplies the known
   38-vertex `F038A` graph.  The packet's model is exactly isomorphic to it and
   contains a `C16`.
7. Erskine--Griggs--Širáň, *Colouring problems for symmetric configurations
   with block size 3*, J. Combin. Des. 29 (2021), 397--423:
   <https://doi.org/10.1002/jcd.21773> and
   <https://oro.open.ac.uk/75716/14/75716VOR.pdf>.  It identifies the cyclic
   `19_3` configuration / `F038A`; it does not state the arbitrary-rank
   side-size exclusion.
8. The McKay--Afzaly data page was searched directly for `C16`/`C_{16}` and
   `{C4,C8,C16}`; no such table or statement occurs.

## Queries used

Exact and variant web/arXiv/GitHub/Zenodo/MathOverflow queries included:

- `"C4" "C8" "C16" bipartite "minimum degree" 3 graph`
- `"no cycles of length 4, 8, or 16" bipartite graph`
- `Erdos Gyarfas conjecture bipartite graph 40 vertices minimum degree 3`
- `site:arxiv.org Erdos Gyarfas bipartite C16 cycle`
- `"19" "Berge C4" "Berge C8" linear hypergraph`
- `"linear hypergraph" 19 vertices "minimum degree" 3 cycle`
- `"bipartition" 19 "Erdős-Gyárfás"`
- `site:github.com "C4" "C8" "C16" bipartite "minimum degree"`
- `site:zenodo.org "C4" "C8" "C16" bipartite graph`
- `configuration "no quadrangles" "no octagons" Levi graph`
- `"19_3" configuration octagon`
- `2026 Erdős Gyárfás conjecture bipartite lower bound counterexample`
- `"bipartite counterexample" "at least 40" graph cycle power of 2`

No query produced the exact theorem or an equivalent arbitrary-rank
19-point incidence result.

## Collision analysis

The **order-40** consequence must not be claimed as the novel item.  From the
McKay--Afzaly table, a minimum-degree-3 `{C4,C8}`-free bipartite graph cannot
have total order 39, while the only extremal order-38 graph is the known
`F038A`; its `C16` is independently explicit.  Thus total order at least 40 is
already implicit in public data.

The certificate proves more: it excludes a 19-vertex bipartition class even
when the opposite side has anywhere up to 57 vertices.  Neither the total-order
table nor the cubic-bipartite order-60 result implies this for arbitrary
minimum-degree-3 graphs.

## Priority verdict

`PLAUSIBLY_NEW_PENDING_SPECIALIST_CONFIRMATION`.

This is deliberately weaker than a novelty claim.  Before a preprint or issue
announcement uses “new”, ask at least one specialist in configurations or
extremal bipartite graphs (for example Gordon Royle, Brendan McKay, or Tomaž
Pisanski) whether the exact part-size statement or its hypergraph equivalent
has appeared in a non-indexed census or table.
