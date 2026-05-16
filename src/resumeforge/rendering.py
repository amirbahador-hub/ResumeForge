from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

from resumeforge.providers import TailoredResumeContent
from resumeforge.resume_templates import ResumeTemplateSpec

_STYLESHEET_LINK_RE = re.compile(
    r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*/?>',
    flags=re.IGNORECASE,
)


def _template_dir(template: ResumeTemplateSpec) -> Path:
    root = Path(__file__).resolve().parents[2]
    path = root / template.asset_dir
    if not path.is_dir():
        raise FileNotFoundError(f"Template asset directory not found: {path}")
    return path


def _inline_stylesheets(html: str, template_dir: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        href = match.group(1)
        if href.startswith(("http://", "https://", "data:")):
            return match.group(0)
        css_path = (template_dir / href).resolve()
        if not css_path.is_file():
            return match.group(0)
        css_text = css_path.read_text(encoding="utf-8")
        return f"<style>\n{css_text}\n</style>"

    return _STYLESHEET_LINK_RE.sub(replace, html)


def render_resume_html(content: TailoredResumeContent, template: ResumeTemplateSpec) -> str:
    template_dir = _template_dir(template)
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    jinja_template = env.get_template("index.html")
    rendered = jinja_template.render(content=content)
    return _inline_stylesheets(rendered, template_dir)


async def render_resume_pdf(
    pdf_path: Path,
    content: TailoredResumeContent,
    template: ResumeTemplateSpec,
) -> None:
    from playwright.async_api import async_playwright

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    html = render_resume_html(content, template)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="load")
            await page.evaluate(
                "() => (document.fonts && document.fonts.ready)"
                " ? document.fonts.ready : Promise.resolve()"
            )
            await page.pdf(
                path=str(pdf_path),
                format="Letter",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
        finally:
            await browser.close()
