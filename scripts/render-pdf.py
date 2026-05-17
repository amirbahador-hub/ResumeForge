#!/usr/bin/env python3
"""Render an HTML file to PDF using Playwright's bundled Chromium.

Usage:
    python3 scripts/render-pdf.py <input.html> <output.pdf>

Why Playwright: it bundles its own Chromium, so we don't depend on a
system Chrome install at a hardcoded path. Works identically on macOS,
Linux, and Windows.

Install once:
    pip install playwright
    playwright install chromium
"""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render-pdf.py <input.html> <output.pdf>", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1]).resolve()
    output_path = Path(sys.argv[2]).resolve()

    if not input_path.is_file():
        print(f"error: input HTML not found: {input_path}", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "error: playwright is not installed.\n"
            "  pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(input_path.as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(output_path),
            format="Letter",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()

    if not output_path.is_file():
        print("error: render failed, no PDF produced", file=sys.stderr)
        return 1

    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
