#!/usr/bin/env python3
"""Check the native novelty oracle against every phase and the M7 inventory.

This reruns the partition in tools/pireus_autonomous_explorer.py. It is a
regression check against a committed inventory, not a separate existence proof.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, default=HERE / "atlas_m7/orbit_classes_inventory.json")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("explorer", ROOT / "tools/pireus_autonomous_explorer.py")
    explorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(explorer)
    engine = explorer.PireusAutonomousExplorer(Path("/tmp/none"), ROOT)
    _, raw_min, _ = engine.run_full_census()
    classes, _, details = engine.compute_orbit_classes(raw_min)
    inventory = json.loads(args.inventory.read_text())
    for row, members, detail in zip(inventory, classes, details):
        if (
            row["class_id"] != detail["class_id"]
            or row["min_quadratic_code"] != min(members)
            or row["quadratic_codes_count"] != len(members)
            or row["raw_matrices_count"] != len(members) * 64
            or row["commutator_defects"] != detail["commutator_defects"]
            or row["square_negative_count"] != detail["square_negative_count"]
            or bool(row["is_unvisited_in_m5"]) != bool(detail["is_unvisited_in_m5"])
        ):
            raise SystemExit(f"inventory mismatch at class {row['class_id']}")
    expected = [-1] * 1024
    for class_id, members in enumerate(classes):
        for code in members:
            expected[code] = class_id
    holdout = {1, 2, 11, 23}
    visited = {row["class_id"] for row in inventory if not row["is_unvisited_in_m5"]}
    counts = Counter()
    started = time.perf_counter()
    for phase in range(65536):
        proc = subprocess.run([str(args.oracle), str(phase)], capture_output=True, text=True, check=True)
        got = json.loads(proc.stdout)
        code = explorer.q_code_from_phase(phase)
        class_id = expected[code]
        counts[class_id] += 1
        distance = abs(details[class_id]["commutator_defects"] - 210) + abs(details[class_id]["square_negative_count"] - 15)
        graded_milli = (26000 + 300 * distance) // 130
        if class_id in holdout:
            novelty_milli = 0
        elif class_id in visited:
            novelty_milli = 100 if distance == 0 else 150
        else:
            novelty_milli = graded_milli
        if (
            got["quadratic_code"] != code
            or got["class_id"] != class_id
            or got["train_visited"] != int(class_id in visited)
            or got["holdout"] != int(class_id in holdout)
            or got["commutator_defect"] != details[class_id]["commutator_defects"]
            or got["square_negative_count"] != details[class_id]["square_negative_count"]
            or got["corpus_distance"] != distance
            or got["novelty_milli"] != novelty_milli
            or got["graded_milli"] != graded_milli
            or got["admitted_reward_milli"] != 500 + novelty_milli
            or got["claim_ready"] is not False
        ):
            raise SystemExit(f"mismatch at phase {phase}: {got}")
    if any(counts[i] != len(classes[i]) * 64 for i in range(32)):
        raise SystemExit("quadratic fibre is not 64 matrices")
    print(json.dumps({
        "status": "PASS",
        "phases_checked": 65536,
        "mismatches": 0,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "oracle_sha256": hashlib.sha256(args.oracle.read_bytes()).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
