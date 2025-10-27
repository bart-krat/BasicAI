"""
Test script for the fixed robust parsing
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from parser import JSONParser, YAMLParser, StructuredOutputParser

def test_fixed_json_parsing():
    """Test the fixed JSON parsing with the problematic cases"""
    print("🧪 Testing Fixed JSON Parsing...")
    
    parser = JSONParser(auto_fix=True)
    
    # The problematic test cases from before
    test_cases = [
        {
            "name": "Trailing comma",
            "text": '{"name": "John", "age": 30,}',
            "expected_success": True,
            "description": "LLM added trailing comma"
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
        },
        {
            "name": "Complex mixed errors",
            "text": '''
            {
                "name": "John",
                "age": 30,
                "skills": ["Python", "JavaScript", "SQL"],
                "details": {
                    "city": "New York",
                    "country": "USA"
                }
            ''',
            "expected_success": True,
            "description": "Multiple missing brackets"
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

def test_fixed_yaml_parsing():
    """Test the fixed YAML parsing with the problematic cases"""
    print("\n🧪 Testing Fixed YAML Parsing...")
    
    parser = YAMLParser(auto_fix=True)
    
    # The problematic test cases from before
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

def test_aggressive_fixes():
    """Test the aggressive fixing capabilities"""
    print("\n🧪 Testing Aggressive Fixes...")
    
    parser = JSONParser(auto_fix=True)
    
    # Complex cases that need aggressive fixing
    test_cases = [
        {
            "name": "Multiple errors combined",
            "text": '''
            {
                name: 'John',
                age: 30,
                skills: [Python, JavaScript, SQL],
                details: {
                    city: 'New York',
                    country: 'USA'
                }
            ''',
            "expected_success": True,
            "description": "Multiple quote, key, and bracket issues"
        },
        {
            "name": "JavaScript-style with errors",
            "text": '''
            {
                // User information
                "name": "John", // User's name
                "age": 30, /* User's age */
                "skills": ["Python", "JavaScript", "SQL"], // Programming skills
            }
            ''',
            "expected_success": True,
            "description": "JavaScript comments with trailing comma"
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

def test_edge_cases():
    """Test edge cases that should still fail"""
    print("\n🧪 Testing Edge Cases (Should Fail)...")
    
    parser = JSONParser(auto_fix=True)
    
    # Cases that should fail even with auto-fix
    test_cases = [
        {
            "name": "Completely invalid",
            "text": "This is not JSON at all",
            "expected_success": False,
            "description": "Text that's not JSON"
        },
        {
            "name": "Too many closing braces",
            "text": '{"name": "John"}}}}}',
            "expected_success": False,
            "description": "Too many closing braces"
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
    """Run all fixed parsing tests"""
    print("🚀 Testing Fixed Robust Parsing...")
    print("=" * 60)
    
    try:
        test_fixed_json_parsing()
        test_fixed_yaml_parsing()
        test_aggressive_fixes()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("🎉 All fixed parsing tests completed!")
        print("\nKey Improvements:")
        print("✅ Fixed order of operations in auto-fix")
        print("✅ Added aggressive JSON fixing")
        print("✅ Added YAML auto-fix capabilities")
        print("✅ Better error detection and recovery")
        print("✅ More comprehensive test coverage")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
