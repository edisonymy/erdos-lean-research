# Certified sigma-19 C16 exclusion

**Status:** `CERTIFIED_UNSAT`  
**Certificate completed:** 2026-08-03 21:37:54 UTC  
**Scope:** a finite bipartite subproblem of Erdős problem #64; **not** a full
solution.

## Theorem B

There is no finite simple bipartite graph `G` satisfying all four conditions:

1. `delta(G) >= 3`;
2. one bipartition class has exactly 19 vertices;
3. `G` has no simple `C4` or `C8`;
4. `G` has no simple `C16`.

No `C32` hypothesis or blocking clause is used.  Equivalently, every
bipartite graph of minimum degree at least three with no `C4`, `C8`, or `C16`
has neither bipartition class of size 19.

Combined with the separately checked `sigma <= 18` ladder, this gives the
campaign corollary that a bipartite Erdős--Gyárfás counterexample has at least
20 vertices in each class and hence at least 40 vertices.  The regenerated
`sigma = 14,...,18` certificates still require durable archiving before the
combined ladder is advertised as a public reproducibility package.

## Why the finite encoding is complete

Fix a 19-vertex bipartition class `P`.  For every vertex `y` in the other
class, make its neighborhood `N(y) subset P` a hyperedge.  Minimum degree
gives hyperedge size at least three and point degree at least three.  If two
hyperedges shared two points, the four corresponding vertices would form a
`C4`; hence `C4`-freeness makes the hypergraph linear.  Each hyperedge then
uses at least three distinct pairs from `P`, so

```text
|Y| <= binom(19,2) / 3 = 57.
```

Padding with unused prefix-labelled hyperedge slots therefore embeds every
candidate into the fixed 57-line encoding.  Under this incidence translation:

- the audited static quadrilateral clauses are exactly the `C8` prohibition;
- a simple alternating incidence cycle of length 16 is exactly a graph
  `C16`;
- each of the 512 learned clauses is the negation of all 16 incidences of one
  such cycle.

The standard-library-only block auditor checked all 512 records, with no
duplicates or malformed cycles.  A separate final-CNF auditor reconstructed
the complete base formula and checked that the frozen file consists of its
381,346 clauses followed by exactly those 512 blockers.  The final dimensions
are 85,498 variables and 381,858 clauses.

The semantic audits of the `C8` equivalence and DoubleLex symmetry breaker
also pass.  The latter is only an orbit selector and does not remove every
representative of a feasible incidence structure.

## Certificate binding

The frozen CNF is
`pure19_final_20260803T211655Z.cnf` (6,712,518 bytes, SHA-256
`2B78BD846EEF041355834C1A1EEF1D526E9F88F844DA624C9C40E5DF27E3AD02`).

CaDiCaL 1.9.5 produced the fresh single-writer binary DRAT proof
`pure19_final_20260803T211655Z.fresh_single.drat` (230,688,966 bytes, SHA-256
`9995B9DC0EE484E525826F18D8D2C17448C466372C9B5C57D34F54E6F0A0F98E`).
The solver binary SHA-256 is
`0FFCD0BB1265203C8744B677DCD8D37185D24CBE00F723D53F2431ADE02D0750`.

The independent Linux `drat-trim` binary (SHA-256
`FE99E01A4990E34789C61A17966A5C13BCDEA5EB4C6FBF94F06D55B4718D0B2D`)
read all 230,688,966 proof bytes and reported:

```text
c detected empty clause; start verification via backward checking
c 647097 of 1537815 lemmas in core using 160990667 resolution steps
c 0 RAT lemmas in core; 1332381 redundant literals in core lemmas
s VERIFIED
c verification time: 473.860 seconds
```

The transcript is
`pure19_final_20260803T211655Z.fresh_single.linux-drat-trim.log`, SHA-256
`CEF389F9182F86EB26C47B7DA0893ADD2D436D2D47A137E54BE379CD9FADCBE6`;
stderr is empty.

The native Windows checker transcript is retained but is **not** part of the
certificate: that build misparsed the binary format, read only 622 proof bytes,
and returned `NOT VERIFIED`.  The Linux replay is the binding check because it
read the full file and returned `VERIFIED`.  Likewise, the separately named
`interleaved.INVALID.drat` came from two accidental concurrent writers and is
explicitly excluded from every result.

Machine-readable binding is in
`pure19_certified_result_20260803T213754Z.json`; core hashes are repeated in
`PURE19_CERT_SHA256SUMS_20260803.txt`.

## Correct scope and priority language

The old packet's direct search ranges `38--50` and `38--54` were carry-over
errors.  With 19 fixed points there are at most 57 opposite vertices, so the
direct encoded total-order range is at most `19+57 = 76`.  The cycle length is
nevertheless at most 38 because a bipartite cycle uses equally many vertices
from each class.  Thus `C4`, `C8`, `C16`, and `C32` are the only dyadic cycle
lengths that could occur in the whole encoded range; Theorem B already closes
the family using `C16` alone.

The known 38-vertex model is Gordon Royle's 2009 graph `F038A`, not a new
construction.  The McKay--Afzaly exact extremal table already implies the
sharp total-order-38 threshold for bipartite `{C4,C8}`-free minimum-degree-3
graphs.  Moreover, that table plus `F038A`'s explicit `C16` makes the weaker
total-order-40 corollary implicit in prior public data.  The potentially new
statement is the stronger **part-size** exclusion: it rules out a 19-vertex
class even when the other class is much larger.

The targeted search recorded in `PRIORITY_SEARCH_PURE19_C16_2026-08-03.md`
found no prior statement of this stronger theorem.  That is finite search
evidence, not proof of novelty.  Correct external wording is:

> Certificate-backed part-size strengthening, plausibly new pending
> confirmation from a configuration/extremal-graph specialist.

Nothing here resolves Erdős problem #64.
