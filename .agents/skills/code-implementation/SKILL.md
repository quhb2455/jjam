# code-implementation

## Purpose
Implement or scaffold code according to the implementation plan.

## Inputs
- `implementation_plan.md`
- `tooling_plan.md`

## Outputs
- Source files
- `assumptions.md`
- Implementation notes

## Procedure
1. Follow the implementation plan in order.
2. Keep each stage input and output explicit.
3. Use Python for MVP code.
4. Separate mock interfaces from future real integrations.
5. Record arbitrary implementation decisions in `assumptions.md`.

## Rules
- Do not claim paper-specific algorithms are implemented unless code actually implements them.
- Avoid excessive framework dependencies.
- Keep implementation boundaries replaceable.
