# Evaluation

Production patterns for testing and measuring GenAI systems.

## What's Here

- **Retrieval Metrics**: MRR, NDCG, precision@k for RAG systems
- **Generation Quality**: Factuality, relevance, and coherence metrics
- **Regression Testing**: Catching quality degradation in production

## Why Evaluation is Critical

GenAI systems degrade silently:
- Model updates change behavior
- Data drift affects retrieval
- Prompt changes have unintended side effects
- No evaluation = flying blind

## Patterns

### 1. Retrieval Evaluation

**Pattern**: Measure retrieval quality with ground truth queries

**Metrics**:
- **MRR (Mean Reciprocal Rank)**: Position of first relevant result
- **NDCG@k**: Relevance-weighted ranking quality
- **Precision@k**: % of top-k results that are relevant
- **Recall@k**: % of relevant docs in top-k

**When to use each**:
- MRR: When first result matters most (e.g., Q&A)
- NDCG: When relevance is graded (very/somewhat/not relevant)
- Precision: When accuracy of results matters
- Recall: When completeness matters

**Creating test sets**:
- Start with 50-100 query-document pairs
- Use production queries + human labeling
- Cover edge cases: ambiguous, multi-intent, out-of-domain
- Update as system evolves

**Failure modes**:
- Test set too small → High variance, unreliable
- Test set too easy → False confidence
- Stale test set → Overfitting to old patterns

### 2. Generation Quality

**Pattern**: Evaluate LLM outputs on multiple dimensions

**Metrics**:
- **Factuality**: Does answer match ground truth?
- **Relevance**: Does answer address the question?
- **Coherence**: Is answer well-structured?
- **Safety**: Any harmful/biased content?

**Evaluation approaches**:
1. **LLM-as-judge**: Use GPT-4 to grade outputs
2. **Human eval**: Gold standard but expensive
3. **Automated metrics**: BLEU, ROUGE for reference comparison
4. **Model-based**: Fine-tuned classifier for your domain

**When to use each**:
- LLM-as-judge: Fast iteration, correlation with human
- Human eval: Final validation, sensitive domains
- Automated: Continuous monitoring, cheap
- Model-based: High volume, domain-specific

**Cost considerations**:
- LLM-as-judge: ~$0.01 per evaluation (GPT-4)
- Human: $0.50-$2.00 per evaluation
- Automated: Nearly free
- Model-based: Training cost upfront, cheap inference

### 3. Regression Testing

**Pattern**: Continuous monitoring to catch quality degradation

**Architecture**:
```
Every deployment → Run test suite → Compare to baseline → Alert on regression
```

**What to test**:
- Golden query set (50-100 queries)
- Edge cases and previous failures
- Performance benchmarks (latency, cost)

**Alert thresholds**:
- Critical: >10% drop in key metric
- Warning: >5% drop in any metric
- Info: Any change in P95 latency

**Automation**:
- Run on every deployment
- Run daily on production
- Store results in time series DB
- Dashboard for trends

**Common pitfalls**:
- Not testing regularly → Slow detection
- No baselines → Can't measure regression
- Alert fatigue → Set reasonable thresholds

## Running Examples

```bash
# Install dependencies
pip install -e ".[evaluation]"

# Run retrieval metrics example
python evaluation/retrieval_metrics.py

# Run generation quality example
python evaluation/generation_quality.py

# Run regression test example
python evaluation/regression_testing.py
```

## Production Checklist

- [ ] Test set covers edge cases and common queries
- [ ] Metrics tracked in time series database
- [ ] Alerts configured for regressions
- [ ] Evaluation runs automatically on deployment
- [ ] Human evaluation for critical changes
- [ ] Test set updated quarterly

## Key Takeaways

1. **Start simple**: 50 queries + MRR beats 0 evaluation
2. **Automate everything**: Manual testing doesn't scale
3. **Monitor continuously**: Quality degrades silently
4. **Update test sets**: Systems and users evolve
5. **Multiple metrics**: No single metric captures everything

## Metrics to Track

**Retrieval**:
- MRR, NDCG@5, Precision@5
- Zero-result rate
- Latency P50/P95/P99

**Generation**:
- Factuality score (0-1)
- Relevance score (0-1)
- Refusal rate (safety)
- Length distribution

**System**:
- End-to-end latency
- Cost per query
- Error rate
- Throughput

## Common Pitfalls

- No test set → Can't measure anything
- Test set too small → High variance
- Only testing happy path → Missing edge cases
- Not versioning test sets → Can't track over time
- Ignoring production data → Test set drift
