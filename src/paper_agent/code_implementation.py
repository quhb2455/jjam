"""MVP code implementation stage."""

from __future__ import annotations

from pathlib import Path

from paper_agent.schemas import ImplementationPlan, ImplementationResult, PaperAnalysisResult
from paper_agent.utils import bullet_list, write_text


class CodeImplementer:
    def implement(self, output_dir: Path, analysis: PaperAnalysisResult, plan: ImplementationPlan) -> ImplementationResult:
        prototype = f"""# Prototype Implementation Notes

## Paper Target
{analysis.title}

## Implemented MVP Behavior
{bullet_list(plan.component_targets)}

## Execution Boundary
This MVP records a deterministic implementation scaffold. Real paper-specific algorithms should be added under a generated project package after the reviewer confirms the target scope and the LLM or heuristic analysis has identified implementable details.
"""
        assumptions = [
            "The default analyzer uses deterministic local heuristics unless an LLM provider is explicitly configured.",
            "PDF input is parsed as extractable text with pypdf; scanned image-only PDFs require a future OCR tool.",
            "The reviewer sub-agent is represented by a deterministic module in this repository.",
            "Generated implementation output is documentation-first scaffolding unless the paper provides directly implementable pseudocode.",
        ]
        created = [
            write_text(output_dir / "prototype_implementation.md", prototype),
            write_text(output_dir / "assumptions.md", "# Assumptions\n\n" + bullet_list(assumptions)),
        ]
        return ImplementationResult(
            created_files=[path.name for path in created],
            assumptions=assumptions,
            notes=["Implementation stage completed with MVP scaffold outputs."],
        )
