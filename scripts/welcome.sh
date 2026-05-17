#!/usr/bin/env bash
# Emits the ResumeForge welcome menu as a SessionStart hook systemMessage.
# Output JSON is consumed by Claude Code; the message is shown to the user.

read -r -d '' MENU <<'EOF'
Welcome to ResumeForge. Here's what you can do:

  /generate-resume   Tailor a resume to a job description (MD + HTML + PDF)
  /analyze-job       Fit, gaps, keywords, and tailoring strategy vs a JD
  /cover-letter      Draft a tailored cover letter from your profile + a JD
  /update-profile    Interactively edit profile/profile.yaml

Your master profile lives at profile/profile.yaml — it's the only source of truth.
Outputs land in artifacts/<slug>/ (gitignored).

What would you like to do?
EOF

jq -n --arg msg "$MENU" '{systemMessage: $msg}'
