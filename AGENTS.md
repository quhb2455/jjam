# Codex Paper Implementation Repository

This repository contains a reusable paper-implementation harness and isolated paper workspaces. When asked to implement a paper, you are the reasoning engine: do not build an orchestrator that calls an external LLM API.

## Repository boundaries

- `paper_impl_harness/` is harness infrastructure. Read it, but do not modify it during a paper implementation.
- `papers/` contains input PDFs.
- `implementations/<paper-title-slug>/` is the only place where paper-specific code, environments, tests, reports, and generated evidence may be written.
- `_useless/` is archived history. Never use it as implementation input.
- The root `README.md` describes this repository and must not be replaced with a paper README.

## Start a paper implementation

1. Read `paper_impl_harness/CODEX_TASK.md` and all policy files in `paper_impl_harness/harness/`.
2. Inspect the paper PDF sufficiently to determine its exact title.
3. Prepare an isolated workspace. Pass the title explicitly so its stable slug becomes the directory name:

```bash
uv run --project paper_impl_harness paper-harness prepare papers/<paper.pdf> --title "<Exact Paper Title>"
```

4. Continue all work inside the workspace path printed by the command.
5. Never write paper code, paper documentation, or paper dependency files at the repository root or inside `paper_impl_harness/`.

## Mandatory workflow inside the workspace

### 1. Understand the paper

Read `.paper-harness/paper-manifest.json`, `.paper-harness/paper.txt`, and the copied `paper.pdf`. Visually inspect figures, equations, tables, and appendices; extracted text is only an index.

Complete `docs/paper_summary.md`. Cite pages, sections, equations, figures, tables, or appendices. Separate paper facts from assumptions and implementation choices.

### 2. Decide implementability

Use `paper_impl_harness/harness/ASSESSMENT_RUBRIC.md`. Complete `docs/feasibility_report.md` and `.paper-harness/feasibility.json`, then run from the repository root:

```bash
uv run --project paper_impl_harness paper-harness check implementations/<paper-title-slug> --phase assessment
```

- `feasible`: the central method and meaningful tests can be implemented locally.
- `partial`: a faithful core is possible, but named components or the full experiment are not.
- `not_feasible`: the central method cannot be responsibly reconstructed with available information/resources.

For `partial`, state exact boundaries and deviations. For `not_feasible`, stop after the summary, feasibility report, and unblock plan; do not create a misleading mock implementation.

### 3. Specify and implement

Complete `docs/implementation_plan.md` before coding. Map paper concepts to modules, interfaces, shapes, equations, configuration, tests, and acceptance criteria.

Follow `paper_impl_harness/harness/CONVENTIONS.md`. Keep the mathematical core small, deterministic where practical, configurable, import-safe, and independently testable. Do not claim unavailable datasets, weights, services, compute scales, or experiments were reproduced.

### 4. Verify fidelity

Follow `paper_impl_harness/harness/VERIFICATION_PROTOCOL.md`. Complete:

- `.paper-harness/implementation-manifest.json`
- `.paper-harness/alignment.json`
- `.paper-harness/validation.json`
- `docs/paper_code_alignment.md`
- `docs/validation_report.md`

Every central claim must link a paper location, code path/symbol, and test or experiment. Distinguish structural, numerical, and empirical evidence. Perform a separate paper-to-code review pass after coding.

### 5. Deliver and validate

The workspace must contain its own `README.md`, source code, tests/small experiments, required reports, and evidence JSON. Run:

```bash
uv run --project paper_impl_harness paper-harness check implementations/<paper-title-slug> --phase final --run-commands
```

Do not declare completion while the final gate fails. Report implemented, verified, deviating, and unverified scope honestly.

