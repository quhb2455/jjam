"""Final report generation."""

from __future__ import annotations

from pathlib import Path

from paper_agent.schemas import ImplementationPlan, ImplementationResult, PaperAnalysisResult, ReviewResult, ToolingPlan, ValidationResult
from paper_agent.utils import bullet_list, write_text


class FinalReporter:
    def write_output(
        self,
        output_dir: Path,
        analysis: PaperAnalysisResult,
        plan: ImplementationPlan,
        tooling: ToolingPlan,
        implementation: ImplementationResult,
        validation: ValidationResult,
        review: ReviewResult,
    ) -> Path:
        content = f"""# Final Report

## Paper Summary
{analysis.summary}

## Implementation Target Summary
{bullet_list(plan.component_targets)}

## Actually Implemented Content
{bullet_list(implementation.created_files)}

## Mapping Between Paper Contents And Code Files
{bullet_list([f"{target} -> prototype_implementation.md / implementation_plan.md" for target in analysis.implementation_targets])}

## Used Skills
{bullet_list(tooling.default_skills)}

## Used Tools
{bullet_list(tooling.default_tools)}

## Evaluation Results
Validation status: {"PASS" if validation.passed else "FAIL"}

{bullet_list(review.behavioral_checks)}

## Differences From The Paper
{bullet_list(review.revision_items)}

## Items Not Implemented And Reasons
{bullet_list(plan.excluded_items)}

## Future Improvement Directions
{bullet_list(["Real LLM integration", "Full PDF parsing", "Paper-specific executable code generation", "Richer reviewer sub-agent with rubric scoring"])}

## Execution Method
`paper-agent run --paper examples/sample_paper.md --out runs/sample_run`

## Environment Setup Method
Install the package in editable mode with `python -m pip install -e .[dev]`, then run `pytest`.

## Configuration File Description
The MVP has no required runtime configuration file. Future versions should add a typed config for model providers, parser backends, and runner settings.
"""
        return write_text(output_dir / "final_report.md", content)
