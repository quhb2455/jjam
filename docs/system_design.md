# System Design

## Overview
The harness is built around a single Orchestrator. Each pipeline stage has explicit input and output schemas defined in `src/paper_agent/schemas.py`.

## Components
- `orchestrator.py`: controls the workflow.
- `paper_analysis.py`: reads papers and extracts implementation-relevant facts.
- `planning.py`: creates implementation plans.
- `tool_registry.py`: records default Tools and additional Tool review requirements.
- `skill_registry.py`: records default Skills.
- `code_implementation.py`: creates MVP implementation artifacts and assumptions.
- `validation.py`: checks generated artifacts.
- `reviewer.py`: simulates the Reviewer Sub-agent.
- `reporting.py`: writes the final report.
- `readme_writer.py`: writes run-specific README output.

## Extension Points
- Replace `PaperReader` with a real PDF parser.
- Replace `PaperAnalyzer` with an LLM-backed analyzer.
- Replace `CodeImplementer` with a paper-specific code generator.
- Replace `Validator` with real test runner integrations.
- Replace `ReviewerSubAgent` with a dedicated sub-agent call.
