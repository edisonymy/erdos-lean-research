# Outside full-resolution refresh — 2 August 2026

**Live-status cutoff:** 2026-08-02 22:31 UTC
**Decision:** **DO NOT PROMOTE an outside target.** Keep the current bounded #151
cycle intact. If that cycle later fails its checkpoint, #719 is the first reserve,
but it has not earned a switch today.

This was a bounded outside-option refresh, not a new campaign. It did not edit or
run the active #151 work. The pre-existing dirty `LOG.md` was deliberately left
untouched.

## Ranked shortlist

| Rank | Problem | Full-resolution endpoint | Fresh evidence | Collision risk | Verdict |
|---:|---|---|---|---|---|
| 1 | [#719](https://www.erdosproblems.com/719) | One finite hypergraph violating the universal Erdős–Sauer decomposition bound | A new exact-61-edge, packing-at-most-two SAT probe produced neither a witness nor an impossibility certificate | Low-to-moderate; no public full resolution found at the cutoff | **DO NOT PROMOTE; first reserve** |
| 2 | [#561](https://www.erdosproblems.com/561) | A finite host below the conjectured size-Ramsey bound for one parameter tuple | The current statement is open, but a June/July 2026 paper sequence withdrew an initially claimed general solution and now proves only uniform cases | High; the same authors appear to be actively repairing the boundary | **DO NOT PROMOTE** |

No third target survived the joint recognition, full-leverage, one-week
reachability, verification, and collision gates. The previously rejected #701,
#149, #778, and #65 were not reopened: this refresh found no new mathematical or
priority evidence that changes their earlier verdicts.

## 1. Single bounded probe: #719

### Statement fidelity and live priority

The live problem asks whether every (r)-uniform hypergraph (G) on (n)
vertices has its edges partitionable into at most

\[
  \operatorname{ex}_r(n,K_{r+1}^{(r)})
\]

pieces, each either one edge or the edge set of a copy of
(K_{r+1}^{(r)}). Equivalently, if \(\nu(G)\) is the maximum number of
edge-disjoint copies, the minimum number of pieces is

\[
  \phi(G)=e(G)-r\nu(G),
\]

and the conjecture is \(\phi(G)\leq
\operatorname{ex}_r(n,K_{r+1}^{(r)})\).

The [live page](https://www.erdosproblems.com/719) still marks #719 **OPEN**.
Its [history](https://www.erdosproblems.com/history/719) contains only the
20 October 2025 statement revision, and its
[forum thread](https://www.erdosproblems.com/forum/thread/719) contains only a
February 2026 small-case comment. Exact statement/terminology searches and the
live [VibeMathed dataset](https://vibemathed.com/api/dataset) (generated
2026-08-02T21:10:38.292Z, 253 entries) exposed no full solution or matching
announcement. This is a targeted recency check, not a proof that no private
work exists. The primary source is Erdős's 1981 paper
([DOI](https://doi.org/10.1007/BF02579174)).

### Why the tested slice could settle the whole problem

For \(r=3,n=9\), the independently certifiable extremal value is

\[
  \operatorname{ex}_3(9,K_4^{(3)})=54.
\]

This value is now pinned by a
[self-contained finite certificate](erdos719_exact61_audit/raw/ex54_certificate.json)
and its [standard-library generator](erdos719_exact61_audit/certify_ex54.py).
The certificate exhaustively obtains the complementary hitting number
\(t_7=12\), propagates it via \((n-3)t_n\geq n t_{n-1}\), and checks explicit
matching cyclic constructions at \(n=8,9\). The independent audit replay
returns \(t_8=20,t_9=30\), hence \(84-30=54\); the promotion calculation below
does not rely on an uncited table value.

Therefore any 61-edge 3-graph with \(\nu(G)\leq2\) would satisfy

\[
  \phi(G)=61-3\nu(G)\geq55>54
\]

and would refute the full universal conjecture. Searching exactly 61 edges
loses no denser witness: deleting edges preserves \(\nu\leq2\) until 61 edges
remain.

The finite model has 84 edge variables and 126 possible tetrahedra. It fixes
the edge count at 61 and lazily forbids every simultaneously present triple of
pairwise edge-disjoint tetrahedra.

### Probe result

A corrected CaDiCaL195 run used a sequential exact-cardinality encoding and a
20,000-conflict cap per solve. It returned seven successive 61-edge models;
each violated the packing condition and generated new exact cuts:

| Round | Present tetrahedra | New forbidden packing triples |
|---:|---:|---:|
| 1 | 45 | 5,325 |
| 2 | 45 | 5,919 |
| 3 | 28 | 1,542 |
| 4 | 26 | 1,198 |
| 5 | 30 | 1,849 |
| 6 | 28 | 1,227 |
| 7 | 29 | 1,343 |

The run stopped **UNKNOWN** at the conflict cap after adding 18,403 distinct
packing-three cuts. It found no candidate with \(\nu\leq2\), and it did not
prove that none exists. Even the best exposed model still had 26 tetrahedra
and at least one forbidden packing triple. This is a functioning encoding, but
not a positive renewal signal.

The corrected implementation, exact command, environment/configuration,
DIMACS, all seven models, and every cut are preserved in the
[#719 exact-61 audit bundle](erdos719_exact61_audit/README.md). Its
[machine-readable replay result](erdos719_exact61_audit/raw/audit_result.json)
is `PASS`: it verifies 84 edge variables, 126 tetrahedra, 2,890 total CNF
variables, 5,612 base clauses, 121 exact-cardinality assignments, all 18,403
packing-three cuts, and four deliberate tamper rejections. The exact artifact
hashes are pinned in
[`SHA256SUMS.json`](erdos719_exact61_audit/SHA256SUMS.json).

### One-week path, verification, and kill rule

This path is retained only for a future conditional promotion:

1. Re-audit the live statement and the short certificate for
   \(\operatorname{ex}_3(9,K_4^{(3)})=54\), then freeze an exact-61 model.
2. Give a proof-capable static CNF or carefully audited incremental equivalent
   at most one CPU-day. Do not expand to (n=10) merely because the solver is
   inconclusive.
3. If a candidate appears, independently count its 61 edges, enumerate all 126
   tetrahedra, and compute the exact maximum edge-disjoint packing with a
   separate branch-and-bound or SAT checker. Re-run the public-priority search
   before any claim.
4. If no candidate appears within the cap, the cut trajectory does not
   materially shrink, or an UNSAT result lacks a replayable certificate, kill
   the lane. A solver status line is not a theorem.

**Current verdict: DO NOT PROMOTE.** #719 remains the best outside reserve
because a tiny, independently checkable finite witness would settle the full
problem, but this probe supplied no such witness, near-witness, structural
lemma, or certificate.

## 2. Screened runner-up: #561

The current page states the conjecture as follows. For descending positive
star degrees

\[
F_1=\bigsqcup_{i=1}^{s}K_{1,n_i},\qquad
F_2=\bigsqcup_{j=1}^{t}K_{1,m_j},
\]

let

\[
  \ell_k=\max_{i+j=k}(n_i+m_j-1).
\]

Then

\[
  \widehat R(F_1,F_2)=\sum_{k=2}^{s+t}\ell_k.
\]

The [live #561 page](https://www.erdosproblems.com/561) is still **OPEN** and
uses the (s+t) upper limit above (an old forum transcription used a different
limit). The established paper
[arXiv:2111.02065](https://arxiv.org/abs/2111.02065) proves substantial special
cases, including all-odd regimes, but not the displayed general statement.

The decisive collision evidence is unusually recent. Version 1 of
[arXiv:2606.04439](https://arxiv.org/html/2606.04439v1), posted 3 June 2026,
claimed a complete solution. Version 2
([4 June](https://arxiv.org/html/2606.04439v2)) narrowed that claim, and version
3 ([4 July](https://arxiv.org/html/2606.04439v3)), now titled *Size Ramsey
minimal graphs for uniform star forests*, explicitly leaves the arbitrary
conjecture open and treats uniform forests. That withdrawal is evidence both
that the general statement is delicate and that a nearby active group is
working directly on it.

A one-week attack could enumerate all unlabeled hosts at the conjectured
boundary for the first unsettled parameter tuples and independently check every
2-colouring. A host below the formula would be a complete counterexample. But
without a new positive finite signal, that is only generic falsification
geometry; it does not outweigh the very high collision/proof-repair risk.

**Verdict: DO NOT PROMOTE.** Reconsider only if a concrete below-bound host or
a genuinely new structural reduction appears, and first compare it against the
latest revision of the active paper.

## Comparison with the active #151 cycle

At the read-only 2026-08-02T22:30:39Z snapshot, the active fixed-clique #151
run had processed 1,020 outer models and committed 1,020 checked cuts (225
forbidden-(K_5) batches and 795 residual-admissibility batches). It had not
yet reached a global or arrowing cut, so this is not a success signal; however,
it already targets an audited finite endpoint capable of resolving the full
problem and is inside its declared bounded cycle.

#719 offers the cleanest alternative endpoint but returned only capped
UNKNOWN, while #561 carries acute live collision risk and no fresh witness.
Interrupting #151 now would therefore lower, not raise, the estimated chance of
a first full resolution within one week.

## Hygiene and claim boundary

- No #151 file or process was edited, restarted, or stopped.
- No long computation, publication, outreach, staging, commit, or push was
  performed.
- `research/full_solution_scout/triage-2026-08-02/LOG.md` was already modified
  by other work and was left unchanged.
- The only audit-repair additions are this report and the isolated
  `erdos719_exact61_audit/` bundle.
- The #719 run is diagnostic evidence only. It proves neither a counterexample
  nor the packing-at-most-two nonexistence statement.
