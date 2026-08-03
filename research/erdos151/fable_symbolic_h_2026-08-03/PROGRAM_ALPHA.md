# Program Alpha: the class clique-coloring constant (opened 2026-08-03)

## Root hostile-audit override (2026-08-03)

The frozen independent audits linked at the end of this file supersede every
inconsistent empirical or scope claim below.  The corrected goal is a
**pure-3 subprogram**: prove a triangle-free-partition or fractional-cover
bound `chi_tf(G) <= C·Delta/ln Delta` with `C<1/2` for K4-free graphs in which
every edge lies in a triangle.  This would eliminate that face for all large
`h`; it does **not** by itself resolve full #151 because a triangle-free class
may contain an ambient-maximal edge.  A full route additionally needs a
genuine clique-colouring/admissible-cover bound or a theorem paying for the
maximal-edge system.

The audit also withdraws all `L(785,53)` 9/10-class claims and brackets: the
10-class replay contains 3,227 monochromatic triangles, the 9-class claim has
no checkable partition, and the purported lower endpoint reverses an
inequality.  Glauber and Moser--Tardos outputs are calibration telemetry only.
No novelty is claimed for the order-of-magnitude clique-transversal result,
which was publicly recorded before this campaign.

## A1. Sparse-triangle regime — PROVED (this file, 2026-08-03)

**Theorem A1.**  Let G be any graph, t_max = max over vertices v of the
number of triangles containing v, and let k = ceil(sqrt(3e·t_max)) + 1
(e = 2.71828...).  Then V(G) can be partitioned into k classes with no
monochromatic triangle.  Consequently, if G is K4-free and every edge of
G lies in a triangle (pure-3), then

    beta(G) >= n / (ceil(sqrt(3e·t_max)) + 1).

Proof.  If `t_max=0`, one class suffices.  Otherwise color every vertex
independently and uniformly from [k].  For
each triangle T let A_T be the event that T is monochromatic:
P(A_T) = k·(1/k)^3 = k^{-2}.  A_T is determined by the colors of its
three vertices, so A_T is mutually independent of all events on
vertex-disjoint triangles; its dependency degree is at most
D = 3(t_max − 1).  The symmetric Lovász Local Lemma applies when
e·P·(D+1) <= 1, i.e. e·k^{-2}·(3t_max − 2) <= 1, which holds for
k >= sqrt(3e·t_max).  With positive probability no A_T occurs; fix such
a coloring.  Each class is triangle-free; in a pure-3 K4-free graph a
triangle-free class contains no nontrivial maximal clique (triangles are
the only ones), so every class is admissible, and the largest class has
size >= n/k.  ∎

**Corollary A1.1 (triangle concentration is forced).**  In units
t_max = η·Δ²/ln²Δ with Δ <= h−1, Theorem A1 gives
chi_tf <= (sqrt(3e·η) + o(1))·Δ/ln Δ = (2.86·sqrt(η) + o(1))·Δ/ln Δ.
Hence a pure-3 K4-free counterexample at parameter h with
n >= (c_R − o(1))h²/ln h must satisfy

    t_max  >  ((c_R/2.86)² − o(1)) · h²/ln²h ,

i.e. some vertex carries Ω(h²/ln²h) triangles.  With c_R = 1/2 the
constant is ≈ 0.031.  This upgrades the log §8 covering heuristic
("counterexamples live in the medium-dense link regime") to a THEOREM on
the maximum: dense links are unavoidable, not just average-forced.
Status: PROVED (symmetric LLL only; no machinery).

**A1-plus proof-route analysis (2026-08-03, in-progress).**  Naive
Moser bookkeeping (per resample: record triangle-id log2(3·t_max) +
pre-color log2(k) + stack bits; recover 3·log2(k)) yields k² > c·t_max
with c WORSE than the plain LLL — the O(1) bits matter.  The two
machineries with genuine improvement potential:
(i) expected-record entropy compression: after resampling x to a fresh
    color, the newly-violated candidates at x are the mono-colored link
    edges, expected e_x/k² << 1 — adaptive coding of the candidate
    identity has low expected cost; the K4-free book structure
    (independent apexes) limits simultaneous violations.  Framework:
    Achlioptas–Iliopoulos / Harvey–Vondrák flaw convergence.
    Honest expected yield: c ≈ 2–4.
