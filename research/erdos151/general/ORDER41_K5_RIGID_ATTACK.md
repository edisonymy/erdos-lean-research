# Order 41, maximum `K5`, rigid row R: saturation-fibre contradiction

**Status (2 August 2026): PROVED under the standing row-R hypotheses.**
This note treats only row R of the order-41 `omega(G)=5` reduction.  It is
not a whole-graph CEGAR run, makes no catalogue-completeness assumption, and
makes no claim about row D, the full order-41 problem, or Erdos problem #151.
The proof was developed against
[`ORDER41_K5_RESIDUAL_OVERLAP.md`](ORDER41_K5_RESIDUAL_OVERLAP.md), its
[`independent audit`](ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.md),
[`GENERAL.md`](GENERAL.md), and
[`N40_CLIQUE_CASES_AUDIT.md`](N40_CLIQUE_CASES_AUDIT.md).  In particular,
none of the overlap package's unaudited old counts `6` and `12` is used.

## 1. Standing case and notation

Assume that `G` has order 41, `beta(G)=9`, and row R holds for a fixed
maximum clique `M` of order five.  Thus

```text
V(G) = M disjoint-union U disjoint-union A_1 ... disjoint-union A_5,
|U|=11,  |A_c|=5,
N_M(u)=empty for u in U,
N_M(a)={c} for a in A_c,
d_G(c)=9 for c in M,
every A_c dominates U,
F_c:=G[U union A_c] has beta(F_c)=5.
```

Also `Delta(G)<=9`, since every open neighbourhood is admissible and hence
has order at most `beta(G)`.

The audited package supplies more facts (`F_c` is `K4`-free and, conditional
on catalogue completeness, contains a spanning Ramsey `(3,6;16)` graph), but
the proof below needs neither of them.

For `c in M`, put

```text
S_c := N_G(c) = (M - {c}) union A_c.
```

Then `|S_c|=9`.  It is ambient-admissible: every nontrivial clique contained
in `N(c)` extends by `c`.  Since `beta(G)=9`, `S_c` is a maximum admissible
set.

## 2. PROVED: a singleton fibre contains at most one vertex

Fix `c in M` and `a in A_c`, and define

```text
P_c(a) = {u in U : N(u) intersect A_c = {a}}.
```

**Lemma 2.1.**  `|P_c(a)|<=1`.

**Proof.**  Let `u in P_c(a)`.  The ten-set `S_c union {u}` is not
admissible.  A witnessing ambient-maximal clique cannot lie in `S_c`, since
every clique there extends by `c`.  It must therefore contain `u`.  The only
neighbour of `u` in `S_c` is `a`, so the witness is the edge `ua`.  In
particular, `ua` is an ambient-maximal 2-clique.

If distinct `u,v` both lay in `P_c(a)`, maximality of `ua` would force `uv`
to be absent (otherwise `v` extends `ua`).  But then

```text
(S_c - {a}) union {u,v}
```

would be an admissible ten-set: `u` and `v` are mutually nonadjacent and
anticomplete to `S_c-{a}`, while a clique contained in `S_c-{a}` cannot be
ambient-maximal because it already lies in the admissible set `S_c`.  This
contradicts `beta(G)=9`.  QED.

This is the exact-fibre saturation mechanism specialized to the five
maximum neighbourhoods `S_c`.  It uses ambient maximality throughout.

## 3. PROVED: the five residual cuts force the exact common core

Write

```text
e_c = e_G(U,A_c),       e_U = e(G[U]).
```

For fixed `c`, domination gives every one of the eleven vertices of `U` at
least one neighbour in `A_c`.  Let `s_c` be the number having exactly one.
Lemma 2.1 injects those vertices into the five choices of their unique
neighbour, so `s_c<=5`.  Hence

```text
e_c >= s_c + 2(11-s_c) = 22-s_c >= 17.             (1)
```

On the other hand, `U` is an induced subgraph of every `F_c`, and an
independent set is always admissible.  Thus

```text
alpha(U) <= alpha(F_c) <= beta(F_c)=5.               (2)
```

