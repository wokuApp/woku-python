#!/usr/bin/env bash
#
# Regenerate the Pydantic v2 request models from the vendored OpenAPI spec.
#
# The spec is the single source of truth (generated from the woku-server Nest
# app, kept in sync with the JS SDK). Run this whenever openapi/openapi-v1.json
# changes. The output is committed so builds and CI never need the generator.
#
# Requires uv (https://docs.astral.sh/uv/). The generator runs through uvx, so
# nothing is installed into the project environment.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC="$ROOT/openapi/openapi-v1.json"
OUT="$ROOT/src/woku/_generated/models.py"

uvx --from 'datamodel-code-generator==0.26.5' datamodel-codegen \
  --input "$SPEC" \
  --input-file-type openapi \
  --output "$OUT" \
  --output-model-type pydantic_v2.BaseModel \
  --target-python-version 3.9 \
  --use-standard-collections \
  --use-annotated \
  --field-constraints \
  --use-field-description \
  --use-schema-description \
  --disable-timestamp \
  --collapse-root-models

# Drop the EmailStr dependency: the API validates recipients server-side and the
# JS SDK types them structurally too, so we keep the runtime dependency-light
# (pydantic + httpx only, no email-validator/dnspython).
python3 - "$OUT" <<'PY'
import re
import sys

path = sys.argv[1]
text = path and open(path, encoding="utf-8").read()
text = text.replace("from pydantic import BaseModel, EmailStr, Field",
                    "from pydantic import BaseModel, Field")
text = re.sub(r"\bEmailStr\b", "str", text)
open(path, "w", encoding="utf-8").write(text)
PY

echo "Generated $OUT"
