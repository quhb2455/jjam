# Workflow

1. User provides a paper in PDF, Markdown, or text form.
2. The Orchestrator reads the input.
3. Paper analysis generates `paper_summary.md` and `implementation_spec.md`.
4. Planning generates `implementation_plan.md`.
5. Tooling planning generates `tooling_plan.md`.
6. Implementation creates MVP scaffold artifacts and records assumptions.
7. Validation checks required outputs.
8. Reviewer Sub-agent simulation generates review artifacts.
9. Final reporting writes `final_report.md`.
10. README generation writes `README.generated.md`.

The CLI entry point is:

```bash
paper-agent run --paper examples/sample_paper.md --out runs/sample_run
```