Equivalently, the complement of `U` is `K6`-free.  Turan's theorem gives

```text
e_U >= C(11,2)-ex(11,K6) = 55-48 = 7.               (3)
```

Finally, vertices of `U` have no neighbours in `M`, so their global degree
budget is exactly

```text
2e_U + sum_c e_c = sum_{u in U} d_G(u) <= 11*9=99.  (4)
```

Combining (1), (3), and (4) gives

```text
99 >= 2*7 + 5*17 = 99.
```

Every inequality is therefore equality.  In particular,

```text
e_U=7,       e_c=17 for every c,       d_G(u)=9 for every u in U.  (5)
```

Equality in Turan's theorem is rigid: the complement of `U` is the balanced
complete five-partite graph `T_5(11)`, with part sizes `3,2,2,2,2`.
Consequently

```text
G[U] is K3 disjoint-union K2 disjoint-union K2
          disjoint-union K2 disjoint-union K2.       (6)
```

There is further equality information which is not needed for the finish:
for every `c`, exactly five vertices of `U` have one neighbour in `A_c`, the
other six have two, and the five singleton vertices have five distinct
unique neighbours in `A_c`.

## 4. PROVED: the transversal obstruction

The following elementary lemma is the terminal obstruction.

**Lemma 4.1.**  Let `F` contain as an induced subgraph

```text
W = C_1 disjoint-union ... disjoint-union C_q,
```

where every `C_i` is a clique of order at least two.  If `F` has any vertex
`a` outside `W`, then `beta(F)>=q+1`.

**Proof.**  Let

```text
L_a = {u in W : au is an F-maximal 2-clique}.
```

The set `L_a` is independent in `F[W]`: if adjacent `u,v` both belonged to
`L_a`, then `a,u,v` would be a triangle and neither incident edge could be a
maximal 2-clique.  Hence `L_a` contains at most one vertex from each `C_i`.
Because `|C_i|>=2`, choose `x_i in C_i-L_a` for every `i`.  The transversal
`I={x_1,...,x_q}` is independent.

The set `I union {a}` has no nontrivial `F`-maximal clique.  There is no edge
inside `I`; every clique involving `a` is therefore an edge `ax_i`; and if
that edge exists, `x_i notin L_a` says precisely that it is not maximal in
`F`.  Thus `I union {a}` is admissible and has order `q+1`.  QED.

Apply Lemma 4.1 to any residual `F_c`, with the five components in (6) and
any `a in A_c`.  It gives

```text
beta(F_c) >= 6,
```

contradicting the standing equality `beta(F_c)=5`.

**Theorem 4.2 (row-R exclusion).**  No graph satisfies the standing rigid
row-R package.

The contradiction occurs before the Folkman arrowing condition
`G -> (3,3)` is needed.  Thus an arrowing-core analysis cannot rescue row R;
the five simultaneous maximum-neighbourhood saturation constraints are
already inconsistent.

## 5. CHECKED: isolated finite sanity check

The standard-library checker
[`checks/rigid_attack/check_rigid_attack.py`](checks/rigid_attack/check_rigid_attack.py)
does not search order-41 graphs.  It independently enumerates only the
finite arithmetic state and the terminal 11-vertex transversal statement.
It verifies

```text
arithmetic states:                              1
forced state:             e(U)=7, all e(U,A_c)=17
maximum independent transversals of K3 + 4K2:  48
independent subsets of K3 + 4K2:               324
independent subsets hitting all transversals:    0
```

Reproduce from the repository root with

```powershell
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\rigid_attack\check_rigid_attack.py
```

The output is `status: CHECKED`.  This check is a falsification guard for
the two tiny finite steps; it is not an UNSAT certificate and is not used as
a substitute for Turan's theorem or the ambient-maximality proofs.

## 6. CONJECTURAL / claim boundary

There is no conjectural step in the row-R exclusion.  The conclusion is
only that row R is impossible under the standing hypotheses.  This note
does not alter the audited status of row D, does not rely on the conditional
Ramsey `(3,6;16)` catalogue reduction, and does not claim a full order-41
theorem, a solution of Erdos #151, publication readiness, or priority.
