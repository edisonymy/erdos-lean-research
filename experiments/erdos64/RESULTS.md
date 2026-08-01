# Erdős problem 64: structured-cover exploration

## Outcome

**No counterexample was found.** This directory records one bounded structured
search, not a solution of Erdős problem 64 and not a novelty or publication
claim.

The current public computational frontier already makes a general small-order
search redundant: `ArjunBalaji79/erdos-gyarfas-min-degree-3` reports SAT-based
UNSAT results for every order through 31, so any counterexample has at least 32
vertices. The separate `floor-licker/erdos-gyarfas-cubic-bipartite` artifact
reports that any cubic-bipartite counterexample has at least 60 vertices. Those
public projects are the appropriate sources for their claims; nothing here
supersedes them.

Links:

- <https://www.erdosproblems.com/64> (still marked falsifiable/open on 2026-08-01)
- <https://github.com/ArjunBalaji79/erdos-gyarfas-min-degree-3>
- <https://github.com/floor-licker/erdos-gyarfas-cubic-bipartite>
- <https://doi.org/10.5281/zenodo.21695513> (archived cubic-bipartite artifact)
- <https://github.com/zacharydgoodman/erdos-gyarfas-ladders>
- <https://github.com/rosharma719/erdos64>

The first repository's order-31 claim is unrefereed and does not currently
include independently checkable UNSAT certificates or complete raw solver
logs. It is still a public priority collision, so orders 30 and 31 are not
presented here as an unclaimed search range. The cubic-bipartite artifact is a
stronger collision within its special family and reports certificate-backed
exhaustion through order 58.

## Structured family tested

The exact experiment considers 8-sheeted permutation covers of `K4`, hence
cubic graphs on 32 vertices. Gauge-fixing the three edges of a star spanning
tree to the identity leaves three permutations of eight sheets, one for each
cotree edge.

Simultaneous relabelling of all sheets conjugates all three permutations. The
search therefore fixes the first cotree permutation to a canonical
representative of each of the 21 nonidentity conjugacy classes of `S8`.
`k4_lift_cegar.py` uses CaDiCaL through PySAT and a CEGAR loop:

1. row/column clauses make each cotree relation a permutation;
2. an exact rooted DFS finds a simple cycle of length 4, 8, 16, or 32;
3. a sound blocking clause says that at least one variable edge of that cycle
   must change;
4. the loop stops on a candidate, timeout, or solver `UNSAT`.

All 21 nonidentity cycle types returned `UNSAT`; iteration counts are retained
in `cycle_type_results.tsv`. The identity first-permutation case does not need a
separate run. An automorphism of `K4` fixing the star centre permutes the three
cotree edges transitively. If either other cotree permutation is nonidentity,
move it into the classified first slot (an orientation reversal only replaces a
permutation by its inverse, which has the same cycle type). If all three are
identity, the cover is eight disjoint copies of `K4`, each containing a
4-cycle.

This gives a reproducible computational exhaustion of this narrow structured
family. It does **not** settle arbitrary 32-vertex graphs.

## Critical limitation

The solver runs did **not** emit a DRAT or LRAT certificate, and no independent
proof checker verified their `UNSAT` conclusions. The CEGAR clauses and cycle
witnesses are inspectable, but the final solver exhaustions remain trusted
solver computations. Accordingly:

- do not call this a computer-assisted theorem;
- do not claim it as novel;
- do not cite it as extending the public frontier;
- treat it only as exploration that rules out a natural cover family, subject
  to rerun and stronger proof-certificate work.

If a future run returns a candidate, `verify_graph.py` is a separate,
standard-library-only exact checker. It validates simplicity and minimum degree,
then exhaustively checks every power-of-two cycle length at most the graph order.

## Environment and rerun

Observed environment:

- Windows / PowerShell
- Python 3.12.4
- `python-sat` / PySAT `1.9.dev7`
- solver backend `cadical195`
- no random seed: the exact CEGAR run is deterministic at the script level

From the workspace root:

```powershell
python -m pip install -r experiments/erdos64/requirements.txt
python experiments/erdos64/verify_graph.py --self-test
python experiments/erdos64/k4_lift_cegar.py
```

The full CEGAR rerun took roughly one minute on the exploration machine, though
solver ordering and timing can vary by build. A nonzero `--seconds-per-type`
turns it into an explicitly incomplete bounded run.

The wider exploratory sweep also tested named cubic graphs, generalized
Petersen graphs, cyclic covers of Petersen/`K4`/the triangular prism and the
other nonbipartite cubic bases on eight vertices, plus seeded random permutation
lifts. None produced a candidate. Those negative random/intermediate logs are
intentionally omitted because they are neither exhaustive nor independently
certifying.

## Independent audit

A separate agent reran the full 21-type `S8` computation and reproduced every
iteration count in `cycle_type_results.tsv` exactly (wall time 112 seconds on
the same machine). It also used independently written subset-DP cycle tests to
check:

- all 216 three-sheet `K4` covers at lengths 4 and 8;
- every first-witness cut against all 216 models (46,656 model/cut pairs);
- 600 random graphs at orders 8 and 10 for all applicable target lengths;
- 200 random ungauged five-sheet covers after explicit gauge isomorphisms; and
- 100 random identity-first cases under the leaf automorphism reduction.

No disagreement or unsound cut was found. These checks independently support
the encoding, reductions, and cycle enumeration. They do not remove the stated
CaDiCaL UNSAT-certificate trust boundary.
