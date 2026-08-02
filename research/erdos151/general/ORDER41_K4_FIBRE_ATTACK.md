# Order 41, maximum `K4`: singleton-fibre cut attack

**Status (2 August 2026).**  The singleton-fibre lemma, its sharp spoke
cut, the weighted-overlap identity, the Turan/degree inequalities, and the
seeded-core consequences below are **PROVED** under the standing order-41
`omega(G)=4` hypotheses.  An isolated standard-library checker verifies the
finite arithmetic and an explicit four-residual local abstraction.  The
attack does **not** close the case: the first serious local abstraction
survives every scalar inequality and even realizes four exact residuals, but
fails the global `alpha(G)<=9` coupling.  The missing constraint is named in
Section 7.  This is not a whole-graph CEGAR run, uses no graph catalogue, and
makes no full-solution, Git, publication, or priority claim.

The standing inputs are the audited order-41 consequences in
[`N40_CLIQUE_CASES_AUDIT.md`](N40_CLIQUE_CASES_AUDIT.md), the four-residual
analysis in [`N41_K4_ANALYTIC.md`](N41_K4_ANALYTIC.md), the general Folkman
package in [`GENERAL.md`](GENERAL.md), and the saturation mechanism used in
[`ORDER41_K5_RIGID_ATTACK.md`](ORDER41_K5_RIGID_ATTACK.md) and
[`ORDER41_K5_DOUBLE_SATURATION.md`](ORDER41_K5_DOUBLE_SATURATION.md).

## 1. Standing notation and two kinds of deficiency

Let `G` have order 41,

```text
beta(G)=9,  5<=d_G(v)<=9,  alpha(G)<=9,  omega(G)=4,
```

and fix a maximum clique `M` of order four.  For `J subseteq M`, let

```text
X_J = {x outside M : N_M(x)=J},
U=X_empty,                  u=|U|=n_0,
A_c=X_{ {c} },
B_c=N(c)\M=union_{J contains c} X_J.
```

Thus `A_c` is the exact singleton fan, whereas `B_c` is the whole outside
spoke and includes vertices adjacent to two or three vertices of `M`.
Write `n_i=sum_{|J|=i}|X_J|`.

There are two different deficiencies, which must not be conflated:

```text
q_c := 9-d_G(c)=6-|B_c|,                  (clique-degree deficiency)
d_c := 22-|Z_c|,  where Z_c=U union A_c.  (residual deficiency)
```

Put `t=sum_c q_c`.  The clique ledger gives

```text
sum_i n_i=37,
n_1+2n_2+3n_3=24-t,
u=13+t+n_2+2n_3.                                      (1)
```

If `r_c=|B_c\A_c|`, then each `r_c` is an ordinary vertex count, while its
sum over `c` counts a degree-`i` vertex `i` times.  Thus

```text
|Z_c|=u+6-q_c-r_c,
sum_c r_c=2n_2+3n_3.
```

Consequently the audited conservation law is recovered exactly:

```text
sum_c d_c + 3t+2n_2+5n_3=12.                         (2)
```

In particular `t<=4`, `u>=13`, and at least two residuals have order in
`[18,22]`.  Every residual satisfies `beta(G[Z_c])<=6`; for those large
residuals least-order minimality and `R(3,6)=18`, `R(3,7)=23` give
`beta(G[Z_c])=6` exactly.

## 2. PROVED: singleton fibres for a saturated clique vertex

Call `c in M` **saturated** when `q_c=0`, equivalently `d_G(c)=9`.  Then

```text
S_c=N_G(c)=(M\{c}) union B_c,  |B_c|=6,  |S_c|=9.
```

Every nontrivial clique in `S_c` extends by `c`, so `S_c` is admissible.
Since `beta(G)=9`, it is maximum.

**Lemma 2.1 (domination).**  `B_c` dominates `U`.

