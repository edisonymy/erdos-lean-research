# HANDOVER — Erdős #64 small-cover / two-defect / σ=19-hunt lanes

> **SUPERSEDED HANDOVER — DO NOT USE ITS PRIORITY OR LIVE-RUN CLAIMS.**
> A hostile successor audit found that the claimed new 38-vertex witness is
> Gordon Royle's 2009 graph `F038A`, that minimum total order 38 was already
> implicit in the McKay--Afzaly exact table, that the correct unoriented
> `C6` count is 19, and that the stated `38..50` hunt range was wrong.  The
> corrected record and exact isomorphism are in
> `root_independent_audit_2026-08-03/`.  Fresh certificates now verify the
> per-side exclusion through 18, and the successor σ=19 `C16` exclusion is
> recorded separately.  The text below is retained only as historical state.

**From:** Fable long-horizon session, 2026-08-03 (~19:20–21:15 UTC).
**To:** successor agent (Sonnet 5.6 or other).
**Branch:** `claude/erdos-64-research-8a0ieh`, PR #10 (draft, subscribed).
**Read first:** `REPORT.md` (summary), `LEDGER.md` (append-only log with
all corrections/audits — keep appending, never edit).

## What is proven / certified (safe to rely on)

1. **Theorem 1 + ladder.** No linear hypergraph on σ ≤ 18 points with
   point-degrees ≥ 3 and edge sizes ≥ 3 has a C8-free incidence graph.
   Equivalently: every bipartite graph, min degree ≥ 3, no C4, no C8,
   has both sides ≥ 19 (order ≥ 38). Status: σ ≤ 17 kissat-UNSAT with
   drat-trim `s VERIFIED`; σ = 18 UNSAT by THREE independent kissat
   solves, clean DRAT written (`pure_sigma18_clean.drat`), drat-trim
   was still running at handover — finish/check `drat18.status`
   (expect `s VERIFIED` appended after `kissat exit 20`).
2. **σ = 19 is SAT**: `sigma19_model.json` = quadrilateral-free (19₃)
   configuration, 38 vertices, girth 6, 38 hexagons, walk-regular
   (single distance profile (1,3,6,9,12,7)); independently verified
   cubic/simple/C4-free/C8-free; HAS C16 and C32. Hence the minimum
   order of a bipartite min-degree-3 {C4,C8}-free graph is EXACTLY 38
   (new extremal number; previous smallest known example: 70-vertex
   (3,10)-cages). Priority searches found nothing prior (LEDGER
   entries 2, 8, and the config-literature checks).
3. **Two-defect blocks** (bipartite F, one degree-2 vertex per side,
   rest 3, no C4/C8/C16/C32; doubling F = cubic counterexample —
   derivation in LEDGER Entry 6, hostile-checked): excluded with DRAT
   certificates for n_F = 24..38 (`certtd.log`, `certtd2.log`,
   `td_h*_r*.cnf/.drat`, `blocks_twodefect_h*.json`); n_F = 40, 42
   solver-status UNSAT (cadical CEGAR); n_F = 44 (h=22) was still
   solving. This kills the bipartite marked-edge mechanism through
   host order ≥ 42.
4. Pure small-cover (bipartite, cover ≤ 15) closed by Theorem 1.

## The live frontier (highest value, resume FIRST)

**`pure19_hunt.py`** — screens the ENTIRE σ=19 family (all linear
hypergraphs on 19 points, degrees ≥ 3, sizes ≥ 3, C8-free) against
C16 and C32 by kissat rounds with audited blocking clauses.
- A surviving model = **full counterexample to Erdős–Gyárfás**
  (38 ≤ n ≤ 50; cycles ≤ 38 so only 4/8/16/32 matter; 4/8 dead
  statically). If you get `CANDIDATE_pure19_*.json`: FREEZE it, run
  `checker_a.py` AND `experiments/erdos64/verify_graph.py` (schema
  {"n":…,"edges":…}), re-run the priority search, and follow the
  9-step protocol in the campaign tasking before any claim.
- UNSAT = every bipartite counterexample has both sides ≥ 20
  (n ≥ 40): beats the published bipartite bound 32, certified.
- State at handover: round 1 done (+512 C16 blocks, 191 s/round),
  blocks persist in `blocks_pure19.jsonl` — restarts RESUME from it.
  Just rerun `python3 pure19_hunt.py <seconds>`. Expect many rounds;
  each is a fresh kissat solve of statics+blocks (~200 s early on).
