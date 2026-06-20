# Assumptions

- The MVP uses deterministic local heuristics instead of LLM calls.
- PDF input is accepted but full semantic PDF parsing is deferred to a paper parser tool.
- The reviewer sub-agent is represented by a deterministic module in this repository.
- Generated implementation output is documentation-first scaffolding unless the paper provides directly implementable pseudocode.
