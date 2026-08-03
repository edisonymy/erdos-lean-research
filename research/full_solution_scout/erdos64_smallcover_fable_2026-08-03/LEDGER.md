# Erdős #64 small-cover attack — append-only research ledger

**Agent:** Fable long-horizon research session, started 2026-08-03 (UTC).
**Directory:** `research/full_solution_scout/erdos64_smallcover_fable_2026-08-03/`
**Status header discipline:** every entry is appended, never edited. Claims are
tagged `[PROVED]`, `[COMPUTED]` (machine-checked, replayable), `[HEURISTIC]`,
or `[CONJECTURE]`.

---

## Entry 1 — 2026-08-03 ~19:40 UTC. Reconnaissance summary

Read: README, target rerank report, `erdos64_theory_max_2026-08-03`
(incidence-kernel public note + finite window), `erdos64_nonhamiltonian_cubic`
packet (order-22 full census, marked-edge/one-defect-block reduction, triangle
terminal reduction), `erdos64_counterexample_pulse` (order-32 annealing wall of
C16 witnesses), `experiments/erdos64` (K4 8-sheet S8 permutation covers all
UNSAT; GP/named/cyclic-cover sweeps negative), issue #9 + 3 comments.

Directories named in the tasking but absent locally
(`erdos64_long_horizon_max`, `erdos64_theory` bridge file,
`erdos64_constructive_max`, `erdos64_marked_sat_max`): not on origin/main
either — presumed concurrent agents' unpushed work. I work from committed
state.

External frontier (fresh check, 2026-08-03, sources in Entry 2):

- General minimum-degree-3: no counterexample with n <= 31
  (ArjunBalaji79/erdos-gyarfas-min-degree-3, SAT-Modulo-Symmetries + Glasgow
  subgraph propagator; unrefereed, no independent certificates). Baseline
  n >= 17 Royle–Markström ~2004 (published).
- Cubic: >= 30 (Markström, published); campaign census: all connected cubic
  through order 22 have empty dyadic edge core (stronger; no marked edge).
- Bipartite: >= 32 (Nowbandegani–Esfandiari, published experimental).
- Cubic bipartite: >= 60 (floor-licker repo + Zenodo, unrefereed,
  certificate-backed per its README).
- Classes where conjecture is proved: planar claw-free (Daniel–Shauger),
  3-connected cubic planar (Heckman–Krakovski 2013), P8-free, P10-free
  (Hu–Shen 2024), P13-free (2025), diameter-2 (Carr 2025, C4-or-C8).
- Carr arXiv:2605.22844 (May 2026): minimal counterexample >= 4/7 cubic.
  Campaign strengthens to d >= 2a+6, and d >= 2a+7 unless a in {3..10}
  (equality window orders 15..36); n >= 37 => d >= ceil((2n+7)/3).
- Liu–Montgomery (odd cycle problem paper): exists absolute constant K such
  that average degree >= K forces a power-of-2 cycle. No girth-based version
  at min degree 3. Sudakov–Verstraëte consecutive-even-lengths needs average
  degree >= 192(k+1): inapplicable to cubic. So high-girth cubic is NOT
  covered by known theorems.
- Markström: four 24-vertex cubic graphs with no C4/C8 whose only dyadic
  cycles are C16s (incl. the planar "Markström graph").

## Entry 2 — sources for Entry 1 (accessed 2026-08-03)

- https://github.com/ArjunBalaji79/erdos-gyarfas-min-degree-3 (README fetched
  raw; SMS table n=17..31 all UNSAT, times to 7351 s at n=31).
- https://github.com/floor-licker/erdos-gyarfas-cubic-bipartite (via campaign
  RESULTS.md; Zenodo DOI 10.5281/zenodo.21695513).
