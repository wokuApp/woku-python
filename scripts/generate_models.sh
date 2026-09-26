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

# Journey resources return dictionaries. Generate their structural types from
# the same schema instead of maintaining a second hand-written contract.
JOURNEY_SPEC="$(mktemp)"
trap 'rm -f "$JOURNEY_SPEC"' EXIT
python3 - "$SPEC" "$JOURNEY_SPEC" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as source:
    spec = json.load(source)
all_schemas = spec["components"]["schemas"]
selected = {}

def collect(value):
    if isinstance(value, dict):
        ref = value.get("$ref", "")
        prefix = "#/components/schemas/"
        if ref.startswith(prefix):
            name = ref[len(prefix):]
            if name not in selected:
                selected[name] = all_schemas[name]
                collect(selected[name])
        for child in value.values():
            collect(child)
    elif isinstance(value, list):
        for child in value:
            collect(child)

for path, operations in spec["paths"].items():
    if path.startswith("/v1/journeys") or path.startswith("/v1/journey-entries") or path == "/v1/journey-events":
        collect(operations)
spec["paths"] = {}
spec["components"] = {"schemas": selected}
with open(sys.argv[2], "w", encoding="utf-8") as output:
    json.dump(spec, output)
PY
uvx --from 'datamodel-code-generator==0.26.5' datamodel-codegen \
  --input "$JOURNEY_SPEC" \
  --input-file-type openapi \
  --output "$ROOT/src/woku/_generated/journeys.py" \
  --output-model-type typing.TypedDict \
  --target-python-version 3.9 \
  --enum-field-as-literal all \
  --use-standard-collections \
  --strict-nullable \
  --disable-timestamp \
  --collapse-root-models
# Keep the generated header deterministic despite the temporary subset path.
python3 - "$ROOT/src/woku/_generated/journeys.py" <<'PY'
import re
import sys

path = sys.argv[1]
with open(path, encoding="utf-8") as source:
    content = source.read()
content = re.sub(r"#   filename: .*", "#   filename: openapi-v1.json (journey subset)", content, count=1)
with open(path, "w", encoding="utf-8") as output:
    output.write(content)
PY