(ii) Radhakrishnan–Srinivasan delayed recoloring (the property-B
    sqrt-log improvement), adapted from 2-coloring to k-coloring of the
    triangle system.  Yield if it transfers: toward c = 2, possibly
    with a log factor gained instead of a constant.
Empirical guardrail (`mt_threshold.jsonl`, **CALIBRATION ONLY**): one seeded
run on each of three instances terminated within budget at `c=1.0` and did
not terminate within budget at `c=0.7`.  A success constructs an
instance-specific upper bound; a budget exhaustion is not a lower bound or a
threshold certificate.  These runs establish no uniform critical constant,
no ceiling for oblivious resampling, and no proved `eta` boundary.  The
former `L(785,53)` bracket is withdrawn by the root audit.
Adversarial miner v3 (subgroup-seeded, proper degrees D = 62–78):
max C_emp found 0.335 — hill-climbing cannot approach 1/2 either.

**A1-plus (next proof project, precise claim, CONJECTURAL until
executed).**  Claim: k = (1+ε)·sqrt(2·t_max) classes suffice, i.e.
C(η) = sqrt(2η)(1+ε), so C < 1/2 already at η < 1/8 (vs 1/36 from A1).
Strategy: Moser–Tardos resampling with a Molloy-style witness-tree
count: a resample step is triggered by a mono triangle at v and rewrites
3 color-registers while the log records one of <= 3·t_max triangle
identities plus O(1) bits; compression wins when k² > (1+ε)·3t_max /
(overlap discount).  The overlap discount (triangles at a vertex share
the vertex-register) is where the constant 3 should drop toward 2; the
calibration table (A-cal: greedy already beats A1 by ~4x) says the true
constant is well below even sqrt(2η) on natural instances.

**Improvement path (open, plausibly week-scale each):**
- entropy compression / Moser–Tardos with a sharper local analysis
  should improve 2.86·sqrt(η) toward sqrt(2η)-type constants (target:
  C < 1/2 at η <= 1/8);
- the lopsided/variable-local LLL replaces t_max by a local average;
- the M-face version: mixed events (mono maximal edges, probability
  k^{-1}) are too heavy for LLL directly; route through Theorem M1
  (burden) instead — open subtask A1'.

## A2. Dense-link regime — block extraction (OPEN, partial tools)

Dense triangle-free links contain large complete-bipartite blocks:
Kővári–Sós–Turán inside L_v (triangle-free on <= Δ vertices, e_v edges)
yields K_{t,t} with t ~ log e_v / log(Δ²/e_v)-scale; in a triangle-free
graph the sides of any complete bipartite subgraph are independent, so
blocks are "clean".  Plan: peel blocks until the residue is A1-sparse;
color side-respectingly on blocks (a class picks one side per block it
meets — kills all block triangles by construction) and run A1 on the
residue.  The glue — coordinating side choices across overlapping block
systems — is the genuinely new machinery (the table-CSP of log §10);
its LP/entropy budget is the heart of the program.  MSV-final graphs
are exactly locally-CBU (log §10 Lemma B1), so they are the A2-pure
test case: for them chi_tf equals the table-CSP optimum; any theorem
here must (and may) exploit that blocks per vertex is Θ(log h) while
sides per block are 2–3.

**Lemma A2.1 (PROVED).**  In a K4-free graph, every complete tripartite
subgraph with all three parts nonempty has independent parts.
Proof: an edge inside one part plus one vertex from each other part
spans a K4.  ∎  (So "blocks" are automatically clean; with KST inside a
dense triangle-free link L_v one extracts K_{t,t} sub-blocks with
t ~ ln d / ln(d²/e_v), forming K_{1,t,t} tripartite blocks at v.)

**FALSE-claim log (caught before use, 2026-08-03):**  "resolvable
(round-structured) locally-CBU systems have chi_tf = 3 via one part per
copy" is WRONG: a class chosen to respect round r's parts has
uncontrolled traces on the blocks of other rounds; rounds entangle and
the table-CSP does not factorize.  No shortcut; A2/A3 remain the hard
core.  (This also corrects any temptation to read the §F5 resolvable
failure as implying resolvable systems are safe for the CONJECTURE side
by a trivial coloring — they are safe only against the specific
random-placement covering arithmetic.)