**Proof.**  For `u in U`, the ten-set `S_c union {u}` is not admissible.
A witnessing ambient-maximal clique cannot lie in `S_c`, hence contains
`u`.  The vertex `u` is anticomplete to `M`, so its neighbours in `S_c`
are exactly `N(u) intersect B_c`; this set is therefore nonempty.  QED.

For `a in B_c`, define the exact singleton fibre

```text
P_c(a)={u in U : N(u) intersect B_c={a}}.
```

**Lemma 2.2 (singleton cap).**  `|P_c(a)|<=1`.

**Proof.**  If `u in P_c(a)`, the only possible witness in
`S_c union {u}` is the edge `ua`; hence `ua` is an ambient-maximal
2-clique.  If distinct `u,v` lay in the same fibre, maximality of `ua`
would force `uv` to be absent, because `v` is adjacent to `a`.  Then

```text
(S_c\{a}) union {u,v}
```

would be an admissible ten-set.  Neither inserted vertex has a neighbour in
the other nine vertices, and a clique in `S_c\{a}` cannot be ambient-maximal
because it already lies in the admissible set `S_c`.  This contradicts
`beta(G)=9`.  QED.

The same exchange proves the more general exact-fibre bound
`|{u in U:N(u) intersect B_c=A}|<=|A|`, but the singleton case already
determines the optimal first-moment cut.

**Corollary 2.3 (sharp six-spoke cut).**  For every saturated `c`,

```text
e_c:=e(U,B_c) >= 2u-6.                               (3)
```

Indeed at most six core vertices have cut-degree one, and all remaining
core vertices have cut-degree at least two.  The bound is sharp at the
abstract bipartite-incidence level: use the six anchors once each and give
every remaining core vertex two spoke neighbours.  Since `u>=13`, every
saturated cut costs at least 20 edges.

No analogous cut is proved for `q_c>0`.  In that case `N(c)` has fewer than
nine vertices and need not extend to a maximum admissible set.  Padding it
with arbitrary vertices and reusing Lemma 2.2 would be unsound.  If

```text
C={c in M:q_c=0},  k=|C|,
```

then only these `k` cuts are available.  The relation `sum q_c=t` gives
`k>=4-t`, but the actual deficiency vector, not merely `t`, determines
which cuts exist.

## 3. PROVED: exact weighted accounting for multi-`M` vertices

For `x outside M union U`, put

```text
i_x=|N_M(x)|,  h_x=|N_U(x)|,
mu_x=|N_M(x) intersect C|.
```

A single edge `ux` is seen in `mu_x` saturated spoke cuts.  Therefore

```text
sum_{c in C} e_c
 = sum_x mu_x h_x
 = E_C+D_C,                                           (4)

E_C=sum_{mu_x>=1} h_x,
D_C=sum_{mu_x>=1}(mu_x-1)h_x.
```

This is the required duplication correction.  If
`E=e(U,V(G)\(M union U))`, then `E>=E_C`, so (3)-(4) imply

```text
E >= k(2u-6)-D_C.                                    (5)
```

It is wrong to sum the cuts as though the `B_c` were disjoint.  Conversely,
subtracting one whole copy for every multi-`M` vertex is also wrong: the
correction is weighted by its actual core degree `h_x` and by `mu_x-1`.

Since `h_x<=9-i_x`, a safe count-only upper bound is

```text
D_C <= Dbar(k,n_2,n_3)
     := 7 n_2 * 1_{k>=2}
        + 6 n_3 * max(0,min(3,k)-1).                  (6)
```

Thus a triple-`M` vertex contributes at most 0, 6, or 12 duplicated units
according as `k<=1`, `k=2`, or `k>=3`.  Formula (4), rather than (6), is the
sharp statement when the exact incidence types `X_J` are known.

## 4. PROVED: Turan and degree-budget inequalities

Every independent set is admissible, and `U subseteq Z_c`, so
`alpha(G[U])<=6`.  If

