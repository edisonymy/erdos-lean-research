# Root audit of the tripartite-owner obstruction

**Audited:** 3 August 2026

## Result

The theorem in `FOLKMAN_OBSTRUCTION.md` passes an independent root-level
dependency audit.  This audit supports a public, narrowly scoped
construction-family closure.  It does not support a solution of Erdős #151 or
a claim of mathematical novelty.

## Definition-level reconstruction

Let the indexed owner supports be `V_i`.  After D1, a surviving generated edge
has endpoints co-contained in exactly one `V_i`; therefore it has a unique
owner.  D2 deletes an edge from every post-D1 triangle that is not contained
in an owner.  Deleting edges cannot create new triangles, so every final
triangle is contained in at least one owner.  Since each of its edges is
uniquely owned and all three endpoints lie in that owner, all three edges have
the same owner.

Each owner is tripartite.  Fix labels `0,1,2` independently inside every
indexed owner and colour its surviving `01` and `12` edges red and its `02`
edges blue.  Unique ownership makes this a global colouring.  Every final
triangle is transversal in one owner, hence has colours red, red, blue.  The
final graph is therefore nonarrowing for `(3,3)`.

The separately audited Folkman reduction in `research/erdos151/general/`
then yields `beta(G) >= H(n)`, exactly the inequality from #151.  The argument
does not use random sampling, asymptotics, parameter sizes, the D2 optimizer,
or a surrogate for `beta`.

## Reproducible checks

- All 20 files in the submitted manifest matched their recorded byte counts
  and SHA-256 hashes before this root audit was added.
- `independent_verify.py` was rerun from the exported `NEAR_MISS.json` without
  importing generator code.  `INDEPENDENT_REPLAY_ROOT.json` records PASS for
  graph parsing, the `K4` check, maximum degree, independent and induced
  triangle-free witnesses, exact triangle count, and the explicit
  nonmonochromatic-triangle edge colouring.
- A semantic search on 3 August 2026 found adjacent Folkman and tripartite
  triangle-colouring literature but no statement matching this MSV-specific
  route obstruction.  Because the proof is elementary, novelty remains
  `UNKNOWN`; the public update must be phrased as a campaign observation and
  route closure, not as a first theorem claim.

## Exact scope

The result excludes every construction that simultaneously retains:

1. tripartite indexed owners;
2. unique surviving edge ownership after D1; and
3. deletion of every extrinsic triangle after D2.

It does not exclude unique-owner constructions with an arrowing owner core,
nor constructions that retain cross-owner triangles.  Those are genuinely
different mechanisms and remain live.
