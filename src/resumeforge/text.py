from __future__ import annotations

import re
from collections.abc import Iterable

TECH_TERMS = {
    "ai": ["ai", "llm", "rag", "agent", "agents", "langgraph", "mcp", "openai", "evaluation"],
    "languages": ["python", "typescript", "javascript", "go", "rust", "java", "sql"],
    "backend": ["fastapi", "django", "flask", "postgres", "redis", "api", "microservices"],
    "infra": ["kubernetes", "docker", "aws", "gcp", "azure", "terraform", "observability"],
    "ops": ["incident", "slo", "monitoring", "tracing", "opentelemetry", "ci/cd", "deployment"],
}

SIGNAL_TERMS = {
    "startup mindset": ["startup", "founding", "0 to 1", "ambiguous", "high agency"],
    "high agency": ["ownership", "owned", "lead", "led", "autonomous", "high agency"],
    "production ownership": ["production", "on-call", "incident", "reliability", "slo"],
    "architecture maturity": [
        "architecture",
        "designed",
        "distributed",
        "event-driven",
        "scalable",
    ],
    "AI-native workflows": ["agent", "llm", "rag", "mcp", "ai-native", "workflow"],
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def contains_any(text: str, terms: Iterable[str]) -> bool:
    normalized = normalize_text(text)
    return any(term.lower() in normalized for term in terms)


def extract_terms(text: str, vocabulary: Iterable[str]) -> list[str]:
    normalized = normalize_text(text)
    found = [
        term
        for term in vocabulary
        if re.search(rf"(?<![a-z0-9]){re.escape(term.lower())}(?![a-z0-9])", normalized)
    ]
    return sorted(set(found), key=str.lower)


def score_coverage(found: int, total: int) -> float:
    if total <= 0:
        return 1.0
    return round(min(1.0, found / total), 3)


def infer_seniority(text: str) -> str:
    normalized = normalize_text(text)
    if contains_any(normalized, ["staff", "principal", "tech lead", "architect"]):
        return "staff_plus"
    if contains_any(normalized, ["senior", "lead", "5+", "7+", "8+"]):
        return "senior"
    if contains_any(normalized, ["junior", "entry level", "new grad"]):
        return "junior"
    if contains_any(normalized, ["mid-level", "mid level", "3+"]):
        return "mid"
    return "unspecified"


def all_known_terms() -> list[str]:
    terms: list[str] = []
    for values in TECH_TERMS.values():
        terms.extend(values)
    return sorted(set(terms), key=str.lower)
