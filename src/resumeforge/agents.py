from __future__ import annotations

from dataclasses import dataclass

from resumeforge.schemas import (
    Archetype,
    AtsReport,
    CompanyProfile,
    EvidenceClaim,
    NormalizedContext,
    OptimizedResume,
    RecruiterProfile,
    ResumeAnalysis,
    ResumeStrategy,
    RoleAnalysis,
    ScoreBlock,
    SourceDocument,
    TruthfulnessReport,
    UserInput,
)
from resumeforge.text import (
    SIGNAL_TERMS,
    TECH_TERMS,
    all_known_terms,
    contains_any,
    extract_terms,
    infer_seniority,
    score_coverage,
)


@dataclass(frozen=True)
class InputNormalizer:
    async def run(self, user_input: UserInput) -> NormalizedContext:
        evidence = [
            SourceDocument(name="resume", content=user_input.resume, source_type="resume"),
            SourceDocument(
                name="job_description",
                content=user_input.job_description,
                source_type="job_description",
            ),
        ]
        if user_input.recruiter_profile:
            evidence.append(
                SourceDocument(
                    name="recruiter_profile",
                    content=user_input.recruiter_profile,
                    source_type="recruiter",
                )
            )
        if user_input.company_context:
            evidence.append(
                SourceDocument(
                    name="company_context",
                    content=user_input.company_context,
                    source_type="company",
                )
            )
        for index, project in enumerate(user_input.projects, start=1):
            evidence.append(
                SourceDocument(name=f"project_{index}", content=project, source_type="portfolio")
            )

        return NormalizedContext(
            job_description=user_input.job_description.strip(),
            resume=user_input.resume.strip(),
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
            evidence_inventory=evidence,
        )


@dataclass(frozen=True)
class RoleAnalyzer:
    async def run(self, context: NormalizedContext) -> RoleAnalysis:
        jd = context.job_description
        all_terms = all_known_terms()
        required = extract_terms(jd, all_terms)
        implicit = [signal for signal, terms in SIGNAL_TERMS.items() if contains_any(jd, terms)]
        stack = {
            group: extract_terms(jd, terms)
            for group, terms in TECH_TERMS.items()
            if extract_terms(jd, terms)
        }
        architecture = [
            signal
            for signal in [
                "distributed systems",
                "event-driven systems",
                "observability",
                "platform engineering",
            ]
            if contains_any(jd, signal.split())
        ]
        hiring = [
            value
            for value in [
                "production ownership",
                "technical depth",
                "rapid execution",
                "cross-functional collaboration",
            ]
            if contains_any(jd, value.split())
        ]
        role_hint = _infer_archetype(jd)
        return RoleAnalysis(
            confidence=0.82 if required else 0.6,
            required_skills=required,
            preferred_skills=[],
            implicit_signals=implicit,
            seniority=infer_seniority(jd),
            culture_signals=[s for s in implicit if s in {"startup mindset", "high agency"}],
            engineering_stack=stack,
            workflow_expectations=[
                value
                for value in ["async workflows", "agentic workflows", "ci/cd", "incident response"]
                if contains_any(jd, value.split())
            ],
            architecture_signals=architecture,
            hiring_priorities=hiring or ["role alignment", "credible delivery evidence"],
            domain_context=[
                value
                for value in [
                    "developer tooling",
                    "ai infrastructure",
                    "fintech",
                    "healthcare",
                    "enterprise saas",
                ]
                if contains_any(jd, value.split())
            ],
            leadership_expectations=[
                value
                for value in ["mentorship", "technical leadership", "ownership"]
                if contains_any(jd, value.split())
            ],
            role_archetype_hint=role_hint,
            assumptions=[
                "Heuristic extraction is used until model-backed adapters are configured."
            ],
        )


