#!/usr/bin/env bash
# Render an HTML file to PDF. Portable across macOS / Linux / Windows (WSL).
#
# Usage:
#   scripts/render-pdf.sh <input.html> <output.pdf>
#
# Strategy (no hardcoded vendor paths):
#   1. Prefer Playwright (Python) — bundles its own Chromium, works everywhere.
#   2. Fall back to Chrome / Chromium / Edge / Brave found on $PATH.
#   3. Otherwise print install instructions and fail.
#
# Install Playwright once (recommended, one-time, ~150MB):
#   pip install playwright
#   playwright install chromium

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <input.html> <output.pdf>" >&2
  exit 2
fi

input="$1"
output="$2"

if [[ ! -f "$input" ]]; then
  echo "error: input HTML not found: $input" >&2
  exit 1
fi

mkdir -p "$(dirname "$output")"

script_dir="$(cd "$(dirname "$0")" && pwd)"

# --- Attempt 1: Playwright via Python ----------------------------------------
pick_python() {
  for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
      if "$cmd" -c "import playwright" >/dev/null 2>&1; then
        echo "$cmd"
        return 0
      fi
    fi
  done
  return 1
}

if py="$(pick_python)"; then
  "$py" "$script_dir/render-pdf.py" "$input" "$output"
  exit $?
fi

# --- Attempt 2: any Chromium-family browser on $PATH -------------------------
case "$input" in
  /*) abs_input="$input" ;;
  *)  abs_input="$PWD/$input" ;;
esac

browser=""
for name in google-chrome google-chrome-stable chromium chromium-browser microsoft-edge brave-browser chrome; do
  if path="$(command -v "$name" 2>/dev/null)"; then
    browser="$path"
    break
  fi
done

if [[ -n "$browser" ]]; then
  "$browser" \
    --headless=new \
    --disable-gpu \
    --no-pdf-header-footer \
    --print-to-pdf="$output" \
    "file://$abs_input" >/dev/null 2>&1

  if [[ -f "$output" ]]; then
    echo "wrote $output"
    exit 0
  fi
fi

# --- Nothing worked ----------------------------------------------------------
cat >&2 <<'MSG'
error: could not render PDF — no rendering backend available.

Recommended (works on macOS, Linux, Windows):
    pip install playwright
    playwright install chromium

Alternative: install Chrome or Chromium and ensure it is on your $PATH
(one of: google-chrome, chromium, chromium-browser, microsoft-edge, brave-browser).
MSG
exit 1
