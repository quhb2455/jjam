# Cross-language implementation conventions

These rules apply unless a paper or ecosystem has a stronger convention.

1. Separate configuration, data loading, core method, training/optimization, evaluation, and command-line entry points.
2. Keep the mathematical core small and testable. Name symbols so they can be traced to the paper; cite equation/algorithm numbers in docstrings or nearby comments when useful.
3. Validate public inputs and data/tensor shapes at boundaries. Do not scatter defensive checks inside the mathematical core.
4. Make randomness explicit and seedable. Record device, dtype, versions, seeds, and reduced-scale settings used for evidence.
5. Keep imports side-effect free. No downloads, training, filesystem mutation, or network access at import time.
6. Put tunable values in configuration or CLI arguments. Do not hide paper hyperparameters as unexplained literals.
7. Prefer standard-library and established dependencies. Every added dependency needs an implementation reason.
8. Provide fast tests for equations, invariants, shapes, edge cases, and a tiny end-to-end path. Expensive reproduction is a separate opt-in command.
9. Use the ecosystem formatter/linter and type annotations where supported. Match existing repository style if implementation code already exists.
10. Fail clearly when an optional dataset, accelerator, weight file, or system tool is absent. Never silently substitute a different experiment.

