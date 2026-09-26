#!/usr/bin/env python3
"""
Pireus M6/M8 GRPO reward engine.

admission.sio decides well-formedness. novelty_oracle.sio decides the orbit
class, whether that class belongs to the frozen M5 training corpus, whether
it is in the fixed holdout, and its integer distance to the Cayley-Dickson
class. Python applies only the published scalar map below. It does not infer
a class from a nonzero phase.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS_DISTANCE_DENOMINATOR = 130
HOLDOUT_CLASSES = (1, 2, 11, 23)

def classify_phase(novelty_bin: Path, phase: int) -> dict:
    proc = subprocess.run(
        [str(novelty_bin), str(int(phase))],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if not proc.stdout.strip():
        raise RuntimeError(proc.stderr.strip() or "EMPTY_NOVELTY_OUTPUT")
    return json.loads(proc.stdout)

def novelty_from_classification(receipt: dict) -> dict:
    """Map one oracle receipt to the published scalar. Holdout gets no reward."""
    if receipt.get("decision") != "CLASSIFIED":
        return {"novelty_reward": 0.0, "novelty_source": "oracle_refused", "split": None}
    distance = int(receipt["corpus_distance"])
    if distance < 0 or distance > CORPUS_DISTANCE_DENOMINATOR:
        raise ValueError(f"CORPUS_DISTANCE_OUT_OF_RANGE:{distance}")
    graded = 0.2 + 0.3 * (distance / CORPUS_DISTANCE_DENOMINATOR)
    if int(receipt["holdout"]) == 1:
        return {
            "novelty_reward": 0.0,
            "held_out_novelty": graded,
            "novelty_source": "holdout_excluded",
            "split": "holdout",
        }
    if int(receipt["train_visited"]) == 1:
        return {
            "novelty_reward": 0.1 if distance == 0 else 0.15,
            "novelty_source": "train_corpus",
            "split": "train",
        }
    return {"novelty_reward": graded, "novelty_source": "unvisited_graded", "split": "train"}

def compute_proposal_reward(
    admission_bin: Path,
    context_path: Path,
    proposal_path: Path,
    novelty_bin: Path | None = None,
) -> dict:
    """
    Evaluates an untrusted model proposal using Sounio's native admission engine.
    Reward:
      syntax 0.1, native admission 0.4, and novelty from novelty_from_classification.
      A kind=2 proposal without the oracle scores novelty 0. It never scores 0.5
      merely because its phase is nonzero. Kind=1 remains a fixed 0.3 lowering
      term and is labeled unclassified.
    """
    result = {
        "proposal": str(proposal_path),
        "reward": 0.0,
        "syntax_reward": 0.0,
        "admission_reward": 0.0,
        "novelty_reward": 0.0,
        "admitted": False,
        "decision": "REFUSE",
        "reason": None,
        "plan_id": None,
        "tensor_sha256": None,
    }

    if not proposal_path.exists():
        result["reason"] = "PROPOSAL_MISSING"
        return result

    try:
        raw_proposal = proposal_path.read_text(encoding="utf-8")
        data = json.loads(raw_proposal)
    except Exception as e:
        result["reason"] = f"JSON_DECODE_ERROR: {str(e)}"
        return result

    # Check syntax structure
    if not isinstance(data, dict):
        result["reason"] = "MALFORMED_ROOT_OBJECT"
        return result

    result["syntax_reward"] = 0.1
    result["reward"] += 0.1

    # Run native Sounio admission engine
    try:
        proc = subprocess.run(
            [str(admission_bin), str(context_path), str(proposal_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        result["reason"] = "ADMISSION_TIMEOUT"
        return result
    except Exception as e:
        result["reason"] = f"EXECUTION_FAILED: {str(e)}"
        return result

    output = proc.stdout.strip()
    if not output:
        result["reason"] = f"EMPTY_ADMISSION_OUTPUT (stderr: {proc.stderr.strip()})"
        return result

    try:
        receipt = json.loads(output)
    except Exception as e:
        result["reason"] = f"RECEIPT_PARSE_ERROR: {output}"
        return result

    decision = receipt.get("decision")
    result["decision"] = decision
    if decision != "ADMIT":
        result["reason"] = receipt.get("reason", "REFUSED")
        return result

    # Admitted
    result["admitted"] = True
    result["admission_reward"] = 0.4
    result["reward"] += 0.4
    result["plan_id"] = receipt.get("plan_id")
    result["tensor_sha256"] = receipt.get("tensor_sha256")

    kind = data.get("kind", 1)
    if kind != 2:
        result["novelty_reward"] = 0.3
        result["novelty_source"] = "unclassified_lowering"
        result["reward"] += 0.3
        return result

    if novelty_bin is None:
        result["reason"] = "NOVELTY_ORACLE_MISSING"
        result["novelty_source"] = "missing_oracle"
        return result
    try:
        classification = classify_phase(novelty_bin, int(data.get("phase", -1)))
    except Exception as exc:
        result["reason"] = f"NOVELTY_ORACLE_FAILED: {exc}"
        result["novelty_source"] = "oracle_failed"
        return result
    graded = novelty_from_classification(classification)
    result.update(graded)
    result["novelty_reward"] = graded["novelty_reward"]
    result["reward"] += graded["novelty_reward"]
    result["class_id"] = classification.get("class_id")
    result["corpus_distance"] = classification.get("corpus_distance")
    result["train_visited"] = classification.get("train_visited")
    return result

def evaluate_group_relative_advantages(group_results: list, epsilon: float = 1e-8) -> list:
    """
    Computes GRPO relative advantages A_i across the group of sampled conclusions.
    A_i = (R_i - mean(R)) / (std(R) + epsilon)
    """
    rewards = [r["reward"] for r in group_results]
    mean_r = sum(rewards) / len(rewards) if rewards else 0.0
    var_r = sum((r - mean_r) ** 2 for r in rewards) / len(rewards) if len(rewards) > 1 else 0.0
    std_r = var_r ** 0.5

    for r in group_results:
        r["advantage"] = (r["reward"] - mean_r) / (std_r + epsilon) if std_r > 0 else 0.0

    return group_results

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission-bin", type=Path, required=True, help="Compiled Sounio admission engine ELF")
    parser.add_argument("--novelty-bin", type=Path, help="Compiled Sounio novelty oracle ELF")
    parser.add_argument("--context", type=Path, required=True, help="Research context JSON")
    parser.add_argument("--proposals-dir", type=Path, required=True, help="Directory containing .proposal.json files")
    parser.add_argument("--output", type=Path, help="Output JSON results")
    args = parser.parse_args()

    proposal_files = sorted(args.proposals_dir.glob("*.proposal.json"))
    if not proposal_files:
        print(f"No proposals found in {args.proposals_dir}", file=sys.stderr)
        sys.exit(1)

    results = []
    for p in proposal_files:
        res = compute_proposal_reward(args.admission_bin, args.context, p, args.novelty_bin)
        results.append(res)

    results = evaluate_group_relative_advantages(results)

    rewards = [r["reward"] for r in results]
    mean_r = sum(rewards) / len(rewards) if rewards else 0.0
    variance = sum((r - mean_r) ** 2 for r in rewards) / len(rewards) if len(rewards) > 1 else 0.0
    holdout_rows = [r for r in results if r.get("split") == "holdout"]
    output_payload = {
        "schema": "pireus-grpo-reward-batch-v2",
        "holdout_classes": list(HOLDOUT_CLASSES),
        "holdout_count": len(holdout_rows),
        "advantage_degenerate": variance == 0.0,
        "evaluator": "Sounio-Native-Admission-Engine",
        "context_file": str(args.context),
        "total_proposals": len(results),
        "admitted_count": sum(1 for r in results if r["admitted"]),
        "mean_reward": sum(r["reward"] for r in results) / len(results) if results else 0.0,
        "evaluations": results,
    }

    json_str = json.dumps(output_payload, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_str + "\n", encoding="utf-8")
        print(f"GRPO rewards written to {args.output}")
    else:
        print(json_str)

if __name__ == "__main__":
    main()
