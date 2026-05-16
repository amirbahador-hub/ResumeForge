from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeTemplateSpec:
    id: str
    display_name: str
    asset_dir: str
    description: str
    aliases: tuple[str, ...]


TEMPLATE_CATALOG: list[ResumeTemplateSpec] = [
    ResumeTemplateSpec(
        id="classic-clean",
        display_name="Classic Clean",
        asset_dir="templates/classic-clean",
        description="Classic centered-header, single-column ATS template with a strong hierarchy.",
        aliases=("jake",),
    ),
    ResumeTemplateSpec(
        id="editorial-compact",
        display_name="Editorial Compact",
        asset_dir="templates/editorial-compact",
        description=(
            "Dense, uppercase-section ATS template with compact spacing and full-width flow."
        ),
        aliases=("mteck",),
    ),
    ResumeTemplateSpec(
        id="modern-line",
        display_name="Modern Line",
        asset_dir="templates/modern-line",
        description=(
            "Minimal one-column ATS template inspired by Rover-style layouts and practical "
            "typography."
        ),
        aliases=("rover",),
    ),
    ResumeTemplateSpec(
        id="portfolio-mirror",
        display_name="Portfolio Mirror",
        asset_dir="templates/portfolio-mirror",
        description=(
            "Mirrors the candidate's own resume layout: stacked name on the left, "
            "right-aligned contact column, and uppercase section heads with thin rules."
        ),
        aliases=("portfolio", "mirror"),
    ),
]


def get_template(template_id: str) -> ResumeTemplateSpec:
    for template in TEMPLATE_CATALOG:
        if template.id == template_id or template_id in template.aliases:
            return template
    raise KeyError(template_id)


def default_template() -> ResumeTemplateSpec:
    return TEMPLATE_CATALOG[0]
