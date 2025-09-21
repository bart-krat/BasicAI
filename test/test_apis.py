import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from api import LLMFactory, Message

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

async def test_openai():
    """Test OpenAI API"""
    print("🧪 Testing OpenAI API...")
    
    try:
        # Create OpenAI provider
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            return False
        
        llm = LLMFactory.create_provider(
            provider_name="openai",
            api_key=openai_key,
            model="gpt-3.5-turbo"
        )
        
        # Test basic completion
        messages = [
            Message(role="system", content="You are a helpful assistant. Keep responses brief."),
            Message(role="user", content="What is 2+2?")
        ]
        
        print("📤 Sending request to OpenAI...")
        response = await llm.generate_response(messages, temperature=0.1)
        
        print(f"✅ OpenAI Response: {response.content}")
        print(f"📊 Model: {response.model}")
        print(f"📈 Usage: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

async def test_anthropic():
    """Test Anthropic API"""
    print("\n🧪 Testing Anthropic API...")
    
    try:
        # Create Anthropic provider
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            print("❌ ANTHROPIC_API_KEY not found in environment variables")
            return False
        
        llm = LLMFactory.create_provider(
            provider_name="anthropic",
            api_key=anthropic_key,
            model="claude-3-haiku-20240307"  # Using haiku for faster/cheaper testing
        )
        
        # Test basic completion
        messages = [
            Message(role="system", content="You are a helpful assistant. Keep responses brief."),
            Message(role="user", content="What is 2+2?")
        ]
        
        print("📤 Sending request to Anthropic...")
        response = await llm.generate_response(messages, temperature=0.1)
        
        print(f"✅ Anthropic Response: {response.content}")
        print(f"📊 Model: {response.model}")
        print(f"📈 Usage: {response.usage}")
        
        return True
        
    except Exception as e:
        print(f"❌ Anthropic test failed: {e}")
        return False

async def test_streaming():
    """Test streaming responses"""
    print("\n🧪 Testing Streaming...")
    
    try:
        # Test with OpenAI (streaming is more commonly supported)
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("❌ OPENAI_API_KEY not found for streaming test")
            return False
        
        llm = LLMFactory.create_provider(
            provider_name="openai",
            api_key=openai_key,
            model="gpt-3.5-turbo"
        )
        
        messages = [
            Message(role="user", content="Count from 1 to 5, one number per line.")
        ]
        
        print("📤 Streaming response from OpenAI...")
        print("📝 Response: ", end="", flush=True)
        
        full_response = ""
        async for chunk in llm.stream_response(messages, temperature=0.1):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print(f"\n✅ Streaming completed. Full response: {full_response}")
        return True
        
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False

async def test_conversation():
    """Test multi-turn conversation"""
    print("\n🧪 Testing Multi-turn Conversation...")
    
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("❌ OPENAI_API_KEY not found for conversation test")
            return False
        
        llm = LLMFactory.create_provider(
            provider_name="openai",
            api_key=openai_key,
            model="gpt-3.5-turbo"
        )
        
        # Start conversation
        messages = [
            Message(role="system", content="You are a helpful math tutor. Keep responses brief."),
            Message(role="user", content="What is 5 + 3?")
        ]
        
        print("📤 Turn 1 - User: What is 5 + 3?")
        response1 = await llm.generate_response(messages, temperature=0.1)
        print(f"🤖 Assistant: {response1.content}")
        
        # Add assistant response and continue conversation
        messages.append(Message(role="assistant", content=response1.content))
        messages.append(Message(role="user", content="Now multiply that by 2"))
        
        print("📤 Turn 2 - User: Now multiply that by 2")
        response2 = await llm.generate_response(messages, temperature=0.1)
        print(f"🤖 Assistant: {response2.content}")
        
        print("✅ Multi-turn conversation test completed")
        return True
        
    except Exception as e:
        print(f"❌ Conversation test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("�� Starting API Tests...")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("❌ .env file not found in root directory")
        print("Please create a .env file with your API keys:")
        print("OPENAI_API_KEY=your_openai_key_here")
        print("ANTHROPIC_API_KEY=your_anthropic_key_here")
        return
    
    # Run tests
    tests = [
        ("OpenAI Basic", test_openai),
        ("Anthropic Basic", test_anthropic),
        ("Streaming", test_streaming),
        ("Conversation", test_conversation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("�� TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your API framework is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
