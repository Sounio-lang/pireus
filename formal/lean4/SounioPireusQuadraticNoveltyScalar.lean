/-
  Integer novelty scalar over the class literal already bound by
  `SounioPireusQuadraticOrbitCertificate`.

  The four 32-entry tables are copied from `continuity/novelty_oracle.sio`:
  commutator defect, negative-square count, M5 membership, and holdout.
  This file recomputes the published thousandths from those literals. It does
  not rerun the orbit enumeration, recompute a commutator, observe the ELF,
  or promote `claimReady`.
-/
import SounioPireusQuadraticOrbitCertificate

namespace SounioPireusQuadraticNoveltyScalar

open SounioPireusQuadraticOrbitCertificate

set_option maxHeartbeats 0
set_option maxRecDepth 1000000

def absDiff (left right : Nat) : Nat :=
  if left ≥ right then left - right else right - left

def frozenCommutator : Array Nat := #[
  210, 210, 210, 210, 114, 114, 114, 114, 114, 114, 114, 114, 114, 114, 114, 114,
  114, 114, 114, 114, 114, 114, 114, 114, 90, 90, 90, 90, 90, 90, 90, 90]

def frozenSquares : Array Nat := #[
  15, 7, 7, 7, 11, 3, 7, 7, 7, 7, 11, 11, 7, 11, 3, 7,
  11, 7, 7, 7, 7, 11, 3, 7, 9, 9, 5, 5, 9, 5, 5, 9]

def frozenVisited : Array Nat := #[
  1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
  1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0]

def frozenHoldout : Array Nat := #[
  0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]

def frozenNoveltyMilli : Array Nat := #[
  100, 0, 0, 150, 150, 449, 440, 440, 440, 440, 150, 0, 440, 150, 449, 440,
  150, 440, 150, 440, 440, 150, 449, 0, 150, 150, 150, 150, 490, 500, 500, 490]

def frozenGradedMilli : Array Nat := #[
  200, 218, 218, 218, 430, 449, 440, 440, 440, 440, 430, 430, 440, 430, 449, 440,
  430, 440, 440, 440, 440, 430, 449, 440, 490, 490, 500, 500, 490, 500, 500, 490]

def distanceOf (classId : Nat) : Option Nat :=
  match frozenCommutator[classId]?, frozenSquares[classId]? with
  | some commutator, some squares => some (absDiff commutator 210 + absDiff squares 15)
  | _, _ => none

def gradedMilli (classId : Nat) : Option Nat :=
  match distanceOf classId with
  | some distance => some ((26000 + 300 * distance) / 130)
  | none => none

def noveltyMilli (classId : Nat) : Option Nat :=
  match distanceOf classId, frozenVisited[classId]?, frozenHoldout[classId]? with
  | some distance, some visited, some held =>
    some (if held == 1 then 0
      else if visited == 1 then if distance == 0 then 100 else 150
      else (26000 + 300 * distance) / 130)
  | _, _, _ => none

def classScalar (classId : Nat) : Bool :=
  noveltyMilli classId == frozenNoveltyMilli[classId]?
    && gradedMilli classId == frozenGradedMilli[classId]?
    && match frozenVisited[classId]?, frozenHoldout[classId]? with
      | some visited, some held => visited == 0 || held == 0
      | _, _ => false

def scalarCertificate : Bool :=
  let classes := (List.range 32).all classScalar
  let codes := (List.range 1024).all fun code =>
    match embeddedSourceClasses[code]? with
    | some classId => classScalar classId
    | none => false
  frozenCommutator.size == 32
    && frozenSquares.size == 32
    && frozenVisited.size == 32
    && frozenHoldout.size == 32
    && frozenNoveltyMilli.size == 32
    && frozenGradedMilli.size == 32
    && embeddedSourceClasses.size == 1024
    && classes
    && codes

theorem quadratic_novelty_scalar : scalarCertificate = true := by
  native_decide

structure Boundary where
  scalarSourceBindingProved : Bool
  orbitRerun : Bool
  commutatorRecomputed : Bool
  executableBindingProved : Bool
  claimReady : Bool
deriving DecidableEq, Repr

def boundary : Boundary :=
  { scalarSourceBindingProved := true
  , orbitRerun := false
  , commutatorRecomputed := false
  , executableBindingProved := false
  , claimReady := false }

theorem quadratic_novelty_scalar_does_not_promote_a_claim :
    boundary.scalarSourceBindingProved = true
      && boundary.orbitRerun = false
      && boundary.commutatorRecomputed = false
      && boundary.executableBindingProved = false
      && boundary.claimReady = false := by
  decide

end SounioPireusQuadraticNoveltyScalar
