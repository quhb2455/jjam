from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import (
    HarnessError,
    check_assessment,
    check_final,
    discover_pdf,
    load_config,
    prepare,
    run_validation_commands,
    select_workspace,
    status,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-harness",
        description="Prepare and validate a Codex-driven paper implementation workspace.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--harness-root",
        type=Path,
        help="harness directory (default: <repo-root>/paper_impl_harness)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="discover and extract the paper, then create templates")
    prepare_parser.add_argument("pdf", nargs="?", help="PDF under the configured papers directory")
    prepare_parser.add_argument("--title", required=True, help="exact paper title, used to create the output slug")
    prepare_parser.add_argument("--output", help="optional output path under implementations/")

    check_parser = subparsers.add_parser("check", help="run an assessment or final evidence gate")
    check_parser.add_argument("workspace", help="paper workspace under implementations/")
    check_parser.add_argument("--phase", choices=("assessment", "final"), required=True)
    check_parser.add_argument("--run-commands", action="store_true", help="run final manifest commands after static checks")

    status_parser = subparsers.add_parser("status", help="show concise artifact progress")
    status_parser.add_argument("workspace", help="paper workspace under implementations/")
    return parser


def _print_check(errors: list[str], warnings: list[str]) -> None:
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo_root = args.repo_root.resolve()
        harness_root = args.harness_root.resolve() if args.harness_root else None
        if args.command == "prepare":
            base_config = load_config(repo_root, harness_root=harness_root)
            pdf = discover_pdf(base_config, args.pdf)
            workspace = select_workspace(base_config, pdf, args.title, args.output)
            config = load_config(repo_root, workspace=workspace, harness_root=harness_root)
            manifest, created = prepare(config, pdf, args.title)
            relative_workspace = config.workspace_root.relative_to(config.repo_root)
            print(f"Prepared {manifest['source_pdf']} ({manifest['pages']} pages, sha256 {manifest['sha256'][:12]}...).")
            print(f"Workspace: {relative_workspace}")
            print(f"Extracted text to {relative_workspace / '.paper-harness' / 'paper.txt'}.")
            if created:
                print(f"Created {len(created)} evidence template(s).")
            else:
                print("Evidence files already exist; none were overwritten.")
            print(f"NOTE: {manifest['extraction_warning']}")
            return 0
        config = load_config(repo_root, workspace=args.workspace, harness_root=harness_root)
        if args.command == "status":
            for label, state in status(config):
                print(f"{label:20} {state}")
            return 0
        result = check_assessment(config) if args.phase == "assessment" else check_final(config)
        _print_check(result.errors, result.warnings)
        if not result.ok:
            print(f"{args.phase} gate failed with {len(result.errors)} error(s).", file=sys.stderr)
            return 1
        if args.run_commands:
            if args.phase != "final":
                print("ERROR: --run-commands is only valid for the final phase.", file=sys.stderr)
                return 2
            command_results = run_validation_commands(config)
            failed = [item for item in command_results if item.get("returncode") != 0]
            for item in command_results:
                outcome = "passed" if item.get("returncode") == 0 else "failed"
                print(f"validation command {item['name']}: {outcome}")
            if failed:
                print(f"Validation commands failed; inspect {config.state_dir / 'check-results.json'}.", file=sys.stderr)
                return 1
        print(f"{args.phase} gate passed.")
        return 0
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
