# Paper Implementation Harness

This directory contains the reusable, API-free engine used by Codex to prepare and validate isolated paper implementations. It must not contain paper-specific code or reports.

## Commands

Run commands from the repository root.

Prepare a workspace using the exact paper title:

```bash
uv run --project paper_impl_harness paper-harness prepare papers/paper.pdf --title "Exact Paper Title"
```

The command copies the source PDF and creates templates under `implementations/<exact-paper-title-slug>/`. Use `--output implementations/custom-slug` only when a deliberate override is needed.

Check progress and gates:

```bash
uv run --project paper_impl_harness paper-harness status implementations/<paper-title-slug>
uv run --project paper_impl_harness paper-harness check implementations/<paper-title-slug> --phase assessment
uv run --project paper_impl_harness paper-harness check implementations/<paper-title-slug> --phase final --run-commands
```

## Responsibilities

- PDF discovery, copying, hashing, and page-separated text extraction
- evidence and documentation scaffolding
- implementability assessment gate
- paper-claim-to-code-to-test traceability checks
- isolated execution of declared validation commands

Semantic judgment remains Codex's responsibility. Static checks cannot prove scientific equivalence, so the workflow requires a separate paper-to-code review and labels evidence as structural, numerical, or empirical.

Configuration lives in `paper-harness.toml`. Tests for the harness are run with:

```bash
uv run --project paper_impl_harness pytest -q paper_impl_harness/tests
```

