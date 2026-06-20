# paper-code-review

## Purpose
Reviewer Sub-agent skill for comparing paper contents against implementation outputs.

## Inputs
- Paper analysis artifacts
- Implementation plan
- Implementation result
- Validation result

## Outputs
- `review_report.md`
- `paper_code_alignment_matrix.md`
- `revision_plan.md`

## Procedure
1. Evaluate paper component coverage.
2. Evaluate algorithmic fidelity.
3. Evaluate behavioral checks.
4. Evaluate reproducibility.
5. Identify differences, missing parts, and unsupported assumptions.
6. Write a revision plan.

## Rules
- Do not reduce review to "similar" or "different".
- Use explicit criteria.
- Mark partial implementations honestly.
