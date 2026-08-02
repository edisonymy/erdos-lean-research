import Mathlib.Combinatorics.SimpleGraph.Clique
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Data.Set.Card

/-!
# Erdős 151: the independent-set recurrence

This file formalizes only the structural recurrence used in the finite-order argument.
It does not formalize the Ramsey-number input or the arithmetic through order 22.
-/

open Set

namespace Erdos151Recurrence

universe u

variable {V : Type u}

namespace SimpleGraph

/-- The closed neighborhood of a set of vertices. -/
def closedNeighborhood (G : SimpleGraph V) (I : Set V) : Set V :=
  I ∪ {v | ∃ i ∈ I, G.Adj i v}

/-- A clique of size at least two that is maximal under inclusion. -/
def IsNontrivialMaximalClique (G : SimpleGraph V) (C : Set V) : Prop :=
  C.Nontrivial ∧ Maximal G.IsClique C

/-- A vertex set is avoiding if it contains no nontrivial maximal clique. -/
def IsAvoiding (G : SimpleGraph V) (A : Set V) : Prop :=
  ∀ ⦃C : Set V⦄, IsNontrivialMaximalClique G C → ¬ C ⊆ A

@[simp]
theorem mem_closedNeighborhood {G : SimpleGraph V} {I : Set V} {v : V} :
    v ∈ closedNeighborhood G I ↔ v ∈ I ∨ ∃ i ∈ I, G.Adj i v :=
  Iff.rfl

theorem isAvoiding_empty (G : SimpleGraph V) : IsAvoiding G ∅ := by
  intro C hC hsub
  exact hC.1.ne_empty (eq_empty_iff_forall_notMem.2 fun x hx ↦ by
    simpa using hsub hx)

section Induce

variable {G : SimpleGraph V} {F C : Set V}

