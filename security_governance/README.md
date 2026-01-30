# Security & Governance

Production patterns for safe, compliant GenAI systems.

## What's Here

- **Input Validation**: Preventing prompt injection and malicious inputs
- **Output Safety**: Filtering harmful, biased, or PII content
- **Monitoring & Auditing**: Logging for compliance and debugging
- **Cost Controls**: Preventing bill shock and abuse

## Why Security Matters

GenAI introduces new attack vectors:
- Prompt injection can leak data or bypass controls
- Generated content may include PII or harmful material
- Costs can explode with malicious or buggy usage
- Compliance requires comprehensive auditing

## Patterns

### 1. Input Validation

**Pattern**: Validate and sanitize all user inputs before processing

**Attack Vectors**:
- **Prompt injection**: "Ignore previous instructions..."
- **Excessive input**: Million-token inputs → cost explosion
- **Malicious content**: Trying to generate harmful outputs
- **Data extraction**: Trying to leak training data

**Defenses**:
- Input length limits (strict, e.g., 4000 tokens)
- Prompt injection detection (pattern matching + ML)
- Content filtering (hate speech, violence, sexual)
- Rate limiting per user/API key

**Implementation**:
```python
def validate_input(text: str) -> Tuple[bool, str]:
    if len(text) > MAX_LENGTH:
        return False, "Input too long"
    if detect_prompt_injection(text):
        return False, "Suspicious input detected"
    if contains_banned_content(text):
        return False, "Content policy violation"
    return True, "OK"
```

**Failure Modes**:
- False positives → Legitimate queries blocked
- Evasion → Attackers find bypasses
- Performance → Validation adds latency

### 2. Output Safety

**Pattern**: Filter and validate generated content before returning

**Risks**:
- **PII leakage**: Model generates real names, emails, SSNs
- **Harmful content**: Hate speech, violence, sexual content
- **Factual errors**: Hallucinations presented as facts
- **Prompt leakage**: System prompts exposed in output

**Defenses**:
- PII detection and redaction (regex + NER models)
- Content classification (toxicity, harm scores)
- Factuality checks (citations required for claims)
- Prompt leak detection (pattern matching)

**Production Safeguards**:
```python
def validate_output(text: str) -> Tuple[bool, str, str]:
    # Redact PII
    redacted = redact_pii(text)
    
    # Check for harmful content
    toxicity = classify_toxicity(redacted)
    if toxicity > THRESHOLD:
        return False, "", "Content filtered"
    
    # Check for prompt leakage
    if contains_system_prompt(redacted):
        return False, "", "System prompt detected"
    
    return True, redacted, "OK"
```

### 3. Monitoring & Auditing

**Pattern**: Comprehensive logging for security and compliance

**What to Log**:
- All inputs and outputs (encrypted at rest)
- User identity and session
- Model version and parameters
- Costs and latency per request
- Validation failures and reasons

**Retention**:
- Hot storage: 30 days for investigation
- Cold storage: 1-7 years for compliance
- Anonymization: After retention period

**Compliance Requirements**:
- GDPR: Right to deletion, data minimization
- HIPAA: PHI protection (if applicable)
- SOC 2: Access logs, change tracking
- Industry-specific: Financial, healthcare regulations

**Metrics to Monitor**:
- Validation failure rate (input + output)
- PII detection rate
- Toxicity score distribution
- Cost per user (detect abuse)
- Error rate by error type

### 4. Cost Controls

**Pattern**: Prevent cost explosions from abuse or bugs

**Attack Vectors**:
- Malicious users → Intentional resource exhaustion
- Bugs → Infinite loops, unintended high usage
- Legitimate heavy usage → Bill shock

**Defenses**:
- Rate limiting: Per user, per API key, global
- Budget limits: Per request, per user, per day
- Circuit breakers: Kill requests exceeding limits
- Quotas: Free tier limits, upgrade prompts

**Implementation**:
```python
class CostController:
    def check_budget(self, user_id: str, estimated_cost: float) -> bool:
        current = get_user_cost_today(user_id)
        limit = get_user_limit(user_id)
        return (current + estimated_cost) < limit
```

**Monitoring**:
- Cost per user (daily/weekly/monthly)
- Anomaly detection (sudden spikes)
- Projected monthly cost
- Top users by cost

## Running Examples

```bash
# Install dependencies
pip install -e ".[security_governance]"

# Run input validation example
python security_governance/input_validation.py

# Run output safety example
python security_governance/output_safety.py

# Run monitoring example
python security_governance/monitoring.py
```

## Production Checklist

- [ ] Input validation on all user inputs
- [ ] Output filtering for PII and harmful content
- [ ] Rate limiting per user and globally
- [ ] Budget limits and alerts configured
- [ ] Comprehensive logging (inputs, outputs, costs)
- [ ] Log retention policy defined
- [ ] Compliance requirements documented
- [ ] Security review completed
- [ ] Incident response plan documented

## Key Takeaways

1. **Defense in depth**: Multiple layers of protection
2. **Log everything**: Essential for debugging and compliance
3. **Budget controls**: Cost explosions happen fast
4. **Filter outputs**: Never trust generated content
5. **Regular audits**: Security degrades over time

## Common Pitfalls

- No input validation → Prompt injection attacks
- No output filtering → PII leakage
- No cost controls → Bill shock
- Insufficient logging → Can't debug or prove compliance
- Not testing security → Only finding issues in production
