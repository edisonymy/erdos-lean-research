# Order 41, maximum `K4`: joint four-residual coupling checkpoint

**Status (2 August 2026).**  This lane proves that the fixed local
abstraction in [`ORDER41_K4_FIBRE_ATTACK.md`](ORDER41_K4_FIBRE_ATTACK.md)
cannot be repaired merely by adding edges between its four fans: a specific
ten-set remains independent whenever the 24 singleton-fibre edges retain
their required ambient maximality.  The lane then tested one strictly broader
incidence template, re-choosing every core--fan and cross-fan edge while
freezing only the core and within-fan graphs.  A deterministic 1,000-model
run reached **no conclusion**: every outer model was separated, and the last
model had residual independence numbers `(6,6,6,6)` but global independence
number `11`.

This is a genuine four-residual result and a precise stopping checkpoint.  It
does **not** exclude the order-41 `omega=4` case, produce a graph with
`alpha<=9`, encode `beta<=9`, or solve Erdős #151.

## 1. Standing fixed abstraction

Use the vertex labels of the checked abstraction:

```text
U = {0,...,12},
A_0 = {13,...,18}, A_1 = {19,...,24},
A_2 = {25,...,30}, A_3 = {31,...,36},
M = {37,38,39,40}.
```

The base edge set is exactly the one in
`checks/k4_fibre_attack/check_k4_fibre_attack.py`.  Every `A_c` is the
singleton fan of one vertex of `M`; there are no edges between distinct fans.
The four residuals `W_c=G[U union A_c]` are triangle-free with
`alpha(W_c)=beta(W_c)=6`.  Each cut has six exact singleton fibres, one over
each fan vertex, and all 24 corresponding `U--A_c` edges are ambient-maximal.

## 2. PROVED: the fixed abstraction has no cross-fan-only completion

Let

```text
T = {1,3,7,10,17,19,21,26,34,35}.
```

This is an independent ten-set in the base graph.  Suppose arbitrary edges
are now added **only between different fans**, while all 24 singleton-fibre
edges remain ambient-maximal.  The only possible new chords of `T` are the 13
different-fan pairs among its six fan vertices.  Every one is forbidden
because it would complete a triangle on a protected maximal edge:

| proposed chord | protected edge it would extend |
|---|---|
| `17-19` | `5-17` |
| `17-21` | `5-17` (also `8-21`) |
| `17-26` | `5-17` |
| `17-34` | `5-17` |
| `17-35` | `6-35` |
| `19-26` | `5-26` |
| `19-34` | `2-19` (also `5-34`) |
| `19-35` | `6-35` |
| `21-26` | `5-26` |
| `21-34` | `5-34` (also `8-21`) |
| `21-35` | `8-21` |
| `26-34` | `5-26` |
| `26-35` | `6-35` |

For example, adding `17-19` creates the triangle `5-17-19`, contradicting
ambient maximality of `5-17`.  The two same-fan pairs `19-21` and `34-35`
remain absent by the allowed-operation hypothesis.  The four core vertices
in `T` remain independent and anticomplete to its six fan vertices.  Hence
`T` stays independent, so every such completion has `alpha>=10`.

This contradiction uses neither the degree bounds nor `omega<=4`.  It is an
exact elimination of the **fixed witness**, not of all possible core/fan
incidence patterns in the rigid ledger profile.

## 3. The broader finite incidence abstraction

To test whether Section 2 was merely an accident of the chosen incidences,
`search_incidence_coupling.py` freezes only:

- the 18 edges of `G[U]`;
- the four within-fan graphs;
- the `K4` on `M` and the six `M--A_c` spokes for each `c`.

It re-chooses all 312 possible `U--fan` edges and all 216 possible edges
between different fans.  Its static CNF imposes:

1. every vertex degree is in `[5,9]`;
2. each fan dominates `U` and each saturated cut has at least `20` edges;
3. every residual `U union A_c` is triangle-free;
4. every exact singleton fibre has size at most one, and its incident edge is
   ambient-maximal;
5. `omega<=4` through the complete family of potential-`K5` clauses.

Exact residual independent seven-sets and exact global independent ten-sets
are then separated lazily.  Thus a terminal SAT model would satisfy
`alpha(W_c)<=6` for every residual and `alpha(G)<=9`, but it would still omit
the global bad-ten-set condition `beta(G)<=9` and the full H3 recursive
seeded-anchor family.  A terminal UNSAT result, after proof-producing replay,
would eliminate only this fixed-`U`/fixed-within-fan template.

The initial CNF has:

```text
12,136 SAT variables (including cardinality auxiliaries)
112,381 static clauses
79,693 potential-K5 clauses within that total
```