@dataclass(frozen=True)
class RecruiterIntelligenceAgent:
    async def run(self, context: NormalizedContext) -> RecruiterProfile:
        text = " ".join(
            [
                context.recruiter_profile or "",
                " ".join(context.recruiter_posts),
                context.company_context or "",
            ]
        )
        interests = extract_terms(text, all_known_terms())
        style = (
            "concise_technical"
            if contains_any(text, ["engineer", "technical", "infra", "ai"])
            else "unknown"
        )
        confidence = 0.76 if text.strip() else 0.35
        return RecruiterProfile(
            confidence=confidence,
            recruiter_name=context.recruiter_name,
            interests=interests,
            communication_style=style,
            hiring_patterns=_extract_patterns(text),
            cultural_signals=[
                signal for signal, terms in SIGNAL_TERMS.items() if contains_any(text, terms)
            ],
            resume_implications=[
                "Prioritize concrete technical evidence over broad claims.",
                "Keep summary concise and role-specific.",
            ],
            assumptions=["Only user-provided recruiter context is analyzed."],
        )


@dataclass(frozen=True)
class CompanyAnalyzer:
    async def run(self, context: NormalizedContext) -> CompanyProfile:
        text = " ".join([context.company_context or "", context.job_description])
        stack = {
            group: extract_terms(text, terms)
            for group, terms in TECH_TERMS.items()
            if extract_terms(text, terms)
        }
        ai_maturity = "active" if contains_any(text, TECH_TERMS["ai"]) else "unknown"
        return CompanyProfile(
            confidence=0.75 if context.company_context else 0.55,
            company_name=context.company_name,
            engineering_culture=[
                signal for signal, terms in SIGNAL_TERMS.items() if contains_any(text, terms)
            ],
            architecture_patterns=[
                value
                for value in [
                    "cloud-native services",
                    "distributed systems",
                    "event-driven systems",
                ]
                if contains_any(text, value.split())
            ],
            ai_maturity=ai_maturity,
            technical_stack=stack,
            hiring_philosophy=["values shipped work"]
            if contains_any(text, ["ship", "shipped", "builder"])
            else [],
            organizational_values=[
                value
                for value in ["customer focus", "speed", "ownership", "quality"]
                if contains_any(text, [value])
            ],
            assumptions=[
                "Company profile uses job description context when no company profile is supplied."
            ],
        )


@dataclass(frozen=True)
class ResumeIntelligenceAgent:
    async def run(self, context: NormalizedContext, role: RoleAnalysis) -> ResumeAnalysis:
        resume = context.resume
        strengths = extract_terms(resume, all_known_terms())
        missing = [skill for skill in role.required_skills if skill not in strengths]
        weak = []
        if not contains_any(resume, ["%", "reduced", "increased", "improved", "saved"]):
            weak.append("limited quantified impact")
        if not contains_any(resume, ["designed", "architecture", "scalable", "distributed"]):
            weak.append("limited architecture signal")
        evidence = [
            EvidenceClaim(claim=f"Evidence for {term}", source="resume", confidence=0.88)
            for term in strengths
        ]
        depth_score = score_coverage(len(strengths), max(len(role.required_skills), 1))
        return ResumeAnalysis(
            confidence=0.82,
            technical_strengths=strengths,
            weak_signals=weak,
            missing_signals=missing,
            ats_weaknesses=_ats_formatting_weaknesses(resume),
            engineering_depth={
                "systems_depth": depth_score,
                "architecture_maturity": 0.75
                if contains_any(resume, ["architecture", "designed"])
                else 0.45,
                "operational_excellence": 0.78 if contains_any(resume, TECH_TERMS["ops"]) else 0.42,
            },
            project_quality=0.8
            if context.projects or contains_any(resume, ["project", "built"])
            else 0.55,
            leadership_indicators=[
                term
                for term in ["led", "mentored", "owned", "drove"]
                if contains_any(resume, [term])
            ],
            architecture_indicators=[
                term
                for term in ["distributed", "event-driven", "scalable", "observability"]
                if contains_any(resume, [term])
            ],
            evidence_map=evidence,
        )


@dataclass(frozen=True)
class RoleArchetypeEngine:
    async def run(self, role: RoleAnalysis, company: CompanyProfile) -> Archetype:
        source = " ".join(
            [
                role.role_archetype_hint or "",
                " ".join(role.required_skills),
                " ".join(company.engineering_culture),
            ]
        )
        primary = _infer_archetype(source)
        expected = _archetype_expectations(primary)
        return Archetype(
            confidence=0.82,
            primary_archetype=primary,
            secondary_archetypes=[
                item
                for item in ["ai_native_workflow_engineer", "startup_infrastructure_engineer"]
                if item != primary
            ][:1],
            expected_behavioral_signals=expected["behavioral"],
            expected_technical_signals=expected["technical"],
            expected_project_types=expected["projects"],
            expected_language_style=["concrete", "technically specific", "impact oriented"],
            resume_strategy={
                "prioritize": expected["technical"][:3],
                "de_emphasize": ["generic claims without evidence"],
            },
        )


