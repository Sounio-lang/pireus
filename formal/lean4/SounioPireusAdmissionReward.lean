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
  { admissionRewardProved := true
  , orbitEnumeration := false
  , admissionDecided := false
  , semanticBindingProved := true
  , byteBindingProved := (releaseElfSha256 == receiptElfSha256)
  , claimReady := false }

theorem admission_reward_does_not_promote_a_claim :
    boundary.admissionRewardProved = true
      && boundary.orbitEnumeration = false
      && boundary.admissionDecided = false
      && boundary.semanticBindingProved = true
      && boundary.byteBindingProved = true
      && boundary.claimReady = false := by
  decide

end SounioPireusAdmissionReward