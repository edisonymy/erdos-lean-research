# Outside option-value checkpoint (counterexample portfolio)

**Recorded:** 2 August 2026 (Europe/London).  **Scope:** a deliberately
narrow, no-compute screen for a *full* negative resolution of an Erdős
problem by one finite object.  This is a guard against #151 sunk-cost, not a
decision to stop #151.

## Decision

**No outside problem cleared the one-CPU-day full-counterexample gate.**  In
particular, no new siege should displace the already-running genuinely global
order-41 `omega=4` #151 model on the strength of this scan alone.  The next
outside allocation should therefore be a refreshed Tier-1/2 pool sweep, not a
solver run on one of the names below.

This is evidence against the *current alternatives*, not a claim that #151 is
likely to fall.  Follow the independently recorded #151 allocation checkpoint:
reassess after its first global run (or roughly twelve hours), and reallocate
if its listed negative signals accumulate.

## Screening sources and collision discipline

* Local campaign exclusions were read from
  [`build_pool.py`](../build_pool.py): the hard touched set excludes #151 and
  every earlier campaign target.
* The local `vibemathed-live-20260802.json` snapshot has **no claimed record**
  for #65, #149, #701, or #778.  That absence is only a screening fact.
* All four have llm-hunter material under
  `llm-hunter-live/attacks/erdos/gpt_5.2` or `gpt_pro_5.2`; it is a flag, not
  evidence.  The relevant files were read before ranking.
* Live-page/forum search and targeted literature checks were performed on 2
  August.  Search snippets are not a full priority audit and must be repeated
  immediately before a real probe or public claim.

## Closest candidates, ranked as *non-promotions*

### 1. #701 — Chvátal's down-set conjecture: retain only as a later audit target

**Faithful finite statement.**  For every down-set
`F subseteq 2^[n]` (the intended ground set is finite), some coordinate `x`
has the property that every pairwise-intersecting subfamily `I subseteq F`
satisfies
`|I| <= |{A in F : x in A}|`.  A counterexample would be a finite down-set and
an intersecting `I` beating **every** star, so a candidate is definition-level
checkable by an independent maximum-clique computation on the intersection
graph.

**Why it initially looked attractive.**  This has genuine yes/no uncertainty;
a finite witness would completely refute the intended finite conjecture.  Its
natural encoding is a Boolean down-set/antichain SAT or exact ILP model, with
lazy intersecting-family separation and orbit symmetry breaking.

**Why it fails this week's gate.**  The live page remains open, but explicitly
says it cannot be resolved by finite computation; its page was last edited 22
January 2026 and the forum has May 2026 discussion about a *different*,
infinite-ground-set formalisation pitfall.  More decisively, Eifler--Gleixner--
Pulaj's certified integer-programming/Coq work already proves all ground sets
through seven elements.  Recent 2023/2026 literature continues to make
structural progress (including the covering-number-two case and a new
Fourier/correlation result).  Thus an `n=8` search would be a non-novel,
possibly very expensive bounded extension, with no reason to expect a finite
counterexample there.

**Pre-committed kill criterion.**  Do not launch until a literature audit
identifies a previously unsearched, symmetry-reduced minimal-counterexample
class and estimates an exact `n=8` (or other fixed) model below one CPU-day.
Kill immediately if the model is merely an unstructured enumeration of
Dedekind families or if any contemporary work already covers the selected
class.

### 2. #149 — Erdős--Nešetřil strong chromatic-index conjecture: do not probe

**Faithful statement.**  For every finite simple graph `G` of maximum degree
`Delta`, its strong chromatic index satisfies
`chi'_s(G) <= (5/4) Delta^2` (the integer rounding convention must be fixed
from the original source before any encoding).  A counterexample is finite and
independently verifiable by checking `Delta` and exact colouring of `L(G)^2`.

**Why it initially looked attractive.**  It is a crisp finite-witness
universal graph statement with a direct SAT/CP encoding: search a bounded-
degree graph and prove `chi(L(G)^2)` exceeds the stated threshold.

