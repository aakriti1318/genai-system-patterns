# Foundations

Core building blocks for GenAI systems. These are the primitives that other patterns build upon.

## What's Here

- **Embedding Management**: Token-efficient embedding generation and caching
- **Retrieval Primitives**: Vector search, filtering, and re-ranking patterns
- **Model Interfaces**: Abstraction patterns for LLM providers

## Why These Matter

Most production issues stem from misunderstanding these fundamentals:
- Embedding model choice affects retrieval quality and cost
- Retrieval strategies determine system responsiveness
- Model interface design impacts testability and vendor lock-in

## Patterns

### 1. Embedding Management

**Pattern**: Batch and cache embeddings to reduce cost and latency

**When to use**: Any system using embeddings for retrieval or similarity

**Architecture**:
```
Input Texts → Batch (max 2048 tokens) → Embed → Cache → Vector Store
```

**Key Decisions**:
- Batch size: Balance latency vs throughput (typically 8-32)
- Cache strategy: In-memory for hot paths, Redis for shared state
- Model choice: ada-002 for English, multilingual-e5 for multi-language

**Failure Modes**:
- Token limit exceeded → Truncate with warning, never fail silently
- Cache miss spike → Monitor hit rate, pre-warm on deployment
- Embedding drift → Version embeddings, test on deployment

**Cost Analysis**:
- ada-002: $0.0001/1k tokens
- Cache hit: ~$0 (just storage)
- Re-embedding entire corpus: Plan for this in budgets

### 2. Retrieval Primitives

**Pattern**: Hybrid retrieval combining vector similarity and filtering

**When to use**: Production RAG where metadata filtering is needed

**Architecture**:
```
Query → Vector Search (top-k=100) → Filter (metadata) → Re-rank → Top-N
```

**Key Decisions**:
- Initial k: 10x final results to allow filtering
- Filter logic: Pre-filter vs post-filter based on selectivity
- Re-ranking: Cross-encoder only if <100 candidates

**Failure Modes**:
- Empty results after filtering → Fallback to broader search
- Slow re-ranking → Timeout and return unranked results
- Stale index → Monitor index freshness

**Performance**:
- Vector search: <50ms for 1M vectors
- Re-ranking: ~100ms per 50 documents
- Filtering: Negligible if indexed

### 3. Model Interface Patterns

**Pattern**: Provider-agnostic interface with fallback chains

**When to use**: Any production system using LLMs

**Architecture**:
```python
class LLMInterface:
    def complete(prompt, **kwargs) -> Response
    def stream(prompt, **kwargs) -> Iterator[Response]
    def fallback_chain() -> List[Provider]
```

**Key Decisions**:
- Abstraction level: High enough for portability, low enough for control
- Retry logic: Exponential backoff with jitter
- Fallback order: GPT-4 → GPT-3.5 → Claude-2 based on cost/capability

**Failure Modes**:
- Rate limits → Exponential backoff, circuit breaker pattern
- Context length exceeded → Truncate with strategy (start/end/summary)
- Provider outage → Automatic failover to backup

**Cost Implications**:
- Retries: Can 2-3x costs if not rate-limited properly
- Fallbacks: Design for cost (expensive model → cheaper backup)
- Streaming: Same cost, better UX

## Running Examples

```bash
# Install dependencies
pip install -e ".[foundations]"

# Run embedding example
python foundations/embedding_management.py

# Run retrieval example
python foundations/retrieval_primitives.py

# Run model interface example
python foundations/model_interface.py
```

## Key Takeaways

1. **Cache aggressively**: Embeddings are deterministic, cache them
2. **Plan for failure**: Every external call should have a fallback
3. **Monitor everything**: Latency, cost, and error rates for each component
4. **Version your models**: Embeddings and LLMs change, track versions

## Production Checklist

- [ ] Embedding cache hit rate >80%
- [ ] P99 latency <200ms for retrieval
- [ ] Automatic failover tested
- [ ] Cost monitoring and alerts configured
- [ ] Token truncation strategy documented
- [ ] Model version pinned and tracked
