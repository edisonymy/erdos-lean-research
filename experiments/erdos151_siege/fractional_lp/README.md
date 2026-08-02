# Fractional aggregation audit at `h=8`

This directory contains a reproducible audit of the numerical claims in
`research/erdos151/general/FRACTIONAL_AGGREGATION.md`.  It does not encode a
graph, prove existence of a graph, or claim progress on the full Erdős
problem.

Run from the repository root with the bundled environment:

```powershell
.\.venv\Scripts\python.exe experiments\erdos151_siege\fractional_lp\audit_fractional_lp.py
```

The script uses SciPy/HiGHS.  It performs four checks:

1. exact binomial arithmetic for F2 and the integer F3 interval;
2. an exact small MILP for the largest number of triangles in a `K4`-free
   graph on eight vertices when every vertex is in at most seven triangles;
3. the optional second-order triangle-overlap calculation;
4. feasibility of the explicitly stated single-base aggregate LP below,
   both over the reals and after every count variable is made integral.

## The aggregate model `P8`

Fix one edge-minimizing maximum admissible set `S`, with `|S|=7`, and put
`X=V(G)\S`, so `|X|=21`.  The variables are:

- `x_cC_dD`: the number of vertices `v` in `X` with
  `|N(v)∩S|=C` and total degree `D`, for `D∈{5,6,7}` and `1≤C≤D`;
- `s_dD`: the number of vertices of `S` of total degree `D`;
- `p=e(G[S])`, `q=e(G[X])`, `z=#isolated(G[S])`,
  `u=#triangles(G[S])`, and `T=#triangles(G)`;
- `a1,a2,a3`: the numbers of fixed-`S` anchor incidences `(v,A)` with
  `|A|=1,2,3`;
- `N2,N3,N4`: the numbers of ambient inclusion-maximal cliques of the
  indicated sizes.

All variables are nonnegative.  The LP contains exactly these families of
linear constraints (the script gives each row a matching descriptive name):

- `sum x=21`, `sum s=7`;
- the exact two degree handshakes
  `sum c*x = sum d*s-2p` and `2q=sum(d-c)*x`;
- the Caro–Wei and Turán necessary consequences of `alpha(G[X])≤7`;
- `x_1≤z`, using F4 and the proved exact-fibre lemma; and the elementary
  incidence bounds `7-z≤2p≤6(7-z)`;
- `u≤12` and `p≤16` because admissibility and `omega(G)≤4` make `G[S]`
  `K4`-free, plus `3u≤5p`;
- anchor coverage prefix inequalities: every `c=1` vertex uses a singleton
  anchor, every `c≤2` vertex uses an anchor of size at most two, and every
  outside vertex uses an anchor of size at most three;
- availability `a_k≤sum binom(c,k)x`, E2 capacities
  `a1≤49`, `a2≤7p`, `a3≤7u`, and the injections
  `a1≤N2`, `a2≤N3`, `a3≤N4`;
- F2 coverage
  `N2*C(26,6)+N3*C(25,5)+N4*C(24,4)≥C(28,8)`;
- `N4≥1`, the consequence of the independently audited order-28 Ramsey-core
  argument (and `omega(G)≤4`, which makes that `K4` ambient-maximal);
- elementary edge/triangle/maximal-clique coverage and supply rows:
  every edge extends to a maximal clique, every non-`L` edge lies in a
  triangle, every nonmaximal triangle lies in a `K4`, and a triangle has at
  most five `K4` extenders;
- total triangle caps `8,12,11` at degree `5,6,7`: the first two are Turán
  bounds in the `K4`-free link, while `11` is the valid mixed-profile raw
  two-walk bound only for degree-seven vertices;
- local `K4` caps `4,8,12` at degrees `5,6,7`, by Zykov's triangle bound in
  the link.

Every displayed row is necessary for a hypothetical least counterexample,
but the converse is false.  In particular `P8` is only a projection of
proved conditions, not an exact formulation of T″.

## Why the proposed small count LP is underdetermined

Counts by `(attachment size,total degree)` do not determine any of the
following data required by T″:

- which outside vertices share a particular anchor and whether pairs inside
  that fibre are adjacent (E2);
- which subsets of `S` are cliques and whether `A∪{v}` is ambient-maximal;
- the adjacency and common-neighbour data needed for `alpha≤7` and the
  domination cascade;
- the rebased attachment type of every other vertex after an E4 exchange;
- overlaps among maximal cliques or among the maximum admissible sets.

For example, after swapping `a` for `v`, the new attachment count of another
outside vertex `w` contains the term
`-1[wa∈E]+1[wv∈E]`.  Neither indicator is determined by the marginal
`x_cC_dD` counts.  Likewise, the degree sequence alone cannot determine an
independence number (`C6` and `2K3` are both 2-regular but have independence
numbers 3 and 2).  Adding the missing pair, clique, anchor, and set-incidence
variables produces a graph/exchange MILP or SAT model indexed by many sets;
it is no longer the advertised small LP over count densities.

