from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from pypdf import PdfWriter

from paper_harness.core import (
    HarnessError,
    check_assessment,
    discover_pdf,
    load_config,
    prepare,
    select_workspace,
    slugify_title,
)


REPOSITORY_ROOT = Path(__file__).parents[1]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def make_workspace(tmp_path: Path) -> Path:
    harness_root = tmp_path / "paper_impl_harness"
    harness_root.mkdir()
    (harness_root / "paper-harness.toml").write_text(
        """
[repository]
input_dir = "papers"
output_dir = "implementations"
[workspace]
state_dir = ".paper-harness"
docs_dir = "docs"
[validation]
command_timeout_seconds = 10
minimum_document_bytes = 20
""".strip(),
        encoding="utf-8",
    )
    shutil.copytree(REPOSITORY_ROOT / "harness", harness_root / "harness")
    (tmp_path / "papers").mkdir()
    (tmp_path / "implementations").mkdir()
    return tmp_path


def make_pdf(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_metadata({"/Title": "Test Paper", "/Author": "Researcher"})
    with path.open("wb") as handle:
        writer.write(handle)


def test_prepare_ignores_archive_and_does_not_overwrite_evidence(tmp_path: Path) -> None:
    root = make_workspace(tmp_path)
    make_pdf(root / "papers" / "paper.pdf")
    base_config = load_config(root)
    pdf = discover_pdf(base_config)
    workspace = select_workspace(base_config, pdf, "Test Paper", None)
    config = load_config(root, workspace=workspace)
    existing = workspace / "docs" / "paper_summary.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("keep my analysis", encoding="utf-8")

    manifest, created = prepare(config, pdf, "Test Paper")

    assert manifest["pdf"] == "paper.pdf"
    assert manifest["source_pdf"] == "papers/paper.pdf"
    assert manifest["title"] == "Test Paper"
    assert manifest["pages"] == 1
    assert manifest["empty_text_pages"] == [1]
    assert existing.read_text(encoding="utf-8") == "keep my analysis"
    assert (workspace / "paper.pdf").is_file()
    assert (workspace / ".paper-harness" / "paper.txt").is_file()
    assert workspace / ".paper-harness" / "feasibility.json" in created


def test_assessment_gate_accepts_evidence_backed_partial_decision(tmp_path: Path) -> None:
    root = make_workspace(tmp_path)
    workspace = root / "implementations" / "test-paper"
    config = load_config(root, workspace=workspace)
    config.state_dir.mkdir(parents=True)
    config.docs_dir.mkdir(parents=True)
    for name in ("paper_summary.md", "feasibility_report.md"):
        (config.docs_dir / name).write_text("# Complete\n\nEvidence-backed analysis.", encoding="utf-8")
    write_json(
        config.state_dir / "feasibility.json",
        {
            "paper": {
                "title": "Test Paper",
                "pdf": "paper.pdf",
                "sha256": "abc",
                "pages": 1,
            },
            "decision": "partial",
            "scores": {
                "method_specification": 2,
                "resource_feasibility": 1,
                "data_asset_access": 1,
                "evaluation_feasibility": 1,
                "dependency_feasibility": 2,
            },
            "binding_constraints": ["Full-scale compute is unavailable"],
            "missing_information": [],
            "assumptions": ["Use a reduced dataset"],
            "implementation_scope": {
                "included": ["Core algorithm"],
                "excluded": ["Full benchmark"],
            },
            "paper_evidence": [{"location": "Section 3, p. 4", "finding": "Defines the core update"}],
        },
    )
    write_json(config.state_dir / "paper-manifest.json", {"pdf": "paper.pdf", "sha256": "abc"})

    result = check_assessment(config)

    assert result.ok, result.errors


def test_assessment_gate_rejects_pending_template(tmp_path: Path) -> None:
    root = make_workspace(tmp_path)
    make_pdf(root / "papers" / "paper.pdf")
    base_config = load_config(root)
    pdf = discover_pdf(base_config)
    workspace = select_workspace(base_config, pdf, "Test Paper", None)
    config = load_config(root, workspace=workspace)
    prepare(config, pdf, "Test Paper")

    result = check_assessment(config)

    assert not result.ok
    assert any("decision" in error for error in result.errors)
    assert any("template placeholders" in error for error in result.errors)


def test_slugify_title_is_stable_and_unicode_safe() -> None:
    assert slugify_title("Self-Consistency Improves Chain of Thought!", "paper") == (
        "self-consistency-improves-chain-of-thought"
    )
    assert slugify_title("논문 구현 방법", "paper") == "논문-구현-방법"


def test_workspace_cannot_escape_or_replace_implementations_root(tmp_path: Path) -> None:
    root = make_workspace(tmp_path)
    config = load_config(root)
    pdf = root / "papers" / "paper.pdf"
    make_pdf(pdf)

    with pytest.raises(HarnessError):
        select_workspace(config, pdf, "Paper", "outside/paper")
    with pytest.raises(HarnessError):
        select_workspace(config, pdf, "Paper", "implementations")
