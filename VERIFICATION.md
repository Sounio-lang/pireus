# PIREUS Verification Chain

One page. What is proved, what is executed, what is missing.

## What Lean proves

Eight main theorems, all `native_decide`. Each boundary also carries `byte_binding_receipt` (`decide`): the equality of the published `novelty.elf` sha256 with the receipt hash. All with axiom audits.

| Theorem | What it proves | Build time |
|---|---|---|
| `quadratic_orbit_certificate` | 20160 ordered bases, 336 admitted actions, 32 orbit classes, all 1024 class literals | 1515s |
| `quadratic_novelty_scalar` | `novelty_milli`, `graded_milli`, `admitted_reward_milli` for all 32 classes and 1024 codes | <1s |
| `quadratic_group_moment` | 8 rewards, signed deviations, centered sum of squares 19481656 | <1s |
| `quadratic_group_moment_consistency` | The 8 rewards are consequences of the frozen oracle tables | 1s |
| `quadratic_pipeline_certificate` | phase → code → class → reward → moment for 8 published phases | 1s |
| `quadratic_phase_to_code` | `phaseToCode (codeToPhase code) == code` for all 1024 codes | 5s |
| `admission_reward_constants` | 800 for kind=1, 100 for semantic refusal | <1s |
| `reward_display_certificate` | `reward = reward_milli / 1000`, `std_division: false` | <1s |

Axiom audits: `propext`, `Quot.sound`, `Lean.ofReduceBool`. The boundary theorems depend on no axioms.

## What the ELF executes

Three binaries, compiled from Sounio source by the committed Madaros prebuilt.

| Binary | Source | Role |
|---|---|---|
| `admission.elf` | `continuity/admission.sio` | Admits or refuses proposals. Emits `reward_milli`. |
| `novelty.elf` | `continuity/novelty_oracle.sio` | Classifies one phase. Emits `reward_milli` for admitted kind=2. |
| `group_variance.elf` | `continuity/group_variance.sio` | Computes the integer population moment. |

## What semantic binding shows

`continuity/check_semantic_binding.py` runs the oracle on one phase per quadratic code and compares all 9 output fields against the Lean frozen tables and formulas.

- 1024 codes checked
- 9 fields: `class_id`, `train_visited`, `holdout`, `commutator_defect`, `square_negative_count`, `corpus_distance`, `novelty_milli`, `graded_milli`, `admitted_reward_milli`
- 0 mismatches
- Includes a byte-storage probe: flipping the one table qword the phase reads changes the answer; flipping a control qword does not

## What byte binding shows

`byteBindingProved` is true. The Madaros const-array image feature stores the 1024-entry class table as a read-only image inside `novelty.elf`, and `continuity/check_byte_corruption.py` proves the classifier reads it:

- BINDING: +1 on the slot the phase reads changes the answer
- CONTROL: +1 on a slot the phase does not read leaves the answer identical
- CLASS_RANGE: forcing class 99 into the read slot is refused, no out-of-bounds class leaks

Each Lean boundary pins the published `novelty.elf` sha256 against `receipts/elf_byte_binding.probe` (`byte_binding_receipt`, closed by `decide`).

## What is missing for claim_ready

Orbit enumeration and the admission decision. `orbitEnumeration = false` and `admissionDecided = false` in every boundary; `claim_ready = false` until they are earned. Receipt: `receipts/elf_byte_binding.probe` (`next_step=orbit_enumeration`).

## How to run everything

### On the Sounio workspace (full verification)

```bash
bash continuity/run_verification.sh /tmp/pireus-verification /tmp/pireus-scalar-lean
```

Compiles all 3 ELFs from source, runs 8 behavioral checks (including 65,536 phases), and 16 Lean targets. ~2 minutes after Lean cache is warm.

### On GitHub CI (Python + Lean)

`.github/workflows/verify.yml` runs on every push. Python tests + the release ELFs (downloaded from `pireus-elfs-v1`, no Madaros on GitHub) + 16 Lean targets. Lean cache avoids the 25-minute orbit rebuild.

### Daily cron on the workspace

`/etc/cron.d/pireus-verify` runs `run_verification.sh` at 06:00. Log: `/tmp/pireus-verification.log`.

## Verification checklist

| Check | What it covers | Where it runs |
|---|---|---|
| Python unit tests | Reward map, component split, integer moment | CI + workspace |
| Admission tests (38) | Parse, semantic refusal, lowering reward, operator | Workspace |
| Oracle 1024 codes | `class_id` matches source table | Workspace |
| Semantic binding 1024 codes | All 9 fields match Lean spec | Workspace |
| Byte corruption triple | Read slot flip changes answer; control does not; class 99 refused | CI + workspace |
| Group variance 10 vectors | Degenerate, extremes, mixed fragments | Workspace |
| M8 batch (8 proposals) | Reward sum 5199, deviations, holdout | Workspace |
| Oracle 65,536 phases | Every phase matches explorer partition | Workspace |
| Lean 16 targets | 8 theorems + 8 axiom audits | CI + workspace |

## Receipts

Every check emits a receipt in `receipts/`. The unified receipt is `receipts/verify_all.v2`. Individual receipts cover each check with ELF hashes, source hashes, and compiler identity.
