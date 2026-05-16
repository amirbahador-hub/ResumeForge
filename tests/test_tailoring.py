from __future__ import annotations

import asyncio
from pathlib import Path

from pypdf import PdfReader

from resumeforge.providers import (
    ExperienceEntry,
    ResumeContact,
    SkillGroup,
    TailoredResumeContent,
)
from resumeforge.rendering import render_resume_pdf
from resumeforge.resume_templates import get_template
from resumeforge.tailoring import _filter_new_questions, _question_key, content_to_markdown


def test_render_resume_pdf(tmp_path: Path) -> None:
    content = TailoredResumeContent(
        name="Jane Doe",
        headline="Senior Engineer",
        contact=ResumeContact(email="jane@example.com"),
        summary="Built Python services.",
        skill_groups=[SkillGroup(label="Languages", items=["Python"])],
        experience=[
            ExperienceEntry(
                role="Engineer",
                company="Acme",
                bullets=["Led platform work."],
            )
        ],
    )
    pdf_path = tmp_path / "resume.pdf"
    asyncio.run(render_resume_pdf(pdf_path, content, get_template("jake")))

    assert pdf_path.exists()
    reader = PdfReader(str(pdf_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "Built Python services" in text
    assert "Led platform work" in text


def test_content_to_markdown_roundtrip() -> None:
    content = TailoredResumeContent(
        name="Jane Doe",
        contact=ResumeContact(email="jane@example.com"),
        summary="Engineer.",
    )
    md = content_to_markdown(content)
    assert "# Jane Doe" in md
    assert "## Summary" in md
    assert "jane@example.com" in md


def test_filter_new_questions_removes_duplicates() -> None:
    asked = {_question_key("Can you provide concrete evidence for agents?")}
    questions = [
        "Can you provide concrete evidence for agents?",
        "Can you provide concrete evidence for evaluation?",
        "Can you provide concrete evidence for agents?",
    ]

    filtered = _filter_new_questions(questions, asked)

    assert filtered == ["Can you provide concrete evidence for evaluation?"]
