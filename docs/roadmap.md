# Roadmap

ResumeForge should evolve from a local YAML-first agent pipeline into a full career intelligence platform for technical professionals.

## Phase 0: Documentation and Contracts

- Define architecture docs.
- Define agent responsibilities.
- Define YAML artifact schemas.
- Define truthfulness and ATS validation philosophy.
- Establish project terminology and non-goals.

## Phase 1: Core Python Foundation

- Create Python package structure.
- Add typed Pydantic schemas for all artifacts.
- Add YAML serialization and validation utilities.
- Add CLI for local pipeline execution.
- Add fixture-based schema tests.
- Add provider-agnostic LLM interfaces.

## Phase 2: Agent Orchestration

- Implement PydanticAI agent wrappers.
- Implement LangGraph DAG orchestration.
- Add async execution for parallel agents.
- Persist artifacts to local storage.
- Add deterministic validators for every artifact.
- Add execution traces and structured logs.

## Phase 3: Resume Intelligence MVP

- Parse resumes into structured sections.
- Build evidence maps.
- Implement Role Analyzer.
- Implement Resume Intelligence Agent.
- Implement Role Archetype Engine.
- Generate `role_analysis.yaml`, `resume_analysis.yaml`, and `archetype.yaml`.

## Phase 4: ATS and Truthfulness Gates

- Implement ATS formatting checks.
- Implement keyword and semantic coverage scoring.
- Implement claim-to-evidence validation.
- Block unsupported generated claims.
- Add interview defensibility scoring.
- Generate `ats_report.yaml` and `truthfulness_report.yaml`.

## Phase 5: Synthesis Engine

- Generate optimized resume variants.
- Generate optimization explanations.
- Generate missing-signal recommendations.
- Add resume diffing.
- Compare original and optimized ATS scores.
- Produce a structured optimization report.

## Phase 6: Recruiter and Company Intelligence

- Implement recruiter profile ingestion from user-provided public context.
- Implement company profile analysis.
- Add cultural and communication-style signals.
- Integrate recruiter-aware synthesis without compromising truthfulness.

## Phase 7: Observability and Reproducibility

- Add OpenTelemetry traces.
- Add agent execution graphs.
- Add YAML lineage tracking.
- Add run manifests.
- Add deterministic replay from saved artifacts.
- Add confidence calibration reports.

## Phase 8: MCP and Harness Integration

- Support MCP-compatible tools.
- Support modular agent harnesses.
- Add external enrichment interfaces.
- Add distributed orchestration mode.
- Add task queue integration with Redis or compatible backends.

## Phase 9: Advanced Career Intelligence

- Add engineering signal scoring.
- Add interview prediction engine.
- Add portfolio and GitHub relevance analysis.
- Add role-fit trend analysis across multiple jobs.
- Add career gap planning.
- Add autonomous career agents for ongoing opportunity monitoring.

## Long-Term Vision

ResumeForge should become career intelligence infrastructure:

- A career operating system for technical professionals.
- A structured hiring intelligence platform.
- A recruiter-aware optimization engine.
- An engineering signal analysis system.
- A truthful alternative to resume keyword spam.
