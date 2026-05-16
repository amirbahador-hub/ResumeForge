# Role Archetypes

Role archetypes are reusable hiring patterns that help ResumeForge interpret implicit expectations behind a job description.

An archetype is not a rigid label. It is a weighted model of expected signals, language, projects, and evaluation criteria.

## Example Archetypes

### Applied AI Engineer

Expected technical signals:

- LLM application architecture
- Retrieval, agents, or evaluation systems
- Python backend experience
- Model provider integration
- Prompt and tool orchestration
- Production reliability

Expected behavioral signals:

- Product judgment
- Fast iteration
- Evaluation mindset
- Comfort with ambiguous requirements

Strong projects:

- Agentic workflows
- RAG systems
- AI evaluation harnesses
- Model observability
- Internal AI tooling

### Startup Infrastructure Engineer

Expected technical signals:

- Kubernetes or container orchestration
- Observability
- CI/CD
- Cloud infrastructure
- Incident response
- Cost and reliability tradeoffs

Expected behavioral signals:

- High agency
- Ownership under ambiguity
- Pragmatic engineering
- Operational maturity

Strong projects:

- Infrastructure automation
- Observability pipelines
- Deployment platforms
- Reliability improvements

### Forward Deployed Engineer

Expected technical signals:

- Full-stack or backend implementation
- Customer-facing technical delivery
- Rapid prototyping
- Integration work
- Production debugging

Expected behavioral signals:

- Communication clarity
- Business context awareness
- Strong ownership
- Ability to translate vague needs into systems

Strong projects:

- Customer integrations
- Internal platforms
- Workflow automation
- Enterprise deployments

### AI-Native Workflow Engineer

Expected technical signals:

- Agent orchestration
- MCP or tool protocols
- Workflow automation
- Human-in-the-loop systems
- Evaluation and observability

Expected behavioral signals:

- Systems thinking
- Experimentation
- Strong product-engineering feedback loops
- Comfort with emerging tooling

Strong projects:

- Agent harnesses
- Developer productivity tools
- AI workflow platforms
- Structured automation systems

## Archetype Output

`archetype.yaml`

```yaml
schema_version: 0.1.0
artifact_type: archetype
primary_archetype: applied_ai_engineer
secondary_archetypes:
  - ai_native_workflow_engineer
confidence: 0.84
expected_technical_signals:
  - python
  - agent orchestration
  - evaluation pipelines
  - production reliability
expected_behavioral_signals:
  - high agency
  - product judgment
  - ambiguity tolerance
expected_project_types:
  - RAG systems
  - AI tooling
  - agentic workflows
language_style:
  - concrete
  - technically specific
  - impact oriented
resume_strategy:
  prioritize:
    - shipped AI systems
    - evaluation and observability
    - backend ownership
  de_emphasize:
    - generic frontend claims
```

## Archetype Detection

Inputs:

- Job description
- Company profile
- Role analysis
- Recruiter signals

Detection should use weighted evidence:

- Explicit title terms
- Required skills
- Repeated verbs
- Product and domain context
- Stack indicators
- Team descriptions
- Seniority language
- Company stage

## How Archetypes Influence Synthesis

Archetypes guide:

- Resume summary emphasis
- Skills grouping
- Project ordering
- Bullet phrasing
- Missing-signal recommendations
- ATS weighting
- Interview defensibility checks

Archetypes must not cause unsupported claims. They only decide which real evidence should be foregrounded.
