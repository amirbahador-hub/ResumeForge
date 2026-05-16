from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ArtifactType(StrEnum):
    NORMALIZED_CONTEXT = "normalized_context"
    ROLE_ANALYSIS = "role_analysis"
    RECRUITER_PROFILE = "recruiter_profile"
    COMPANY_PROFILE = "company_profile"
    RESUME_ANALYSIS = "resume_analysis"
    ARCHETYPE = "archetype"
    ATS_REPORT = "ats_report"
    TRUTHFULNESS_REPORT = "truthfulness_report"
    RESUME_STRATEGY = "resume_strategy"
    OPTIMIZED_RESUME = "optimized_resume"
    OPTIMIZATION_REPORT = "optimization_report"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Artifact(StrictModel):
    schema_version: str = "0.1.0"
    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    artifact_type: ArtifactType
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    agent_name: str
    source_artifacts: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    assumptions: list[str] = Field(default_factory=list)
    validation_errors: list[str] = Field(default_factory=list)


class SourceDocument(StrictModel):
    name: str
    content: str
    source_type: Literal[
        "resume",
        "job_description",
        "recruiter",
        "company",
        "github",
        "linkedin",
        "portfolio",
        "other",
    ]


class UserInput(StrictModel):
    job_description: str
    resume: str
    recruiter_name: str | None = None
    recruiter_profile: str | None = None
    recruiter_posts: list[str] = Field(default_factory=list)
    company_name: str | None = None
    company_context: str | None = None
    github: str | None = None
    linkedin: str | None = None
    portfolio: str | None = None
    projects: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class NormalizedContext(Artifact):
    artifact_type: ArtifactType = ArtifactType.NORMALIZED_CONTEXT
    agent_name: str = "input_normalizer"
    confidence: float = 1.0
    job_description: str
    resume: str
    recruiter_name: str | None = None
    recruiter_profile: str | None = None
    recruiter_posts: list[str] = Field(default_factory=list)
    company_name: str | None = None
    company_context: str | None = None
    github: str | None = None
    linkedin: str | None = None
    portfolio: str | None = None
    projects: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    evidence_inventory: list[SourceDocument] = Field(default_factory=list)


class ScoreBlock(StrictModel):
    score: float = Field(ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)


class RoleAnalysis(Artifact):
    artifact_type: ArtifactType = ArtifactType.ROLE_ANALYSIS
    agent_name: str = "role_analyzer"
    required_skills: list[str]
    preferred_skills: list[str] = Field(default_factory=list)
    implicit_signals: list[str] = Field(default_factory=list)
    seniority: str
    culture_signals: list[str] = Field(default_factory=list)
    engineering_stack: dict[str, list[str]] = Field(default_factory=dict)
    workflow_expectations: list[str] = Field(default_factory=list)
    architecture_signals: list[str] = Field(default_factory=list)
    hiring_priorities: list[str] = Field(default_factory=list)
    domain_context: list[str] = Field(default_factory=list)
    leadership_expectations: list[str] = Field(default_factory=list)
    role_archetype_hint: str | None = None


class RecruiterProfile(Artifact):
    artifact_type: ArtifactType = ArtifactType.RECRUITER_PROFILE
    agent_name: str = "recruiter_intelligence_agent"
    recruiter_name: str | None = None
    interests: list[str] = Field(default_factory=list)
    communication_style: str = "unknown"
    hiring_patterns: list[str] = Field(default_factory=list)
    cultural_signals: list[str] = Field(default_factory=list)
    resume_implications: list[str] = Field(default_factory=list)


class CompanyProfile(Artifact):
    artifact_type: ArtifactType = ArtifactType.COMPANY_PROFILE
    agent_name: str = "company_analyzer"
    company_name: str | None = None
    engineering_culture: list[str] = Field(default_factory=list)
    architecture_patterns: list[str] = Field(default_factory=list)
    ai_maturity: str = "unknown"
    technical_stack: dict[str, list[str]] = Field(default_factory=dict)
    hiring_philosophy: list[str] = Field(default_factory=list)
    organizational_values: list[str] = Field(default_factory=list)


class EvidenceClaim(StrictModel):
    claim: str
    source: str
    confidence: float = Field(ge=0.0, le=1.0)


