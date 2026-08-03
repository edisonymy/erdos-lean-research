# Append-only protected-core ledger

## Scope lock

- Target: a genuine order-50 `K4`-free graph with `beta <= 10`, or a
  theorem excluding a quantified protected-core class.
- Distinct route: exact first-nonadaptable link templates and their
  cross-link compatibility.
- Excluded reruns: generic graph-level CEGAR; random/process/circulant/MSV
  scans; prior catalogue searches.
- Any SAT graph must be frozen and independently checked before escalation.
  Any UNSAT statement is scoped to its explicitly encoded class.

## Cycle 1 -- degree ladder and pure-core gate

- The unconditional order-41 `K4`-free theorem implies that every
  order-50 `K4`-free graph with `beta <= 10` has `beta=10` and degrees in
  `{9,10}`.  This uses a 41-vertex induced subgraph of `G-N[v]`; it does
  not use a through-order-49 exclusion chain and does not require leastness.
- A graph in this lane cannot itself be an edge-minimal `(3,3)`-Ramsey
  graph.  The proof uses the exact ten-edge adaptability threshold at a
  degree-ten vertex, the saturation inequality, divisibility of the
  triangle-incidence sum, and Brooks' theorem in the all-degree-nine case.
- Consequence: any witness needs genuine core/ambient slack.

## Cycle 2 -- balanced nonreciprocal uniform type-5 subclass

- Frozen scope: 24 vertices, all links type 5 (``H?`DA_{``), with the
  codegree-four matching quotient restricted to nonreciprocal arcs and
  balanced endpoint targets.  This is not the full uniform type-5 class.
- The quotient's underlying graph is 8-regular, hence its complement is
  cubic.  All 94 unlabeled cubic complements on twelve vertices were
  enumerated, including disconnected cases.
- All 94 split CNFs are UNSAT.  Per-case DRAT and LRAT proofs were retained;
  all were accepted by pinned Linux DRAT/LRAT checkers and an independent
  native Windows LRAT checker.
- The reciprocal/endpoint-imbalanced perfect-matching relaxation is being
  pursued only in the separate `type5_full_matching_*` lane.

## Cycle 3 -- pure-triangular chromatic gate

- If every ambient edge were triangular, every open neighborhood would be
  admissible, so `Delta<=beta<=10`.
- Lovasz maximum-degree decomposition into degree-at-most-three parts,
  followed by Brooks on each `K4`-free part, gives `chi<=9`.
- The two largest color classes then form an admissible set of order at
  least `ceil(100/9)=12`, contradicting `beta<=10`.
- Therefore every order-50 `K4`-free witness has an ambient-maximal edge.
  In fact, coloring the pure-triangular subgraph after deleting all maximal
  edges yields a triangle-free 12-set whose induced maximal-edge graph has
  vertex-cover number at least two; triangle-freeness then forces two
  vertex-disjoint maximal edges.
- A sharper nine-color-class remainder count shows that matching number at
  most two would leave at least 46 vertices outside a four-vertex matching
  cover, while all nine remainders together have order at most 45.  Hence
  the maximal-edge graph has a matching of size at least three.
- Uniform finite form: for `beta<=b`, put
  `q=3 ceil((b+1)/4)` and `P=b+(q-2)floor(b/2)`; then
  `nu(M)>=ceil((n-P)/2)`.  This is non-asymptotic.  Besides `(50,10)->3`,
  the arithmetic check records `(59,11)->7`.
- The disjoint-maximal-edge-triple OR supersedes the pair OR as the recorded
  next-run CEGAR constraint; no live inherited process was changed or
  restarted.
- For any three such disjoint maximal edges, their endpoint pairs have an
  independent transversal unless the six endpoints induce the odd-parity
  triangular prism (two maximal triangles joined by the three maximal
  edges).  This is recorded as a structural corollary, not a live-run gate.
