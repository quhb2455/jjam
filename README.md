# Paper Agent Harness

Paper Agent Harness is a Codex-oriented MVP for turning AI papers into structured implementation artifacts. It uses one Orchestrator, reusable Skills, a default Tool Registry, and a Reviewer Sub-agent design to analyze a paper, plan an implementation, scaffold MVP outputs, validate them, and write final reports.

## Setup

```bash
python -m pip install -e .[dev]
```

## Run The Sample

```bash
paper-agent run --paper examples/sample_paper.md --out runs/sample_run
```

The run writes:

- `paper_summary.md`
- `implementation_spec.md`
- `implementation_plan.md`
- `tooling_plan.md`
- `validation_result.md`
- `review_report.md`
- `paper_code_alignment_matrix.md`
- `revision_plan.md`
- `final_report.md`
- `README.generated.md`

The implementation stage also writes `prototype_implementation.md` and `assumptions.md`.

## Test

```bash
pytest
```

## Configuration

The MVP has no required runtime configuration file. Future versions should add typed configuration for model providers, MCP tools, PDF parsers, and test runners.

## Current Limitations

- Markdown and plain text inputs are read directly.
- PDF inputs are accepted as a placeholder boundary, but full PDF parsing is deferred.
- Paper analysis is heuristic and deterministic.
- The Reviewer Sub-agent is implemented as a deterministic module rather than a separate live agent process.
