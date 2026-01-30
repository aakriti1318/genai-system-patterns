"""
Model Interface Pattern

Demonstrates provider-agnostic LLM interface with fallback chains.

Key Production Concerns:
1. Reliability: Automatic fallback when providers fail
2. Cost: Intelligent routing based on capability/cost
3. Observability: Track latency, errors, and costs per provider
"""

from typing import Iterator, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time
import random


class ProviderType(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    text: str
    model: str
    provider: ProviderType
    tokens_used: int
    latency_ms: float
    cost_usd: float


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    provider: ProviderType
    model: str
    max_retries: int = 3
    timeout_seconds: float = 30.0
    cost_per_1k_tokens: float = 0.002


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures.
    
    Pattern: If a provider fails repeatedly, stop trying for a cooldown period.
    """
    
    def __init__(self, failure_threshold: int = 5, cooldown_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self._failures = 0
        self._last_failure_time = 0.0  # Use time.monotonic() to avoid clock adjustments
        self._is_open = False
    
    def record_success(self):
        """Record successful call."""
        self._failures = 0
        self._is_open = False
    
    def record_failure(self):
        """Record failed call."""
        self._failures += 1
        self._last_failure_time = time.monotonic()  # Monotonic for reliable timing
        
        if self._failures >= self.failure_threshold:
            self._is_open = True
            print(f"Circuit breaker OPEN after {self._failures} failures")
    
    def can_attempt(self) -> bool:
        """Check if we should attempt to call this provider."""
        if not self._is_open:
            return True
        
        # Check if cooldown period has passed
        if time.monotonic() - self._last_failure_time > self.cooldown_seconds:
            print("Circuit breaker attempting reset...")
            self._is_open = False
            self._failures = 0
            return True
        
        return False


class LLMProvider:
    """Base class for LLM provider implementations."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.circuit_breaker = CircuitBreaker()
    
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate completion from prompt.
        
        In production: Implement actual API calls with retry logic.
        """
        if not self.circuit_breaker.can_attempt():
            raise Exception(f"Circuit breaker open for {self.config.provider.value}")
        
        try:
            response = self._call_api(prompt, **kwargs)
            self.circuit_breaker.record_success()
            return response
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise
    
    def _call_api(self, prompt: str, **kwargs) -> LLMResponse:
        """Mock API call. In production: implement real API call."""
        # Simulate API latency
        time.sleep(0.1)
        
        # Simulate occasional failures (5% failure rate)
        if random.random() < 0.05:
            raise Exception(f"API error from {self.config.provider.value}")
        
        tokens = len(prompt.split())  # Rough estimate
        cost = (tokens / 1000) * self.config.cost_per_1k_tokens
        
        return LLMResponse(
            text=f"Response from {self.config.model}",
            model=self.config.model,
            provider=self.config.provider,
            tokens_used=tokens,
            latency_ms=100.0,
            cost_usd=cost
        )


class LLMInterface:
    """Provider-agnostic interface with automatic fallback.
    
    Production Pattern:
    - Try providers in order of capability/cost
    - Automatic fallback on failure
    - Circuit breakers to prevent cascading failures
    - Comprehensive metrics for monitoring
    """
    
    def __init__(self, provider_configs: List[ProviderConfig]):
        self.providers = [LLMProvider(config) for config in provider_configs]
        self._metrics = {
            "total_requests": 0,
            "total_cost": 0.0,
            "provider_usage": {},
            "fallback_count": 0
        }
    
    def complete(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate completion with automatic fallback.
        
        Tries providers in order until one succeeds.
        """
        self._metrics["total_requests"] += 1
        last_error = None
        
        for i, provider in enumerate(self.providers):
            try:
                print(f"Attempting {provider.config.provider.value}...")
                response = provider.complete(prompt, **kwargs)
                
                # Track metrics
                provider_name = provider.config.provider.value
                self._metrics["provider_usage"][provider_name] = \
                    self._metrics["provider_usage"].get(provider_name, 0) + 1
                self._metrics["total_cost"] += response.cost_usd
                
                if i > 0:
                    self._metrics["fallback_count"] += 1
                    print(f"✓ Fallback successful to {provider_name}")
                
                return response
                
            except Exception as e:
                last_error = e
                print(f"✗ {provider.config.provider.value} failed: {e}")
                
                if i < len(self.providers) - 1:
                    print(f"  Falling back to next provider...")
                continue
        
        # All providers failed
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get usage metrics for monitoring."""
        return self._metrics.copy()


def main():
    """Demonstrate model interface pattern with fallback."""
    print("=== Model Interface Pattern with Fallback ===\n")
    
    # Configure fallback chain: expensive → cheap
    configs = [
        ProviderConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4",
            cost_per_1k_tokens=0.03
        ),
        ProviderConfig(
            provider=ProviderType.OPENAI,
            model="gpt-3.5-turbo",
            cost_per_1k_tokens=0.002
        ),
        ProviderConfig(
            provider=ProviderType.ANTHROPIC,
            model="claude-2",
            cost_per_1k_tokens=0.008
        ),
    ]
    
    interface = LLMInterface(configs)
    
    # Example usage
    prompt = "Explain the benefits of circuit breakers in distributed systems."
    
    print("Making request...")
    try:
        response = interface.complete(prompt)
        print(f"\n✓ Success!")
        print(f"  Model: {response.model}")
        print(f"  Provider: {response.provider.value}")
        print(f"  Cost: ${response.cost_usd:.6f}")
        print(f"  Latency: {response.latency_ms}ms")
    except Exception as e:
        print(f"\n✗ All providers failed: {e}")
    
    print("\n" + "="*50)
    print("\nMetrics:")
    metrics = interface.get_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*50)
    print("\nKey Takeaways:")
    print("1. Abstract provider details behind common interface")
    print("2. Implement automatic fallback for reliability")
    print("3. Use circuit breakers to prevent cascading failures")
    print("4. Track metrics for cost optimization and monitoring")
    print("5. Design fallback chain: expensive/capable → cheap/basic")


if __name__ == "__main__":
    main()
