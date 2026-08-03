# Immutable target lock: Erdős problem #151

**Authoritative live entry:** [Erdős Problems #151](https://www.erdosproblems.com/151).
**Campaign definition source:** [`../../erdos151/README.md`](../../erdos151/README.md).
**Locked on:** 3 August 2026.

For a finite simple graph `G` on `n` vertices:

- `tau(G)` is the minimum size of a vertex set meeting every
  inclusion-maximal clique of `G` having at least two vertices;
- `beta(G)` is the maximum size of a vertex set containing no such ambient
  maximal clique, so `tau(G)=n-beta(G)`;
- `H(n)` is the minimum independence number among all triangle-free graphs on
  `n` vertices.

The exact target is

```text
for every n and every n-vertex graph G, tau(G) <= n-H(n),
```

equivalently `beta(G)>=H(n)`.

Its exact negation is

```text
there exist n and an n-vertex graph G with beta(G)<H(n),
```

equivalently `tau(G)>n-H(n)`.

The finite MSV route searched for the stronger sufficient witness

```text
G is K4-free and tf_3(G)<H(n),
```

where `tf_3(G)` is the largest size of an induced triangle-free vertex set.
This implies the exact negation because every triangle of a `K4`-free graph is
ambient-maximal, so every admissible set is triangle-free and
`beta(G)<=tf_3(G)`. The converse is neither needed nor asserted.