**A2-occupancy entry point (formulated 2026-08-03).**  Work with the
Gibbs measure mu_lambda on triangle-free induced sets S (weight
lambda^{|S|}).  The local constraint at v is exactly "S ∩ N(v) is
edge-free in the link L_v".  On a locally-CBU graph the link-local
count of edge-free traces FACTORIZES over blocks:

    Z_{L_v}(lambda) = prod_i [ (1+lambda)^{a_i} + (1+lambda)^{b_i} - 1 ]

for blocks K_{a_i,b_i}.  Program: (1) prove a DKPS-style local-occupancy
bound for this factorized model, uniform over block profiles with
sum(a_i+b_i) = d(v) <= Delta; (2) convert occupancy to a fractional
triangle-free-cover bound and then to chi_tf <= C_CBU·Delta/ln Delta
with explicit C_CBU (target < 1/2); (3) A3 handles cross-block shear
via K4-freeness (independent book apexes).  The one-block extremes:
balanced a = b = d/2 gives Z = 2(1+lambda)^{d/2} - 1 (cheap, big
sides); many tiny blocks a=b=1 degenerate to independent-set hard-core
(the expensive JMRS-like end).  The profile war is a clean calculus
problem — the first genuinely tractable formulation of the dense
regime.  Status: FORMULATED; next session executes the one-block and
uniform-profile calculus.

**Profile-war v1 post-mortem (2026-08-03, profile_war.jsonl).**  The
mean-field (independent-neighbor) local model reports worst C_needed ∈
[0.31, 0.80] with single-huge-block profiles as extremal and a
bistability artifact at D=256 — but single-block links are in truth the
EASIEST case (side-picking), which the product measure cannot express.
DIAGNOSIS (FALSE-model, logged): the A2 local model must include
per-block side fields (symmetry-broken / Ising-like ensemble); the
truly frustrated profiles are medium-many medium blocks with
cross-block side conflicts.  The decisive missing datum is the ACTUAL
block hypergraph of class members (blocks per vertex, block sizes,
overlap pattern) — being measured on the anchor next.  Table-CSP
arithmetic note: independent per-block tables lose only ~h^{0.2}
against the requirement at t_blocks ~ 3 ln h; pairwise-correlated
tables (Sherali–Adams level 2) are a plausible closing mechanism.

## A3. Interpolation and the class profile (OPEN)

The covering demand forces average link density ~h²/(12 ln h)
(hereditarily, at every scale — log §8); A1 forces max density
Ω(h²/ln²h); A2 handles block-shaped density.  Needed: a decomposition
theorem "every K4-free pure-3 graph = block part + A1-sparse part"
with the block part's table-CSP solvable in (1/2−δ)·Δ/ln Δ classes.
Failure mode to watch: cross-block triangle "shear" (triangles with
edges in three different blocks) — excluded in exactly-locally-CBU
graphs, present in general; quantify via K4-freeness (apex sets of
books are independent).

## A-cal. Empirical calibration (2026-08-03, chitf_landscape.py + inline)

COMPUTATIONALLY CHECKED, two families, greedy upper bounds on chi_tf:

| family | n | Δ | t_max | η | k | C_emp = k·lnΔ/Δ |
|---|---|---|---|---|---|---|
| capped process (purified) | 200 | 22 | 30–34 | .29 | 4 | 0.562 |
| capped process | 400 | 32 | 51 | .35 | 5 | 0.542 |
| capped process | 800 | 47 | 77–83 | .43 | 6 | 0.492 |
| capped process | 1600 | 69 | 123–124 | .46 | 8 | **0.491** |
| MSV-shape l=33 | 500 | 96 | 504 | 1.14 | 7 | **0.333** |
| MSV-shape l=21 | 500 | 78 | 278 | .87 | 7 | 0.391 |
| MSV-shape l=15 | 500 | 75 | 227 | .75 | 8 | 0.461 |

Audited reading: these are valid greedy upper bounds for the generated
instances, but four of the eight stored capped-process records are at least
`1/2` (`0.562,0.562,0.542,0.542`).  The table therefore does not support the
former claims "below 1/2 everywhere" or "every family with margin."  JMRS is
known to be order-tight; its leading coefficient `1` is not proved optimal.
The data remain useful for generating hypotheses, not for a theorem or a
uniform constant claim.

