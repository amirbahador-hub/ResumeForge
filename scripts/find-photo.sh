#!/usr/bin/env bash
# Print the path to the user's profile photo if one exists.
#
# Convention: place your photo at `profile/pic.<ext>`. Accepted extensions:
# jpg, jpeg, png, webp. The first match wins.
#
# Exits 0 with the path on stdout if found; exits 1 silently if not found.

set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"

for ext in JPG jpg JPEG jpeg PNG png WEBP webp; do
  candidate="$repo_root/profile/pic.$ext"
  if [[ -f "$candidate" ]]; then
    echo "$candidate"
    exit 0
  fi
done

exit 1