## 4. CHECKED: bounded 1,000-model result

The deterministic CaDiCaL-195 run was stopped at exactly 1,000 outer models:

```text
status:                 NO_CONCLUSION_ITERATION_LIMIT
residual-alpha cuts:    1,359
global-alpha cuts:      17,477
SAT or UNSAT result:    neither
```

The complete 1,000-iteration trajectory was run twice after the iteration
bound was added; both executions returned exactly `1,359` and `17,477` cuts
and the same final edge hash.  The lightweight standard-library checker
replays the frozen graph and mathematical properties, but deliberately does
not pretend to certify the internal SAT counter history.

Every observed model violated at least one exact separation condition.  The
1,000th pre-cut outer model is preserved in
`checks/k4_global_coupling/incidence_coupling_status.json`.  Independent
standard-library replay gives:

```text
variable edges:         109 = 81 incidences + 28 cross-fan edges
full degree interval:   [7,9]
four cut sizes:         [20,21,20,20]
singleton counts:       [6,5,6,6]
residual alphas:        [6,6,6,6]
omega:                  4
global alpha:           11 (required <=9)
global witness:         {7,9,12,14,15,17,19,23,27,29,36}
```

Its canonical full-edge SHA-256 is
`f37c34dbc2403a9520052f796b27deb188c24887831b797273b85a42ae901e41`.
The final iteration added the 11 ten-subsets of this independent 11-set,
which explains the counter change from `17,466` at iteration entry to
`17,477` in the frozen status.

The full H3 recursive seeded-anchor condition was deliberately not hidden in
the static abstraction.  Replay finds respectively `29,36,18,49`
independent-six seeds (counting a seed once when at least one required core
vertex lacks an ambient-maximal anchor into it) that fail H3 in the four
residuals.  Therefore the last outer model is not a globally compatible
joint model, and it is not evidence that only `beta` remains.  It is a
reproducible near-model showing exactly where this abstraction still fails.

## 5. Reproduction and hashes

From the repository root, the bounded run is:

```powershell
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\k4_global_coupling\search_incidence_coupling.py --max-iterations 1000 --output research\erdos151\general\checks\k4_global_coupling\incidence_coupling_status.json
```

The nonzero checkpoint exit is intentional: it records no SAT/UNSAT
conclusion.  Independent replay is:

```powershell
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\k4_global_coupling\check_global_coupling.py
```

It returns `VERIFIED_BOUNDED_NO_CONCLUSION`.  Frozen SHA-256 values:

| artifact | SHA-256 |
|---|---|
| `search_joint_alpha.py` | `e839821b428aa2e32abcb92d037bc4969f5a67c98db93fe58e25e142ece936a2` |
| `search_incidence_coupling.py` | `bc34e88d12f9d755d93f30a90c52b5b56bd0a4a1c78df6f291ed79eb5625f661` |
| `check_global_coupling.py` | `f745f65bccd524599b038320638b17c5285fdf6556bacb36f911fbe9c45bbc3d` |
| `incidence_coupling_status.json` | `b3daace4c917aa61c43e80751ece11b919d5a738bd78ca136fc92b260fe94f26` |
| frozen base checker | `2cc997f7092acb91785cbb92ec7a64894176667fd1132b54524bb6a5e3fe2029` |

## 6. Claim boundary and stopping recommendation

**PROVED:** the exact fixed abstraction cannot be completed by cross-fan
edges while preserving its singleton-fibre maximal edges and `alpha<=9`.

**COMPUTATIONALLY CHECKED:** the finite abstraction, the 1,000-model status,
the last outer model, and every statistic explicitly replayed above.

**NOT PROVED:** existence or nonexistence of a globally `alpha<=9` incidence
completion; H3 feasibility; `beta<=9`; exclusion of the rigid profile;
exclusion of the order-41 `omega=4` case; or Erdős #151.

This lane should now stop.  Its reusable contribution is a new
**singleton-shadow separator**: when an independent ten-set has no possible
cross-fan chord without destroying a singleton maximal edge, the solver must
rewire a core--fan incidence rather than merely densify the fan graph.  That
separator may be useful inside the already assigned whole-graph CEGAR lane.
But the bounded trajectory accumulated thousands of heterogeneous
independence cuts, still missed global alpha by two, and also missed H3 in all
four residuals.  Those are rabbit-hole warning signals under
`ALLOCATION_CHECKPOINT.md`, not evidence for another bespoke local attack.
Renew #151 resources only if the whole-graph lane produces a globally
`alpha<=9` model with shrinking `beta` violations, a substantial certified
profile exclusion, or a genuinely all-four-residual theorem.
