# Training-Free Retrieval Calibration For Lightweight QA

## Abstract
This sample paper proposes a training-free method for calibrating retrieved passages before a question answering model consumes them. The method scores passages using lexical overlap, source reliability, and recency metadata, then selects a compact context window.

## Key Contributions
- A training-free passage calibration pipeline.
- A data strategy that accepts question, passages, source metadata, and timestamps.
- An evaluation method using answer accuracy, context compression ratio, and ablation over scoring features.

## Method
Input: a user question, a list of retrieved passages, and metadata for each passage.
Output: a ranked list of passages and a compact context window.

Algorithm:
1. Normalize the question and passage text.
2. Compute overlap_score = shared_terms / question_terms.
3. Compute metadata_score = reliability_weight + recency_weight.
4. Compute final_score = overlap_score + metadata_score.
5. Return top-k passages.

## Evaluation
The paper evaluates accuracy, compression ratio, and ablation results for overlap, reliability, and recency features.
