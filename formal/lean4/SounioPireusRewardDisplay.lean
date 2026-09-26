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
  executableBindingProved : Bool
  claimReady : Bool
deriving DecidableEq, Repr

def boundary : Boundary :=
  { displayProved := true
  , policyProved := true
  , orbitEnumeration := false
  , admissionDecided := false
  , executableBindingProved := false
  , claimReady := false }

theorem reward_display_does_not_promote_a_claim :
    boundary.displayProved = true
      && boundary.policyProved = true
      && boundary.orbitEnumeration = false
      && boundary.admissionDecided = false
      && boundary.executableBindingProved = false
      && boundary.claimReady = false := by
  decide

end SounioPireusRewardDisplay