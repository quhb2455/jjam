"""Command line interface for paper-agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from paper_agent.orchestrator import Orchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-agent",
        description="Run the paper implementation harness pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Analyze a paper and generate implementation artifacts.")
    run_parser.add_argument("--paper", required=True, type=Path, help="Path to a PDF, Markdown, or text paper.")
    run_parser.add_argument("--out", required=True, type=Path, help="Directory for generated run artifacts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        artifacts = Orchestrator().run(args.paper, args.out)
        print(f"paper-agent completed: {artifacts.output_dir}")
        for path in artifacts.files:
            print(f"- {path.name}")
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
