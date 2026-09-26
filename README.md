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
| **M6/M8** | Reward engine present | `continuity/grpo_reward_engine.py` takes syntax and admission from `admission.sio`. For `kind=2`, novelty comes from `continuity/novelty_oracle.sio`: frozen class, M5 membership, holdout classes 1/2/11/23, and integer corpus distance. `receipts/m8_novelty_oracle.exhaustive` records two checks: all 65,536 phases against the explorer partition, and all 1,024 embedded class entries against a third implementation that imports no PIREUS code. Both had 0 mismatches. `formal/lean4/SounioPireusQuadraticOrbitCertificate.lean` discharges the same 20160/336/32 census inside Lean and checks all 1024 source-table entries from `novelty_oracle.sio`. The axiom audit retains `Lean.ofReduceBool`. The Lean check binds that source literal, not the compiled ELF. `continuity/check_oracle_executable.py` then ran one phase from each of the 1024 fibres through the committed-compiler `novelty.elf` (`2fc7909e0820dee6d35f9268b2d8aa836dcc45095262cf91c6811de27411becc`) and matched every `class_id`, with `claim_ready` false. That run is behavioral equality. It does not show that the binary stores the table, and `executableBindingProved` stays false. The same oracle now emits the novelty scalar as `novelty_milli`. `formal/lean4/SounioPireusQuadraticNoveltyScalar.lean` checks the same thousandths for all 1024 source-table classes. It reads the class literal and the frozen commutator, square, visited, and holdout tables, and checks `500 + novelty_milli` for every class. It does not recompute a commutator, admit a proposal, or bind the ELF. Its axiom audit retains `Lean.ofReduceBool`. `receipts/m8_novelty_oracle_milli.exhaustive` reruns all 65,536 phases against that ELF (`0296f02319c1d8b97ed3ecfe041dd3f3af4bf52aea34890f60b18438d513c980`) and matches `novelty_milli` and `graded_milli`, with 0 mismatches. It does not replace the earlier exhaustive receipt. `receipts/m8_grpo_batch_native_milli.json` is the eight-proposal batch read from that field. `continuity/group_variance.sio` then takes those eight rewards in thousandths and returns the integer population moment: sum 5199, centered sum of squares 19481656, denominator 512, not degenerate. `receipts/m8_grpo_batch_group_variance.json` records that bit. Float variance is not the degeneracy decision. The same executable now also returns the signed centered deviation of each reward. For this batch the eight numerators are `-399`, `1`, `2393`, `2801`, and `-1199` four times. `receipts/m8_grpo_batch_centered_deviation.json` records them. Nothing divides those numerators by a standard deviation. `grpo_reward_engine.py` requires `group_variance.sio` for the same bit and no longer computes a float standard deviation. For an admitted `kind=2` proposal, `reward_milli` is copied from the oracle field `admitted_reward_milli`, which is `500 + novelty_milli`. The displayed `reward` is that integer divided by 1000. Python does not add the syntax, admission, and novelty floats. A `kind=1` admission receipt now carries `reward_milli: 800`; the engine copies it and does not invent that constant. A parsed semantic refusal carries `reward_milli: 100`. A parse failure carries no reward. The engine no longer writes `100` before admission returns, so an unparsed proposal stays at reward `0` and has no `reward_milli`. The operator receipt has no reward field. `receipts/m8_novelty_oracle_admitted_reward.exhaustive` matches that field on all 65,536 phases of ELF `63007d26532facb04ba93b8e956c616eb0b0256f4d908ba2197f068884c3e1d4`. The oracle does not admit the proposal. It does not replace `receipts/m8_grpo_batch.json`: exact fractions such as `0.449230...` become `0.449` under floor division by 130. `receipts/m8_grpo_batch.json` is one eight-proposal batch admitted and classified by those native executables: visited rewards stay below 1.0, holdout novelty is excluded, and the reward variance is nonzero. The same sources, compiled under `SOUNIO_REQUIRE_COMMITTED_MADAROS=1` with the committed prebuilt `bin/madaros-linux-x86_64`, produced byte-identical executables and the same rewards. That prebuilt is not a from-source build of the working tree. None of these checks promotes `claim_ready`. |
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
