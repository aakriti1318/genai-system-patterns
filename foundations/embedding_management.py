"""
Embedding Management Pattern

Demonstrates batching and caching for cost-efficient embedding generation.

Key Production Concerns:
1. Cost: Batch requests to minimize API calls
2. Latency: Cache hot embeddings
3. Reliability: Handle token limits gracefully
"""

from typing import List, Dict, Optional
import hashlib
import time


class EmbeddingCache:
    """Simple in-memory cache for embeddings.
    
    In production, use Redis or similar distributed cache.
    """
    
    def __init__(self):
        self._cache: Dict[str, List[float]] = {}
        self._hits = 0
        self._misses = 0
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text."""
        key = self._hash_text(text)
        if key in self._cache:
            self._hits += 1
            return self._cache[key]
        self._misses += 1
        return None
    
    def set(self, text: str, embedding: List[float]):
        """Cache embedding for text."""
        key = self._hash_text(text)
        self._cache[key] = embedding
    
    def _hash_text(self, text: str) -> str:
        """Create cache key from text.
        
        Uses MD5 for fast hashing. MD5 is acceptable here because:
        1. This is for cache keys, not cryptographic security
        2. Collision resistance is sufficient for caching purposes
        3. Speed matters for cache lookups
        Production: MD5 is fine for cache keys, but document this choice.
        """
        return hashlib.md5(text.encode()).hexdigest()
    
    def stats(self) -> Dict[str, float]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "size": len(self._cache)
        }


class EmbeddingManager:
    """Manages embedding generation with batching and caching.
    
    Production Pattern:
    - Batch requests to reduce API calls
    - Cache results to avoid re-computing
    - Handle token limits gracefully
    - Monitor costs and performance
    """
    
    def __init__(self, batch_size: int = 16, max_tokens: int = 8191):
        self.batch_size = batch_size
        self.max_tokens = max_tokens
        self.cache = EmbeddingCache()
        self._total_tokens = 0
        self._total_requests = 0
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts with batching and caching.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (one per text)
            
        Production Notes:
        - Check cache first to minimize costs
        - Batch uncached texts to reduce API calls
        - Handle token limits (truncate with warning, don't fail silently)
        - Log metrics for cost tracking
        """
        # Initialize results list with None placeholders
        results = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []
        
        # Check cache first
        for i, text in enumerate(texts):
            cached = self.cache.get(text)
            if cached:
                results[i] = cached
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)
        
        # Embed uncached texts in batches
        if uncached_texts:
            embeddings = self._embed_batch(uncached_texts)
            
            # Cache new embeddings and insert into results at correct positions
            for idx, text, embedding in zip(uncached_indices, uncached_texts, embeddings):
                self.cache.set(text, embedding)
                results[idx] = embedding
        
        return results
    
    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts.
        
        In production, replace with actual embedding API call.
        This is a stub that simulates the pattern.
        """
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            # Truncate if needed (production: use tiktoken for accurate counting)
            batch = [self._truncate_text(t) for t in batch]
            
            # Simulate API call
            # In production: call OpenAI, Cohere, or local model
            batch_embeddings = self._mock_embed(batch)
            embeddings.extend(batch_embeddings)
            
            self._total_requests += 1
            self._total_tokens += sum(len(t.split()) for t in batch)  # Rough estimate
        
        return embeddings
    
    def _truncate_text(self, text: str) -> str:
        """Truncate text to fit token limit.
        
        Production: Use tiktoken for accurate token counting.
        """
        # Rough approximation: 1 token ≈ 4 characters
        max_chars = self.max_tokens * 4
        if len(text) > max_chars:
            print(f"WARNING: Text truncated from {len(text)} to {max_chars} chars")
            return text[:max_chars]
        return text
    
    def _mock_embed(self, texts: List[str]) -> List[List[float]]:
        """Mock embedding function for demonstration.
        
        In production, replace with actual API call.
        """
        # Simulate API latency
        time.sleep(0.01 * len(texts))
        
        # Return mock embeddings (in production: real embeddings)
        return [[0.1] * 1536 for _ in texts]  # OpenAI ada-002 dimension
    
    def get_stats(self) -> Dict:
        """Get usage statistics for cost monitoring."""
        cache_stats = self.cache.stats()
        
        # Estimate cost (OpenAI ada-002: $0.0001 per 1k tokens)
        estimated_cost = (self._total_tokens / 1000) * 0.0001
        
        return {
            "total_requests": self._total_requests,
            "total_tokens": self._total_tokens,
            "estimated_cost_usd": estimated_cost,
            "cache": cache_stats
        }


def main():
    """Demonstrate embedding management pattern."""
    print("=== Embedding Management Pattern ===\n")
    
    manager = EmbeddingManager(batch_size=8)
    
    # Example texts
    texts = [
        "How do I reset my password?",
        "What are your business hours?",
        "How do I contact support?",
        "How do I reset my password?",  # Duplicate - should hit cache
        "What is your refund policy?",
    ]
    
    print("Embedding texts (first pass)...")
    embeddings = manager.embed_texts(texts)
    print(f"Generated {len(embeddings)} embeddings\n")
    
    print("Stats after first pass:")
    stats = manager.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    print("\n" + "="*50 + "\n")
    print("Key Takeaways:")
    print("1. Cache hit rate improves with repeated queries")
    print("2. Batching reduces number of API calls")
    print("3. Monitor token usage for cost tracking")
    print("4. Handle truncation gracefully, never fail silently")


if __name__ == "__main__":
    main()
