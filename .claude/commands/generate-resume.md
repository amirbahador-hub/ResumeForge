---
description: Tailor a resume to a specific job description using the master profile and a chosen template.
---

You are running the `/generate-resume` command for ResumeForge.

## Inputs to gather (ask the user, one at a time only if not provided in $ARGUMENTS)
1. **Job description** — paste, file path, or URL. If a URL, fetch it. If a path, read it.
2. **Template** — run `bash scripts/list-templates.sh` and let the user pick. Templates tagged `[photo]` need a profile photo at `profile/pic.<ext>`; run `bash scripts/find-photo.sh` to check. If a `[photo]` template is chosen and no photo is found, ask the user to drop one in `profile/` (jpg/jpeg/png/webp) or pick a different template. If $ARGUMENTS already names one (e.g. "portrait"), skip the prompt.
3. **Target company / role title** — used only for file naming and the optional summary line. Skip if obvious from the JD.

Don't bombard the user. Ask each missing input as it comes up, not all at once.

## Sources you MUST read before generating
- `profile/profile.yaml` — the only allowed source of truth for claims.
- `prompts/resume-best-practices.md` — apply every rule.
- `prompts/ats-rules.md` — apply every rule.
- `prompts/recruiter-signals.md` — bias bullet ordering and tailoring decisions toward these signals.
- The chosen `templates/<id>/index.html` and `templates/<id>/style.css` — these are the rendering target.

## What you do

### 1. Analyze the JD
Extract, in your head:
- Must-have stack and tools.
- Nice-to-have stack and tools.
- Seniority + scope expectations.
- Domain/industry.
- 5–10 keywords worth surfacing verbatim.
- Any hard constraints (location, work auth, on-call, language).

If the JD lacks essential context, ask ONE clarifying question before continuing.

### 2. Match against the profile
- Map each JD requirement to evidence in `profile/profile.yaml`. Note which are strong, weak, or missing.
- If something the JD calls a hard requirement is missing from the profile, surface it as a question to the user before generating. Do not invent.

### 3. Draft the tailored content
Produce, in this exact order:

**a. `artifacts/<slug>/tailored_resume.md`** — Markdown version of the tailored resume.
- Reorder Skills so JD-relevant categories lead.
- Reorder bullets within each role so JD-relevant work leads.
- Rewrite bullets where wording can mirror the JD *without* changing the underlying truth.
- Drop bullets with no signal for this role.
- Add an optional 3-line summary only if it's sharper than the rest of the resume.
- **Story line per role**: directly under each role's header (and *before* the bullets), write ONE italic narrative line framing the situation/scope/context of the role. Use the profile's `context:` field as the seed where present, tailored to the JD. See `prompts/resume-best-practices.md` → "Story line per role".
- **Bold the JD's important keywords** inside bullets — technologies, tools, frameworks, named systems. 1–3 per bullet. See `prompts/resume-best-practices.md` → "Keyword bolding".

**b. `artifacts/<slug>/changes.md`** — A short, scannable diff explaining:
- What you reordered.
- What you reworded (old → new).
- What you dropped and why.
- What you did NOT add despite the JD asking for it (because the profile doesn't support it).

**c. `artifacts/<slug>/questions.md`** — Any open questions for the user. Examples:
- "JD mentions Terraform; your profile doesn't. Have you used it? If yes, where?"
- "JD requires on-call rotation experience. Add to profile or leave off?"
- Only generate this file if there are questions. If none, skip it.

**d. `artifacts/<slug>/tailored_resume.html`** — Fill in the chosen template by hand.
- Read `templates/<id>/index.html`. It uses Jinja2-style placeholders (`{{ ... }}`, `{% ... %}`).
- Substitute every placeholder with concrete values from the tailored content. Remove control flow tags entirely after evaluating them.
- The result must be a single, complete, valid HTML document.
- Copy `templates/<id>/style.css` next to `tailored_resume.html` so the relative `style.css` href resolves.
- **If the template references `{{ content.photo }}`**: copy the user's photo (found via `bash scripts/find-photo.sh`) into `artifacts/<slug>/` keeping the same filename (e.g. `pic.JPG`), and substitute `{{ content.photo }}` with that filename. If no photo was found, ask the user before proceeding — do not strip the photo silently.

The slug is `<lastname>-<companyOrRole>-<YYYYMMDD>`, lowercased and hyphenated.

### 4. Render the PDF
Run:
```
bash scripts/render-pdf.sh artifacts/<slug>/tailored_resume.html artifacts/<slug>/tailored_resume.pdf
```
If it fails (no Chromium installed), tell the user how to install it and stop. Don't try to fake the PDF.

If a profile photo is embedded and the resulting PDF exceeds ~1MB, downscale the in-artifact `pic.<ext>` (e.g. `sips -Z 600 ... -s formatOptions 80`) and re-render. Don't ship a >1MB PDF.

### 5. Validate — ATS check, AI-tell check, page count

Run **both** validators:

```
bash scripts/ats-check.sh   artifacts/<slug>/tailored_resume.pdf profile/jd.md
bash scripts/ai-detect.sh   artifacts/<slug>/tailored_resume.pdf
```

The ATS harness reports:
- Page count (target ≤ 2).
- File size (target ≤ 1MB).
- Whether each JD must-have keyword appears in the extracted PDF text.
- Whether standard section headings (Skills / Experience / Education) are present.

The AI-detect harness reports an "AI-suspicion" score (em-dash density + flagged phrases + triadic-pattern density). **Target < 20 (LOW).**

**If any check fails, iterate**. In order:
1. AI-detect score ≥ 20 → rewrite per `prompts/resume-best-practices.md` → "Sounding human". Replace em-dashes, swap phrase-blacklist words for plain alternatives, vary bullet structure.
2. Missing JD keywords → revisit the profile match; if the user *has* the experience, surface it in a bullet. If not, leave it and note in `changes.md`.
3. Page count > 2 or last page mostly empty → apply density rules from `prompts/resume-best-practices.md` → "Density iteration", re-render, re-check.
4. Standard headings missing → fix the template fill-in.

Re-run **both** validators after each iteration. Stop only when both pass OR you've explained in `changes.md` why a remaining failure is unavoidable (e.g. truthful keyword the user genuinely doesn't have).

### 6. Report
Print, in one short block:
- Path to the four output files.
- Top 3 keyword matches.
- Top 1–2 gaps the user should know about.
- ATS check summary line (passed/failed counts + final page count).
- A single next-step suggestion (e.g., "answer questions.md to strengthen the next pass").

## Rules
- Truth before optimization. Re-read `prompts/resume-best-practices.md` if you feel tempted to invent.
- Never invent metrics. If the profile says "improved productivity" with no number, the bullet stays without a number.
- Don't add features to this command. Stay narrow.
- If the user provides arguments inline (`$ARGUMENTS`), parse them and skip the matching question.

$ARGUMENTS
