"""Single orchestrator facade for the LangGraph paper-agent harness."""

from __future__ import annotations

from pathlib import Path

from paper_agent.code_implementation import CodeImplementer
from paper_agent.graph import PaperAgentGraph
from paper_agent.paper_analysis import PaperAnalyzer, PaperReader
from paper_agent.planning import ImplementationPlanner
from paper_agent.readme_writer import ReadmeWriter
from paper_agent.reporting import FinalReporter
from paper_agent.reviewer import ReviewerSubAgent
from paper_agent.schemas import RunArtifacts
from paper_agent.tool_registry import ToolRegistry
from paper_agent.validation import Validator


class Orchestrator:
    """Compatibility facade that runs the LangGraph workflow."""

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
        self.graph = PaperAgentGraph(
            reader=reader,
            analyzer=analyzer,
            planner=planner,
            tool_registry=tool_registry,
            implementer=implementer,
            validator=validator,
            reviewer=reviewer,
            reporter=reporter,
            readme_writer=readme_writer,
        )

    def run(self, paper_path: Path, output_dir: Path) -> RunArtifacts:
        return self.graph.run(paper_path, output_dir)