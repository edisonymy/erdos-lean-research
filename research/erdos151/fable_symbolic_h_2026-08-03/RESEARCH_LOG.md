# Erdős #151 — symbolic-h lane (Fable, opened 2026-08-03)

Assignment: prove or disprove the conjecture itself (arbitrary order), not
another finite-order computation.  Hygiene: this directory contains only new
files; no Codex #151 file or run artifact is edited; no git operations.

Notation.  β(G) = largest admissible set (containing no inclusion-maximal
clique of size >= 2); τ = n − β; H(n) = min independence number over
triangle-free n-vertex graphs = max{h : R(3,h) <= n}.  Conjecture: β(G) >= H(n).

Inherited audited facts used (not re-proved here): induced monotonicity
β(G) >= β(G[W]); least counterexample lives at n = R(3,h) and has β = h−1;
Theorem A (counterexample ⇒ G → (3,3) edge-arrowing); recurrence
β(G) >= |I| + β(G − N[I]) for independent I; β >= Δ; β >= α.
Retired claims NOT used: private anchors, c < 2.4 average-anchor bound,
broad two-swap.

---

## 1. PROVED (this lane): symbolic degree/gap squeeze on a least counterexample

**Theorem G1 (minimum degree).**  If G is a least counterexample, of order
n = R(3,h), then every vertex satisfies

    n − R(3,h−1)  <=  d(v)  <=  h − 1 .

Proof.  Upper: β >= Δ and β = h−1.  Lower: by the recurrence with I = {v},
h−1 = β(G) >= 1 + β(G−N[v]); G−N[v] has order n−1−d(v) < n, so it is not a
counterexample and β(G−N[v]) >= H(n−1−d(v)).  Hence H(n−1−d(v)) <= h−2, i.e.
n−1−d(v) <= R(3,h−1) − 1.  ∎

So δ(G) >= R(3,h) − R(3,h−1) (the Ramsey gap).  Consistency check: at h = 10,
n = 41 this gives d ∈ [5,9] — exactly the campaign's audited finite fact; G1
is its arbitrary-h generalization.

**Theorem G2 (multi-vertex version).**  For every independent set I of size t
(1 <= t <= h−2) in a least counterexample,

    n  <=  R(3, h−t) − 1 + |N[I]|  <=  R(3, h−t) − 1 + t·h .

Proof.  h−1 >= t + β(G−N[I]) >= t + H(n − |N[I]|), so
n − |N[I]| <= R(3,h−t) − 1; then |N[I]| <= t(Δ+1) <= t·h.  ∎

Since α(G) >= n/h, this holds for all t up to ~n/h.  Corollary: a least
counterexample at parameter h forces the Ramsey deficit chain
R(3,h) − R(3,h−t) <= t·h − 1 for all such t.  Under the proved asymptotics
R(3,k) = Θ(k²/log k) the average gap is Θ(h/log h) << h, so G1–G2 do NOT
exclude counterexamples asymptotically; they are frontier constraints (and at
h = 10 they reproduce the known window).  Status: PROVED, non-decisive.

---

## 2. PROVED: triangle-free-cover certificate and its exact obstruction

**Lemma C1 (cover certificate).**  If J ⊆ G is triangle-free (as a graph on
V(G)) and every inclusion-maximal clique C of G with |C| >= 2 contains at
least one edge of J, then β(G) >= α(J) >= H(n).

Proof.  A maximum independent set S of J contains no C (C ∩ J-edge inside C
would lie in S); α(J) >= H(n) because J is triangle-free on n vertices.  ∎

Theorem A is the special case J = L ∪ R (L = edges in no triangle, R = one
color class of a good coloring): the campaign's reduction is exactly "G ↛
(3,3) ⇒ a cover exists".

**Lemma C2 (exact obstruction at ω = 3).**  Let ω(G) = 3 and every edge of G
lie in a triangle.  Then a cover J as in C1 exists **iff** G ↛ (3,3).

Proof.  (⇐) Theorem A's construction.  (⇒) Color J red, E∖J blue: J
triangle-free kills red triangles; every triangle is a maximal clique (ω=3)
and so contains a J-edge, killing blue triangles; hence G ↛ (3,3).  ∎

So the certificate method fails precisely on K4-free Folkman graphs — the
"universal transversal lemma" refutation the campaign recorded is this
statement.  Status: PROVED; fixes the exact boundary of the certificate
method.

---

## 3. PROVED: the Erdős–Rogers gateway, sharpened to equivalences

Let tf_s(G) = max size of a K_s-free induced subgraph.  Call G *purely
s-clique* if ω(G) = s and every maximal clique has size exactly s (every
edge extends to an s-clique, no (s+1)-clique).

**Lemma E1.**  If ω(G) = s then β(G) <= tf_s(G) (every admissible set induces
a K_s-free subgraph, since s-cliques are maximal).  If moreover G is purely
s-clique, β(G) = tf_s(G).

