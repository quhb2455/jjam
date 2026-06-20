"""Validation stage for generated run artifacts."""

from __future__ import annotations

from pathlib import Path

from paper_agent.schemas import ValidationResult
from paper_agent.utils import bullet_list, write_text


REQUIRED_ARTIFACTS = [
    "paper_summary.md",
    "implementation_spec.md",
    "implementation_plan.md",
    "tooling_plan.md",
    "prototype_implementation.md",
    "assumptions.md",
]


class Validator:
    def validate(self, output_dir: Path) -> ValidationResult:
        checks: list[str] = []
        failures: list[str] = []
        for name in REQUIRED_ARTIFACTS:
            path = output_dir / name
            if path.exists() and path.read_text(encoding="utf-8").strip():
                checks.append(f"{name} exists and is non-empty")
            else:
                failures.append(f"{name} is missing or empty")
        return ValidationResult(passed=not failures, checks=checks, failures=failures)

    def write_output(self, output_dir: Path, result: ValidationResult) -> Path:
        status = "PASS" if result.passed else "FAIL"
        content = f"""# Validation Result

## Status
{status}

## Passed Checks
{bullet_list(result.checks)}

## Failures
{bullet_list(result.failures)}
"""
        return write_text(output_dir / "validation_result.md", content)
