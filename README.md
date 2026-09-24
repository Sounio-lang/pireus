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
- **Koka**: `EFFECT_PARITY`. Models algebraic effect topologics and phase transitions (*fail-closed*).
- **C++ / PTX**: `MATERIAL_PARITY`. Validates cycle-accurate silicon measurements on targeted microarchitectures (Intel Xeon AVX-512, NVIDIA SM121 Blackwell, Apple Silicon, AMD Alveo U250).
- **LLMs (Inkling / Claude / GPT)**: `PROPOSAL_GENERATOR` & `REVIEW_ONLY`. External models propose candidates (`UntrustedProposal`); they **never** create expected outputs, define equivalence, or promote claims.
- **Python / Rust**: Prohibited as semantic or expected-result oracles.

---

## 2. Directory Layout

- **`ontology/`**: Formal hardware capability descriptions and SPARQL queries over target nodes (`DarwinXeon`, `AppleSilicon`, `DGXSpark`, `AlveoU250`).
- **`engine/`**: Operator morphogenesis, cubic operator forge, bilinear genesis, and native machine code emitters:
  - `admission.sio`: The non-delegable admission boundary for external proposals.
  - `materialize_ptx.sio`: GPU PTX generator for admitted operators supporting bilinear twists.
  - `pireus_xor_materializer.sio`: 1004-byte static assembly artifact for Xeon AVX-512.
- **`continuity/`**: Proposal generation, Slurm batch scheduling, paired canary benchmarking, and the **GRPO Verifiable Reward Engine** (`grpo_reward_engine.py`).
- **`formal/`**: Lean 4 formal obligations and axiom audits (including `SounioPireusMultiProbePartitionV14.lean`).
- **`receipts/`**: Cryptographic formal parity receipts, hardware audits, and benchmark evidence.
- **`scripts/ci/`**: Official gate scripts ensuring semantic boundaries, gate reference ratchets, and tensor invariant preservation.

---

## 3. The Continuous Loop: Milestones M0 through M6

| Milestone | Scope | Status | Acceptance Key |
|---|---|---|---|
| **M0** | Preservation & Lineage | `COMPLETE` | Full lineage, Walsh channel spectrum audited and preserved. |
| **M1** | Compilador & Ontologia | `COMPLETE` | SPARQL ontology queries pass; Lean 4 V13/V14 proofs verified pure. |
| **M2** | Runtime Spark / TP=2 | `PASS_FROZEN_OFFLINE_CANARY` | Slurm jobs on `spark-3c59` & `spark-8e54` with 32 GiB memory envelope. |
| **M3** | Admissão de Propostas | `PASS_REAL_CANARY` | `admission.sio` accepts valid proposals and rejects all invalid/tampered variants. |
| **M4** | Benchmark de Silício | `PASS_CANARY_NO_GAIN` | 16/16 candidate-node paired comparisons PASS (5120 exact component bits). |
| **M5** | Novos Operadores | `IN_PROGRESS` | Multilinear tensor generation in $\mathbb{Z}^{16 \times 16 \times 16}$ & $GL(4,2)$ orbit separation. |
| **M6** | Recompensa GRPO | `IN_PROGRESS` | Deterministic compiler-as-a-reward engine (`grpo_reward_engine.py`) with holdout validation. |

---

## 4. Building & Validating

### Compile the Admission Engine
```sh
souc engine/admission.sio /tmp/pireus_admission.elf
chmod +x /tmp/pireus_admission.elf
python3 continuity/test_admission.py /tmp/pireus_admission.elf
```

### Run GRPO Group-Relative Reward Evaluation
```sh
python3 continuity/grpo_reward_engine.py \
    --admission-bin /tmp/pireus_admission.elf \
    --context continuity/validation/deterministic-live-baseline-20260907/context.json \
    --proposals-dir continuity/validation/deterministic-live-baseline-20260907 \
    --output /tmp/grpo_rewards.json
```

### Verify Lean 4 Parity Proofs
```sh
cd formal/lean4
lake build SounioPireusMultiProbePartitionV14
lake build SounioPireusMultiProbePartitionV14AxiomAudit
```

---

## License

Apache-2.0 licensed. See [LICENSE](LICENSE).  
Authored and maintained within the [Sounio-lang](https://github.com/Sounio-lang) organization.
