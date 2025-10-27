"""
Tool Management for Agent Framework

This module provides tool management for agents to register, discover,
and execute various tools and functions with comprehensive Pydantic validation.
"""

import asyncio
import inspect
import json
import time
from typing import Any, Dict, List, Optional, Callable, Union, Type, Generic, TypeVar
from datetime import datetime
import hashlib

# Required Pydantic imports
from pydantic import BaseModel, Field, validator, ValidationError
from enum import Enum

# Type variables for generic tool schemas
TInput = TypeVar('TInput', bound=BaseModel)
TOutput = TypeVar('TOutput', bound=BaseModel)

class ToolResultStatus(str, Enum):
    """Tool execution status"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    WARNING = "warning"

class ToolResult(BaseModel):
    """Standardized tool execution result with Pydantic validation"""
    tool_name: str = Field(..., description="Name of the executed tool")
    status: ToolResultStatus = Field(..., description="Execution status")
    data: Optional[Any] = Field(None, description="Tool output data")
    error: Optional[str] = Field(None, description="Error message if failed")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Execution timestamp")
    
    @validator('data')
    def validate_data(cls, v, values):
        """Validate data based on status"""
        status = values.get('status')
        if status == ToolResultStatus.SUCCESS and v is None:
            raise ValueError("Data cannot be None for successful execution")
        if status == ToolResultStatus.ERROR and v is not None:
            raise ValueError("Data should be None for error status")
        return v
    
    @validator('error')
    def validate_error(cls, v, values):
        """Validate error field"""
        status = values.get('status')
        if status == ToolResultStatus.ERROR and not v:
            raise ValueError("Error message required for error status")
        if status == ToolResultStatus.SUCCESS and v:
            raise ValueError("Error message should be None for success status")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        validate_assignment = True
    
    @classmethod
    def success(cls, tool_name: str, data: Any, **kwargs) -> 'ToolResult':
        """Create successful result"""
        return cls(
            tool_name=tool_name,
            status=ToolResultStatus.SUCCESS,
            data=data,
            **kwargs
        )
    
    @classmethod
    def error(cls, tool_name: str, error: str, **kwargs) -> 'ToolResult':
        """Create error result"""
        return cls(
            tool_name=tool_name,
            status=ToolResultStatus.ERROR,
            error=error,
            **kwargs
        )
    
    @classmethod
    def partial(cls, tool_name: str, data: Any, warnings: List[str], **kwargs) -> 'ToolResult':
        """Create partial success result"""
        return cls(
            tool_name=tool_name,
            status=ToolResultStatus.PARTIAL,
            data=data,
            warnings=warnings,
            **kwargs
        )

class ToolMetadata(BaseModel):
    """Tool metadata with validation"""
    version: Optional[str] = Field(None, description="Tool version")
    author: Optional[str] = Field(None, description="Tool author")
    tags: List[str] = Field(default_factory=list, description="Tool tags")
    documentation: Optional[str] = Field(None, description="Tool documentation URL")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate and clean tags"""
        return [tag.strip().lower() for tag in v if tag.strip()]

class Tool(BaseModel):
    """A tool definition with comprehensive Pydantic validation"""
    name: str = Field(..., min_length=1, max_length=100, description="Tool name")
    description: str = Field(..., min_length=1, max_length=500, description="Tool description")
    function: Callable = Field(..., description="Function to execute")
    input_schema: Optional[Type[BaseModel]] = Field(None, description="Pydantic model for input validation")
    output_schema: Optional[Type[BaseModel]] = Field(None, description="Pydantic model for output validation")
    category: Optional[str] = Field(None, max_length=50, description="Tool category")
    metadata: ToolMetadata = Field(default_factory=ToolMetadata, description="Tool metadata")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate tool name"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Tool name must contain only alphanumeric characters, underscores, and hyphens")
        return v.lower()
    
    @validator('category')
    def validate_category(cls, v):
        """Validate category"""
        if v:
            return v.lower().strip()
        return v
    
    class Config:
        arbitrary_types_allowed = True  # Allow Callable type
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'metadata': self.metadata.dict()
        }
        
        # Add Pydantic schemas
        if self.input_schema:
            result['input_schema'] = self.input_schema.schema()
        if self.output_schema:
            result['output_schema'] = self.output_schema.schema()
            
        return result
    
    def has_validation(self) -> bool:
        """Check if tool has validation enabled"""
        return self.input_schema is not None or self.output_schema is not None

