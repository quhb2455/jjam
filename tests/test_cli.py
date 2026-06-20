import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from paper_agent.cli import main


def assert_cli_run_generates_outputs(tmp_path: Path) -> None:
    paper = tmp_path / 'paper.md'
    paper.write_text('# CLI Paper\n\nMethod and evaluation details.', encoding='utf-8')
    out_dir = tmp_path / 'cli_run'

    exit_code = main(['run', '--paper', str(paper), '--out', str(out_dir)])

    assert exit_code == 0
    assert (out_dir / 'final_report.md').exists()
    assert (out_dir / 'README.generated.md').exists()


def test_cli_run_generates_outputs(tmp_path: Path) -> None:
    assert_cli_run_generates_outputs(tmp_path)


class CliTests(unittest.TestCase):
    def test_cli_run_generates_outputs(self) -> None:
        with TemporaryDirectory() as directory:
            assert_cli_run_generates_outputs(Path(directory))


if __name__ == '__main__':
    unittest.main()
