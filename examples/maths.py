"""
Math Tools Registration Example

Demonstrates registering custom tools with Pydantic validation
for basic mathematical operations.
"""

import asyncio
from typing import Optional
from pathlib import Path
import sys
from pydantic import BaseModel, Field, validator

# Import your framework components
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))


from tools import ToolManager, ToolMetadata


# ============================================================================
# PYDANTIC INPUT/OUTPUT SCHEMAS
# ============================================================================

class MathInput(BaseModel):
    """Input schema for binary math operations (add, subtract, multiply, divide)"""
    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")
    
    @validator('b')
    def validate_b_for_division(cls, v, values):
        """Note: Division by zero is checked in the function"""
        return v


class MathOutput(BaseModel):
    """Output schema for math operations"""
    operation: str = Field(..., description="Operation performed")
    a: float = Field(..., description="First operand")
    b: Optional[float] = Field(None, description="Second operand (if applicable)")
    result: Optional[float] = Field(None, description="Result of operation")
    success: bool = Field(..., description="Whether operation succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")


class PowerInput(BaseModel):
    """Input schema for power operation"""
    base: float = Field(..., description="Base number")
    exponent: float = Field(..., description="Exponent")


class RootInput(BaseModel):
    """Input schema for root operation"""
    number: float = Field(..., ge=0, description="Number to find root of (must be non-negative)")
    n: int = Field(default=2, ge=1, description="Which root (2=square root, 3=cube root, etc.)")
    
    @validator('number')
    def validate_positive_for_even_root(cls, v, values):
        """Ensure non-negative for even roots"""
        if v < 0 and 'n' in values and values['n'] % 2 == 0:
            raise ValueError("Cannot take even root of negative number")
        return v


# ============================================================================
# MATH TOOL FUNCTIONS
# ============================================================================

def add(a: float, b: float) -> MathOutput:
    """Add two numbers"""
    try:
        result = a + b
        return MathOutput(
            operation="addition",
            a=a,
            b=b,
            result=result,
            success=True
        )
    except Exception as e:
        return MathOutput(
            operation="addition",
            a=a,
            b=b,
            success=False,
            error=str(e)
        )


def subtract(a: float, b: float) -> MathOutput:
    """Subtract b from a"""
    try:
        result = a - b
        return MathOutput(
            operation="subtraction",
            a=a,
            b=b,
            result=result,
            success=True
        )
    except Exception as e:
        return MathOutput(
            operation="subtraction",
            a=a,
            b=b,
            success=False,
            error=str(e)
        )


def multiply(a: float, b: float) -> MathOutput:
    """Multiply two numbers"""
    try:
        result = a * b
        return MathOutput(
            operation="multiplication",
            a=a,
            b=b,
            result=result,
            success=True
        )
    except Exception as e:
        return MathOutput(
            operation="multiplication",
            a=a,
            b=b,
            success=False,
            error=str(e)
        )


def divide(a: float, b: float) -> MathOutput:
    """Divide a by b"""
    try:
        if b == 0:
            return MathOutput(
                operation="division",
                a=a,
                b=b,
                success=False,
                error="Division by zero"
            )
        
        result = a / b
        return MathOutput(
            operation="division",
            a=a,
            b=b,
            result=result,
            success=True
        )
    except Exception as e:
        return MathOutput(
            operation="division",
            a=a,
            b=b,
            success=False,
            error=str(e)
        )


def power(base: float, exponent: float) -> MathOutput:
    """Raise base to the power of exponent"""
    try:
        result = base ** exponent
        return MathOutput(
            operation="power",
            a=base,
            b=exponent,
            result=result,
            success=True
        )
    except Exception as e:
        return MathOutput(
            operation="power",
            a=base,
            b=exponent,
            success=False,
            error=str(e)
        )


def root(number: float, n: int = 2) -> MathOutput:
    """Calculate the nth root of a number"""
    try:
        # nth root is same as raising to power of (1/n)
        result = number ** (1/n)
        return MathOutput(
            operation=f"{n}th_root",
            a=number,
            b=float(n),
            result=result,
            success=True
        )
    except Exception as e:
        return MathOutput(
            operation=f"{n}th_root",
            a=number,
            b=float(n),
            success=False,
            error=str(e)
        )


# ============================================================================
# REGISTER TOOLS
# ============================================================================