class ResumeAnalysis(Artifact):
    artifact_type: ArtifactType = ArtifactType.RESUME_ANALYSIS
    agent_name: str = "resume_intelligence_agent"
    technical_strengths: list[str] = Field(default_factory=list)
    weak_signals: list[str] = Field(default_factory=list)
    missing_signals: list[str] = Field(default_factory=list)
    ats_weaknesses: list[str] = Field(default_factory=list)
    engineering_depth: dict[str, float] = Field(default_factory=dict)
    project_quality: float = Field(ge=0.0, le=1.0)
    leadership_indicators: list[str] = Field(default_factory=list)
    architecture_indicators: list[str] = Field(default_factory=list)
    evidence_map: list[EvidenceClaim] = Field(default_factory=list)


class Archetype(Artifact):
    artifact_type: ArtifactType = ArtifactType.ARCHETYPE
    agent_name: str = "role_archetype_engine"
    primary_archetype: str
    secondary_archetypes: list[str] = Field(default_factory=list)
    expected_behavioral_signals: list[str] = Field(default_factory=list)
    expected_technical_signals: list[str] = Field(default_factory=list)
    expected_project_types: list[str] = Field(default_factory=list)
    expected_language_style: list[str] = Field(default_factory=list)
    resume_strategy: dict[str, list[str]] = Field(default_factory=dict)


class AtsReport(Artifact):
    artifact_type: ArtifactType = ArtifactType.ATS_REPORT
    agent_name: str = "ats_validation_engine"
    overall_score: float = Field(ge=0.0, le=1.0)
    parser_safety: ScoreBlock
    keyword_coverage: ScoreBlock
    formatting_quality: ScoreBlock
    section_consistency: ScoreBlock
    semantic_matching: ScoreBlock
    readability: ScoreBlock
    covered_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class TruthfulnessReport(Artifact):
    artifact_type: ArtifactType = ArtifactType.TRUTHFULNESS_REPORT
    agent_name: str = "truthfulness_validator"
    overall_status: Literal["pass", "needs_review", "fail"]
    unsupported_claims: list[str] = Field(default_factory=list)
    needs_user_confirmation: list[str] = Field(default_factory=list)
    grounded_claims: list[EvidenceClaim] = Field(default_factory=list)
    interview_risks: list[str] = Field(default_factory=list)


class ResumeStrategy(Artifact):
    artifact_type: ArtifactType = ArtifactType.RESUME_STRATEGY
    agent_name: str = "synthesis_engine"
    priority_signals: list[str] = Field(default_factory=list)
    missing_signals: list[str] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)
    optimization_actions: list[str] = Field(default_factory=list)


class OptimizedResume(Artifact):
    artifact_type: ArtifactType = ArtifactType.OPTIMIZED_RESUME
    agent_name: str = "synthesis_engine"
    resume_markdown: str
    optimization_explanation: list[str] = Field(default_factory=list)
    diff_summary: list[str] = Field(default_factory=list)


class OptimizationReport(Artifact):
    artifact_type: ArtifactType = ArtifactType.OPTIMIZATION_REPORT
    agent_name: str = "report_generator"
    interview_probability_score: float = Field(ge=0.0, le=1.0)
    recruiter_resonance: float = Field(ge=0.0, le=1.0)
    technical_credibility: float = Field(ge=0.0, le=1.0)
    ats_survivability: float = Field(ge=0.0, le=1.0)
    hiring_manager_alignment: float = Field(ge=0.0, le=1.0)
    summary: str
    next_actions: list[str] = Field(default_factory=list)


class PipelineResult(StrictModel):
    normalized_context: NormalizedContext
    role_analysis: RoleAnalysis
    recruiter_profile: RecruiterProfile
    company_profile: CompanyProfile
    resume_analysis: ResumeAnalysis
    archetype: Archetype
    ats_report: AtsReport
    truthfulness_report: TruthfulnessReport
    resume_strategy: ResumeStrategy
    optimized_resume: OptimizedResume
    optimization_report: OptimizationReport

    def artifacts(self) -> list[Artifact]:
        return [
            self.normalized_context,
            self.role_analysis,
            self.recruiter_profile,
            self.company_profile,
            self.resume_analysis,
            self.archetype,
            self.ats_report,
            self.truthfulness_report,
            self.resume_strategy,
            self.optimized_resume,
            self.optimization_report,
        ]


class PipelineRequest(StrictModel):
    input: UserInput
    artifact_dir: str | None = None


class PipelineResponse(StrictModel):
    run_id: str
    artifacts: dict[str, Any]

    @field_validator("run_id")
    @classmethod
    def run_id_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("run_id cannot be empty")
        return value
