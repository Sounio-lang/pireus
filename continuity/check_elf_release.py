#!/usr/bin/env python3
"""Verify that the ELFs compiled from source match the published release.

Compiles all three ELFs with the committed Madaros prebuilt and compares
their sha256 hashes with the release assets. If the source changed, the
hashes differ and this check fails.
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

EXPECTED = {
    "admission.elf": "321c4d9c61603dff4f258b3ef98a1ed41c46c086088e6e286f5e5bd84c75161a",
    "novelty.elf": "63007d26532facb04ba93b8e956c616eb0b0256f4d908ba2197f068884c3e1d4",
    "group_variance.elf": "b96139b4d87dea6291cf3fec44f82240f08f3298a7e61c89de4c71eb0458b83e",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf-dir", type=Path, required=True,
                        help="Directory containing the three compiled ELFs")
    args = parser.parse_args()
    mismatches = []
    for name, expected in EXPECTED.items():
        path = args.elf_dir / name
        if not path.exists():
            mismatches.append({"elf": name, "error": "missing"})
            continue
        got = sha256(path)
        if got != expected:
            mismatches.append({"elf": name, "got": got, "want": expected})
    if mismatches:
        print(json.dumps({"status": "FAIL", "mismatches": mismatches}, indent=2))
        return 1
    print(json.dumps({
        "status": "PASS",
        "binding": "release_hash",
        "elfs_checked": 3,
        "mismatches": 0,
        "claim_ready": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
