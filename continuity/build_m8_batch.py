#!/usr/bin/env python3
"""Build one M8 reward batch from the native admission and novelty executables.

The historical M5 and M7 atlas files are not inputs and are not rewritten.
Degeneracy comes from group_variance.sio. Float variance is not consulted.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import grpo_reward_engine as engine

CONTEXT = {
    "schema": 1,
    "target": 701202,
    "dimension": 16,
    "precision": 64,
    "order": 1,
    "fma": 0,
    "capabilities": 55,
    "lane_width": 32,
    "facts_state": 1,
}
CASES = (
    (0, "visited_corpus"),
    (1128, "visited_nonzero_phase"),
    (35, "unvisited"),
    (32841, "unvisited"),
    (1, "holdout"),
    (32768, "holdout"),
    (9, "holdout"),
    (32812, "holdout"),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission-bin", type=Path, required=True)
    parser.add_argument("--novelty-bin", type=Path, required=True)
    parser.add_argument("--group-bin", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    work = args.work_dir
    proposals = work / "proposals"
    proposals.mkdir(parents=True, exist_ok=True)
    context_bytes = (json.dumps(CONTEXT, separators=(",", ":")) + "\n").encode()
    context_path = work / "context.json"
    context_path.write_bytes(context_bytes)
    context_hash = hashlib.sha256(context_bytes).hexdigest()
    for index, (phase, _role) in enumerate(CASES):
        proposal = {
            "schema": 1,
            "target": 701202,
            "dimension": 16,
            "precision": 64,
            "order": 1,
            "fma": 0,
            "kind": 2,
            "phase": phase,
            "lane_stride": 1,
            "lane_offset": 0,
            "load": 0,
            "layout": 0,
            "unroll": 1,
            "context": context_hash,
        }
        (proposals / f"{index:03d}.proposal.json").write_bytes(
            (json.dumps(proposal, separators=(",", ":")) + "\n").encode()
        )
    rows = []
    for path in sorted(proposals.glob("*.proposal.json")):
        row = engine.compute_proposal_reward(args.admission_bin, context_path, path, args.novelty_bin)
        row["proposal"] = path.name
        if row.get("novelty_milli") is None or row.get("reward_milli") != 500 + int(row["novelty_milli"]):
            print("missing native reward_milli", file=sys.stderr)
            return 1
        rows.append(row)
    stats = engine.group_statistics(args.group_bin, [row["reward_milli"] for row in rows])
    for row, deviation in zip(rows, stats["centered_deviation"]):
        row["centered_deviation"] = deviation
    holdout_millis = [row["reward_milli"] for row in rows if row.get("split") == "holdout"]
    holdout_deviations = [row["centered_deviation"] for row in rows if row.get("split") == "holdout"]
    payload = {
        "schema": "pireus-grpo-reward-batch-v5",
        "claim_ready": False,
        "historical_atlas_rewritten": False,
        "supersedes_prior_batches": False,
        "degeneracy_authority": "continuity/group_variance.sio",
        "holdout_classes": list(engine.HOLDOUT_CLASSES),
        "holdout_count": len(holdout_millis),
        "advantage_numerator": "centered_deviation",
        "std_division": False,
        "advantage_degenerate": bool(stats["degenerate"]),
        "reward_sum": int(stats["reward_sum"]),
        "centered_sum_squares": int(stats["centered_sum_squares"]),
        "variance_denominator": int(stats["variance_denominator"]),
        "total_proposals": len(rows),
        "admitted_count": sum(row["admitted"] for row in rows),
        "admission_sha256": hashlib.sha256(args.admission_bin.read_bytes()).hexdigest(),
        "novelty_sha256": hashlib.sha256(args.novelty_bin.read_bytes()).hexdigest(),
        "group_sha256": hashlib.sha256(args.group_bin.read_bytes()).hexdigest(),
        "evaluations": rows,
    }
    if payload["admitted_count"] != len(CASES) or payload["advantage_degenerate"] or payload["holdout_count"] != 4:
        print(json.dumps(payload, indent=2), file=sys.stderr)
        return 1
    if len(set(holdout_millis)) != 1 or len(set(holdout_deviations)) != 1:
        print("holdout rewards differ", file=sys.stderr)
        return 1
    if stats["centered_deviation"] != [-399, 1, 2393, 2801, -1199, -1199, -1199, -1199]:
        print("centered deviations do not match the published eight rewards", file=sys.stderr)
        return 1
    if all(deviation == 0 for deviation in stats["centered_deviation"]):
        print("every centered deviation is zero", file=sys.stderr)
        return 1
    if any(row["reward_milli"] >= 1000 for row in rows if row.get("novelty_source") == "train_corpus"):
        print("visited corpus reward reached 1000 thousandths", file=sys.stderr)
        return 1
    if payload["reward_sum"] != 5199 or payload["centered_sum_squares"] != 19481656 or payload["variance_denominator"] != 512:
        print("integer moment does not match the published eight rewards", file=sys.stderr)
        return 1
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
