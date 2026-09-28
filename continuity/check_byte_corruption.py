#!/usr/bin/env python3
"""Corruption-triple probe for the image-backed class table.

Modifies single qwords of the embedded 1024-entry class table and
re-executes the oracle:
1. BINDING: +1 on the slot the phase reads (slot = quadratic_code)
   -> the answer must change.
2. CONTROL: +1 on a slot the phase does not read -> identical answer.
3. CLASS_RANGE: force class 99 into the read slot -> the oracle must
   REFUSE with CLASS_RANGE, never leak the class stored at index 99.
"""
import argparse
import json
import re
import struct
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--phase", type=int, default=0)
    args = parser.parse_args()

    work = args.oracle.parent / "corrupt.elf"

    src = args.source.read_text()
    block = src.split("let classes: [i64; 1024] = [", 1)[1].split("]", 1)[0]
    values = [int(x) for x in re.findall(r"-?\d+", block)]
    if len(values) != 1024:
        raise SystemExit(f"source table has {len(values)} entries")
    packed = struct.pack("<1024q", *values)

    data = bytearray(args.oracle.read_bytes())
    off = bytes(data).find(packed)
    if off < 0:
        raise SystemExit("table needle not found in ELF")

    def run(buf):
        work.write_bytes(buf)
        work.chmod(0o755)
        proc = subprocess.run([str(work), str(args.phase)],
                              capture_output=True, text=True)
        return proc.stdout.strip()

    def corrupt(slot, new_value):
        buf = bytearray(data)
        struct.pack_into("<q", buf, off + slot * 8, new_value)
        return buf

    pristine = run(data)
    qc = int(re.search(r'"quadratic_code":(\d+)', pristine).group(1))
    control_slot = (qc + 1) % 1024

    binding_changed = run(corrupt(qc, values[qc] + 1)) != pristine
    control_identical = run(corrupt(control_slot, values[control_slot] + 1)) == pristine
    range_out = run(corrupt(qc, 99))
    range_refused = "CLASS_RANGE" in range_out and str(values[99]) not in range_out

    ok = binding_changed and control_identical and range_refused
    print(json.dumps({
        "status": "PASS" if ok else "FAIL",
        "probe": "corruption_triple",
        "table_offset": off,
        "read_slot": qc,
        "read_slot_flipped_answer_changed": binding_changed,
        "control_slot": control_slot,
        "control_slot_flipped_answer_identical": control_identical,
        "out_of_range_slot_refused": range_refused,
        "claim_ready": False,
    }, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
