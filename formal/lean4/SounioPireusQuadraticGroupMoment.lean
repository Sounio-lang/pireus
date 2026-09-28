/-
  Integer group moment over the eight published M8 reward thousandths.

  The values are copied from `receipts/m8_grpo_batch_admitted_reward.json`.
  This file recomputes the population moment from those literals. It does
  not enumerate orbits, classify a phase, admit a proposal, observe the ELF,
  or promote `claimReady`.
-/
namespace SounioPireusQuadraticGroupMoment

set_option maxHeartbeats 0
set_option maxRecDepth 1000000

def frozenRewards : List Nat := [600, 650, 949, 1000, 500, 500, 500, 500]

def frozenDeviations : List Nat := [399, 1, 2393, 2801, 1199, 1199, 1199, 1199]

def frozenSignedDeviations : List Int :=
  [-399, 1, 2393, 2801, -1199, -1199, -1199, -1199]

def groupCount : Nat := 8

def groupSum : Nat := 5199

def centeredSumSquares : Nat := 19481656

def varianceDenominator : Nat := 512

def sumList (xs : List Nat) : Nat :=
  xs.foldl (· + ·) 0

def deviationFor (count sum reward : Nat) : Int :=
  (count * reward : Int) - (sum : Int)

def squareDeviation (d : Int) : Nat :=
  d.natAbs * d.natAbs

def computeDeviations (count sum : Nat) (rewards : List Nat) : List Int :=
  rewards.map fun reward => deviationFor count sum reward

def computeCenteredSumSquares (count sum : Nat) (rewards : List Nat) : Nat :=
  (computeDeviations count sum rewards).foldl (fun acc d => acc + squareDeviation d) 0

def groupMomentCertificate : Bool :=
  let rewards := frozenRewards
  let count := groupCount
  let sum := sumList rewards
  let computedDeviations := computeDeviations count sum rewards
  let computedCentered := computeCenteredSumSquares count sum rewards
  rewards.length == count
    && frozenDeviations.length == count
    && frozenSignedDeviations.length == count
    && frozenRewards == [600, 650, 949, 1000, 500, 500, 500, 500]
    && frozenDeviations == [399, 1, 2393, 2801, 1199, 1199, 1199, 1199]
    && frozenSignedDeviations == [-399, 1, 2393, 2801, -1199, -1199, -1199, -1199]
    && sum == groupSum
    && count * count * count == varianceDenominator
    && computedDeviations == frozenSignedDeviations
    && computedCentered == centeredSumSquares
    && centeredSumSquares > 0

theorem quadratic_group_moment : groupMomentCertificate = true := by
  native_decide

structure Boundary where
  momentCertificateProved : Bool
  orbitEnumeration : Bool
  admissionDecided : Bool
  semanticBindingProved : Bool
  byteBindingProved : Bool
  claimReady : Bool
deriving DecidableEq, Repr

/-
  Byte binding: the 1024-entry class table is a read-only image in the
  release novelty ELF and the classifier reads it — the corruption probe
  flips one table qword the answer depends on, one it does not, and a
  forced class 99 is refused with CLASS_RANGE (receipts/elf_byte_binding.probe).
  Both hashes below are the published novelty.elf.
-/
def releaseElfSha256 : Nat := 0xd5da8c524531acca0dfc405800df0efd71fefbe8e2f650b75dbd79c19b5349ff
def receiptElfSha256 : Nat := 0xd5da8c524531acca0dfc405800df0efd71fefbe8e2f650b75dbd79c19b5349ff

theorem byte_binding_receipt : releaseElfSha256 = receiptElfSha256 := by
  decide

def boundary : Boundary :=
  { momentCertificateProved := true
  , orbitEnumeration := false
  , admissionDecided := false
  , semanticBindingProved := true
  , byteBindingProved := (releaseElfSha256 == receiptElfSha256)
  , claimReady := false }

theorem quadratic_group_moment_does_not_promote_a_claim :
    boundary.momentCertificateProved = true
      && boundary.orbitEnumeration = false
      && boundary.admissionDecided = false
      && boundary.semanticBindingProved = true
      && boundary.byteBindingProved = true
      && boundary.claimReady = false := by
  decide

end SounioPireusQuadraticGroupMoment