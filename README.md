# ResumeForge

Tailor your resume to any job description, using an AI coding assistant you already have.

There's no app to install and no Python package to set up. ResumeForge is a folder of prompts, a structured profile, and a few small scripts. You open the folder in an AI CLI (Claude Code, Codex CLI, Gemini CLI, Cursor, Cline, or Aider), point it at a job description, and it produces a tailored Markdown resume, an HTML version, and a final PDF — all in `artifacts/`.

## Quick start

1. **Clone the repo** and `cd` into it.

   ```sh
   git clone <this-repo> && cd ResumeForge
   ```

2. **Install the PDF renderer** (one-time, ~150 MB):

   ```sh
   pip install playwright
   playwright install chromium
   ```

   Playwright bundles its own browser, so this works on macOS, Linux, and Windows without needing Chrome installed. If you already have Chrome or Chromium on your `PATH`, ResumeForge will use it as a fallback.

3. **Fill in your profile.** Open `profile/profile.yaml` and edit it so it accurately describes your real experience. This file is the single source of truth — anything not in it will not show up on the generated resume.

4. **(Optional) Add a headshot.** If you want to use a photo template, drop your picture at `profile/pic.jpg` (or `.jpeg` / `.png` / `.webp`). The `profile/` folder is gitignored, so the file stays on your machine.

5. **Open the folder in your CLI** and run:

   ```
   /generate-resume
   ```

   The assistant will ask for the job description, let you pick a template, and produce everything in `artifacts/<slug>/`:

   - `tailored_resume.md` — markdown
   - `tailored_resume.html` — styled HTML
   - `tailored_resume.pdf` — final PDF
   - `changes.md` — what was reordered, reworded, or dropped
   - `questions.md` — any gaps the assistant wants you to confirm

## Commands

| Command | What it does |
| --- | --- |
| `/generate-resume` | Tailors a resume to a job description. Outputs MD + HTML + PDF + a changes/questions writeup. |
| `/analyze-job` | Fit-and-gap analysis of a JD against your profile. No resume is generated. |
| `/cover-letter` | Drafts a cover letter from your profile + a JD. |
| `/update-profile` | Interactively edits `profile/profile.yaml` (add a role, update skills, etc). |

In Cursor, Cline, or Aider — where slash commands aren't built in — just ask in chat: *"run generate-resume with the JD at ./jd.md"*. The assistant will read the matching spec from `.claude/commands/` and follow it.

## Templates

Run `bash scripts/list-templates.sh` to see what's available. Templates tagged `[photo]` need a headshot at `profile/pic.<ext>`.

| Template | Photo? | Style |
| --- | --- | --- |
| `classic-clean` | no | Centered header, single-column flow. |
| `editorial-compact` | no | Left-aligned header, compact typography. |
| `modern-line` | no | Minimal ATS-safe layout with thin rules. |
| `portrait` | **yes** | Circular headshot, stacked name, teal accents. |
| `portrait-noir` | **yes** | Same layout as Portrait, black-and-red palette. |

To **add a new template**, drop a folder under `templates/<id>/` with `index.html` and `style.css`, and add an entry to `templates/manifest.json` (with `needs_photo: true|false`). No code changes needed.

## Supported AI CLIs

| CLI | How it reads instructions | How to invoke a command |
| --- | --- | --- |
| Claude Code | `CLAUDE.md` (→ `AGENTS.md`) | `/generate-resume` |
| Codex CLI | `AGENTS.md` | `/generate-resume` |
| Gemini CLI | `GEMINI.md` (→ `AGENTS.md`) | `/generate-resume` |
| Cursor | `.cursorrules` (→ `AGENTS.md`) | Ask in chat |
| Cline | `.clinerules` (→ `AGENTS.md`) | Ask in chat |
| Aider | `CONVENTIONS.md` (→ `AGENTS.md`) | Ask in chat |

`AGENTS.md` is the canonical instructions file; every other root file is a symlink to it.

## How your data stays private

- `profile/` is gitignored — your YAML profile and photo never get committed.
- `artifacts/` is gitignored — generated resumes never get committed.
- No data leaves your machine except via your AI CLI's own API calls, which you control.

## Principles

- **Truth before optimization.** Every claim on a tailored resume must trace to `profile/profile.yaml`.
- **Never invent metrics.** If a number isn't in the profile, the bullet ships without one.
- **Prompts as code.** All behavior lives in `.claude/commands/` and `prompts/`. Edit them like you'd edit source.
- **No app.** The AI is the runtime. Nothing to install except the optional PDF renderer.

## Troubleshooting

- **PDF rendering fails** — run `pip install playwright && playwright install chromium`. Or install Chrome/Chromium and make sure it's on your `$PATH`.
- **Photo doesn't show up** — make sure the file is at `profile/pic.JPG` (or `.jpg`, `.jpeg`, `.png`, `.webp`) and that you picked a `[photo]` template.
- **The assistant invented something** — open an issue. Re-running with a fuller `profile/profile.yaml` is the usual fix.

## License

MIT