@dataclass(frozen=True)
class AtsValidationEngine:
    async def run(self, resume_text: str, role: RoleAnalysis) -> AtsReport:
        covered = [skill for skill in role.required_skills if contains_any(resume_text, [skill])]
        missing = [skill for skill in role.required_skills if skill not in covered]
        keyword_score = score_coverage(len(covered), len(role.required_skills))
        formatting_issues = _ats_formatting_weaknesses(resume_text)
        parser_score = max(0.2, 1.0 - (len(formatting_issues) * 0.15))
        readability_score = 0.9 if len(resume_text.split()) < 900 else 0.7
        overall = round(
            (parser_score * 0.3) + (keyword_score * 0.25) + (readability_score * 0.15) + 0.3, 3
        )
        return AtsReport(
            confidence=0.86,
            overall_score=overall,
            parser_safety=ScoreBlock(score=round(parser_score, 3), issues=formatting_issues),
            keyword_coverage=ScoreBlock(
                score=keyword_score, issues=[f"Missing: {item}" for item in missing]
            ),
            formatting_quality=ScoreBlock(score=round(parser_score, 3), issues=formatting_issues),
            section_consistency=ScoreBlock(score=0.84, issues=[]),
            semantic_matching=ScoreBlock(score=max(0.4, keyword_score), issues=[]),
            readability=ScoreBlock(score=readability_score, issues=[]),
            covered_keywords=covered,
            missing_keywords=missing,
            recommendations=[
                "Add truthful evidence for missing role-critical skills."
                if missing
                else "Keyword coverage is acceptable."
            ],
        )


@dataclass(frozen=True)
class TruthfulnessValidator:
    async def run(
        self, generated_resume: str, resume_analysis: ResumeAnalysis
    ) -> TruthfulnessReport:
        unsupported = []
        needs_confirmation = []
        for metric in _extract_metric_claims(generated_resume):
            if not any(metric in claim.claim for claim in resume_analysis.evidence_map):
                needs_confirmation.append(metric)
        status = "needs_review" if unsupported or needs_confirmation else "pass"
        return TruthfulnessReport(
            confidence=0.88,
            overall_status=status,
            unsupported_claims=unsupported,
            needs_user_confirmation=needs_confirmation,
            grounded_claims=resume_analysis.evidence_map,
            interview_risks=["Confirm any quantified impact before using externally."]
            if needs_confirmation
            else [],
        )


@dataclass(frozen=True)
class SynthesisEngine:
    async def build_strategy(
        self,
        role: RoleAnalysis,
        recruiter: RecruiterProfile,
        resume: ResumeAnalysis,
        ats: AtsReport,
        archetype: Archetype,
    ) -> ResumeStrategy:
        priorities = sorted(
            set(
                role.required_skills[:6]
                + archetype.expected_technical_signals[:4]
                + recruiter.interests[:3]
            ),
            key=str.lower,
        )
        risks = resume.weak_signals + ats.missing_keywords
        return ResumeStrategy(
            confidence=0.84,
            priority_signals=priorities,
            missing_signals=resume.missing_signals,
            risk_signals=risks,
            optimization_actions=[
                "Move role-relevant technical evidence closer to the top.",
                "Use concrete project and ownership language.",
                "Remove or confirm unsupported quantified claims.",
            ],
        )

    async def synthesize(
        self,
        context: NormalizedContext,
        role: RoleAnalysis,
        resume: ResumeAnalysis,
        strategy: ResumeStrategy,
    ) -> OptimizedResume:
        lines = [
            "# Optimized Resume Draft",
            "",
            "## Targeted Technical Summary",
            _summary_sentence(role, resume, strategy),
            "",
            "## Priority Signals",
        ]
        lines.extend(f"- {signal}" for signal in strategy.priority_signals[:8])
        lines.extend(["", "## Current Resume Evidence", context.resume])
        if resume.missing_signals:
            lines.extend(["", "## Missing Signals To Address Truthfully"])
            lines.extend(f"- {signal}" for signal in resume.missing_signals)
        return OptimizedResume(
            confidence=0.78,
            resume_markdown="\n".join(lines),
            optimization_explanation=[
                "Prioritized role-relevant signals already present in the source resume.",
                "Separated missing signals from generated resume claims to preserve truthfulness.",
            ],
            diff_summary=[
                "Added targeted summary.",
                "Added priority signal section.",
                "Preserved original resume evidence for human editing.",
            ],
        )


