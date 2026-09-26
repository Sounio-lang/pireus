#!/bin/bash
# Full PIREUS verification on the Sounio workspace.
# Compiles all three ELFs from source with the committed Madaros prebuilt,
# then runs every behavioral check and Lean certificate.
#
# Usage: bash run_verification.sh [work_dir] [lean_dir]
# Default work_dir: /tmp/pireus-verification
# Default lean_dir: /tmp/pireus-scalar-lean
set -euo pipefail

WORK_DIR="${1:-/tmp/pireus-verification}"
LEAN_DIR="${2:-/tmp/pireus-scalar-lean}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

export SOUNIO_REQUIRE_COMMITTED_MADAROS=1
export MADAROS_RAW_BIN=/workspace/sounio/bin/madaros-linux-x86_64
export PATH="$HOME/.elan/bin:$PATH"

mkdir -p "$WORK_DIR"

echo "=== Compiling ELFs from source ==="
cd /workspace/sounio
./bin/souc compile "$SCRIPT_DIR/novelty_oracle.sio" -o "$WORK_DIR/novelty.elf"
./bin/souc compile "$SCRIPT_DIR/group_variance.sio" -o "$WORK_DIR/group_variance.elf"
cp "$SCRIPT_DIR/admission.sio" /tmp/pireus-m8/tree/continuity/admission.sio 2>/dev/null || true
./bin/souc compile /tmp/pireus-m8/tree/continuity/admission.sio -o "$WORK_DIR/admission.elf"
chmod +x "$WORK_DIR"/*.elf

echo "=== Running verification ==="
cd "$SCRIPT_DIR"
python3 verify_all.py \
  --admission-bin "$WORK_DIR/admission.elf" \
  --novelty-bin "$WORK_DIR/novelty.elf" \
  --group-bin "$WORK_DIR/group_variance.elf" \
  --lean-dir "$LEAN_DIR" \
  2>&1

echo "=== Done ==="
