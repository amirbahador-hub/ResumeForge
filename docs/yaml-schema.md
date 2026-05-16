# YAML Schema

ResumeForge is YAML-first. Agents exchange structured YAML artifacts backed by typed Pydantic schemas.

YAML artifacts make intermediate reasoning inspectable, testable, diffable, and reproducible.

## Shared Artifact Metadata

Every artifact should include:

```yaml
schema_version: 0.1.0
artifact_id: "uuid"
artifact_type: "role_analysis"
created_at: "2026-05-16T00:00:00Z"
agent_name: "role_analyzer"
source_artifacts: []
confidence: 0.82
assumptions: []
validation_errors: []
```

## role_analysis.yaml

```yaml
schema_version: 0.1.0
artifact_type: role_analysis
required_skills:
  - python
  - kubernetes
  - observability
preferred_skills:
  - langgraph
  - fastapi
implicit_signals:
  - startup mindset
  - high agency
  - AI-native workflows
seniority:
  level: senior
  confidence: 0.78
engineering_stack:
  languages:
    - python
  infrastructure:
    - kubernetes
  ai:
    - agents
    - evaluation
architecture_signals:
  - distributed systems
  - async workflows
hiring_priorities:
  - production ownership
  - technical depth
  - rapid execution
domain_context:
  - developer tooling
leadership_expectations:
  - cross-functional ownership
```

## recruiter_profile.yaml

```yaml
schema_version: 0.1.0
artifact_type: recruiter_profile
interests:
  - MCP
  - agentic workflows
  - startup builders
communication_style:
  label: concise_technical
  evidence:
    - "Public posts emphasize technical hiring criteria."
hiring_patterns:
  - "Highlights builders with shipped systems."
cultural_signals:
  - high agency
resume_implications:
  - "Use concise technical summary language."
```

## company_profile.yaml

```yaml
schema_version: 0.1.0
artifact_type: company_profile
engineering_culture:
  - product engineering
  - high ownership
architecture_patterns:
  - cloud-native services
ai_maturity:
  level: emerging
  confidence: 0.65
technical_stack:
  languages:
    - python
  platforms:
    - aws
hiring_philosophy:
  - values shipped work
organizational_values:
  - customer focus
```

## resume_analysis.yaml

```yaml
schema_version: 0.1.0
artifact_type: resume_analysis
technical_strengths:
  - backend systems
  - observability
weak_signals:
  - limited quantified impact
missing_signals:
  - AI evaluation experience
ats_weaknesses:
  - nonstandard project section heading
engineering_depth:
  systems_depth: 0.78
  architecture_maturity: 0.7
  operational_excellence: 0.74
project_quality:
  score: 0.8
leadership_indicators:
  - led migration project
architecture_indicators:
  - designed event-driven service
evidence_map:
  - claim: "Built observability pipeline"
    source: resume
    confidence: 0.92
```

## archetype.yaml

```yaml
schema_version: 0.1.0
artifact_type: archetype
primary_archetype: applied_ai_engineer
secondary_archetypes:
  - ai_native_workflow_engineer
expected_behavioral_signals:
  - high agency
expected_technical_signals:
  - python
  - agent orchestration
expected_project_types:
  - AI workflow systems
expected_language_style:
  - concise
  - technically specific
```

## ats_report.yaml

```yaml
schema_version: 0.1.0
artifact_type: ats_report
overall_score: 0.81
parser_safety:
  score: 0.9
  issues: []
keyword_coverage:
  score: 0.76
  covered:
    - python
  missing:
    - incident response
formatting_quality:
  score: 0.88
section_consistency:
  score: 0.84
semantic_matching:
  score: 0.79
readability:
  score: 0.86
```

## truthfulness_report.yaml

```yaml
schema_version: 0.1.0
artifact_type: truthfulness_report
overall_status: pass
unsupported_claims: []
needs_user_confirmation:
  - claim: "Reduced deployment time by 40%"
    reason: "Metric appears plausible but is not present in source evidence."
grounded_claims:
  - claim: "Built Python backend services"
    evidence_source: resume
    confidence: 0.95
interview_risks:
  - "AI evaluation experience is implied by project context but not explicit."
```

## resume_strategy.yaml

```yaml
schema_version: 0.1.0
artifact_type: resume_strategy
priority_signals:
  - distributed systems
  - AI-native workflows
  - observability
missing_signals:
  - public AI projects
  - technical writing
risk_signals:
  - weak ATS keyword coverage
optimization_actions:
  - "Move AI workflow project above generic web projects."
  - "Rewrite summary around backend ownership and agent systems."
```

## Schema Versioning

Schemas should use semantic versions. Breaking schema changes require migration helpers and fixture updates.

Recommended test fixtures:

- Minimal valid artifact
- Full valid artifact
- Missing required field
- Invalid confidence value
- Unsupported claim artifact
- Parser-safety failure artifact
