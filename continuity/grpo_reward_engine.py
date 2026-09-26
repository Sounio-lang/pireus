#!/usr/bin/env python3
"""
Pireus M6/M8 GRPO reward engine.

admission.sio decides well-formedness. novelty_oracle.sio decides the orbit
class, the training split, and the published novelty scalar in thousandths.
Python converts those thousandths. Group degeneracy is the integer centered
sum of squares from group_variance.sio, not a float variance. Python does not
infer a class, a novelty scalar, or that bit from a phase.
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

def milli_to_reward(milli: int) -> float:
    if milli < 0 or milli > 500:
        raise ValueError(f"NOVELTY_MILLI_OUT_OF_RANGE:{milli}")
    return milli / 1000.0


def novelty_from_classification(receipt: dict) -> dict:
    """Read the scalar the native oracle already chose. Holdout gets no reward."""
    if receipt.get("decision") != "CLASSIFIED":
        return {"novelty_reward": 0.0, "novelty_source": "oracle_refused", "split": None}
    distance = int(receipt["corpus_distance"])
    if distance < 0 or distance > CORPUS_DISTANCE_DENOMINATOR:
        raise ValueError(f"CORPUS_DISTANCE_OUT_OF_RANGE:{distance}")
    novelty = milli_to_reward(int(receipt["novelty_milli"]))
    graded = milli_to_reward(int(receipt["graded_milli"]))
    if int(receipt["holdout"]) == 1:
        if novelty != 0.0:
            raise ValueError("HOLDOUT_TRAINING_REWARD")
        return {
            "novelty_reward": 0.0,
            "held_out_novelty": graded,
            "novelty_source": "holdout_excluded",
            "split": "holdout",
        }
    if int(receipt["train_visited"]) == 1:
        return {"novelty_reward": novelty, "novelty_source": "train_corpus", "split": "train"}
    return {"novelty_reward": novelty, "novelty_source": "unvisited_graded", "split": "train"}

def apply_reward_milli(result: dict, reward_milli: int) -> None:
    """Split one native total. Nothing here chooses the total."""
    if reward_milli < 0 or reward_milli > 1000:
        raise ValueError(f"REWARD_MILLI_OUT_OF_RANGE:{reward_milli}")
    result["reward_milli"] = reward_milli
    result["reward"] = reward_milli / 1000.0
    result["syntax_reward"] = min(reward_milli, 100) / 1000.0
    result["admission_reward"] = min(max(reward_milli - 100, 0), 400) / 1000.0
    result["novelty_reward"] = max(reward_milli - 500, 0) / 1000.0


def compute_proposal_reward(
    admission_bin: Path,
    context_path: Path,
    proposal_path: Path,
    novelty_bin: Path | None = None,
) -> dict:
    """
    Evaluates an untrusted model proposal using Sounio's native admission engine.
    Reward:
      reward_milli is the authority. reward is that integer divided by 1000.
      Admitted kind=2 copies admitted_reward_milli from the oracle. Without the
      oracle its novelty term stays 0. Kind=1 copies reward_milli from the
      admission receipt. A nonzero phase never scores novelty by itself.
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
        if receipt.get("reward_milli") is not None:
            apply_reward_milli(result, int(receipt["reward_milli"]))
        return result

    # Admitted
    result["admitted"] = True
    result["plan_id"] = receipt.get("plan_id")
    result["tensor_sha256"] = receipt.get("tensor_sha256")

    kind = data.get("kind", 1)
    if kind != 2:
        if receipt.get("reward_milli") is None:
            result["reason"] = "LOWERING_REWARD_MISSING"
            return result
        result["novelty_source"] = "unclassified_lowering"
        apply_reward_milli(result, int(receipt["reward_milli"]))
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
    result["novelty_milli"] = int(classification["novelty_milli"])
    result["admitted_reward_milli"] = int(classification["admitted_reward_milli"])
    apply_reward_milli(result, result["admitted_reward_milli"])
    result["class_id"] = classification.get("class_id")
    result["corpus_distance"] = classification.get("corpus_distance")
    result["train_visited"] = classification.get("train_visited")
    return result

def group_statistics(group_bin: Path, reward_millis: list[int]) -> dict:
    """Read the integer population moment. Degeneracy is not a float compare."""
    proc = subprocess.run(
        [str(group_bin), *[str(int(reward)) for reward in reward_millis]],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if not proc.stdout.strip():
        raise RuntimeError(proc.stderr.strip() or "EMPTY_GROUP_VARIANCE_OUTPUT")
    stats = json.loads(proc.stdout)
    if stats.get("decision") != "COMPUTED" or stats.get("claim_ready") is not False:
        raise RuntimeError(f"GROUP_VARIANCE_REFUSED:{stats}")
    deviations = [int(item) for item in stats["centered_deviation"]]
    if (
        int(stats["count"]) != len(reward_millis)
        or int(stats["variance_numerator"]) != int(stats["centered_sum_squares"])
        or len(deviations) != len(reward_millis)
    ):
        raise RuntimeError(f"GROUP_VARIANCE_SHAPE:{stats}")
    stats["centered_deviation"] = deviations
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission-bin", type=Path, required=True, help="Compiled Sounio admission engine ELF")
    parser.add_argument("--novelty-bin", type=Path, help="Compiled Sounio novelty oracle ELF")
    parser.add_argument("--group-bin", type=Path, required=True, help="Compiled Sounio group variance ELF")
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

    try:
        millis = [int(row["reward_milli"]) if "reward_milli" in row else 0 for row in results]
    except (KeyError, TypeError, ValueError):
        print("missing reward_milli", file=sys.stderr)
        sys.exit(1)
    stats = group_statistics(args.group_bin, millis)
    for row, deviation in zip(results, stats["centered_deviation"]):
        row["centered_deviation"] = deviation
    holdout_rows = [row for row in results if row.get("split") == "holdout"]
    output_payload = {
        "schema": "pireus-grpo-reward-batch-v5",
        "holdout_classes": list(HOLDOUT_CLASSES),
        "holdout_count": len(holdout_rows),
        "advantage_numerator": "centered_deviation",
        "std_division": False,
        "advantage_degenerate": bool(stats["degenerate"]),
        "reward_sum": int(stats["reward_sum"]),
        "centered_sum_squares": int(stats["centered_sum_squares"]),
        "variance_denominator": int(stats["variance_denominator"]),
        "evaluator": "Sounio-Native-Admission-Engine",
        "context_file": str(args.context),
        "total_proposals": len(results),
        "admitted_count": sum(1 for row in results if row["admitted"]),
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
