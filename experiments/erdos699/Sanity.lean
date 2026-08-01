import FormalConjecturesUtil

/-!
# Erdős 699 sanity certificate

This checks that the famous exception to the strict `p > i` strengthening is
not an exception to the weak `p ≥ i` statement formalized in the benchmark.
-/

namespace Erdos699Experiment

/-- The weak and strict common-prime claims differ only at the boundary `p = i`.
In particular, a strict-form exception can still satisfy the weak target only
when `i` itself is prime and divides the common gcd. -/
theorem weak_iff_strong_or_boundary (n i j : ℕ) :
    (∃ p : ℕ,
        p.Prime ∧
          i ≤ p ∧
            p ∣ Nat.gcd (Nat.choose n i) (Nat.choose n j)) ↔
      (∃ p : ℕ,
          p.Prime ∧
            i < p ∧
              p ∣ Nat.gcd (Nat.choose n i) (Nat.choose n j)) ∨
        (i.Prime ∧ i ∣ Nat.gcd (Nat.choose n i) (Nat.choose n j)) := by
  constructor
  · rintro ⟨p, hp, hip, hpdvd⟩
    rcases lt_or_eq_of_le hip with hip' | rfl
    · exact Or.inl ⟨p, hp, hip', hpdvd⟩
    · exact Or.inr ⟨hp, hpdvd⟩
  · rintro (⟨p, hp, hip, hpdvd⟩ | ⟨hi, hidvd⟩)
    · exact ⟨p, hp, hip.le, hpdvd⟩
    · exact ⟨i, hi, le_rfl, hidvd⟩

/-- A prime larger than both lower indices and larger than both complementary
indices divides both binomial coefficients.  The important special case is a
prime in `(n - i, n]`: under `i < j ≤ n / 2`, such a prime automatically meets
the four strict inequalities below. -/
theorem large_prime_suffices (n i j p : ℕ) (hp : p.Prime)
    (hi : i < p) (hni : n - i < p) (hj : j < p) (hnj : n - j < p) (hpn : p ≤ n) :
    p ∣ Nat.gcd (Nat.choose n i) (Nat.choose n j) := by
  exact Nat.dvd_gcd (hp.dvd_choose hi hni hpn) (hp.dvd_choose hj hnj hpn)

/-- Therefore the full Erdős 699 conclusion holds whenever the final interval
`(n - i, n]` contains a prime. -/
theorem target_of_prime_in_final_interval (n i j p : ℕ)
    (hij : i < j) (hjhalf : j ≤ n / 2) (hp : p.Prime)
    (hleft : n - i < p) (hpn : p ≤ n) :
    ∃ q : ℕ,
      q.Prime ∧
        i ≤ q ∧
          q ∣ Nat.gcd (Nat.choose n i) (Nat.choose n j) := by
  have hi : i < p := by omega
  have hj : j < p := by omega
  have hnj : n - j < p := by omega
  exact ⟨p, hp, hi.le, large_prime_suffices n i j p hp hi hleft hj hnj hpn⟩

/-- The classical strong-form exception `(n,i,j) = (28,5,14)` still satisfies
the weak target exactly, with the boundary prime `p = i = 5`. -/
theorem exception_28_5_14_satisfies_weak_target :
    ∃ p : ℕ,
      p.Prime ∧
        5 ≤ p ∧
          p ∣ Nat.gcd (Nat.choose 28 5) (Nat.choose 28 14) := by
  refine ⟨5, by norm_num, by norm_num, ?_⟩
  have hfive : Nat.choose 28 5 = 98280 := by decide
  have hfourteen : Nat.choose 28 14 = 40116600 := by decide
  norm_num [hfive, hfourteen]

#print axioms exception_28_5_14_satisfies_weak_target
#print axioms weak_iff_strong_or_boundary
#print axioms large_prime_suffices
#print axioms target_of_prime_in_final_interval

end Erdos699Experiment