**Anchor claims WITHDRAWN (root replay, 2026-08-03).**  The conflict-repair
routine removes only one blocker before inserting a vertex and can leave
other monochromatic triangles.  Deterministic replay of the reported first
restart produced ten classes, all invalid, with 3,227 monochromatic
triangles.  Moreover `alpha_tf>=156` cannot imply
`chi_tf>=ceil(785/156)`: that direction would require an *upper* bound on
`alpha_tf`.  No structural or constant conclusion may be drawn from the
reported 9/10-class objects.  After repairing the ejection rule and saving
the colour classes, the independent checker verifies a **13-class**
partition (`anchor_pin_fixed_verified.json`), hence only the safe upper bound
`chi_tf(L785,53)<=13` and `C_upper=0.421`.  No nontrivial lower bound is
claimed.

**Anchor datum (near-class-member, 2026-08-03, superseded reading).**  L(785,53) — the
circulant underlying the F_e(3,3;4) <= 786 record graph G_786 — built
and verified here: 785 vertices, 156-regular, K4-free (checked), t_max
= 1638 (η = 1.72), no triangle-free 2-partition found by local search
(as expected one vertex shy of arrowing).  Greedy chi_tf <= 17 classes:
C_emp = 0.55 (6 restarts; true value plausibly ~0.5).  Reading: on
genuine Folkman-type structure the constant sits AT the c_R = 1/2
target, not below — the race is tight exactly where it must be; the
easy sub-1/2 numbers on process/MSV-shape graphs do not transfer for
free.  Program consequence: A2/A3 must be built for
subgroup-circulant-like block entanglement, and the assembly target
C < 1/2 is a genuine fight, while C < 1 (sufficient if c_R > 1/2)
retains large empirical margin on every family measured.  Also
re-verified in passing: dense Folkman graphs are conjecture-safe via
β >= Δ (156 >> H(785) ≈ 50); the entire #151 danger zone is SPARSE
arrowing graphs (Δ <= h−1), i.e. exactly the open bounded-degree
Folkman question of log §13/14.

**Family sweep (2026-08-03, circulant_cemp_sweep.py, COMPUTATIONALLY
CHECKED).**  78 K4-free triangle-rich subgroup circulants L(n,g),
n ∈ [301, 1207], degrees 24–200, η up to 1.9:
C_emp ∈ [0.223, 0.398], median 0.317.  No instance above 0.4.  The
entire known near-class family sits far below the 1/2 target.

**MT calibration (mt_threshold.py, partial and non-certifying).**  On the
stored seed the routine found colourings at the displayed values, including
`c=1.4`.  This is instance-specific constructive evidence only; it neither
confirms the conjectural A1-plus theorem nor turns a budget failure into a
lower bound.

**Anchor-pin2 claim WITHDRAWN.**  No generating script, colour assignment, or
independently checkable partition accompanies `anchor_pin2.json`; its
`k<=9` telemetry and `[6,9]` bracket are not evidence.

**A2 dead-end note (in-turn analysis):** mixed strategies that
pre-commit side choices on large blocks and randomize small ones fail
by the same (3/2)^{t_L} table explosion as §10 — uncorrelated
pre-commitments give k ~ 2.5·D/ln D, WORSE than JMRS.  The correlation
must come from a counting/occupancy argument over whole colorings, not
per-block decisions.  This is now a three-times-confirmed wall
(random tables, resolvable rounds, mixed pre-commitment); the occupancy
route is the serious path.

**Adversarial miner launched (cemp_miner.py):** hill-climbing connection
sets to MAXIMIZE C_emp over general K4-free circulants — hunting the
empirical extremal instance that A2 must handle; stagnation below ~0.45
would be a fourth independent confirmation of the target.

## A4'. CONSOLIDATION (2026-08-03): fractional suffices + the Master
## Inequality

**Lemma A4.1 (PROVED).**  For any nonempty pure-3 graph G (all nontrivial maximal
cliques are triangles): β(G) >= n / χ_tf^f(G), where χ_tf^f is the
FRACTIONAL triangle-free cover number.  Proof: weights x_S with
Σ_{S∋v} x_S >= 1 give Σ_S x_S|S| >= n, so some triangle-free S in the
support has |S| >= n/Σx_S; triangle-free sets are admissible in pure-3
graphs.  ∎  Consequence: the integrality gap and every ln(n) rounding
loss DISSOLVE — the program only needs fractional bounds, which is
precisely what occupancy methods certify.

