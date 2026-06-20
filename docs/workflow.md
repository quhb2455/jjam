# Workflow

This document is the short reference workflow for the Paper Agent Harness. The more detailed working notes live in the repository-root `workflow.md`.

1. User provides a paper in PDF, Markdown, or text form.
2. The CLI loads optional LLM configuration from `.env` or `--env-file`.
3. The Orchestrator delegates execution to `PaperAgentGraph`.
4. `PaperReader` reads Markdown/text directly or extracts PDF text with `pypdf`.
5. `PaperAnalyzer` generates structured analysis with deterministic heuristics by default, or with an OpenAI-compatible LLM when `--llm-provider openai-compatible` is set.
6. Paper analysis writes `paper_summary.md` and `implementation_spec.md`.
7. Planning writes `implementation_plan.md`.
8. Tooling planning writes `tooling_plan.md`.
9. Implementation creates MVP scaffold artifacts and records assumptions.
10. Validation checks required outputs.
11. The deterministic Reviewer Sub-agent module generates review artifacts.
12. Final reporting writes `final_report.md`.
13. README generation writes `README.generated.md`.

Default heuristic run:

```bash
uv run paper-agent run --paper examples/sample_paper.md --out runs/sample_run
```

PDF run:

```bash
uv run paper-agent run --paper test_paper.pdf --out runs/pdf_run
```

LLM-backed PDF run:

```bash
uv run paper-agent run \
  --paper test_paper.pdf \
  --out runs/pdf_llm_run \
  --llm-provider openai-compatible
```

Required `.env` keys for LLM-backed analysis:

```bash
PAPER_AGENT_LLM_API_KEY=...
PAPER_AGENT_LLM_MODEL=YOUR_MODEL
PAPER_AGENT_LLM_BASE_URL=https://api.openai.com/v1
PAPER_AGENT_LLM_TIMEOUT_SECONDS=60
```
