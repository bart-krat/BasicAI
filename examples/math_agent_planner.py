"""
Math Agent Planner Example

Demonstrates:
1. Agent receives a complex math problem
2. Agent generates a YAML plan to solve it step-by-step
3. Executor chains math tools together using the plan
4. State tracks intermediate results
"""

import asyncio
import logging
from pathlib import Path
import sys

# Setup path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from agent import create_openai_agent
from state import create_state_manager, StateSchema
from executor import create_executor, ExecutionPlan
from tools import create_tool_manager
from parser import YAMLParser
import yaml

# Import math tools registration from examples
sys.path.insert(0, str(project_root / 'examples'))
from maths import register_math_tools

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def extract_result_value(result_data):
    """
    Helper to extract numeric result from nested data structures
    
    Handles:
    - ToolResult objects
    - Pydantic models
    - Dicts
    - Plain values
    """
    # Handle ToolResult
    if hasattr(result_data, 'data'):
        result_data = result_data.data
    elif isinstance(result_data, dict) and 'data' in result_data:
        result_data = result_data['data']
    
    # Handle Pydantic models
    if hasattr(result_data, 'result'):
        return result_data.result
    elif isinstance(result_data, dict) and 'result' in result_data:
        return result_data['result']
    
    # Plain value
    return result_data


