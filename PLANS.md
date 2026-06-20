# PLANS.md

## MVP Plan
1. Provide a Python package with a `paper-agent` CLI.
2. Accept Markdown, text, and placeholder PDF paper input.
3. Generate structured analysis, planning, tooling, validation, review, and final report artifacts.
4. Keep all stage interfaces replaceable so real LLM APIs, MCP tools, PDF parsers, and test runners can be connected later.
5. Include default Skill definitions and Tool planning.
6. Include tests for the orchestrator and CLI.

## Near-Term Improvements
- Add a real PDF parser backend.
- Add typed configuration for provider selection.
- Add LLM-backed analysis and planning adapters.
- Generate paper-specific source code workspaces when explicit algorithms are available.
- Add rubric scores to reviewer outputs.

## Out Of Scope For MVP
- Multi-agent implementation teams.
- Networked LLM calls.
- Arbitrary paper-to-code synthesis.
- Heavy workflow frameworks.
