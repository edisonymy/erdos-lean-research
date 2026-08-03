# The order-50 pure protected-core gate

**Status:** scoped theorem, executable arithmetic audit.  This is not a
resolution of Erdős problem #151.

## Outcome

Let `G` be a `K4`-free graph on 50 vertices with `beta(G)<=10`.  Then:

```text
beta(G)=10,             9 <= d_G(v) <= 10 for every v,
```

and `G` cannot itself be an edge-minimal `(3,3)`-Ramsey graph.  Therefore
every hypothetical witness in the order-50 `K4`-free face needs a proper
minimal arrowing core and genuine ambient/core slack.  This removes the
most economical protected-owner construction, in which the ambient graph
is exactly its protected core.

The degree statement is unconditional on smaller open orders.  In
particular, it does **not** depend on a through-order-49 exclusion chain and
does not assume that order 50 is the least counterexample order.

## 1. Degree ladder, with the dependency audited

The hash-pinned order-41 theorem says that every `K4`-free 41-vertex graph
has `beta>=10`.  Taking any induced 41-vertex subgraph of `G` and using
induced monotonicity gives `beta(G)>=10`; hence `beta(G)=10`.

Every open neighbourhood is ambient-admissible, so `Delta(G)<=10`.
Suppose `d(v)<=8`.  Then `G-N[v]` contains an induced 41-vertex graph `F`.
The order-41 theorem supplies an `F`-admissible ten-set `A`.  An admissible
set in an induced subgraph is ambient-admissible: an ambient-maximal clique
contained in the subgraph remains maximal there.  Since `v` is anticomplete
to `A`, the set `A union {v}` is ambient-admissible of order 11, a
contradiction.  Thus `delta(G)>=9`.

This is a strengthening of the least-counterexample-only wording in the
predecessor owner packet.  The actual dependency is the separately audited
unconditional order-41 theorem, not an unverified 42--49 chain.

## 2. Pure-core exclusion

Assume additionally, for a contradiction, that `G` is edge-minimal subject
to `G -> (3,3)`.  Such a graph is connected.  Every edge lies in at least
two triangles: otherwise a good colouring of `G-e` extends over `e`.

For a vertex `v`, its link `L_v=G[N(v)]` is triangle-free (`G` is
`K4`-free) and has minimum degree at least two.  Moreover `L_v` is not
universally adaptably 2-colourable.  Indeed, colour `G-v` without a
monochromatic triangle.  If its edge-colours on `L_v` admitted adaptable
spoke colours, those spoke colours would extend the good colouring to `G`.

### 2.1 If a degree-ten vertex exists

Put

```text
kappa(v)=sum_{a in N(v)} (10-d(a)).
```

The uniform saturation inequality at `n=50`, `beta<=10`, and `d(v)=10`
gives

```text
2 t(v)+kappa(v) <= 22.                                  (2.1)
```

The link has ten vertices and minimum degree two, so `t(v)=e(L_v)>=10`.
If `t(v)=10`, then `L_v` is 2-regular, a disjoint union of cycles.  Such a
link is universally adaptable: orient every cycle and colour the spoke at
the head of each oriented link edge opposite to that link edge's colour.
This contradicts the preceding paragraph.  (The direct census independently
records no obstruction at `(link order,edges)=(10,10)` and one at
`(10,11)`.)  Hence (2.1) forces

```text
t(v)=11 and kappa(v)=0.                                 (2.2)
```

Every neighbour of `v` consequently has degree ten.  Thus the set of
degree-ten vertices is a union of connected components.  Since `G` is
connected and this set is nonempty, `G` is 10-regular.  Applying (2.2) at
every vertex gives

```text
sum_v t(v)=50*11=550.
```

But every triangle contributes three to this sum, while `550` is not
divisible by three.  Contradiction.

### 2.2 If no degree-ten vertex exists

The degree ladder makes `G` connected and 9-regular.  Since every edge is
in a triangle and `G` is `K4`-free, its only nontrivial maximal cliques are
triangles.  Consequently an induced triangle-free set is admissible.

Brooks' theorem gives a proper vertex colouring with at most nine colours:
`G` is neither complete nor an odd cycle.  The union of any two colour
classes is bipartite and hence triangle-free.  The two largest of nine
classes on 50 vertices have total size at least

```text
ceil(2*50/9)=12.
```

Therefore `beta(G)>=12`, contradicting `beta(G)<=10`.

The two degree branches are exhaustive, proving the pure-core exclusion.

## 3. Consequence and exact scope

The published bound `R(3,11)<=50` and the standard Folkman reduction force
any graph in the target face to arrow `(3,3)`.  It therefore contains an
edge-minimal arrowing subgraph `Q`.  Section 2 proves `Q` is a proper
subgraph of `G`.

"Proper" is deliberately not strengthened to `V(Q) proper subset V(G)`:
the needed slack could consist only of ambient edges omitted from a spanning
core.  Nor does this theorem constrain ambient-degree-nine core links to the
ten predecessor templates; that template list applies at ambient degree ten
after the saturation bound.

## 4. Route fingerprint and progress vector

```text
representation:        ambient graph exactly equal to protected minimal core
local mechanism:       nonadaptable K4-free links + degree saturation
cross-link mechanism:  kappa=0 propagates degree ten across core edges
global closure:        triangle-incidence divisibility / Brooks colouring
generic CEGAR used:    no
counterexamples found: 0
quantified class closed: all pure-core graphs in the n=50 K4-free beta<=10 face
remaining object:      proper core with non-core ambient edge/vertex slack
```

## 5. Reproduction

From the workspace root:

```powershell
.\.venv\Scripts\python.exe `
  research\erdos151\n50_protected_core_max_2026-08-03\audit_pure_core_gate.py `
  --census research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\k4free_links_through11_direct.result.json `
  --order41-result research\erdos151\general\k4free_h10\result.json `
  --order41-proof research\erdos151\general\k4free_h10\K4FREE_ORDER41.md `
  --order41-audit research\erdos151\general\k4free_h10\INDEPENDENT_AUDIT.md `
  --saturation-note research\erdos151\high_effort_wave_2026-08-03\general_global\GLOBAL_CORE_AND_ERDOS_ROGERS.md `
  --authoritative-target research\full_solution_scout\erdos151_folkman_owner_coupling_max_2026-08-03\TARGET_LOCK.md `
  --output research\erdos151\n50_protected_core_max_2026-08-03\audit_pure_core_gate.result.json
```

The audit pins every imported dependency by SHA-256, redecodes all ten link
graphs, independently rechecks their Hell--Zhu obstruction status, and
replays the two terminal arithmetic contradictions.