- After σ=19 resolves, the same question at σ=20 (statics likely SAT)
  continues the ladder: adapt SIGMA in the script.

## Running-at-handover processes (check logs; may have died with
container)

- `pure19_hunt.py 10800` → `pure19_hunt.log` (resumable, see above).
- `sat_search_linear.py twodefect 22 7200` → `td22.log` (NOT
  resumable — no persistence in that script; if dead, prefer
  `certify_twodefect.py 22 <sec>` which re-derives with certificates).
- `certify_twodefect.py 20/21` loop → `certtd2.log` (h=20 was mid-run;
  h=19 already VERIFIED).
- `sat_search_core2.py 13/14/15` → `core2b_s1{3,4,5}.log`: the
  general small-cover family (cover edges allowed, σ ≤ 15, n ≤ 50).
  Only s15 persists blocks (`blocks_s15.jsonl`, 2921 at handover;
  relaunch: `python3 sat_search_core2.py 15 <sec> blocks_s15.jsonl`).
  s13/s14 had no persistence; treat as lost if dead. These were
  slow-converging (t≤2 mixed-C8 CEGAR); an UNSAT here would prove "no
  counterexample has independence number ≥ n−15"; a model surviving
  all rounds is again a full counterexample. Honest status:
  undetermined.
- `regen18.sh` → `drat18.status` (σ=18 certificate; kissat done,
  drat-trim pending).

## Verification standards (do not relax)

- Any SAT "candidate": two independent checkers + freeze + hash +
  fresh priority search BEFORE any announcement (campaign rules).
- Any new UNSAT you want to state publicly: kissat + drat-trim
  certificate (pattern in `certify_pure.py` / `certify_twodefect.py`),
  or clearly label solver-status. CEGAR blocks must be audited
  (audit_block / audit_cycle functions) and saved.
- The encodings' faithfulness arguments live in LEDGER entries 3–5 and
  12 (exact quadrilateral excuses; symmetry-with-aux soundness; the
  corrected bridge-counting lemma — my first version was WRONG, the
  correction is Entry 5; treat every new counting lemma as hostile).

## Ready-to-post public update

`ISSUE_UPDATE_DRAFT.md` is written for issue #9 with [bracketed]
numbers to finalize: fill in (a) σ=18 DRAT verdict, (b) two-defect
frontier (42 or 44), (c) pure19_hunt status (UNSAT ⇒ "both sides ≥
20" / rounds-in-progress), (d) core σ=13..15 statuses. Post it as an
issue comment (campaign style: "not a solution" header, exact evidence
classes, hashes). Also update README.md's #64 bullet to mention the
38-vertex sharp threshold and point to this packet.

## Unfinished small threads (cheap, optional)

- The 38-vertex object looked cyclic-ish (single distance profile).
  A networkx vf2 test against Haar graphs H(19; 0,a,b) (171 candidates)
  was interrupted; if it IS a Haar graph, the writeup gets a crisp
  description and the σ=19 family's cyclic slice connects to
  difference-set arithmetic (LEDGER Entry 3 context).
- `nosym_rest.py` (symmetry-free certificates σ ≥ 9): σ=9 done
  VERIFIED; σ=10 was mid-solve when trimmed. Only needed to remove
  the (classical, citable) double-lex dependency — low priority.
- Two-defect flip zone n_F ∈ [46, 70]: needs floor-licker-style
  streaming (their repo: erdos-gyarfas-cubic-bipartite), not tonight's
  SAT. Any (3,10)-cage minus an edge shows the C8-part flips by 70.
- Extremal question N(k) (Entry 8) is publishable standalone; a hand
  proof of σ ≥ 13-ish would complement the certificates (my corrected
  count only gives σ ≥ 9).

## Environment notes

- Proxy blocks arxiv.org, houseofgraphs.org, erdosproblems.com,
  wikipedia; GitHub raw + clones and PyPI work. kissat + drat-trim are
  built in the scratchpad (rebuild: clone arminbiere/kissat,
  marijnheule/drat-trim; see `certify_pure.py` paths).
- Large DRAT files (>2 MB) are intentionally NOT committed; hashes in
  `CERT_SHA256SUMS.txt`; everything regenerates deterministically.
- Known-frontier context and all sources: LEDGER entries 1–2.
