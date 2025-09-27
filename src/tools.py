"""
Tool Management for Agent Framework

This module provides tool management for agents to register, discover,
and execute various tools and functions.
"""

import asyncio
import inspect
import json
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class Tool:
    """A tool definition"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'category': self.category,
            'metadata': self.metadata or {}
        }

class ToolManager:
    """
    Tool management for agents
    
    Provides:
    - Tool registration and discovery
    - Tool execution with error handling
    - Tool categorization and metadata
    - Tool discovery based on context
    """
    
    def __init__(self, auto_discover: bool = True):
        """
        Initialize tool manager
        
        Args:
            auto_discover: Whether to automatically discover tools from registered functions
        """
        self.tools: Dict[str, Tool] = {}
        self.auto_discover = auto_discover
        self._lock = asyncio.Lock()
        
        # Register default tools if auto_discover is enabled
        if auto_discover:
            self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        # Calculator tool
        self.register_tool(
            name="calculator",
            description="Perform basic mathematical calculations",
            function=self._calculator,
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            },
            category="math"
        )
        
        # Text processing tool
        self.register_tool(
            name="text_processor",
            description="Process and analyze text",
            function=self._text_processor,
            parameters={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to process"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["count_words", "count_chars", "uppercase", "lowercase"],
                        "description": "Operation to perform on the text"
                    }
                },
                "required": ["text", "operation"]
            },
            category="text"
        )
        
        # System information tool
        self.register_tool(
            name="system_info",
            description="Get system information",
            function=self._system_info,
            parameters={
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "enum": ["time", "date", "timestamp"],
                        "description": "Type of system information to retrieve"
                    }
                },
                "required": ["info_type"]
            },
            category="system"
        )
    
    def register_tool(self, 
                     name: str, 
                     description: str, 
                     function: Callable,
                     parameters: Dict[str, Any],
                     category: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register a new tool
        
        Args:
            name: Tool name (must be unique)
            description: Tool description
            function: Function to execute
            parameters: JSON schema for parameters
            category: Optional category for organization
            metadata: Optional metadata
        """
        if name in self.tools:
            raise ValueError(f"Tool '{name}' already registered")
        
        tool = Tool(
            name=name,
            description=description,
            function=function,
            parameters=parameters,
            category=category,
            metadata=metadata
        )
        
        self.tools[name] = tool
        print(f"🔧 Registered tool: {name}")
    
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
    
    async def execute_tool(self, name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a tool with given parameters
        
        Args:
            name: Tool name
            parameters: Parameters to pass to the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found
            Exception: If tool execution fails
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        
        tool = self.tools[name]
        
        try:
            # Validate parameters against schema
            self._validate_parameters(parameters, tool.parameters)
            
            # Execute the tool
            if asyncio.iscoroutinefunction(tool.function):
                result = await tool.function(**parameters)
            else:
                result = tool.function(**parameters)
            
            print(f"🔧 Executed tool '{name}' with parameters: {parameters}")
            return result
            
        except Exception as e:
            print(f"❌ Tool execution failed for '{name}': {str(e)}")
            raise
    
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
    
    # Default tool implementations
    def _calculator(self, expression: str) -> Dict[str, Any]:
        """Calculator tool implementation"""
        try:
            # Safe evaluation of mathematical expressions
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                raise ValueError("Invalid characters in expression")
            
            result = eval(expression)
            return {
                "expression": expression,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": str(e),
                "success": False
            }
    
    def _text_processor(self, text: str, operation: str) -> Dict[str, Any]:
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
            
            return {
                "text": text,
                "operation": operation,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "text": text,
                "operation": operation,
                "error": str(e),
                "success": False
            }
    
    def _system_info(self, info_type: str) -> Dict[str, Any]:
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
            
            return {
                "info_type": info_type,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "info_type": info_type,
                "error": str(e),
                "success": False
            }
    
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
        return {
            'total_tools': len(self.tools),
            'categories': self.get_tool_categories(),
            'tool_names': list(self.tools.keys()),
            'auto_discover': self.auto_discover
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
    """Create a new tool manager instance"""
    return ToolManager(auto_discover=auto_discover)

def register_calculator_tool(tool_manager: ToolManager) -> None:
    """Register a calculator tool"""
    tool_manager.register_tool(
        name="calculator",
        description="Perform basic mathematical calculations",
        function=tool_manager._calculator,
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        },
        category="math"
    )

# Example usage
async def example_usage():
    """Example of how to use the tool management"""
    
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

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