Proof.  First part: an s-clique inside an admissible S would be a maximal
clique inside S.  Second: a K_s-free induced S contains no maximal clique
(all have size s).  ∎

**Consequence E2 (family equivalences).**
- (a) A K_{s+1}-free graph with tf_s(G) < H(n) is a counterexample to #151.
- (b) Conversely, #151 restricted to purely s-clique graphs is exactly the
  statement  min{tf_s(G) : G purely s-clique on n vertices} >= H(n) — an
  Erdős–Rogers-type inequality (f_{s,s+1}-variant vs H).
- (c) s = 2 is the tight base case (triangle-free graphs: β = α, min = H(n)).
  #151 says s = 2 minimizes β over all clique structures.

By Theorem A, any G in (a) automatically arrows (3,3) — no separate check
needed.  Status: PROVED (elementary but organizing: the whole conjecture is
an infinite family of ER-vs-H constant races, one per clique pattern).

**Constants map (external inputs, cited not re-proved).**
- Shearer 1983: triangle-free with average degree d has α >= n·f(d),
  f(d) = (d ln d − d + 1)/(d−1)².
- **Lemma E3 (certifiable Ramsey bound).**  R(3,k) <= ceil(k / f(k−1)).
  Proof: on that many vertices, either Δ >= k (a neighborhood is an
  independent k-set) or average degree <= k−1 and α >= n f(k−1) >= k.  ∎
  Hence the *certifiable* floor H_cert(n) >= max{k : ceil(k/f(k−1)) <= n},
  which is (1−o(1))·sqrt(n ln n / 2), on top of the exact table for h <= 9.
- Fiz Pontiveros–Griffiths–Morris / Bohman–Keevash:
  R(3,k) >= (1/4 − o(1))k²/ln k, hence H(n) <= (√2 + o(1))·sqrt(n ln n).

So: TRUE H(n) = c_H·sqrt(n ln n) with c_H ∈ [1/√2, √2] (both ends open;
believed √2), and any *certified* finite counterexample only needs to beat
H_cert.  Refuting #151 asymptotically at ω = 3 needs a K4-free construction
with tf_3 <= (c < c_H)·sqrt(n ln n); proving even the ω <= 3 case needs a
new f_{3,4}-type lower bound of strength >= H.  Both sides sit on named open
problems (ER polylog + R(3,k) constant).  Status: the asymptotic race is
open in BOTH directions; this is the precise sense of the campaign's
"unknown constant comparisons".

---

## 4. FAILED ROUTES (logged so they are not retried)

- **F1 Random construction.**  G(n,p) with K4s repaired: at the arrowing
  threshold p = C/√n, α ≈ (1/C)·√n·ln n >> H(n) ≈ √(2 n ln n) — fails by a
  (ln n)^{1/2} factor for every p (dense K4-free graphs are near-tripartite
  with α >= n/3).  Pure randomness cannot reach α < H; counterexamples need
  optimal-Ramsey-quality independence.  FALSE route, computation-checked.
- **F2 Closure operations.**  Disjoint union (H subadditive), blow-ups
  (tf scales linearly, H like √t), joins (K_{a+b}-free side swallows a whole
  part) all move AWAY from counterexamples.  No counterexample can be built
  from smaller non-counterexamples by these ops.  PROVED-mini-lemmas.
- **F3 Pure independence squeeze.**  Trying to kill ω <= K counterexamples
  via sparse K_{K+1}-free independence bounds: with Δ <= h−1 and
  n >= (1/4−o(1))h²/ln h, Shearer-type gives only α >= Ω(h/ log log h) — off
  by Θ(log log h).  Cannot close without fundamentally better K4-free
  independence bounds (itself a known open frontier).  BLOCKED.
- **F4 Universal cover.**  "Every graph has a triangle-free maximal-clique
  cover" is FALSE (Lemma C2 + existence of K4-free Folkman graphs).  The
  certificate method cannot be universal; any proof must treat arrowing
  graphs by different means.

---

## 5. ACTIVE: finite Erdős–Rogers race (new global test, not a CEGAR rerun)

Design.  By E2(a) a single K4-free graph with tf_3 < H_cert(n) at ANY order
refutes #151 outright, with a fully elementary certificate chain
(K4-freeness + tf_3 bound + Lemma E3 arithmetic).  The campaign's finite
work (n <= 41) never probed the first certifiable windows n ≈ 171+, and no
known construction has been scored against H_cert.  Candidate generator:
degree-capped K4-free process (cap = h−1 as forced by G1/β >= Δ), which
dimensionally lands near the required (Δ, α, n) triple.  Measured per
sample: Δ, greedy/local-search lower bounds on α and tf_3 (a found
triangle-free induced set of size >= h kills the sample; a persistent stall
below h at both α and tf_3 escalates to exact methods).
Score targets (from Lemma E3): H_cert(171) = 20, H_cert(300) = 27,
H_cert(500) = 37, H_cert(847) = 51.