async def solve_math_problem_with_agent():
    """
    Solve a complex math problem using Agent + Executor + Tools
    
    Problem: Calculate ((10 + 5) * 3) / (2^2) - √16
    
    Step breakdown:
    1. Add: 10 + 5 = 15
    2. Multiply: 15 * 3 = 45
    3. Power: 2^2 = 4
    4. Divide: 45 / 4 = 11.25
    5. Root: √16 = 4
    6. Subtract: 11.25 - 4 = 7.25
    
    Expected answer: 7.25
    """
    
    print("="*70)
    print("🧮 MATH AGENT PLANNER - Complex Problem Solver")
    print("="*70)
    
    # ========================================================================
    # STEP 1: Setup Components
    # ========================================================================
    print("\n📦 Setting up components...")
    
    # Create tool manager and register math tools
    tool_manager = create_tool_manager(auto_discover=False)
    register_math_tools(tool_manager)
    
    # Create state manager with schema
    state_schema = StateSchema(
        required_keys=["problem", "plan"],
        key_types={
            "problem": {"type": "string"},
            "plan": {"type": "object"},
            "step_1_result": {"type": "object"},
            "step_2_result": {"type": "object"},
            "step_3_result": {"type": "object"},
            "step_4_result": {"type": "object"},
            "step_5_result": {"type": "object"},
            "step_6_result": {"type": "object"},
            "final_answer": {"type": "number"}
        }
    )
    state = create_state_manager(
        session_id="math_problem_solver",
        state_schema=state_schema
    )
    
    # Create agent (for plan generation)
    agent = create_openai_agent(
        model="gpt-4o-mini",
        state_manager=state,
        tool_manager=tool_manager
    )
    
    # Create executor (for plan execution)
    executor = create_executor(tool_manager, state)
    
    print("✅ Components ready!")
    
    # ========================================================================
    # STEP 2: Define the Problem
    # ========================================================================
    problem = "Calculate: ((10 + 5) * 3) / (2^2) - √16"
    print(f"\n📝 Problem: {problem}")
    
    # Set problem in state
    problem_set = await state.set("problem", problem)
    if not problem_set:
        print("⚠️  Warning: Failed to set 'problem' in state (validation may have failed)")
    else:
        print("✅ Successfully set 'problem' in state")
    
    # Verify it was saved
    saved_problem = await state.get("problem")
    print(f"🔍 Verified 'problem' in state: {saved_problem is not None}")
    
    # ========================================================================
    # STEP 3: Agent Generates Execution Plan
    # ========================================================================
    print("\n🤖 Agent analyzing problem and generating plan...")
    
    planning_prompt = f"""
You are a math problem solver. Break down this problem into steps using the available math tools.

Problem: {problem}

Available tools:
- add(a, b): Add two numbers
- subtract(a, b): Subtract b from a
- multiply(a, b): Multiply two numbers
- divide(a, b): Divide a by b
- power(base, exponent): Calculate base^exponent
- root(number, n): Calculate nth root

Generate a YAML execution plan that solves this step-by-step.
Each step should:
1. Use ONE tool
2. Reference previous results using ${{step_N_result.result}} notation
3. Store output in step_N_result

IMPORTANT: 
- Use ONLY the exact tool names listed above
- For power operation, use input keys: base, exponent
- For root operation, use input keys: number, n
- For other operations, use input keys: a, b
- Reference previous step results as: ${{step_1_result.result}}

Example format:
```yaml
task: "Solve the math problem"
steps:
  - step: 1
    tool: "add"
    input:
      a: 10
      b: 5
    output_key: "step_1_result"
    description: "Add 10 + 5"
    
  - step: 2
    tool: "multiply"
    input:
      a: "${{step_1_result.result}}"
      b: 3
    output_key: "step_2_result"
    description: "Multiply result by 3"
```

Now generate the complete plan for: {problem}

Return ONLY the YAML, no other text.
"""
    
    # Get plan from agent (raw LLM output, may contain markdown fences)
    raw_plan = await agent.generate(
        prompt=planning_prompt,
        temperature=0.3,  # Lower temperature for more deterministic planning
        use_state=False,
        use_tools=False
    )
    
    print("\n📋 Generated Plan (raw from LLM):")
    print("-" * 70)
    print(raw_plan)
    print("-" * 70)
    
    # Parse and clean YAML from LLM output (handles markdown fences, errors, etc.)
    print("\n🔧 Parsing and cleaning YAML plan...")
    yaml_parser = YAMLParser(safe_load=True, auto_fix=True)
    parse_result = yaml_parser.parse(raw_plan)
    
    if not parse_result.success:
        print(f"❌ Failed to parse YAML plan: {parse_result.error}")
        raise ValueError(f"YAML parsing failed: {parse_result.error}")
    
    if parse_result.warnings:
        print(f"⚠️  YAML parsing warnings: {parse_result.warnings}")
    
    # Convert parsed dict back to clean YAML string (no markdown fences)
    clean_yaml = yaml.dump(parse_result.data, default_flow_style=False)
    
    # Verify the clean YAML can be parsed by executor
    try:
        test_plan = ExecutionPlan.from_yaml(clean_yaml)
        print(f"\n✅ Clean YAML verified: Can be parsed by ExecutionPlan")
        print(f"   - Task: {test_plan.task}")
        print(f"   - Steps: {len(test_plan.steps)}")
    except Exception as e:
        print(f"\n❌ Clean YAML verification failed: {e}")
        raise ValueError(f"Clean YAML cannot be parsed by ExecutionPlan: {e}")
    
    print("\n✅ Clean YAML plan ready:")
    print("-" * 70)
    print(clean_yaml)
    print("-" * 70)
    
    # Save clean YAML to state (use "plan" to match schema requirement)
    print("\n💾 Saving plan to state...")
    plan_set = await state.set("plan", parse_result.data)  # Store as dict for easier access
    
    if not plan_set:
        print("❌ Failed to set 'plan' in state (validation may have failed)")
        raise ValueError("Failed to save plan to state")
    else:
        print("✅ Successfully set 'plan' in state")
    
    # Verify both required keys are now in state
    print("\n🔍 Verifying state keys:")
    saved_problem = await state.get("problem")
    saved_plan = await state.get("plan")
    
    print(f"  - 'problem' in state: {saved_problem is not None} (value: {type(saved_problem).__name__})")
    print(f"  - 'plan' in state: {saved_plan is not None} (value: {type(saved_plan).__name__})")
    
    if saved_plan:
        print(f"  - Plan structure: task='{saved_plan.get('task', 'N/A')}', steps={len(saved_plan.get('steps', []))}")
    
    # Verify the plan structure matches ExecutionPlan expectations
    if saved_plan:
        required_plan_keys = ["task", "steps"]
        missing_keys = [key for key in required_plan_keys if key not in saved_plan]
        if missing_keys:
            print(f"⚠️  Warning: Plan missing required keys: {missing_keys}")
        else:
            print("✅ Plan structure is valid (has 'task' and 'steps')")
    
    # Final validation: Check if state schema is satisfied
    if state.state_schema:
        all_state = await state.get_all()
        final_validation = state.state_schema.validate_state(all_state)
        if final_validation['valid']:
            print("\n✅ Final state validation: PASSED (all required keys present)")
        else:
            print(f"\n⚠️  Final state validation: {final_validation['errors']}")
            if final_validation['warnings']:
                print(f"   Warnings: {final_validation['warnings']}")
    
    # ========================================================================
    # STEP 4: Execute the Plan
    # ========================================================================
    print("\n⚙️  Executing plan with Executor...")
    print("="*70)
    
    try:
        # Execute the plan (executor receives clean YAML, ready for execution)
        summary = await executor.execute_plan(clean_yaml)
        
        print("\n" + "="*70)
        print("📊 Execution Summary")
        print("="*70)
        print(f"Total Steps: {summary['total_steps']}")
        print(f"Successful: {summary['successful_steps']}")
        print(f"Failed: {summary['failed_steps']}")
        
        # ========================================================================
        # STEP 5: Extract Final Answer
        # ========================================================================
        print("\n🎯 Results:")
        print("-" * 70)
        
        # Get all step results
        for step_num in range(1, summary['total_steps'] + 1):
            step_result = await state.get(f"step_{step_num}_result")
            if step_result:
                # Extract the actual numeric result
                value = extract_result_value(step_result)
                print(f"Step {step_num}: {value}")
        
        # Get the last step's result as final answer
        last_step = summary['total_steps']
        final_result = await state.get(f"step_{last_step}_result")
        
        if final_result:
            final_answer = extract_result_value(final_result)
            await state.set("final_answer", final_answer)
            
            print("-" * 70)
            print(f"\n✨ Final Answer: {final_answer}")
            print(f"\n✅ Expected: 7.25")
            print(f"   Got: {final_answer}")
            print(f"   Match: {'✅ YES' if abs(float(final_answer) - 7.25) < 0.01 else '❌ NO'}")
        
        # ========================================================================
        # STEP 6: Show State Context
        # ========================================================================
        print("\n" + "="*70)
        print("💾 State Context (for LLM)")
        print("="*70)
        context = await state.get_context(max_entries=10)
        print(context)
        
        return final_answer
        
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def solve_with_manual_plan():
    """
    Alternative: Use a manually defined plan (for comparison)
    
    This shows what the agent SHOULD generate
    """
    print("\n" + "="*70)
    print("🔧 Alternative: Manual Plan Execution")
    print("="*70)
    
    # Setup
    tool_manager = create_tool_manager(auto_discover=False)
    register_math_tools(tool_manager)
    state = create_state_manager(session_id="manual_solver")
    executor = create_executor(tool_manager, state)
    
    # Manual YAML plan
    manual_plan = """
task: "Calculate ((10 + 5) * 3) / (2^2) - √16"
steps:
  - step: 1
    tool: "add"
    input:
      a: 10
      b: 5
    output_key: "step_1_result"
    description: "Add 10 + 5"
    
  - step: 2
    tool: "multiply"
    input:
      a: "${step_1_result.result}"
      b: 3
    output_key: "step_2_result"
    description: "Multiply result by 3"
    
  - step: 3
    tool: "power"
    input:
      base: 2
      exponent: 2
    output_key: "step_3_result"
    description: "Calculate 2^2"
    
  - step: 4
    tool: "divide"
    input:
      a: "${step_2_result.result}"
      b: "${step_3_result.result}"
    output_key: "step_4_result"
    description: "Divide result by 4"
    
  - step: 5
    tool: "root"
    input:
      number: 16
      n: 2
    output_key: "step_5_result"
    description: "Calculate square root of 16"
    
  - step: 6
    tool: "subtract"
    input:
      a: "${step_4_result.result}"
      b: "${step_5_result.result}"
    output_key: "step_6_result"
    description: "Subtract sqrt(16) from result"
"""
    
    print("\n📋 Manual Plan:")
    print(manual_plan)
    
    print("\n⚙️  Executing...")
    summary = await executor.execute_plan(manual_plan)
    
    # Get final answer
    final_result = await state.get("step_6_result")
    if final_result:
        final_answer = extract_result_value(final_result)
        
        print(f"\n✨ Manual Plan Result: {final_answer}")
        print(f"   Expected: 7.25")
        print(f"   Match: {'✅ YES' if abs(float(final_answer) - 7.25) < 0.01 else '❌ NO'}")


async def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🚀 MATH AGENT PLANNER DEMO")
    print("="*70)
    print("\nThis demo shows:")
    print("1. Agent receives complex math problem")
    print("2. Agent generates YAML execution plan")
    print("3. Executor chains math tools together")
    print("4. State tracks all intermediate results")
    print("="*70)
    
    # Run agent-based solution
    await solve_math_problem_with_agent()
    
    # Run manual plan for comparison
    


if __name__ == "__main__":
    asyncio.run(main())

