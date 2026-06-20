import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from paper_agent.cli import build_analyzer, build_parser, main


def assert_cli_run_generates_outputs(tmp_path: Path) -> None:
    paper = tmp_path / 'paper.md'
    paper.write_text('# CLI Paper\n\nMethod and evaluation details.', encoding='utf-8')
    out_dir = tmp_path / 'cli_run'

    exit_code = main(['run', '--paper', str(paper), '--out', str(out_dir)])

    assert exit_code == 0
    assert (out_dir / 'final_report.md').exists()
    assert (out_dir / 'README.generated.md').exists()


def test_build_analyzer_reads_llm_settings_from_env_file(tmp_path: Path, monkeypatch) -> None:
    for key in [
        'PAPER_AGENT_LLM_API_KEY',
        'OPENAI_API_KEY',
        'PAPER_AGENT_LLM_MODEL',
        'PAPER_AGENT_LLM_BASE_URL',
        'PAPER_AGENT_LLM_TIMEOUT_SECONDS',
    ]:
        monkeypatch.delenv(key, raising=False)

    env_file = tmp_path / '.env'
    env_file.write_text(
        'PAPER_AGENT_LLM_API_KEY=test-key\n'
        'PAPER_AGENT_LLM_MODEL=test-model\n'
        'PAPER_AGENT_LLM_BASE_URL=https://llm.example/v1\n'
        'PAPER_AGENT_LLM_TIMEOUT_SECONDS=12\n',
        encoding='utf-8',
    )
    args = build_parser().parse_args([
        'run',
        '--paper', str(tmp_path / 'paper.md'),
        '--out', str(tmp_path / 'out'),
        '--env-file', str(env_file),
        '--llm-provider', 'openai-compatible',
    ])

    analyzer = build_analyzer(args)

    assert analyzer.llm_client is not None
    assert analyzer.llm_client.api_key == 'test-key'
    assert analyzer.llm_client.model == 'test-model'
    assert analyzer.llm_client.base_url == 'https://llm.example/v1'
    assert analyzer.llm_client.timeout_seconds == 12.0

def test_cli_run_generates_outputs(tmp_path: Path) -> None:
    assert_cli_run_generates_outputs(tmp_path)


class CliTests(unittest.TestCase):
    def test_cli_run_generates_outputs(self) -> None:
        with TemporaryDirectory() as directory:
            assert_cli_run_generates_outputs(Path(directory))


if __name__ == '__main__':
    unittest.main()
