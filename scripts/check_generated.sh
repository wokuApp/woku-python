#!/usr/bin/env bash
# Check generated artifacts without modifying the checkout.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT="$(mktemp -d)"
trap 'rm -rf "$OUTPUT"' EXIT
WOKU_CODEGEN_OUTPUT_ROOT="$OUTPUT" bash "$ROOT/scripts/generate_models.sh"
for artifact in models.py journeys.py; do
  diff -u "$ROOT/src/woku/_generated/$artifact" "$OUTPUT/$artifact"
done
printf 'Generated Python API models are up to date.\n'
