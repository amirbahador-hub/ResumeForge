from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


def to_plain_data(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json", exclude_none=True)


def dump_yaml(model: BaseModel) -> str:
    return yaml.safe_dump(to_plain_data(model), sort_keys=False, allow_unicode=False)


def write_yaml(path: Path, model: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_yaml(model), encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping: {path}")
    return data
