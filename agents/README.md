# Agents

Production patterns for building reliable agent systems.

## What's Here

- **Tool-using Agents**: Reliable tool selection and execution
- **Multi-Agent Orchestration**: Coordination patterns for agent teams
- **Agent Error Handling**: Graceful degradation and recovery

## Why Agents are Risky in Production

Agents introduce non-determinism and complexity:
- Tool selection can fail unpredictably
- Loops and recursion can explode costs
- Error propagation across agent boundaries
- Difficult to test and debug

## Patterns

### 1. Tool-Using Agents

**Pattern**: Agent selects and executes tools based on task requirements

**When to use**: Tasks requiring multiple steps with different capabilities

**Architecture**:
```
User Request → Task Planning → Tool Selection → Tool Execution → Result Synthesis
```

**Key Decisions**:
- Tool schema: Clear descriptions, typed parameters, error handling
- Selection strategy: Few-shot prompting vs fine-tuned model
- Execution safety: Sandboxing, timeouts, cost limits

**Failure Modes**:
- Wrong tool selected → Provide clear tool descriptions and examples
- Tool execution fails → Retry with different parameters or fallback tool
- Infinite loops → Max iterations limit (typically 10-15)
- Cost explosion → Budget per request, kill on threshold

**Cost Analysis**:
- Per iteration: 1 LLM call (tool selection) + tool execution cost
- Average task: 3-5 iterations
- Monitor: Iteration count distribution and cost per task

**Production Safeguards**:
- Max iterations: 15 (hard limit)
- Timeout per tool: 30 seconds
- Budget per request: $0.50 (adjustable)
- Rate limiting: Per user/API key

### 2. Multi-Agent Orchestration

**Pattern**: Multiple specialized agents coordinated by orchestrator

**When to use**: Complex tasks benefiting from specialization

**Architecture**:
```
Orchestrator → [Research Agent, Code Agent, Review Agent] → Result Aggregation
```

**Key Decisions**:
- Communication: Shared context vs message passing
- Coordination: Centralized (orchestrator) vs decentralized (peer-to-peer)
- State management: Who owns state, how to handle conflicts

**Failure Modes**:
- Agent disagreement → Use voting or confidence scores
- Deadlock → Timeout and escalate to human
- Context drift → Explicit context passing, not implicit state

**When to Use**:
- Task naturally decomposes by skill (research vs code vs review)
- Parallel execution reduces latency
- Specialization improves quality

**When NOT to Use**:
- Task is simple enough for single agent
- Communication overhead > benefit of specialization
- Debugging complexity outweighs benefits

### 3. Agent Error Handling

**Pattern**: Structured error recovery with graceful degradation

**When to use**: Always - agents must handle errors gracefully

**Architecture**:
```
Try Agent Action → Error → Classify Error → Recovery Strategy → Fallback/Retry/Escalate
```

**Error Types**:
1. **Transient** (rate limit, timeout): Retry with backoff
2. **Invalid input**: Request clarification or use default
3. **Tool failure**: Try alternative tool or skip
4. **Logic error**: Log, return partial result

**Recovery Strategies**:
- Retry: For transient errors (max 3 times)
- Fallback: Use simpler tool or default behavior
- Partial result: Return what we have with caveats
- Human escalation: For critical failures

**Production Checklist**:
- Every tool call has timeout
- Every API call has retry logic
- Every agent has max iterations
- Every request has cost budget
- All errors logged with context

## Running Examples

```bash
# Install dependencies
pip install -e ".[agents]"

# Run tool-using agent example
python agents/tool_using_agent.py

# Run multi-agent example
python agents/multi_agent.py

# Run error handling example
python agents/error_handling.py
```

## Key Takeaways

1. **Limit iterations**: Agents can loop infinitely, set hard limits
2. **Budget everything**: Cost can explode with agent autonomy
3. **Test failure modes**: Error cases are more common than success
4. **Logging is critical**: Agent decisions are hard to debug
5. **Start simple**: Single agent + tools before multi-agent

## Production Metrics to Track

- Iterations per task (mean, p95, max)
- Cost per task
- Success rate by task type
- Tool selection accuracy
- Error rate by error type
- Human escalation rate

## Common Pitfalls

- No iteration limit → infinite loops
- No cost budget → bill shock
- Poor tool descriptions → wrong tool selection
- No error handling → cascading failures
- Over-engineering → use single agent when sufficient
