# Order-17 continuation geometry

Date: 2026-08-03

Status: `BUDGET_CHECKPOINT`.  No order-17 enumeration has been claimed.

For a smallest counterexample on 17 vertices, the degree-three packing bound
gives `3t<=17-t` and the degree sum makes `t=68-2m` even.  Therefore only

* `t=4`, `m=32`;
* `t=2`, `m=33`;
* `t=0`, `m=34` (4-regular)

can occur.

## Four-defect route

The four degree-three neighbourhoods are disjoint triples occupying twelve
of the thirteen degree-four vertices.  Removing the defects leaves a
13-vertex graph `H` with degree sequence `4^1 3^12`.  The four attachment
triples must be independent in `H^2`, and the local equality constraints
force `H` to be triangle-free.  This suggests a compact core enumeration:

1. generate all `4^1 3^12` graphs on 13 vertices;
2. reject cores with a triangle;
3. enumerate partitions of twelve vertices into four `H^2`-independent
   triples, leaving the degree-four core vertex unattached;
4. seek twelve compatibility pairs (`32-20`).

## Two-defect route

The two degree-three radius-two balls leave nine other vertices `X`.  The
cross edges between their neighbour triples form a matching of size
`r=0,1,2,3`.  U- and W-block sizes are two for matched core vertices and
three for unmatched ones; each side covers `9-r` of the nine X-vertices.
Matched opposite blocks are disjoint and every block is independent.

The order-16 theta enumerator generalizes directly to `K9`, with internal
edge count `7+r` after exact residual degrees.  Because `K9` subset spaces
grow sharply, first count the W-patterns and degree-vector buckets before
deciding between residual backtracking and a SAT/f-factor encoding.

## Regular route

Run only the count gate first:

`geng -c -d4 -D4 -u 17 34`.

If tractable, reuse the order-16 disk-bounded `res/mod` streaming protocol.
Do not materialize a catalogue before estimating record count, stream bytes,
and two-pass runtime.  A theorem requires both the primary compatibility
graph pass and the independent reverse/on-demand replay with exact shard
hash agreement.

## Boundary

These are exact necessary profiles and proposed finite reductions, not an
order-17 theorem.  The strongest frozen bounded theorem is order at most 16.
