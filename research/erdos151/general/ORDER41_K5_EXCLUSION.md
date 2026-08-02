# Conditional exclusion at order 41 and clique number five

**Status (2 August 2026): CONDITIONAL THEOREM, independently audited.**

## Theorem and exact premise

Assume the published catalogue of Ramsey `(3,6;17)` graphs is complete, and
identify its seven isomorphism classes with the seven graph6 records pinned at

```text
experiments/erdos128/r36_17.g6
SHA-256 3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361
records 7
```

Then every graph `G` on 41 vertices with `omega(G)=5` satisfies

```text
beta(G) >= 10.
```

Equivalently, every such graph has a clique transversal of order at most 31.
Here an admissible, or clique-free, set contains no inclusion-maximal clique
of the ambient graph having at least two vertices, and `beta(G)` is its
maximum order.

The catalogue-completeness statement is the sole external premise of this
theorem package, and it is used only to infer triangle-freeness of the
order-17 residuals (hence of their common induced core `U`).  The pinned
bytes and local graph properties have been replayed, and the analytic row-D
and row-T simplifiers have passed their stated audits and isolated checkers.
The repaired overlap enumeration has also been independently re-audited, but
is corroboration only and is not a logical premise of the proof.  The theorem
must nevertheless not be called unconditional: the repository does not
itself prove that the published seven-record catalogue is complete.

## Prior maximum-neighbourhood fact