# Default tool input/output schemas
class CalculatorInput(BaseModel):
    """Calculator tool input"""
    expression: str = Field(..., min_length=1, description="Mathematical expression to evaluate")
    
    @validator('expression')
    def validate_expression(cls, v):
        """Validate mathematical expression"""
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in v):
            raise ValueError("Expression contains invalid characters")
        return v.strip()

class CalculatorOutput(BaseModel):
    """Calculator tool output"""
    expression: str = Field(..., description="Original expression")
    result: Optional[float] = Field(None, description="Calculation result")
    success: bool = Field(..., description="Whether calculation succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")

class TextProcessorInput(BaseModel):
    """Text processor tool input"""
    text: str = Field(..., min_length=1, description="Text to process")
    operation: str = Field(..., description="Operation to perform")
    
    @validator('operation')
    def validate_operation(cls, v):
        """Validate operation type"""
        allowed_ops = ["count_words", "count_chars", "uppercase", "lowercase"]
        if v not in allowed_ops:
            raise ValueError(f"Operation must be one of: {allowed_ops}")
        return v

class TextProcessorOutput(BaseModel):
    """Text processor tool output"""
    text: str = Field(..., description="Original text")
    operation: str = Field(..., description="Operation performed")
    result: Optional[Union[str, int]] = Field(None, description="Processing result")
    success: bool = Field(..., description="Whether operation succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")

class SystemInfoInput(BaseModel):
    """System info tool input"""
    info_type: str = Field(..., description="Type of system information")
    
    @validator('info_type')
    def validate_info_type(cls, v):
        """Validate info type"""
        allowed_types = ["time", "date", "timestamp"]
        if v not in allowed_types:
            raise ValueError(f"Info type must be one of: {allowed_types}")
        return v

class SystemInfoOutput(BaseModel):
    """System info tool output"""
    info_type: str = Field(..., description="Type of information requested")
    result: str = Field(..., description="System information result")
    success: bool = Field(..., description="Whether operation succeeded")
    error: Optional[str] = Field(None, description="Error message if failed")

