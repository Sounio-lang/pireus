# PIREUS (Πειραιεύς)

**Autonomous Operator Foundry, Hardware Capability Ontology, and Verifiable Reinforcement Learning Compiler Framework for Sounio.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Authority](https://img.shields.io/badge/Semantic_Authority-Sounio_Native-emerald.svg)](https://github.com/Sounio-lang/sounio)
[![Parity](https://img.shields.io/badge/Formal_Parity-Lean_4.33-purple.svg)](formal/lean4)

---

## 1. Vision & Architectural Charter

**PIREUS** is the mathematical foundry and second-order compiler engine for the Sounio ecosystem. It operates where non-associative hypercomplex algebra, silicon microarchitecture ontologies, formal proof systems, and group-relative reinforcement learning meet.

### The Immutable Authority Hierarchy
Across all contracts (V0 through V14) and execution pipelines, PIREUS strictly enforces non-delegable semantic authority:

$$\text{GARDEN} \longrightarrow \text{SOUNIO\_EXECUTABLE} \longrightarrow \text{SEMANTICS\_FROZEN} \longrightarrow \text{PARITY\_OPEN} \longrightarrow \text{CLAIM\_READY}$$

- **Sounio Executable**: Sole `SEMANTIC_AUTHORITY`. Generates algebra tensors, checks well-formedness, defines canonical equivalence classes, and makes admission decisions (`admission.sio`).
- **Lean 4**: `FORMAL_PARITY`. Formally proves gauge-coboundary rebase invariants, quotient group actions under $GL(4,2) \times C_2$, and exact partition coverings without `sorry`.
- **Koka**: declared as an `EFFECT_PARITY` role in the charter. This extraction contains no `.kk` sources, so that role is not instantiated here.
- **C++ / PTX**: `MATERIAL_PARITY`. The repository contains lowering and probe sources for Intel Xeon AVX-512, NVIDIA SM121, Apple Silicon, and AMD Alveo U250. A probe source is not a recorded hardware run.
- **LLMs (Inkling / Claude / GPT)**: `PROPOSAL_GENERATOR` & `REVIEW_ONLY`. External models propose candidates (`UntrustedProposal`); they **never** create expected outputs, define equivalence, or promote claims.
- **Python / Rust**: Prohibited as semantic or expected-result oracles.

---

## 2. Directory Layout

- **`ontology/`**: Formal hardware capability descriptions and SPARQL queries over target nodes (`DarwinXeon`, `AppleSilicon`, `DGXSpark`, `AlveoU250`).
- **`engine/`**: Operator morphogenesis, cubic operator forge, bilinear genesis, and target-specific material probes, including `pireus_xor_materializer.sio`.
- **`continuity/`**: The admission boundary (`admission.sio`), the SM121 PTX emitter (`materialize_ptx.sio`), proposal custody, paired benchmarking, and the **GRPO reward engine** (`grpo_reward_engine.py`).
- **`formal/lean4/`**: Lean 4 parity obligations and axiom audits. `lakefile.lean` declares the PIREUS libraries and the imported `SounioCDCocycle` module. Historical receipts under `receipts/` bind earlier monorepo builds; they do not hash this standalone lakefile.
- **`receipts/`**: Cryptographic formal parity receipts, hardware audits, and benchmark evidence.
- **`scripts/ci/`**: Official gate scripts ensuring semantic boundaries, gate reference ratchets, and tensor invariant preservation.

---

## 3. Milestones

`status.json` is a frozen monorepo ledger from 2026-09-10. It predates this extraction and is not the status of the tagged releases. The artifact-backed status is:

| Milestone | Status in this repository | What is actually present |
|---|---|---|
| **M0–M4** | Recorded in the frozen ledger | The operational evidence named by `status.json` lives in the Sounio monorepo, not in this extraction. |
| **M5** | Artifact present, tag `v1.1.0` | `continuity/atlas_m5/`: 16 admitted proposals, 16 distinct tensor hashes, 16 static SM121 PTX sources. Recorded mean reward is **0.975** (15×1.0 and one 0.6). |
| **M6/M8** | Reward engine present | The reward authority is the Sounio executable. `admission.sio` admits or refuses proposals. An admitted `kind=1` receipt carries `reward_milli: 800`. A parsed semantic refusal carries `reward_milli: 100`. A parse failure carries no reward. `novelty_oracle.sio` classifies one phase against the frozen M5/M7 partition and emits `reward_milli` for an admitted `kind=2` proposal (`500 + novelty_milli`). `grpo_reward_engine.py` reads `reward_milli` from each receipt, divides by 1000 for display, and delegates degeneracy to `group_variance.sio`. Python does not choose reward values, compute standard deviation, or emit component splits. `formal/lean4/SounioPireusQuadraticOrbitCertificate.lean` discharges the 20160/336/32 census and binds all 1024 class literals. `formal/lean4/SounioPireusQuadraticNoveltyScalar.lean` checks the novelty scalar and `500 + novelty_milli` for every class. Both axiom audits retain `Lean.ofReduceBool`. `formal/lean4/SounioPireusQuadraticGroupMoment.lean` verifies the eight reward thousandths, their signed deviations, and the centered sum of squares against the published literals. Its axiom audit retains `Lean.ofReduceBool`. `formal/lean4/SounioPireusQuadraticPhaseToCode.lean` verifies the roundtrip `phaseToCode (codeToPhase code) == code` for all 1024 codes, binding the Lean phase-to-code map to the Sounio `quadratic_code` semantics. `formal/lean4/SounioPireusQuadraticPipeline.lean` closes the chain: phase to quadratic code to class to reward to group moment, all eight published phases producing the published rewards from the frozen tables alone. `formal/lean4/SounioPireusQuadraticGroupMomentConsistency.lean` checks that the eight reward thousandths are consequences of the frozen oracle tables through `admittedRewardMilli`, not free literals. Exhaustive receipts cover 65,536 phases against the explorer partition, the committed-compiler ELF, and the behavioral binding of `class_id`. `claim_ready` remains false throughout. |
| **M7** | Computational artifacts present, tag `v1.2.0` | `continuity/atlas_m7/`: 65,536-matrix census, 32 orbit-class records, 20 classes marked unvisited relative to the encoded M5 phases, 16 selected proposals, 16 static SM121 PTX sources. Recorded mean reward is **1.0**. |

PTX files are emitted source artifacts. This repository does not archive CUDA module-load, kernel-launch, device-identity, or numerical-output receipts for the M5 or M7 batches, so those batches are not hardware-execution evidence.

The M7 reward is degenerate as a group-relative signal: candidates are prefiltered to unvisited classes and the novelty term is the constant 0.5, so every reward is 1.0, the standard deviation is 0, and every advantage is 0. The M5 batch is the non-degenerate example.

---

## 4. Building & Validating

The `.sio` sources import the Sounio compiler and standard library. Neither is vendored here. Build them with the `souc` that matches the Sounio commit you intend to treat as semantic authority; this repository does not pin that compiler by itself.

```sh
souc continuity/admission.sio /tmp/pireus_admission.elf
chmod +x /tmp/pireus_admission.elf
python3 continuity/test_admission.py /tmp/pireus_admission.elf
```

GRPO evaluation needs that executable plus a context and a proposal directory. The historical path `continuity/validation/deterministic-live-baseline-20260907/` was not extracted. The checked-in atlas batches are result artifacts, not a self-contained rerun fixture.

### Lean 4

```sh
cd formal/lean4
lake build SounioPireusMultiProbePartitionV14
lake build SounioPireusMultiProbePartitionV14AxiomAudit
```

`lake build` without a target builds every declared PIREUS library. Several parity files use `native_decide`, so a full build is a finite-computation check, not a small structural proof. Axiom audits record that `native_decide` is outside the kernel-axiom-free claim.

## 5. Citation

There is no PIREUS DOI yet. `CITATION.cff` is the citation metadata. `.zenodo.json` relates this repository to the Sounio repository by URL. It does not reuse a Sounio Zenodo record as a PIREUS DOI. A DOI is added only after a PIREUS deposit is actually published.

---

## License

Apache-2.0 licensed. See [LICENSE](LICENSE).  
Authored and maintained within the [Sounio-lang](https://github.com/Sounio-lang) organization.