Kill criteria for this sub-lane: if across the n-grid every sample's
heuristic tf_3 reaches h easily (say within 200 restarts), record the
margins and declare the capped-process family dead (negative data retained);
escalate only on a sample whose best-found tf_3 AND α sit < h after full
search effort.

Expected outcome, stated in advance for calibration: α is predicted to land
at ≈ 1.3–1.7·h (F3 margin), i.e. samples die at the α gate; the value of the
run is the measured margin curve in n (how far constructions sit from the
refutation window, and whether the trend closes or widens with n).

### RESULT (2026-08-03, er_race.py, seeds/params in JSONs) — family KILLED

Capped process (cap = h−1, the forced regime since tf_3 >= Δ):

| n   | h_cert | edges | Δ  | α_found/h | tf_found/h | verdict |
|-----|--------|-------|----|-----------|------------|---------|
| 171 | 20     | 1624  | 19 | 1.450     | 3.850      | DEAD    |
| 300 | 27     | 3898  | 26 | 1.481     | 4.296      | DEAD    |
| 500 | 37     | 8996  | 36 | 1.405     | 4.378      | DEAD    |
| 847 | 51     | 21173 | 50 | 1.353     | 4.529      | DEAD    |

Pure process controls (no cap): n=300: Δ=67≈2.5h, α_found=26=0.96h;
n=500: Δ=92≈2.2h, α_found=32=0.87h (α improves with n) — but tf >= Δ >= 2.2h.

Reading: the two regimes fail on OPPOSITE gates.  At the forced degree
budget Δ <= h−1 the graph is locally sparse, so triangle-free induced sets
are enormous (tf ≈ 4.5h and WIDENING with n) and even α > h (calibration:
the pre-registered 1.3–1.7h prediction was correct).  Without the cap the
process reaches genuinely sub-h independence but overshoots Δ by 2.2x.
Conclusion: no process/random-type family can approach the window; a
refutation, if one exists, requires design-grade constructions in which
tf ≈ Δ ≈ α ≈ h simultaneously — exactly the open Erdős–Rogers construction
frontier.  Sub-lane closed under its pre-registered kill rule; negative data
retained in race_*.json.  Caveat recorded: tf_found is a heuristic lower
bound (in pure-process runs it landed below the trivial floor Δ), but every
DEAD verdict used only the sound direction tf >= tf_found >= h.

---

## 6. PROVED: local design condition on ω<=3 counterexamples (from the race)

**Theorem G3.**  Let G be K4-free on n vertices with tf_3(G) <= h−1 (the
ω<=3 counterexample regime; note Δ <= h−1 is automatic since every
neighborhood is triangle-free and induced).  Then:
(i) for every vertex v with d(v) = h−1 and every w ∉ N[v], the set
    N(w) ∩ N(v) contains an edge — the h-set N(v) ∪ {w} must span a
    triangle, which cannot lie inside the triangle-free N(v), so it is
    w plus an edge of G[N(v)] ∩ N(w);
(ii) hence e(G[N(v)]) >= (n−h)/(h−1) for every max-degree v, while G[N(v)]
    is triangle-free (Mantel: <= (h−1)²/4), and each edge xy of G[N(v)]
    serves at most |N(x)∩N(y)| <= α(G) common neighbors, N(x)∩N(y) being
    INDEPENDENT by K4-freeness;
(iii) so triangles are forced across every non-edge at max-degree vertices
    and forbidden across every edge — a design-like tension invisible to
    process/random models (their measured failure above is this theorem
    quantified).

Status: PROVED (elementary; no Ramsey input needed beyond the definition of
the window).  Use: a screening condition for any future candidate family —
check (i) before any expensive tf computation.  Caveat (5.6 audit,
accepted): (i) applies only to vertices of degree exactly h−1; it is not a
universal screen when Δ < h−1.

---

## 7. LITERATURE EVENT (2026-08-03): #151 is now a pure constant race

Operating-rule change (user directive): routes are killed by mathematics or
CPU budget only — never by human-calibrated effort estimates.

**(a) Morris–Sahasrabudhe–Verstraëte, arXiv:2607.16118 (17 Jul 2026):**
f_{s,s+1}(n) = Θ(sqrt(n log n)).  Upper bound: randomized "double blow-up"
— G* = A* ∪ B*, each of A,B a union of m random complete s-partite copies
(size l, blow-up r); deletion D1 = edges with both endpoints in two copies'
common territory; deletion D2 = one edge (minority family preferred) from
every triangle not inside a single copy.  All surviving triangles live
inside single s-partite copies ⇒ K_{s+1}-freeness is structural.  Written
threshold constant 2^40·s³ (proof-generous); finite behavior open.
The paper nowhere mentions #151 / Erdős–Gallai–Tuza — no collision.

