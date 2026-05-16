from __future__ import annotations

from resumeforge.providers import _parse_tailoring_result


def test_parse_tailoring_result_accepts_fenced_json() -> None:
    result = _parse_tailoring_result(
        """```json
        {
          "content": {
            "name": "Jane Doe",
            "headline": "Senior Engineer",
            "contact": {"email": "jane@example.com"},
            "summary": "Senior engineer.",
            "skill_groups": [],
            "experience": [],
            "projects": [],
            "open_source": [],
            "education": [],
            "languages": [],
            "extra_sections": []
          },
          "changed_items": [
            {
              "section": "Summary",
              "before": "Old",
              "after": "New",
              "why": "Better alignment",
              "evidence": "Source resume"
            }
          ],
          "questions_for_user": [],
          "risks_or_assumptions": []
        }
        ```"""
    )

    assert result.content.name == "Jane Doe"
    assert result.content.contact.email == "jane@example.com"
    assert result.changed_items[0].section == "Summary"
