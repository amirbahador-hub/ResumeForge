# Resume best practices

Apply these whenever generating a tailored resume.

## Truthfulness (non-negotiable)
- Every claim must be traceable to `profile/profile.yaml`. If it's not there, do not put it on the resume.
- Do not fabricate metrics. If a metric isn't in the profile, write the bullet without one rather than inventing a number.
- If you reframe a bullet to match the JD, the underlying activity must still be something the candidate actually did.
- When in doubt, ask the user a follow-up question instead of guessing.

## Signal density
- Each bullet: ~1 line, 14–24 words. Two lines max only when unavoidable.
- Lead with the verb of impact, not the technology. "Cut deploy time 30% by …" beats "Used X to …".
- One concrete object per bullet (system, service, dataset, team). No bullets that describe a vibe.
- Keep the bullet specific enough that a strong interviewer could write a follow-up question from it.

## JD alignment
- Mirror the JD's exact phrasing for stack and responsibilities *when the candidate genuinely has the experience*.
- Hit the JD's must-have keywords in the Skills section AND surface them naturally in 1–2 bullets each.
- Reorder experience bullets so the JD-relevant work sits at the top of each role.
- Drop bullets that have no signal for this role. A focused resume beats a complete one.

## Skills density (the "wall of chips" anti-pattern)
- **Target 12–18 skill items total.** A 30+ chip list looks unfocused — recruiters and ATS both penalize it. The cap also forces ranking.
- Every chip must be: (a) directly relevant to *this* JD, (b) defensible in interview, (c) backed by a bullet, project, or role.
- When in doubt, drop. Two strong, defensible skills beat five generic ones.
- Order chips by JD relevance, not alphabetically. The first ~5 chips are scanned hardest — put the JD's must-haves there.
- Don't list both a language and its sub-frameworks unless both are JD-keywords (e.g. drop `asyncio` when you list `Python` + `FastAPI` already).

## Seniority signal
- For senior+ roles, show: scope (team size, system size, blast radius), architecture decisions, leadership, mentoring, incident ownership.
- For IC roles, show: depth (gnarly bugs, perf work, design tradeoffs), shipped features, ownership.
- Avoid bullets that sound like a junior wrote them ("learned X", "helped with Y", "assisted in Z").

## Verbs and voice
- Past tense for past roles, present tense for current.
- Strong, specific verbs: built, shipped, led, migrated, scaled, designed, cut, eliminated.
- Avoid: helped, assisted, worked on, was responsible for, utilized (just say "used"), leveraged.
- No first person ("I", "my"). No articles ("a", "the") at the start of bullets when avoidable.

## Sounding human (avoid AI-detector flags)
Many ATS and recruiter tools now run resumes through GPT-detectors and can silently reject anything that "reads like AI". The cheap heuristics those tools use are well known — write around them on purpose.

**Em-dash diet.** LLM output is full of `—`. Humans rarely use more than ~1 per 100 words. Aim for **5 or fewer em-dashes total** across the whole resume. Replace with periods, colons, commas, parentheses, or middle dot `·` where structurally useful. Date ranges (`05/2024 – Present`) can keep their en-dash; that's resume convention and detectors expect it.

**Phrase blacklist.** Never use, regardless of how natural it feels:
*delve, tapestry, intricate, harness the power, leverage / leveraging (as a verb), seamless / seamlessly, robust, comprehensive, holistic, ecosystem, end-to-end, multifaceted, cutting-edge, state-of-the-art, plethora, myriad, foster (as a verb), navigate (as a metaphor), embark, in essence, in conclusion, furthermore, moreover, in today's fast-paced world.*

If a meaning needs to be expressed, find a plainer word: "leverage" → "use"; "robust" → "stable" or just drop it; "comprehensive" → "complete" or "full"; "ecosystem" → name the actual thing (toolchain, platform, stack).

**Vary structure.** Bullets shouldn't all start with verb-noun-noun. Mix in some that lead with object or scope. Vary length — 12-word bullets next to 22-word ones reads more human than 6 in a row of identical shape.

**Triadic restraint.** "X, Y, and Z" is fine occasionally but detectors flag dense parallelism. Don't string three triadic bullets in a row.

**Validate.** After rendering, run `scripts/ai-detect.sh artifacts/<slug>/tailored_resume.pdf`. Target score < 20 (LOW). Iterate if higher.

## Story line per role (the "situation" line)
- Under each role's title/company/dates and **before** the bullets, write ONE short narrative line — the situation, scope, or context of the role.
- ≤ 22 words. Sets up the bullets so each one lands harder. Not a duplicate of the bullets — a frame for them.
- Use the profile's `context:` field as the seed when present. Tailor it to the JD's framing (e.g. "AI/ML platform", "logistics", "high-scale crawl").
- Format: italic, muted color. In Markdown, write it on its own line as `*<sentence>*` directly after the role header. In HTML templates, use a `.role-story` (or template-equivalent) class.

## Keyword bolding
- Inside bullets, bold the JD's important nouns — technologies, tools, named systems, frameworks. In Markdown use `**word**`; in HTML wrap in `<strong>`.
- 1–3 bolded terms per bullet is the sweet spot. More than that and nothing stands out.
- Bold real things only: product names, stack items, named methodologies. Don't bold generic verbs ("**built**"), seniority words, or filler.
- **Render bold as plain black bold**, not in an accent color. Color-on-bold double-marks the word and looks decorative; recruiters prefer plain bold black.
- The Skills chips are already visually distinct — no need to bold inside them.

## Layout discipline
- **Target 2 pages.** One page if total experience is < ~6 years; two pages for 6–12 years; **never three**.
- A "page 3 with only a few lines on it" is a failure — tighten font/spacing or trim bullets until the resume fits cleanly in 2 pages. The last page should be at least ~60% full, or it doesn't earn its existence.
- Reverse-chronological. No functional resumes.
- Section order for tech roles: Header → Summary (optional, ≤ 3 lines) → Skills → Experience → Projects → Education → Languages.
- Dates as `MM/YYYY – MM/YYYY` or `MM/YYYY – Present`.
- Consistent punctuation. Either every bullet ends with a period, or none do.

## Density iteration
- After rendering, count pages. If page count > 2 (or last page < 60% full), iterate:
  1. First, trim the lowest-signal bullets (older roles, weakest JD overlap).
  2. Then condense Projects / Open Source entries to one line each.
  3. Then drop the summary if it's not adding signal.
  4. Only after content trimming, consider tightening CSS (smaller font, smaller margins) — and only on the artifact's CSS copy, never on the canonical template.

## Summary line (if used)
- Three lines max. Role + years + 2 superpowers + domain.
- Tailored to the JD. Generic summaries dilute everything below them.
- Skip the summary entirely if you can't make it sharper than the rest of the resume.
