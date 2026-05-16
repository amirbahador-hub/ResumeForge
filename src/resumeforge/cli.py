from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import json

from resumeforge.documents import read_document
from resumeforge.pipeline import ResumeForgePipeline
from resumeforge.providers import TailoredResumeContent, select_provider
from resumeforge.rendering import render_resume_pdf
from resumeforge.resume_templates import TEMPLATE_CATALOG, get_template
from resumeforge.schemas import UserInput
from resumeforge.tailoring import tailor_resume
from resumeforge.yaml_io import dump_yaml

app = typer.Typer(help="ResumeForge career intelligence pipeline.")


@app.command()
def run(
    job: Path = typer.Option(
        ..., "--job", exists=True, readable=True, help="Job description text file."
    ),
    resume: Path = typer.Option(
        ..., "--resume", exists=True, readable=True, help="Resume text/markdown file."
    ),
    output: Path = typer.Option(
        Path("artifacts"), "--output", help="Directory for YAML artifacts."
    ),
    company: str | None = typer.Option(None, "--company", help="Target company name."),
    recruiter: str | None = typer.Option(None, "--recruiter", help="Recruiter name."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of YAML summary."),
) -> None:
    """Run the deterministic ResumeForge pipeline."""

    user_input = UserInput(
        job_description=read_document(job),
        resume=read_document(resume),
        company_name=company,
        recruiter_name=recruiter,
    )
    result = asyncio.run(ResumeForgePipeline(artifact_dir=output).run(user_input))
    report = result.optimization_report
    if json_output:
        typer.echo(json.dumps(report.model_dump(mode="json"), indent=2))
    else:
        typer.echo(dump_yaml(report))


@app.command()
def tailor(
    job: Path = typer.Option(
        Path("examples/jd.md"),
        "--job",
        exists=True,
        readable=True,
        help="Job description file.",
    ),
    resume: Path = typer.Option(
        Path("examples/my_resume.pdf"),
        "--resume",
        exists=True,
        readable=True,
        help="Resume file. Supports PDF, Markdown, and text.",
    ),
    output: Path = typer.Option(
        Path("artifacts/tailored"),
        "--output",
        help="Directory for tailored resume outputs.",
    ),
    provider: str = typer.Option(
        "auto",
        "--provider",
        help="Provider selection: auto, openai, anthropic, none.",
    ),
    template: str | None = typer.Option(
        None,
        "--template",
        help=(
            "Template selection: classic-clean, editorial-compact, modern-line. "
            "If omitted, the CLI prompts."
        ),
    ),
    company: str | None = typer.Option(None, "--company", help="Target company name."),
    recruiter: str | None = typer.Option(None, "--recruiter", help="Recruiter name."),
) -> None:
    """Create a tailored resume and a change rationale report."""

    provider_config = select_provider(provider)
    user_input = UserInput(
        job_description=read_document(job),
        resume=read_document(resume),
        company_name=company,
        recruiter_name=recruiter,
    )
    summary = asyncio.run(tailor_resume(user_input, output, provider_config, template))
    _print_tailor_summary(summary, provider_config)


@app.command()
def render(
    content: Path = typer.Option(
        ...,
        "--content",
        exists=True,
        readable=True,
        help="Path to a tailored_resume.json produced by `tailor`.",
    ),
    output: Path = typer.Option(
        ...,
        "--output",
        help=(
            "Output PDF path, or output directory when --all-templates is used."
        ),
    ),
    template: str | None = typer.Option(
        None,
        "--template",
        help="Template id (classic-clean, editorial-compact, modern-line, portfolio-mirror).",
    ),
    all_templates: bool = typer.Option(
        False,
        "--all-templates",
        help="Render the content once per template into --output (treated as a directory).",
    ),
) -> None:
    """Re-render a saved tailored resume into a PDF without rerunning the LLM pipeline."""

    data = json.loads(content.read_text(encoding="utf-8"))
    resume_content = TailoredResumeContent.model_validate(data)

    if all_templates:
        output.mkdir(parents=True, exist_ok=True)
        for spec in TEMPLATE_CATALOG:
            pdf_path = output / f"{content.stem}.{spec.id}.pdf"
            asyncio.run(render_resume_pdf(pdf_path, resume_content, spec))
            typer.echo(f"Rendered {spec.display_name}: {pdf_path}")
        return

    if template is None:
        raise typer.BadParameter("Provide --template or use --all-templates.")
    spec = get_template(template)
    asyncio.run(render_resume_pdf(output, resume_content, spec))
    typer.echo(f"Rendered {spec.display_name}: {output}")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
) -> None:
    """Start the FastAPI service."""

    import uvicorn

    uvicorn.run("resumeforge.api:api", host=host, port=port, reload=False)


if __name__ == "__main__":
    app()


def _print_tailor_summary(summary, provider_config) -> None:
    console = Console()
    baseline = summary.baseline_report.optimization_report
    tailored = summary.tailored_report.optimization_report
    score_delta = round(
        tailored.interview_probability_score - baseline.interview_probability_score,
        3,
    )

    header = Text("ResumeForge Tailoring Complete", style="bold white")
    console.print(Panel(header, border_style="magenta"))
    provider_line = f"[bold cyan]Provider:[/bold cyan] {provider_config.provider}"
    if provider_config.model:
        provider_line += f"  [bold cyan]Model:[/bold cyan] {provider_config.model}"
    console.print(provider_line)
    console.print(f"[bold green]Tailored PDF:[/bold green] {summary.tailored_pdf}")
    console.print(f"[bold green]Tailored markdown:[/bold green] {summary.tailored_markdown}")
    console.print(f"[bold green]Change report:[/bold green] {summary.changes_report}")
    console.print(f"[bold green]Follow-up questions:[/bold green] {summary.questions_report}")

    table = Table(title="Score Comparison", show_lines=False, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Before", style="white")
    table.add_column("After", style="white")
    table.add_column("Delta", style="white")
    table.add_row(
        "Interview probability",
        f"{baseline.interview_probability_score}",
        f"{tailored.interview_probability_score}",
        f"{score_delta}",
    )
    table.add_row(
        "ATS survivability",
        f"{baseline.ats_survivability}",
        f"{tailored.ats_survivability}",
        f"{round(tailored.ats_survivability - baseline.ats_survivability, 3)}",
    )
    table.add_row(
        "Technical credibility",
        f"{baseline.technical_credibility}",
        f"{tailored.technical_credibility}",
        f"{round(tailored.technical_credibility - baseline.technical_credibility, 3)}",
    )
    console.print(table)

    console.print(
        Panel(
            "\n".join(
                [
                    "Truthfulness status: "
                    f"{summary.tailored_report.truthfulness_report.overall_status}",
                    f"Template: {summary.template.display_name}",
                    f"Changed items: {len(summary.tailoring.changed_items)}",
                    *[
                        f"- {item.section}: {item.why}"
                        for item in summary.tailoring.changed_items[:4]
                    ],
                ]
            ),
            title="What Changed",
            border_style="green",
        )
    )
    if summary.tailoring.questions_for_user:
        console.print(
            Panel(
                "\n".join(f"- {question}" for question in summary.tailoring.questions_for_user),
                title="Pending Questions",
                border_style="yellow",
            )
        )
