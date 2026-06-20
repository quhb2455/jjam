"""Paper analysis stage."""

from __future__ import annotations

import re
from pathlib import Path

from paper_agent.schemas import PaperAnalysisResult, PaperInput
from paper_agent.utils import bullet_list, write_text


class PaperReader:
    """Reads supported paper files.

    PDF support is intentionally shallow in the MVP because external PDF
    parsers are a replaceable tool boundary.
    """

    def read(self, path: Path) -> PaperInput:
        if not path.exists():
            raise FileNotFoundError(f"Paper file does not exist: {path}")
        suffix = path.suffix.lower()
        if suffix in {".md", ".txt"}:
            text = path.read_text(encoding="utf-8")
        elif suffix == ".pdf":
            text = (
                f"# PDF input: {path.name}\n\n"
                "The MVP detected a PDF file. Full PDF parsing is a future tool integration; "
                "this run records the file as the paper source and uses placeholder analysis."
            )
        else:
            raise ValueError(f"Unsupported paper format: {suffix}")
        return PaperInput(path=path, text=text)


class PaperAnalyzer:
    def analyze(self, paper: PaperInput) -> PaperAnalysisResult:
        title = self._extract_title(paper)
        lines = [line.strip() for line in paper.text.splitlines() if line.strip()]
        summary = self._summarize(lines)
        contributions = self._find_section_items(paper.text, ["contribution", "key contribution"])
        targets = self._infer_targets(paper.text)
        evals = self._find_keywords(
            paper.text,
            ["accuracy", "benchmark", "ablation", "smoke", "evaluation", "metric", "fidelity"],
        )
        equations = [line for line in lines if any(token in line for token in ["=", "Algorithm", "Input:", "Output:"])]
        return PaperAnalysisResult(
            title=title,
            summary=summary,
            key_contributions=contributions or ["Extract paper claims and implementation targets from the input document."],
            implementation_targets=targets,
            required_input_data=self._infer_inputs(paper.text),
            required_output_format=["Markdown analysis reports", "Implementation plan", "Review and final report"],
            required_models_or_libraries=self._infer_libraries(paper.text),
            evaluation_methods=evals or ["Smoke tests", "Static paper-to-code review", "Coverage matrix"],
            equations_or_pseudocode=equations or ["No explicit equations or pseudocode detected by the MVP analyzer."],
            unspecified_parts=[
                "Exact LLM prompting strategy is not specified.",
                "Repository-specific implementation target language beyond Python is not specified.",
                "PDF parsing backend is not specified.",
            ],
            mvp_scope=[
                "Single orchestrator pipeline",
                "Structured markdown artifacts",
                "Mock code implementation stage",
                "Reviewer sub-agent design as a deterministic module",
            ],
            excluded_scope=[
                "Real LLM API calls",
                "Full PDF semantic extraction",
                "Automatic generation of arbitrary research code repositories",
            ],
        )

    def write_outputs(self, output_dir: Path, result: PaperAnalysisResult) -> list[Path]:
        summary = f"""# Paper Summary

## Title
{result.title}

## Overall Summary
{result.summary}

## Key Contributions
{bullet_list(result.key_contributions)}

## MVP Scope
{bullet_list(result.mvp_scope)}

## Excluded Scope
{bullet_list(result.excluded_scope)}
"""
        spec = f"""# Implementation Spec

## Algorithms Or Methodologies To Implement
{bullet_list(result.implementation_targets)}

## Required Input Data
{bullet_list(result.required_input_data)}

## Required Output Format
{bullet_list(result.required_output_format)}

## Required Models Or External Libraries
{bullet_list(result.required_models_or_libraries)}

## Required Evaluation Methods
{bullet_list(result.evaluation_methods)}

## Equations, Algorithms, And Pseudocode
{bullet_list(result.equations_or_pseudocode)}

## Implementation-Relevant Gaps
{bullet_list(result.unspecified_parts)}
"""
        return [
            write_text(output_dir / "paper_summary.md", summary),
            write_text(output_dir / "implementation_spec.md", spec),
        ]

    def _extract_title(self, paper: PaperInput) -> str:
        for line in paper.text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()
        return paper.path.stem.replace("_", " ").title()

    def _summarize(self, lines: list[str]) -> str:
        content = " ".join(line.lstrip("# ") for line in lines[:8])
        return content[:900] if content else "No paper text was available for analysis."

    def _find_section_items(self, text: str, names: list[str]) -> list[str]:
        items: list[str] = []
        for line in text.splitlines():
            normalized = line.lower()
            if any(name in normalized for name in names):
                cleaned = line.strip("#- * ")
                if cleaned:
                    items.append(cleaned)
        return items[:6]

    def _find_keywords(self, text: str, keywords: list[str]) -> list[str]:
        lowered = text.lower()
        return [f"Paper mentions {keyword}-based evaluation." for keyword in keywords if keyword in lowered]

    def _infer_targets(self, text: str) -> list[str]:
        lowered = text.lower()
        targets = []
        if "algorithm" in lowered or "method" in lowered:
            targets.append("Represent the paper method as explicit pipeline stages.")
        if "data" in lowered or "dataset" in lowered:
            targets.append("Model paper data assumptions and expected input artifacts.")
        if "evaluation" in lowered or "metric" in lowered:
            targets.append("Generate validation and review artifacts from implementation results.")
        targets.append("Produce a reproducible README and final report.")
        return targets

    def _infer_inputs(self, text: str) -> list[str]:
        matches = re.findall(r"(?:input|dataset|data)[: ]+([^.\n]+)", text, flags=re.IGNORECASE)
        return [match.strip() for match in matches[:5]] or ["Paper file in PDF, Markdown, or plain text format"]

    def _infer_libraries(self, text: str) -> list[str]:
        lowered = text.lower()
        libraries = ["Python standard library"]
        for name in ["numpy", "pandas", "torch", "transformers", "scikit-learn"]:
            if name in lowered:
                libraries.append(name)
        return libraries
