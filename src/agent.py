"""
Simple Agent Framework

This module provides a simplified interface for interacting with different LLM providers.
"""

from typing import Optional, Dict, Any, AsyncGenerator
from api import LLMFactory, Message, LLMResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Agent:
    """Simple agent interface for LLM interactions"""
    
    def __init__(self, provider: str, model: str, api_key: Optional[str] = None):
        """
        Initialize the agent with provider and model
        
        Args:
            provider: 'openai' or 'anthropic'
            model: Model name (e.g., 'gpt-4', 'claude-3-sonnet-20240229')
            api_key: Optional API key (will use environment variable if not provided)
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
    
    async def generate(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None, 
        temperature: float = 0.7,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            prompt: The user prompt
            max_tokens: Maximum tokens to generate (optional)
            temperature: Temperature for response generation (0.0-1.0)
            system_message: Optional system message to set context
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Generated response as string
        """
        # Build messages
        messages = []
        
        if system_message:
            messages.append(Message(role="system", content=system_message))
        
        messages.append(Message(role="user", content=prompt))
        
        # Generate response
        response = await self.llm.generate_response(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
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
        """Start an interactive chat session"""
        conversation = [{"role": "system", "content": system_message}]
    
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'quit':
                break
            
            # Add user message
            conversation.append({"role": "user", "content": user_input})
            
            # Get AI response - THIS IS WHERE IT USES chat()
            response = await self.chat(conversation)  # ← Uses chat() internally
            
            print(f"AI: {response}")
            
            # Add AI response
            conversation.append({"role": "assistant", "content": response})
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        return {
            'provider': self.provider,
            'model': self.model,
            'api_key_configured': bool(self.api_key)
        }

# Convenience functions for quick agent creation
def create_openai_agent(model: str = "gpt-3.5-turbo", api_key: Optional[str] = None) -> Agent:
    """Create an OpenAI agent quickly"""
    return Agent(provider="openai", model=model, api_key=api_key)

def create_anthropic_agent(model: str = "claude-3-haiku-20240307", api_key: Optional[str] = None) -> Agent:
    """Create an Anthropic agent quickly"""
    return Agent(provider="anthropic", model=model, api_key=api_key)

# Usage examples
async def example_usage():
    """Example of how to use the agent framework"""
    
    # Create agents
    openai_agent = create_openai_agent("gpt-4")
    anthropic_agent = create_anthropic_agent("claude-3-sonnet-20240229")
    
    # Simple generation
    response1 = await openai_agent.generate(
        prompt="What is the capital of France?",
        temperature=0.7
    )
    print(f"OpenAI: {response1}")
    
    # With system message
    response2 = await anthropic_agent.generate(
        prompt="Explain quantum computing",
        system_message="You are a physics professor explaining to undergraduate students.",
        temperature=0.3
    )
    print(f"Anthropic: {response2}")
    
    # Streaming
    print("Streaming response:")
    async for chunk in openai_agent.stream(
        prompt="Write a short story about a robot",
        temperature=0.8
    ):
        print(chunk, end="", flush=True)
    print("\n")
    
    # Chat conversation
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help you today?"},
        {"role": "user", "content": "What's the weather like?"}
    ]
    
    response3 = await openai_agent.chat(conversation)
    print(f"Chat response: {response3}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())