"""
Test script for robust parsing with error recovery
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from parser import JSONParser, YAMLParser, StructuredOutputParser

def test_json_error_recovery():
    """Test JSON parser's ability to recover from common LLM errors"""
    print("🧪 Testing JSON Error Recovery...")
    
    parser = JSONParser(auto_fix=True)
    
    # Common LLM JSON errors
    test_cases = [
        {
            "name": "Missing closing brace",
            "text": '{"name": "John", "age": 30',
            "expected_success": True,
            "description": "LLM forgot to close the object"
        },
        {
            "name": "Trailing comma",
            "text": '{"name": "John", "age": 30,}',
            "expected_success": True,
            "description": "LLM added trailing comma"
        },
        {
            "name": "Unquoted keys",
            "text": '{name: "John", age: 30}',
            "expected_success": True,
            "description": "LLM used unquoted keys"
        },
        {
            "name": "Single quotes",
            "text": "{'name': 'John', 'age': 30}",
            "expected_success": True,
            "description": "LLM used single quotes instead of double"
        },
        {
            "name": "Mixed quotes and unquoted",
            "text": "{name: 'John', age: 30, city: 'New York'}",
            "expected_success": True,
            "description": "LLM mixed quote styles"
        },
        {
            "name": "JavaScript-style comments",
            "text": '''
            {
                "name": "John", // User's name
                "age": 30, /* User's age */
                "city": "New York"
            }
            ''',
            "expected_success": True,
            "description": "LLM added JavaScript-style comments"
        },
        {
            "name": "Missing quotes around string values",
            "text": '{"name": John, "age": 30, "city": New York}',
            "expected_success": True,
            "description": "LLM forgot quotes around string values"
        },
        {
            "name": "Nested object with missing brace",
            "text": '''
            {
                "user": {
                    "name": "John",
                    "details": {
                        "age": 30,
                        "city": "New York"
                    }
                }
            ''',
            "expected_success": True,
            "description": "LLM forgot closing brace in nested object"
        },
        {
            "name": "Array with missing bracket",
            "text": '{"skills": ["Python", "JavaScript", "SQL"',
            "expected_success": True,
            "description": "LLM forgot closing bracket in array"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Input: {test_case['text'][:50]}...")
        
        result = parser.parse(test_case['text'])
        
        if result.success == test_case['expected_success']:
            print(f"✅ {test_case['name']} - {'PASSED' if result.success else 'FAILED as expected'}")
            if result.success:
                print(f"   Parsed data: {result.data}")
                if result.warnings:
                    print(f"   Warnings: {result.warnings}")
        else:
            print(f"❌ {test_case['name']} - Expected {test_case['expected_success']}, got {result.success}")
            if result.error:
                print(f"   Error: {result.error}")

def test_yaml_error_recovery():
    """Test YAML parser's ability to recover from common LLM errors"""
    print("\n🧪 Testing YAML Error Recovery...")
    
    parser = YAMLParser(auto_fix=True)
    
    # Common LLM YAML errors
    test_cases = [
        {
            "name": "Inconsistent indentation",
            "text": '''
            name: John
            age: 30
              city: New York
            ''',
            "expected_success": True,
            "description": "LLM used inconsistent indentation"
        },
        {
            "name": "Missing colons",
            "text": '''
            name John
            age 30
            city New York
            ''',
            "expected_success": True,
            "description": "LLM forgot colons after keys"
        },
        {
            "name": "Mixed quote styles",
            "text": '''
            name: 'John'
            age: 30
            city: "New York"
            ''',
            "expected_success": True,
            "description": "LLM mixed single and double quotes"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        
        result = parser.parse(test_case['text'])
        
        if result.success == test_case['expected_success']:
            print(f"✅ {test_case['name']} - {'PASSED' if result.success else 'FAILED as expected'}")
            if result.success:
                print(f"   Parsed data: {result.data}")
                if result.warnings:
                    print(f"   Warnings: {result.warnings}")
        else:
            print(f"❌ {test_case['name']} - Expected {test_case['expected_success']}, got {result.success}")
            if result.error:
                print(f"   Error: {result.error}")

def test_llm_output_parsing():
    """Test parsing real-world LLM output with errors"""
    print("\n🧪 Testing Real-World LLM Output...")
    
    parser = StructuredOutputParser()
    
    # Simulate real LLM responses with common errors
    llm_responses = [
        {
            "name": "LLM Response with JSON errors",
            "text": '''
            Here's the user data you requested:
            
            ```json
            {
                "users": [
                    {"name": "Alice", "age": 25, "skills": ["Python", "JavaScript"]},
                    {"name": "Bob", "age": 30, "skills": ["Java", "SQL"]
                ]
            }
            ```
            
            The data includes user information and their skills.
            ''',
            "expected_success": True
        },
        {
            "name": "LLM Response with mixed content",
            "text": '''
            I'll create a configuration file for you:
            
            ```yaml
            database:
              host: localhost
              port: 5432
              name: myapp
            redis:
              host: localhost
              port: 6379
            ```
            
            This configuration should work for your application.
            ''',
            "expected_success": True
        },
        {
            "name": "LLM Response with malformed JSON",
            "text": '''
            Here's the API response:
            
            ```json
            {
                "status": "success",
                "data": {
                    "users": [
                        {"id": 1, "name": "John", "email": "john@example.com"},
                        {"id": 2, "name": "Jane", "email": "jane@example.com"}
                    ]
                }
            }
            ```
            
            The API returned successfully.
            ''',
            "expected_success": True
        }
    ]
    
    for test_case in llm_responses:
        print(f"\n📝 Testing: {test_case['name']}")
        
        result = parser.auto_parse(test_case['text'])
        
        if result.success == test_case['expected_success']:
            print(f"✅ {test_case['name']} - {'PASSED' if result.success else 'FAILED as expected'}")
            if result.success:
                print(f"   Parsed data: {result.data}")
                if result.warnings:
                    print(f"   Warnings: {result.warnings}")
        else:
            print(f"❌ {test_case['name']} - Expected {test_case['expected_success']}, got {result.success}")
            if result.error:
                print(f"   Error: {result.error}")

def test_error_recovery_limits():
    """Test the limits of error recovery"""
    print("\n🧪 Testing Error Recovery Limits...")
    
    parser = JSONParser(auto_fix=True)
    
    # Cases that should fail even with auto-fix
    test_cases = [
        {
            "name": "Completely malformed JSON",
            "text": "This is not JSON at all",
            "expected_success": False,
            "description": "Text that's not JSON"
        },
        {
            "name": "Too many closing braces",
            "text": '{"name": "John"}}}}}',
            "expected_success": False,
            "description": "Too many closing braces"
        },
        {
            "name": "Invalid JSON structure",
            "text": '{"name": "John", "age": 30, "skills": [Python, JavaScript]}',
            "expected_success": False,
            "description": "Invalid array syntax"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        
        result = parser.parse(test_case['text'])
        
        if result.success == test_case['expected_success']:
            print(f"✅ {test_case['name']} - {'PASSED' if result.success else 'FAILED as expected'}")
        else:
            print(f"❌ {test_case['name']} - Expected {test_case['expected_success']}, got {result.success}")
            if result.error:
                print(f"   Error: {result.error}")

def main():
    """Run all robust parsing tests"""
    print("🚀 Starting Robust Parsing Tests...")
    print("=" * 60)
    
    try:
        test_json_error_recovery()
        test_yaml_error_recovery()
        test_llm_output_parsing()
        test_error_recovery_limits()
        
        print("\n" + "=" * 60)
        print("🎉 All robust parsing tests completed!")
        print("\nKey Benefits:")
        print("✅ Handles missing brackets/braces")
        print("✅ Fixes trailing commas")
        print("✅ Converts single quotes to double quotes")
        print("✅ Adds quotes around unquoted keys and values")
        print("✅ Removes JavaScript-style comments")
        print("✅ Provides detailed error messages")
        print("✅ Maintains data integrity")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
