import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from paper_agent.orchestrator import Orchestrator


def assert_orchestrator_generates_required_artifacts(tmp_path: Path) -> None:
    paper = tmp_path / 'paper.md'
    paper.write_text(
        '''# Example Method

## Key Contributions
- A deterministic method.

Algorithm:
1. Compute score = a + b.

## Evaluation
Accuracy and ablation are reported.
''',
        encoding='utf-8',
    )
    out_dir = tmp_path / 'run'

    artifacts = Orchestrator().run(paper, out_dir)

    expected = {
        'paper_summary.md',
        'implementation_spec.md',
        'implementation_plan.md',
        'tooling_plan.md',
        'validation_result.md',
        'review_report.md',
        'paper_code_alignment_matrix.md',
        'revision_plan.md',
        'final_report.md',
        'README.generated.md',
        'assumptions.md',
        'prototype_implementation.md',
    }
    assert expected.issubset({path.name for path in artifacts.files})
    for name in expected:
        assert (out_dir / name).read_text(encoding='utf-8').strip()


def assert_orchestrator_rejects_missing_paper(tmp_path: Path) -> None:
    missing = tmp_path / 'missing.md'
    out_dir = tmp_path / 'run'

    try:
        Orchestrator().run(missing, out_dir)
    except FileNotFoundError as exc:
        assert 'Paper file does not exist' in str(exc)
    else:
        raise AssertionError('Expected missing paper to raise FileNotFoundError')


def test_orchestrator_generates_required_artifacts(tmp_path: Path) -> None:
    assert_orchestrator_generates_required_artifacts(tmp_path)


def test_orchestrator_rejects_missing_paper(tmp_path: Path) -> None:
    assert_orchestrator_rejects_missing_paper(tmp_path)


class OrchestratorTests(unittest.TestCase):
    def test_generates_required_artifacts(self) -> None:
        with TemporaryDirectory() as directory:
            assert_orchestrator_generates_required_artifacts(Path(directory))

    def test_rejects_missing_paper(self) -> None:
        with TemporaryDirectory() as directory:
            assert_orchestrator_rejects_missing_paper(Path(directory))


if __name__ == '__main__':
    unittest.main()
