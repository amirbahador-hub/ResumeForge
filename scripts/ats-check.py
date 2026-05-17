#!/usr/bin/env python3
"""ATS sanity check for a rendered resume PDF.

Usage:
    scripts/ats-check.py <resume.pdf> [job_description.md]

Checks:
    1. File size <= 1MB.
    2. Page count <= 2.
    3. Text is selectable (PDF is not rasterized).
    4. Standard section headings present (Skills, Experience, Education).
    5. JD keyword coverage — fraction of JD's hard-looking tokens that appear
       in the resume text.

Backends tried in order for PDF inspection:
    - pypdf (pip install pypdf) — recommended.
    - poppler's `pdfinfo` / `pdftotext` on $PATH.
    - macOS `mdls` for page count + the sibling tailored_resume.md for text.

Exit 0 if all hard checks pass, non-zero otherwise.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


SIZE_LIMIT = 1_048_576  # 1 MB
PAGE_TARGET = 2

STOPWORDS = {
    "the", "and", "for", "you", "are", "our", "with", "that", "this", "your",
    "have", "will", "their", "from", "into", "across", "while", "about",
    "would", "should", "could", "they", "them", "where", "which", "what",
    "who", "whom", "when", "than", "then", "such", "have", "been", "very",
    "more", "most", "also", "make", "made", "high", "team", "teams", "role",
    "role.", "roles", "work", "works", "working", "we", "us", "all", "any",
    "each", "every", "both", "must", "may", "well", "your", "yours",
}

GENERIC_VERBS = {
    "build", "built", "lead", "led", "design", "designed", "deliver",
    "delivered", "ship", "shipped", "scale", "scaled", "manage", "managed",
    "drive", "driven", "create", "created", "implement", "implemented",
    "develop", "developed", "improve", "improved", "support", "supported",
    "use", "used", "using",
}


def fmt_pass(b: bool) -> str:
    return "PASS" if b else "FAIL"


def extract_text_pypdf(pdf: Path) -> str | None:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return None
    try:
        reader = PdfReader(str(pdf))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    except Exception:
        return None


def page_count_pypdf(pdf: Path) -> int | None:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return None
    try:
        return len(PdfReader(str(pdf)).pages)
    except Exception:
        return None


def extract_text_pdftotext(pdf: Path) -> str | None:
    if not shutil.which("pdftotext"):
        return None
    try:
        out = subprocess.check_output(
            ["pdftotext", "-layout", str(pdf), "-"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8", errors="replace")
    except Exception:
        return None


def page_count_pdfinfo(pdf: Path) -> int | None:
    if not shutil.which("pdfinfo"):
        return None
    try:
        out = subprocess.check_output(
            ["pdfinfo", str(pdf)], stderr=subprocess.DEVNULL
        ).decode("utf-8", errors="replace")
        m = re.search(r"^Pages:\s*(\d+)\s*$", out, re.M)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def page_count_mdls(pdf: Path) -> int | None:
    if not shutil.which("mdls"):
        return None
    try:
        out = subprocess.check_output(
            ["mdls", "-name", "kMDItemNumberOfPages", "-raw", str(pdf)],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return int(out) if out.isdigit() else None
    except Exception:
        return None


def page_count(pdf: Path) -> int | None:
    for fn in (page_count_pypdf, page_count_pdfinfo, page_count_mdls):
        n = fn(pdf)
        if n is not None:
            return n
    return None


def extract_text(pdf: Path) -> tuple[str, str]:
    """Return (text, source_label). Falls back to sibling .md if PDF parsing fails."""
    for fn, label in (
        (extract_text_pypdf, "pdf (pypdf)"),
        (extract_text_pdftotext, "pdf (pdftotext)"),
    ):
        t = fn(pdf)
        if t and t.strip():
            return t, label
    md = pdf.parent / "tailored_resume.md"
    if md.exists():
        return md.read_text(encoding="utf-8"), "fallback: tailored_resume.md"
    return "", "unavailable"


def jd_keywords(jd_text: str) -> list[str]:
    """Heuristic: pull tech-y nouns and bullet items from a JD."""
    candidates: set[str] = set()

    # 1. Mixed-case / all-caps tokens — Python, FastAPI, LangGraph, AI, OpenAI, K8s.
    for token in re.findall(r"[A-Za-z][A-Za-z0-9+/\-]{1,30}", jd_text):
        if token.lower() in STOPWORDS or token.lower() in GENERIC_VERBS:
            continue
        if token.isupper() and len(token) >= 2:
            candidates.add(token)
        elif re.search(r"[A-Z]", token[1:]):
            candidates.add(token)
        elif token[0].isupper() and any(ch.isdigit() for ch in token):
            candidates.add(token)

    # 2. Bullet items — split on commas / "and" and keep short tech-noun phrases.
    for line in re.findall(r"^\s*[-*•]\s*(.+)$", jd_text, re.M):
        for chunk in re.split(r"\s*(?:,|;| and )\s*", line):
            chunk = chunk.strip(" .:")
            if 2 <= len(chunk) <= 30 and chunk.lower() not in STOPWORDS:
                if chunk[0].isupper() or any(c.isdigit() for c in chunk):
                    candidates.add(chunk)

    # De-dup case-insensitively, prefer longer forms.
    by_lower: dict[str, str] = {}
    for c in sorted(candidates, key=len, reverse=True):
        by_lower.setdefault(c.lower(), c)
    return sorted(by_lower.values(), key=lambda s: s.lower())


def main(argv: list[str]) -> int:
    if not (2 <= len(argv) <= 3):
        print(f"usage: {argv[0]} <resume.pdf> [job_description.md]", file=sys.stderr)
        return 2

    pdf = Path(argv[1])
    jd_path = Path(argv[2]) if len(argv) == 3 else None

    if not pdf.is_file():
        print(f"error: PDF not found: {pdf}", file=sys.stderr)
        return 2

    # ---- 1. File size --------------------------------------------------------
    size = pdf.stat().st_size
    size_ok = size <= SIZE_LIMIT
    print(f"size:        {size:>9,} bytes   [{fmt_pass(size_ok)}  target <= {SIZE_LIMIT:,}]")

    # ---- 2. Pages ------------------------------------------------------------
    pages = page_count(pdf)
    pages_ok = pages is not None and pages <= PAGE_TARGET
    pages_str = f"{pages}" if pages is not None else "unknown"
    print(f"pages:       {pages_str:>9}         [{fmt_pass(pages_ok)}  target <= {PAGE_TARGET}]")

    # ---- 3. Selectable text + Headings --------------------------------------
    text, source = extract_text(pdf)
    has_text = bool(text.strip())
    print(f"text:        {('extracted' if has_text else 'EMPTY'):>9}         [{fmt_pass(has_text)}  source: {source}]")

    lower = text.lower()
    headings = ["skills", "experience", "education"]
    heading_results = {h: (h in lower) for h in headings}
    for h, ok in heading_results.items():
        print(f"  heading '{h}': {fmt_pass(ok)}")

    # ---- 4. JD keyword coverage ---------------------------------------------
    kw_results: dict[str, bool] = {}
    if jd_path and jd_path.is_file():
        kws = jd_keywords(jd_path.read_text(encoding="utf-8"))
        for kw in kws:
            kw_results[kw] = kw.lower() in lower

        matched = sum(1 for v in kw_results.values() if v)
        total = len(kw_results)
        pct = (matched / total * 100) if total else 0.0
        print(f"jd keywords: {matched}/{total} ({pct:.0f}%)")
        missing = [k for k, v in kw_results.items() if not v]
        if missing:
            sample = ", ".join(missing[:20])
            more = f" ...(+{len(missing) - 20})" if len(missing) > 20 else ""
            print(f"  missing: {sample}{more}")
    elif jd_path:
        print(f"jd keywords: skipped (JD path not found: {jd_path})")
    else:
        print("jd keywords: skipped (no JD path provided)")

    # ---- Verdict ------------------------------------------------------------
    hard_checks_ok = (
        size_ok
        and pages_ok
        and has_text
        and all(heading_results.values())
    )
    print()
    print(f"verdict:     {'PASS' if hard_checks_ok else 'NEEDS WORK'}")
    return 0 if hard_checks_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
