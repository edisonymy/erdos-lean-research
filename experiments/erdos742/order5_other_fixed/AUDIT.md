# Independent audit of `search.py`

Audit date: 2026-08-02.

## Conclusion

No soundness bug was found in the quotient scope or centralizer lex leaders for
`fixed = 10, 15, 20`. The current solver output must nevertheless remain
exploratory until the generated CNF is hash-locked and an independently
replayed proof certificate is complete.

## Cycle types and edge orbits

An order-five permutation on 25 vertices has cycle type

```text
1^f 5^c,  where f + 5c = 25 and f in {0,5,10,15,20}.
```

The `f=0` case cannot have 157 edges because every unordered-pair orbit has
size five. The certified fixed-five package handles `f=5`. Thus the search
choices `10,15,20` are exactly the remaining cycle types.

For `f` fixed points and `c` five-cycles, the singleton edge orbits are the
`C(f,2)` fixed–fixed pairs. The size-five orbits consist of:

```text
f*c                    fixed-to-cycle orbits,
2*c                    within-cycle distance orbits,
5*C(c,2)               between-cycle offset orbits.
```

`audit_search.py` confirms the following exact counts and verifies that every
listed generator induces a bijection of these edge orbits.

| fixed `f` | cycles `c` | singleton orbits | size-five orbits | total |
|---:|---:|---:|---:|---:|
| 10 | 3 | 45 | 51 | 96 |
| 15 | 2 | 105 | 39 | 144 |
| 20 | 1 | 190 | 22 | 212 |

In particular, the fixed-10 weighted cardinality encoding loses no residue
class. It includes all nine solutions

```text
(fixed edges, five-orbits) =
(2,31), (7,30), (12,29), (17,28), (22,27),
(27,26), (32,25), (37,24), (42,23)
```

to `t + 5q = 157` within `0 <= t <= 45`, `0 <= q <= 51`. The audit fixes a
representative assignment for every possible count pair and compares the
custom weighted CNF with the arithmetic condition. It likewise checks every
count pair for `f=15` and `f=20`.

## Centralizer generators

For the canonical order-five permutation `sigma`, its centralizer on the
vertices is

```text
S_f x (C5 wr S_c).
```

The implementation supplies:

1. adjacent transpositions of the `f` fixed points, generating `S_f`;
2. aligned adjacent swaps of the five-cycles, generating `S_c`; and
3. an independent rotation of each five-cycle, generating `C5^c`.

The audit verifies for every concrete generator that it is a permutation,
commutes with `sigma` on all 25 vertices, maps every pair orbit into one pair
orbit, and induces a bijection of the primary edge variables. The generator
counts are 14, 17, and 20 for `f=10,15,20`, respectively.

The lex constraints are safe even though inequalities for a generating set do
not give complete symmetry breaking. For any graph vector `x`, choose the
lexicographically least vector `x*` in its finite centralizer orbit. For every
generator `g`, `g(x*)` lies in the same orbit, so `x* <=lex g(x*)`. Thus at
least one representative of every graph-isomorphism orbit satisfies all the
added inequalities. Using the generator rather than its inverse does not
matter, since both act within the same finite orbit. The underlying
`add_lex_leader` encoder is the same helper exhaustively audited in the
fixed-five package.

The code uses only the centralizer, not the larger normalizer that can send
`sigma` to a nontrivial power. This leaves symmetry unbroken but cannot remove
a graph.

## Quotient-versus-definition tests

`audit_search.py` independently compares the semantic quotient CNF with
direct all-pairs distances and direct deletion of every edge.

- It exhausts all 512 graphs of type `5^2`, all 2,048 graphs of type
  `1^1 5^2`, and all 16,384 graphs of type `1^2 5^2`: zero mismatches.
- For the production fixed-10 type `1^10 5^3`, it compares 5,000 deterministic
  random invariant graphs: zero mismatches.
- It asks the quotient CNF to accept all 4,095 nontrivial complete bipartite
  graphs obtained by assigning the 13 vertex orbits to two sides. Direct
  deletion checks are repeated for every possible smaller part size 1 through
  12. All pass.

These are strong falsification tests, not a formal proof of the order-25
encoding. The mathematical result still depends on the hand proof that one
pair representative per `sigma`-orbit suffices and on the local critical-edge
witness characterization documented in the fixed-five package.

## Remaining trust boundary

Even if the active searches return UNSAT, publication requires:

1. immutable hashes of `search.py`, the imported fixed-five generator, and
   every generated CNF;
2. proof-producing solver traces and independent DRAT/LRAT replay;
3. the same published Fan, maximum-degree, and dominating-edge reductions used
   in the fixed-five result; and
4. an explicit statement that native LRAT checking is not a Lean proof and
   that the quotient equivalence is hand-audited rather than kernel-checked.

Run the independent implementation audit from the repository root with:

```powershell
.venv\Scripts\python.exe `
  experiments\erdos742\order5_other_fixed\audit_search.py
```

Its claim scope is implementation validation only; it does not accept or
promote the current UNSAT result.

## Independent audit of the fixed-15/fixed-20 split search

`search_split_case.py` replaces the monolithic weighted edge-count automaton
by disjoint ordinary-cardinality cases while leaving the graph constraints and
centralizer lex leaders unchanged. `audit_split_search.py` independently
checks this refactoring.

The audit recovered exactly 21 fixed-15 count pairs and 23 fixed-20 count
pairs. It checked all 4,240 possible singleton/moving count pairs for fixed 15
and all 4,393 for fixed 20: the monolithic encoding accepted exactly 21 and 23
pairs respectively, while each selected split encoding accepted exactly its
one intended pair. There were zero mismatches.

Before cardinality clauses, the monolithic and split production formulas are
byte-identical clause sequences. Their prefix hashes are:

```text
fixed 15: ad5895fc8d4147be6e06d6e992d6e2f207f5316617f11c6eb0736eebe5477640
fixed 20: 5fabf5cfe3b4642043b57e1a70a18797a5adde4f756e50b0ebf820d91c652c21
```

The audit additionally compared the encoded centralizer lex predicates with
their direct Boolean-vector definition on 500 deterministic assignments for
each cycle type, and compared monolithic/split production semantics with
direct graph checks on 30 fully fixed assignments per type. All comparisons
matched. These random production tests are falsification tests, not a formal
proof of the full encoder.

Run the audit from the repository root with:

```powershell
.venv\Scripts\python.exe `
  experiments\erdos742\order5_other_fixed\audit_split_search.py
```

An individual fixed-15 case, for example, is launched with:

```powershell
.venv\Scripts\python.exe `
  experiments\erdos742\order5_other_fixed\search_split_case.py `
  --fixed 15 --fixed-edge-count 57 `
  --cnf .research-cache\f15_t57\case.cnf `
  --metadata .research-cache\f15_t57\metadata.json `
  --candidate .research-cache\f15_t57\candidate.json
```

No split case is promoted merely because a trusted solver returns UNSAT;
publication still requires a hash-locked DRAT/LRAT certificate and independent
replay. Any SAT candidate must pass the direct graph verifier.
