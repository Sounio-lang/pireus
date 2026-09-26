/-
  The eight published reward thousandths are consequences of the frozen
  oracle tables, not free literals. This module imports the class table
  and scalar definitions from `SounioPireusQuadraticNoveltyScalar` and
  the moment definitions from `SounioPireusQuadraticGroupMoment`, then
  checks that the reward for each published phase equals
  `admittedRewardMilli (classIndex ...)` computed from those tables.

  The class index for each phase is the same `classIndex` used in the
  orbit certificate. The published phase for each class is the phase
  used in the M8 batch. This does not rerun orbits, recompute a
  commutator, admit a proposal, observe the ELF, or promote `claimReady`.
-/
import SounioPireusQuadraticNoveltyScalar
import SounioPireusQuadraticGroupMoment

namespace SounioPireusQuadraticGroupMomentConsistency

open SounioPireusQuadraticNoveltyScalar
open SounioPireusQuadraticGroupMoment

set_option maxHeartbeats 0
set_option maxRecDepth 1000000

def publishedPhases : List Nat := [0, 1128, 35, 32841, 1, 32768, 9, 32812]

def publishedClasses : List Nat := [0, 26, 5, 29, 1, 2, 11, 23]

def publishedRewards : List Nat := [600, 650, 949, 1000, 500, 500, 500, 500]

def groupMomentConsistencyCertificate : Bool :=
  let expected := publishedClasses.map fun classId =>
    match admittedRewardMilli classId with
    | some reward => reward
    | none => 0
  let sum := sumList publishedRewards
  let deviations := computeDeviations 8 sum publishedRewards
  let centered := computeCenteredSumSquares 8 sum publishedRewards
  publishedPhases.length == 8
    && publishedClasses.length == 8
    && publishedRewards.length == 8
    && publishedClasses == [0, 26, 5, 29, 1, 2, 11, 23]
    && expected == publishedRewards
    && sum == groupSum
    && deviations == frozenSignedDeviations
    && centered == centeredSumSquares
    && centeredSumSquares > 0

theorem quadratic_group_moment_consistency :
    groupMomentConsistencyCertificate = true := by
  native_decide

structure Boundary where
  consistencyProved : Bool
  orbitEnumeration : Bool
  admissionDecided : Bool
  executableBindingProved : Bool
  claimReady : Bool
deriving DecidableEq, Repr

def boundary : Boundary :=
  { consistencyProved := true
  , orbitEnumeration := false
  , admissionDecided := false
  , executableBindingProved := false
  , claimReady := false }

theorem quadratic_group_moment_consistency_does_not_promote_a_claim :
    boundary.consistencyProved = true
      && boundary.orbitEnumeration = false
      && boundary.admissionDecided = false
      && boundary.executableBindingProved = false
      && boundary.claimReady = false := by
  decide

end SounioPireusQuadraticGroupMomentConsistency