**Master Inequality (TARGET — the whole program in one line).**  For the
Gibbs measure μ_λ on triangle-free induced sets of a class graph
(K4-free, covering-forced link density), prove local occupancy

    P(v ∈ S)  >=  (2+δ)·ln Δ / Δ        (some fixed λ = λ(Δ)).

Then χ_tf^f <= Δ/((2+δ)lnΔ), so β >= (2+δ)·n·lnΔ/Δ, beating the proved
Ramsey coefficient `1/2` for all large `h` **on the pure-3 face only**.
At the sparse-link
extreme this is the known factor-2 occupancy wall (constant 1); the
class excludes that extreme, and the factorized CBU computation (A2
entry point) suggests dense blocks may raise free volume.  The stored Glauber
numbers are finite single-chain mean-density diagnostics without mixing or
error certificates.  On non-transitive instances a mean density does not
give the uniform per-vertex marginals required for a fractional cover.
All prior findings (dichotomy §8, pincer, MT boundary η=1/4) are now
one inequality about one measure.  Status: TARGET, with A1 covering
the sparse regime unconditionally and the factorized model giving the
dense regime a closed-form entry.

## A5. THE TRICHOTOMY ARCHITECTURE (2026-08-03 — the session's main
## theoretical discovery; statuses labeled)

**Block-structure measurement (COMPUTATIONALLY CHECKED,
block_structure_L785.log):** the anchor's links are 21-regular
high-girth triangle-free graphs; maximal bipartite blocks are stars
K_{1,21} (~165 per vertex).  The anchor is a THIN-BOOK graph, not
MSV-fat-tripartite: the dense regime has two sub-shapes.

**Empirical link-degree law (CONJECTURAL, fits all measured data):**

    chi_tf(G)  ≈  d_link / ln d_link,     d_link = average link degree
                                          = 2*e_v/D.

The former anchor comparison used the withdrawn `[6,9]` bracket and supplies
no evidence for this law.  The conjectural analogy is a
"second-level Johansson": partitioning G into triangle-free classes
costs what PROPERLY coloring the (triangle-free!) links costs — and
K4-freeness is exactly what makes links triangle-free.

**The ln-margin (heuristic arithmetic, to be made rigorous):**  the
covering demand forces d_link ≈ h/(6 ln h) on average, so the law gives
beta >= n*ln(d_link)/d_link ≈ 6*c_R*h*ln h  — exceeding the
counterexample threshold h by Θ(ln h), NOT by a constant.  Master
Inequality v2: occupancy of μ_λ >= c*ln(d_link)/d_link for ANY fixed
c > 0 suffices at average-forced link density — no knife-edge.

**Trichotomy of link regimes (the proof plan):**
(R1) sparse links (e_v <= eta*D²/ln²D, small eta): Theorem A1 (PROVED)
     already gives more than enough.
(R2) medium links: the ln-margin regime — Master Inequality v2 at the
     link-degree scale; the whole Θ(ln h) slack is available.
(R3) Mantel-dense links (e_v ~ D²/4): triangle-free stability forces
     near-bipartite links = fat blocks; side-symmetry-broken ensemble
     makes classes nearly free (single-block truth chi_tf ≈ 2-3).
     Needs the quantitative "near-bipartite => cheap" lemma.
Seams: R2/R3 interpolation via stability defect; per-vertex mixtures
handled by local (not global-average) versions.  Nothing here is a
knife-edge except possibly the seams — a qualitatively better position
than the flat constant race (1 vs 1/2) this program started from.

Immediate falsification duties: (i) test the link-degree law on
constructed instances with ADVERSARIAL link-degree profiles (mixtures
of R1/R3 vertices); (ii) check the law's failure mode on the miner's
worst instances; (iii) then attempt Master Inequality v2 in R2 first.

## A4. Assembly target

`chi_tf <= C·Delta/ln Delta` with explicit `C<1/2`, plus finite
effectivization, eliminates only the pure-3 large-`h` face.  Full #151 also
requires a genuine clique-colouring/admissible fractional-cover theorem or a
quantitative bridge paying for maximal edges.  Use rigorous Ramsey lower
coefficients (currently `1/2`) rather than assuming an asymptotic constant
exists.

## Frozen hostile audits

- `FABLE_X1_TCG_A4_M1_V1_HOSTILE_AUDIT_2026-08-03.md`
- `audit_lll_fractional_max_2026-08-03/AUDIT_REPORT.md`
- `audit_sources_data_2026-08-03/AUDIT_REPORT.md`
