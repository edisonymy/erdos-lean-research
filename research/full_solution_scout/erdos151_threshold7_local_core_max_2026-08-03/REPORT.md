# Erdős #151 threshold-7 local-core search

Date: 2026-08-03

## Outcome

There is no connected graph `Q` on at most 12 vertices satisfying all four
local-core constraints and arrowing `(K3,K3)`:

1. every edge of `Q` belongs to at least two triangles;
2. `omega(Q) <= 4`;
3. every vertex belongs to at most seven triangles; and
4. every link `Q[N(v)]` is one of the four exact nonuniversally-adaptable
   types: `K4`, bowtie, the 7-edge five-vertex graph `Djs`, or the 7-edge
   six-vertex dumbbell.

Two exhaustive graph-generation implementations agree that exactly four
graphs survive the local constraints through order 12.  Independent
CaDiCaL and Z3 checks give explicit triangle-avoiding edge 2-colorings of
all four.  Thus none arrows `(K3,K3)`.

This is a certified finite-order result for the threshold-7 bottleneck.  It
does **not** prove the general threshold-7 coloring lemma, does **not** treat
orders 13 and above, and does **not** solve Erdős #151.

## The four survivors

`B` denotes a bowtie link and `D` the six-vertex dumbbell link.

| Order | Edges | graph6 | Link profile | Triangles | `chi(Q)` | Arrows `(3,3)`? |
|---:|---:|---|---|---:|---:|---|
| 8 | 20 | `GQ~vvg` | `B^8` | 16 | 4 | No |
| 10 | 25 | `IQjUjqm]O` | `B^10` | 20 | 5 | No |
| 12 | 30 | `KCOethkudiLc` | `B^12` | 24 | 4 | No |
| 12 | 33 | `KCOethmuTlLi` | `B^6 D^6` | 26 | 4 | No |

For every row, NetworkX independently confirms connectedness, clique number
at most four, at least two triangles through every edge, at most seven
triangles through every vertex, and exact link isomorphism.  CaDiCaL and Z3
produce different avoiding colorings in every case, and a definition-level
checker confirms directly that neither color contains a triangle.

## Exhaustiveness

A `K4` link at `v` makes `N[v]` a `K5`, contradicting `omega(Q)<=4`.
Consequently the `K4` link can be removed before generation.  The other
three links force every vertex degree to be five or six:

| Link | Vertex degree | Triangles through vertex | K4s through vertex |
|---|---:|---:|---:|
| bowtie (`B`) | 5 | 6 | 2 |
| `Djs` (`J`) | 5 | 7 | 3 |
| dumbbell (`D`) | 6 | 7 | 2 |

For a type profile `(b,j,d)`, the primary scan used the necessary incidence
conditions

* `b+j` even (degree handshake);
* `6b+7j+7d` divisible by 3 (triangle incidence); and
* `2b+3j+2d` divisible by 4 (K4 incidence).

Nauty `geng` generated every connected unlabeled graph of each retained
order and size with minimum degree five and maximum degree six.  The primary
C++ filter scanned 10,329,398 graphs and identified links by a structural
invariant followed by exact canonical labeling.

The independent audit deliberately removed all three incidence restrictions.
It generated **every** connected degree-5-to-6 graph through order 12,
10,814,685 graphs in total, and recognized links by direct permutation
isomorphism rather than canonical codes.  It found the same four graph6
records and no others.  Counts by order were:

| Order | Full-range graphs | Local cores |
|---:|---:|---:|
| 6 | 1 | 0 |
| 7 | 4 | 0 |
| 8 | 17 | 1 |
| 9 | 172 | 0 |
| 10 | 4,428 | 1 |
| 11 | 187,990 | 0 |
| 12 | 10,622,073 | 2 |

The independent raw counts, survivor set, and the primary counts on every
included `(order,edge-count)` slice agree exactly.  The pinned `geng`
executable has SHA-256
`64fa2d95bdaff155ce0fc748d4cba83a50e5ffb03e3acc5f41d86581c0bba7ef`.

## New structural evidence

All four survivors are line graphs of loopless 4-regular multigraphs.  A
separate reconstruction selected the root's incident four-edge cliques,
required every vertex of `Q` to lie in exactly two such cliques, rebuilt the
multigraph, and checked the resulting line graph by independent isomorphism.
The roots are:

* `GQ~vvg`: `C4` with every edge doubled;
* `IQjUjqm]O`: `C5` with every edge doubled;
* `KCOethkudiLc`: `C6` with every edge doubled; and
* `KCOethmuTlLi`: two disjoint triangles joined by a doubled perfect
  matching.

This supports the theory-lane hypothesis that the allowed local structures
may force a line graph of a restricted loopless 4-regular multigraph.  In
that representation `chi(Q)=chi'(H)`.  The exact chromatic numbers
`4,5,4,4` give a second explanation for nonarrowing via the standard
five-color pullback.  The computation is evidence only: it neither proves
the line-graph classification at arbitrary order nor proves the required
edge-chromatic bound for all possible roots.

## Reproduction and artifacts

Primary scan:

```powershell
& .\scan_local_cores.exe <path-to-geng.exe> 12 scan_through_12.json
```

Independent full-range enumeration:

```powershell
& .\audit_full_range.exe <path-to-geng.exe> 12 audit_full_range.json
```

Definition-level and structural checks:

```powershell
& ..\..\..\.venv\Scripts\python.exe crosscheck_enumerations.py
& ..\..\..\.venv\Scripts\python.exe verify_survivors.py
& ..\..\..\.venv\Scripts\python.exe analyze_line_graph_roots.py
```

The consolidated result is `RESULT.json`; detailed raw counts and graph6
records are in `scan_through_12.json` and `audit_full_range.json`; exact
coloring masks are in `survivor_verification.json`; recovered root edge
multiplicities are in `line_graph_root_analysis.json`.

## Stop boundary

Order 12 already required a full-range scan of more than 10.6 million
unlabeled graphs, up from 187,990 at order 11.  Order 13 was not launched.
Extending the catalogue or converting the observed multigraph structure into
a theorem is a new allocation and should be judged against the campaign's
other active lanes.

No git operation, publication, deletion, or edit outside this package was
performed.
