"""
Tool-Using Agent Pattern

Demonstrates reliable tool selection and execution with safeguards.

Key Production Concerns:
1. Safety: Iteration limits, timeouts, cost budgets
2. Reliability: Error handling, retries, fallbacks
3. Observability: Detailed logging of decisions and costs
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time


class ToolExecutionResult(Enum):
    """Result of tool execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"


@dataclass
class Tool:
    """Tool that an agent can use."""
    name: str
    description: str
    parameters: Dict[str, str]
    function: Callable
    timeout_seconds: float = 10.0
    cost_estimate: float = 0.0


@dataclass
class ToolExecution:
    """Record of a tool execution."""
    tool_name: str
    parameters: Dict[str, Any]
    result: ToolExecutionResult
    output: Any
    error_message: Optional[str]
    execution_time_ms: float
    cost_usd: float


class AgentSafetyLimits:
    """Safety limits to prevent runaway agents."""
    
    def __init__(
        self,
        max_iterations: int = 15,
        max_cost_usd: float = 0.50,
        max_total_time_seconds: float = 120.0
    ):
        self.max_iterations = max_iterations
        self.max_cost_usd = max_cost_usd
        self.max_total_time_seconds = max_total_time_seconds


class ToolUsingAgent:
    """Agent that selects and executes tools to complete tasks.
    
    Production Pattern:
    - Clear tool descriptions for reliable selection
    - Safety limits: iterations, cost, time
    - Comprehensive logging for debugging
    - Graceful error handling
    """
    
    def __init__(
        self,
        tools: List[Tool],
        safety_limits: Optional[AgentSafetyLimits] = None
    ):
        self.tools = {tool.name: tool for tool in tools}
        self.safety_limits = safety_limits or AgentSafetyLimits()
        self._execution_log: List[ToolExecution] = []
        self._total_cost = 0.0
        self._start_time = 0.0
    
    def run(self, task: str) -> Dict[str, Any]:
        """Execute task using available tools.
        
        Returns:
            Dict with final result, execution log, and metrics
        """
        print(f"=== Agent Task: {task} ===\n")
        self._start_time = time.monotonic()  # Monotonic for accurate elapsed time
        self._execution_log = []
        self._total_cost = 0.0
        
        iterations = 0
        task_complete = False
        result = None
        
        while not task_complete and iterations < self.safety_limits.max_iterations:
            iterations += 1
            print(f"\n--- Iteration {iterations} ---")
            
            # Check safety limits
            if not self._check_safety_limits(iterations):
                break
            
            # Decide next action (production: use LLM)
            action = self._decide_next_action(task, iterations)
            
            if action["type"] == "complete":
                task_complete = True
                result = action["result"]
                print(f"✓ Task complete: {result}")
                break
            
            if action["type"] == "use_tool":
                tool_name = action["tool"]
                parameters = action["parameters"]
                
                # Execute tool
                execution = self._execute_tool(tool_name, parameters)
                self._execution_log.append(execution)
                self._total_cost += execution.cost_usd
                
                print(f"  Tool: {tool_name}")
                print(f"  Result: {execution.result.value}")
                print(f"  Cost: ${execution.cost_usd:.4f}")
                
                if execution.result == ToolExecutionResult.FAILURE:
                    print(f"  Error: {execution.error_message}")
        
        elapsed = time.monotonic() - self._start_time
        
        return {
            "result": result,
            "success": task_complete,
            "iterations": iterations,
            "total_cost_usd": self._total_cost,
            "elapsed_seconds": elapsed,
            "execution_log": self._execution_log
        }
    
    def _check_safety_limits(self, iteration: int) -> bool:
        """Check if safety limits are exceeded."""
        elapsed = time.monotonic() - self._start_time
        
        if self._total_cost >= self.safety_limits.max_cost_usd:
            print(f"✗ Cost limit exceeded: ${self._total_cost:.2f}")
            return False
        
        if elapsed >= self.safety_limits.max_total_time_seconds:
            print(f"✗ Time limit exceeded: {elapsed:.1f}s")
            return False
        
        return True
    
    def _decide_next_action(self, task: str, iteration: int) -> Dict[str, Any]:
        """Decide next action based on task and context.
        
        In production: Use LLM with tool descriptions in prompt.
        This is a mock implementation for demonstration.
        """
        # Mock decision logic
        if iteration <= 2:
            return {
                "type": "use_tool",
                "tool": "search_database",
                "parameters": {"query": task}
            }
        else:
            return {
                "type": "complete",
                "result": "Task completed based on tool outputs"
            }
    
    def _execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> ToolExecution:
        """Execute a tool with timeout and error handling.
        
        Production: Implement actual timeout using:
        - concurrent.futures.ThreadPoolExecutor with timeout
        - signal.alarm() on Unix systems
        - threading.Timer for async timeout
        This example shows the pattern without actual timeout for simplicity.
        """
        if tool_name not in self.tools:
            return ToolExecution(
                tool_name=tool_name,
                parameters=parameters,
                result=ToolExecutionResult.FAILURE,
                output=None,
                error_message=f"Unknown tool: {tool_name}",
                execution_time_ms=0.0,
                cost_usd=0.0
            )
        
        tool = self.tools[tool_name]
        start_time = time.time()
        
        try:
            # Execute with timeout (production: use proper timeout mechanism)
            output = tool.function(**parameters)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolExecution(
                tool_name=tool_name,
                parameters=parameters,
                result=ToolExecutionResult.SUCCESS,
                output=output,
                error_message=None,
                execution_time_ms=execution_time,
                cost_usd=tool.cost_estimate
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            return ToolExecution(
                tool_name=tool_name,
                parameters=parameters,
                result=ToolExecutionResult.FAILURE,
                output=None,
                error_message=str(e),
                execution_time_ms=execution_time,
                cost_usd=0.0
            )


# Example tools
def search_database(query: str) -> Dict[str, Any]:
    """Search internal database."""
    time.sleep(0.1)  # Simulate latency
    return {"results": [f"Result for: {query}"], "count": 1}


def fetch_api(endpoint: str) -> Dict[str, Any]:
    """Fetch data from external API."""
    time.sleep(0.2)  # Simulate latency
    return {"data": f"Data from {endpoint}", "status": 200}


def calculate(expression: str) -> float:
    """Perform calculation.
    
    WARNING: This is a simplified example. In production, NEVER use eval().
    Use a safe math parser like ast.literal_eval() or a library like simpleeval.
    """
    # For demo purposes only - DO NOT use eval() in production
    # Production: Use safe alternatives like numexpr or simpleeval
    try:
        # Very basic safety check (still not safe!)
        if any(keyword in expression for keyword in ['import', '__', 'exec', 'eval']):
            raise ValueError("Invalid expression")
        return eval(expression)
    except Exception as e:
        raise ValueError(f"Invalid calculation: {e}")


def main():
    """Demonstrate tool-using agent pattern."""
    print("=== Tool-Using Agent Pattern ===\n")
    
    # Define tools
    tools = [
        Tool(
            name="search_database",
            description="Search internal database for information",
            parameters={"query": "search query string"},
            function=search_database,
            cost_estimate=0.001
        ),
        Tool(
            name="fetch_api",
            description="Fetch data from external API",
            parameters={"endpoint": "API endpoint path"},
            function=fetch_api,
            cost_estimate=0.002
        ),
        Tool(
            name="calculate",
            description="Perform mathematical calculation",
            parameters={"expression": "mathematical expression"},
            function=calculate,
            cost_estimate=0.0
        ),
    ]
    
    # Create agent with safety limits
    safety = AgentSafetyLimits(
        max_iterations=10,
        max_cost_usd=0.10,
        max_total_time_seconds=30.0
    )
    
    agent = ToolUsingAgent(tools, safety)
    
    # Run task
    task = "Find information about user authentication"
    result = agent.run(task)
    
    print("\n" + "="*50)
    print("\nFinal Results:")
    print(f"  Success: {result['success']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Total cost: ${result['total_cost_usd']:.4f}")
    print(f"  Elapsed time: {result['elapsed_seconds']:.2f}s")
    
    print("\n" + "="*50)
    print("\nKey Takeaways:")
    print("1. Always set hard limits: iterations, cost, time")
    print("2. Log every tool execution for debugging")
    print("3. Handle tool failures gracefully")
    print("4. Monitor costs in real-time, kill if exceeded")
    print("5. Clear tool descriptions improve selection accuracy")


if __name__ == "__main__":
    main()
