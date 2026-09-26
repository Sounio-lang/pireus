#!/usr/bin/env python3
"""Extract the 1024-entry class table from the novelty oracle ELF and compare
it with the source literal in novelty_oracle.sio.

This is byte-level storage binding, not behavioral equivalence. It proves the
table is present in the binary. It does not prove the binary uses it.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path


def source_table(path):
    text = path.read_text()
    block = text.split("let classes: [i64; 1024] = [", 1)[1].split("]", 1)[0]
    values = [int(item) for item in re.findall(r"-?\d+", block)]
    if len(values) != 1024:
        raise SystemExit(f"source table has {len(values)} entries")
    return values


def find_table_in_elf(elf_path, expected):
    data = elf_path.read_bytes()
    # Pack the expected table as 1024 little-endian i64 values.
    packed = struct.pack(f"<{len(expected)}q", *expected)
    idx = data.find(packed)
    if idx >= 0:
        return idx
    # Try i32.
    packed32 = struct.pack(f"<{len(expected)}i", *expected)
    idx = data.find(packed32)
    if idx >= 0:
        return idx
    return -1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    expected = source_table(args.source)
    offset = find_table_in_elf(args.oracle, expected)
    if offset < 0:
        print(json.dumps({
            "status": "FAIL",
            "reason": "table_not_found_in_elf",
            "entries_expected": len(expected),
            "claim_ready": False,
        }, indent=2))
        return 1
    print(json.dumps({
        "status": "PASS",
        "binding": "byte_storage",
        "entries_matched": 1024,
        "elf_offset": offset,
        "claim_ready": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