- arXiv:2605.22844 (Carr, predominantly cubic).
- arXiv:2508.19302 (Carr, diameter-2, Aug 2025).
- arXiv:2410.22842 (long induced paths / P13-free line).
- arXiv:0707.2117 (Sudakov–Verstraëte, Cycle lengths in sparse graphs).
- arXiv:2312.09999 (Győri–Li–Salia–Tompkins–Varga–Zhu: no 0 mod 4 cycles =>
  <= floor(3(n-1)/2) edges; used by campaign finite-window note).
- Wikipedia Erdős–Gyárfás page; dwest openp page (403-blocked; content via
  search snippets only).
- erdosproblems.com/64: proxy-blocked this session; campaign packets record
  it OPEN as of 2026-08-03 with proposers expecting a negative answer.
- WebSearch runs (2026-08-03): "Erdős–Gyárfás 2025 2026 preprint",
  "Liu Montgomery girth power of two", "Sudakov Verstraete cycle lengths
  sparse graphs", "Markström cubic 30 cages", "quadrilateral-free
  configurations n_3", "Erdős-Gyárfás bipartite one side vertex cover".
  None surfaced a resolution claim or the small-cover family below.

## Entry 3 — hypothesis selection: the small-cover family

**Observation A [PROVED, elementary].** If G has an independent set L with
|V(G) \ L| = sigma, then every simple cycle of G has length <= 2*sigma
(a cycle cannot visit two L-vertices consecutively).

**Consequence.** A graph of minimum degree >= 3 whose complement-of-cover
size sigma <= 15 can only contain dyadic cycles of lengths 4, 8, 16.
If it avoids those three lengths it avoids ALL powers of two
(2*15 = 30 < 32): it is a full counterexample to Erdős #64.

**Observation B [PROVED, elementary].** In such a G, distinct L-vertices
have <= 1 common S-neighbour (two common neighbours give a C4), i.e. the
L-neighbourhoods form a linear hypergraph on S; each L-vertex has degree
>= 3, so it consumes >= 3 of the C(sigma,2) point-pairs. Hence
|L| = m <= C(sigma,2)/3 <= 35 for sigma = 15, and n = sigma + m <= 50.
With the (unrefereed) SMS frontier n >= 32 one needs m >= 32 - sigma, so
3*(32 - sigma) <= C(sigma,2), forcing sigma >= 12. The bipartite sub-case
(S independent too) is exactly: a linear hypergraph on sigma <= 15 points,
edge sizes >= 3, minimum point-degree 3, whose incidence graph avoids C8
("no quadrilateral of lines") and C16 ("no octagon of lines"), while C6
(triangles of lines), C10, C12, C14 are allowed. Triangle-permitting but
quadrilateral-free partial linear spaces are NOT a standard studied family
(generalized polygons kill triangles first; Feit–Higman does not apply to
irregular incidence structures).

**Why this is new leverage.** (i) All prior exhaustive searches (SMS n<=31)
are parameterized by total order n and hit a wall at 31; this family is
parameterized by sigma <= 15 and is finite (n <= 50) BEYOND the wall.
(ii) No published or repo lane restricts by vertex cover / small side.
(iii) A hit is immediately a certified counterexample (two independent
cycle checkers planned). (iv) An exhaustive UNSAT closes a clean infinite
class (all graphs with cover <= 15... precisely: any counterexample must
have every independent set of size >= n-11... exact statement to be fixed
when results exist) — either outcome is informative.

**Plan.**
1. Stage 1 (pure bipartite, uniform triples): SAT, sigma in 12..15,
   static C4 linearity + static C8 quadrilateral clauses via collinearity
   variables, CEGAR for C16. All line sizes = 3 first.
2. Stage 2: variable line sizes >= 3 (u_j used-line indicators).
3. Stage 3: general core (edges inside S allowed; mixed cycles handled by
   CEGAR over the actual graph; static mixed-C4 clauses).
4. Stage 4 (if all UNSAT): sigma = 16..19 with C32 = 16-ring exclusion
   added; and/or convert the UNSATs into a human counting proof.
Verification standard: any SAT model is frozen raw, hashed, rebuilt as an
edge list, and checked by two independently written cycle enumerators plus
`experiments/erdos64/verify_graph.py`.