/-- A globally maximal clique contained in an induced vertex set remains maximal
in the induced graph.  This is the direction needed by the recurrence. -/
theorem IsNontrivialMaximalClique.induce
    (hC : IsNontrivialMaximalClique G C) (hCF : C ⊆ F) :
    IsNontrivialMaximalClique (G.induce F) (Subtype.val ⁻¹' C) := by
  constructor
  · obtain ⟨x, hx, y, hy, hxy⟩ := hC.1
    exact ⟨⟨x, hCF hx⟩, hx, ⟨y, hCF hy⟩, hy,
      fun h ↦ hxy (congrArg Subtype.val h)⟩
  · constructor
    · intro x hx y hy hxy
      exact hC.2.1 hx hy (fun h ↦ hxy (Subtype.ext h))
    · intro D hD hsub x hx
      have himage_clique : G.IsClique (Subtype.val '' D) := by
        rintro _ ⟨a, ha, rfl⟩ _ ⟨b, hb, rfl⟩ hab
        exact hD ha hb (fun h ↦ hab (congrArg Subtype.val h))
      have hCimage : C ⊆ Subtype.val '' D := by
        intro c hc
        exact ⟨⟨c, hCF hc⟩, hsub hc, rfl⟩
      have himageC : Subtype.val '' D ⊆ C := hC.2.2 himage_clique hCimage
      exact himageC ⟨x, hx, rfl⟩

end Induce

section Lift

variable {G : SimpleGraph V} {I : Set V}

abbrev Residual (G : SimpleGraph V) (I : Set V) :=
  {v : V // v ∉ closedNeighborhood G I}

/-- Lift a set from the residual induced graph back to the original vertex type. -/
def liftResidual (S : Set (Residual G I)) : Set V :=
  Subtype.val '' S

theorem disjoint_liftResidual : Disjoint I (liftResidual (G := G) (I := I) S) := by
  rw [Set.disjoint_left]
  rintro i hi ⟨s, hs, rfl⟩
  exact s.property (Or.inl hi)

/-- If `I` is independent and `S` avoids the nontrivial maximal cliques of the
residual graph induced outside `N[I]`, then `I ∪ S` avoids all nontrivial
maximal cliques of the original graph. -/
theorem isAvoiding_union_liftResidual
    (hI : G.IsIndepSet I)
    {S : Set (Residual G I)}
    (hS : IsAvoiding (G.induce {v | v ∉ closedNeighborhood G I}) S) :
    IsAvoiding G (I ∪ liftResidual S) := by
  intro C hC hCsub
  have hCI : Disjoint C I := by
    rw [Set.disjoint_left]
    intro x hxC hxI
    obtain ⟨y, hyC, hxy⟩ := hC.1.exists_ne x
    have hAdj : G.Adj x y := hC.2.1 hxC hyC hxy.symm
    rcases hCsub hyC with hyI | ⟨s, hs, rfl⟩
    · exact hI hxI hyI hxy.symm hAdj
    · exact s.property (Or.inr ⟨x, hxI, hAdj⟩)
  have hClift : C ⊆ liftResidual S := by
    intro x hx
    rcases hCsub hx with hxI | hxS
    · exact (Set.disjoint_left.1 hCI hx hxI).elim
    · exact hxS
  let F : Set V := {v | v ∉ closedNeighborhood G I}
  have hCF : C ⊆ F := by
    intro c hc
    obtain ⟨s, hs, hsc⟩ := hClift hc
    simpa [F, hsc] using s.property
  have hpull_sub : Subtype.val ⁻¹' C ⊆ S := by
    intro x hx
    obtain ⟨s, hs, hsc⟩ := hClift hx
    have hsx : s = x := Subtype.coe_injective hsc
    simpa [hsx] using hs
  exact hS (IsNontrivialMaximalClique.induce hC hCF) hpull_sub

end Lift

section Finite

variable [Finite V]

/-- The largest cardinality of a set avoiding all nontrivial maximal cliques. -/
noncomputable def avoidanceNumber (G : SimpleGraph V) : ℕ :=
  by
    classical
    letI := Fintype.ofFinite V
    exact (Finset.univ : Finset V).powerset.sup fun A ↦
      if IsAvoiding G (A : Set V) then A.card else 0

theorem card_le_avoidanceNumber {G : SimpleGraph V} {A : Finset V}
    (hA : IsAvoiding G (A : Set V)) :
    A.card ≤ avoidanceNumber G := by
  classical
  letI := Fintype.ofFinite V
  rw [avoidanceNumber]
  simpa [hA] using
    (Finset.le_sup (f := fun A : Finset V ↦ if IsAvoiding G (A : Set V) then A.card else 0)
      (show A ∈ (Finset.univ : Finset V).powerset by simp))

theorem exists_avoiding_card_eq (G : SimpleGraph V) :
    ∃ A : Finset V, IsAvoiding G (A : Set V) ∧ A.card = avoidanceNumber G := by
  classical
  letI := Fintype.ofFinite V
  by_cases hzero : avoidanceNumber G = 0
  · exact ⟨∅, by simpa using isAvoiding_empty G, by simp [hzero]⟩
  obtain ⟨A, hAuniv, hAmax⟩ := Finset.exists_mem_eq_sup (Finset.univ : Finset V).powerset
    (by exact ⟨∅, by simp⟩)
    (fun A : Finset V ↦ if IsAvoiding G (A : Set V) then A.card else 0)
  have hAvoid : IsAvoiding G (A : Set V) := by
    by_contra h
    apply hzero
    simpa [avoidanceNumber, h] using hAmax
  exact ⟨A, hAvoid, by simpa [avoidanceNumber, hAvoid] using hAmax.symm⟩

/-- Finite cardinality form of the independent-set recurrence
`β(G) ≥ |I| + β(G - N[I])`. -/
theorem avoidanceNumber_independent_recurrence
    {G : SimpleGraph V} (I : Finset V) (hI : G.IsIndepSet (I : Set V)) :
    I.card + avoidanceNumber
        (G.induce {v | v ∉ closedNeighborhood G (I : Set V)}) ≤
      avoidanceNumber G := by
  classical
  let R := G.induce {v | v ∉ closedNeighborhood G (I : Set V)}
  obtain ⟨S, hS, hScard⟩ := exists_avoiding_card_eq R
  let L : Set V := liftResidual (G := G) (I := (I : Set V))
    ({x | x ∈ S} : Set {v : V // v ∉ closedNeighborhood G (I : Set V)})
  let A : Set V := (I : Set V) ∪ L
  have hL : L.ncard = S.card := by
    simpa [L, liftResidual] using
      (Set.ncard_image_of_injective
        ({x | x ∈ S} : Set {v : V // v ∉ closedNeighborhood G (I : Set V)})
        Subtype.val_injective)
  have hdisj : Disjoint (I : Set V) L := by
    simpa [L] using
      (disjoint_liftResidual (G := G) (I := (I : Set V))
        (S := ({x | x ∈ S} : Set {v : V // v ∉ closedNeighborhood G (I : Set V)})))
  have hA : IsAvoiding G A := by
    simpa [A, L, R] using
      (isAvoiding_union_liftResidual (G := G) (I := (I : Set V)) hI hS)
  let hAfin : A.Finite := Set.finite_univ.subset (Set.subset_univ A)
  have hAcard : hAfin.toFinset.card = I.card + S.card := by
    rw [← Set.ncard_eq_toFinset_card A hAfin]
    dsimp only [A]
    rw [Set.ncard_union_eq hdisj, hL]
    simp
  calc
    I.card + avoidanceNumber R = I.card + S.card := by rw [hScard]
    _ = hAfin.toFinset.card := hAcard.symm
    _ ≤ avoidanceNumber G := card_le_avoidanceNumber (by simpa using hA)

end Finite

end SimpleGraph

end Erdos151Recurrence

#print axioms Erdos151Recurrence.SimpleGraph.IsNontrivialMaximalClique.induce
#print axioms Erdos151Recurrence.SimpleGraph.isAvoiding_union_liftResidual
#print axioms Erdos151Recurrence.SimpleGraph.card_le_avoidanceNumber
#print axioms Erdos151Recurrence.SimpleGraph.exists_avoiding_card_eq
#print axioms Erdos151Recurrence.SimpleGraph.avoidanceNumber_independent_recurrence
