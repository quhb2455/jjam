# validation

## Purpose
Run smoke checks and report the validation result.

## Inputs
- Generated run artifacts
- Source code
- Tests

## Outputs
- `validation_result.md`

## Procedure
1. Check required files exist and are non-empty.
2. Run available tests or smoke checks.
3. Record passed checks.
4. Record failures without hiding them.

## Rules
- Do not claim completion without validation.
- Failed checks must remain visible in reports.
