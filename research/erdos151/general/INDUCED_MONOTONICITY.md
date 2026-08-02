# Induced-subgraph monotonicity and Ramsey-jump reduction

**Status (2 August 2026): independently reconstructed and verified by three
campaign agents.** This is a reduction of the orders requiring proof/search,
not a solution of Erdos #151.  A targeted literature search found no explicit
use of this reduction for problem 151; because the lemma is elementary, this
note makes no claim of novelty.

## Lemma: induced-subgraph monotonicity

If `F=G[W]` is an induced subgraph, then

`beta(G) >= beta(F)`.

Indeed, let `S` be admissible in `F`. If a nontrivial maximal clique `K` of
`G` were contained in `S`, then `K` would also be maximal in `F`: any vertex
of `F` extending `K` would be a vertex of `G` extending it. This contradicts
the admissibility of `S` in `F`. Hence `S` is admissible in `G`.

More generally, for every induced `F=G[W]`, every `F`-admissible set remains
`G`-admissible. The restriction to nontrivial maximal cliques causes no issue,
because a nontrivial `G`-maximal clique remains the same nontrivial clique in
`F`.

## Corollary: a least counterexample occurs only at a Ramsey jump

Let `G` be a least-order counterexample on `n` vertices and write
`h=H(n)`. If `H(n-1)=h`, then for any vertex `v`, least-order minimality gives

`beta(G-v) >= H(n-1)=h`.

The lemma then gives `beta(G)>=beta(G-v)>=h`, contradicting that `G` is a
counterexample. Therefore

`H(n-1)<H(n)`,

which is equivalent to

`n=R(3,h)`.

Thus the full problem need only be proved at the Ramsey jump orders
`R(3,2),R(3,3),...`; every order between two jumps propagates immediately by
taking an induced subgraph at the preceding jump.

## Consequence for the current campaign

The campaign has proved the conjecture through order 27, and the next Ramsey
jump is `R(3,8)=28`. Therefore the only order requiring proof or search in the
entire `h=8` plateau is order 28. If every 28-vertex graph has `beta>=8`, then
every graph of orders 29 through 35 does as well by taking any induced
28-vertex subgraph. Order-29 and order-30 search lanes should be cancelled.

The same observation makes the elaborate order-24 proof logically redundant
after the independently audited order-23 theorem: an induced 23-vertex
subgraph already propagates `beta>=7` through order 27. The order-24 proof
remains a valid independent structural check.
