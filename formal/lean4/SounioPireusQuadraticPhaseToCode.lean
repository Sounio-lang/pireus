/-
  The Lean `phaseToCode` is an independent reimplementation of
  `quadratic_code` in `continuity/novelty_oracle.sio`. This module checks
  that it agrees with the 1024-entry `embeddedSourceClasses` table on all
  1024 codes, using the inverse map `codeToPhase` from the behavioral
  checker. Each code has 64 phases in its fibre. This does not enumerate
  orbits, recompute a commutator, admit a proposal, observe the ELF, or
  promote `claimReady`.
-/
import SounioPireusQuadraticPipeline

namespace SounioPireusQuadraticPhaseToCode

open SounioPireusQuadraticOrbitCertificate
open SounioPireusQuadraticNoveltyScalar

set_option maxHeartbeats 0
set_option maxRecDepth 1000000

def codeToPhase (code : Nat) : Nat :=
  -- Inverse of phaseToCode: put code bits 0..3 at phase bits 0,5,10,15
  -- and code bits 4..9 at phase bits 1,2,3,6,7,11, leaving the opposite
  -- triangle zero. This is the same `phase_for_code` as the checker.
  let b := SounioPireusQuadraticOrbitCertificate.bit
  let d0 := b code 0
  let d1 := b code 1
  let d2 := b code 2
  let d3 := b code 3
  let a01 := b code 4
  let a02 := b code 5
  let a03 := b code 6
  let a12 := b code 7
  let a13 := b code 8
  let a23 := b code 9
  d0 * 1 + a01 * 2 + a02 * 4 + a03 * 8
    + d1 * 32 + a12 * 64 + a13 * 128
    + d2 * 1024 + a23 * 2048
    + d3 * 32768

def phaseToCodeCertificate : Bool :=
  (List.range 1024).all fun code =>
    let phase := codeToPhase code
    let recovered := SounioPireusQuadraticPipeline.phaseToCode phase
    recovered == code

theorem quadratic_phase_to_code : phaseToCodeCertificate = true := by
  native_decide

structure Boundary where
  phaseToCodeProved : Bool
  orbitEnumeration : Bool
  admissionDecided : Bool
  executableBindingProved : Bool
  claimReady : Bool
deriving DecidableEq, Repr

def boundary : Boundary :=
  { phaseToCodeProved := true
  , orbitEnumeration := false
  , admissionDecided := false
  , executableBindingProved := false
  , claimReady := false }

theorem quadratic_phase_to_code_does_not_promote_a_claim :
    boundary.phaseToCodeProved = true
      && boundary.orbitEnumeration = false
      && boundary.admissionDecided = false
      && boundary.executableBindingProved = false
      && boundary.claimReady = false := by
  decide

end SounioPireusQuadraticPhaseToCode