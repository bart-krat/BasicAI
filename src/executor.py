"""
Plan Executor for Agent Framework

This module provides plan execution capabilities that coordinate between
ToolManager and StateManager to execute multi-step workflows.
"""

import asyncio
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator
import yaml

from tools import ToolManager, ToolResult, ToolResultStatus
from state import StateManager


class StepStatus(str, Enum):
    """Execution status for individual steps"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionStep(BaseModel):
    """A single step in an execution plan"""
    step: int = Field(..., description="Step number")
    tool: str = Field(..., description="Tool name to execute")
    input: Dict[str, Any] = Field(..., description="Input parameters (may contain variables)")
    output_key: str = Field(..., description="State key to store output")
    description: Optional[str] = Field(None, description="Human-readable description")
    retry_count: int = Field(default=3, ge=0, le=10, description="Max retry attempts")
    timeout: Optional[float] = Field(None, ge=1, description="Timeout in seconds")
    required: bool = Field(default=True, description="Whether step is required")
    
    @validator('output_key')
    def validate_output_key(cls, v):
        """Ensure output key is valid state key"""
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError("Output key must be valid state key")
        return v.lower()


class ExecutionPlan(BaseModel):
    """Complete execution plan with metadata"""
    task: str = Field(..., description="Task description")
    steps: List[ExecutionStep] = Field(..., description="Execution steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Plan metadata")
    
    @validator('steps')
    def validate_steps(cls, v):
        """Ensure steps are numbered sequentially"""
        if not v:
            raise ValueError("Plan must have at least one step")
        
        step_numbers = [step.step for step in v]
        expected = list(range(1, len(v) + 1))
        if step_numbers != expected:
            raise ValueError(f"Steps must be numbered 1-{len(v)}, got {step_numbers}")
        
        return v
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'ExecutionPlan':
        """Create plan from YAML string"""
        data = yaml.safe_load(yaml_str)
        return cls(**data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionPlan':
        """Create plan from dictionary"""
        return cls(**data)


class StepMetadata(BaseModel):
    """Metadata for step execution"""
    status: StepStatus = StepStatus.PENDING
    attempts: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result_status: Optional[str] = None
    execution_time: Optional[float] = None


class PlanExecutor:
    """
    Execute multi-step plans using ToolManager and StateManager
    
    Coordinates tool execution and state management for complex workflows.
    """
    
    def __init__(
        self, 
        tool_manager: ToolManager,
        state_manager: StateManager,
        auto_save: bool = True
    ):
        """
        Initialize plan executor
        
        Args:
            tool_manager: Tool manager instance
            state_manager: State manager instance
            auto_save: Whether to auto-save state after each step
        """
        self.tools = tool_manager
        self.state = state_manager
        self.auto_save = auto_save
        self._current_plan: Optional[ExecutionPlan] = None
        self._execution_log: List[Dict[str, Any]] = []
    
    async def execute_plan(
        self, 
        plan: Union[ExecutionPlan, Dict[str, Any], str],
        start_from_step: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete plan
        
        Args:
            plan: ExecutionPlan, dict, or YAML string
            start_from_step: Optional step number to resume from
            
        Returns:
            Execution summary with results
        """
        # Parse plan
        if isinstance(plan, str):
            self._current_plan = ExecutionPlan.from_yaml(plan)
        elif isinstance(plan, dict):
            self._current_plan = ExecutionPlan.from_dict(plan)
        else:
            self._current_plan = plan
        
        # Save plan to state
        await self.state.set("execution_plan", self._current_plan.dict())
        await self.state.set("execution_status", "running")
        
        print(f"🚀 Starting execution: {self._current_plan.task}")
        print(f"📋 Total steps: {len(self._current_plan.steps)}")
        
        # Determine starting step
        start_step = start_from_step or 1
        
        # Execute steps
        results = {}
        for step in self._current_plan.steps:
            if step.step < start_step:
                print(f"⏭️  Skipping step {step.step} (resuming from {start_step})")
                continue
            
            try:
                result = await self.execute_step(step)
                results[step.output_key] = result
                
                if result.status == ToolResultStatus.ERROR and step.required:
                    print(f"❌ Required step {step.step} failed, stopping execution")
                    await self.state.set("execution_status", "failed")
                    break
                    
            except Exception as e:
                print(f"❌ Fatal error in step {step.step}: {e}")
                await self.state.set("execution_status", "failed")
                await self.state.set("execution_error", str(e))
                raise
        
        # Mark completion
        await self.state.set("execution_status", "complete")
        await self.state.set("execution_completed_at", datetime.now().isoformat())
        
        summary = await self._generate_summary()
        print(f"✅ Execution complete: {summary['successful_steps']}/{summary['total_steps']} steps succeeded")
        
        return summary
    
    async def execute_step(self, step: ExecutionStep) -> ToolResult:
        """
        Execute a single step with retry logic
        
        Args:
            step: Step to execute
            
        Returns:
            ToolResult from execution
        """
        metadata = StepMetadata()
        step_key = f"step_{step.step}"
        
        print(f"\n🔧 Step {step.step}: {step.description or step.tool}")
        
        for attempt in range(step.retry_count):
            try:
                # Update metadata
                metadata.status = StepStatus.RUNNING
                metadata.attempts = attempt + 1
                metadata.started_at = datetime.now()
                await self.state.set(f"{step_key}_metadata", metadata.dict())
                
                # Resolve input variables
                resolved_input = await self._resolve_variables(step.input)
                print(f"   📥 Input: {self._format_input_preview(resolved_input)}")
                
                # Execute tool
                if step.timeout:
                    result = await asyncio.wait_for(
                        self.tools.execute_tool(step.tool, resolved_input),
                        timeout=step.timeout
                    )
                else:
                    result = await self.tools.execute_tool(step.tool, resolved_input)
                
                # Update metadata
                metadata.completed_at = datetime.now()
                metadata.execution_time = result.execution_time
                metadata.result_status = result.status.value
                
                # Check result status
                if result.status == ToolResultStatus.ERROR:
                    metadata.status = StepStatus.FAILED
                    metadata.error = result.error
                    
                    if attempt < step.retry_count - 1:
                        print(f"   ⚠️  Attempt {attempt + 1} failed: {result.error}")
                        print(f"   🔄 Retrying...")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        print(f"   ❌ Failed after {step.retry_count} attempts")
                        await self.state.set(f"{step_key}_metadata", metadata.dict())
                        return result
                
                # Success!
                metadata.status = StepStatus.COMPLETE
                print(f"   ✅ Complete in {result.execution_time:.3f}s")
                
                # Store result in state
                await self.state.set(step.output_key, result.data)
                await self.state.set(f"{step_key}_metadata", metadata.dict())
                await self.state.set(f"{step_key}_result", result.dict())
                
                # Log execution
                self._execution_log.append({
                    "step": step.step,
                    "tool": step.tool,
                    "status": "success",
                    "execution_time": result.execution_time,
                    "timestamp": datetime.now().isoformat()
                })
                
                return result
                
            except asyncio.TimeoutError:
                metadata.status = StepStatus.FAILED
                metadata.error = f"Timeout after {step.timeout}s"
                print(f"   ⏱️  Timeout after {step.timeout}s")
                
                if attempt < step.retry_count - 1:
                    print(f"   🔄 Retrying...")
                    continue
                else:
                    await self.state.set(f"{step_key}_metadata", metadata.dict())
                    return ToolResult.error(step.tool, metadata.error)
                    
            except Exception as e:
                metadata.status = StepStatus.FAILED
                metadata.error = str(e)
                print(f"   ❌ Error: {e}")
                
                if attempt < step.retry_count - 1:
                    print(f"   🔄 Retrying...")
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    await self.state.set(f"{step_key}_metadata", metadata.dict())
                    raise
        
        # Should never reach here, but just in case
        return ToolResult.error(step.tool, "Max retries exceeded")
    
    async def _resolve_variables(self, input_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve variable references in input
        
        Supports:
        - ${variable_name} - from state
        - ${step_1.output} - from previous step output
        - literal values
        
        Args:
            input_spec: Input specification with potential variables
            
        Returns:
            Resolved input dictionary
        """
        resolved = {}
        
        for key, value in input_spec.items():
            if isinstance(value, str):
                # Check for variable reference
                resolved[key] = await self._resolve_value(value)
            elif isinstance(value, dict):
                # Recursively resolve nested dicts
                resolved[key] = await self._resolve_variables(value)
            elif isinstance(value, list):
                # Resolve list items
                resolved[key] = [
                    await self._resolve_value(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                # Use literal value
                resolved[key] = value
        
        return resolved
    
    async def _resolve_value(self, value: str) -> Any:
        """Resolve a single value that might be a variable reference"""
        # Pattern: ${variable_name} or ${step_1.output}
        pattern = r'\$\{([^}]+)\}'
        match = re.search(pattern, value)
        
        if not match:
            # Not a variable, return as-is
            return value
        
        var_path = match.group(1)
        
        # Check if it's a dotted path (e.g., step_1.output)
        if '.' in var_path:
            parts = var_path.split('.')
            # Get base value from state
            base_value = await self.state.get(parts[0])
            
            # Navigate nested structure
            current = base_value
            for part in parts[1:]:
                if isinstance(current, dict):
                    current = current.get(part)
                elif hasattr(current, part):
                    current = getattr(current, part)
                else:
                    raise ValueError(f"Cannot resolve path: {var_path}")
            
            return current
        else:
            # Simple variable lookup
            result = await self.state.get(var_path)
            if result is None:
                raise ValueError(f"Variable not found in state: {var_path}")
            return result
    
    def _format_input_preview(self, input_data: Dict[str, Any], max_len: int = 50) -> str:
        """Format input for display"""
        preview = {}
        for key, value in input_data.items():
            if isinstance(value, str) and len(value) > max_len:
                preview[key] = value[:max_len] + "..."
            elif isinstance(value, (list, dict)):
                preview[key] = f"<{type(value).__name__}>"
            else:
                preview[key] = value
        return str(preview)
    
    async def _generate_summary(self) -> Dict[str, Any]:
        """Generate execution summary"""
        total_steps = len(self._current_plan.steps) if self._current_plan else 0
        successful_steps = 0
        failed_steps = 0
        
        for step in range(1, total_steps + 1):
            metadata = await self.state.get(f"step_{step}_metadata")
            if metadata and metadata.get("status") == "complete":
                successful_steps += 1
            elif metadata and metadata.get("status") == "failed":
                failed_steps += 1
        
        return {
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "execution_log": self._execution_log,
            "plan": self._current_plan.dict() if self._current_plan else None
        }
    
    async def resume_execution(self) -> Dict[str, Any]:
        """
        Resume execution from last checkpoint
        
        Returns:
            Execution summary
        """
        # Load plan from state
        plan_data = await self.state.get("execution_plan")
        if not plan_data:
            raise ValueError("No execution plan found in state")
        
        plan = ExecutionPlan.from_dict(plan_data)
        
        # Find last completed step
        last_completed = 0
        for step in plan.steps:
            metadata = await self.state.get(f"step_{step.step}_metadata")
            if metadata and metadata.get("status") == "complete":
                last_completed = step.step
            else:
                break
        
        print(f"🔄 Resuming from step {last_completed + 1}")
        return await self.execute_plan(plan, start_from_step=last_completed + 1)
    
    async def get_step_status(self, step_number: int) -> Optional[StepMetadata]:
        """Get status of a specific step"""
        metadata = await self.state.get(f"step_{step_number}_metadata")
        if metadata:
            return StepMetadata(**metadata)
        return None
    
    async def get_execution_progress(self) -> Dict[str, Any]:
        """Get current execution progress"""
        plan_data = await self.state.get("execution_plan")
        if not plan_data:
            return {"status": "no_execution"}
        
        plan = ExecutionPlan.from_dict(plan_data)
        progress = []
        
        for step in plan.steps:
            metadata = await self.state.get(f"step_{step.step}_metadata")
            progress.append({
                "step": step.step,
                "tool": step.tool,
                "description": step.description,
                "status": metadata.get("status") if metadata else "pending",
                "attempts": metadata.get("attempts") if metadata else 0
            })
        
        return {
            "task": plan.task,
            "status": await self.state.get("execution_status"),
            "progress": progress
        }


# Convenience function
def create_executor(
    tool_manager: ToolManager,
    state_manager: StateManager
) -> PlanExecutor:
    """Create a new plan executor"""
    return PlanExecutor(tool_manager, state_manager)