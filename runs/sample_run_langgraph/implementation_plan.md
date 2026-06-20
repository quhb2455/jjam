# Implementation Plan

## Implementation Objective
Implement an MVP harness for the paper target: Training-Free Retrieval Calibration For Lightweight QA

## Implementation Targets By Paper Component
- Represent the paper method as explicit pipeline stages.
- Model paper data assumptions and expected input artifacts.
- Generate validation and review artifacts from implementation results.
- Produce a reproducible README and final report.

## Module Structure
- orchestrator: controls the end-to-end workflow
- paper_analysis: reads and extracts implementation-relevant paper facts
- planning: converts analysis into a build plan
- skill_registry/tool_registry: records reusable capabilities
- code_implementation: creates MVP implementation artifacts
- validation: performs smoke checks
- reviewer: reviewer sub-agent simulation
- reporting/readme_writer: final documentation

## File Structure
- src/paper_agent/*.py
- .agents/skills/*/SKILL.md
- docs/*.md
- examples/sample_paper.md
- runs/<run_id>/*.md
- tests/*.py

## Required Dependencies
- Python >=3.10
- pytest for development tests

## Required Skills
- paper-analysis
- implementation-planning
- code-implementation
- validation
- paper-code-review
- final-report-generation

## Required Tools
- filesystem tool
- git tool when repository metadata is available
- python execution tool
- test runner tool
- package inspection tool
- paper parser tool
- report writer tool

## Implementation Order
1. Read paper input
2. Analyze paper and write paper_summary.md plus implementation_spec.md
3. Write implementation_plan.md
4. Write tooling_plan.md
5. Run implementation stage
6. Validate outputs
7. Run reviewer sub-agent simulation
8. Write final report and generated README

## Test Plan
- Unit test the orchestrator creates all required artifacts
- Unit test CLI argument path executes successfully
- Smoke test sample paper run

## Expected Risks
- MVP paper analysis is heuristic and cannot guarantee semantic completeness.
- PDF parsing is a placeholder integration point.
- Generated implementation work is represented as scaffolding, not arbitrary paper code synthesis.

## Items Not Implemented And Reasons
- Real LLM API calls
- Full PDF semantic extraction
- Automatic generation of arbitrary research code repositories
