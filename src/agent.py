"""
Agent Framework with Direct Injection

This module provides a modular agent interface with direct injection of components
like state management, tools, context, and MCP clients.
"""

from typing import Optional, Dict, Any, AsyncGenerator, List
from api import LLMFactory, Message, LLMResponse
from state import StateManager
from tools import ToolManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Agent:
    """Agent with direct injection of components"""
    
    def __init__(self, 
                 provider: str, 
                 model: str, 
                 api_key: Optional[str] = None,
                 state_manager: Optional[StateManager] = None,
                 tool_manager: Optional[ToolManager] = None):
        """
        Initialize the agent with provider, model, and optional components
        
        Args:
            provider: 'openai' or 'anthropic'
            model: Model name (e.g., 'gpt-4', 'claude-3-sonnet-20240229')
            api_key: Optional API key (will use environment variable if not provided)
            state_manager: Optional state manager for persistence
            tool_manager: Optional tool manager for function calling
        """
        self.provider = provider
        self.model = model
        
        # Get API key from parameter or environment
        if api_key:
            self.api_key = api_key
        else:
            if provider == 'openai':
                self.api_key = os.getenv('OPENAI_API_KEY')
            elif provider == 'anthropic':
                self.api_key = os.getenv('ANTHROPIC_API_KEY')
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        if not self.api_key:
            raise ValueError(f"API key not found for provider: {provider}")
        
        # Initialize the LLM provider
        self.llm = LLMFactory.create_provider(
            provider_name=provider,
            api_key=self.api_key,
            model=model
        )
        
        # Direct injection of components
        self.state = state_manager
        self.tools = tool_manager
    
    async def generate(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None, 
        temperature: float = 0.7,
        system_message: Optional[str] = None,
        use_state: bool = True,
        use_tools: bool = True,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM with optional state and tools
        
        Args:
            prompt: The user prompt
            max_tokens: Maximum tokens to generate (optional)
            temperature: Temperature for response generation (0.0-1.0)
            system_message: Optional system message to set context
            use_state: Whether to include state context
            use_tools: Whether to include available tools
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Generated response as string
        """
        # Build enhanced prompt with state and tools
        enhanced_prompt = await self._build_enhanced_prompt(
            prompt, system_message, use_state, use_tools
        )
        
        # Build messages
        messages = []
        
        if system_message:
            messages.append(Message(role="system", content=system_message))
        
        messages.append(Message(role="user", content=enhanced_prompt))
        
        # Generate response
        response = await self.llm.generate_response(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Save interaction to state if available
        if self.state and use_state:
            await self.state.set("last_prompt", prompt)
            await self.state.set("last_response", response.content)
        
        return response.content
    
    async def stream(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None, 
        temperature: float = 0.7,
        system_message: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response from the LLM
        
        Args:
            prompt: The user prompt
            max_tokens: Maximum tokens to generate (optional)
            temperature: Temperature for response generation (0.0-1.0)
            system_message: Optional system message to set context
            **kwargs: Additional parameters for the LLM
            
        Yields:
            Response chunks as they are generated
        """
        # Build messages
        messages = []
        
        if system_message:
            messages.append(Message(role="system", content=system_message))
        
        messages.append(Message(role="user", content=prompt))
        
        # Stream response
        async for chunk in self.llm.stream_response(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk
    
    async def chat(
        self, 
        messages: list, 
        max_tokens: Optional[int] = None, 
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Chat with the LLM using a list of messages
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate (optional)
            temperature: Temperature for response generation (0.0-1.0)
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Generated response as string
        """
        # Convert to Message objects
        message_objects = []
        for msg in messages:
            message_objects.append(Message(
                role=msg['role'], 
                content=msg['content']
            ))
        
        # Generate response
        response = await self.llm.generate_response(
            messages=message_objects,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.content


    async def start_chat(self, system_message: str = "You are a helpful assistant."):
        """Start an interactive chat session with state and tools"""
        conversation = [{"role": "system", "content": system_message}]
        
        # Initialize state if available
        if self.state:
            await self.state.set("chat_started", True)
            await self.state.set("system_message", system_message)
    
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'quit':
                break
            
            # Add user message
            conversation.append({"role": "user", "content": user_input})
            
            # Save user input to state
            if self.state:
                await self.state.set("last_user_input", user_input)
            
            # Get AI response with enhanced context
            response = await self.generate(
                prompt=user_input,
                system_message=system_message,
                use_state=True,
                use_tools=True
            )
            
            print(f"AI: {response}")
            
            # Add AI response
            conversation.append({"role": "assistant", "content": response})
            
            # Save conversation to state
            if self.state:
                await self.state.set("conversation_history", conversation[-6:])  # Keep last 3 exchanges
    
    async def _build_enhanced_prompt(self, 
                                   prompt: str, 
                                   system_message: Optional[str] = None,
                                   use_state: bool = True,
                                   use_tools: bool = True) -> str:
        """Build enhanced prompt with state and tools context"""
        enhanced_parts = []
        
        # Add state context if available
        if self.state and use_state:
            state_context = await self.state.get_context(max_entries=5)
            if state_context and state_context != "No previous context available.":
                enhanced_parts.append(state_context)
        
        # Add tools context if available
        if self.tools and use_tools:
            tools_info = self.tools.get_info()
            if tools_info['total_tools'] > 0:
                tools_context = f"Available tools: {', '.join(tools_info['tool_names'])}"
                enhanced_parts.append(tools_context)
        
        # Add original prompt
        enhanced_parts.append(f"User: {prompt}")
        
        return "\n\n".join(enhanced_parts)
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a tool if available"""
        if not self.tools:
            raise ValueError("No tool manager available")
        
        return await self.tools.execute_tool(tool_name, parameters)
    
    async def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        if not self.tools:
            return []
        
        return self.tools.get_tool_names()
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        info = {
            'provider': self.provider,
            'model': self.model,
            'api_key_configured': bool(self.api_key),
            'has_state_manager': self.state is not None,
            'has_tool_manager': self.tools is not None
        }
        
        if self.state:
            info['state_info'] = self.state.get_info()
        
        if self.tools:
            info['tools_info'] = self.tools.get_info()
        
        return info

# Convenience functions for quick agent creation
def create_openai_agent(model: str = "gpt-3.5-turbo", 
                       api_key: Optional[str] = None,
                       state_manager: Optional[StateManager] = None,
                       tool_manager: Optional[ToolManager] = None) -> Agent:
    """Create an OpenAI agent quickly"""
    return Agent(provider="openai", model=model, api_key=api_key,
                state_manager=state_manager, tool_manager=tool_manager)

def create_anthropic_agent(model: str = "claude-3-haiku-20240307", 
                          api_key: Optional[str] = None,
                          state_manager: Optional[StateManager] = None,
                          tool_manager: Optional[ToolManager] = None) -> Agent:
    """Create an Anthropic agent quickly"""
    return Agent(provider="anthropic", model=model, api_key=api_key,
                state_manager=state_manager, tool_manager=tool_manager)

# Usage examples
async def example_usage():
    """Example of how to use the agent framework with direct injection"""
    
    # Create components
    state_manager = StateManager(session_id="example_session")
    tool_manager = ToolManager()
    
    # Create agents with injected components
    openai_agent = create_openai_agent(
        model="gpt-3.5-turbo",
        state_manager=state_manager,
        tool_manager=tool_manager
    )
    
    # Simple generation with state and tools
    response1 = await openai_agent.generate(
        prompt="What is 2 + 2?",
        temperature=0.7
    )
    print(f"OpenAI: {response1}")
    
    # Execute a tool directly
    result = await openai_agent.execute_tool("calculator", {"expression": "5 * 3"})
    print(f"Tool result: {result}")
    
    # Get agent info
    info = openai_agent.get_info()
    print(f"Agent info: {info}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())