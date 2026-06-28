# Codex Paper Implementations

This repository uses Codex and a local, API-free harness to turn research-paper PDFs into isolated, traceable implementations. The harness supplies the workflow and evidence gates; each paper gets its own codebase under `implementations/`.

## Repository layout

```text
.
├── AGENTS.md                  # Codex routing and mandatory workflow
├── papers/                    # Input PDFs
├── paper_impl_harness/        # Reusable harness; never paper-specific output
│   ├── README.md
│   ├── CODEX_TASK.md
│   ├── harness/
│   ├── src/paper_harness/
│   └── tests/
└── implementations/          # One independent directory per paper
    └── <paper-title-slug>/
        ├── paper.pdf
        ├── README.md
        ├── src/
        ├── tests/
        ├── docs/
        └── .paper-harness/
```

## Use with Codex

1. Put one or more PDFs in `papers/`.
2. Start a new Codex session at the repository root.
3. Ask:

```text
papers/<file>.pdf를 구현해줘. AGENTS.md와 paper_impl_harness/CODEX_TASK.md를 따르고 최종 검증까지 완료해줘.
```

Codex determines the exact paper title, prepares `implementations/<paper-title-slug>/`, assesses feasibility, implements the supported scope, and runs the evidence gates.

No manual virtual-environment activation is needed. `uv run --project paper_impl_harness ...` manages the harness environment. A paper implementation may have its own environment inside its workspace if its dependencies require one.

See [paper_impl_harness/README.md](paper_impl_harness/README.md) for CLI and internal design details.

