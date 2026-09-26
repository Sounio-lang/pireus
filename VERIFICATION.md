# PIREUS Verification Chain

One page. What is proved, what is executed, what is missing.

## What Lean proves

Eight theorems, all `native_decide`, all with axiom audits.

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
- Behavioral equivalence, not byte storage

## What is missing for claim_ready

`byteBindingProved` is false. The class table is not stored as a contiguous literal in the ELF — the Madaros compiler generates runtime initialization. Byte inspection cannot close this gap.

`claim_ready` requires either:
1. A compiler change that stores the table as a literal, or
2. A redefinition of `claim_ready` to mean semantic binding, or
3. Acceptance that `claim_ready` stays false

Currently: option 3. `semanticBindingProved = true`, `byteBindingProved = false`, `claim_ready = false`.

## How to run everything

### On the Sounio workspace (full verification)

```bash
bash continuity/run_verification.sh /tmp/pireus-verification /tmp/pireus-scalar-lean
```

Compiles all 3 ELFs from source, runs 8 behavioral checks (including 65,536 phases), and 16 Lean targets. ~2 minutes after Lean cache is warm.

### On GitHub CI (Python + Lean)

`.github/workflows/verify.yml` runs on every push. Python tests + 16 Lean targets. No ELFs (no Madaros on GitHub). Lean cache avoids the 25-minute orbit rebuild.

### Daily cron on the workspace

`/etc/cron.d/pireus-verify` runs `run_verification.sh` at 06:00. Log: `/tmp/pireus-verification.log`.

## Verification checklist

| Check | What it covers | Where it runs |
|---|---|---|
| Python unit tests | Reward map, component split, integer moment | CI + workspace |
| Admission tests (38) | Parse, semantic refusal, lowering reward, operator | Workspace |
| Oracle 1024 codes | `class_id` matches source table | Workspace |
| Semantic binding 1024 codes | All 9 fields match Lean spec | Workspace |
| Group variance 10 vectors | Degenerate, extremes, mixed fragments | Workspace |
| M8 batch (8 proposals) | Reward sum 5199, deviations, holdout | Workspace |
| Oracle 65,536 phases | Every phase matches explorer partition | Workspace |
| Lean 16 targets | 8 theorems + 8 axiom audits | CI + workspace |

## Receipts

Every check emits a receipt in `receipts/`. The unified receipt is `receipts/verify_all.v2`. Individual receipts cover each check with ELF hashes, source hashes, and compiler identity.
