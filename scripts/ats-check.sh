#!/usr/bin/env bash
# Thin wrapper around scripts/ats-check.py.
#
# Usage:
#   scripts/ats-check.sh <resume.pdf> [job_description.md]
#
# Reads the rendered PDF and a JD, reports:
#   - file size vs. 1MB cap
#   - page count vs. 2-page target
#   - whether text is selectable
#   - whether standard headings (Skills / Experience / Education) are present
#   - JD keyword coverage
#
# For best results: pip install pypdf  (otherwise falls back to pdftotext /
# mdls / the sibling tailored_resume.md). The script still runs without pypdf
# but page-count and PDF-text checks may be less reliable.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <resume.pdf> [job_description.md]" >&2
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

exec "$py" "$script_dir/ats-check.py" "$@"
