# Implementability assessment rubric

Score each dimension from 0 to 2 and support it with paper locations.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Method specification | Central method is absent/contradictory | Important details require bounded assumptions | Algorithm/equations are sufficient |
| Resource feasibility | Requires inaccessible resources | Reduced-scale substitute is possible | Can run locally as described or at meaningful scale |
| Data/asset access | Essential assets are unavailable | Synthetic/public substitute supports only part | Required data/assets are available or generatable |
| Evaluation feasibility | Main behavior cannot be checked | Structural/numerical checks only | Claimed behavior has a practical evaluation |
| Dependency feasibility | Critical proprietary/unknown component | Replaceable component with disclosed deviation | Dependencies are available and suitable |

Decision rules:

- `feasible`: no zero in method specification, data/assets, or evaluation; core contribution can be tested.
- `partial`: faithful central mechanism is possible, but full training, dataset, scale, or evaluation is not.
- `not_feasible`: central mechanism cannot be determined or exercised without inventing decisive details.

The score is guidance, not arithmetic theater. Explain the binding constraint, the minimum meaningful scope, assumptions, excluded claims, and what evidence would change the decision.

