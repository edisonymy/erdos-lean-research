# Immutable target lock: Erdős problem #151

**Status:** copied without mathematical alteration from
`../erdos151_msv_random_blowup_max_2026-08-03/TARGET_LOCK.md` on 3 August
2026.  The authoritative source SHA-256 is
`129e292c307923c10e3d2d7897c9acd0a07803dd1c5e6a5b5393d0c24001173f`.

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

equivalently `beta(G)>=H(n)`.  Its exact negation is the existence of `G` with
`beta(G)<H(n)`.

The stronger condition

```text
G is K4-free and tf_3(G)<H(n)
```

is only a sufficient counterexample certificate: in a K4-free graph every
triangle is ambient-maximal, so `beta(G)<=tf_3(G)`.  It is not an equivalent
restatement and is never used as one in this packet.
