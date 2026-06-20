"""Small utility helpers for markdown output."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Iterable


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str) -> Path:
    ensure_dir(path.parent)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return path


def bullet_list(items: Iterable[str]) -> str:
    values = list(items)
    if not values:
        return "- None"
    return "\n".join(f"- {item}" for item in values)


def numbered_list(items: Iterable[str]) -> str:
    values = list(items)
    if not values:
        return "1. None"
    return "\n".join(f"{idx}. {item}" for idx, item in enumerate(values, start=1))


def simple_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(cell.replace("\n", " ") for cell in row) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def dataclass_dict(value: object) -> dict:
    if not is_dataclass(value):
        raise TypeError(f"Expected dataclass, got {type(value)!r}")
    return asdict(value)
