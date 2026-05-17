#!/usr/bin/env bash
# Thin wrapper around scripts/ai-detect.py.
#
# Usage:
#   scripts/ai-detect.sh <resume.pdf|.md|.html>           # default threshold
#   scripts/ai-detect.sh <file> --strict                  # strict threshold
#
# Scores how "LLM-sounding" the resume reads (em-dash density, common AI
# phrase tells, triadic-pattern frequency). Exit 0 if the score is below
# the threshold; non-zero otherwise.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <resume-file> [--strict]" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"

py=""
for cmd in python3 python; do
  if command -v "$cmd" >/dev/null 2>&1; then
    py="$cmd"
    break
  fi
done

if [[ -z "$py" ]]; then
  echo "error: python3 not found on PATH" >&2
  exit 1
fi

exec "$py" "$script_dir/ai-detect.py" "$@"
