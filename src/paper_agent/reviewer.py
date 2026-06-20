"""Reviewer sub-agent simulation."""

from __future__ import annotations

from pathlib import Path

from paper_agent.schemas import ImplementationPlan, ImplementationResult, PaperAnalysisResult, ReviewResult, ValidationResult
from paper_agent.utils import bullet_list, simple_table, write_text


class ReviewerSubAgent:
    """Deterministic reviewer that models the intended sub-agent contract."""

    def review(
        self,
        analysis: PaperAnalysisResult,
        plan: ImplementationPlan,
        implementation: ImplementationResult,
        validation: ValidationResult,
    ) -> ReviewResult:
        coverage = [f"Covered target: {target}" for target in plan.component_targets]
        fidelity = [
            "Pipeline flow follows the requested paper-to-code harness workflow.",
            "Paper-specific algorithms are not claimed as implemented unless present in generated notes.",
            "Equations and pseudocode are captured in implementation_spec.md but not automatically converted to executable code in the MVP.",
        ]
        behavioral = implementation.notes + [f"Validation status: {'PASS' if validation.passed else 'FAIL'}"]
        reproducibility = [
            "CLI command is documented.",
            "Generated README is produced in the run directory.",
            "Dependencies are declared in pyproject.toml.",
        ]
        revisions = [
            "Integrate a real PDF parser tool.",
            "Replace heuristic analyzer with an LLM-backed implementation target extractor.",
            "Add generated code workspaces for papers with explicit pseudocode.",
        ]
        if validation.failures:
            revisions.extend(validation.failures)
        return ReviewResult(coverage, fidelity, behavioral, reproducibility, revisions)

    def write_outputs(self, output_dir: Path, result: ReviewResult, analysis: PaperAnalysisResult) -> list[Path]:
        review_report = f"""# Review Report

## Paper Component Coverage
{bullet_list(result.coverage)}

## Algorithmic Fidelity
{bullet_list(result.fidelity)}

## Behavioral Check
{bullet_list(result.behavioral_checks)}

## Reproducibility
{bullet_list(result.reproducibility)}
"""
        matrix_rows = [
            [target, "Implemented as MVP scaffold", "Partial", "See prototype_implementation.md"]
            for target in analysis.implementation_targets
        ]
        matrix = f"""# Paper-Code Alignment Matrix

{simple_table(["Paper Component", "Code Artifact", "Status", "Notes"], matrix_rows)}
"""
        revision_plan = f"""# Revision Plan

## Proposed Revisions
{bullet_list(result.revision_items)}
"""
        return [
            write_text(output_dir / "review_report.md", review_report),
            write_text(output_dir / "paper_code_alignment_matrix.md", matrix),
            write_text(output_dir / "revision_plan.md", revision_plan),
        ]
