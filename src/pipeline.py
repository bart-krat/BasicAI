"""
Pipeline for Simple Workflows

This module provides a simple pipeline class for executing tasks step-by-step
with state management and tool integration.
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from state import StateManager
from tools import ToolManager
from agent import Agent

@dataclass
class PipelineStep:
    """A single step in the pipeline"""
    step_number: int
    name: str
    description: str
    input_keys: List[str]
    output_keys: List[str]
    function: Optional[Callable] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'step_number': self.step_number,
            'name': self.name,
            'description': self.description,
            'input_keys': self.input_keys,
            'output_keys': self.output_keys,
            'function': self.function.__name__ if self.function else None
        }

class Pipeline:
    """
    Simple pipeline for executing workflows step-by-step
    
    Provides:
    - Step-by-step execution
    - State management
    - Tool integration
    - Error handling
    - Progress tracking
    """
    
    def __init__(self, 
                 name: str,
                 state_manager: Optional[StateManager] = None,
                 tool_manager: Optional[ToolManager] = None,
                 agent: Optional[Agent] = None):
        """
        Initialize pipeline
        
        Args:
            name: Pipeline name
            state_manager: Optional state manager for persistence
            tool_manager: Optional tool manager for function calling
            agent: Optional agent for LLM interactions
        """
        self.name = name
        self.state = state_manager
        self.tools = tool_manager
        self.agent = agent
        
        # Pipeline steps
        self.steps: List[PipelineStep] = []
        self.current_step_index = 0
        self.execution_log: List[Dict[str, Any]] = []
        
        # Initialize pipeline state
        if self.state:
            self.state.set("pipeline_name", name)
            self.state.set("pipeline_status", "initialized")
    
    def add_step(self, 
                 step_number: int,
                 name: str,
                 description: str,
                 input_keys: Optional[List[str]] = None,
                 output_keys: Optional[List[str]] = None,
                 function: Optional[Callable] = None) -> 'Pipeline':
        """
        Add a step to the pipeline
        
        Args:
            step_number: Order of execution
            name: Step name
            description: Step description
            input_keys: List of state keys this step needs as input
            output_keys: List of state keys this step will produce as output
            function: Function to execute
            
        Returns:
            Pipeline instance for chaining
        """
        step = PipelineStep(
            step_number=step_number,
            name=name,
            description=description,
            input_keys=input_keys or [],
            output_keys=output_keys or [],
            function=function
        )
        
        self.steps.append(step)
        # Sort steps by step_number to ensure correct order
        self.steps.sort(key=lambda s: s.step_number)
        return self
    
    async def execute_step(self, step_index: int) -> Dict[str, Any]:
        """Execute a specific step with proper state management"""
        if step_index >= len(self.steps):
            raise ValueError(f"Step index {step_index} out of range")
        
        step = self.steps[step_index]
        start_time = datetime.now()
        
        try:
            # 1. Check input state (using input_keys)
            if step.input_keys and self.state:
                missing_inputs = []
                for key in step.input_keys:
                    if not await self.state.has(key):
                        missing_inputs.append(key)
                
                if missing_inputs:
                    raise ValueError(f"Missing required inputs: {missing_inputs}")
            
            # 2. Get input data from state
            input_data = {}
            if step.input_keys and self.state:
                for key in step.input_keys:
                    input_data[key] = await self.state.get(key)
            
            # 3. Execute step with input data
            result = None
            if step.function:
                if asyncio.iscoroutinefunction(step.function):
                    result = await step.function(**input_data)  # Pass input data
                else:
                    result = step.function(**input_data)  # Pass input data
            else:
                raise ValueError(f"No function provided for step: {step.name}")
            
            # 4. Store outputs in state (using output_keys)
            if step.output_keys and self.state:
                if isinstance(result, dict):
                    # If result is dict, store each output key
                    for key in step.output_keys:
                        if key in result:
                            await self.state.set(key, result[key])
                else:
                    # If result is single value, store in first output key
                    await self.state.set(step.output_keys[0], result)
            
            # 5. Log execution
            execution_log = {
                'step_name': step.name,
                'step_index': step_index,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration': (datetime.now() - start_time).total_seconds(),
                'status': 'success',
                'result': result
            }
            
            self.execution_log.append(execution_log)
            
            # 6. Update pipeline state
            if self.state:
                await self.state.set("current_step", step.name)
                await self.state.set("current_step_index", step_index)
                await self.state.set("pipeline_status", "running")
            
            return execution_log
            
        except Exception as e:
            # Log error
            execution_log = {
                'step_name': step.name,
                'step_index': step_index,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration': (datetime.now() - start_time).total_seconds(),
                'status': 'error',
                'error': str(e)
            }
            
            self.execution_log.append(execution_log)
            
            # Update pipeline state
            if self.state:
                await self.state.set("pipeline_status", "error")
                await self.state.set("last_error", str(e))
            
            raise e
    
    async def execute_all(self) -> List[Dict[str, Any]]:
        """
        Execute all steps in the pipeline
        
        Returns:
            List of execution results
        """
        results = []
        
        for i, step in enumerate(self.steps):
            try:
                result = await self.execute_step(i)
                results.append(result)
                
                # Check if we should stop
                if result['status'] == 'error':
                    break
                    
            except Exception as e:
                print(f"Pipeline stopped at step {i} due to error: {e}")
                break
        
        # Update final status
        if self.state:
            if all(r['status'] == 'success' for r in results):
                await self.state.set("pipeline_status", "completed")
            else:
                await self.state.set("pipeline_status", "failed")
        
        return results
    
    async def execute_from_step(self, start_index: int) -> List[Dict[str, Any]]:
        """
        Execute pipeline from a specific step
        
        Args:
            start_index: Index to start execution from
            
        Returns:
            List of execution results
        """
        results = []
        
        for i in range(start_index, len(self.steps)):
            try:
                result = await self.execute_step(i)
                results.append(result)
                
                if result['status'] == 'error':
                    break
                    
            except Exception as e:
                print(f"Pipeline stopped at step {i} due to error: {e}")
                break
        
        return results
    
    def get_step(self, step_index: int) -> Optional[PipelineStep]:
        """Get a specific step by index"""
        if 0 <= step_index < len(self.steps):
            return self.steps[step_index]
        return None
    
    def get_current_step(self) -> Optional[PipelineStep]:
        """Get current step"""
        return self.get_step(self.current_step_index)
    
    def get_next_step(self) -> Optional[PipelineStep]:
        """Get next step"""
        return self.get_step(self.current_step_index + 1)
    
    def get_previous_step(self) -> Optional[PipelineStep]:
        """Get previous step"""
        return self.get_step(self.current_step_index - 1)
    
    def list_steps(self) -> List[Dict[str, Any]]:
        """Get list of all steps"""
        return [step.to_dict() for step in self.steps]
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get execution log"""
        return self.execution_log
    
    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
        return {
            'name': self.name,
            'total_steps': len(self.steps),
            'current_step_index': self.current_step_index,
            'execution_log_count': len(self.execution_log),
            'has_state_manager': self.state is not None,
            'has_tool_manager': self.tools is not None,
            'has_agent': self.agent is not None
        }
    
    async def reset(self) -> None:
        """Reset pipeline to initial state"""
        self.current_step_index = 0
        self.execution_log = []
        
        if self.state:
            await self.state.set("pipeline_status", "initialized")
            await self.state.set("current_step", None)
            await self.state.set("current_step_index", 0)

# Convenience functions
def create_pipeline(name: str, 
                   state_manager: Optional[StateManager] = None,
                   tool_manager: Optional[ToolManager] = None,
                   agent: Optional[Agent] = None) -> Pipeline:
    """Create a new pipeline instance"""
    return Pipeline(name, state_manager, tool_manager, agent)