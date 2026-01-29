# Ops (Operations)

Production patterns for deploying, scaling, and operating GenAI systems.

## What's Here

- **Deployment Patterns**: Blue-green, canary, feature flags
- **Scaling Strategies**: Batching, caching, rate limiting
- **Cost Optimization**: Right-sizing, caching, model selection
- **Monitoring & Alerting**: What to track and when to alert

## Why Ops is Different for GenAI

GenAI systems have unique operational challenges:
- Non-deterministic behavior makes debugging hard
- Costs scale with usage, not infrastructure
- Quality degradation is silent and gradual
- Vendor dependencies and rate limits

## Patterns

### 1. Deployment Strategies

**Pattern**: Deploy changes gradually with rollback capability

**Strategies**:

**Blue-Green Deployment**:
- Two identical environments: blue (current) and green (new)
- Switch traffic to green after validation
- Instant rollback by switching back to blue

**Canary Deployment**:
- Route 5% of traffic to new version
- Monitor key metrics (quality, latency, errors)
- Gradually increase to 100% or rollback

**Feature Flags**:
- Deploy code disabled, enable via config
- A/B test different prompts, models, parameters
- Instant disable without code deployment

**When to use each**:
- Blue-green: Major changes, need instant rollback
- Canary: Gradual rollout, measure impact
- Feature flags: Rapid experimentation, A/B testing

**Key Metrics to Monitor**:
- Quality: Task success rate, user satisfaction
- Latency: P50, P95, P99
- Cost: Per request, per user, total
- Errors: Rate, types, patterns

### 2. Scaling Strategies

**Pattern**: Handle growing traffic efficiently

**Techniques**:

**Request Batching**:
- Accumulate requests for 100ms
- Process in single batch
- Reduces API calls by 10-50x

**Caching**:
- Embedding cache: 80%+ hit rate typical
- Response cache: For deterministic queries
- Invalidation: Time-based or event-based

**Rate Limiting**:
- Per user: Prevent abuse
- Global: Respect vendor limits
- Graceful degradation: Queue vs reject

**Auto-scaling**:
- Scale on: Queue depth, latency, error rate
- NOT on: CPU/memory (not the bottleneck)
- Pre-warm: Embeddings, popular queries

**Cost vs Latency Tradeoffs**:
- Batching: Lower cost, higher latency
- Caching: Lower cost, same latency
- Bigger models: Higher cost, better quality
- Streaming: Same cost, better UX

### 3. Cost Optimization

**Pattern**: Deliver value at minimum cost

**Strategies**:

**Model Selection**:
- Use cheapest model that meets quality bar
- GPT-3.5 vs GPT-4: 10x cost difference
- Consider open-source models for high-volume

**Right-sizing**:
- Measure actual token usage
- Truncate contexts intelligently
- Summarize long inputs

**Caching**:
- Cache embeddings aggressively
- Cache responses for common queries
- Cache costs ~$0 vs re-computing

**Batching**:
- Batch embeddings: Same cost, higher throughput
- Batch LLM calls where possible

**Cost Breakdown** (typical RAG system):
- Embeddings: 10-20%
- LLM generation: 70-80%
- Vector DB: 5-10%
- Compute/infrastructure: 5-10%

**Optimization Priority**:
1. Cache hot queries/embeddings (biggest impact)
2. Use cheaper models where quality allows
3. Optimize context size (reduce tokens)
4. Batch requests (reduce API overhead)

### 4. Monitoring & Alerting

**Pattern**: Know what's happening, act when needed

**What to Monitor**:

**Quality Metrics**:
- Task success rate
- User satisfaction (thumbs up/down)
- Retrieval quality (MRR, NDCG)
- Generation quality (factuality, relevance)

**Performance Metrics**:
- Latency: P50, P95, P99, max
- Throughput: Requests/sec
- Error rate: By type (timeouts, rate limits, etc.)
- Availability: Uptime %

**Cost Metrics**:
- Cost per request
- Cost per user (daily/monthly)
- Total cost
- Projected monthly cost

**System Metrics**:
- Cache hit rate
- Queue depth
- Model version in use
- Vendor API status

**Alert Thresholds**:

**Critical** (page on-call):
- Availability < 99.5%
- P95 latency > 2x baseline
- Error rate > 5%
- Cost spike > 2x normal

**Warning** (notify, investigate):
- Quality drop > 10%
- Cache hit rate < 70%
- Cost spike > 1.5x normal

**Info** (log, review):
- Model version change
- Deployment complete
- Config change

## Running Examples

```bash
# Install dependencies
pip install -e ".[ops]"

# Run caching example
python ops/caching_strategy.py

# Run cost monitoring example
python ops/cost_monitoring.py

# Run deployment example
python ops/deployment_patterns.py
```

## Production Checklist

- [ ] Deployment strategy defined (blue-green, canary, or feature flags)
- [ ] Rollback procedure tested
- [ ] Caching implemented (embeddings at minimum)
- [ ] Rate limiting configured
- [ ] Cost monitoring and alerts configured
- [ ] Quality metrics tracked
- [ ] On-call runbook documented
- [ ] Incident response plan defined

## Key Takeaways

1. **Deploy gradually**: Canary deployments catch issues early
2. **Cache aggressively**: Biggest cost reduction lever
3. **Monitor quality continuously**: Degradation is silent
4. **Budget for scale**: Costs grow linearly with traffic
5. **Plan for failure**: Vendor outages happen

## Common Pitfalls

- Deploying changes without canary → Production incidents
- Not caching → 10x higher costs
- Wrong scaling metrics → Auto-scale doesn't help
- Alert fatigue → Too many low-priority alerts
- No cost tracking → Bill shock
- Not versioning prompts/models → Can't rollback

## Cost Optimization Quick Wins

1. **Enable caching** (embeddings + responses): -50% cost
2. **Use cheaper models** where quality allows: -70% cost
3. **Optimize context size** (smarter truncation): -30% cost
4. **Batch requests** (embeddings especially): -20% cost
5. **A/B test models** (validate cheaper works): Variable savings