## Entry 4 — Stage 1+2 results (pure bipartite): UNSAT, plus a hand proof

`sat_search.py` (static C4-linearity + static C8-quadrilateral clauses via
collinearity/triple-collinearity variables, C16 CEGAR, u-prefix + double-lex
symmetry breaking, CaDiCaL):

- sigma=12: UNSAT, 0.74 s, 0 CEGAR iterations
- sigma=13: UNSAT, 1.28 s, 0
- sigma=14: UNSAT, 4.36 s, 0
- sigma=15: UNSAT, 6.49 s, 0

Positive control [COMPUTED]: identical encoding minus the C8 clauses at
sigma=12 is SAT (14 lines, verified C4-free, C8 present by the driver's DFS),
so the base encoding is not vacuously contradictory.

**Bridge-counting lemma [PROVED, to be written up carefully].** In a linear
3-uniform hypergraph whose incidence graph is C8-free:
for ANY two distinct lines L, L', at most one pair (q in L\L', q' in L'\L)
is collinear — otherwise two disjoint "bridges" M1, M2 between L and L'
form a genuine quadrilateral (linearity forces all lines distinct and the
four corners distinct).  Counting bridge triples (M; {q,q'} in M; L∋q, L'∋q')
each collinear pair {q,q'} lies in a unique line and contributes
(r_q-1)(r_{q'}-1) bridges, all landing on distinct line pairs {L,L'}:
   sum_{collinear pairs} (r_q-1)(r_{q'}-1) <= C(m,2).
With point degrees r >= 3 (pure bipartite!) and (a-1)(b-1) >= 2(a-1)+2(b-1)-4:
   LHS >= 4 sum_p r_p(r_p-1) - 12m >= 4 sigma rbar(rbar-1) - 12m,
rbar = 3m/sigma.  This gives C(m,2) >= 36m^2/sigma - 24m, i.e.
sigma >= 72m/(m+47); with m >= sigma (from degrees >= 3) this forces
**sigma >= 25** for 3-uniform pure-bipartite.  The weak form
(each collinear pair contributes >= 4) already gives m >= 25, killing
sigma=12 (m <= 22 by pair budget) by hand, matching the solver.

Consequence [PROVED modulo the size->=4 general case + hostile audit]:
no Erdős–Gyárfás counterexample is bipartite with a 3-uniform side and
other side of size <= 24.  The solver UNSATs at sigma<=15 cover general
line sizes >= 3, so the sigma<=15 statement holds unconditionally
(solver-trust; DRAT replay queued as hardening work).

**Decision:** pure bipartite small-side is closed.  The live target is
Stage 3: cover S of size <= 15 WITH internal edges (non-bipartite core).
There the point-side line-degrees can drop below 3 (core edges supply
degree), and the bridge-counting obstruction dissolves.  Cycles are still
<= 2 sigma <= 30, so {4,8,16}-avoidance still suffices for a full
counterexample.  C4 exclusion stays static (core C4s, 2-core-path +
collinear endpoints, linearity); C8 and C16 move to CEGAR over the decoded
mixed graph.  Line-side symmetry breaking only (row breaking would interact
with core edges unsoundly).

## Entry 5 — CORRECTION of Entry 4's bridge-counting lemma

Hostile re-audit of my own lemma found an error.  Two bridges between the
same line pair that SHARE an endpoint create a C6 (three lines, three
points), which is allowed, not a C8.  Only bridges with all four endpoints
distinct force a quadrilateral.  A maximal intersecting family of bridge
pairs between two 3-element line remainders is a star of size <= 3, so the
correct inequality is
   sum_{collinear pairs} (r_q-1)(r_{q'}-1) <= 3*C(m,2),
and the derived bound weakens from sigma >= 25 to sigma >= 9 (3-uniform
pure bipartite).  The claimed hand kill of sigma=12 via m>=25 is withdrawn;
the weak form now gives only m >= 9.

Status after correction:
- The four solver UNSATs (sigma=12..15 pure bipartite) STAND as solver
  results; the static C8 encoding was re-audited and forbids exactly the
  genuine quadrilaterals (an endpoint-sharing bridge pattern involves only
  3 points and triggers no 4-subset clause).
- Hardening queued: (i) sigma=9,10,11 probe runs, which must be UNSAT if
  the encoding and the published n>=17 / unrefereed n<=31 exclusions are
  all consistent; (ii) DRAT-certified replay or an independent orderly
  enumeration for sigma<=13.
- Lesson recorded: treat my own counting lemmas as hostile; the first
  version survived one write-up pass and was still wrong.

## Entry 6 — second lane: the bipartite two-defect block [derivation]

**Claim [PROVED, double-checked hostile].** Let F be a bipartite graph on
sides X, Y with exactly one vertex u in X and one vertex v in Y of degree
2, all other degrees 3, and let F contain no cycle of length 4, 8, or 16
(automatically none longer than |F| <= 30, so no dyadic cycle at all).
Take two disjoint copies (F_i, u_i, v_i), add midpoints w_i adjacent to
u_i and v_i, and the bridge w_1w_2.  The resulting G is CUBIC and has no
power-of-two cycle:
 - cycles inside a copy avoiding w_i are cycles of F (non-dyadic);
 - cycles through w_i are (u_i - v_i path) + 2 edges; u,v lie in opposite
   colour classes so such paths are odd, giving odd cycles: never dyadic;
 - the bridge is a cut edge and lies in no cycle.
So F existing at any order <= 30 resolves #64 negatively.  Conversely this
is the bipartite specialization of the campaign's marked-edge criterion
with the Mersenne condition holding FOR FREE (bipartite H = F + uv has no
odd cycles).  Same-side defects are impossible: 3|X| - 2 = |E| = 3|Y|
has no integer solution (mod 3), which is why opposite-side — exactly the
parity that kills the Mersenne condition — is also the only option.

Degree-sum: |E(F)| = (3n-2)/2, exactly ONE more than the
Győri–Li–Salia–Tompkins–Varga–Zhu maximum floor(3(n-1)/2) for graphs with
no 0-mod-4 cycle: F must contain 0-mod-4 cycles (necessarily of lengths
in {12,20,24,28}) but sits at the extremal boundary — structurally the
right place to look.

Known-exclusion boundary: campaign census => no cubic bipartite H on
<= 22 vertices has a nonempty dyadic core, hence n_F >= 24.  The
floor-licker cubic-bipartite >= 60 result does not apply (F is not
regular; H = F+uv has dyadic cycles).  The unpushed concurrent
"marked-sat" agent searched general cubic marked edges (near-miss at
order 28 with two disjoint C4 obstructions per the tasking); the
bipartite two-defect encoding here is a different, strictly cleaner
criterion (no Mersenne clause, half the cycle lengths, biadjacency
variables) and is run at n_F in {24, 26, 28, 30}.

Search: `sat_search_twodefect.py`, h = n/2 in {12, 13, 14, 15}: exact
degree cards (one defect per side, pinned at index 0), static C4
(Zarankiewicz clauses), CEGAR C8/C16 batched, double-lex on non-defect
rows/cols.

## Entry 7 — two-defect ladder results and the n=70 flip point

CEGAR version (`sat_search_twodefect.py`): n=24: UNSAT 0.12s; n=26:
UNSAT 0.23s; n=28: UNSAT 0.46s; n=30: UNSAT 0.75s; n=32: UNSAT 1.4s;
n=34: UNSAT 3.5s; n=36: UNSAT 9.3s; n=38: UNSAT 26s (first C16 blocks
appear); n=40: timeout at 100s (126k C8 clauses).

Static-C8 version (`sat_search_linear.py twodefect`): n=30: UNSAT 0.33s;
n=40: UNSAT 70s, ZERO cegar iterations.  Positive control at h=13 without
quad clauses: SAT with a C8 present and no C4 (linearity operative).

**Consequences [COMPUTED, solver-trust]:**
- No bipartite two-defect block exists through n_F = 42 pending (n=42
  running).  Through n_F = 40 closed.  Via Entry 6 this kills the entire
  bipartite marked-edge mechanism through cubic host order 40 — far beyond
  the campaign's census bound (>= 24), in seconds rather than censuses.
- Every one of these UNSATs was carried by C4+C8 alone (C16 blocking
  first engaged at n=38 and never exceeded 128 clauses).

**Calibration [PROVED by example].** The Balaban 10-cage (and the other
two (3,10)-cages) minus any edge is a bipartite two-defect block with no
C4/C8 (girth 10) on 70 vertices.  Hence the C8-part of the ladder MUST
become satisfiable somewhere in 42 < n <= 70; the two-defect family there
is "girth->=10-or-C6-rich C8-free near-cubic bipartite", and the real
battle becomes C16/C32.  All three cages contain C16 (checked directly:
`checker_a.py` on LCF builds), so cage-minus-edge does not resolve
anything; a hit needs a C16-desert girth-10-ish object, orders ~56-70.
This defines this lane's endgame: h = 21..35 with full statics and long
budgets, watching where C8-UNSAT flips.

**Emerging phenomenon worth a theorem.** Across both lanes, near-3-regular
bipartite incidence structures that are C8-free but may be C6-rich die by
counting well below n=50.  "Quadrilateral-free, triangle-permitting"
partial linear spaces near 3-regularity appear to need >= 21+ points per
side (solver); the corrected bridge inequality proves only sigma >= 9.
A tight hand theorem here would kill marked-edge search spaces
structurally and stands alone as combinatorics.  Parked; solver evidence
suffices for campaign routing today.

## Entry 8 — h=21 closed; the unified extremal question

`sat_search_linear.py twodefect 21`: UNSAT in 352 s.  All C8s were dead
statically; CEGAR only saw 512 C16s in 2 iterations.  Two-defect blocks
are now excluded through n_F = 42, i.e. the bipartite marked-edge
mechanism has no host through cubic order 42.

Both lanes are instances of one extremal question with no literature I
can find (searched: "quadrilateral-free configurations", cages, girth):

  N(k) := minimum order of a bipartite graph with minimum degree 3
          except k vertices of degree 2, containing no C4 and no C8
          (C6 explicitly allowed).

Data so far: k=2: N(2) > 42 and N(2) <= 70 (any (3,10)-cage minus an
edge); k=0: N(0) <= 70 (cage itself); pure small-side runs give
"smaller side >= 16" for k=0.  The allowed-C6 relaxation makes this a
nonstandard "mixed-girth cage" problem; each h-rung UNSAT is new
territory.  For Erdős #64 the payoff is structural: any counterexample's
bipartite-ish substructures must be at least this large.

## Entry 9 — certified Theorem 1 (pure bipartite small side)

kissat-4.0.4 + drat-trim replays, all VERIFIED (`certify_pure_results.json`,
CNF/DRAT hashes recorded there; sigma=4 is a two-line hand argument):

**Theorem 1 [COMPUTED, DRAT-certified].** For sigma <= 15 there is no
linear hypergraph on sigma points with every point-degree >= 3 and every
edge of size >= 3 whose bipartite incidence graph is C8-free.
Equivalently: **every bipartite graph with minimum degree >= 3 containing
no C4 and no C8 has at least 16 vertices on each side** (so order >= 32).
The C16 constraint was never needed.  Corollary: every bipartite
counterexample to Erdős–Gyárfás has >= 16 vertices per side, already
because of the C4/C8 conditions alone; with (unrefereed) SMS n<=31 this
is tight-adjacent territory.  Dependencies: faithfulness of the encoding
(audited in Entries 4-5: exact quadrilateral clauses), the classical
soundness of double-lex + used-prefix symmetry breaking, kissat, and
drat-trim.  Symmetry-free certificates additionally exist for
sigma <= 8 (`certify_pure_nosym_results.json` in progress), removing the
double-lex dependency there; the rest queue in background.