class ToolManager(BaseModel):
    """
    Tool management for agents with comprehensive Pydantic validation
    
    Provides:
    - Tool registration and discovery with validation
    - Tool execution with comprehensive error handling
    - Tool categorization and metadata management
    - Tool discovery based on context
    - Automatic input/output validation
    """
    
    tools: Dict[str, Tool] = Field(default_factory=dict, description="Registered tools")
    auto_discover: bool = Field(default=True, description="Auto-discover default tools")
    _lock: Optional[asyncio.Lock] = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True  # Allow asyncio.Lock
    
    def __init__(self, auto_discover: bool = True, **kwargs):
        """Initialize tool manager with Pydantic validation"""
        super().__init__(auto_discover=auto_discover, **kwargs)
        self._lock = asyncio.Lock()
        
        # Register default tools if auto_discover is enabled
        if auto_discover:
            self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools with Pydantic validation"""
        # Calculator tool
        self.register_tool_with_pydantic(
            name="calculator",
            description="Perform basic mathematical calculations",
            function=self._calculator,
            input_schema=CalculatorInput,
            output_schema=CalculatorOutput,
            category="math",
            metadata=ToolMetadata(
                version="1.0.0",
                author="BasicAI Framework",
                tags=["math", "calculation", "arithmetic"],
                examples=[{"expression": "2 + 2", "result": 4}]
            )
        )
        
        # Text processing tool
        self.register_tool_with_pydantic(
            name="text_processor",
            description="Process and analyze text",
            function=self._text_processor,
            input_schema=TextProcessorInput,
            output_schema=TextProcessorOutput,
            category="text",
            metadata=ToolMetadata(
                version="1.0.0",
                author="BasicAI Framework",
                tags=["text", "processing", "analysis"],
                examples=[{"text": "Hello World", "operation": "count_words", "result": 2}]
            )
        )
        
        # System information tool
        self.register_tool_with_pydantic(
            name="system_info",
            description="Get system information",
            function=self._system_info,
            input_schema=SystemInfoInput,
            output_schema=SystemInfoOutput,
            category="system",
            metadata=ToolMetadata(
                version="1.0.0",
                author="BasicAI Framework",
                tags=["system", "info", "datetime"],
                examples=[{"info_type": "time", "result": "14:30:25"}]
            )
        )
    
    def register_tool_with_pydantic(self, 
                                   name: str, 
                                   description: str, 
                                   function: Callable,
                                   input_schema: Optional[Type[BaseModel]] = None,
                                   output_schema: Optional[Type[BaseModel]] = None,
                                   category: Optional[str] = None,
                                   metadata: Optional[ToolMetadata] = None) -> None:
        """
        Register a tool with Pydantic validation (REQUIRED)
        
        Args:
            name: Tool name (must be unique)
            description: Tool description
            function: Function to execute
            input_schema: Pydantic model for input validation
            output_schema: Pydantic model for output validation
            category: Optional category for organization
            metadata: Optional tool metadata
        """
        if name in self.tools:
            raise ValueError(f"Tool '{name}' already registered")
        
        # Validate that at least one schema is provided
        if not input_schema and not output_schema:
            raise ValueError("At least one schema (input_schema or output_schema) must be provided")
        
        # Create tool with Pydantic validation
        tool = Tool(
            name=name,
            description=description,
            function=function,
            input_schema=input_schema,
            output_schema=output_schema,
            category=category,
            metadata=metadata or ToolMetadata()
        )
        
        self.tools[name] = tool
        validation_info = []
        if input_schema:
            validation_info.append("input validation")
        if output_schema:
            validation_info.append("output validation")
        
        validation_str = f" with {', '.join(validation_info)}"
        print(f"🔧 Registered tool with Pydantic{validation_str}: {name}")
    
    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool
        
        Args:
            name: Tool name to unregister
            
        Returns:
            True if tool was unregistered, False if not found
        """
        if name in self.tools:
            del self.tools[name]
            print(f"🗑️ Unregistered tool: {name}")
            return True
        return False
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[Tool]:
        """
        List all tools, optionally filtered by category
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of tools
        """
        if category:
            return [tool for tool in self.tools.values() if tool.category == category]
        return list(self.tools.values())
    
    def get_tool_names(self, category: Optional[str] = None) -> List[str]:
        """Get list of tool names"""
        tools = self.list_tools(category)
        return [tool.name for tool in tools]
    
    def search_tools(self, query: str) -> List[Tool]:
        """
        Search for tools by name or description
        
        Args:
            query: Search query
            
        Returns:
            List of matching tools
        """
        query_lower = query.lower()
        matches = []
        
        for tool in self.tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower()):
                matches.append(tool)
        
        return matches
    
    async def execute_tool(self, name: str, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute a tool with comprehensive Pydantic validation
        
        Args:
            name: Tool name
            parameters: Parameters to pass to the tool
            
        Returns:
            ToolResult with standardized output
            
        Raises:
            ValueError: If tool not found or validation fails
        """
        if name not in self.tools:
            return ToolResult.error(name, f"Tool '{name}' not found")
        
        tool = self.tools[name]
        start_time = time.time()
        
        try:
            # Validate input with Pydantic
            validated_input = None
            if tool.input_schema:
                try:
                    validated_input = tool.input_schema(**parameters)
                except ValidationError as e:
                    execution_time = time.time() - start_time
                    return ToolResult.error(
                        name, 
                        f"Input validation failed: {e}",
                        execution_time=execution_time
                    )
            
            # Execute tool with validated input
            if validated_input:
                if asyncio.iscoroutinefunction(tool.function):
                    raw_result = await tool.function(**validated_input.dict())
                else:
                    raw_result = tool.function(**validated_input.dict())
            else:
                if asyncio.iscoroutinefunction(tool.function):
                    raw_result = await tool.function(**parameters)
                else:
                    raw_result = tool.function(**parameters)
            
            # Validate output with Pydantic
            validated_output = None
            warnings = []
            
            if tool.output_schema:
                try:
                    validated_output = tool.output_schema(**raw_result)
                except ValidationError as e:
                    warnings.append(f"Output validation warning: {e}")
                    validated_output = raw_result  # Use raw result with warning
            
            execution_time = time.time() - start_time
            
            # Return standardized result
            if warnings:
                return ToolResult.partial(
                    tool_name=name,
                    data=validated_output if validated_output else raw_result,
                    warnings=warnings,
                    execution_time=execution_time,
                    metadata={'input_validated': validated_input is not None}
                )
            else:
                return ToolResult.success(
                    tool_name=name,
                    data=validated_output if validated_output else raw_result,
                    execution_time=execution_time,
                    metadata={'input_validated': validated_input is not None}
                )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult.error(
                tool_name=name,
                error=str(e),
                execution_time=execution_time
            )
    
    def _validate_parameters(self, parameters: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate parameters against JSON schema"""
        # Basic validation - check required parameters
        required = schema.get("required", [])
        for param in required:
            if param not in parameters:
                raise ValueError(f"Required parameter '{param}' not provided")
        
        # Check parameter types
        properties = schema.get("properties", {})
        for param_name, param_value in parameters.items():
            if param_name in properties:
                param_schema = properties[param_name]
                expected_type = param_schema.get("type")
                
                if expected_type == "string" and not isinstance(param_value, str):
                    raise ValueError(f"Parameter '{param_name}' must be a string")
                elif expected_type == "number" and not isinstance(param_value, (int, float)):
                    raise ValueError(f"Parameter '{param_name}' must be a number")
                elif expected_type == "boolean" and not isinstance(param_value, bool):
                    raise ValueError(f"Parameter '{param_name}' must be a boolean")
    
    # Default tool implementations with Pydantic models
    def _calculator(self, expression: str) -> CalculatorOutput:
        """Calculator tool implementation"""
        try:
            result = eval(expression)
            return CalculatorOutput(
                expression=expression,
                result=result,
                success=True
            )
        except Exception as e:
            return CalculatorOutput(
                expression=expression,
                result=None,
                success=False,
                error=str(e)
            )
    
    def _text_processor(self, text: str, operation: str) -> TextProcessorOutput:
        """Text processing tool implementation"""
        try:
            if operation == "count_words":
                result = len(text.split())
            elif operation == "count_chars":
                result = len(text)
            elif operation == "uppercase":
                result = text.upper()
            elif operation == "lowercase":
                result = text.lower()
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            return TextProcessorOutput(
                text=text,
                operation=operation,
                result=result,
                success=True
            )
        except Exception as e:
            return TextProcessorOutput(
                text=text,
                operation=operation,
                result=None,
                success=False,
                error=str(e)
            )
    
    def _system_info(self, info_type: str) -> SystemInfoOutput:
        """System information tool implementation"""
        try:
            if info_type == "time":
                result = datetime.now().strftime("%H:%M:%S")
            elif info_type == "date":
                result = datetime.now().strftime("%Y-%m-%d")
            elif info_type == "timestamp":
                result = datetime.now().isoformat()
            else:
                raise ValueError(f"Unknown info type: {info_type}")
            
            return SystemInfoOutput(
                info_type=info_type,
                result=result,
                success=True
            )
        except Exception as e:
            return SystemInfoOutput(
                info_type=info_type,
                result="",
                success=False,
                error=str(e)
            )
    
    # Advanced tool management
    def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool schema for LLM function calling"""
        tool = self.get_tool(name)
        if not tool:
            return None
        
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters
        }
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas for LLM function calling"""
        return [self.get_tool_schema(name) for name in self.tools.keys()]
    
    def get_tools_for_context(self, context: str) -> List[Tool]:
        """
        Get tools relevant to a given context
        
        Args:
            context: Context string to match against
            
        Returns:
            List of relevant tools
        """
        context_lower = context.lower()
        relevant_tools = []
        
        for tool in self.tools.values():
            # Check if tool name or description matches context
            if (context_lower in tool.name.lower() or 
                context_lower in tool.description.lower() or
                (tool.category and context_lower in tool.category.lower())):
                relevant_tools.append(tool)
        
        return relevant_tools
    
    def get_tool_categories(self) -> List[str]:
        """Get all tool categories"""
        categories = set()
        for tool in self.tools.values():
            if tool.category:
                categories.add(tool.category)
        return list(categories)
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get tools by category"""
        return [tool for tool in self.tools.values() if tool.category == category]
    
    # Utility methods
    def get_info(self) -> Dict[str, Any]:
        """Get information about the tool manager"""
        validated_tools = sum(1 for tool in self.tools.values() if tool.has_validation())
        
        return {
            'total_tools': len(self.tools),
            'validated_tools': validated_tools,
            'categories': self.get_tool_categories(),
            'tool_names': list(self.tools.keys()),
            'auto_discover': self.auto_discover,
            'pydantic_enforced': True,
            'validation_required': True
        }
    
    def export_tools(self, filepath: str) -> None:
        """Export tools to JSON file"""
        data = {
            'tools': [tool.to_dict() for tool in self.tools.values()],
            'exported_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📁 Exported {len(self.tools)} tools to {filepath}")
    
    def import_tools(self, filepath: str) -> None:
        """Import tools from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        imported_count = 0
        for tool_data in data.get('tools', []):
            # Note: This only imports tool metadata, not the actual functions
            # Functions would need to be re-registered
            print(f"📁 Imported tool metadata: {tool_data['name']}")
            imported_count += 1
        
        print(f"📁 Imported {imported_count} tool definitions from {filepath}")

# Convenience functions
def create_tool_manager(auto_discover: bool = True) -> ToolManager:
    """Create a new tool manager instance with Pydantic validation"""
    return ToolManager(auto_discover=auto_discover)

def register_calculator_tool(tool_manager: ToolManager) -> None:
    """Register a calculator tool with Pydantic validation"""
    tool_manager.register_tool_with_pydantic(
        name="calculator",
        description="Perform basic mathematical calculations",
        function=tool_manager._calculator,
        input_schema=CalculatorInput,
        output_schema=CalculatorOutput,
        category="math"
    )

# Example usage
async def example_usage():
    """Example of how to use the tool management with Pydantic validation"""
    
    # Create tool manager
    tool_manager = create_tool_manager()
    
    # List available tools
    tools = tool_manager.list_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")
    
    # Execute a calculator tool
    result = await tool_manager.execute_tool("calculator", {"expression": "2 + 2"})
    print(f"Calculator result: {result}")
    
    # Execute a text processing tool
    result = await tool_manager.execute_tool("text_processor", {
        "text": "Hello World",
        "operation": "count_words"
    })
    print(f"Text processing result: {result}")
    
    # Search for tools
    math_tools = tool_manager.search_tools("math")
    print(f"Math tools: {[tool.name for tool in math_tools]}")
    
    # Get tool info
    info = tool_manager.get_info()
    print(f"Tool manager info: {info}")
    
    # Example of registering a custom tool with Pydantic
    class CustomInput(BaseModel):
        message: str = Field(..., min_length=1)
        count: int = Field(..., ge=1, le=100)
    
    class CustomOutput(BaseModel):
        result: str = Field(...)
        success: bool = Field(...)
    
    def custom_function(message: str, count: int) -> CustomOutput:
        return CustomOutput(
            result=f"{message} repeated {count} times",
            success=True
        )
    
    tool_manager.register_tool_with_pydantic(
        name="custom_tool",
        description="Custom tool with Pydantic validation",
        function=custom_function,
        input_schema=CustomInput,
        output_schema=CustomOutput,
        category="custom"
    )
    
    # Execute custom tool
    result = await tool_manager.execute_tool("custom_tool", {
        "message": "Hello",
        "count": 3
    })
    print(f"Custom tool result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
