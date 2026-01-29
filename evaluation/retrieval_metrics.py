"""
Retrieval Evaluation Pattern

Demonstrates measuring retrieval quality with standard metrics.

Key Production Concerns:
1. Test set quality: Representative queries and ground truth
2. Multiple metrics: No single metric captures everything
3. Continuous monitoring: Track metrics over time
"""

from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class Query:
    """A test query with ground truth relevant documents."""
    query_text: str
    relevant_doc_ids: Set[str]


@dataclass
class RetrievalResult:
    """Results from a retrieval system."""
    query_text: str
    retrieved_doc_ids: List[str]  # Ordered by relevance


class RetrievalMetrics:
    """Calculate standard retrieval metrics.
    
    Production Pattern:
    - Track multiple metrics (MRR, NDCG, Precision, Recall)
    - Use ground truth test set
    - Monitor trends over time
    """
    
    @staticmethod
    def mean_reciprocal_rank(results: List[Tuple[Query, RetrievalResult]]) -> float:
        """Calculate Mean Reciprocal Rank (MRR).
        
        MRR measures the position of the first relevant result.
        Higher is better (max = 1.0).
        
        When to use: When first result matters most (e.g., Q&A).
        """
        reciprocal_ranks = []
        
        for query, result in results:
            rank = None
            for i, doc_id in enumerate(result.retrieved_doc_ids, 1):
                if doc_id in query.relevant_doc_ids:
                    rank = i
                    break
            
            if rank:
                reciprocal_ranks.append(1.0 / rank)
            else:
                reciprocal_ranks.append(0.0)
        
        return statistics.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
    
    @staticmethod
    def precision_at_k(results: List[Tuple[Query, RetrievalResult]], k: int = 5) -> float:
        """Calculate Precision@k.
        
        Precision@k = (# relevant docs in top-k) / k
        
        When to use: When accuracy of top results matters.
        """
        precisions = []
        
        for query, result in results:
            top_k = result.retrieved_doc_ids[:k]
            relevant_in_top_k = len([
                doc_id for doc_id in top_k 
                if doc_id in query.relevant_doc_ids
            ])
            precisions.append(relevant_in_top_k / k)
        
        return statistics.mean(precisions) if precisions else 0.0
    
    @staticmethod
    def recall_at_k(results: List[Tuple[Query, RetrievalResult]], k: int = 5) -> float:
        """Calculate Recall@k.
        
        Recall@k = (# relevant docs in top-k) / (# total relevant docs)
        
        When to use: When completeness matters.
        """
        recalls = []
        
        for query, result in results:
            if not query.relevant_doc_ids:
                continue
            
            top_k = result.retrieved_doc_ids[:k]
            relevant_in_top_k = len([
                doc_id for doc_id in top_k 
                if doc_id in query.relevant_doc_ids
            ])
            recalls.append(relevant_in_top_k / len(query.relevant_doc_ids))
        
        return statistics.mean(recalls) if recalls else 0.0
    
    @staticmethod
    def ndcg_at_k(
        results: List[Tuple[Query, RetrievalResult]], 
        k: int = 5,
        relevance_scores: Dict[Tuple[str, str], float] = None
    ) -> float:
        """Calculate Normalized Discounted Cumulative Gain (NDCG@k).
        
        NDCG measures ranking quality with position-based discounting.
        Higher is better (max = 1.0).
        
        When to use: When relevance is graded and ranking quality matters.
        
        Note: Simplified binary relevance version (relevant=1, not=0).
        Production: Use graded relevance scores (0-3 or 0-5).
        """
        ndcgs = []
        
        for query, result in results:
            # Calculate DCG (Discounted Cumulative Gain)
            dcg = 0.0
            for i, doc_id in enumerate(result.retrieved_doc_ids[:k], 1):
                if doc_id in query.relevant_doc_ids:
                    # Binary relevance: rel=1 if relevant, 0 otherwise
                    rel = 1.0
                    # Discount by position (log base 2)
                    dcg += rel / (i + 1)  # Simplified: should be log2(i+1)
            
            # Calculate IDCG (Ideal DCG)
            ideal_ranking = sorted(
                result.retrieved_doc_ids[:k],
                key=lambda d: 1 if d in query.relevant_doc_ids else 0,
                reverse=True
            )
            idcg = 0.0
            for i, doc_id in enumerate(ideal_ranking[:k], 1):
                if doc_id in query.relevant_doc_ids:
                    idcg += 1.0 / (i + 1)
            
            # Normalize
            if idcg > 0:
                ndcgs.append(dcg / idcg)
            else:
                ndcgs.append(0.0)
        
        return statistics.mean(ndcgs) if ndcgs else 0.0


