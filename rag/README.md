# RAG (Retrieval-Augmented Generation)

Production-grade RAG patterns for building reliable, cost-effective retrieval systems.

## What's Here

- **Basic RAG**: Core pattern with chunking, embedding, and retrieval
- **Hybrid Search**: Combining vector similarity with keyword search
- **Advanced RAG**: Query rewriting, re-ranking, and result fusion

## Why RAG is Hard in Production

Simple demos hide real complexities:
- Chunk size affects retrieval quality and cost
- Index staleness causes incorrect answers
- Query reformulation is critical for accuracy
- Cost scales with corpus size and query volume

## Patterns

### 1. Basic RAG

**Pattern**: Chunk documents, embed, store in vector DB, retrieve on query

**When to use**: Starting point for any RAG system

**Architecture**:
```
Documents → Chunk (500 tokens, 50 overlap) → Embed → Vector DB
Query → Embed → Retrieve (top-k=5) → Context → LLM → Response
```

**Key Decisions**:
- Chunk size: 500 tokens balances context vs relevance
- Overlap: 50-100 tokens prevents context loss at boundaries
- Top-k: Start with 5, increase if quality suffers
- Embedding model: Same for docs and queries (obviously, but often missed)

**Failure Modes**:
- No relevant chunks → Return "I don't know" instead of hallucinating
- Too many chunks → LLM context overflow, summarize or prioritize
- Outdated index → Implement incremental updates, not full reindex

**Cost Analysis**:
- Embedding costs: One-time for docs, per-query for searches
- Vector DB: Storage + query costs
- LLM: Grows with context size (retrieved chunks)

**Performance**:
- Indexing: ~1000 docs/sec with batching
- Query latency: <100ms for retrieval + 1-2s for LLM
- Freshness: Minutes for incremental updates

### 2. Hybrid Search

**Pattern**: Combine vector similarity with BM25 keyword search

**When to use**: Queries with specific keywords or entities

**Architecture**:
```
Query → [Vector Search (top-50) + BM25 (top-50)] → RRF → Top-5 → LLM
```

**Key Decisions**:
- Fusion method: Reciprocal Rank Fusion (RRF) is simple and effective
- Weight ratio: 50/50 vector/keyword for general use
- When to use: Proper nouns, technical terms benefit from hybrid

**Failure Modes**:
- Keyword dominates → Adjust weights based on query type
- Slow fusion → Pre-compute and cache common queries
- Inconsistent rankings → Log and analyze fusion conflicts

**Performance Impact**:
- Latency: +20-30ms for BM25 + fusion
- Quality: +10-20% for queries with specific terms
- Cost: Minimal (BM25 is cheap)

### 3. Advanced RAG: Query Rewriting

**Pattern**: Transform user query for better retrieval

**When to use**: Natural language queries that don't match document style

**Architecture**:
```
User Query → [Rewrite, Expand, Generate Sub-queries] → Multiple Retrievals → Dedupe → Rank → LLM
```

**Key Decisions**:
- Rewrite strategy: Simplify, expand, or generate sub-queries
- When to rewrite: Based on query analysis (length, ambiguity)
- Cost: Each rewrite = 1 LLM call, budget accordingly

**Failure Modes**:
- Over-rewriting → Query drift, retrieve irrelevant docs
- Latency explosion → Parallelize retrievals, set timeout
- Cost explosion → Cache rewrites, limit sub-queries

**When to Use**:
- User queries are conversational
- Domain-specific terminology in documents
- Multi-hop reasoning required

**Cost**:
- Per query: 1-3 LLM calls (rewrite) + 2-5 retrievals
- Monitor: Rewrite hit rate and quality impact

### 4. Re-ranking

**Pattern**: Use cross-encoder to re-rank top retrieved documents

**When to use**: When precision matters more than recall

**Architecture**:
```
Query → Vector Search (top-100) → Cross-Encoder Re-rank → Top-5 → LLM
```

**Key Decisions**:
- Initial k: 10-20x final results (retrieve 100, return 5)
- Model: ms-marco-MiniLM-L-6-v2 is fast and effective
- When to skip: If initial retrieval is already good

**Failure Modes**:
- Slow re-ranking → Set timeout, fallback to vector scores
- Over-reliance → Re-ranker can introduce bias
- Model drift → A/B test re-ranker versions

**Performance**:
- Latency: +50-200ms depending on candidate count
- Quality: +15-25% NDCG improvement
- Cost: Compute for cross-encoder (run locally)

## Running Examples

```bash
# Install dependencies
pip install -e ".[rag]"

# Run basic RAG example
python rag/basic_rag.py

# Run hybrid search example
python rag/hybrid_search.py

# Run query rewriting example
python rag/query_rewriting.py
```

## Production Checklist

- [ ] Chunk size and overlap validated on your data
- [ ] Retrieval quality metrics (MRR, NDCG) tracked
- [ ] Index freshness SLA defined and monitored
- [ ] Query latency P95 < 200ms
- [ ] Cost per query monitored and alerted
- [ ] Fallback for "no relevant docs" cases
- [ ] A/B testing framework for retrieval changes

## Key Takeaways

1. **Chunk carefully**: Size affects both quality and cost
2. **Hybrid > Pure vector**: For most real-world queries
3. **Monitor quality continuously**: Retrieval degrades over time
4. **Budget for rewrites**: They improve quality but add cost
5. **Re-ranking is expensive**: Use selectively, not by default

## Common Pitfalls

- Using different embeddings for docs vs queries
- Not handling "no results" cases gracefully
- Ignoring index staleness
- Over-engineering: Start simple, add complexity only when measured
- Forgetting to version your retrieval pipeline