Every open neighbourhood is admissible, because a clique contained in
`N(v)` extends by `v`.  Thus `Delta(G)<=beta(G)`.  This fact and its equality
case are prior art: S. H. Bhat, Shivaraja Bhat, and Sowmya Bhat,
[“Clique Free Number of a Graph”](https://www.engineeringletters.com/issues_v31/issue_4/EL_31_4_55.pdf),
*Engineering Letters* **31**(4), 1832–1836 (December 2023), Proposition II.3,
prove in their notation that `Delta(G)<=beta_vc(G)` and that, at equality,
the open neighbourhood of every maximum-degree vertex is a maximum
clique-free set.

Accordingly, the use of a degree-nine neighbourhood as a maximum admissible
nine-set is credited to Bhat–Bhat–Bhat and is not claimed as new.  The local
argument below simultaneously imposes this equality structure at several
vertices of one maximum `K5`.

## Proof

Suppose for contradiction that `G` has order 41, `omega(G)=5`, and
`beta(G)<=9`.  Then `Delta(G)<=9`.  Fix a maximum clique `M` of order five,
put `X=V(G)-M`, and let `n_i` count the vertices of `X` with exactly `i`
neighbours in `M`.  No outside vertex has five `M`-neighbours.  Write

```text
W=sum_i i*n_i=e(M,X),       t=25-W>=0.
```

For `c in M`, let `U` be the `n_0` class, let `A_c` contain the vertices
whose `M`-neighbourhood is exactly `{c}`, and put

```text
Z_c=U union A_c.
```

The audited clique-residual argument gives, pointwise,

```text
beta(G[Z_c])<=5,       |Z_c|<=17.
```

The first inequality uses ambient maximality in the sound direction; the
second uses the verified theorem through order 39 and `R(3,6)=18`.  Direct
elimination gives

```text
sum_c |Z_c|=80+4t+3n_2+7n_3+11n_4<=85.
```

The defining equations and five pointwise capacities have exactly the
following three profiles:

| row | `(t,n_2,n_3,n_4)` | `(n_0,n_1)` | fan sizes | residual sizes |
|---|---:|---:|---:|---:|
| R | `(0,0,0,0)` | `(11,25)` | `5,5,5,5,5` | `16,16,16,16,16` |
| D | `(0,1,0,0)` | `(12,23)` | `4,4,5,5,5` | `16,16,17,17,17` |
| T | `(1,0,0,0)` | `(12,24)` | `4,5,5,5,5` | `16,17,17,17,17` |

Every displayed residual has beta exactly five.  These profiles were
independently checked and are exhaustive for the assumed graph.  It remains
to exclude them.

### Row R: unconditional analytic contradiction

All five vertices `c in M` have degree nine and

```text
N(c)=(M-{c}) union A_c.
```

Each `A_c` dominates the common 11-set `U`.  For `a in A_c`, define the
exact singleton fibre

```text
P_c(a)={u in U:N(u) intersect A_c={a}}.
```

The maximum-neighbourhood ten-set argument gives `|P_c(a)|<=1`.  Indeed,
for `u in P_c(a)`, the only possible ambient-maximal clique in
`N(c) union {u}` is the edge `ua`, so that edge is ambient-maximal.  If two
vertices `u,v` had the same anchor `a`, then `uv` cannot be present because
`u,a,v` would extend `ua`; if `uv` is absent, replacing `a` in `N(c)` by
`u,v` gives an admissible ten-set.  Both cases contradict the assumptions.

At most five of the eleven dominated vertices can therefore have fan-degree
one.  For every `c`,

```text
e(U,A_c)>=5+2*6=17.                              (R1)
```

Since `U` is induced in a beta-five residual, `alpha(U)<=5`.  The complement
of `G[U]` is `K6`-free, and Turán's theorem gives

```text
e(U)>=C(11,2)-ex(11,K6)=55-48=7.                (R2)
```

Vertices of `U` are anticomplete to `M`, so their exact global degree sum is

```text
sum_{u in U}d_G(u)=2e(U)+sum_c e(U,A_c)<=11*9=99.
```

The lower bounds (R1)–(R2) also total `2*7+5*17=99`; equality holds
throughout.  Equality in Turán's theorem makes the complement `T_5(11)`
with part sizes `3,2,2,2,2`, hence

```text
G[U]=K3 disjoint-union 4K2.                     (R3)
```

Fix any `a in A_c`.  The endpoints in `U` for which `au` is an
`F_c=G[U union A_c]`-maximal edge form an independent set and meet each of
the five clique components in (R3) at most once.  Choose one vertex from
each component outside that endpoint set.  Those five independent vertices
together with `a` contain no nontrivial `F_c`-maximal clique.  Thus
`beta(F_c)>=6`, contradicting `beta(F_c)=5`.  Row R is impossible without
any catalogue premise.

### Row T: audited analytic triangle-saturation contradiction

Row T has a four-fan `A_0` at one degree-eight clique vertex and four full
degree-nine fans.  Conditional on the stated catalogue completeness, every
full order-17 residual is triangle-free; therefore their common induced
12-vertex core `G[U]` is triangle-free.  This is the only use of the external
catalogue premise.

For each full fan `A_i`, the singleton-fibre proof from row R applies with
12 vertices in `U`: at most five vertices have fan-degree one, and domination
then gives

```text
e(U,A_i)>=5+2*7=19                    (T1)
```

for each of the four full fans.  This uses ambient maximality in `G` and the
fact that the corresponding clique neighbourhood has the maximum admissible
order nine.

At the deficient fan put

```text
D_0={u in U:N(u) intersect A_0=empty}.
```

If two vertices of `D_0` were nonadjacent, adjoining them to the eight-set
`N(c_0)` would give an ambient-admissible ten-set.  Thus `D_0` is a clique.
Since `U` is triangle-free, `|D_0|<=2`, and hence

```text
e(U,A_0)>=12-|D_0|>=10.               (T2)
```

No singleton-fibre cap is asserted for this deficient fan.

We also use the audited sparse lemma:

```text
H triangle-free, |H|=12, alpha(H)<=5  implies  e(H)>=11,
with equality only for C5 disjoint-union C5 disjoint-union K2.    (S)
```

For completeness, if `H` has `k` components, the bounds `R(3,3)=6` and
`alpha(H)<=5` give `k<=3`.  With at most ten edges, `k=1` would require at
least 11 edges, `k=2` is a forest, and `k=3` is a forest or has one
unicyclic component;
the tree bound `ceil(s/2)`, the unicyclic bound `floor(s/2)`, and parity at
total order 12 always give an independent six-set.  At 11 edges the one-
and two-component cases again give six; the three-component cycle-rank-two
case `(2,0,0)` also gives six by the theta/figure-eight/dumbbell 2-core
classification (including its exceptional two-odd-cycle dumbbell).  The
remaining distribution `(1,1,0)` can attain five only with two odd
non-bipartite unicyclic components and an even tree, forcing component
orders `(5,5,2)`, namely `C5+C5+K2`.  The independent D re-audit enumerator
checks the forest, unicyclic, and bicyclic branches separately.

Here `alpha(U)<=5`, because `U` is induced in a beta-five residual.  Applying
(S), (T1), and (T2) to the exact degree sum yields

```text
108>=sum_{u in U}d_G(u)
   =2e(U)+e(U,A_0)+sum_{i=1}^4 e(U,A_i)
   >=2*11+10+4*19=108.
```

Equality is forced throughout, so

```text
G[U]=C5 disjoint-union C5 disjoint-union K2.            (T3)
```

Fix `a` in a full fan `A_i`, put `F=G[U union A_i]`, and let `E_a` be the
vertices `u in U` for which `au` is an inclusion-maximal 2-clique of `F`.
The set `E_a` is independent: two adjacent members together with `a` would
extend both incident edges to a triangle.  Every independent set in
`C5+C5+K2` is disjoint from some maximum independent five-set `I`: choose an
independent pair outside it in each 5-cycle and the unused endpoint of the
edge.  Thus choose `I` disjoint from `E_a`.  The six-set `I union {a}` is
`F`-admissible, because its only possible nontrivial cliques are edges `au`
with `u notin E_a`, and none is maximal in `F`.  This contradicts
`beta(F)=5`.

The cut proof uses ambient maximality in `G`; the terminal argument uses
maximality only in the residual `F`.  No reversal between those notions is
made.  Row T is impossible under the catalogue premise, without any overlap
enumeration.

### Row D: audited analytic sparse-saturation contradiction

Let `w` be the unique outside vertex with `N_M(w)={p,q}` and define five
order-five spokes

```text
B_p=A_p union {w},       B_q=A_q union {w},
B_c=A_c for the other three clique vertices.
```

Every clique vertex has degree nine, each `B_c` dominates the common
12-set `U`, and the singleton-fibre proof applies to all five spokes,
including the anchor `a=w` in the two shared spokes.  Hence

```text
e_c=e(U,B_c)>=5+2*7=19                 for every c.    (D1)
```

Let `e_U=e(G[U])` and `r=|N(w) intersect U|`.  Since `w` already meets
`p,q` and `Delta(G)<=9`, `r<=7`.  The two shared cuts count every `U-w`
edge twice, whereas the actual `U`-degree sum counts it once.  Therefore

```text
sum_{u in U}d_G(u)=2e_U+sum_c e_c-r.
```

Using (D1) and the twelve degree-nine budgets,

```text
108>=2e_U+5*19-7=2e_U+88,
```

so

```text
e_U<=10.                                             (D2)
```

Conditional on catalogue completeness, any one of the three full order-17
residuals is triangle-free, so its induced core `U` is triangle-free.  This
is again the sole use of the external premise.  Also `alpha(U)<=5`, because
`U` is induced in a beta-five residual.  The audited sparse lemma (S) now
gives

```text
e_U>=11,                                             (D3)
```

contradicting (D2).  The independent strengthened-D re-audit verified (S)
both analytically and by an exhaustive spanning-tree-extension enumerator.
Thus row D is impossible under the catalogue premise, without the D17
overlap enumeration.

Rows R, D, and T exhaust the assumed graph, and each is impossible.  Hence
`beta(G)>=10`, proving the conditional theorem.  QED.

## Audit and computation ledger

| component | result | theorem dependence |
|---|---|---|
| profile/residual proof | PASS after repair and independent re-audit | unconditional given the verified through-order-39 theorem |
| row R | PASS independent audit | analytic; no catalogue |
| row T analytic simplifier | PASS; isolated checker replayed | catalogue completeness only through residual triangle-freeness |
| row D analytic simplifier | PASS independent strengthened-proof re-audit | catalogue completeness only through residual triangle-freeness |
| sparse triangle-free lemma | PASS analytic audit and independent exact enumerator | no catalogue |
| repaired overlap enumeration | PASS after remediation and independent re-audit | none; corroboration only (`T 10 -> 0`, `D 17` cores) |
| pinned catalogue bytes/properties | hashes, manifest, seven local graph properties PASS | does not prove external completeness |

The overlap checker is not a search over all 41-vertex graphs and emits no
order-41 UNSAT certificate.  It exactly enumerates the much smaller
catalogue-overlap problem supplied by the analytic reduction, but neither
row D nor row T logically depends on it.  The rigid, double-saturation,
triangle-saturation, and sparse-profile checkers are isolated arithmetic,
set-system, or finite-lemma guards; their companion notes and audits supply
the mathematical arguments.

## Reproduction

From the repository root in PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
.\.venv\Scripts\python.exe -B experiments\erdos128\verify_manifest.py
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\rigid_attack\check_rigid_attack.py
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\double_saturation\check_double_saturation.py
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\double_saturation_trianglefree\check_trianglefree_12_profile.py
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\double_saturation_reaudit\check_trianglefree_12_enumerator.py
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\triangle_saturation\check_triangle_saturation.py
.\.venv\Scripts\python.exe -B research\erdos151\general\checks\check_order41_k5_overlap.py
```

The relevant outputs are respectively:

```text
manifest: all pinned entries OK; r36_17.g6 has 7 records and the stated hash
rigid: status CHECKED; unique arithmetic state; 48 transversals; 0 hitting sets
double: status CHECKED; minima 128,130,132 > degree budget 108
triangle-free D profile guard: status CHECKED; 150/16/30/165 profiles
D re-audit enumerator: status VERIFIED; 150 sparse profiles, 0 survivors;
  109 equality profiles, unique C5+C5+K2 survivor
triangle saturation: status CHECKED; forced e(U)=11 and C5+C5+K2;
  363 independent endpoint sets, 0 hitting all 50 maximum independent sets
overlap corroboration: status VERIFIED; 4368, 786, 1963, T 10 -> 0, D 17
```

The verified through-order-39 finite inputs can additionally be replayed by

```powershell
.\.venv\Scripts\python.exe -B research\erdos151\check_order28_36_coloring.py
.\.venv\Scripts\python.exe -B research\erdos151\checks\check_k4free_core_degree7.py
```

The environment used for this replay was Python 3.12.4 on Windows 11,
NetworkX 3.5, and python-sat 1.9.dev7.

## Exact artifact hashes

These are the exact source, audit, result, checker, and pinned-data hashes
used by this synthesis.

### Upstream definitions and through-order-39 input

| artifact | SHA-256 |
|---|---|
| `research/erdos151/README.md` | `cf451d0c26bc913816525e180c63fda7bcb125357f8bc1827e9c8d04fb4b45a1` |
| `research/erdos151/general/GENERAL.md` | `bc5503b15bff283ecd23aec8fd9d38496a4a8f108079cc5d5b4d50eefaab8a16` |
| `research/erdos151/general/N40_CLIQUE_CASES_AUDIT.md` | `fce032ea2724c22bb2527624c737377f47461616a7707f518e0c1ea845bb132b` |
| `research/erdos151/order28_36.md` | `ebdfa23d129183fce4c47220bae8c5a5f02a75631c89dcae9a386997780ef11d` |
| `research/erdos151/audit_order28_36.md` | `23f425230da80edd6871043acd223f0bb5b885249a2af28dd82367b3f852d0dd` |
| `research/erdos151/result.json` | `bec51fe5d82881c2ed3a47f258ab0818a542de05bc9d79ac06e8bf55f3455c3a` |
| `research/erdos151/check_order28_36_coloring.py` | `19fa7222a421bad4bbfa9cdb73c86e44673b790f2a51b26952c7b7c69a09c573` |
| `research/erdos151/check_order28_36_coloring.result.json` | `1ec5e5650c805ff16ae22a782af5db9b17a23148caf0884859f3c96394f7b519` |
| `research/erdos151/checks/check_k4free_core_degree7.py` | `ae08af0e380ad4147f3ad9d51327336a8c395f707a1e753c0a3b3b3b75e3e316` |
| `research/erdos151/checks/check_k4free_core_degree7.result.json` | `207bf54c93cf3f08cd58459ba434633a3fb82867111abbaa70656e3a1e7c4bdf` |

### Profile package and repaired overlap corroboration

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_RESIDUAL_OVERLAP.md` | `880b2de61369c2539218ec027b9757b9f8da5b98dd8243a9e06c11e0a09d07ca` |
| `ORDER41_K5_RESIDUAL_OVERLAP_RESULT.json` | `02452b459e79c672b79089c550fd48b1f0eba7cf6257b90c0e891f01efc9d987` |
| `checks/check_order41_k5_overlap.py` | `d4eee390c83862f5b166b9bbd6c71415929d0bf428e7f62aeec2817ba3cc3d95` |
| immutable `ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.md` | `bde66a3d221f5e1762e218cc7b40de70ca690e019c3c99c93a1b0cd1d2120567` |
| immutable `ORDER41_K5_RESIDUAL_OVERLAP_AUDIT.json` | `6f3411401846cc7304264c0025da252f4421467c15190a19572b94b270a19165` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.md` | `d5e7b337867bf449f946472e690ce3119f1f6f8c4e351d583567bb5f2d02896f` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REMEDIATION.json` | `c015740e97888f230bb0e769ea887eb27d8ac86154a115a297f3fb1c50dee4db` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REAUDIT.md` | `05152283f4377073664d2d8e33a922c6cd49ed7aa32ce69a2d07a25bdaee97a9` |
| `ORDER41_K5_RESIDUAL_OVERLAP_REAUDIT.json` | `e5e35724f2d031e78b130f20fc022cc530675aac716cbcca4696b70bcdee7d3c` |

### Row R, row D, and row T analytic packages

| artifact | SHA-256 |
|---|---|
| `ORDER41_K5_RIGID_ATTACK.md` | `9e3803fcb92234c8c75d9c687347bb82e92e7ae30262460d68dc38483c592ab3` |
| `ORDER41_K5_RIGID_ATTACK_AUDIT.md` | `9c0640abbdcecceb41d49c3672204916fd3f8c96e57ca42477b916e9544518bc` |
| `ORDER41_K5_RIGID_ATTACK_AUDIT.json` | `5f37b21616d715bf1567ecdd0ffb82f42b184261e06ea0ac3ea8675a2b845794` |
| `checks/rigid_attack/check_rigid_attack.py` | `0f76e55bb1c28bda2c34dafa3952bf373f86877593e96f1302e650bf0ba46cd7` |
| current strengthened `ORDER41_K5_DOUBLE_SATURATION.md` | `8353be6fde22d8e6edeb455187169b5eae4f6093ae971debcae353e7debddebd` |
| point-in-time source revision bound by the PASS audit | `277b65c4956b56298c76a5e08ed3daf31af040033b4fb001550db3831f7955ca` |
| `ORDER41_K5_DOUBLE_SATURATION_AUDIT.md` | `760a2a904e6416e907fac2c569298704a41f216f2a3b53e5321820f3163d6d4d` |
| `ORDER41_K5_DOUBLE_SATURATION_AUDIT.json` | `e4895962c37fd6ce32636717ba0afb6b041068267542ecc118632db0c0e2656b` |
| `checks/double_saturation/check_double_saturation.py` | `be3cf20744516eaac13e0bb29dee47377ea4b66a33269c659dd0639a8a865951` |
| `ORDER41_K5_DOUBLE_SATURATION_ADDENDUM.md` | `96af57c9754f8b8be871c89787845b7ec1146c91863793df42dba6a63d7ae4d4` |
| `checks/double_saturation_trianglefree/check_trianglefree_12_profile.py` | `68a73ad39d1a4f3857b512b23bb85b90b3cfc73a58784f4c82d5a5e53eb1a325` |
| `ORDER41_K5_DOUBLE_SATURATION_REAUDIT.md` | `af7a974a02891d02a7bb72596ecf5ae442975acb8c3c196aa137c09190e0dbcf` |
| `ORDER41_K5_DOUBLE_SATURATION_REAUDIT.json` | `9bf0db41510cc93708d0380176acef803815c89fb6b070fdc14966ef80ee950a` |
| `checks/double_saturation_reaudit/check_trianglefree_12_enumerator.py` | `d67ea28044f9ca66816eb94d8a92148a7a34ed6146dafc941c31f3d7201cf691` |
| `ORDER41_K5_TRIANGLE_SATURATION.md` | `8b4bf32e955e0d8853d157b87c3a29fe9bf16b1e69ac649a5dbc5601e2aa97ce` |
| `checks/triangle_saturation/check_triangle_saturation.py` | `a495e66dff787f81fe00a5f4f6ad789010ba32efdcb5b5a210cd3c6d557423be` |

### Catalogue, checker dependencies, and priority record

| artifact | SHA-256 |
|---|---|
| `experiments/erdos128/r36_17.g6` | `3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361` |
| `experiments/erdos128/MANIFEST.json` | `ef41bb5eb474a58503549a21b411f13a77217f70edbcc63479f00247c11c92fc` |
| `experiments/erdos128/verify_manifest.py` | `58356d097e737cc00cd38bf6ea1dc3ff4f4491c219837b68f36f3e62158680a4` |
| `experiments/erdos128/r36_16.g6.gz` | `5fd4e68d880e1d4ed05337b97cba0ce15387e1f545744aed80b91bb4b2186f25` |
| `checks/order16_beta5_triangle_witness.json` | `b3778f99571afed723c088143df118e00ab36515083167445b37f024a6e5ad36` |
| `experiments/erdos151_siege/beta_lib.py` | `228c8d82de6a0c292f0f1c89b4a5fc9411feef051d9ddf9cb0950faa1fe6ffac` |
| `experiments/erdos151_siege/beta_bb.py` | `4f8d7fe9361d56119a4ed651ca46acb81366fba612916891178f7d28d06531d6` |
| `ORDER41_K5_PRIORITY.md` | `53569bfce745023775e5af225084c5a0d041cd38256ee594eb64e50ddd649ef9` |

The order-16 catalogue and beta-engine entries are checker-replay
dependencies of the repaired overlap corroboration only.  The analytic
order-41 proof uses the order-17 catalogue solely to infer residual
triangle-freeness.

## Computation, AI assistance, and priority boundary

AI agents materially assisted with discovery, proof development, adversarial
auditing, exact computation, and documentation under Edison Yi's direction.
The theorem's logical row-D and row-T exclusions are the analytic
sparse-saturation and triangle-saturation arguments above.  The strengthened
D proof passed a separate independent re-audit, including an independent
exact enumerator, and the T proof has an isolated exhaustive checker.  The
older T/D overlap computation was repaired after an independent audit found a
missing automorphism-orbit defect and then passed a post-remediation
independent re-audit using a separate parser, isomorphism/automorphism
implementation, and bounded-sum dynamic program.  That history, including
the original FAIL audit, is retained as corroboration; no overlap count is a
premise of this theorem.

The literature search in `ORDER41_K5_PRIORITY.md` found no prior use of this
combined finite architecture.  That is negative-search evidence, not proof
of novelty.  Publication-safe method wording is:

> Bhat, Bhat, and Bhat already proved that equality in
> `Delta(G)<=beta_vc(G)` makes every maximum-degree neighbourhood a maximum
> clique-free set.  The additional finite argument imposes this maximality
> simultaneously at the five vertices of a maximum `K5`, extracts
> singleton-fibre and residual-cut constraints, and combines them with
> sparse triangle-free rigidity, residual maximal-edge transversals, and a
> pinned Ramsey `(3,6;17)` catalogue used only to infer residual
> triangle-freeness.  We found no prior source using this combination.

No categorical “first” claim is made for the fibre observation, and neither
the invariant, Proposition II.3, generic transversal arguments, nor the
Ramsey catalogue is claimed as new.

Finally, this theorem treats only graphs of order 41 with clique number
exactly five.  It does not settle the order-41 `omega=4` lane, all graph
orders, or Erdős problem #151.  It is not a full-solution announcement and,
because of the catalogue premise, is not an unconditional theorem.
