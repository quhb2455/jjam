"""Implementation planning stage."""

from __future__ import annotations

from pathlib import Path

from paper_agent.schemas import ImplementationPlan, PaperAnalysisResult
from paper_agent.utils import bullet_list, numbered_list, write_text


class ImplementationPlanner:
    def create_plan(self, analysis: PaperAnalysisResult) -> ImplementationPlan:
        return ImplementationPlan(
            objective=f"Implement an MVP harness for the paper target: {analysis.title}",
            component_targets=analysis.implementation_targets,
            module_structure=[
                "orchestrator: controls the end-to-end workflow",
                "paper_analysis: reads and extracts implementation-relevant paper facts",
                "planning: converts analysis into a build plan",
                "skill_registry/tool_registry: records reusable capabilities",
                "code_implementation: creates MVP implementation artifacts",
                "validation: performs smoke checks",
                "reviewer: reviewer sub-agent simulation",
                "reporting/readme_writer: final documentation",
            ],
            file_structure=[
                "src/paper_agent/*.py",
                ".agents/skills/*/SKILL.md",
                "docs/*.md",
                "examples/sample_paper.md",
                "runs/<run_id>/*.md",
                "tests/*.py",
            ],
            dependencies=["Python >=3.10", "pytest for development tests"],
            required_skills=[
                "paper-analysis",
                "implementation-planning",
                "code-implementation",
                "validation",
                "paper-code-review",
                "final-report-generation",
            ],
            required_tools=[
                "filesystem tool",
                "git tool when repository metadata is available",
                "python execution tool",
                "test runner tool",
                "package inspection tool",
                "paper parser tool",
                "report writer tool",
            ],
            implementation_order=[
                "Read paper input",
                "Analyze paper and write paper_summary.md plus implementation_spec.md",
                "Write implementation_plan.md",
                "Write tooling_plan.md",
                "Run implementation stage",
                "Validate outputs",
                "Run reviewer sub-agent simulation",
                "Write final report and generated README",
            ],
            test_plan=[
                "Unit test the orchestrator creates all required artifacts",
                "Unit test CLI argument path executes successfully",
                "Smoke test sample paper run",
            ],
            risks=[
                "MVP paper analysis is heuristic and cannot guarantee semantic completeness.",
                "PDF parsing is a placeholder integration point.",
                "Generated implementation work is represented as scaffolding, not arbitrary paper code synthesis.",
            ],
            excluded_items=analysis.excluded_scope,
        )

    def write_output(self, output_dir: Path, plan: ImplementationPlan) -> Path:
        content = f"""# Implementation Plan

## Implementation Objective
{plan.objective}

## Implementation Targets By Paper Component
{bullet_list(plan.component_targets)}

## Module Structure
{bullet_list(plan.module_structure)}

## File Structure
{bullet_list(plan.file_structure)}

## Required Dependencies
{bullet_list(plan.dependencies)}

## Required Skills
{bullet_list(plan.required_skills)}

## Required Tools
{bullet_list(plan.required_tools)}

## Implementation Order
{numbered_list(plan.implementation_order)}

## Test Plan
{bullet_list(plan.test_plan)}

## Expected Risks
{bullet_list(plan.risks)}

## Items Not Implemented And Reasons
{bullet_list(plan.excluded_items)}
"""
        return write_text(output_dir / "implementation_plan.md", content)