def register_math_tools(tool_manager: ToolManager) -> None:
    """
    Register all math tools with the tool manager
    
    Args:
        tool_manager: ToolManager instance to register tools with
    """
    
    # Addition
    tool_manager.register_tool_with_pydantic(
        name="add",
        description="Add two numbers together",
        function=add,
        input_schema=MathInput,
        output_schema=MathOutput,
        category="math",
        metadata=ToolMetadata(
            version="1.0.0",
            author="BasicAI Framework",
            tags=["math", "arithmetic", "addition"],
            examples=[
                {"a": 5, "b": 3, "result": 8},
                {"a": -10, "b": 5, "result": -5}
            ]
        )
    )
    
    # Subtraction
    tool_manager.register_tool_with_pydantic(
        name="subtract",
        description="Subtract second number from first number",
        function=subtract,
        input_schema=MathInput,
        output_schema=MathOutput,
        category="math",
        metadata=ToolMetadata(
            version="1.0.0",
            author="BasicAI Framework",
            tags=["math", "arithmetic", "subtraction"],
            examples=[
                {"a": 10, "b": 3, "result": 7},
                {"a": 5, "b": 10, "result": -5}
            ]
        )
    )
    
    # Multiplication
    tool_manager.register_tool_with_pydantic(
        name="multiply",
        description="Multiply two numbers",
        function=multiply,
        input_schema=MathInput,
        output_schema=MathOutput,
        category="math",
        metadata=ToolMetadata(
            version="1.0.0",
            author="BasicAI Framework",
            tags=["math", "arithmetic", "multiplication"],
            examples=[
                {"a": 5, "b": 3, "result": 15},
                {"a": -2, "b": 4, "result": -8}
            ]
        )
    )
    
    # Division
    tool_manager.register_tool_with_pydantic(
        name="divide",
        description="Divide first number by second number",
        function=divide,
        input_schema=MathInput,
        output_schema=MathOutput,
        category="math",
        metadata=ToolMetadata(
            version="1.0.0",
            author="BasicAI Framework",
            tags=["math", "arithmetic", "division"],
            examples=[
                {"a": 10, "b": 2, "result": 5},
                {"a": 7, "b": 2, "result": 3.5}
            ]
        )
    )
    
    # Power
    tool_manager.register_tool_with_pydantic(
        name="power",
        description="Raise base to the power of exponent (base^exponent)",
        function=power,
        input_schema=PowerInput,
        output_schema=MathOutput,
        category="math",
        metadata=ToolMetadata(
            version="1.0.0",
            author="BasicAI Framework",
            tags=["math", "power", "exponent"],
            examples=[
                {"base": 2, "exponent": 3, "result": 8},
                {"base": 5, "exponent": 2, "result": 25}
            ]
        )
    )
    
    # Root
    tool_manager.register_tool_with_pydantic(
        name="root",
        description="Calculate the nth root of a number (default: square root)",
        function=root,
        input_schema=RootInput,
        output_schema=MathOutput,
        category="math",
        metadata=ToolMetadata(
            version="1.0.0",
            author="BasicAI Framework",
            tags=["math", "root", "square root"],
            examples=[
                {"number": 9, "n": 2, "result": 3},
                {"number": 27, "n": 3, "result": 3}
            ]
        )
    )
    
    print("✅ Registered 6 math tools: add, subtract, multiply, divide, power, root")


# ============================================================================
# TEST THE TOOLS
# ============================================================================

async def test_math_tools():
    """Test all registered math tools"""
    from tools import create_tool_manager
    
    # Create tool manager (without auto-discover to avoid default tools)
    tool_manager = create_tool_manager(auto_discover=False)
    
    # Register our math tools
    register_math_tools(tool_manager)
    
    print("\n" + "="*60)
    print("🧮 TESTING MATH TOOLS")
    print("="*60)
    
    # Test Addition
    print("\n1️⃣  Testing Addition (5 + 3)")
    result = await tool_manager.execute_tool("add", {"a": 5, "b": 3})
    print(f"   Status: {result.status}")
    print(f"   Result: {result.data}")
    
    # Test Subtraction
    print("\n2️⃣  Testing Subtraction (10 - 4)")
    result = await tool_manager.execute_tool("subtract", {"a": 10, "b": 4})
    print(f"   Status: {result.status}")
    print(f"   Result: {result.data}")
    
    # Test Multiplication
    print("\n3️⃣  Testing Multiplication (7 * 6)")
    result = await tool_manager.execute_tool("multiply", {"a": 7, "b": 6})
    print(f"   Status: {result.status}")
    print(f"   Result: {result.data}")
    
    # Test Division
    print("\n4️⃣  Testing Division (20 / 4)")
    result = await tool_manager.execute_tool("divide", {"a": 20, "b": 4})
    print(f"   Status: {result.status}")
    print(f"   Result: {result.data}")
    
    # Test Division by Zero
    print("\n5️⃣  Testing Division by Zero (10 / 0)")
    result = await tool_manager.execute_tool("divide", {"a": 10, "b": 0})
    print(f"   Status: {result.status}")
    print(f"   Error: {result.error or result.data.get('error')}")
    
    # Test Power
    print("\n6️⃣  Testing Power (2^8)")
    result = await tool_manager.execute_tool("power", {"base": 2, "exponent": 8})
    print(f"   Status: {result.status}")
    print(f"   Result: {result.data}")
    
    # Test Square Root
    print("\n7️⃣  Testing Square Root (√16)")
    result = await tool_manager.execute_tool("root", {"number": 16, "n": 2})
    print(f"   Status: {result.status}")
    print(f"   Result: {result.data}")
    
    # Test Cube Root
    print("\n8️⃣  Testing Cube Root (∛27)")
    result = await tool_manager.execute_tool("root", {"number": 27, "n": 3})
    print(f"   Status: {result.status}")
    print(f"   Result: {result.data}")
    
    # Test Input Validation (negative square root)
    print("\n9️⃣  Testing Invalid Input (√-4)")
    try:
        result = await tool_manager.execute_tool("root", {"number": -4, "n": 2})
        print(f"   Status: {result.status}")
        print(f"   Error: {result.error}")
    except Exception as e:
        print(f"   ❌ Validation Error (expected): {e}")
    
    # List all math tools
    print("\n" + "="*60)
    print("📋 ALL MATH TOOLS")
    print("="*60)
    math_tools = tool_manager.list_tools(category="math")
    for tool in math_tools:
        print(f"   • {tool.name}: {tool.description}")
    
    print("\n" + "="*60)
    print("✅ Math tools test complete!")
    print("="*60)
    
    return tool_manager


if __name__ == "__main__":
    asyncio.run(test_math_tools())