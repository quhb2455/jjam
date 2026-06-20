"""Shared schemas for the paper-agent pipeline.

The MVP keeps schemas as dataclasses so the pipeline has clear contracts
without adding a validation framework too early.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PaperInput:
    path: Path
    text: str


@dataclass(frozen=True)
class PaperAnalysisResult:
    title: str
    summary: str
    key_contributions: list[str]
    implementation_targets: list[str]
    required_input_data: list[str]
    required_output_format: list[str]
    required_models_or_libraries: list[str]
    evaluation_methods: list[str]
    equations_or_pseudocode: list[str]
    unspecified_parts: list[str]
    mvp_scope: list[str]
    excluded_scope: list[str]


@dataclass(frozen=True)
class ImplementationPlan:
    objective: str
    component_targets: list[str]
    module_structure: list[str]
    file_structure: list[str]
    dependencies: list[str]
    required_skills: list[str]
    required_tools: list[str]
    implementation_order: list[str]
    test_plan: list[str]
    risks: list[str]
    excluded_items: list[str]


@dataclass(frozen=True)
class ToolingPlan:
    default_tools: list[str]
    default_skills: list[str]
    additional_tools: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class ImplementationResult:
    created_files: list[str]
    assumptions: list[str]
    notes: list[str]


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    checks: list[str]
    failures: list[str]


@dataclass(frozen=True)
class ReviewResult:
    coverage: list[str]
    fidelity: list[str]
    behavioral_checks: list[str]
    reproducibility: list[str]
    revision_items: list[str]


@dataclass(frozen=True)
class RunArtifacts:
    output_dir: Path
    files: list[Path]