def _infer_archetype(text: str) -> str:
    if contains_any(text, ["forward deployed", "customer", "implementation", "solutions"]):
        return "forward_deployed_engineer"
    if contains_any(text, ["kubernetes", "terraform", "observability", "infrastructure"]):
        return "startup_infrastructure_engineer"
    if contains_any(text, ["agent", "mcp", "workflow", "automation"]):
        return "ai_native_workflow_engineer"
    if contains_any(text, ["llm", "rag", "ai", "model"]):
        return "applied_ai_engineer"
    return "technical_generalist"


def _archetype_expectations(archetype: str) -> dict[str, list[str]]:
    expectations = {
        "applied_ai_engineer": {
            "technical": [
                "python",
                "llm systems",
                "evaluation pipelines",
                "production reliability",
            ],
            "behavioral": ["product judgment", "iteration speed", "ambiguity tolerance"],
            "projects": ["RAG systems", "AI tooling", "agentic workflows"],
        },
        "startup_infrastructure_engineer": {
            "technical": ["kubernetes", "observability", "ci/cd", "cloud infrastructure"],
            "behavioral": ["high agency", "operational ownership", "pragmatism"],
            "projects": ["deployment platforms", "observability pipelines", "infra automation"],
        },
        "forward_deployed_engineer": {
            "technical": ["backend systems", "integrations", "debugging", "rapid prototyping"],
            "behavioral": ["communication clarity", "customer empathy", "ownership"],
            "projects": ["customer integrations", "workflow automation", "enterprise deployments"],
        },
        "ai_native_workflow_engineer": {
            "technical": ["agent orchestration", "MCP", "workflow automation", "evaluation"],
            "behavioral": ["systems thinking", "experimentation", "product-engineering loop"],
            "projects": ["agent harnesses", "developer tooling", "AI workflow platforms"],
        },
    }
    return expectations.get(
        archetype,
        {
            "technical": ["software engineering", "system design", "production delivery"],
            "behavioral": ["ownership", "clarity", "collaboration"],
            "projects": ["shipped technical systems"],
        },
    )


def _extract_patterns(text: str) -> list[str]:
    if not text.strip():
        return []
    patterns = []
    if contains_any(text, ["shipped", "builder", "built"]):
        patterns.append("Highlights candidates with shipped systems.")
    if contains_any(text, ["ai", "agent", "llm"]):
        patterns.append("Shows interest in AI-native engineering roles.")
    return patterns


def _ats_formatting_weaknesses(resume: str) -> list[str]:
    issues = []
    if "|" in resume:
        issues.append("Tables or pipe-delimited layouts may parse poorly.")
    if len([line for line in resume.splitlines() if line.strip().startswith("##")]) < 2:
        issues.append("Resume may need clearer standard section headings.")
    if contains_any(resume, ["image", "graphic"]):
        issues.append("Image-based content may not be ATS-readable.")
    return issues


def _extract_metric_claims(text: str) -> list[str]:
    import re

    return re.findall(
        r"\b(?:increased|reduced|improved|saved|cut)\s+[^.;\n]*?\d+%?", text, flags=re.I
    )


def _summary_sentence(role: RoleAnalysis, resume: ResumeAnalysis, strategy: ResumeStrategy) -> str:
    signals = ", ".join(strategy.priority_signals[:4]) or "role-relevant engineering work"
    strengths = ", ".join(resume.technical_strengths[:4]) or "software engineering"
    seniority = role.seniority.replace("_", " ")
    return (
        f"{seniority.title()} technical candidate with demonstrated evidence in {strengths}. "
        f"Positioning should emphasize {signals} while keeping all claims grounded in "
        "supplied evidence."
    )
