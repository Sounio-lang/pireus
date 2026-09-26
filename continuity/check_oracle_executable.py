#!/usr/bin/env python3
"""Compare the compiled novelty oracle with the source class table.

One phase is chosen for each of the 1024 quadratic codes. The executable's
class_id must equal the literal in continuity/novelty_oracle.sio. This is a
behavioral check, not a proof that the binary stores those bytes.
"""
import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def source_classes(path: Path):
    text = path.read_text()
    block = text.split("let classes: [i64; 1024] = [", 1)[1].split("]", 1)[0]
    values = [int(item) for item in re.findall(r"-?\d+", block)]
    if len(values) != 1024:
        raise SystemExit(f"source table has {len(values)} entries")
    return values


def phase_for_code(code: int) -> int:
    phase = 0
    for source_bit, phase_bit in ((0, 0), (1, 5), (2, 10), (3, 15), (4, 1), (5, 2), (6, 3), (7, 6), (8, 7), (9, 11)):
        if (code >> source_bit) & 1:
            phase |= 1 << phase_bit
    return phase


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=HERE / "novelty_oracle.sio")
    args = parser.parse_args()
    expected = source_classes(args.source)
    mismatches = []
    started = time.perf_counter()
    for code, class_id in enumerate(expected):
        phase = phase_for_code(code)
        proc = subprocess.run([str(args.oracle), str(phase)], capture_output=True, text=True, check=True)
        got = json.loads(proc.stdout)
        if got["quadratic_code"] != code or got["class_id"] != class_id or got["claim_ready"] is not False:
            mismatches.append({"code": code, "phase": phase, "got": got, "expected_class": class_id})
            if len(mismatches) == 5:
                break
    if mismatches:
        raise SystemExit(json.dumps(mismatches, indent=2))
    print(json.dumps({
        "status": "PASS",
        "codes_checked": 1024,
        "mismatches": 0,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "oracle_sha256": hashlib.sha256(args.oracle.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "binding": "behavioral",
        "byte_binding": False,
        "claim_ready": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
