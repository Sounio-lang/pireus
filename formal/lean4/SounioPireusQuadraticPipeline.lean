/-
  End-to-end pipeline: phase to quadratic code to class to reward to moment.

  `phaseToCode` mirrors `quadratic_code` in `continuity/novelty_oracle.sio`:
  diagonal bits 0..3 at phase bits 0,5,10,15; off-diagonal bits 4..9 at
  phase bits 1,2,3,6,7,11,12,13,14 as pairwise XOR sums. `classOfCode`
  reads the same `embeddedSourceClasses` table already bound to the orbit
  certificate. `admittedRewardMilli` from the scalar module computes the
  reward. This does not enumerate orbits, recompute a commutator, admit a
  proposal, observe the ELF, or promote `claimReady`.
-/
import SounioPireusQuadraticNoveltyScalar
import SounioPireusQuadraticGroupMoment

namespace SounioPireusQuadraticPipeline

open SounioPireusQuadraticOrbitCertificate
open SounioPireusQuadraticNoveltyScalar
open SounioPireusQuadraticGroupMoment

set_option maxHeartbeats 0
set_option maxRecDepth 1000000

def bit (value coordinate : Nat) : Nat :=
  (value / 2 ^ coordinate) % 2

def xorNat (a b : Nat) : Nat :=
  -- Natural XOR via repeated bit extraction.
  let rec go (x y acc place fuel : Nat) : Nat :=
    match fuel with
    | 0 => acc
    | n + 1 =>
      let ax := (x / place) % 2
      let bx := (y / place) % 2
      let r := if ax != bx then 1 else 0
      go x y (acc + r * place) (place * 2) n
  go a b 0 1 32

def phaseToCode (phase : Nat) : Nat :=
  let d0 := bit phase 0
  let d1 := bit phase 5
  let d2 := bit phase 10
  let d3 := bit phase 15
  let a01 := (bit phase 1 + bit phase 4) % 2
  let a02 := (bit phase 2 + bit phase 8) % 2
  let a03 := (bit phase 3 + bit phase 12) % 2
  let a12 := (bit phase 6 + bit phase 9) % 2
  let a13 := (bit phase 7 + bit phase 13) % 2
  let a23 := (bit phase 11 + bit phase 14) % 2
  d0 + d1 * 2 + d2 * 4 + d3 * 8 + a01 * 16 + a02 * 32 + a03 * 64 + a12 * 128 + a13 * 256 + a23 * 512

def classOfCode (code : Nat) : Nat :=
  embeddedSourceClasses[code]?.getD 999

def pipelineReward (phase : Nat) : Nat :=
  let code := phaseToCode phase
  let classId := classOfCode code
  match admittedRewardMilli classId with
  | some reward => reward
  | none => 0

def publishedPhases : List Nat := [0, 1128, 35, 32841, 1, 32768, 9, 32812]

def publishedRewards : List Nat := [600, 650, 949, 1000, 500, 500, 500, 500]

def pipelineCertificate : Bool :=
  let computed := publishedPhases.map pipelineReward
  let sum := sumList computed
  let deviations := computeDeviations 8 sum computed
  let centered := computeCenteredSumSquares 8 sum computed
  publishedPhases.length == 8
    && publishedRewards.length == 8
    && computed == publishedRewards
    && sum == groupSum
    && deviations == frozenSignedDeviations
    && centered == centeredSumSquares
    && centeredSumSquares > 0

theorem quadratic_pipeline_certificate : pipelineCertificate = true := by
  native_decide

structure Boundary where
  pipelineProved : Bool
  orbitEnumeration : Bool
  admissionDecided : Bool
  executableBindingProved : Bool
  claimReady : Bool
deriving DecidableEq, Repr

def boundary : Boundary :=
  { pipelineProved := true
  , orbitEnumeration := false
  , admissionDecided := false
  , executableBindingProved := false
  , claimReady := false }

theorem quadratic_pipeline_does_not_promote_a_claim :
    boundary.pipelineProved = true
      && boundary.orbitEnumeration = false
      && boundary.admissionDecided = false
      && boundary.executableBindingProved = false
      && boundary.claimReady = false := by
  decide

end SounioPireusQuadraticPipeline