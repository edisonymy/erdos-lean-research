import FormalConjecturesUtil

/-!
# Arithmetic layer for the order-five symmetry attack on Erdos 742

For the canonical order-five action, fixed--fixed pairs form singleton edge
orbits and every other edge orbit has size five.  These lemmas kernel-check
the resulting edge-count split at the forced counterexample size 157.
-/

namespace Erdos742OrderFive

/-- If `t` singleton edge orbits and `q` five-element edge orbits are selected
and the graph has 157 edges, then `t` is 2 modulo 5. -/
theorem fixedEdgeResidue (t q : Nat) (h : t + 5 * q = 157) :
    t % 5 = 2 := by
  omega

/-- A fixed-point-free order-five action cannot preserve a 157-edge graph. -/
theorem fixedPointFreeImpossible (q : Nat) : 5 * q ≠ 157 := by
  omega

/-- For cycle type `1^10 5^3`, there are 45 singleton edge orbits and 51
five-element edge orbits.  These are exactly the nine feasible count pairs. -/
theorem fixedTenCountCases (t q : Nat) (ht : t <= 45) (_hq : q <= 51)
    (h : t + 5 * q = 157) :
    (t = 2 /\ q = 31) \/
    (t = 7 /\ q = 30) \/
    (t = 12 /\ q = 29) \/
    (t = 17 /\ q = 28) \/
    (t = 22 /\ q = 27) \/
    (t = 27 /\ q = 26) \/
    (t = 32 /\ q = 25) \/
    (t = 37 /\ q = 24) \/
    (t = 42 /\ q = 23) := by
  omega

/-- For cycle type `1^15 5^2`, the 21 split cases are exactly the values
`t = 2 (mod 5)` between 2 and 102. -/
theorem fixedFifteenSplitCharacterization (t q : Nat) (ht : t <= 105)
    (_hq : q <= 39) (h : t + 5 * q = 157) :
    2 <= t /\ t <= 102 /\ t % 5 = 2 := by
  omega

/-- For cycle type `1^20 5^1`, the 23 split cases are exactly the values
`t = 2 (mod 5)` between 47 and 157. -/
theorem fixedTwentySplitCharacterization (t q : Nat) (_ht : t <= 190)
    (hq : q <= 22) (h : t + 5 * q = 157) :
    47 <= t /\ t <= 157 /\ t % 5 = 2 := by
  omega

#print axioms fixedEdgeResidue
#print axioms fixedPointFreeImpossible
#print axioms fixedTenCountCases
#print axioms fixedFifteenSplitCharacterization
#print axioms fixedTwentySplitCharacterization

end Erdos742OrderFive