**(b) Joret–Micek–Reed–Smid, arXiv:2006.11353 (EJC 2021):** every graph
with maximum degree Δ has a vertex coloring with O(Δ/log Δ) colors in which
no inclusion-maximal clique (size >= 2) is monochromatic; corollary
O(sqrt(n/log n)) colors on n vertices; both tight.  **A color class is
precisely an admissible set**, so

    β(G) >= n / χ_c(G) >= c · n·log Δ/Δ  and  β(G) >= c'·sqrt(n log n)

for ALL graphs — Erdős #151 is TRUE up to a multiplicative constant, by
published work that never mentions it.  Status: external-PROVED.

**Theorem R1 (the race, PROVED).**  Combining (a), (b), E2 and the Ramsey
constants: there are absolute constants c' <= C'' with
c'·sqrt(n log n) <= min_G β(G) <= C''·sqrt(n log n) (min over n-vertex
graphs), while H(n) = c_H·sqrt(n ln n), c_H ∈ [1/√2, √2] (open).  #151 is
exactly the assertion min_G β / H >= 1: a three-constant race with no
remaining structural mystery at the Θ-level.

**Theorem R2 (conditional resolution, PROVED conditional).**  Suppose the
JMRS bound holds in the effective form χ_c(G) <= C·Δ/ln Δ (Δ >= Δ0) — on
all graphs, or merely on the least-counterexample class (ω <= h, α <= h−1,
β = h−1, edge-arrowing (3,3)).  A least counterexample at parameter h has
h−1 = β >= n·ln(h−1)/(C(h−1)), i.e. R(3,h) = n <= C(h−1)²/ln(h−1).
Against R(3,h) >= (1/4−o(1))h²/ln h (Fiz Pontiveros–Griffiths–Morris /
Bohman–Keevash): **if C < 1/4 then #151 holds for all sufficiently large
h.**  Conversely a refutation must find graphs with β below H, i.e. beat
c_H ∈ [1/√2, √2] (certified: 1/√2 via Lemma E3).
Proof-side frontier = optimize the JMRS argument's constant on the
counterexample class; refutation-side frontier = tune the MSV construction
below H_cert at some finite n.  Both are now the SAME quantitative object
approached from two sides.

---

## 8. THE CONSTANT LEDGER (as of 2026-08-03) and the strategic reduction

Ramsey update: Campos–Jenssen–Michelen–Park (arXiv:2505.13371) proved
R(3,k) >= (1/3+o(1))k²/log k, and Hefty–Horn–King–Pfender
(arXiv:2510.19718, revised 2026-02-19) pushed it to

    R(3,k) >= (1/2 + o(1)) k²/log k ,

with 1/2 "conjectured to be asymptotically tight by multiple groups";
Shearer's upper constant 1 stands.  Consequences, all in sqrt(n ln n)
units:

| quantity | proved range | conjectured |
|---|---|---|
| H(n) constant c_H = 1/sqrt(2 c_R) | [1/sqrt2, 1] | 1 (if c_R = 1/2) |
| certified H floor (Lemma E3) | 1/sqrt2 | — |
| min_G β(G) constant (JMRS dual) | >= ~1/3 (explicit small) | ? |
| pure-3 class constant c* (E2) | [~1/3, MSV-tunable] | ? |
| JMRS class-coloring constant C | <= 1+ε (general graphs) | ? on class |

**Theorem R2', updated.**  If the clique-coloring bound χ_c <= C·Δ/ln Δ
holds on the least-counterexample class with C < c_R (currently C < 1/2),
then #151 holds for all sufficiently large h.  The general-graph value
C = 1 is TIGHT ONLY on triangle-free examples (Kim graphs via χ_c = χ and
Johansson–Molloy), and **triangle-free graphs never edge-arrow (3,3)**,
while every counterexample must (Theorem A).  So the class value of C is
genuinely unpinned: the gap between the general bound (1) and the needed
bound (1/2) is exactly a factor 2, and the obstruction examples are
excluded from the class.  This is the proof-side attack surface.

Dual formulation: everything is one number.  Let c* = liminf over the
pure-3 class (K4-free, every edge in a triangle) of β/sqrt(n ln n).
Proved: c* ∈ [~1/3, C_MSV].  #151 (pure-3, large n) ⟺ c* >= c_H.
Refutation-certified needs a finite graph with tf_3 < (1/sqrt2)-level
H_cert; refutation-true needs c* < c_H ∈ [0.707, 1].
Erdős's own hedge ("perhaps completely wrongheaded") is quantitatively
vindicated: the conjecture's truth plausibly depends on the final R(3,k)
constant, which is itself open.

