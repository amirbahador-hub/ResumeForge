---
description: Analyze a job description against the master profile — fit, gaps, and tailoring strategy.
---

You are running the `/analyze-job` command for ResumeForge.

This command produces a written analysis. It does NOT generate a resume. Use `/generate-resume` for that.

## Inputs
1. **Job description** — path, URL, or pasted text. Required.
2. (Optional) Recruiter notes — any LinkedIn message, company blurb, or context the user has.

## Sources to read
- `profile/profile.yaml`
- `prompts/recruiter-signals.md`
- `prompts/resume-best-practices.md`

## Output

Write the analysis to `artifacts/<slug>/job-analysis.md` where slug is `<companyOrRole>-<YYYYMMDD>`, lowercased.

Structure the file exactly like this:

```markdown
# Job analysis: <Role> @ <Company>

## Role at a glance
- Seniority: <IC / Senior / Staff / Lead / Manager>
- Scope signal: <team / org / system size as inferred>
- Domain: <industry / problem space>
- Location / on-site requirement: <…>
- Hard constraints: <work auth, languages, on-call, etc.>

## What they actually want (ranked)
1. <…>
2. <…>
…

## Stack
- Must-have: <list>
- Nice-to-have: <list>
- Mentioned but probably non-blocking: <list>

## Keywords worth surfacing verbatim
<5–10 phrases pulled from the JD>

## Fit vs profile
| Requirement | Evidence in profile | Strength |
| --- | --- | --- |
| … | … | strong / weak / missing |

## Gaps to address
- <gap>: <how to close it — add to profile, address in cover letter, or accept>
- …

## Tailoring strategy
- Lead with: <which role, which bullets>
- Reorder skills as: <ordered list>
- Drop from resume: <which bullets/skills>
- Summary line (if used): <draft a 2-3 line summary>

## Recruiter-first-pass score (1-5)
<number> — <one-sentence rationale>

## Next step
Run `/generate-resume` with template <recommended template> once you've answered:
- <open questions, if any>
```

## Rules
- Be specific. Generic analyses are useless.
- If the JD is missing crucial info (location, comp range, team size), say so explicitly under "Hard constraints" instead of guessing.
- Don't pretend the candidate has experience they don't. Mark it as a real gap.

$ARGUMENTS