```text
L_p(m)=(p-r) binom(a,2)+r binom(a+1,2),
where m=pa+r and 0<=r<p,
```

then Turan's theorem in the complement gives

```text
e_U:=e(G[U]) >= L_6(u).                              (7)
```

The exact core degree identity and `Delta(G)<=9` are

```text
2e_U+E=sum_{u in U}d_G(u)<=9u.                       (8)
```

Combining (5)-(8) yields the necessary scalar cut inequality

```text
2L_6(u)+k(2u-6)-D_C <= 9u,                           (9)
```

and the weaker incidence-free version with `D_C` replaced by `Dbar`.

Global `alpha(G)<=9` also applies to the positive-`M` part
`Y=V(G)\(M union U)`, of order `v=37-u`.  Hence `e(G[Y])>=L_9(v)`.  The
sum of degrees over `Y` counts `24-t` edges to `M`, `E` edges to `U`, and
twice its internal edges, giving the second necessary inequality

```text
k(2u-6)-D_C+2L_9(v) <= 9v-(24-t).                   (10)
```

These use the independence hypothesis in a sound count-level way.  They do
not encode where the independent sets lie across the four fans.

For reference, each residual separately also satisfies

```text
e(G[Z_c])>=L_6(|Z_c|),                               (11)
```

but (11) is weaker than the actual condition `beta(G[Z_c])<=6` and does
not sharpen (9) in the first surviving profile below.

## 5. PROVED: seeded core shadows

Let `c` be one of the at least two vertices for which `18<=|Z_c|<=22`, so
`beta(G[Z_c])=6`.  If `I subseteq U` is an independent six-set, then

```text
(M\{c}) union I
```

is a maximum admissible nine-set.  Saturation therefore forces every
`z in U\I` to have an anchor inside `I`.  Since `I` is independent, that
anchor is a singleton.  Consequently:

> **Seeded maximal-edge property.**  For every independent six-set
> `I subseteq U` and every `z in U\I`, some `x in I` makes `zx` an
> ambient-maximal 2-clique.

This is stronger than ordinary domination: the selected edge has no common
neighbour anywhere in `G`.  The statement is vacuous if `alpha(U)<6`.

There is also an exact global independence shadow.  For any independent
`I subseteq U`, define

```text
R(I)={x outside U : N_U(x) intersect I=empty}.
```

Then

```text
alpha(G[R(I)]) <= 9-|I|.                             (12)
```

Otherwise an independent set in `R(I)` could be united with `I`.  In
particular, every independent six-seed leaves a cross-fan shadow of
independence number at most three.  Unlike (7), (9), and (10), condition
(12) is structural and couples all four fans simultaneously.

## 6. Arrowing-core facts: sound boundary

The general Folkman reduction proves `G -> (3,3)`.  Thus `G` contains an
edge-minimal arrowing subgraph `Q` with

```text
chi(Q)>=6,  omega(Q)<=4,
every Q-edge in at least two Q-triangles,
t_Q(v)>=d_Q(v)+1.
```

For completeness, the first triangle assertion follows by extending a good
colouring of `Q-e` when `e` lies in at most one triangle.  The chromatic
bound follows by pulling back a good two-edge-colouring of `K5`.  For the
last inequality, every vertex of the link of `v` has degree at least two,
because the corresponding spoke is in at least two `Q`-triangles.  Hence
the link has at least `d_Q(v)` edges.  Equality would make it a disjoint
union of cycles.  After colouring `Q-v` well, the spokes on each edge-labelled
link cycle can be coloured so that no link edge has both endpoint spokes in
its own colour: alternate on an even cycle; on an odd cycle alternate along
a spanning path and choose the repeated endpoint colour opposite to the
closing edge.  This would extend the good colouring to `Q`, a contradiction.
Thus the inequality is strict.  These arguments concern `Q`, not arbitrary
ambient edges or vertices.