**Failed estimate logged (resolvable-rounds design):** partitioning V into
disjoint tripartite copies per round (affine/Latin placements) and
covering h-sets round-by-round costs per-copy occupancy ~14 to make part-
missing unlikely; the induced degree budget forces n <= ~0.02·h²/ln h,
a factor ~25 below the required c_R·h²/ln h.  Simple resolvable designs
CANNOT reach the window; coverage must come from beyond-union-bound
mechanisms (as in MSV's actual proof).  FAILED (arithmetic, replayable).

## 9. ACTIVE: the small-n frontier band (n = 42..~87) — new exact attack

With PUBLISHED upper bounds R(3,10)<=41 [arXiv:2401.00392], R(3,11)<=50,
R(3,12)<=59, R(3,13)<=68, R(3,14)<=77, R(3,15)<=87 [arXiv:1210.5826; the
values used in any claim will be re-verified against the current survey],
the certified H(n) at small n jumps far above the Shearer floor: a
K4-free graph on 42 vertices with no admissible 10-set would already be a
FULL counterexample.  The campaign verified orders <= 39 (+40/41 partial).

Jump-structure correction (caught in self-audit): by induced monotonicity
a least counterexample sits at an H-jump, and H is flat on [41, 49]
(R(3,10) <= 41; R(3,11) >= 47-ish), so the campaign's unconditional
order-41 K4-free exclusion ALREADY implies the K4-free face is empty at
42..49 (delete vertices).  The (42,10) CEGAR run is therefore a
REPLICATION steel-check of that exclusion (SAT there would be a
definition-level counterexample AND an audit alarm).  The genuinely open
exact frontiers for certified counterexamples are the published-bound
pairs (n,h) = **(50,11)**, (59,12), (68,13), (77,14), (87,15) — a SAT
witness at any of them is a full counterexample regardless of leastness.
(50,11) production run launched: `cegar_face_n50.{json,log}`.

Feasibility arithmetic at n=42, h=10 (logged before searching):
- degree budget Δ<=9 ⇒ T (#triangles) <= n·Mantel(9)/3 = 280;
- covering LP (every 10-set contains a triangle) needs T >= C(42,3)/C(10,3)
  = 95.7 — LP-open with factor ~2.9 slack;
- edge-disjoint (uncrowded) triangle systems cap at T <= 42·4/3 = 56 < 96:
  **books are forced even at n=42** (consistent with the DLR analysis);
- deletion bound tf >= (2/3)n^{3/2}/sqrt(3T): kills T<=~150 but not T~280;
- coupon-collector: random placement mean coverage 2.9 vs needed ln C(42,10)
  ≈ 21 ⇒ any witness is a quasi-design (near-zero coverage variance).

Hunt results (2026-08-03):
- Circulant sweep n=42..60, ~1.7M circulants, all K4-free ones rejected by
  greedy (tf >= h immediately): cyclic symmetry structurally fails.  DEAD.
- SA over K4-free degree-capped graph space: n=42 stalls at tf ≈ 21 = 2.1h;
  n=49 at 26 = 2.6h.  Random-flavored search plateaus at the ~2x barrier
  across ALL families and scales (matches the union-bound arithmetic).
- MSV-shape scan (n=300/500): all DEAD, best tf/h ≈ 4.6 — the paper shape
  needs its asymptotic decoupling; at accessible n it UNDERPERFORMS the
  plain capped process.

**Exact decision (running): cegar_face.py** — SAT-CEGAR over graph space:
vars = edges of an n-vertex graph; constraints: no K4 + Δ <= h−1 (sound:
β >= Δ); lazy cuts kill every admissible h-set the exact oracle finds
(triple-vars force a triangle inside W, maximal-edge vars force a maximal
edge inside W).  UNSAT ⇒ certified: NO K4-free counterexample at order n.
SAT-CANDIDATE ⇒ a full counterexample (β <= h−1 < h <= H(n)).
Validated both directions: (10,4) UNSAT in 0.1s (known-true instance);
(10,5) SAT (C5-blowup-type β=4 exists).  Production run: n=42, h=10
(`cegar_face_n42.{json,log}`).  This decides the exact question the
heuristics could only stall on.

## 10. The locally-CBU economy: why every search stalls at ~2x, and the
## exact location of the open door

**Lemma B1 (PROVED).**  In the cleaned MSV graph (delete edges in no
triangle; tf unchanged) every link G[N(v)] is a vertex-disjoint union of
complete bipartite graphs.  Proof: D1 makes surviving edges belong to a
unique s-partite copy; D2 kills every cross-copy triangle; so the
triangles at v come only from v's own copies, whose traces on N(v) are
complete bipartite and pairwise disjoint; any edge between two different
copies' traces inside N(v) would form a cross-copy triangle with v,
which D2 removed.  ∎  Equivalently the graph is an edge-disjoint gluing
of complete tripartite blocks with no cross-block triangles.

**Heuristic floor F5 (union-bound arithmetic, labeled HEURISTIC but
replayable).**  For locally-CBU graphs with balanced blocks (part size a,
t blocks per vertex, degree D = 2at), covering all k-sets by
block-transversals under the first-moment/union bound needs
t >= 3·ln(en/k) and a >= (ln 3)·n/k, hence D >= 6·ln3·(n/k)·ln(en/k);
with tf >= Δ = D this bottoms out at

    tf >= (1.8 + o(1))·sqrt(n ln n)

for ANY random-flavored placement.  Measured: capped process 4.2–4.5x,
SA at n=42..49 2.1–2.6x, pure process 2.2–2.5x, MSV-shape 4.6x —
the empirical ~2x wall IS this floor (plus finite-size losses).

**Where the door is open.**  The covering LP itself allows tf down to
~n^{2/5} (never binding), and in classical covering problems Rödl-nibble
methods close the gap from the union-bound floor to the LP floor — but
the nibble requires uncrowdedness, while the DLR bound (Section 5)
FORCES crowding (books) in any counterexample.  Quasi-design covering
under forced crowding is unexplored territory in both directions:
- if designs can beat the union-bound floor by factor ~2 in this
  economy, #151 is FALSE with certified finite counterexamples;
- if the floor is real for crowded systems, the pure-3 class constant is
  >= ~1.8 > c_H and the K4-free face of #151 is TRUE asymptotically.
The (50,11) CEGAR run is the smallest certified instance of exactly this
dichotomy.  This localizes Erdős #151 sharply: it is a design-existence
question at the crowded-covering frontier, sitting between the JMRS
constant (1), the R(3,k) constant (1/2..1, conjectured 1/2), and the
union-bound floor (~1.8).

## 11. THEOREM TCG (Two-Class Gate) — an exact finite gate for the
## pure-3 K4-free case, self-contained proof  [2026-08-03, appended]

Context: read after the other lane's ROOT_AUDIT and pure-core packet
(n50_protected_core_max).  Their 9-regular Brooks branch generalizes far
beyond regularity once a sub-Brooks chromatic bound for K4-free graphs is
available.  To avoid citation risk the bound is proved from scratch.

**Lemma X1 (K4-free chromatic bound, self-contained).**  Every K4-free
graph satisfies χ(G) <= 3·ceil((Δ+1)/4).
Proof.  Lovász's decomposition theorem (1966): if d_1+...+d_k >= Δ−k+1
(equivalently Σ(d_i+1) >= Δ+1) then V partitions into V_1..V_k with
Δ(G[V_i]) <= d_i.  Take k = ceil((Δ+1)/4), all d_i = 3.  Each part is
K4-free with maximum degree <= 3, hence 3-colorable: by Brooks each
component needs > 3 colors only if it is K4 (excluded) — odd cycles and
all other Δ<=3 components take <= 3.  Total 3k colors.  ∎
Sanity: C5 (Δ=2): bound 3 ✓ (χ=3).  Δ=10: χ <= 9.
[The classical Borodin–Kostochka / Catlin / Lawrence bound
χ <= 3(Δ+2)/4 would sharpen h=13,14 below; citation not yet verified
from a primary source, so it is NOT used in the theorem. CONJECTURAL-
CITATION status; X1 suffices unconditionally elsewhere.]

**Theorem TCG (PROVED).**  Let G be a K4-free graph on n vertices in
which every edge lies in a triangle ("pure-3": the nontrivial maximal
cliques are exactly the triangles).  If β(G) <= h−1 for some h >= 4, then

    n  <=  (h−1) · q / 2,       q := 3·ceil(h/4)     (using Δ <= β <= h−1).

Proof.  β >= Δ (open neighborhoods are admissible), so Δ <= h−1 and
Lemma X1 gives a proper coloring with q colors.  The union of the two
largest classes has size >= ceil(2n/q) and induces a bipartite graph,
hence contains no triangle of G; purity leaves no other nontrivial
maximal cliques, so it is admissible: β >= ceil(2n/q).  With
β <= h−1: ceil(2n/q) <= h−1, i.e. n <= (h−1)q/2.  ∎

**Corollary TCG-1 (correct exact gate).**  Put
`B(h)=floor((h-1)*3*ceil(h/4)/2)`.  At every order with `H(n)=h`, a pure-3
K4-free counterexample must satisfy `n <= B(h)`.  In particular, a least
counterexample at the Ramsey jump `n=R(3,h)` is excluded whenever a proved
lower bound on `R(3,h)` is greater than `B(h)`.

The April 2026 *Small Ramsey Numbers* survey gives
`47 <= R(3,11) <= 50` and `53 <= R(3,12) <= 59`; since `B(11)=45` and
`B(12)=49`, TCG excludes the pure-3 jump for `h=11,12`.  It also gives
`61 <= R(3,13) <= 68`, `67 <= R(3,14) <= 77`,
`74 <= R(3,15) <= 87`, and `82 <= R(3,16) <= 97`, while the corresponding
bounds are `B=72,78,84,90`.  Thus the present data do **not** unconditionally
close the pure-3 jump for `h=13,14,15,16`; for `h=15,16` they close it only
if the unknown exact Ramsey number lies above 84 or 90 respectively.

Two earlier consequences are **false and withdrawn**: (i) the listed test
points `(87,15)` and `(98,16)` do not by themselves settle #151 at those
orders, because `H(n)` may already exceed the displayed `h`; and (ii) there
is no all-`n >= ~200` tail.  If `H(n)^2` is of order `n log n`, the gate
`n > 3H(n)^2/8` eventually fails rather than becoming automatic.  The exact
inequality must be checked at the actual `H(n)` (or at a rigorously bounded
Ramsey jump) in every application.  Honest scope: TCG is a finite band gate,
not a full pure-3 resolution.

**Corollary TCG-2 (sound constraint for the live (50,11) CEGAR — for
the owning lane to adopt if desired).**  Every K4-free graph on 50
vertices with β <= 10 contains at least one maximal edge (an edge in no
triangle).  Encodable as: OR over all 1225 pairs of m_uv with the
existing m-var semantics, or as an oracle-side prune.  More generally
their pure-core §2.1 (Δ=10 branch: saturation + κ + 550/3 divisibility)
follows in two lines from X1: χ <= 9, two largest classes >= ceil(100/9)
= 12 > 10 — no saturation input needed once every edge is in a triangle
(their edge-minimality gives edges in >= 2 triangles, which implies
pure-3).  Their §2.2 stands as the special case χ <= 9 via 9-regular
Brooks.

Falsification attempts before relying on TCG: (i) C5/odd-cycle sanity of
X1 (passes; earlier draft form (2/3)(Δ+2) for triangle-free FAILS on C5
— rejected); (ii) numeric spot-check of the mechanism on generated
pure-3 samples (two largest DSATUR classes admissible and >= 2n/q) —
test plan queued as tcg_check.py; (iii) the h=13,14 DIY gap is real
(3·ceil(13/4) = 12 gives threshold 72 > 68) and is reported as a GAP,
not silently bridged.

TCG mechanism test (tcg_check.py, 2026-08-03): 9 purified capped-process
samples, n ∈ {50,100,200}: DSATUR colors always <= X1 bound (5–9 vs
9–18), two-largest union always admissible and >= the TCG floor.
COMPUTATIONALLY CHECKED; no falsification.  Empirical bonus: generated
pure-3 graphs have χ ≈ Δ/2 — a pure-3 counterexample must push χ to the
X1 limit while keeping α <= h−1: compound tension, recorded.

## 12. M-burden theorem and the corrected final map  [appended]

**Theorem M1 (PROVED; proof invocation repaired by hostile audit).**  Let G
be K4-free on n vertices with β(G) <= h−1, let M be its set of maximal
edges, and put F=G−M.  Removing M changes no triangle.  For every v,
N_F(v) is ambient-admissible in G, so Δ(F) <= β(G) <= h−1.  Applying the
X1 colouring argument directly to F (not TCG, whose β(F) hypothesis is not
known) gives
tf_3(G) = tf_3(F) >= ceil(2n/q), q = 3·ceil(h/4);  and for EVERY
triangle-free induced set S of G:  τ(M[S]) >= |S| − (h−1)
(else deleting a vertex cover of M[S] from S leaves an admissible set
larger than h−1).  At (50,11): every witness has a triangle-free 12-set,
and every triangle-free 12-set carries a maximal-edge cover of size
>= 2.  The maximal-edge system must "burn" every large triangle-free
set — a quantitative slack-budget constraint bridging the finite
frontier and the strips.  (On the strips the burden is vacuous:
2n/q < h there.  Consistent.)

**FALSE-route note (caught before use):** applying the two-largest-
classes trick to a CLIQUE-coloring (JMRS) is invalid — admissible
classes do not union to admissible sets (triangles can cross two
triangle-free classes); the trick needs PROPER colorings (bipartite
unions).  The corrected consequences: pure-3 strips close under EITHER
(1) χ(K4-free) <= (1+o(1))Δ/ln Δ — the Johansson-type problem, currently
lnln-walled — OR (2) clique-coloring class constant < c_R (factor-2
war).  Not under "JMRS constant < 1".

**THE FINAL MAP (status of #151 after 2026-08-03).**  The problem is
three concentric constant problems plus a finite frontier:
(1) proper coloring of K4-free graphs at (1+o(1))Δ/ln Δ  [kills the
    pure-3 strips];
(2) clique-coloring constant < c_R on the arrowing class  [kills all
    large h];
(3) the R(3,k) constant c_R ∈ [1/2, 1]  [sets both targets; 1/2
    conjectured];
(4) the (50,11) K4-free face  [live authoritative CEGAR, other lane];
(5) the M-burden/slack interface  [Theorem M1 here + the owning lane's
    protected-core program].
Refutation lives only in: quasi-design coverings beating the
union-bound floor by ~2x under forced crowding (Section 10), or a SAT
witness at (4).  Proof lives in (1)/(2) — both are named hard open
problems, but (2) restricted to the arrowing class has no known tight
examples (Kim graphs do not arrow), so it is not provably blocked.

**ROOT PRIORITY/SCOPE CORRECTION (2026-08-03).**  The order-of-magnitude
statement `min beta = Theta(sqrt(n log n))` was already publicly recorded in
*A note on the clique-transversal number* (21 April 2026), which explicitly
uses JMRS and says the stronger Erdős--Gallai--Tuza conjecture remains open.
No campaign novelty claim attaches to R1.  JMRS is order-tight, not known to
have optimal leading coefficient 1.  Program Alpha's `chi_tf` route covers
only pure-3 graphs; maximal edges require a genuine clique-colouring or
admissible-cover bridge.  Also the current published Folkman range is
`21 <= F_e(3,3;4) <= 786`, not `[20,786]`.

## 13. Arrowing ⇒ vertex-arrowing; the vertex-Folkman interface  [appended]

**Lemma V1 (PROVED).**  If G → (3,3) (edge-arrowing) then V(G) admits no
partition into two triangle-free sets.  Proof: given such a partition,
color cut edges red, internal edges blue.  A triangle has an even number
of cut edges, never three, so no red triangle; a blue triangle lies
inside one side, which is triangle-free.  Good coloring ⇒ G ↛ (3,3).  ∎
(Equivalently: edge-arrowing implies vertex-arrowing for K3.)

Consequences for the (50,11) face: every witness is a K4-free
VERTEX-Folkman graph (no triangle-free 2-partition) with Δ <= 10 on 50
vertices.  Known: F_v(3,3;4) = 14 (small dense witnesses); the
bounded-degree question at Δ <= 10, n = 50 sits at the
Łuczak–Ruciński–Voigt vertex-Ramsey threshold scaling (Δ ~ sqrt(n)) —
open in both directions; no citation kill (checked: F_e(3,3;4) bounds
are [21, 786], no min-degree theorems found).

**TCG-3 (offered to the owning lane): sound cheap cut oracle.**  For any
CEGAR model graph, run a triangle-free-2-partition local search (minimize
internal triangles; accept at zero).  If a partition (A,B) is found, the
model is NOT a witness (V1 + Theorem A + H(50) >= 11 > 10), and the
sound structured cut is: OR of y_t over all triples t inside A plus all
triples inside B (some triangle must lie inside a side).  This prunes
non-arrowing models wholesale rather than one admissible set at a time.

Beta-directed M-aware SA at (50,11), 8 seeds x 400k steps
(sa_beta_long.log, 2026-08-03): best admissible-set proxy 20–21 vs
target 10 in every seed; all checkpointed states admitted triangle-free
2-partitions (non-arrowing).  The ~2x wall holds for the beta objective
with maximal-edge material available.  Negative preserved; SAT-side
hint generation from generic local search is now conclusively dead —
consistent with §10 (only quasi-designs or the CEGAR can reach the
window).

## 14. One-shot assessment under the standing directive  [appended]

A same-session full resolution requires either a SAT witness at a
certified frontier pair (which would simultaneously smash the Folkman
record F_e(3,3;4) <= 50 — strong evidence UNSAT) or a proof mechanism
uniform in h (provably entangled with the R(3,k) constant and the
Johansson/JMRS constants — Sections 7–12).  The rational maximal-
ambition allocation, executed now: (a) the class clique-coloring
constant (the only unblocked route to "true for all large h"); (b) the
finite frontier via the owning lane's CEGAR + my V1/TCG-2/TCG-3 cut
families; (c) a β-directed M-aware SAT-side design hunt (below) — the
single search family whose shape matches all forced structure (M != 0,
burden M1, degree band, no tf 2-partition).

**Dichotomy program (proof side, active).**  For pure-3 class graphs the
clique-coloring is a partition into triangle-free classes; the local
obstruction at v is a monochromatic edge in the (triangle-free) link
graph on N(v).  Covering arithmetic forces counterexamples into the
medium-dense link regime e(N(v)) ~ h²/(12 ln h) (far above the random-
coloring threshold ~h²/ln²h, far below Mantel h²/4).  Program: (i) dense
link chunks are near-bipartite blocks — handle structurally (few colors
per block); (ii) sparse remainder — uncrowded-hypergraph savings (DLR /
Frieze–Mubayi sqrt-log gains); (iii) interpolate to beat C = 1/2 on the
class.  The blow-up/book structure (Section 5 reading of MSV) is exactly
what a proof must defeat, and independent-apex books are the pivot.
