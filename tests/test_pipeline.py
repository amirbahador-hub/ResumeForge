from __future__ import annotations

import pytest

from resumeforge.pipeline import ResumeForgePipeline
from resumeforge.schemas import UserInput


@pytest.mark.asyncio
async def test_pipeline_generates_truthful_artifacts() -> None:
    result = await ResumeForgePipeline().run(
        UserInput(
            job_description=(
                "Senior Applied AI Engineer. Python, FastAPI, LangGraph, Kubernetes, "
                "observability, agentic workflows, and production ownership."
            ),
            resume=(
                "## Experience\n"
                "- Built Python FastAPI services with Docker and observability.\n"
                "- Led backend platform work for production APIs.\n"
                "## Projects\n"
                "- Built an agent workflow prototype with evaluation notes."
            ),
            recruiter_name="Example Recruiter",
            recruiter_profile="Hiring technical builders working on AI agents and MCP.",
            company_name="Example AI",
            company_context="AI infrastructure startup that values ownership and shipped systems.",
        )
    )

    assert result.role_analysis.required_skills
    assert result.archetype.primary_archetype in {
        "applied_ai_engineer",
        "ai_native_workflow_engineer",
        "startup_infrastructure_engineer",
    }
    assert result.ats_report.overall_score > 0
    assert result.truthfulness_report.overall_status == "pass"
    assert "Optimized Resume Draft" in result.optimized_resume.resume_markdown


@pytest.mark.asyncio
async def test_pipeline_writes_yaml_artifacts(tmp_path) -> None:
    await ResumeForgePipeline(artifact_dir=tmp_path).run(
        UserInput(
            job_description="Python backend engineer with Kubernetes and observability.",
            resume="## Experience\n- Built Python APIs.\n## Skills\nPython",
        )
    )

    written = list(tmp_path.glob("*/*.yaml"))
    assert {path.name for path in written} >= {
        "role_analysis.yaml",
        "resume_analysis.yaml",
        "ats_report.yaml",
        "optimized_resume.yaml",
    }
