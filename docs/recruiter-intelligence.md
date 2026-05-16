# Recruiter Intelligence

Recruiter intelligence helps ResumeForge adapt language, emphasis, and presentation to the human screening context while preserving truthfulness.

The goal is not to manipulate recruiters or infer sensitive personal traits. The goal is to understand public hiring signals, communication style, and role emphasis.

## Inputs

- Recruiter name
- Recruiter profile
- Recruiter posts
- Public hiring activity
- Company hiring pages
- Job description
- Public company signals

## Analyzed Signals

- Preferred communication style
- Technical interests
- Hiring themes
- Repeated terminology
- Role families commonly recruited
- Startup, enterprise, research, or product orientation
- Cultural signals from public job posts
- Candidate attributes emphasized in public content

## Boundaries

ResumeForge should not infer or use sensitive attributes such as age, ethnicity, religion, health, political beliefs, or private personal information.

It should also avoid overfitting the resume to a single recruiter. Recruiter intelligence is a prioritization signal, not a source of truth.

## Output Artifact

`recruiter_profile.yaml`

```yaml
schema_version: 0.1.0
artifact_type: recruiter_profile
recruiter:
  name: "Example Recruiter"
confidence: 0.72
communication_style:
  summary: concise_technical
  evidence:
    - source: public_post
      observation: "Uses short posts focused on AI infrastructure roles."
interests:
  - name: MCP
    confidence: 0.8
  - name: agentic workflows
    confidence: 0.76
  - name: startup builders
    confidence: 0.69
hiring_patterns:
  - "Highlights candidates who show shipped systems, not only model usage."
resume_implications:
  - "Prioritize concrete AI workflow infrastructure experience."
  - "Keep summary concise and technical."
assumptions:
  - "Analysis is based only on public activity supplied by the user."
```

## Resume Implications

Recruiter intelligence can affect:

- Summary tone
- Ordering of project bullets
- Which truthful evidence is emphasized
- Level of technical specificity
- Company or mission alignment language
- Cover note or outreach message style

It must not affect:

- Factual claims
- Employment dates
- Project ownership
- Metrics
- Skill proficiency beyond evidence

## Confidence Handling

Low-confidence recruiter signals should be surfaced in the optimization report, not silently baked into resume claims.

Examples:

- High confidence: recruiter repeatedly posts about AI infrastructure roles.
- Medium confidence: recruiter uses concise technical language in several posts.
- Low confidence: one post mentions a technology once.

## Ethical Constraints

Recruiter intelligence should be recruiter-aware, not recruiter-invasive. Only public, user-provided, or user-authorized information should be used.
