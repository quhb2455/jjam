"""Single orchestrator for the paper-agent harness."""

from __future__ import annotations

from pathlib import Path

from paper_agent.code_implementation import CodeImplementer
from paper_agent.paper_analysis import PaperAnalyzer, PaperReader
from paper_agent.planning import ImplementationPlanner
from paper_agent.readme_writer import ReadmeWriter
from paper_agent.reporting import FinalReporter
from paper_agent.reviewer import ReviewerSubAgent
from paper_agent.schemas import RunArtifacts
from paper_agent.tool_registry import ToolRegistry
from paper_agent.utils import ensure_dir
from paper_agent.validation import Validator


class Orchestrator:
    """Controls the complete MVP pipeline."""

    def __init__(
        self,
        reader: PaperReader | None = None,
        analyzer: PaperAnalyzer | None = None,
        planner: ImplementationPlanner | None = None,
        tool_registry: ToolRegistry | None = None,
        implementer: CodeImplementer | None = None,
        validator: Validator | None = None,
        reviewer: ReviewerSubAgent | None = None,
        reporter: FinalReporter | None = None,
        readme_writer: ReadmeWriter | None = None,
    ) -> None:
        self.reader = reader or PaperReader()
        self.analyzer = analyzer or PaperAnalyzer()
        self.planner = planner or ImplementationPlanner()
        self.tool_registry = tool_registry or ToolRegistry()
        self.implementer = implementer or CodeImplementer()
        self.validator = validator or Validator()
        self.reviewer = reviewer or ReviewerSubAgent()
        self.reporter = reporter or FinalReporter()
        self.readme_writer = readme_writer or ReadmeWriter()

    def run(self, paper_path: Path, output_dir: Path) -> RunArtifacts:
        output_dir = ensure_dir(output_dir)
        files: list[Path] = []

        paper = self.reader.read(paper_path)
        analysis = self.analyzer.analyze(paper)
        files.extend(self.analyzer.write_outputs(output_dir, analysis))

        plan = self.planner.create_plan(analysis)
        files.append(self.planner.write_output(output_dir, plan))

        tooling = self.tool_registry.build_plan()
        files.append(self.tool_registry.write_output(output_dir, tooling))

        implementation = self.implementer.implement(output_dir, analysis, plan)
        files.extend(output_dir / name for name in implementation.created_files)

        validation = self.validator.validate(output_dir)
        files.append(self.validator.write_output(output_dir, validation))

        review = self.reviewer.review(analysis, plan, implementation, validation)
        files.extend(self.reviewer.write_outputs(output_dir, review, analysis))

        files.append(self.reporter.write_output(output_dir, analysis, plan, tooling, implementation, validation, review))
        files.append(self.readme_writer.write_output(output_dir, analysis, validation))

        return RunArtifacts(output_dir=output_dir, files=files)
