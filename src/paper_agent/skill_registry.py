"""Skill registry used by the orchestrator."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillDefinition:
    name: str
    purpose: str
    inputs: list[str]
    outputs: list[str]


class SkillRegistry:
    def list_skills(self) -> list[SkillDefinition]:
        return [
            SkillDefinition("paper-analysis", "Extract paper summary and implementation targets.", ["paper"], ["paper_summary.md", "implementation_spec.md"]),
            SkillDefinition("implementation-planning", "Convert paper analysis into a concrete implementation plan.", ["implementation_spec.md"], ["implementation_plan.md"]),
            SkillDefinition("code-implementation", "Implement or scaffold code according to the plan.", ["implementation_plan.md"], ["code files", "assumptions.md"]),
            SkillDefinition("validation", "Run smoke checks and report failures honestly.", ["code files"], ["validation_result.md"]),
            SkillDefinition("paper-code-review", "Compare paper components with implementation outputs.", ["paper", "code files"], ["review_report.md", "paper_code_alignment_matrix.md", "revision_plan.md"]),
            SkillDefinition("final-report-generation", "Write final implementation and evaluation report.", ["all artifacts"], ["final_report.md"]),
            SkillDefinition("readme-generation", "Write user-facing setup and execution instructions.", ["all artifacts"], ["README.generated.md"]),
        ]
