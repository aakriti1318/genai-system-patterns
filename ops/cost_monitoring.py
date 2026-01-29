"""
Cost Monitoring Pattern

Demonstrates tracking and alerting on GenAI system costs.

Key Production Concerns:
1. Visibility: Track costs per request, user, and component
2. Budgets: Set limits and alert before exceeding
3. Optimization: Identify cost drivers for optimization
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import statistics


class CostComponent(Enum):
    """Components that contribute to cost."""
    EMBEDDING = "embedding"
    LLM_GENERATION = "llm_generation"
    VECTOR_DB = "vector_db"
    COMPUTE = "compute"


@dataclass
class CostRecord:
    """Record of a cost-incurring operation."""
    timestamp: datetime
    user_id: str
    component: CostComponent
    amount_usd: float
    tokens_used: int = 0
    metadata: Dict = field(default_factory=dict)


class CostTracker:
    """Track costs across all system components.
    
    Production Pattern:
    - Track costs per request for granular analysis
    - Aggregate by user, component, time period
    - Alert when budgets are at risk
    """
    
    def __init__(self):
        self._records: List[CostRecord] = []
        self._user_budgets: Dict[str, float] = {}  # user_id -> daily budget
    
    def record_cost(
        self,
        user_id: str,
        component: CostComponent,
        amount_usd: float,
        tokens_used: int = 0,
        metadata: Dict = None
    ):
        """Record a cost-incurring operation.
        
        Production: Send to time series database (Prometheus, CloudWatch, etc.).
        """
        record = CostRecord(
            timestamp=datetime.now(),
            user_id=user_id,
            component=component,
            amount_usd=amount_usd,
            tokens_used=tokens_used,
            metadata=metadata or {}
        )
        self._records.append(record)
        
        # Check if user is approaching budget
        self._check_user_budget(user_id)
    
    def get_total_cost(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        component: Optional[CostComponent] = None
    ) -> float:
        """Get total cost with optional filters."""
        filtered = self._filter_records(start_time, end_time, user_id, component)
        return sum(r.amount_usd for r in filtered)
    
    def get_cost_breakdown(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Get cost breakdown by component."""
        filtered = self._filter_records(start_time, end_time)
        
        breakdown = {}
        for component in CostComponent:
            component_cost = sum(
                r.amount_usd for r in filtered 
                if r.component == component
            )
            breakdown[component.value] = component_cost
        
        return breakdown
    
    def get_top_users(
        self,
        limit: int = 10,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[tuple]:
        """Get top users by cost."""
        filtered = self._filter_records(start_time, end_time)
        
        user_costs = {}
        for record in filtered:
            user_costs[record.user_id] = \
                user_costs.get(record.user_id, 0) + record.amount_usd
        
        sorted_users = sorted(
            user_costs.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_users[:limit]
    
    def get_cost_stats(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """Get statistical summary of costs."""
        filtered = self._filter_records(start_time, end_time)
        
        if not filtered:
            return {
                "total": 0,
                "mean": 0,
                "median": 0,
                "p95": 0,
                "max": 0,
                "count": 0
            }
        
        costs = [r.amount_usd for r in filtered]
        sorted_costs = sorted(costs)
        p95_idx = int(len(sorted_costs) * 0.95)
        
        return {
            "total": sum(costs),
            "mean": statistics.mean(costs),
            "median": statistics.median(costs),
            "p95": sorted_costs[p95_idx] if p95_idx < len(sorted_costs) else sorted_costs[-1],
            "max": max(costs),
            "count": len(costs)
        }
    
    def set_user_budget(self, user_id: str, daily_budget_usd: float):
        """Set daily budget for a user."""
        self._user_budgets[user_id] = daily_budget_usd
    
    def _check_user_budget(self, user_id: str):
        """Check if user is approaching or exceeding budget."""
        if user_id not in self._user_budgets:
            return
        
        budget = self._user_budgets[user_id]
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        user_cost_today = self.get_total_cost(
            start_time=today_start,
            user_id=user_id
        )
        
        usage_percent = (user_cost_today / budget) * 100
        
        if usage_percent >= 100:
            print(f"🚨 ALERT: User {user_id} exceeded daily budget!")
            print(f"   Used: ${user_cost_today:.2f} / ${budget:.2f}")
        elif usage_percent >= 80:
            print(f"⚠️  WARNING: User {user_id} at {usage_percent:.0f}% of daily budget")
            print(f"   Used: ${user_cost_today:.2f} / ${budget:.2f}")
    
    def _filter_records(
        self,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        user_id: Optional[str] = None,
        component: Optional[CostComponent] = None
    ) -> List[CostRecord]:
        """Filter records by criteria."""
        filtered = self._records
        
        if start_time:
            filtered = [r for r in filtered if r.timestamp >= start_time]
        
        if end_time:
            filtered = [r for r in filtered if r.timestamp <= end_time]
        
        if user_id:
            filtered = [r for r in filtered if r.user_id == user_id]
        
        if component:
            filtered = [r for r in filtered if r.component == component]
        
        return filtered


def simulate_usage(tracker: CostTracker):
    """Simulate system usage for demonstration."""
    import random
    
    users = ["user_001", "user_002", "user_003", "user_004", "user_005"]
    
    # Simulate 100 operations
    for _ in range(100):
        user = random.choice(users)
        
        # Embedding cost (cheaper)
        tracker.record_cost(
            user_id=user,
            component=CostComponent.EMBEDDING,
            amount_usd=random.uniform(0.0001, 0.001),
            tokens_used=random.randint(100, 500)
        )
        
        # LLM generation cost (more expensive)
        if random.random() < 0.7:  # 70% of requests generate
            tracker.record_cost(
                user_id=user,
                component=CostComponent.LLM_GENERATION,
                amount_usd=random.uniform(0.01, 0.05),
                tokens_used=random.randint(500, 2000)
            )
        
        # Vector DB cost (small, per-operation)
        tracker.record_cost(
            user_id=user,
            component=CostComponent.VECTOR_DB,
            amount_usd=0.0001
        )


def main():
    """Demonstrate cost monitoring pattern."""
    print("=== Cost Monitoring Pattern ===\n")
    
    tracker = CostTracker()
    
    # Set user budgets
    tracker.set_user_budget("user_001", 1.00)  # $1/day
    tracker.set_user_budget("user_002", 0.50)  # $0.50/day
    
    # Simulate usage
    print("Simulating system usage...\n")
    simulate_usage(tracker)
    
    # Get total cost
    total = tracker.get_total_cost()
    print(f"Total cost: ${total:.4f}")
    
    # Cost breakdown
    print("\nCost breakdown by component:")
    breakdown = tracker.get_cost_breakdown()
    for component, cost in breakdown.items():
        percentage = (cost / total * 100) if total > 0 else 0
        print(f"  {component:20s}: ${cost:.4f} ({percentage:.1f}%)")
    
    # Top users
    print("\nTop users by cost:")
    top_users = tracker.get_top_users(limit=5)
    for user_id, cost in top_users:
        print(f"  {user_id}: ${cost:.4f}")
    
    # Cost statistics
    print("\nCost statistics per operation:")
    stats = tracker.get_cost_stats()
    print(f"  Mean:   ${stats['mean']:.4f}")
    print(f"  Median: ${stats['median']:.4f}")
    print(f"  P95:    ${stats['p95']:.4f}")
    print(f"  Max:    ${stats['max']:.4f}")
    print(f"  Count:  {stats['count']}")
    
    print("\n" + "="*50)
    print("\nKey Takeaways:")
    print("1. Track costs per request for granular analysis")
    print("2. Monitor costs by user to detect abuse")
    print("3. Break down costs by component to find optimization targets")
    print("4. Set budgets and alert before exceeding")
    print("5. Track trends over time to project future costs")
    
    print("\n" + "="*50)
    print("\nProduction Metrics to Track:")
    print("- Cost per request (mean, median, p95)")
    print("- Cost per user (daily, monthly)")
    print("- Cost breakdown by component")
    print("- Projected monthly cost")
    print("- Cost anomalies (sudden spikes)")


if __name__ == "__main__":
    main()