These facts cannot presently be inserted into (9).  The core `Q` need not
contain `M`, any prescribed spoke edge, or any prescribed core vertex, and
an ambient edge outside `Q` need not lie in two triangles.  Charging
`t_Q(v)>=d_Q(v)+1` to all vertices of `U` or to all four clique vertices
would therefore be unsound.  The only unconditional aggregate consequence
used here is `chi(G)>=6`; it supplies no sharper scalar cut than (9)-(10).

## 7. CHECKED: the first surviving abstraction and the missing constraint

The smallest ledger profile already survives all scalar inequalities:

```text
t=n_2=n_3=0,
u=13,  n_1=24,
q_c=0 and |B_c|=|A_c|=6 for all c,
|Z_c|=19 and d_c=3 for all c.
```

There is no duplication.  Since `L_6(13)=8` and `L_9(24)=21`, (9) and
(10) reduce to

```text
2*8+4*20 = 96 <= 117,
4*20+2*21 = 122 <= 192.                              (13)
```

Thus the proposed fibre/Turan/degree contradiction is false even in the
all-saturated, disjoint-spoke row.

The isolated checker goes substantially beyond this numerical row.  It
validates one fixed 41-vertex **local abstraction** with:

```text
M a maximum K4;
U of order 13 with e(U)=18;
four disjoint six-vertex singleton fans;
cut sizes 20,21,20,20;
six singleton fibres in every cut, all forced edges ambient-maximal;
degrees in [5,9], with every U and M vertex of degree 9;
each W_c=G[U union A_c] triangle-free with alpha=beta=6;
every independent residual six-seed satisfying the seeded core anchors.
```

The exact core budget is tight in this abstraction:

```text
2e(U)+sum_c e(U,A_c)=2*18+81=117=13*9.
```

This explicitly refutes any claim that four simultaneous singleton-fibre
cuts, exact residual beta, seeded core domination, and the degree budget
alone are contradictory.

It is deliberately **not** a standing counterexample: its global
independence number is 15.  The checker records an independent ten-set
already visible before any global completion.  More precisely, the maximum
values of `alpha(R(I))` over independent core sets of ranks `0,...,6` are

```text
15,14,13,10,8,4,1.
```

Thus the abstraction even passes the rank-six bound in (12), but fails it
already at rank two (`13>9-2`).  Seeded six-sets alone therefore cannot
repair the global independence gap.  The first missing constraint is
precise:

> **Missing joint cross-fan constraint.**  Realize the four residuals over
> one common `U` while satisfying every shadow (12), preserving all forced
> ambient-maximal singleton/seed edges, the degree ceiling, and
> `omega(G)=4`.  Only after that must the global bad-ten-set condition and
> the arrowing core also be imposed.

Residual-by-residual data and scalar Turan bounds do not encode this joint
completion problem.  Proving that no such completion exists would close
the gap exposed by this attack; producing one would show that the missing
constraint lies still later, at global maximal-clique saturation or
arrowing.  Per the requested stopping rule, this note stops at the first
serious surviving local abstraction and does not start a whole-graph
search.

Run the check from the repository root with

```powershell
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\k4_fibre_attack\check_k4_fibre_attack.py
```

The script uses only the Python standard library.  It checks the 29
conservation profiles, the weighted-duplication identity on all tiny local
states, the scalar survivor (13), and every stated property of the fixed
local abstraction.  It is a falsification guard, not an UNSAT certificate
or a search for a counterexample to Erdos #151.

## 8. Claim boundary

**PROVED:** (1)-(12), including the saturated singleton fibre, the sharp
`2u-6` cut, exact weighted duplication, deficient-vertex qualification,
the Turan/degree inequalities, and the seeded core shadows.

**CHECKED:** the finite arithmetic and the explicit local abstraction in
Section 7.

**CONJECTURAL / open:** impossibility of the named joint cross-fan
completion, and hence the remaining order-41 `omega=4` case.  Nothing here
excludes that case or proves Erdos #151.
