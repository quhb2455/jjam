"""Generated README writer for each run."""

from __future__ import annotations

from pathlib import Path

from paper_agent.schemas import PaperAnalysisResult, ValidationResult
from paper_agent.utils import bullet_list, write_text


class ReadmeWriter:
    def write_output(self, output_dir: Path, analysis: PaperAnalysisResult, validation: ValidationResult) -> Path:
        content = f"""# Generated Paper-Agent Run README

## Paper
{analysis.title}

## What This Run Produced
{bullet_list(["paper_summary.md", "implementation_spec.md", "implementation_plan.md", "tooling_plan.md", "validation_result.md", "review_report.md", "paper_code_alignment_matrix.md", "final_report.md"])}

## How To Reproduce
Run:

```bash
paper-agent run --paper examples/sample_paper.md --out runs/sample_run
```

## Validation Status
{"PASS" if validation.passed else "FAIL"}

## Configuration
No external configuration is required for the MVP. LLM, MCP, parser, and test runner integrations are intentionally isolated for later replacement.
"""
        return write_text(output_dir / "README.generated.md", content)
