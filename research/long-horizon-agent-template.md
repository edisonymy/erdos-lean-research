# Long-horizon mathematical-agent prompt protocol

**Adopted:** 3 August 2026
**Purpose:** give difficult open-problem lanes enough autonomous intellectual
room without confusing persistence with unmeasured repetition.

## What the successful public examples actually suggest

The best public prompt evidence does not favour an enormous mathematical
instruction block.

- The OpenAI unit-distance run received a precise problem statement, an exact
  description of both acceptable polarities, and the instruction that partial
  progress did not count as a complete resolution.  It then produced the
  counterexample in one long response.  Thomas Bloom's retrospective identifies
  persistence down a path a human might dismiss as not worth pursuing as part
  of the success.
- Huang's reproducible sum-product agent used three short rounds: propose and
  develop a plan; construct a complete proof while adapting the approach; then
  critically review, repair, and rewrite it.  Seven of eight independent trials
  succeeded, at a reported mean of 132.4k reasoning tokens.  Its checkpointing
  and continuation mechanism mattered at least as much as its wording.  Its
  system prompt and theorem statement supplied the correct polarity, so an
  unknown conjecture should instead run proof and disproof branches separately.
- AlphaProof Nexus used independent persistent episode loops, compiler or
  prover feedback after each episode, accumulated sketches with explicit
  lessons from failed episodes, and an evolutionary population of attempts.
  It reports solving nine of 353 formalized open Erdős problems with runs of up
  to 3,000 episodes.  A persistence-heavy prose prompt alone solved none of a
  nine-problem test, while its tool-coupled goal mode solved seven.  This is
  evidence for stateful, verifier-coupled search—not for exhortations or asking
  one agent to produce a large list of shallow ideas.
- Aletheia's released Erdős transcripts likewise show user prompts that are
  often just the mathematical question.  The long-horizon behaviour comes from
  the agent's iterative generate--verify--revise inference scaffold and tool
  use, not from verbose task wording.  The released authors also warn that the
  raw outputs contain inaccuracies, reinforcing the need for an external audit
  layer.
- The reported Erdős #728 workflow separated research/brainstorming, a short
  clean mathematical prompt, a fresh proof instance, a fresh critic, and a
  formalizer.  The report is a practitioner account rather than a controlled
  study, but the role separation is consistent with the stronger evidence.
- Broad one-prompt surveys are useful for acquisition but have produced many
  rediscoveries, hidden-assumption solutions, and subtle errors.  More tokens
  do not replace statement and priority audits or independent checking.
- LLM Hunter's public one-response template contains many good hygiene checks,
  but also offers `UNRESOLVED` as a terminal.  Its recorded #1 attempt proves
  elementary lemmas, lists generic next moves, and takes that exit.  A polished
  obstruction report can become cheaper than another serious mechanism;
  persistence therefore has to be enforced by the controller rather than
  requested rhetorically inside one response.
- Rethlas implements exactly the persistence feature relevant here: it resumes
  one Codex session through repeated generate--verify--repair iterations,
  alternates search-disabled and search-enabled turns, and stores proof/memory
  artifacts.  But a public Erdős deployment reports that only about five of 74
  verifier-approved outputs were genuinely new, because the verifier checked
  the generated claim rather than whether it still solved the original
  problem.  Reuse the loop, but add an immutable statement/scope gate.

Sources:

