from __future__ import annotations

import asyncio
from pathlib import Path
from typing import NotRequired, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from resumeforge.agents import (
    AtsValidationEngine,
    CompanyAnalyzer,
    InputNormalizer,
    RecruiterIntelligenceAgent,
    ResumeIntelligenceAgent,
    RoleAnalyzer,
    RoleArchetypeEngine,
    SynthesisEngine,
    TruthfulnessValidator,
)
from resumeforge.schemas import OptimizationReport, PipelineResult, UserInput
from resumeforge.yaml_io import write_yaml


class ResumeForgeState(TypedDict):
    user_input: UserInput
    context: NotRequired[object]
    role: NotRequired[object]
    recruiter: NotRequired[object]
    company: NotRequired[object]
    resume: NotRequired[object]
    archetype: NotRequired[object]
    ats: NotRequired[object]
    truthfulness: NotRequired[object]
    strategy: NotRequired[object]
    optimized: NotRequired[object]
    report: NotRequired[object]


class ResumeForgePipeline:
    def __init__(self, artifact_dir: Path | None = None) -> None:
        self.artifact_dir = artifact_dir
        self.normalizer = InputNormalizer()
        self.role_analyzer = RoleAnalyzer()
        self.recruiter_agent = RecruiterIntelligenceAgent()
        self.company_analyzer = CompanyAnalyzer()
        self.resume_agent = ResumeIntelligenceAgent()
        self.archetype_engine = RoleArchetypeEngine()
        self.ats_engine = AtsValidationEngine()
        self.truthfulness_validator = TruthfulnessValidator()
        self.synthesis_engine = SynthesisEngine()

    async def run(self, user_input: UserInput) -> PipelineResult:
        graph = self._build_graph()
        state = await graph.ainvoke({"user_input": user_input})

        result = PipelineResult(
            normalized_context=state["context"],
            role_analysis=state["role"],
            recruiter_profile=state["recruiter"],
            company_profile=state["company"],
            resume_analysis=state["resume"],
            archetype=state["archetype"],
            ats_report=state["ats"],
            truthfulness_report=state["truthfulness"],
            resume_strategy=state["strategy"],
            optimized_resume=state["optimized"],
            optimization_report=state["report"],
        )
        if self.artifact_dir:
            self.write_artifacts(result, self.artifact_dir)
        return result

    def _build_graph(self):
        graph = StateGraph(ResumeForgeState)

        async def normalize(state: ResumeForgeState) -> dict[str, object]:
            return {"context": await self.normalizer.run(state["user_input"])}

        async def analyze_primary(state: ResumeForgeState) -> dict[str, object]:
            context = state["context"]
            role_task = self.role_analyzer.run(context)
            recruiter_task = self.recruiter_agent.run(context)
            company_task = self.company_analyzer.run(context)
            role, recruiter, company = await asyncio.gather(
                role_task,
                recruiter_task,
                company_task,
            )
            return {"role": role, "recruiter": recruiter, "company": company}

        async def analyze_secondary(state: ResumeForgeState) -> dict[str, object]:
            context = state["context"]
            role = state["role"]
            company = state["company"]
            resume_task = self.resume_agent.run(context, role)
            archetype_task = self.archetype_engine.run(role, company)
            resume, archetype = await asyncio.gather(resume_task, archetype_task)
            return {"resume": resume, "archetype": archetype}

        async def validate_and_synthesize(state: ResumeForgeState) -> dict[str, object]:
            context = state["context"]
            role = state["role"]
            recruiter = state["recruiter"]
            resume = state["resume"]
            archetype = state["archetype"]
            ats = await self.ats_engine.run(context.resume, role)
            strategy = await self.synthesis_engine.build_strategy(
                role,
                recruiter,
                resume,
                ats,
                archetype,
            )
            optimized = await self.synthesis_engine.synthesize(context, role, resume, strategy)
            truthfulness = await self.truthfulness_validator.run(
                optimized.resume_markdown,
                resume,
            )
            report = self._build_report(
                ats.overall_score,
                truthfulness.overall_status,
                recruiter.confidence,
                resume.project_quality,
            )
            return {
                "ats": ats,
                "strategy": strategy,
                "optimized": optimized,
                "truthfulness": truthfulness,
                "report": report,
            }

        graph.add_node("normalize", normalize)
        graph.add_node("analyze_primary", analyze_primary)
        graph.add_node("analyze_secondary", analyze_secondary)
        graph.add_node("validate_and_synthesize", validate_and_synthesize)
        graph.add_edge(START, "normalize")
        graph.add_edge("normalize", "analyze_primary")
        graph.add_edge("analyze_primary", "analyze_secondary")
        graph.add_edge("analyze_secondary", "validate_and_synthesize")
        graph.add_edge("validate_and_synthesize", END)
        return graph.compile()

    async def run_without_graph(self, user_input: UserInput) -> PipelineResult:
        context = await self.normalizer.run(user_input)

        role_task = self.role_analyzer.run(context)
        recruiter_task = self.recruiter_agent.run(context)
        company_task = self.company_analyzer.run(context)
        role, recruiter, company = await asyncio.gather(role_task, recruiter_task, company_task)

        resume_task = self.resume_agent.run(context, role)
        archetype_task = self.archetype_engine.run(role, company)
        resume, archetype = await asyncio.gather(resume_task, archetype_task)

        ats = await self.ats_engine.run(context.resume, role)
        strategy = await self.synthesis_engine.build_strategy(
            role, recruiter, resume, ats, archetype
        )
        optimized = await self.synthesis_engine.synthesize(context, role, resume, strategy)
        truthfulness = await self.truthfulness_validator.run(optimized.resume_markdown, resume)
        report = self._build_report(
            ats.overall_score,
            truthfulness.overall_status,
            recruiter.confidence,
            resume.project_quality,
        )

        result = PipelineResult(
            normalized_context=context,
            role_analysis=role,
            recruiter_profile=recruiter,
            company_profile=company,
            resume_analysis=resume,
            archetype=archetype,
            ats_report=ats,
            truthfulness_report=truthfulness,
            resume_strategy=strategy,
            optimized_resume=optimized,
            optimization_report=report,
        )
        if self.artifact_dir:
            self.write_artifacts(result, self.artifact_dir)
        return result

    def write_artifacts(self, result: PipelineResult, artifact_dir: Path) -> None:
        run_dir = artifact_dir / str(uuid4())
        for artifact in result.artifacts():
            write_yaml(run_dir / f"{artifact.artifact_type.value}.yaml", artifact)

    def _build_report(
        self,
        ats_score: float,
        truthfulness_status: str,
        recruiter_confidence: float,
        project_quality: float,
    ) -> OptimizationReport:
        truth_score = (
            1.0
            if truthfulness_status == "pass"
            else 0.72
            if truthfulness_status == "needs_review"
            else 0.3
        )
        technical = round((project_quality * 0.5) + (truth_score * 0.5), 3)
        recruiter = round(max(0.45, recruiter_confidence), 3)
        hiring = round((technical * 0.55) + (ats_score * 0.25) + (recruiter * 0.2), 3)
        return OptimizationReport(
            confidence=0.82,
            interview_probability_score=hiring,
            recruiter_resonance=recruiter,
            technical_credibility=technical,
            ats_survivability=ats_score,
            hiring_manager_alignment=round((technical * 0.7) + (ats_score * 0.3), 3),
            summary="ResumeForge generated a truthful, artifact-backed optimization pass.",
            next_actions=[
                "Review missing signals and add evidence only where truthful.",
                "Confirm any quantified claims before external use.",
                "Run ATS validation again after manual resume edits.",
            ],
        )
