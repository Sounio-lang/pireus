#!/usr/bin/env python3
"""Third implementation of the admitted affine action. Imports nothing from PIREUS code."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def cd_sigma(a, b, bits=4):
    if a == 0 or b == 0:
        return 1
    if bits <= 1:
        return -1
    half = 1 << (bits - 1)
    ah, bh = int(a >= half), int(b >= half)
    al, bl = a & (half - 1), b & (half - 1)
    if ah == 0 and bh == 0:
        return cd_sigma(al, bl, bits - 1)
    if ah == 0 and bh == 1:
        return cd_sigma(bl, al, bits - 1)
    if ah == 1 and bh == 0:
        return cd_sigma(al, 0, bits - 1) if bl == 0 else -cd_sigma(al, bl, bits - 1)
    return -cd_sigma(0, al, bits - 1) if bl == 0 else cd_sigma(bl, al, bits - 1)

CD = [[1 if cd_sigma(i, j) == -1 else 0 for j in range(16)] for i in range(16)]

def is_coboundary(table):
    for i in range(16):
        if table[i][0] or table[0][i] or table[i][i]:
            return False
    q = [0] * 16
    for a, b in ((1, 2), (1, 4), (1, 8), (2, 4), (2, 8), (4, 8)):
        q[a ^ b] = table[a][b]
    for ab, c, abc in ((3, 4, 7), (3, 8, 11), (5, 8, 13), (6, 8, 14)):
        q[abc] = table[ab][c] ^ q[ab]
    q[15] = table[7][8] ^ q[7]
    return all(table[i][j] == (q[i] ^ q[j] ^ q[i ^ j]) for i in range(16) for j in range(16))

def in_bilinear_plus_coboundary(table):
    diagonal = [[0] * 4 for _ in range(4)]
    for r in range(4):
        diagonal[r][r] = table[1 << r][1 << r]
    for r in range(4):
        for s in range(r + 1, 4):
            both = (1 << r) ^ (1 << s)
            diagonal[r][s] = table[both][both] ^ table[1 << r][1 << r] ^ table[1 << s][1 << s]
    bilinear = [[0] * 16 for _ in range(16)]
    for i in range(16):
        for j in range(16):
            value = 0
            for r in range(4):
                if (i >> r) & 1:
                    for s in range(4):
                        if (j >> s) & 1:
                            value ^= diagonal[r][s]
            bilinear[i][j] = value
    return is_coboundary([[table[i][j] ^ bilinear[i][j] for j in range(16)] for i in range(16)])

PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))

def quadratic_from_values(values):
    code = 0
    for r in range(4):
        code |= values[1 << r] << r
    for idx, (r, s) in enumerate(PAIRS):
        both = (1 << r) ^ (1 << s)
        code |= (values[both] ^ values[1 << r] ^ values[1 << s]) << (4 + idx)
    return code

def values_from_quadratic(code):
    values = [0] * 16
    for x in range(16):
        result = 0
        for r in range(4):
            if (x >> r) & 1:
                result ^= (code >> r) & 1
        for idx, (r, s) in enumerate(PAIRS):
            if ((x >> r) & 1) and ((x >> s) & 1):
                result ^= (code >> (4 + idx)) & 1
        values[x] = result
    return values

admitted = []
for r0 in range(1, 16):
    span1 = {0, r0}
    for r1 in range(1, 16):
        if r1 in span1:
            continue
        span2 = span1 | {r1, r0 ^ r1}
        for r2 in range(1, 16):
            if r2 in span2:
                continue
            span3 = span2 | {r2, r0 ^ r2, r1 ^ r2, r0 ^ r1 ^ r2}
            for r3 in range(1, 16):
                if r3 in span3:
                    continue
                mapped = [0] * 16
                for vector in range(16):
                    mapped[vector] = (
                        (((bin(r0 & vector).count("1") & 1) << 0)
                         | ((bin(r1 & vector).count("1") & 1) << 1)
                         | ((bin(r2 & vector).count("1") & 1) << 2)
                         | ((bin(r3 & vector).count("1") & 1) << 3))
                    )
                for swap in (0, 1):
                    delta = [[0] * 16 for _ in range(16)]
                    for i in range(16):
                        for j in range(16):
                            source_i, source_j = (mapped[j], mapped[i]) if swap else (mapped[i], mapped[j])
                            delta[i][j] = CD[source_i][source_j] ^ CD[i][j]
                    if in_bilinear_plus_coboundary(delta):
                        admitted.append((mapped, quadratic_from_values([delta[x][x] for x in range(16)])))
if len(admitted) != 336:
    raise SystemExit(f"admitted {len(admitted)}")
parent = list(range(1024))
def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i
evals = [values_from_quadratic(code) for code in range(1024)]
for mapped, displacement in admitted:
    for code in range(1024):
        pulled = quadratic_from_values([evals[code][mapped[x]] for x in range(16)]) ^ displacement
        a, b = find(code), find(pulled)
        if a != b:
            parent[a] = b
groups = {}
for code in range(1024):
    groups.setdefault(find(code), []).append(code)
ordered = sorted(groups.values(), key=min)
if len(ordered) != 32 or sum(len(g) for g in ordered) != 1024:
    raise SystemExit("partition failed")
independent = [-1] * 1024
for class_id, members in enumerate(ordered):
    for code in members:
        independent[code] = class_id
source = (ROOT / "continuity/novelty_oracle.sio").read_text()
block = source.split("let classes: [i64; 1024] = [", 1)[1].split("]", 1)[0]
embedded = [int(x) for x in re.findall(r"-?\d+", block)]
if embedded != independent:
    for code, (left, right) in enumerate(zip(embedded, independent)):
        if left != right:
            raise SystemExit(f"first mismatch q={code} embedded={left} independent={right}")
inventory = json.loads((ROOT / "continuity/atlas_m7/orbit_classes_inventory.json").read_text())
for row, members in zip(inventory, ordered):
    if row["min_quadratic_code"] != min(members) or row["quadratic_codes_count"] != len(members):
        raise SystemExit(f"inventory mismatch {row['class_id']}")
print(json.dumps({
    "status": "PASS",
    "admitted_actions": 336,
    "classes": 32,
    "quadratic_codes_matched": 1024,
    "embedded_table_mismatches": 0,
    "inventory_minima_matched": 32,
    "implementation": "cd_sigma, coboundary test, and affine action rewritten without importing PIREUS",
}, indent=2))