- [original unit-distance prompt and output](https://cdn.openai.com/pdf/74c24085-19b0-4534-9c90-465b8e29ad73/unit-distance-proof.pdf)
- [independent remarks on the unit-distance discovery](https://cdn.openai.com/pdf/74c24085-19b0-4534-9c90-465b8e29ad73/unit-distance-remarks.pdf)
- [Huang's three-round prompts and checkpointing code](https://github.com/yichenhuang/sum-product/blob/main/run.py)
- [AlphaProof Nexus architecture](https://arxiv.org/abs/2605.22763)
- [Aletheia architecture](https://arxiv.org/abs/2602.10177) and
  [released Erdős prompts/responses](https://github.com/google-deepmind/superhuman/blob/main/aletheia/Erdos/Erdos.tex)
- [reported #728 workflow](https://www.reddit.com/r/singularity/comments/1q6vaxj/how_we_used_gpt52_to_solve_an_erdos_problem/)
- [GPT-Erdos outcome taxonomy](https://github.com/neelsomani/gpt-erdos)
- [LLM Hunter's one-response prompt](https://github.com/mehmetmars7/Erdosproblems-llm-hunter/blob/main/CONTRIBUTING.md)
- [Rethlas generate--verify loop](https://github.com/frenzymath/Rethlas) and
  [its public Erdős deployment audit](https://leon2k2k2k.github.io/posts/2026/rethlas-autonomous-erdos-pipeline/)

## Design decision

Use two layers:

1. a short **mathematical core prompt** that gives the exact target and demands
   a full resolution in either direction; and
2. an **outer research contract** that supplies persistence, tools, records,
   novelty control, resource limits, and independent review.

Do not burden the creative core with the campaign's entire compliance manual.
Do not tell an agent which technical route must work unless it is deliberately
assigned as one orthogonal branch.  Do not ask it to estimate how many human
months a route represents.

## Mathematical core prompt

```text
Resolve the following mathematical problem completely.

[Insert the exact, independently audited statement, definitions, and quantifier
scope. Include only mathematical context that is known to be correct.]

A complete resolution may be either:

1. a rigorous proof of the asserted universal/existential statement; or
2. a rigorous disproof, preferably by an explicit independently checkable
   counterexample or infinite counterexample family.

Work autonomously and adapt your approach as needed. Explore both polarities
unless one is already logically fixed. Do not infer that a direction is
unpromising because humans have worked on it for a long time or because a
human project would be described as taking months. Pursue technically deep or
cross-disciplinary routes when the mathematics supports them.

Partial bounds, finite cases, structural reductions, and computational
near-misses are not a complete resolution, but may be used as stepping stones.
Do not present them as the requested final result. State every imported theorem
precisely and identify every unproved gap.
```

## Outer research contract for a persistent subagent

Append the following after the core prompt, or provide it as the task's durable
operating instructions.

```text
Own this target as a long-horizon research program, not a one-response
brainstorm. Do not return after a literature summary, one plausible sketch, or
the first failed mechanism. Continue through multiple substantive attack
cycles, preserving state between them.

At the beginning:
- freeze and restate the exact audited claim; keep it immutable in a separate
  scope record and hash that the generator cannot rewrite; pass that record
  directly to every checker rather than asking the generator to reproduce it;
- check current priority using primary sources, recent preprints, dissertations,
  comments, repositories, and equivalent terminology; database OPEN status is
  only a lead;
- read the campaign's prior attempts and name what must not be rediscovered;
- define a progress vector, such as verified obligations closed, target cases
  covered, residual complexity, counterexample objective gap, best exact-search
  score, and novelty confidence.

Then work in cycles:
0. Unless a verified full result appears, complete at least four substantive
   cycles spanning at least three genuinely different mechanism families,
   including a deep proof-directed cycle and a deep disproof-directed cycle.
1. Maintain proof and disproof/counterexample branches when both are live.
2. Re-encode the problem in at least two substantially different mathematical
   languages and actively look for a cross-field transfer.
3. Give each route a mechanism fingerprint: representation, central lemma,
   search object, evaluator/checker, and predicted obstruction.  Parameter
   changes alone are not a new mechanism.  Select a small portfolio and
   develop the strongest one deeply; use computation to test a precommitted,
   falsifiable prediction rather than sampling tools shallowly.
4. After each cycle, audit the key implication chain, record what was proved,
   falsified, or merely sampled, update the progress metrics, and choose the
   next cycle yourself.
5. When a mechanism fails, extract the exact obstruction and change a real
   mathematical ingredient. Do not repeat the same search with cosmetic
   parameter changes.
6. Periodically attack your current best argument as a hostile referee. A
   promising candidate must be handed to an independently written checker or
   fresh proof reviewer before any claim.

Stopping and allocation:
- Never stop an intellectual lane because of a human-duration analogy or an
  unsupported guess about how long the remaining insight should take.
- CPU jobs and storage may have explicit measured caps. Stopping one job does
  not kill the underlying mathematical route.
- Continue while audited lemmas remove real cases or quantifiers, a declared
  metric improves, a new orthogonal mechanism survives testing, or the problem
  is converted into a sharper finite target.
- Reallocate only on observed evidence: priority is lost; a central premise is
  falsified; several genuinely different cycles converge to the same precise
  obstruction without further gap reduction; or repeated completed cycles
  leave all declared metrics unchanged. Use judgment rather than a mechanical
  wall-clock rule.

Research record:
- keep a concise append-only ledger of hypotheses, attempts, counterexamples to
  lemmas, exact computations, sources, and next moves;
- save executable artifacts, seeds, versions, hashes, and checker boundaries;
- distinguish PROVED, COMPUTATIONALLY CHECKED, HEURISTIC, CONJECTURAL, and
  FAILED;
- if no full result is obtained in this run, leave a successor packet that
  makes the next cycle stronger rather than merely explaining that the problem
  is difficult.

Worker status is one of `VERIFIED_FULL_RESULT`, `RESULT_CANDIDATE`,
`LANE_EXHAUSTED`, `EXTERNAL_BLOCKER`, `CONTINUE_PACKET`, or
`BUDGET_CHECKPOINT`.  Never return a global `UNRESOLVED` verdict.  A context or
compute limit produces a continuation packet, not an epistemic conclusion.

On a candidate full result:
- stop unrelated exploration;
- pass four separately owned gates: target fidelity and logical entailment;
  internal proof/witness correctness; full-problem coverage and significance;
  and novelty/provenance;
- rerun the statement and priority audit;
- produce a complete human-readable argument or explicit witness;
- obtain independent definition-level verification and formal verification
  when it materially strengthens trust without delaying the public timestamp;
- prepare a narrowly scoped, reproducible public announcement immediately.

Do not ask for routine sign-off. Make bounded in-scope decisions autonomously.
Report early only for a verified full result, a priority collision, a genuine
external blocker, or a decision that would materially expand the authorized
scope.
```

The controller, not the worker, owns promotion and reallocation.  In
particular, correctness verification must receive the authoritative target
artifact directly.  Checking a worker-authored restatement can certify a true
but irrelevant theorem.  Likewise, formal compilation is downstream of a
separate encoding-fidelity check, and novelty is downstream of both.

A worker may nominate `LANE_EXHAUSTED` only after at least three materially
different route fingerprints since the last verified progress, convergence on
the same explicit obstruction, an unchanged progress vector, no untried
orthogonal route within that lane, and agreement from a fresh critic.  This
retires one mechanism family, not the whole problem.

For later episodes, the controller can use this compact continuation prompt:

```text
Read the immutable target, state, ledger, artifacts, and failed-route
fingerprints. Do not recap the campaign. Run the next numbered substantive
cycle using a mechanism not already falsified. If a candidate exists, spend
this cycle trying to destroy it from the original definitions. Update the
durable artifacts and return a status packet; never declare the problem
globally unresolved.
```

## Three-round proof refinement, after a mechanism is chosen

The long-horizon explorer should not also be trusted as its only referee.  Once
it identifies a serious mechanism, use these short continuation prompts, in the
same context for the first two and a fresh context for the third.

### Round 1: develop

```text
Identify the most promising route to a complete proof or disproof and develop
it as far as possible. Give a precise implication chain. Prove every
intermediate claim you can. For each remaining gap, state exactly what would
close it and test whether the gap is actually true. Adapt the route rather than
protecting the first idea.
```

### Round 2: complete

```text
Construct a complete rigorous resolution, using the preceding work but changing
the approach wherever needed. Resolve every named gap. If a claimed lemma is
false, exhibit the failure and replace the mechanism rather than hiding it.
```

### Round 3: fresh hostile review

```text
Act as a skeptical expert referee with no obligation to preserve the proposed
solution. Reconstruct the exact target from the authoritative statement, audit
every quantifier and imported theorem, and search actively for counterexamples
to each key lemma. Repair only defects that can be repaired rigorously. Return
either a complete gap-free proof/disproof or an exact failure certificate and
the smallest unresolved mathematical obligation.
```

## Campaign-specific correction

The original campaign prompt was excellent on fidelity, novelty, Lean trust,
and honest negative packages, but it also invited abandonment when a target
looked "substantially harder than expected" and foregrounded tractability as a
human-style forecast.  Retain its audit discipline.  Replace forecast-based
abandonment with the observed-progress policy above, and treat Lean as a
verification/publication tool rather than a prerequisite for mathematical
discovery.
