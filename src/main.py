"""
Main example demonstrating the modular agent framework with direct injection
"""

import asyncio
import os
from dotenv import load_dotenv
from agent import Agent
from state import StateManager
from tools import ToolManager

# Load environment variables
load_dotenv()

async def main():
    """Demonstrate the modular agent framework"""
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your API key in .env file or environment")
        return
    
    print("🚀 Creating modular agent with direct injection...")
    
    # 1. Create components (user defines what they need)
    print("\n📦 Creating components...")
    
    # State manager for persistence
    state_manager = StateManager(
        session_id="demo_session",
        state_dir="./demo_state"
    )
    print("✅ State manager created")
    
    # Tool manager with default tools
    tool_manager = ToolManager(auto_discover=True)
    print("✅ Tool manager created with default tools")
    
    # 2. Create agent with injected components
    print("\n🤖 Creating agent with direct injection...")
    agent = Agent(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key=api_key,
        state_manager=state_manager,
        tool_manager=tool_manager
    )
    print("✅ Agent created with state and tools")
    
    # 3. Demonstrate agent capabilities
    print("\n🧪 Testing agent capabilities...")
    
    # Show agent info
    info = agent.get_info()
    print(f"Agent info: {info}")
    
    # Test state functionality
    print("\n📊 Testing state management...")
    await state_manager.set("user_name", "Demo User")
    await state_manager.set("demo_step", 1)
    
    user_name = await state_manager.get("user_name")
    print(f"Stored user name: {user_name}")
    
    # Test tools functionality
    print("\n🔧 Testing tools...")
    available_tools = await agent.get_available_tools()
    print(f"Available tools: {available_tools}")
    
    # Execute a tool
    calc_result = await agent.execute_tool("calculator", {"expression": "10 + 5"})
    print(f"Calculator result: {calc_result}")
    
    # Test text processing tool
    text_result = await agent.execute_tool("text_processor", {
        "text": "Hello World",
        "operation": "count_words"
    })
    print(f"Text processing result: {text_result}")
    
    # 4. Test enhanced generation with state and tools
    print("\n💬 Testing enhanced generation...")
    
    response = await agent.generate(
        prompt="What is 15 * 3? You can use the calculator tool if needed.",
        system_message="You are a helpful assistant with access to tools.",
        use_state=True,
        use_tools=True
    )
    print(f"AI Response: {response}")
    
    # 5. Interactive chat with state and tools
    print("\n🎯 Starting interactive chat with state and tools...")
    print("Type 'quit' to exit, 'info' to see agent info, 'tools' to see available tools")
    
    await agent.start_chat(
        system_message="You are a helpful assistant with access to tools and memory. You can remember our conversation and use tools when needed."
    )
    
    # 6. Show final state
    print("\n📋 Final state:")
    all_state = await state_manager.get_all()
    for key, value in all_state.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())