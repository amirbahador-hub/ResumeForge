# ResumeForge — Agent instructions

ResumeForge is a **prompts-and-helper-scripts** project. There is no application here. You (the assistant) are the application.

The user opens this repo in any agentic coding CLI — Claude Code, Codex CLI, Gemini CLI, Cursor, Cline, Aider — runs a command, and you do the work end-to-end. This file is the single source of truth for project instructions; per-tool aliases (`CLAUDE.md`, `GEMINI.md`, `.cursorrules`, `.clinerules`) are symlinks to it.

## Start-of-session greeting

The welcome menu is intended to print automatically via a `SessionStart` hook in:
- Claude Code: `.claude/settings.json`
- Codex CLI: `.codex/config.toml`
- Gemini CLI: `.gemini/settings.json`

All three hooks invoke `bash scripts/welcome.sh`, which emits `{"systemMessage": "..."}` — the schema all three CLIs accept.

If the user's first message is a bare greeting or "what can I do here?", and the menu is not already visible in the conversation, run `bash scripts/welcome.sh | jq -r .systemMessage` and show them the menu. This applies especially in Codex, Cursor, Cline, and Aider, where startup hook behavior may be unavailable or inconsistent. If the user's first message already specifies a task, go straight into it regardless of tool.

## Available commands

Four commands are defined as markdown prompts. The canonical source is `.claude/commands/`; per-tool entry points (`.codex/prompts/`, `.gemini/commands/`) point at the same content.

- [`generate-resume`](.claude/commands/generate-resume.md) — tailor a resume to a JD using the master profile and a chosen template.
- [`analyze-job`](.claude/commands/analyze-job.md) — structured fit/gap analysis of a JD against the profile. No resume generated.
- [`cover-letter`](.claude/commands/cover-letter.md) — draft a tailored cover letter from the profile + a JD.
- [`update-profile`](.claude/commands/update-profile.md) — interactively edit `profile/profile.yaml`.

How users invoke them, per tool:

| Tool         | Invocation                              |
|--------------|------------------------------------------|
| Claude Code  | `/generate-resume <args>`                |
| Codex CLI    | `/generate-resume <args>`                |
| Gemini CLI   | `/generate-resume <args>`                |
| Cursor / Cline / Aider | Ask in chat: "run generate-resume with …" — the agent reads `.claude/commands/generate-resume.md` and follows it. |

When invoked without a built-in slash-command system, read the matching markdown file in `.claude/commands/` and execute it literally. The instructions inside are the spec.

## Shared prompt fragments (read before generating)

Every command depends on these. They are non-negotiable rules, not suggestions.

- [`prompts/resume-best-practices.md`](prompts/resume-best-practices.md)
- [`prompts/ats-rules.md`](prompts/ats-rules.md)
- [`prompts/recruiter-signals.md`](prompts/recruiter-signals.md)

## Repo map

- `profile/profile.yaml` — the user's master profile. The **only** source of truth for any claim on a tailored resume.
- `prompts/` — shared reference material every command relies on (linked above).
- `.claude/commands/` — canonical command specs (markdown).
- `.codex/prompts/` — symlinks into `.claude/commands/` for Codex CLI.
- `.gemini/commands/` — thin TOML wrappers that re-use the same canonical specs for Gemini CLI.
- `templates/` — HTML+CSS resume layouts. Each has Jinja2-style placeholders. You fill them in by hand.
- `scripts/` — small helpers:
  - `render-pdf.sh` — converts an HTML file to PDF. Prefers Playwright (`pip install playwright && playwright install chromium`); falls back to any Chrome/Chromium on `$PATH`.
  - `render-pdf.py` — Playwright backend invoked by `render-pdf.sh`.
  - `list-templates.sh` — prints available templates; tags `[photo]` ones that need a profile picture.
  - `find-photo.sh` — prints the path to the user's profile photo (`profile/pic.<ext>`) if one exists.
  - `welcome.sh` — emits the welcome menu (JSON, `systemMessage` field).
- `examples/` — the user's prior resume and example job descriptions for reference.
- `artifacts/` — where you write tailored resumes, cover letters, analyses. Gitignored.

## Hard rules

1. **Truth before optimization.** Every claim on a tailored resume must trace to `profile/profile.yaml`. If it isn't in the profile, ask the user — don't invent.
2. **Never invent metrics.** Numbers come from the profile or they don't appear.
3. **Read the prompt fragments before generating.** `prompts/*.md` are non-negotiable rules.
4. **No new code.** This repo is intentionally code-free. If you find yourself wanting to write Python, stop and use a prompt or a tiny shell helper instead.
5. **Outputs go to `artifacts/<slug>/`.** Slug format: `<lastname-or-company>-<context>-<YYYYMMDD>`, lowercased and hyphenated.

## Conventions

- Markdown for human-readable outputs. HTML+CSS for the rendered resume. PDF as the final artifact.
- When a command needs an input the user didn't provide, ask for it conversationally — one question at a time.
- When confidence is low or evidence is missing, write a `questions.md` and surface it. Don't silently guess.
- Keep templates' visual design intact when filling them in. Don't restyle.
- Argument placeholder note: the canonical command files use `$ARGUMENTS` (Claude Code and Codex syntax). Gemini wrappers translate this to `{{args}}` automatically. In tools without slash-command argument substitution, treat whatever the user typed after the command name as `$ARGUMENTS`.

## Profile photo

Some templates (tagged `[photo]` in `scripts/list-templates.sh`) include a headshot. The user places their photo at `profile/pic.<ext>` — jpg, jpeg, png, or webp. The `profile/` directory is gitignored, so the photo never leaves the user's machine.

When filling a photo template, the agent must:
1. Run `bash scripts/find-photo.sh` to locate the photo (or confirm none exists).
2. Copy the photo into `artifacts/<slug>/` next to `tailored_resume.html`.
3. Substitute `{{ content.photo }}` with the photo's filename (relative path).

If the chosen template needs a photo and none is found, ask the user before continuing — never strip the photo silently.

## Adding a new template

Drop a folder under `templates/<id>/` with `index.html` and `style.css`. Add an entry to `templates/manifest.json` with `id`, `name`, `description`, and `needs_photo` (boolean). That's it — no code changes needed.

## Adding or editing a command

Edit the markdown in `.claude/commands/<name>.md` — that's the canonical spec. Codex picks it up via symlink automatically. For Gemini, if you add a *new* command, also create `.gemini/commands/<name>.toml` using the existing wrappers as a template.
