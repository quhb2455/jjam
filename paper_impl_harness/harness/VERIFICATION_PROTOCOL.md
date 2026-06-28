# Paper-to-code verification protocol

Verification has three evidence levels:

- **Structural**: modules, data flow, shapes, loss terms, and algorithm steps match the paper.
- **Numerical**: equations and invariants match hand calculations, reference cases, or independent implementations.
- **Empirical**: the paper's metric is measured under a comparable dataset, protocol, scale, and checkpoint regime.

For every central claim, add one record to `.paper-harness/alignment.json` and a readable row to `docs/paper_code_alignment.md`. A record is incomplete unless it has:

1. a precise paper location and summarized claim;
2. at least one real implementation file plus symbol or line description;
3. at least one real test/experiment file and named test or command;
4. an evidence level and honest status;
5. any deviation and its expected effect.

Review independently after coding:

- compare equations term-by-term, including normalization, signs, reduction, boundary conditions, and update order;
- trace shapes and units through the full path;
- compare preprocessing, initialization, sampling, optimization, stopping, and evaluation protocols;
- test invariants and degenerate cases;
- separate “test passes” from “paper result reproduced”;
- mark unsupported claims `unverified` or `deviates`, never `verified`.

