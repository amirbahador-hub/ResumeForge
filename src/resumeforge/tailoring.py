from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from resumeforge.pipeline import ResumeForgePipeline
from resumeforge.providers import (
    EducationEntry,
    ExperienceEntry,
    LanguageEntry,
    LLMTailoringClient,
    ProjectEntry,
    ProviderConfig,
    ResumeContact,
    ResumeLink,
    SkillGroup,
    TailoredResumeContent,
    TailoringChange,
    TailoringResult,
)
from resumeforge.rendering import render_resume_pdf
from resumeforge.resume_templates import TEMPLATE_CATALOG, ResumeTemplateSpec, get_template
from resumeforge.schemas import PipelineResult, UserInput
from resumeforge.yaml_io import dump_yaml, write_yaml


@dataclass
class TailoringSummary:
    baseline_report: PipelineResult
    tailored_report: PipelineResult
    tailoring: TailoringResult
    tailored_pdf: Path
    tailored_markdown: Path
    changes_report: Path
    questions_report: Path
    template: ResumeTemplateSpec


@dataclass
class QuestionMemory:
    asked: set[str]
    answered: dict[str, str]
    skipped: set[str]
    finished: bool = False


async def tailor_resume(
    user_input: UserInput,
    output_dir: Path,
    provider_config: ProviderConfig,
    template_id: str | None = None,
) -> TailoringSummary:
    output_dir.mkdir(parents=True, exist_ok=True)
    baseline = await ResumeForgePipeline(artifact_dir=output_dir / "artifacts" / "baseline").run(
        user_input
    )
    tailoring = await _run_tailoring_or_fallback(baseline, provider_config)
    if tailoring.questions_for_user:
        tailoring = await _interactive_refine_tailoring(
            baseline,
            provider_config,
            tailoring,
            tailoring.questions_for_user,
            output_dir,
        )
    template = _select_template(template_id)
    tailored_markdown_text = content_to_markdown(tailoring.content)
    tailored_markdown = output_dir / "tailored_resume.md"
    changes_report = output_dir / "changes.md"
    questions_report = output_dir / "questions.md"
    tailored_markdown.write_text(tailored_markdown_text + "\n", encoding="utf-8")
    (output_dir / "tailored_resume.json").write_text(
        json.dumps(tailoring.content.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )
    await render_resume_pdf(
        output_dir / "tailored_resume.pdf",
        tailoring.content,
        template,
    )
    write_tailoring_outputs(output_dir, baseline, tailoring, provider_config)
    tailored_input = UserInput(
        job_description=user_input.job_description,
        resume=tailored_markdown_text,
        recruiter_name=user_input.recruiter_name,
        recruiter_profile=user_input.recruiter_profile,
        recruiter_posts=user_input.recruiter_posts,
        company_name=user_input.company_name,
        company_context=user_input.company_context,
        github=user_input.github,
        linkedin=user_input.linkedin,
        portfolio=user_input.portfolio,
        projects=user_input.projects,
        constraints=user_input.constraints,
    )
    tailored_report = await ResumeForgePipeline(
        artifact_dir=output_dir / "artifacts" / "tailored"
    ).run(tailored_input)
    return TailoringSummary(
        baseline_report=baseline,
        tailored_report=tailored_report,
        tailoring=tailoring,
        tailored_pdf=output_dir / "tailored_resume.pdf",
        tailored_markdown=tailored_markdown,
        changes_report=changes_report,
        questions_report=questions_report,
        template=template,
    )


async def _run_tailoring_or_fallback(
    result: PipelineResult,
    provider_config: ProviderConfig,
    answers: dict[str, str] | None = None,
    history: dict[str, str] | None = None,
) -> TailoringResult:
    if provider_config.provider == "none":
        return _fallback_tailoring(
            result,
            "No provider configured; used deterministic fallback.",
            answers,
        )

    prompt = _build_tailoring_prompt(result, answers, history)
    try:
        client = LLMTailoringClient(provider_config.provider, provider_config.model)
        return await client.tailor(prompt)
    except Exception as exc:
        return _fallback_tailoring(
            result,
            f"Provider call failed; used fallback: {exc}",
            answers,
        )


async def _interactive_refine_tailoring(
    result: PipelineResult,
    provider_config: ProviderConfig,
    initial_tailoring: TailoringResult,
    questions: list[str],
    output_dir: Path,
) -> TailoringResult:
    console = Console()
    memory = QuestionMemory(asked=set(), answered={}, skipped=set())
    current_questions = _filter_new_questions(questions, memory.asked)
    current_result = initial_tailoring
    for _round in range(10):
        if not current_questions or memory.finished:
            break
        answers: dict[str, str] = {}
        for question in current_questions:
            answer, finished = _prompt_multiline_answer(console, question)
            memory.asked.add(_question_key(question))
            if finished:
                memory.finished = True
                break
            if answer:
                answers[question] = answer.strip()
                memory.answered[question] = answer.strip()
            else:
                memory.skipped.add(question)
        if answers:
            current_result = await _run_tailoring_or_fallback(
                result,
                provider_config,
                answers,
                memory.answered,
            )
        if memory.finished:
            break
        next_questions = _filter_new_questions(
            current_result.questions_for_user,
            memory.asked,
        )
        if not next_questions or next_questions == current_questions:
            break
        current_questions = next_questions
        (output_dir / "questions_followup.md").write_text(
            _questions_markdown(current_result),
            encoding="utf-8",
        )
    return current_result


def write_tailoring_outputs(
    output_dir: Path,
    result: PipelineResult,
    tailoring: TailoringResult,
    provider_config: ProviderConfig,
) -> None:
    (output_dir / "changes.md").write_text(
        _changes_markdown(tailoring, provider_config),
        encoding="utf-8",
    )
    (output_dir / "questions.md").write_text(
        _questions_markdown(tailoring),
        encoding="utf-8",
    )
    write_yaml(output_dir / "resume_strategy.yaml", result.resume_strategy)
    write_yaml(output_dir / "ats_report.yaml", result.ats_report)
    write_yaml(output_dir / "truthfulness_report.yaml", result.truthfulness_report)
    (output_dir / "optimization_report.yaml").write_text(
        dump_yaml(result.optimization_report),
        encoding="utf-8",
    )


_CONTENT_SCHEMA_HINT = """{
  "content": {
    "name": "Full Name",
    "headline": "Target Role · Seniority",
    "contact": {
      "email": "user@example.com",
      "phone": "+00 000 000",
      "location": "City, Country",
      "links": [
        {"label": "linkedin.com/in/handle", "url": "https://linkedin.com/in/handle"},
        {"label": "github.com/handle", "url": "https://github.com/handle"}
      ]
    },
    "summary": "Tight 3-4 sentence positioning paragraph.",
    "skill_groups": [
      {"label": "Languages", "items": ["Python", "Go"]}
    ],
    "experience": [
      {
        "role": "Senior Software Engineer",
        "company": "Company",
        "location": "City, Country",
        "dates": "2023-08 – 2024-02",
        "bullets": ["Plain-text bullet, no markdown asterisks or links."]
      }
    ],
    "projects": [
      {
        "name": "ProjectName",
        "description": "One-line tagline.",
        "url": "https://github.com/handle/Project",
        "bullets": []
      }
    ],
    "open_source": [],
    "education": [
      {"degree": "B.Sc. Computer Engineering", "institution": "University", "dates": "", "details": ""}
    ],
    "languages": [
      {"name": "English", "proficiency": "Full Professional"}
    ],
    "extra_sections": [
      {"heading": "Content & Community", "items": ["YouTube: youtube.com/@channel"]}
    ]
  },
  "changed_items": [
    {"section": "Summary", "before": "...", "after": "...", "why": "...", "evidence": "..."}
  ],
  "questions_for_user": ["Specific gap questions, or empty if confident."],
  "risks_or_assumptions": ["Items that need user confirmation."]
}"""


def _build_tailoring_prompt(
    result: PipelineResult,
    answers: dict[str, str] | None = None,
    history: dict[str, str] | None = None,
) -> str:
    answers_block = ""
    if answers:
        answers_block = "\nUSER ANSWERS:\n" + "\n".join(
            f"- {question}: {answer}" for question, answer in answers.items()
        )
    history_block = ""
    if history:
        history_block = "\nQUESTION HISTORY:\n" + "\n".join(
            f"- {question}: {answer}" for question, answer in history.items()
        )
    return f"""
You are tailoring a resume aggressively for a specific job description. The output must read
as if it was written for THIS role — not as a generic engineering resume. Reframe everything
through the lens of what this employer actually cares about, while staying strictly truthful.

Return valid JSON with this exact shape:
{_CONTENT_SCHEMA_HINT}

REWRITING RULES (apply to every bullet, the summary, the headline, and project descriptions):
1. SUMMARY: 3–4 sentences. Use the JD's own vocabulary for the role, the team's mission, and
   the must-have signals. Open with the candidate's positioning in JD terms, not a generic
   "Senior engineer with X years" intro. Do not pad.
2. EVERY EXPERIENCE BULLET must be rewritten — not copy-pasted from the source. Lead each
   bullet with a strong action verb aligned to the JD (e.g. if JD asks for "advocate /
   demo / enable / partner / advise", prefer verbs in that register over generic
   "Implemented / Built"). If a bullet from the source has no plausible JD relevance,
   either reframe it toward a transferable signal or drop it.
3. PROJECT DESCRIPTIONS: Reframe each project's one-line description to surface why it
   matters to THIS job (e.g. "high-signal demo of agentic context engineering" beats
   "AI-native context engineering system"). Add 1–2 bullets per project only when truthful
   and JD-relevant; otherwise leave bullets empty.
4. SKILL GROUPS: Reorder so the most JD-aligned group is first. Drop skill items that are
   irrelevant to this JD even if they were in the source resume.
5. HEADLINE: Set to the JD's exact role title when reasonable (e.g. "AI Deployment Engineer
   · Senior Software Engineer"), so ATS sees the alignment.
6. Use the JD's domain phrases verbatim where the candidate's evidence supports them
   (e.g. "customer-facing technical enablement", "AI coding tool power user",
   "Codex / agentic workflows"). Never claim a phrase the source resume cannot back.

TRUTHFULNESS RULES (override all rewriting rules):
- Do not invent employers, dates, projects, metrics, education, titles, tools, or skills.
- If a relevant role requirement is not evidenced, do not claim it. Ask a question instead.
- Do not place unconfirmed skills in the resume body, even with qualifiers like "see questions".
- Missing skills and uncertain claims belong only in questions_for_user or risks_or_assumptions.
- Numbers and percentages in the source resume can be kept; do not invent new metrics.

FORMAT RULES:
- Bullets are plain text. No Markdown syntax (no **bold**, no *italic*, no [text](url)).
- Hyperlinks go in contact.links or project.url fields only, never inside bullets/summary.
- Group skills semantically (Languages, Frameworks, Infrastructure, etc).
- Explain every meaningful rewrite in changed_items with concrete before/after text.

JOB DESCRIPTION:
{result.normalized_context.job_description}

SOURCE RESUME TEXT:
{result.normalized_context.resume}

ROLE ANALYSIS YAML:
{dump_yaml(result.role_analysis)}

RESUME ANALYSIS YAML:
{dump_yaml(result.resume_analysis)}

ATS REPORT YAML:
{dump_yaml(result.ats_report)}

STRATEGY YAML:
{dump_yaml(result.resume_strategy)}
{answers_block}
{history_block}
""".strip()


def _fallback_tailoring(
    result: PipelineResult,
    reason: str,
    answers: dict[str, str] | None = None,
) -> TailoringResult:
    content = parse_markdown_to_content(result.normalized_context.resume)
    if not content.summary:
        strengths = ", ".join(result.resume_analysis.technical_strengths[:6])
        content = content.model_copy(
            update={
                "summary": (
                    "Senior engineer with experience across " + strengths
                    if strengths
                    else "Senior engineer."
                )
            }
        )
    changes = [
        TailoringChange(
            section="Summary",
            before="No targeted summary generated by source resume parser.",
            after="Added a role-targeted technical summary based on evidenced skills.",
            why="The job description should see role alignment immediately.",
            evidence=", ".join(result.resume_analysis.technical_strengths[:6]) or "source resume",
        ),
        TailoringChange(
            section="Priority Signals",
            before="Role-relevant signals were distributed across the resume.",
            after="Added priority signal ordering for the target role.",
            why="Recruiters and ATS systems benefit from explicit, truthful role-relevant signal.",
            evidence=", ".join(result.resume_strategy.priority_signals[:8]) or "role analysis",
        ),
    ]
    questions = [
        f"Can you provide concrete evidence for {signal}?"
        for signal in result.resume_strategy.missing_signals[:6]
    ]
    if answers:
        questions = []
    return TailoringResult(
        content=content,
        changed_items=changes,
        questions_for_user=questions,
        risks_or_assumptions=[reason, *result.truthfulness_report.interview_risks],
    )


def _changes_markdown(tailoring: TailoringResult, provider_config: ProviderConfig) -> str:
    lines = [
        "# What Changed and Why",
        "",
        f"Provider: {provider_config.provider}",
    ]
    if provider_config.model:
        lines.append(f"Model: {provider_config.model}")
    lines.append("")
    for index, item in enumerate(tailoring.changed_items, start=1):
        lines.extend(
            [
                f"## {index}. {item.section}",
                "",
                f"Before: {item.before or 'Not present / not directly preserved.'}",
                "",
                f"After: {item.after}",
                "",
                f"Why: {item.why}",
                "",
                f"Evidence: {item.evidence}",
                "",
            ]
        )
    if tailoring.risks_or_assumptions:
        lines.extend(["# Risks or Assumptions", ""])
        lines.extend(f"- {item}" for item in tailoring.risks_or_assumptions)
        lines.append("")
    return "\n".join(lines)


def _questions_markdown(tailoring: TailoringResult) -> str:
    lines = ["# Follow-Up Questions", ""]
    if not tailoring.questions_for_user:
        lines.append("No follow-up questions generated.")
    else:
        lines.extend(f"- {question}" for question in tailoring.questions_for_user)
    lines.append("")
    return "\n".join(lines)


def _prompt_multiline_answer(console: Console, question: str) -> tuple[str, bool]:
    console.print()
    console.print(
        Panel(
            Text(question, style="bold white"),
            title="Follow-up Question",
            border_style="cyan",
        )
    )
    console.print(
        "[dim]Paste a multi-line answer if needed. Finish with a line containing[/dim] "
        "[bold]/done[/bold][dim]. Use[/dim] [bold]/skip[/bold][dim] to leave it blank.[/dim]"
    )
    lines: list[str] = []
    while True:
        line = console.input("[cyan]>[/cyan] ")
        stripped = line.strip()
        if stripped == "/finish":
            return "\n".join(lines).strip(), True
        if not lines and stripped == "/skip":
            return "", False
        if stripped == "/done":
            return "\n".join(lines).strip(), False
        lines.append(line)


def _question_key(question: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", question.lower()).strip()


def _filter_new_questions(questions: list[str], asked: set[str]) -> list[str]:
    seen = set(asked)
    fresh: list[str] = []
    for question in questions:
        key = _question_key(question)
        if key in seen:
            continue
        seen.add(key)
        fresh.append(question)
    return fresh


def _select_template(template_id: str | None) -> ResumeTemplateSpec:
    if template_id:
        return get_template(template_id)
    return _prompt_template_selection()


def _prompt_template_selection() -> ResumeTemplateSpec:
    console = Console()
    table = Table(title="Resume Templates", header_style="bold magenta")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Template", style="white")
    table.add_column("Local file", style="green")
    table.add_column("Why it fits", style="white")
    for index, template in enumerate(TEMPLATE_CATALOG, start=1):
        table.add_row(
            str(index),
            template.display_name,
            template.asset_dir,
            template.description,
        )
    console.print(table)
    while True:
        choice = console.input("[cyan]Choose a template number[/cyan] ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(TEMPLATE_CATALOG):
                return TEMPLATE_CATALOG[index - 1]
        console.print("[red]Invalid selection. Enter 1, 2, or 3.[/red]")


def content_to_markdown(content: TailoredResumeContent) -> str:
    """Render structured content as ATS-friendly Markdown for downstream pipeline analysis."""
    lines: list[str] = [f"# {content.name}"]
    if content.headline:
        lines.append(f"**{content.headline}**")
    contact_bits: list[str] = []
    if content.contact.email:
        contact_bits.append(content.contact.email)
    if content.contact.phone:
        contact_bits.append(content.contact.phone)
    if content.contact.location:
        contact_bits.append(content.contact.location)
    if contact_bits:
        lines.append(" · ".join(contact_bits))
    if content.contact.links:
        lines.append(
            " · ".join(f"[{link.label}]({link.url})" for link in content.contact.links)
        )
    lines.append("")

    if content.summary:
        lines.extend(["## Summary", "", content.summary, ""])

    if content.skill_groups:
        lines.append("## Skills")
        lines.append("")
        for group in content.skill_groups:
            lines.append(f"**{group.label}:** {', '.join(group.items)}")
        lines.append("")

    if content.experience:
        lines.append("## Experience")
        lines.append("")
        for job in content.experience:
            header = f"### {job.role} — {job.company}"
            lines.append(header)
            meta_bits = [bit for bit in (job.dates, job.location) if bit]
            if meta_bits:
                lines.append(f"*{' · '.join(meta_bits)}*")
            lines.extend(f"- {bullet}" for bullet in job.bullets)
            lines.append("")

    if content.projects:
        lines.append("## Projects")
        lines.append("")
        for project in content.projects:
            line = f"**{project.name}**"
            if project.description:
                line += f" — {project.description}"
            if project.url:
                line += f" ({project.url})"
            lines.append(line)
            lines.extend(f"- {bullet}" for bullet in project.bullets)
            lines.append("")

    if content.open_source:
        lines.append("## Open Source")
        lines.append("")
        for project in content.open_source:
            line = f"**{project.name}**"
            if project.description:
                line += f" — {project.description}"
            if project.url:
                line += f" ({project.url})"
            lines.append(line)
            lines.extend(f"- {bullet}" for bullet in project.bullets)
            lines.append("")

    if content.education:
        lines.append("## Education")
        lines.append("")
        for entry in content.education:
            parts = [entry.degree]
            if entry.institution:
                parts.append(entry.institution)
            line = " — ".join(parts)
            if entry.dates:
                line += f" ({entry.dates})"
            lines.append(f"**{line}**")
            if entry.details:
                lines.append(entry.details)
        lines.append("")

    if content.languages:
        lines.append("## Languages")
        lines.append("")
        for lang in content.languages:
            label = lang.name
            if lang.proficiency:
                label += f" — {lang.proficiency}"
            lines.append(f"- {label}")
        lines.append("")

    for section in content.extra_sections:
        lines.append(f"## {section.heading}")
        lines.append("")
        lines.extend(f"- {item}" for item in section.items)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


_HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD_LEADING_RE = re.compile(r"^\*\*([^*]+):\*\*\s*(.*)$")


def parse_markdown_to_content(markdown_text: str) -> TailoredResumeContent:
    """Best-effort markdown → structured content for the fallback path."""
    lines = [line.rstrip() for line in markdown_text.splitlines()]
    idx = 0
    name = ""
    headline = ""
    contact = ResumeContact()

    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx < len(lines):
        match = _HEADING_RE.match(lines[idx])
        if match and len(match.group(1)) == 1:
            name = match.group(2).strip()
            idx += 1

    if idx < len(lines):
        bold_match = re.match(r"^\*\*(.+?)\*\*\s*$", lines[idx].strip())
        if bold_match:
            headline = bold_match.group(1).strip()
            idx += 1

    contact_lines: list[str] = []
    while idx < len(lines):
        text = lines[idx].strip()
        if not text:
            idx += 1
            if contact_lines:
                break
            continue
        if _HEADING_RE.match(text):
            break
        contact_lines.append(text)
        idx += 1
    if contact_lines:
        contact = _parse_contact_lines(contact_lines)

    extras: list[tuple[str, list[str]]] = []
    current_heading = None
    current_block: list[str] = []
    while idx < len(lines):
        text = lines[idx]
        heading_match = _HEADING_RE.match(text.strip())
        if heading_match and len(heading_match.group(1)) == 2:
            if current_heading is not None:
                extras.append((current_heading, current_block))
            current_heading = heading_match.group(2).strip()
            current_block = []
        else:
            if current_heading is not None:
                current_block.append(text)
        idx += 1
    if current_heading is not None:
        extras.append((current_heading, current_block))

    content = TailoredResumeContent(
        name=name or "Candidate",
        headline=headline,
        contact=contact,
    )
    summary_parts: list[str] = []
    extra_sections = []
    for heading, block in extras:
        body = "\n".join(line for line in block).strip()
        if heading.lower() == "summary":
            summary_parts.append(re.sub(r"\s+", " ", body))
        elif body:
            extra_sections.append({"heading": heading, "items": [body]})
    if summary_parts:
        content = content.model_copy(update={"summary": " ".join(summary_parts)})
    if extra_sections:
        from resumeforge.providers import ExtraSection

        content = content.model_copy(
            update={
                "extra_sections": [ExtraSection(**section) for section in extra_sections],
            }
        )
    return content


def _parse_contact_lines(contact_lines: list[str]) -> ResumeContact:
    joined = " · ".join(contact_lines)
    links: list[ResumeLink] = []
    for match in _LINK_RE.finditer(joined):
        links.append(ResumeLink(label=match.group(1).strip(), url=match.group(2).strip()))
    text_only = _LINK_RE.sub("", joined)
    tokens = [tok.strip() for tok in re.split(r"[·|]", text_only) if tok.strip()]
    email = next((tok for tok in tokens if "@" in tok and " " not in tok), None)
    phone = next((tok for tok in tokens if re.search(r"\d", tok) and tok != email), None)
    location = next(
        (tok for tok in tokens if tok != email and tok != phone),
        None,
    )
    return ResumeContact(email=email, phone=phone, location=location, links=links)


# Silence unused-import warnings (kept for downstream re-export convenience).
_ = (
    EducationEntry,
    ExperienceEntry,
    LanguageEntry,
    ProjectEntry,
    SkillGroup,
)
