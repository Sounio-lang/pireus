/-
  Admission reward constants from `continuity/admission.sio`.

  A parsed semantic refusal carries `reward_milli: 100`. An admitted
  kind=1 (lowering) proposal carries `reward_milli: 800`. A parse failure
  carries no reward. These are the only reward values decided outside
  the novelty oracle. This does not classify a phase, enumerate orbits,
  observe the ELF, or promote `claimReady`.
-/
namespace SounioPireusAdmissionReward

set_option maxHeartbeats 0

def semanticRefusalRewardMilli : Nat := 100

def loweringRewardMilli : Nat := 800

def syntaxThousandths : Nat := 100

def admissionThousandths : Nat := 400

def loweringUnclatteredTerm : Nat := 300

def admissionRewardCertificate : Bool :=
  semanticRefusalRewardMilli == 100
    && loweringRewardMilli == syntaxThousandths + admissionThousandths + loweringUnclatteredTerm
    && loweringRewardMilli == 800
    && syntaxThousandths == 100
    && admissionThousandths == 400
    && loweringUnclatteredTerm == 300

theorem admission_reward_constants : admissionRewardCertificate = true := by
  native_decide

structure Boundary where
  admissionRewardProved : Bool
  orbitEnumeration : Bool
  admissionDecided : Bool
  executableBindingProved : Bool
  claimReady : Bool
deriving DecidableEq, Repr

def boundary : Boundary :=
  { admissionRewardProved := true
  , orbitEnumeration := false
  , admissionDecided := false
  , executableBindingProved := false
  , claimReady := false }

theorem admission_reward_does_not_promote_a_claim :
    boundary.admissionRewardProved = true
      && boundary.orbitEnumeration = false
      && boundary.admissionDecided = false
      && boundary.executableBindingProved = false
      && boundary.claimReady = false := by
  decide

end SounioPireusAdmissionReward