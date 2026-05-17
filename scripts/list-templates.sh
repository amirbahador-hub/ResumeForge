#!/usr/bin/env bash
# List available resume templates with their descriptions.
#
# Reads templates/manifest.json. Templates with `needs_photo: true` are
# tagged with [photo] so the user knows to drop a `profile/pic.<ext>`
# before generating.

set -euo pipefail

manifest="templates/manifest.json"

if [[ ! -f "$manifest" ]]; then
  echo "error: $manifest not found" >&2
  exit 1
fi

if command -v jq >/dev/null 2>&1; then
  jq -r '.templates[] | "\(.id)\t\(if .needs_photo then "[photo] " else "" end)\(.name) — \(.description)"' "$manifest"
else
  python3 -c '
import json
with open("templates/manifest.json") as f:
    data = json.load(f)
for t in data["templates"]:
    tag = "[photo] " if t.get("needs_photo") else ""
    print(f"{t[\"id\"]}\t{tag}{t[\"name\"]} — {t[\"description\"]}")
'
fi
