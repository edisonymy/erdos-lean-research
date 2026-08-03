# Erdős #64: small-cover and two-defect lanes — session report

**Date:** 2026-08-03/04 (UTC).  **Agent:** Fable long-horizon session.
**Status: no counterexample and no universal proof.  This report makes
no solution claim.**  It records two new finite counterexample families,
one DRAT-certified structural theorem, bounded closures of both families
at the stated orders, and exact derivations that reshape the marked-edge
search space.  The append-only log with sources, failures, and the
correction history is `LEDGER.md`.

## 1. New reductions

### 1.1 Small-cover family

If a graph G has an independent set L with |V \ L| = sigma, every simple
cycle of G has length <= 2*sigma.  Hence a minimum-degree-3 graph with
sigma <= 15 avoiding C4, C8, C16 avoids every power of two: a full
counterexample.  Distinct L-vertices share at most one neighbour (else a
C4), so L-neighbourhoods form a linear hypergraph on the cover S; with
|L| = m, linearity gives m <= C(sigma,2)/3 <= 35, so the whole family is
finite (n <= 50) and sits beyond the public SMS frontier (n <= 31),
which is parameterized by total order and stalled at 31.

### 1.2 Bipartite two-defect blocks (Mersenne-free marked edges)

For a BIPARTITE cubic host H with marked edge e, the campaign's
marked-edge criterion loses its Mersenne condition entirely: cycles
through the subdivided edge become odd.  Concretely, let F be bipartite
with exactly one degree-2 vertex per side (all other degrees 3) and no
C4, C8, C16 (n_F <= 30; add C32 up to 62).  Doubling F through midpoints
joined by a bridge yields a CUBIC graph with no power-of-two cycle.
Same-side defects are impossible by a mod-3 edge count; opposite-side
parity is exactly what kills the Mersenne obstruction.  |E(F)| sits ONE
edge above the Győri–Li–Salia–Tompkins–Varga–Zhu maximum for graphs with
no 0-mod-4 cycle, so F must contain 0-mod-4 cycles yet avoid 4, 8, 16,
32 — the extremal boundary where such graphs are scarcest.

## 2. Results

### 2.1 Certified: bipartite C4+C8-free graphs need 16+16 vertices

**Theorem 1.** For sigma <= 15 there is no linear hypergraph on sigma
points with all point-degrees >= 3 and all edge sizes >= 3 whose
incidence graph is C8-free.  Equivalently: every bipartite graph with
minimum degree >= 3 and no C4 and no C8 has at least 16 vertices in each
side.  Corollary: every bipartite Erdős–Gyárfás counterexample has both
sides >= 16, using only its C4 and C8 conditions.

Evidence: per-sigma CNF + DRAT certificates, kissat-4.0.4 solve,
drat-trim `s VERIFIED` (hashes in `certify_pure_results.json`; sigma=4
is a two-line hand argument; symmetry-free certificates for sigma <= 8+
in `certify_pure_nosym_results.json` remove the double-lex dependency
there).  The C16 constraint was never needed.  Encoding audit trail:
LEDGER entries 3-5 (includes one found-and-corrected error in my own
bridge-counting lemma and the exactness proof of the quadrilateral
clauses).  Remaining trust base: encoding faithfulness (audited),
double-lex + prefix symmetry soundness (classical), drat-trim.

### 2.2 Two-defect blocks excluded through n_F = 42+ (solver)

`sat_search_twodefect.py` (CEGAR) and `sat_search_linear.py` (static
quadrilateral clauses, CEGAR C16/C32) give UNSAT at every even
n_F = 24..42 (seconds up to ~6 minutes each; n_F=44 running).  Via 1.2
this kills the bipartite marked-edge mechanism for cubic bipartite hosts
through order 42, versus the campaign census bound of 24.  Calibration:
any (3,10)-cage minus an edge IS a C4/C8-free two-defect block on 70
vertices, so the C8-part of the ladder must flip SAT in 44 < n <= 70;
all three cages contain C16 (checked directly), so the surviving battle
there is C16/C32.  The floor-licker streaming architecture (girth
dichotomy + triangle-rooted canonical search, certificate-backed to 58
for cubic bipartite) is the right tool for n_F in [46, 70]; SAT rungs
continue meanwhile.

### 2.3 Small-cover, bipartite case: closed by Theorem 1

Pure bipartite small-cover counterexamples require sigma >= 16 by
Theorem 1, and sigma <= 15 was the whole family: closed.

### 2.4 Small-cover with core edges: in progress

With edges allowed inside the cover S, the point-side line-degrees can
fall below 3 and Theorem 1's counting dissolves.  Encoding v2: static
core-C4 / mixed-C4, static pure quadrilaterals, static t=3 mixed C8
shapes (both gap patterns (2,2,4) and (2,3,3), with degeneracy excuses
proven exact via conjunction expansion), CEGAR for t <= 2 C8s and
C16/C32, adjacent-transposition graph-lex on cover vertices.
sigma = 13, 14, 15 running at session end; sigma <= 12 caps n at 34 and
is mostly inside the (unrefereed) SMS n <= 31 zone, so it was deprioritized.

### 2.5 Voltage-lift sweep (lane 3)

Cyclic Z_m lifts of bipartite cubic bases (Heawood, Möbius–Kantor,
Pappus, Desargues, Tutte–Coxeter, K33, Q3) and Petersen at n <= 126,
exact girth + exact C8/C16/C32/C64 checks per lift.  Motivation: at
girth >= 9 the first two dyadic lengths die by girth, and no published
theorem covers min-degree-3 girth >= 9 (Sudakov–Verstraëte needs average
degree >= 192(k+1); Liu–Montgomery needs a large constant average
degree).  Cages die at C16 (checked: all three (3,10)-cages, both
(3,10)-relatives at 70, Balaban 11-cage pending, McGee and Tutte–Coxeter
die at C8).  Running at session end.

## 3. Negative controls and audit discipline

- Positive controls: dropping the C8 clauses makes sigma=12 (pure) and
  h=13 (two-defect) SAT with verified C8-present, C4-free models.
- sigma=9..11 probes are UNSAT, consistent with published n>=17 and SMS.
- One encoding leak (t=3 shape B) was detected by CEGAR histogram,
  diagnosed to a non-anchored degeneracy excuse, fixed by an exact
  conjunction expansion, and verified gone.
- My own first bridge-counting lemma was WRONG (endpoint-sharing
  bridges give C6, not C8); LEDGER Entry 5 records the correction.

## 4. What this changes for the campaign

1. Bipartite marked-edge search below order 44 is proven empty —
   redirect all marked-edge compute to nonbipartite hosts or n >= 44.
2. Any counterexample has no small vertex cover: bipartite side proven
   (both sides >= 16); general cover <= 15 pending the core runs.
3. The C8 wall is structural: "triangle-permitting quadrilateral-free"
   near-cubic incidence structures below ~44 vertices do not exist.
   The clean extremal question N(k) (LEDGER Entry 8) is worth a
   standalone paper and a hand proof.
4. High-girth famous graphs are dead ends (C16/C32 present); lifts must
   be sculpted, not found among cages.

## 5. Reproduction

All scripts are standard-library + PySAT; kissat and drat-trim build
from their public GitHub sources.  `certify_pure.py` regenerates and
verifies every certificate.  Each searcher prints one JSON status line
per run; raw logs are retained in this directory.
