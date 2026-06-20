"""LangGraph workflow for the paper-agent harness."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, StateGraph

from paper_agent.code_implementation import CodeImplementer
from paper_agent.paper_analysis import PaperAnalyzer, PaperReader
from paper_agent.planning import ImplementationPlanner
from paper_agent.readme_writer import ReadmeWriter
from paper_agent.reporting import FinalReporter
from paper_agent.reviewer import ReviewerSubAgent
from paper_agent.schemas import (
    ImplementationPlan,
    ImplementationResult,
    PaperAnalysisResult,
    PaperInput,
    ReviewResult,
    RunArtifacts,
    ToolingPlan,
    ValidationResult,
)
from paper_agent.tool_registry import ToolRegistry
from paper_agent.utils import ensure_dir
from paper_agent.validation import Validator


class PaperAgentState(TypedDict, total=False):
    """State passed through the LangGraph pipeline."""

    paper_path: Path
    output_dir: Path
    files: list[Path]
    paper: PaperInput
    analysis: PaperAnalysisResult
    plan: ImplementationPlan
    tooling: ToolingPlan
    implementation: ImplementationResult
    validation: ValidationResult
    review: ReviewResult
    revision_required: bool


class PaperAgentGraph:
    """Builds and executes the LangGraph version of the paper-agent workflow."""

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
        self.app = self._compile()

    def run(self, paper_path: Path, output_dir: Path) -> RunArtifacts:
        output_dir = ensure_dir(output_dir)
        final_state = self.app.invoke(
            {
                "paper_path": paper_path,
                "output_dir": output_dir,
                "files": [],
                "revision_required": False,
            }
        )
        return RunArtifacts(output_dir=output_dir, files=final_state["files"])

    def _compile(self):
        graph = StateGraph(PaperAgentState)
        graph.add_node("read_paper", self._read_paper)
        graph.add_node("analyze_paper", self._analyze_paper)
        graph.add_node("plan_implementation", self._plan_implementation)
        graph.add_node("plan_tooling", self._plan_tooling)
        graph.add_node("implement_code", self._implement_code)
        graph.add_node("validate_outputs", self._validate_outputs)
        graph.add_node("review_alignment", self._review_alignment)
        graph.add_node("decide_revision", self._decide_revision)
        graph.add_node("write_final_report", self._write_final_report)
        graph.add_node("write_run_readme", self._write_run_readme)

        graph.set_entry_point("read_paper")
        graph.add_edge("read_paper", "analyze_paper")
        graph.add_edge("analyze_paper", "plan_implementation")
        graph.add_edge("plan_implementation", "plan_tooling")
        graph.add_edge("plan_tooling", "implement_code")
        graph.add_edge("implement_code", "validate_outputs")
        graph.add_edge("validate_outputs", "review_alignment")
        graph.add_edge("review_alignment", "decide_revision")
        graph.add_edge("decide_revision", "write_final_report")
        graph.add_edge("write_final_report", "write_run_readme")
        graph.add_edge("write_run_readme", END)
        return graph.compile()

    def _read_paper(self, state: PaperAgentState) -> PaperAgentState:
        return {"paper": self.reader.read(state["paper_path"])}

    def _analyze_paper(self, state: PaperAgentState) -> PaperAgentState:
        analysis = self.analyzer.analyze(state["paper"])
        files = [*state["files"], *self.analyzer.write_outputs(state["output_dir"], analysis)]
        return {"analysis": analysis, "files": files}

    def _plan_implementation(self, state: PaperAgentState) -> PaperAgentState:
        plan = self.planner.create_plan(state["analysis"])
        files = [*state["files"], self.planner.write_output(state["output_dir"], plan)]
        return {"plan": plan, "files": files}

    def _plan_tooling(self, state: PaperAgentState) -> PaperAgentState:
        tooling = self.tool_registry.build_plan()
        files = [*state["files"], self.tool_registry.write_output(state["output_dir"], tooling)]
        return {"tooling": tooling, "files": files}

    def _implement_code(self, state: PaperAgentState) -> PaperAgentState:
        implementation = self.implementer.implement(state["output_dir"], state["analysis"], state["plan"])
        files = [*state["files"], *(state["output_dir"] / name for name in implementation.created_files)]
        return {"implementation": implementation, "files": files}

    def _validate_outputs(self, state: PaperAgentState) -> PaperAgentState:
        validation = self.validator.validate(state["output_dir"])
        files = [*state["files"], self.validator.write_output(state["output_dir"], validation)]
        return {"validation": validation, "files": files}

    def _review_alignment(self, state: PaperAgentState) -> PaperAgentState:
        review = self.reviewer.review(state["analysis"], state["plan"], state["implementation"], state["validation"])
        files = [*state["files"], *self.reviewer.write_outputs(state["output_dir"], review, state["analysis"])]
        return {"review": review, "files": files}

    def _decide_revision(self, state: PaperAgentState) -> PaperAgentState:
        validation_failed = not state["validation"].passed
        revision_required = validation_failed or bool(state["review"].revision_items)
        return {"revision_required": revision_required}

    def _write_final_report(self, state: PaperAgentState) -> PaperAgentState:
        path = self.reporter.write_output(
            state["output_dir"],
            state["analysis"],
            state["plan"],
            state["tooling"],
            state["implementation"],
            state["validation"],
            state["review"],
        )
        return {"files": [*state["files"], path]}

    def _write_run_readme(self, state: PaperAgentState) -> PaperAgentState:
        path = self.readme_writer.write_output(state["output_dir"], state["analysis"], state["validation"])
        return {"files": [*state["files"], path]}