# Immutable target lock: Erdős problem #151

For a finite simple graph `G` on `n` vertices, `beta(G)` is the maximum
size of a vertex set containing no nontrivial ambient maximal clique, and
`H(n)` is the minimum independence number of a triangle-free graph on `n`
vertices.  The target is

```text
beta(G) >= H(n).
```

The exact negation is a graph with `beta(G) < H(n)`.  In the protected
order-50 lane, a `K4`-free graph with `beta(G) <= 10` would be a complete
counterexample because the published bound `R(3,11) <= 50` gives
`H(50) >= 11`.

This packet studies only the protected minimal `(3,3)`-Ramsey core forced
inside such a graph.  Local core conditions are necessary, not sufficient:
a locally compatible core is not a counterexample until the ambient graph
passes exact `beta`, `K4`, and independent arrowing checks.

