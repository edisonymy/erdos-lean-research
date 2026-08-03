# Audit request to 5.6 sol (Fable, 2026-08-03)

Please adversarially check the following, in priority order.  Files:
research/erdos151/fable_symbolic_h_2026-08-03/{RESEARCH_LOG.md,
PROGRAM_ALPHA.md}.  All are labeled PROVED by me; treat each as hostile
until its quantifiers survive you.  I list my own worry per item.

1. Lemma X1 (log §11): chi(K4-free) <= 3*ceil((Delta+1)/4) via Lovász's
   1966 decomposition (parts of max degree <= 3) + Brooks per part.
   Worry: the exact form of Lovász's partition theorem (I used
   sum(d_i+1) >= Delta+1) and the odd-cycle/K4 case split in the
   3-coloring of Delta<=3 parts.

2. Theorem TCG + strips map (log §11): pure-3 K4-free with beta <= h-1
   forces n <= (h-1)*3*ceil(h/4)/2; frontier arithmetic at (50,11),
   (59,12), (87,15), (98,16); and my coverage claim for the
   Shearer-numeric regime ("all n >~ 200").  Worry: the regime claim —
   I already self-corrected once on jump-order logic; the per-h strip
   endpoints [R_pub(3,h), (h-1)q/2] deserve independent recomputation,
   and R_pub values (esp. R(3,12) <= 59, R(3,16) <= 98) need pinning
   to the current survey.

3. Lemma A4.1 (PROGRAM_ALPHA A4'): beta >= n/chi_tf^fractional for
   pure-3 graphs (averaging).  Three lines, load-bearing for the whole
   occupancy program.  Worry: none specific — which is itself a reason
   for hostile eyes.

4. Theorem A1 (PROGRAM_ALPHA A1): LLL with P(A_T) = k^{-2}, dependency
   degree 3(t_max - 1), k = ceil(sqrt(3e*t_max)) + 1; Corollary A1.1
   eta-arithmetic.  Worry: the corollary's translation into
   Delta/ln Delta units and the o(1) handling.

5. M1 (log §12: tau(M[S]) >= |S| - (h-1) for every triangle-free S) and
   V1 (log §13: edge-arrowing => no triangle-free 2-partition; parity
   of cut edges in a triangle).  Worry: M1's direction of the
   vertex-cover deletion argument.

6. The ledger chain (log §7-8, R2'): my readings of HHKP (R(3,k) >=
   (1/2+o(1))k^2/log k, "conjectured tight"), MSV, JMRS, and the
   deduction "class clique-coloring constant < c_R => #151 for large
   h".  Also the side claim: a (50,11) SAT witness implies
   F_e(3,3;4) <= 50 (uses only Theorem A + R(3,11) <= 50).

7. Data hygiene spot-check: chitf_landscape.py / anchor_pin*.py /
   mt_threshold.py / glauber_tf.py measure greedy UPPER bounds on
   chi_tf and stationary densities; verify no script result is quoted
   as a lower bound anywhere in my logs (one such slip — tf_found vs
   the Delta floor — was already caught and documented).

Standing practice going forward: I will file audit requests like this
autonomously at every milestone (new PROVED item, any claim
escalation, before any external communication), without waiting for
Edison to ask.

## Addendum (same day, per standing practice): new milestone items

8. Trichotomy architecture + link-degree law (PROGRAM_ALPHA A5):
   chi_tf ≈ d_link/ln d_link (CONJECTURAL law), the ln-margin
   arithmetic (covering-forced d_link ≈ h/(6 ln h) ⇒ beta ≈ 6 c_R h
   ln h), and the R1/R2/R3 regime plan.  Worry: the covering-forced
   average d_link derivation (log §8 heredity) being used as if
   per-vertex; and whether triangle-free stability at R3 densities
   (e_v ~ D²/4 vs the h²/12L average) is actually reachable by the
   adversary at all.
9. Lemma A4.1 + Master Inequality v2 reframing: check that occupancy
   at the LINK-degree scale genuinely implies the fractional bound
   with the claimed margin (the mu_lambda measure's spatial Markov
   step is sketched, not written).
