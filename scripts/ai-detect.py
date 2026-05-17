#!/usr/bin/env python3
"""Heuristic AI-generated-text detector for resume content.

Some ATS and recruiter tools now flag resumes suspected of being written by
an LLM. Real detectors (GPTZero, Originality.ai, Copyleaks, ZeroGPT) use
perplexity + burstiness models we can't easily replicate locally, but the
phrase-level and structural tells are well known and a curated heuristic
catches the most common offenders.

Heuristics applied:
    1. Em-dash density. LLMs love `—`. Humans rarely use more than 1 every
       100 words; LLM output often runs 3–6x that.
    2. Tier-1 phrase tells. Words/phrases very strongly associated with LLM
       prose ("delve", "tapestry", "in today's fast-paced", "leverage" as a
       verb, "harness the power", etc.).
    3. Tier-2 phrase tells. Words that are sometimes legitimate in
       engineering writing but score on every detector ("robust",
       "seamlessly", "comprehensive", "end-to-end", "ecosystem").
    4. Triadic-pattern density. "X, Y, and Z" repeated 10+ times in a
       short document is a classic LLM parallelism signature.

Usage:
    scripts/ai-detect.py <file>             # .pdf, .md, .html, .txt
    scripts/ai-detect.py <pdf> --strict     # exit non-zero on MODERATE+

Score 0–100; lower is more human-sounding. Exit code 0 if score < 30
(default) or < 20 (--strict).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# Tier-1: rarely legitimate in a tailored resume.
AI_PHRASES_HIGH = [
    "delve", "tapestry", "intricate", "navigate the", "navigating the",
    "in today's fast-paced", "in the realm of", "embark on", "embark upon",
    "in essence", "it is important to note", "it's important to note",
    "comprehensive understanding", "holistic", "paradigm shift",
    "groundbreaking", "cutting-edge", "state-of-the-art",
    "in conclusion", "furthermore,", "moreover,",
    "by leveraging", "leveraging the", "harness the power",
    "robust solution", "robust framework", "elevate your", "elevate the",
    "foster a", "foster an", "underscore the", "pivotal role",
    "plethora of", "myriad of", "testament to",
    "ever-evolving", "ever-changing", "dynamic landscape",
    "in the world of", "world of",
]

# Tier-2: sometimes legitimate, but every detector still scores them.
AI_PHRASES_MED = [
    "leverage", "leveraged", "leverages",
    "seamless", "seamlessly",
    "robust", "comprehensive", "ecosystem",
    "scalable solution", "end-to-end", "end to end",
    "multifaceted", "synergy",
    "best-in-class", "world-class",
    "drive innovation", "transformative",
    "unparalleled", "unprecedented",
    "tailored to", "tailored for",
]

TRIADIC_RE = re.compile(r"\b(\w+),\s+(\w+),\s+(?:and\s+)?(\w+)\b")
EMDASH_RE = re.compile(r"—|–|--")
WORD_RE = re.compile(r"\b\w+\b")


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore
            return "\n".join(
                (p.extract_text() or "") for p in PdfReader(str(path)).pages
            )
        except Exception:
            md = path.parent / "tailored_resume.md"
            if md.exists():
                return md.read_text(encoding="utf-8")
            return ""
    if suffix in {".html", ".htm"}:
        raw = path.read_text(encoding="utf-8")
        return re.sub(r"<[^>]+>", " ", raw)
    return path.read_text(encoding="utf-8")


def score_text(text: str) -> tuple[int, list[str]]:
    word_count = len(WORD_RE.findall(text))
    word_count = max(word_count, 1)
    lower = text.lower()

    score = 0
    triggers: list[str] = []

    emdashes = len(EMDASH_RE.findall(text))
    per100 = emdashes / word_count * 100
    if per100 > 1.0:
        bump = min(int(per100 * 5), 30)
        score += bump
        triggers.append(
            f"em-dash density {per100:.1f}/100w ({emdashes} in {word_count} words) [+{bump}]"
        )

    for phrase in AI_PHRASES_HIGH:
        cnt = lower.count(phrase.lower())
        if cnt:
            bump = cnt * 8
            score += bump
            triggers.append(f"high-tell {phrase!r} x{cnt} [+{bump}]")

    for phrase in AI_PHRASES_MED:
        cnt = lower.count(phrase.lower())
        if cnt:
            bump = cnt * 3
            score += bump
            triggers.append(f"medium-tell {phrase!r} x{cnt} [+{bump}]")

    triads = TRIADIC_RE.findall(text)
    triad_ratio = len(triads) / word_count
    if triad_ratio > 0.015 and len(triads) > 6:
        bump = min(int(len(triads) * 1.2), 15)
        score += bump
        triggers.append(
            f"triadic patterns: {len(triads)} instances ({triad_ratio*100:.1f}%) [+{bump}]"
        )

    score = min(score, 100)
    return score, triggers


def label_for(score: int) -> str:
    if score < 20:
        return "LOW (human-sounding)"
    if score < 40:
        return "MODERATE"
    if score < 60:
        return "HIGH"
    return "VERY HIGH"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Heuristic AI-tell scorer for resumes.")
    p.add_argument("path", help="Path to resume file (.pdf, .md, .html, .txt)")
    p.add_argument("--strict", action="store_true",
                   help="Fail on score >= 20 (default: 30)")
    args = p.parse_args(argv[1:])

    path = Path(args.path)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    text = extract_text(path)
    if not text.strip():
        print("error: no text extracted", file=sys.stderr)
        return 2

    score, triggers = score_text(text)
    word_count = len(WORD_RE.findall(text))

    print(f"text source:    {path}")
    print(f"word count:     {word_count}")
    print()
    if triggers:
        print("triggers:")
        for t in triggers:
            print(f"  - {t}")
    else:
        print("triggers: none")
    print()
    print(f"AI-suspicion:   {score}/100   [{label_for(score)}]")

    threshold = 20 if args.strict else 30
    return 0 if score < threshold else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
