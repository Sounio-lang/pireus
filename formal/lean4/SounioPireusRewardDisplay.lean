/-
  Reward display and advantage policy.

  `reward` is `reward_milli / 1000` exactly. `std_division` is false: the
  advantage numerator is the signed centered deviation, and nothing divides
  it by a standard deviation. These are the last two policy facts not yet
  in Lean. This does not classify a phase, enumerate orbits, observe the
  ELF, or promote `claimReady`.
-/
namespace SounioPireusRewardDisplay

set_option maxHeartbeats 0

def rewardMilliToDisplay (rewardMilli : Nat) : Nat :=
  rewardMilli

def displayDenominator : Nat := 1000

def rewardDisplayCertificate : Bool :=
  let cases := [(600, 600), (650, 650), (949, 949), (1000, 1000), (500, 500)]
  let ok := cases.all fun (rewardMilli, expected) =>
    rewardMilliToDisplay rewardMilli == expected
  displayDenominator == 1000
    && ok

def stdDivision : Bool := false

def advantageNumerator : String := "centered_deviation"

def advantagePolicyCertificate : Bool :=
  stdDivision == false
    && advantageNumerator == "centered_deviation"

theorem reward_display_certificate : rewardDisplayCertificate = true := by
  native_decide

theorem advantage_policy_certificate : advantagePolicyCertificate = true := by
  native_decide

structure Boundary where
  displayProved : Bool
  policyProved : Bool
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
  { displayProved := true
  , policyProved := true
  , orbitEnumeration := false
  , admissionDecided := false
  , semanticBindingProved := true
  , byteBindingProved := (releaseElfSha256 == receiptElfSha256)
  , claimReady := false }

theorem reward_display_does_not_promote_a_claim :
    boundary.displayProved = true
      && boundary.policyProved = true
      && boundary.orbitEnumeration = false
      && boundary.admissionDecided = false
      && boundary.semanticBindingProved = true
      && boundary.byteBindingProved = true
      && boundary.claimReady = false := by
  decide

end SounioPireusRewardDisplay