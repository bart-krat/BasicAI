"""
Manual Math Executor

Demonstrates the Executor running a manually-defined YAML plan
to solve a complex math problem by chaining tools.

Problem: ((10 + 5) * 3) / (2^2) - √16
Expected Answer: 7.25

This shows:
1. How to define a YAML execution plan
2. How the Executor chains tools together
3. How State tracks intermediate results
4. Variable resolution (${step_X_result.result})
"""

import asyncio
from pathlib import Path
import sys

# Setup path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'examples'))

from maths import register_math_tools
from tools import create_tool_manager
from state import create_state_manager
from executor import create_executor


def extract_result_value(result_data):
    """Helper to extract numeric result from nested data structures"""
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


async def main():
    """Execute a manually-defined math problem solving plan"""
    
    print("="*70)
    print("🧮 MANUAL MATH EXECUTOR")
    print("="*70)
    print("\nProblem: ((10 + 5) * 3) / (2^2) - √16")
    print("Expected: 7.25")
    print("="*70)
    
    # ========================================================================
    # STEP 1: Setup Components
    # ========================================================================
    print("\n📦 Setting up components...")
    
    # Create tool manager and register math tools
    tool_manager = create_tool_manager(auto_discover=False)
    register_math_tools(tool_manager)
    print(f"✅ Registered {len(tool_manager.tools)} math tools")
    
    # Create state manager
    state = create_state_manager(session_id="manual_math_solver")
    print("✅ State manager ready")
    
    # Create executor
    executor = create_executor(tool_manager, state)
    print("✅ Executor ready")
    
    # ========================================================================
    # STEP 2: Define the Execution Plan
    # ========================================================================
    print("\n📋 Execution Plan:")
    print("-" * 70)
    
    plan_yaml = """
task: "Calculate ((10 + 5) * 3) / (2^2) - √16"
steps:
  - step: 1
    tool: "add"
    input:
      a: 10
      b: 5
    output_key: "step_1_result"
    description: "Add 10 + 5 = 15"
    
  - step: 2
    tool: "multiply"
    input:
      a: "${step_1_result.result}"
      b: 3
    output_key: "step_2_result"
    description: "Multiply 15 * 3 = 45"
    
  - step: 3
    tool: "power"
    input:
      base: 2
      exponent: 2
    output_key: "step_3_result"
    description: "Calculate 2^2 = 4"
    
  - step: 4
    tool: "divide"
    input:
      a: "${step_2_result.result}"
      b: "${step_3_result.result}"
    output_key: "step_4_result"
    description: "Divide 45 / 4 = 11.25"
    
  - step: 5
    tool: "root"
    input:
      number: 16
      n: 2
    output_key: "step_5_result"
    description: "Calculate √16 = 4"
    
  - step: 6
    tool: "subtract"
    input:
      a: "${step_4_result.result}"
      b: "${step_5_result.result}"
    output_key: "step_6_result"
    description: "Subtract 11.25 - 4 = 7.25"
"""
    
    print(plan_yaml)
    print("-" * 70)
    
    # ========================================================================
    # STEP 3: Execute the Plan
    # ========================================================================
    print("\n⚙️  Executing plan step-by-step...")
    print("="*70)
    
    summary = await executor.execute_plan(plan_yaml)
    
    # ========================================================================
    # STEP 4: Display Results
    # ========================================================================
    print("\n" + "="*70)
    print("📊 EXECUTION SUMMARY")
    print("="*70)
    print(f"Total Steps: {summary['total_steps']}")
    print(f"Successful: {summary['successful_steps']}")
    print(f"Failed: {summary['failed_steps']}")
    
    print("\n🎯 Step-by-Step Results:")
    print("-" * 70)
    
    # Show each step's result
    step_descriptions = [
        "10 + 5",
        "15 * 3",
        "2^2",
        "45 / 4",
        "√16",
        "11.25 - 4"
    ]
    
    for step_num in range(1, summary['total_steps'] + 1):
        step_result = await state.get(f"step_{step_num}_result")
        if step_result:
            value = extract_result_value(step_result)
            desc = step_descriptions[step_num - 1] if step_num <= len(step_descriptions) else "N/A"
            print(f"Step {step_num} ({desc}): {value}")
    
    # ========================================================================
    # STEP 5: Final Answer
    # ========================================================================
    final_result = await state.get("step_6_result")
    
    if final_result:
        final_answer = extract_result_value(final_result)
        
        print("-" * 70)
        print(f"\n✨ FINAL ANSWER: {final_answer}")
        print(f"\n   Expected: 7.25")
        print(f"   Got:      {final_answer}")
        
        # Check if answer is correct (with floating point tolerance)
        is_correct = abs(float(final_answer) - 7.25) < 0.01
        print(f"   Match:    {'✅ CORRECT!' if is_correct else '❌ INCORRECT'}")
        
        if is_correct:
            print("\n🎉 SUCCESS! The executor correctly chained all math tools!")
    else:
        print("\n❌ No final result found")
    
    # ========================================================================
    # STEP 6: Show State Context
    # ========================================================================
    print("\n" + "="*70)
    print("💾 STATE CONTEXT (What the State Manager Tracked)")
    print("="*70)
    
    context = await state.get_context(max_entries=20)
    print(context)
    
    # ========================================================================
    # STEP 7: Show Execution Log
    # ========================================================================
    print("\n" + "="*70)
    print("📝 EXECUTION LOG")
    print("="*70)
    
    for i, log_entry in enumerate(summary.get('execution_log', []), 1):
        print(f"{i}. Tool: {log_entry['tool']}, "
              f"Status: {log_entry['status']}, "
              f"Time: {log_entry['execution_time']:.4f}s")
    
    print("\n" + "="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)
    
    print("\n📚 What This Demonstrated:")
    print("  1. ✅ YAML plan definition")
    print("  2. ✅ Variable resolution (${step_X_result.result})")
    print("  3. ✅ Tool chaining (output of step 1 → input of step 2)")
    print("  4. ✅ State persistence (all results tracked)")
    print("  5. ✅ Pydantic validation (inputs/outputs validated)")
    print("  6. ✅ Error handling (retry logic, graceful failures)")
    print("\n🎯 Next step: Use an Agent to generate this plan automatically!")


if __name__ == "__main__":
    asyncio.run(main())

