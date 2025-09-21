from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from dataclasses import dataclass
import json
import httpx

@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None  # tokens_used, etc.
    metadata: Optional[Dict[str, Any]] = None

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def stream_response(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream responses from the LLM (generator)"""
        pass
    
    def validate_messages(self, messages: List[Message]) -> bool:
        """Validate message format"""
        if not messages:
            raise ValueError("Messages list cannot be empty")
        
        for msg in messages:
            if not isinstance(msg, Message):
                raise ValueError("All messages must be Message instances")
            if msg.role not in ['user', 'assistant', 'system']:
                raise ValueError(f"Invalid role: {msg.role}")
        
        return True

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_response(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        self.validate_messages(messages)
        
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        response_data = await self._make_api_call(payload)
        
        return LLMResponse(
            content=response_data["choices"][0]["message"]["content"],
            model=self.model,
            usage=response_data.get("usage"),
            metadata=response_data
        )
    
    async def stream_response(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream responses from OpenAI"""
        self.validate_messages(messages)
        
        openai_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30.0
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
    
    async def _make_api_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call to OpenAI"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API implementation"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    
    async def generate_response(
        self, 
        messages: List[Message], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        self.validate_messages(messages)
        
        # Separate system message if present
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                user_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens or 1024,
            "messages": user_messages,
            "temperature": temperature,
            **kwargs
        }
        
        if system_message:
            payload["system"] = system_message
        
        response_data = await self._make_api_call(payload)
        
        # Extract content from Anthropic's response format
        content = ""
        if response_data.get("content"):
            if isinstance(response_data["content"], list):
                content = "".join([block["text"] for block in response_data["content"] if block["type"] == "text"])
            else:
                content = response_data["content"]
        
        return LLMResponse(
            content=content,
            model=self.model,
            usage=response_data.get("usage"),
            metadata=response_data
        )
    
    async def stream_response(self, messages: List[Message], **kwargs):
        """Stream responses from Anthropic"""
        self.validate_messages(messages)
        
        # Separate system message if present
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                user_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        payload = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "messages": user_messages,
            "temperature": kwargs.get("temperature", 0.7),
            "stream": True,
            **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]}
        }
        
        if system_message:
            payload["system"] = system_message
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30.0
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk.get("type") == "content_block_delta":
                                delta = chunk.get("delta", {})
                                if delta.get("type") == "text_delta" and "text" in delta:
                                    yield delta["text"]
                        except json.JSONDecodeError:
                            continue
    
    async def _make_api_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call to Anthropic"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

class LLMFactory:
    """Factory for creating LLM provider instances"""
    
    _providers = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        # Add more providers as needed
    }
    
    @classmethod
    def create_provider(
        self, 
        provider_name: str, 
        api_key: str, 
        model: str, 
        **kwargs
    ) -> BaseLLMProvider:
        """Create a provider instance"""
        if provider_name not in self._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = self._providers[provider_name]
        return provider_class(api_key, model, **kwargs)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: BaseLLMProvider):
        """Register a new provider"""
        cls._providers[name] = provider_class

# Usage example
async def main():
    # Create provider
    llm = LLMFactory.create_provider(
        provider_name="openai",
        api_key="your-api-key",
        model="gpt-4"
    )
    
    # Use the provider
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Hello, how are you?")
    ]
    
    response = await llm.generate_response(messages)
    print(response.content)
