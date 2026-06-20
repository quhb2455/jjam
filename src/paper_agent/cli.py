"""Command line interface for paper-agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from paper_agent.orchestrator import Orchestrator
from paper_agent.paper_analysis import OpenAICompatibleAnalysisClient, PaperAnalyzer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-agent",
        description="Run the paper implementation harness pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Analyze a paper and generate implementation artifacts.")
    run_parser.add_argument("--paper", required=True, type=Path, help="Path to a PDF, Markdown, or text paper.")
    run_parser.add_argument("--out", required=True, type=Path, help="Directory for generated run artifacts.")
    run_parser.add_argument(
        "--llm-provider",
        choices=["heuristic", "openai-compatible"],
        default="heuristic",
        help="Paper analysis backend. Use openai-compatible to call a chat completions API.",
    )
    run_parser.add_argument("--llm-model", help="Model name for --llm-provider openai-compatible.")
    run_parser.add_argument(
        "--llm-base-url",
        default="https://api.openai.com/v1",
        help="Base URL for an OpenAI-compatible API.",
    )
    run_parser.add_argument(
        "--llm-api-key-env",
        default="PAPER_AGENT_LLM_API_KEY",
        help="Environment variable containing the LLM API key. Falls back to OPENAI_API_KEY.",
    )
    run_parser.add_argument(
        "--llm-timeout-seconds",
        type=float,
        default=60.0,
        help="Timeout for the LLM analysis request.",
    )
    return parser


def build_analyzer(args: argparse.Namespace) -> PaperAnalyzer:
    if args.llm_provider == "heuristic":
        return PaperAnalyzer()

    import os

    api_key = os.getenv(args.llm_api_key_env) or os.getenv("OPENAI_API_KEY", "")
    model = args.llm_model or os.getenv("PAPER_AGENT_LLM_MODEL", "")
    client = OpenAICompatibleAnalysisClient(
        api_key=api_key,
        model=model,
        base_url=args.llm_base_url,
        timeout_seconds=args.llm_timeout_seconds,
    )
    return PaperAnalyzer(llm_client=client)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        analyzer = build_analyzer(args)
        artifacts = Orchestrator(analyzer=analyzer).run(args.paper, args.out)
        print(f"paper-agent completed: {artifacts.output_dir}")
        for path in artifacts.files:
            print(f"- {path.name}")
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