def create_test_set() -> List[Query]:
    """Create a test set of queries with ground truth.
    
    Production Notes:
    - Use real production queries
    - Have domain experts label relevant documents
    - Cover edge cases: ambiguous, multi-intent, out-of-domain
    - Start with 50-100 queries, expand over time
    """
    return [
        Query(
            query_text="How do I reset my password?",
            relevant_doc_ids={"doc_password_reset", "doc_account_help"}
        ),
        Query(
            query_text="What are your business hours?",
            relevant_doc_ids={"doc_hours", "doc_contact"}
        ),
        Query(
            query_text="Refund policy",
            relevant_doc_ids={"doc_refunds", "doc_returns"}
        ),
        Query(
            query_text="How to contact support?",
            relevant_doc_ids={"doc_contact", "doc_support"}
        ),
    ]


def mock_retrieval_system(query: Query) -> RetrievalResult:
    """Mock retrieval system for demonstration.
    
    In production: Call your actual retrieval system.
    """
    # Simulate retrieval results
    # In reality, these would come from your vector DB, etc.
    
    all_docs = [
        "doc_password_reset", "doc_account_help", "doc_hours",
        "doc_contact", "doc_refunds", "doc_returns", "doc_support",
        "doc_faq", "doc_terms", "doc_privacy"
    ]
    
    # Simple mock: relevant docs ranked higher, but not perfect
    relevant = [d for d in all_docs if d in query.relevant_doc_ids]
    irrelevant = [d for d in all_docs if d not in query.relevant_doc_ids]
    
    # Simulate imperfect ranking: 70% of relevant docs in top half
    import random
    random.shuffle(irrelevant)
    retrieved = relevant[:2] + irrelevant[:2] + relevant[2:] + irrelevant[2:]
    
    return RetrievalResult(
        query_text=query.query_text,
        retrieved_doc_ids=retrieved[:10]
    )


def main():
    """Demonstrate retrieval evaluation pattern."""
    print("=== Retrieval Evaluation Pattern ===\n")
    
    # Create test set
    test_queries = create_test_set()
    print(f"Test set: {len(test_queries)} queries\n")
    
    # Run retrieval on test set
    results = []
    for query in test_queries:
        result = mock_retrieval_system(query)
        results.append((query, result))
    
    # Calculate metrics
    print("Metrics:")
    print(f"  MRR:          {RetrievalMetrics.mean_reciprocal_rank(results):.3f}")
    print(f"  Precision@5:  {RetrievalMetrics.precision_at_k(results, k=5):.3f}")
    print(f"  Recall@5:     {RetrievalMetrics.recall_at_k(results, k=5):.3f}")
    print(f"  NDCG@5:       {RetrievalMetrics.ndcg_at_k(results, k=5):.3f}")
    
    print("\n" + "="*50)
    print("\nKey Takeaways:")
    print("1. Track multiple metrics - no single metric tells full story")
    print("2. MRR for first result quality, NDCG for overall ranking")
    print("3. Build test set from production queries + human labeling")
    print("4. Monitor metrics over time to catch regressions")
    print("5. Update test set as system and users evolve")
    
    print("\n" + "="*50)
    print("\nProduction Checklist:")
    print("- [ ] Test set has 50-100 queries")
    print("- [ ] Ground truth validated by domain experts")
    print("- [ ] Edge cases covered (ambiguous, out-of-domain)")
    print("- [ ] Metrics tracked in time series database")
    print("- [ ] Alerts configured for regressions")
    print("- [ ] Evaluation runs automatically on deployment")


if __name__ == "__main__":
    main()
