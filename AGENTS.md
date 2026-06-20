# AGENTS.md

## Project Purpose
This repository implements a Codex-based Agent Harness that takes AI papers with relatively few external constraints and turns them into structured implementation artifacts, review outputs, and reproducible reports.

## Architecture
The project uses a single Orchestrator-first architecture. `paper_agent.orchestrator.Orchestrator` owns the end-to-end workflow and invokes deterministic stages for paper analysis, implementation planning, tooling planning, implementation scaffolding, validation, reviewer evaluation, and reporting.

The initial MVP must not grow into a complex multi-agent system. The only sub-agent concept is the Reviewer Sub-agent, represented by a deterministic reviewer module with a clear input/output contract.

## Skill Usage Rules
- Use existing default Skills before proposing new Skills.
- Keep Skills focused on repeatable workflow stages.
- Skill outputs must be written as explicit artifacts.
- Do not hide assumptions inside Skill behavior; write them to `assumptions.md`.

Default Skills:
- `paper-analysis`
- `implementation-planning`
- `code-implementation`
- `validation`
- `paper-code-review`
- `final-report-generation`
- `readme-generation`

## Tool Usage Rules
- Use the default Tool Registry first.
- Do not create a new Tool for every paper.
- Any additional Tool must document its name, reason, input format, output format, failure conditions, and implementation priority before implementation.
- Tool failures must be surfaced in validation or review artifacts.

Default Tool candidates:
- filesystem tool
- git tool
- python execution tool
- test runner tool
- package inspection tool
- paper parser tool
- report writer tool

## Reviewer Sub-agent Usage Rules
- The Reviewer Sub-agent compares paper content against generated implementation artifacts.
- It must evaluate coverage, algorithmic fidelity, behavioral checks, and reproducibility.
- It must produce `review_report.md`, `paper_code_alignment_matrix.md`, and `revision_plan.md`.
- It must not claim equivalence when only an MVP scaffold exists.

## Assumption Recording Rules
- If implementation details are decided without explicit support from the paper, record them in `assumptions.md`.
- Assumptions must be specific enough to review later.
- Assumptions should distinguish MVP decisions from paper claims.

## Test Execution Rules
- Run unit tests or smoke checks before claiming completion.
- Report failed tests honestly.
- Do not delete or ignore failing outputs to make the run look successful.

## Final Report Rules
- The final report must include paper summary, implementation target summary, implemented content, paper-to-code mapping, used Skills, used Tools, evaluation results, differences from the paper, excluded items, future work, execution method, environment setup, and configuration notes.

## Prohibited Actions
- Do not claim that something not described in the paper has been implemented.
- Do not claim completion without testing.
- Do not hide failed tests.
- Do not create an unnecessary multi-agent structure.
- Do not create new Tools carelessly for every paper.
- Do not implement functionality without a README.