The feasible real and integral outputs therefore prove only that this honest
marginal projection does not close `h=8`.  They are not graph witnesses.

## The F3 corner is already empty

The arithmetic `59≤N3≤65` is correct after retaining only F2 and the coarse
consequence `t_v≤7`.  It is not a realizable corner under the complete
two-walk assumptions cited in the source note.  In the 7-regular case, if
`ell_v` is the number of isolated vertices of the link and `u_v` counts
nonneighbors with a unique common neighbor, the audited argument gives

```text
u_v >= 2t_v-2,       u_v <= 6ell_v.
```

Thus `L=∅` gives `ell_v=0` and `t_v≤1`.  On the other hand, `L=∅` says every
one of the seven link vertices is nonisolated, so the link has at least four
edges and `t_v≥4`.  This is an immediate contradiction.  Independently, the
audited order-28 Ramsey-core proof forces a `K4`, so its hypothetical
counterexample also cannot have `omega=3`.  The script prints this scope
warning immediately after reproducing `59..65`.

## Second-order overlap identity

In the counterfactual F3 corner (`7`-regular, `omega=3`, `L=∅`), put `m_W`
for the number of triangles in an eight-set `W`.  If
`A=sum_e binom(mu_e,2)` and `V=sum_v binom(t_v,2)`, then the exact pair count
is

```text
P = 7315 A + 1540 V + 231 binom(N3,2).
```

The coefficients come from union sizes four, five, and six:
`C(24,4)=10626`, `C(23,3)=1771`, and `C(22,2)=231`.

The best local bound is `m_W≤15`, and it is sharp.  Analytically, for an
eight-vertex induced graph `H`, degree seven makes all triangles pass through
the universal vertex (`≤7` total), while degree six gives at most twice the
triangles through that vertex (`≤14`).  If `Delta(H)≤5`, Mantel in every link
gives `3m_W≤8*6`, and equality 16 would force `H` to be 5-regular.  Its
complement would then be 2-regular; `K4`-freeness leaves only `C3+C5` among
the possible cycle decompositions with independence number at most three,
and its complement has 15 rather than 16 triangles.  The complement of
`C3+C5` attains 15.  The local MILP independently verifies this optimum.

Consequently `D=sum_W(m_W-1)≥2P/15`; the printed table excludes the
projected values `N3=59,...,63` and leaves `64,65`.  This remains a
counterfactual projection because, as above, the full `L=∅` two-walk package
is already infeasible.

## Next sound target with `L≠∅`

A next count experiment should first keep the exact `L` data in the
7-regular `omega≤4` subcase.  It can remain linear by solving a separate LP
for each fixed integer `m=N2≥1`:

- enumerate the realizable seven-vertex link profiles
  `(ell,t,k)=(#isolates,#edges,#triangles)`, retaining the two-walk condition
  `t≤3ell+1`, and let `y_ell,t,k` count ambient vertices of each profile;
- impose `sum y=28`, `sum ell*y=2m`, `sum t*y=3T`, and
  `sum k*y=4N4`;
- introduce `q_j` for triangles having exactly `j=0,...,5` `K4` extenders,
  with `q_0=N3`, `sum q_j=T`, and `sum j*q_j=4N4`;
- introduce `p_j` for edges in exactly `j=0,...,6` triangles, with
  `p_0=m`, `sum p_j=98`, and `sum j*p_j=3T`;
- retain the summed unique-common-neighbour routing inequality
  `sum max(0,2t-2)y_ell,t,k ≤ sum ell(ell-1)y_ell,t,k`.

The first genuinely stronger `L`-independent-set lower bound is the
third-order Bonferroni truncation.  Put

```text
P_adj = sum_v binom(ell_v,2),
P_dis = binom(m,2)-P_adj.
```

Then the pair-intersection sum for the events "an eight-set contains this
`L`-edge" is

```text
S2 = P_adj*C(25,5) + P_dis*C(24,4).
```

To bound the triple sum, add `z_ab`, the number of `L`-edges joining
vertices of `L`-degrees `a,b`, with the usual degree-mixing handshakes.  The
number of three-edge subsets of `L` whose union has four vertices is exactly

```text
R4 = sum_v binom(ell_v,3) + sum_ab (a-1)(b-1) z_ab,
```

counting 3-stars and `P4`s.  The remaining triple types have unions of five
or six vertices, so a valid upper bound is

```text
S3 ≤ C(23,3)*binom(m,3) + (C(24,4)-C(23,3))*R4.
```

Hence

```text
# L-independent 8-sets ≥ C(28,8)-m*C(26,6)+S2-S3_upper,
```

which can replace the first-order right side in F2.  Fixing `m` makes every
binomial term constant, so this is a genuine small LP rather than a hidden
quadratic count program.  It directly retains the `L` structure that made
the old corner collapse.  If this relaxation is still feasible, the next
honest refinements are the three-edge matching count (instead of dropping
its favorable term) and maximal-clique overlap types—not unsupported
exchange-closure inequalities on marginal attachment counts.
