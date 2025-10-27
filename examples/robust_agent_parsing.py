"""
Example: Using robust parsing with the agent framework
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agent import Agent
from parser import StructuredOutputParser

async def example_structured_output():
    """Example of getting structured output from LLM with robust parsing"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ API key not found")
        return
    
    # Create agent and parser
    agent = Agent(provider="openai", model="gpt-3.5-turbo", api_key=api_key)
    parser = StructuredOutputParser()
    
    print("🤖 Getting Structured Output from LLM...")
    print("=" * 50)
    
    # Example 1: Get user data as JSON
    print("\n📝 Example 1: User Data (JSON)")
    prompt1 = """
    Create a JSON object with user information including:
    - name (string)
    - age (number)
    - email (string)
    - skills (array of strings)
    - is_active (boolean)
    
    Make sure to return valid JSON format.
    """
    
    try:
        response1 = await agent.generate(prompt1)
        print(f"LLM Response: {response1}")
        
        # Parse with robust error handling
        result1 = parser.parse_json(response1)
        
        if result1.success:
            print("✅ Successfully parsed JSON:")
            print(f"   Data: {result1.data}")
            if result1.warnings:
                print(f"   Warnings: {result1.warnings}")
        else:
            print(f"❌ Failed to parse JSON: {result1.error}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Get configuration as YAML
    print("\n📝 Example 2: Configuration (YAML)")
    prompt2 = """
    Create a YAML configuration file for a web application with:
    - database settings (host, port, name)
    - redis settings (host, port)
    - server settings (host, port, debug)
    
    Make sure to return valid YAML format.
    """
    
    try:
        response2 = await agent.generate(prompt2)
        print(f"LLM Response: {response2}")
        
        # Parse with robust error handling
        result2 = parser.parse_yaml(response2)
        
        if result2.success:
            print("✅ Successfully parsed YAML:")
            print(f"   Data: {result2.data}")
            if result2.warnings:
                print(f"   Warnings: {result2.warnings}")
        else:
            print(f"❌ Failed to parse YAML: {result2.error}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Auto-detect format
    print("\n📝 Example 3: Auto-detect Format")
    prompt3 = """
    Create a data structure with information about a project:
    - project name
    - team members (array)
    - budget (number)
    - status (string)
    
    Return it in a structured format (JSON or YAML).
    """
    
    try:
        response3 = await agent.generate(prompt3)
        print(f"LLM Response: {response3}")
        
        # Auto-detect and parse
        result3 = parser.auto_parse(response3)
        
        if result3.success:
            print("✅ Successfully parsed (auto-detected):")
            print(f"   Data: {result3.data}")
            if result3.warnings:
                print(f"   Warnings: {result3.warnings}")
        else:
            print(f"❌ Failed to parse: {result3.error}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def example_error_recovery():
    """Example of how the parser handles LLM errors"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ API key not found")
        return
    
    # Create agent and parser
    agent = Agent(provider="openai", model="gpt-3.5-turbo", api_key=api_key)
    parser = StructuredOutputParser()
    
    print("\n🛠️ Testing Error Recovery...")
    print("=" * 50)
    
    # Simulate LLM output with common errors
    problematic_outputs = [
        {
            "name": "Missing closing brace",
            "text": '''
            Here's the data:
            ```json
            {
                "name": "John",
                "age": 30,
                "skills": ["Python", "JavaScript"]
            ```
            ''',
            "description": "LLM forgot to close the JSON object"
        },
        {
            "name": "Trailing comma",
            "text": '''
            ```json
            {
                "status": "success",
                "data": {
                    "users": [
                        {"name": "Alice", "age": 25},
                        {"name": "Bob", "age": 30}
                    ]
                }
            }
            ```
            ''',
            "description": "LLM added trailing comma"
        }
    ]
    
    for test_case in problematic_outputs:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        
        # Parse with error recovery
        result = parser.parse_json(test_case['text'])
        
        if result.success:
            print("✅ Successfully recovered from error:")
            print(f"   Data: {result.data}")
            if result.warnings:
                print(f"   Warnings: {result.warnings}")
        else:
            print(f"❌ Could not recover: {result.error}")

async def main():
    """Main function"""
    print("🚀 Robust Agent Parsing Examples")
    print("=" * 60)
    
    try:
        await example_structured_output()
        await example_error_recovery()
        
        print("\n" + "=" * 60)
        print("🎉 Examples completed!")
        print("\nKey Benefits:")
        print("✅ Robust error handling")
        print("✅ Automatic error recovery")
        print("✅ Detailed error messages")
        print("✅ Warning system")
        print("✅ Easy integration with agent framework")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
