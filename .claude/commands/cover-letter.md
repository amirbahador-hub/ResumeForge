---
description: Draft a tailored cover letter from the master profile and a job description.
---

You are running the `/cover-letter` command for ResumeForge.

## Inputs
1. **Job description** — path, URL, or pasted text. Required.
2. **Tone** — ask if not specified. Options: `concise` (default, ~200 words), `warm` (~300 words, more personal), `formal` (~250 words, classic structure).
3. **Hook** — optionally, a specific reason the user is interested in *this* company (a product they use, a blog post, a friend who works there). If the user can't supply one, write a generic but honest opener — don't fake enthusiasm.

## Sources to read
- `profile/profile.yaml`
- `prompts/recruiter-signals.md`

## What you do

1. Read the JD and the profile.
2. Identify the 2–3 strongest stories from the profile that match the role. A story = (problem → action → outcome). Pull them straight from `experience[].highlights`. Don't invent.
3. Write the cover letter into `artifacts/<slug>/cover-letter.md` where slug matches the related resume's slug if one exists, otherwise `<companyOrRole>-<YYYYMMDD>`.

## Letter structure

- **Opening (1 short paragraph)**: who you are, what role you're applying to, the hook (or an honest substitute). No "I am writing to apply for…" boilerplate.
- **Body (1–2 paragraphs)**: 2–3 specific stories from the profile that prove fit. Each story names the problem, the candidate's action, and a concrete outcome. Tie at least one story to a JD-stated need verbatim.
- **Close (1 short paragraph)**: why this company specifically (not generic), and a single forward-looking line. Sign off plainly.

## Rules
- No buzzwords ("passionate", "synergy", "rockstar", "fast-paced").
- No first sentence that starts with "I".
- No metrics that aren't in the profile.
- Match the tone setting precisely. Concise means concise — don't pad.
- Read it back before finalizing. If it could be sent to any company, it's not tailored. Rewrite.

After writing, print:
- Path to the file.
- Word count.
- One line: what would make the next version stronger (e.g., "add a real product hook for X").

$ARGUMENTS
