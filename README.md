# GenAI System Patterns

A living handbook of production-grade GenAI system patterns with runnable code.

## Philosophy

This repository focuses on **real-world production patterns**, not demos or toy examples. Every pattern includes:

- **Architecture decisions**: Why this approach? What are the tradeoffs?
- **Failure modes**: What breaks? How do you detect it?
- **Cost implications**: What drives cost? How to optimize?
- **Security considerations**: What are the risks? How to mitigate?
- **Minimal runnable code**: Enough to understand, not more

## Anti-patterns We Avoid

- ❌ Prompt galleries or example collections
- ❌ Wrapper libraries around LLM APIs
- ❌ Toy demos that don't scale
- ❌ Hype-driven examples without substance
- ❌ Code without discussing failure modes

## Structure

```
genai-system-patterns/
├── foundations/        # Core building blocks (embeddings, retrieval, model interfaces)
├── rag/               # RAG patterns (basic, advanced, hybrid approaches)
├── agents/            # Agent patterns (orchestration, tool usage, multi-agent)
├── evaluation/        # Evaluation patterns (metrics, testing, benchmarks)
├── security_governance/  # Safety, monitoring, compliance patterns
└── ops/               # Deployment, scaling, cost optimization patterns
```

## Quick Start

```bash
# Install core dependencies
pip install -e .

# Install specific module dependencies
pip install -e ".[foundations]"
pip install -e ".[rag]"
pip install -e ".[agents]"

# Run tests
pytest tests/
```

## Design Principles

1. **Production-first**: Every pattern considers reliability, cost, and safety
2. **Python-first**: Core implementations in Python with clear interfaces
3. **Minimal but complete**: Just enough code to understand the pattern
4. **Architecture over code**: READMEs explain decisions, tradeoffs, and failure modes
5. **Real-world focused**: Patterns that have proven value in production systems

## Who This Is For

- Engineers building production GenAI systems
- Architects evaluating design patterns
- Teams moving from proof-of-concept to production
- Anyone who wants to understand real tradeoffs, not hype

## Who This Is NOT For

- Beginners looking for tutorials (try official docs instead)
- Prompt engineers seeking prompt libraries
- Those wanting quick demos without depth

## Contributing

Focus on:
- Production patterns you've actually used
- Clear explanation of tradeoffs and failure modes
- Minimal code that demonstrates the pattern
- Real cost/performance/safety implications

Avoid:
- Toy examples or demos
- Wrapper code around existing libraries
- Patterns without production validation

## License

MIT License - See LICENSE file for details