**Why it fails this week's gate.**  The `C_5` blow-up attains the proposed
constant for even degree, strongly supporting sharpness rather than falsity.
The live page (last edited 10 April 2026) records exact positive results for
`Delta<=4`; a counterexample would need a new degree regime, while the best
general theorem is still far from the sharp constant.  The llm-hunter file
contains only elementary background, not a near-witness.  This is a classic
finite-falsifiability trap: a one-day bounded search cannot reach the unknown
regime or meaningfully update the likelihood of a counterexample.

**Pre-committed kill criterion.**  No solver time unless an analytic reduction
forces a counterexample into a specified small order/degree class.  Do not
count a new small-degree verification as portfolio progress.

### 3. #778 — clique-building games: active, composite, and wrong endpoint

**Faithful statement.**  The entry packages three games.  In the first,
players alternately colour edges of `K_n`; Alice wins precisely if her final
clique number is strictly larger than Bob's.  Erdős conjectured Bob wins for
all `n>=3`.  An Alice-win strategy for a single `n` would refute *that first
subquestion*, and can in principle be checked by a minimax certificate.

**Why it initially looked attractive.**  It has real uncertainty and an exact
finite game-tree/strategy-certificate encoding.  The local hunter already
checked the tiny cases through `n=6` (all Bob wins for the first game).

**Why it fails this week's gate.**  It is a recently active specialist race:
Malekshahian--Spiro's peer-reviewed 2026 paper proves Bob wins for density at
least `3/4` of orders and gives propagation constraints; Cambie--Provoost's
2025/26 work is also directed at the same games.  The database entry itself
contains three independent questions, so a finite outcome for the first does
not resolve the full #778 entry.  Reaching `n=7` already needs substantial
symmetry-aware minimax, and there is no evidence that an Alice-win order is
small.

**Pre-committed kill criterion.**  Do not run a raw game tree.  Permit a probe
only with a new strategy-certificate representation that reaches `n=7` within
one CPU-day and a check that it is not duplicating the two current research
programs.  Kill after one bounded `n=7` result regardless of outcome.

## Explicitly rejected for statement fidelity: #65

#65's remaining question concerns extremising the reciprocal sum of
**distinct cycle lengths** at a given density.  A finite graph is easy to
verify, but the live material describes the issue in asymptotic/minimisation
language and contains an apparent direction conflict: the question says
"minimised" by a complete bipartite graph, whereas the February 2026 page
notes forthcoming work saying "maximised."  The first displayed lower-bound
question is already proved.  The page labels the remaining issue not
resolvable by finite computation and was edited 8 February 2026.  Until the
quantifiers and direction are reconstructed from the primary sources, it is
not recognition-safe and is not a target.

## Resource rule for the next checkpoint

Keep #151's current single global model while it meets its written renewal
criteria.  If two #151 rabbit-hole indicators occur, give the freed capacity
to a *fresh* top-slice scan rather than reviving #701/#149/#778 by default.
Promote an outside target only when all of the following are written down:

1. a one-object witness settles the whole intended statement, not a range or
   subquestion;
2. a concrete size/parameter bound makes the first exact run plausibly under
   one CPU-day;
3. two independent definition-level checkers are straightforward; and
4. live page, comments, VibeMathed, local hunter files, and targeted primary
   literature search show no prior solution or live collision.

### Live sources consulted

* [#701 page](https://www.erdosproblems.com/701) and
  [forum](https://www.erdosproblems.com/forum/thread/701);
  [Eifler--Gleixner--Pulaj exact-framework record](https://portal.mardi4nfdi.de/wiki/A_Safe_Computational_Framework_for_Integer_Programming_applied_to_Chv%5C%27atal%27s_Conjecture).
* [#149 page](https://www.erdosproblems.com/149) and
  [forum](https://www.erdosproblems.com/forum/thread/149).
* [#778 page](https://www.erdosproblems.com/778) and the
  [2026 Malekshahian--Spiro article record](https://ora.ox.ac.uk/objects/uuid%3A9860b403-00c0-47a1-9a2e-609494faec80).
* [#65 page](https://www.erdosproblems.com/65) and
  [forum](https://www.erdosproblems.com/forum/thread/65).
