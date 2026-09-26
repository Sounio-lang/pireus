#!/usr/bin/env python3
"""Build one M8 reward batch from the native admission and novelty executables.

The historical M5 and M7 atlas files are not inputs and are not rewritten.
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
        rows.append(row)
    rows = engine.evaluate_group_relative_advantages(rows)
    rewards = [row["reward"] for row in rows]
    mean = sum(rewards) / len(rewards)
    variance = sum((reward - mean) ** 2 for reward in rewards) / len(rewards)
    payload = {
        "schema": "pireus-grpo-reward-batch-v2",
        "claim_ready": False,
        "historical_atlas_rewritten": False,
        "holdout_classes": list(engine.HOLDOUT_CLASSES),
        "holdout_count": sum(row.get("split") == "holdout" for row in rows),
        "advantage_degenerate": variance == 0.0,
        "reward_variance": variance,
        "total_proposals": len(rows),
        "admitted_count": sum(row["admitted"] for row in rows),
        "mean_reward": mean,
        "admission_sha256": hashlib.sha256(args.admission_bin.read_bytes()).hexdigest(),
        "novelty_sha256": hashlib.sha256(args.novelty_bin.read_bytes()).hexdigest(),
        "evaluations": rows,
    }
    if payload["admitted_count"] != len(CASES) or payload["advantage_degenerate"] or payload["holdout_count"] != 4:
        print(json.dumps(payload, indent=2), file=sys.stderr)
        return 1
    if any(row["reward"] >= 1.0 for row in rows if row.get("novelty_source") == "train_corpus"):
        print("visited corpus reward reached 1.0", file=sys.stderr)
        return 1
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
