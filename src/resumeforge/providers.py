from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

ProviderName = Literal["openai", "anthropic", "none"]


class TailoringChange(BaseModel):
    section: str
    before: str = ""
    after: str
    why: str
    evidence: str


class ResumeLink(BaseModel):
    label: str
    url: str


class ResumeContact(BaseModel):
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[ResumeLink] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    role: str
    company: str
    location: str = ""
    dates: str = ""
    bullets: list[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    name: str
    description: str = ""
    url: str | None = None
    bullets: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    degree: str
    institution: str = ""
    dates: str = ""
    details: str = ""


class SkillGroup(BaseModel):
    label: str
    items: list[str] = Field(default_factory=list)


class LanguageEntry(BaseModel):
    name: str
    proficiency: str = ""


class ExtraSection(BaseModel):
    heading: str
    items: list[str] = Field(default_factory=list)


class TailoredResumeContent(BaseModel):
    name: str
    headline: str = ""
    contact: ResumeContact = Field(default_factory=ResumeContact)
    summary: str = ""
    skill_groups: list[SkillGroup] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    open_source: list[ProjectEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    languages: list[LanguageEntry] = Field(default_factory=list)
    extra_sections: list[ExtraSection] = Field(default_factory=list)


class TailoringResult(BaseModel):
    content: TailoredResumeContent
    changed_items: list[TailoringChange] = Field(default_factory=list)
    questions_for_user: list[str] = Field(default_factory=list)
    risks_or_assumptions: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class ProviderConfig:
    provider: ProviderName
    model: str


class LLMTailoringClient:
    def __init__(self, provider: ProviderName = "none", model: str = "") -> None:
        self.provider = provider
        self.model = model

    async def tailor(self, prompt: str) -> TailoringResult:
        if self.provider == "openai":
            return await self._tailor_openai(prompt)
        if self.provider == "anthropic":
            return await self._tailor_anthropic(prompt)
        raise RuntimeError("No LLM provider configured.")

    async def _tailor_openai(self, prompt: str) -> TailoringResult:
        from openai import AsyncOpenAI

        client = AsyncOpenAI()
        response = await client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are ResumeForge's truthful technical resume tailoring engine. "
                        "Return only valid JSON matching the requested schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.output_text or "{}"
        return _parse_tailoring_result(content)

    async def _tailor_anthropic(self, prompt: str) -> TailoringResult:
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic()
        response = await client.messages.create(
            model=self.model,
            max_tokens=6000,
            temperature=0.2,
            system=(
                "You are ResumeForge's truthful technical resume tailoring engine. "
                "Return only valid JSON matching the requested schema."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        content = "\n".join(
            block.text for block in response.content if getattr(block, "type", "") == "text"
        )
        return _parse_tailoring_result(content)


def select_provider(requested: str = "auto") -> ProviderConfig:
    load_dotenv()
    requested = requested.lower()
    if requested not in {"auto", "openai", "anthropic", "none"}:
        raise ValueError("--provider must be one of: auto, openai, anthropic, none")

    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    openai_model = os.getenv("RESUMEFORGE_OPENAI_MODEL", "gpt-5.4-mini")
    anthropic_model = os.getenv("RESUMEFORGE_ANTHROPIC_MODEL", "claude-sonnet-4-6")

    if requested == "openai":
        return ProviderConfig("openai", openai_model) if has_openai else ProviderConfig("none", "")
    if requested == "anthropic":
        return (
            ProviderConfig("anthropic", anthropic_model)
            if has_anthropic
            else ProviderConfig("none", "")
        )
    if requested == "none":
        return ProviderConfig("none", "")
    if has_openai:
        return ProviderConfig("openai", openai_model)
    if has_anthropic:
        return ProviderConfig("anthropic", anthropic_model)
    return ProviderConfig("none", "")


def _parse_tailoring_result(content: str) -> TailoringResult:
    try:
        data = json.loads(_extract_json_object(content))
        return TailoringResult.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError("Provider returned invalid tailoring JSON.") from exc


def _extract_json_object(content: str) -> str:
    content = content.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, flags=re.S)
    if fenced:
        return fenced.group(1)
    start = content.find("{")
    end = content.rfind("}")
    if start >= 0 and end > start:
        return content[start : end + 1]
    return content
