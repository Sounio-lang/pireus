#!/usr/bin/env python3
"""Unified PIREUS verification: behavioral checks, Lean certificates, axiom audits.

Runs every verification in order. Stops on the first failure. Emits one receipt.
Run on the Sounio workspace with the committed Madaros prebuilt.

Usage:
  python3 verify_all.py \
    --admission-bin /path/to/admission.elf \
    --novelty-bin /path/to/novelty.elf \
    --group-bin /path/to/group_variance.elf \
    --lean-dir /path/to/formal/lean4
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd, label, timeout=600, cwd=None):
    started = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    elapsed = round(time.perf_counter() - started, 3)
    if proc.returncode != 0:
        print(f"FAIL [{label}] rc={proc.returncode}", file=sys.stderr)
        print(proc.stdout[-2000:], file=sys.stderr)
        print(proc.stderr[-2000:], file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS [{label}] {elapsed}s")
    return proc.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission-bin", type=Path, default=None)
    parser.add_argument("--novelty-bin", type=Path, default=None)
    parser.add_argument("--group-bin", type=Path, default=None)
    parser.add_argument("--lean-dir", type=Path, default=None)
    parser.add_argument("--skip-lean", action="store_true",
                        help="Skip Lean certificate builds")
    args = parser.parse_args()

    results = {}
    started = time.perf_counter()
    import os
    have_elfs = bool(args.admission_bin and args.novelty_bin and args.group_bin)

    if args.novelty_bin:
        os.environ["PIREUS_NOVELTY_ORACLE"] = str(args.novelty_bin)
    if args.group_bin:
        os.environ["PIREUS_GROUP_VARIANCE"] = str(args.group_bin)

    # 1. Python unit tests (no ELF required)
    run([sys.executable, str(HERE / "test_grpo_novelty.py")], "python-unit-tests")

    if have_elfs:
        # 2. Admission tests (38 cases)
        run([sys.executable, str(HERE / "test_admission.py"), str(args.admission_bin)],
            "admission-tests")

        # 3. Oracle executable check (1024 codes)
        out = run([sys.executable, str(HERE / "check_oracle_executable.py"),
                   "--oracle", str(args.novelty_bin),
                   "--source", str(HERE / "novelty_oracle.sio")],
                  "oracle-1024-codes")
        results["oracle_1024"] = json.loads(out)

        # 4. Semantic binding (1024 codes, 9 fields)
        out = run([sys.executable, str(HERE / "check_semantic_binding.py"),
                   "--oracle", str(args.novelty_bin),
                   "--source", str(HERE / "novelty_oracle.sio")],
                  "semantic-binding-1024-codes")
        results["semantic_binding"] = json.loads(out)

        # 5. Group variance vectors (10 vectors)
        out = run([sys.executable, str(HERE / "check_group_variance.py"),
                   "--oracle", str(args.group_bin)],
                  "group-variance-10-vectors")
        results["group_variance"] = json.loads(out)

        # 6. Eight-proposal batch
        out = run([sys.executable, str(HERE / "build_m8_batch.py"),
                   "--admission-bin", str(args.admission_bin),
                   "--novelty-bin", str(args.novelty_bin),
                   "--group-bin", str(args.group_bin),
                   "--work-dir", "/tmp/pireus-verify-all"],
                  "m8-batch")
        batch = json.loads(out)
        results["m8_batch"] = {
            "reward_sum": batch["reward_sum"],
            "centered_sum_squares": batch["centered_sum_squares"],
            "variance_denominator": batch["variance_denominator"],
            "advantage_degenerate": batch["advantage_degenerate"],
            "holdout_count": batch["holdout_count"],
            "admitted_count": batch["admitted_count"],
        }

        # 7. Exhaustive 65536-phase check (needs numpy for the explorer)
        try:
            import numpy  # noqa: F401
            out = run([sys.executable, str(HERE / "check_novelty_oracle.py"),
                       "--oracle", str(args.novelty_bin)],
                      "oracle-65536-phases", timeout=600)
            # The explorer prints progress before the JSON. Extract the last JSON object.
            json_start = out.rfind("{\n")
            if json_start < 0:
                json_start = out.rfind("{")
            results["oracle_65536"] = json.loads(out[json_start:])
        except ImportError:
            results["oracle_65536"] = "skipped_no_numpy"
    else:
        results["elf_checks"] = "skipped_no_binaries"

    # 8. Lean certificates
    if not args.skip_lean and args.lean_dir:
        lean_targets = [
            "SounioPireusQuadraticOrbitCertificate",
            "SounioPireusQuadraticOrbitCertificateAxiomAudit",
            "SounioPireusQuadraticNoveltyScalar",
            "SounioPireusQuadraticNoveltyScalarAxiomAudit",
            "SounioPireusQuadraticGroupMoment",
            "SounioPireusQuadraticGroupMomentAxiomAudit",
            "SounioPireusQuadraticGroupMomentConsistency",
            "SounioPireusQuadraticGroupMomentConsistencyAxiomAudit",
            "SounioPireusQuadraticPipeline",
            "SounioPireusQuadraticPipelineAxiomAudit",
            "SounioPireusQuadraticPhaseToCode",
            "SounioPireusQuadraticPhaseToCodeAxiomAudit",
            "SounioPireusAdmissionReward",
            "SounioPireusAdmissionRewardAxiomAudit",
            "SounioPireusRewardDisplay",
            "SounioPireusRewardDisplayAxiomAudit",
        ]
        out = run(["lake", "build", *lean_targets],
                  "lean-certificates", timeout=1800, cwd=args.lean_dir)
        results["lean"] = {
            "targets": len(lean_targets),
            "toolchain": "leanprover/lean4:v4.33.0",
        }

    elapsed = round(time.perf_counter() - started, 3)
    receipt = {
        "schema": "pireus-verify-all-v2",
        "status": "PASS",
        "claim_ready": False,
        "elapsed_seconds": elapsed,
        "elf_checks": "ran" if have_elfs else "skipped",
        "lean_checks": "ran" if (not args.skip_lean and args.lean_dir) else "skipped",
        "results": results,
    }
    if have_elfs:
        receipt["admission_elf_sha256"] = sha256(args.admission_bin)
        receipt["novelty_elf_sha256"] = sha256(args.novelty_bin)
        receipt["group_elf_sha256"] = sha256(args.group_bin)
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
