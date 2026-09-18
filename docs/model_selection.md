# Module 4 Model Selection

## First Release

- Chinese semantic embeddings: BGE-M3, or `bge-small-zh-v1.5` when CPU and cost matter more.
- Vector storage: PostgreSQL + pgvector.
- Session recall: Markov transitions and session co-occurrence.
- Re-ranking: the weighted deterministic formula in `app/services/scoring.py`.
- Similar cases: pgvector plus structured multi-feature similarity.
- Explanation: Qwen3-8B-Instruct or an equivalent Chinese Instruct API.

## Ranking Formula

```text
score =
  0.35 * semantic_similarity +
  0.30 * knowledge_graph_relation +
  0.20 * sequence_transition +
  0.10 * historical_feedback +
  0.05 * content_freshness
```

Candidates with less than 35% of the total feature weight are returned as insufficient-information
warnings instead of being rewarded by aggressive renormalization.

## Similar-Case Formula

```text
case_score =
  0.35 * chart_structure_similarity +
  0.30 * hexagram_path_similarity +
  0.20 * topic_symbol_similarity +
  0.15 * session_sequence_similarity
```

Missing features are excluded and the remaining weights are renormalized. The default threshold is
`0.60`, and at most three cases are returned.

## Later Iterations

After enough consented interaction data exists, evaluate LightGBM LambdaMART for re-ranking, SASRec
for session sequence modeling, a Siamese network for case matching, and contextual bandits for
feedback exploration.

The LLM remains an explanation layer. It is never allowed to decide deterministic facts or ranking.
