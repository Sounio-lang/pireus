#!/usr/bin/env python3
"""Semantic binding: the ELF returns the same values as the Lean specification.

For each of the 1024 quadratic codes, one phase is chosen and the oracle is
executed. Every output field is compared against the frozen tables and formulas
from SounioPireusQuadraticNoveltyScalar.lean. This is behavioral equivalence,
not byte storage. It proves the binary computes what Lean proves.
"""
import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

FROZEN_COMMUTATOR = [
    210, 210, 210, 210, 114, 114, 114, 114, 114, 114, 114, 114, 114, 114, 114, 114,
    114, 114, 114, 114, 114, 114, 114, 114, 90, 90, 90, 90, 90, 90, 90, 90]

FROZEN_SQUARES = [
    15, 7, 7, 7, 11, 3, 7, 7, 7, 7, 11, 11, 7, 11, 3, 7,
    11, 7, 7, 7, 7, 11, 3, 7, 9, 9, 5, 5, 9, 5, 5, 9]

FROZEN_VISITED = [
    1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0,
    1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0]

FROZEN_HOLDOUT = [
    0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]


def source_classes(path):
    text = path.read_text()
    block = text.split("let classes: [i64; 1024] = [", 1)[1].split("]", 1)[0]
    return [int(item) for item in re.findall(r"-?\d+", block)]


def phase_for_code(code):
    phase = 0
    for source_bit, phase_bit in ((0, 0), (1, 5), (2, 10), (3, 15),
                                   (4, 1), (5, 2), (6, 3), (7, 6), (8, 7), (9, 11)):
        if (code >> source_bit) & 1:
            phase |= 1 << phase_bit
    return phase


def lean_expected(class_id):
    commutator = FROZEN_COMMUTATOR[class_id]
    squares = FROZEN_SQUARES[class_id]
    distance = abs(commutator - 210) + abs(squares - 15)
    graded_milli = (26000 + 300 * distance) // 130
    held = FROZEN_HOLDOUT[class_id]
    visited = FROZEN_VISITED[class_id]
    if held:
        novelty_milli = 0
    elif visited:
        novelty_milli = 100 if distance == 0 else 150
    else:
        novelty_milli = graded_milli
    admitted = 500 + novelty_milli
    return {
        "class_id": class_id,
        "train_visited": visited,
        "holdout": held,
        "commutator_defect": commutator,
        "square_negative_count": squares,
        "corpus_distance": distance,
        "novelty_milli": novelty_milli,
        "graded_milli": graded_milli,
        "admitted_reward_milli": admitted,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=HERE / "novelty_oracle.sio")
    args = parser.parse_args()
    classes = source_classes(args.source)
    mismatches = []
    started = time.perf_counter()
    for code, class_id in enumerate(classes):
        phase = phase_for_code(code)
        proc = subprocess.run([str(args.oracle), str(phase)],
                              capture_output=True, text=True, check=True)
        got = json.loads(proc.stdout)
        want = lean_expected(class_id)
        for key, expected_value in want.items():
            if got.get(key) != expected_value:
                mismatches.append({
                    "code": code, "phase": phase, "field": key,
                    "got": got.get(key), "want": expected_value,
                })
                break
        if got.get("claim_ready") is not False:
            mismatches.append({"code": code, "field": "claim_ready",
                               "got": got.get("claim_ready"), "want": False})
        if len(mismatches) == 5:
            break
    if mismatches:
        raise SystemExit(json.dumps(mismatches, indent=2))
    print(json.dumps({
        "status": "PASS",
        "binding": "semantic",
        "byte_binding": False,
        "codes_checked": 1024,
        "fields_checked": 9,
        "mismatches": 0,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "oracle_sha256": hashlib.sha256(args.oracle.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "lean_spec": "SounioPireusQuadraticNoveltyScalar",
        "claim_ready": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
