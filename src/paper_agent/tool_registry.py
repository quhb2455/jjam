"""Default tool registry for the harness."""

from __future__ import annotations

from pathlib import Path

from paper_agent.schemas import ToolingPlan
from paper_agent.utils import bullet_list, simple_table, write_text


DEFAULT_TOOLS = [
    "filesystem tool",
    "git tool",
    "python execution tool",
    "test runner tool",
    "package inspection tool",
    "paper parser tool",
    "report writer tool",
]


class ToolRegistry:
    def build_plan(self) -> ToolingPlan:
        return ToolingPlan(
            default_tools=DEFAULT_TOOLS,
            default_skills=[
                "paper-analysis",
                "implementation-planning",
                "code-implementation",
                "validation",
                "paper-code-review",
                "final-report-generation",
                "readme-generation",
            ],
            additional_tools=[],
        )

    def write_output(self, output_dir: Path, plan: ToolingPlan) -> Path:
        rows = [
            [
                "No additional tool",
                "MVP can run with default tools and mock interfaces",
                "N/A",
                "N/A",
                "N/A",
                "Low",
            ]
        ]
        content = f"""# Tooling Plan

## Default Tools
{bullet_list(plan.default_tools)}

## Default Skills
{bullet_list(plan.default_skills)}

## Additional Tool Review
The MVP must not create a new tool for every paper. Additional tools require documented need before implementation.

{simple_table(["Tool Name", "Reason", "Input", "Output", "Failure Conditions", "Priority"], rows)}
"""
        return write_text(output_dir / "tooling_plan.md", content)
