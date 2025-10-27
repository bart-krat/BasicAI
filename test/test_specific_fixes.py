"""
Test script for specific parsing fixes
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from parser import JSONParser, YAMLParser

def test_specific_json_fixes():
    """Test the specific JSON cases that were failing"""
    print("🧪 Testing Specific JSON Fixes...")
    
    parser = JSONParser(auto_fix=True)
    
    # Test case 1: Array with missing bracket
    print("\n📝 Testing: Array with missing bracket")
    text1 = '{"skills": ["Python", "JavaScript", "SQL"'
    print(f"   Input: {text1}")
    
    result1 = parser.parse(text1)
    if result1.success:
        print(f"✅ SUCCESS: {result1.data}")
        if result1.warnings:
            print(f"   Warnings: {result1.warnings}")
    else:
        print(f"❌ FAILED: {result1.error}")
    
    # Test case 2: Complex nested structure
    print("\n📝 Testing: Complex nested structure")
    text2 = '''
    {
        "user": {
            "name": "John",
            "details": {
                "age": 30,
                "city": "New York"
            }
        }
    '''
    print(f"   Input: {text2[:50]}...")
    
    result2 = parser.parse(text2)
    if result2.success:
        print(f"✅ SUCCESS: {result2.data}")
        if result2.warnings:
            print(f"   Warnings: {result2.warnings}")
    else:
        print(f"❌ FAILED: {result2.error}")

def test_specific_yaml_fixes():
    """Test the specific YAML cases that were failing"""
    print("\n🧪 Testing Specific YAML Fixes...")
    
    parser = YAMLParser(auto_fix=True)
    
    # Test case 1: Inconsistent indentation
    print("\n📝 Testing: Inconsistent indentation")
    text1 = '''
    name: John
    age: 30
      city: New York
    '''
    print(f"   Input: {text1}")
    
    result1 = parser.parse(text1)
    if result1.success:
        print(f"✅ SUCCESS: {result1.data}")
        if result1.warnings:
            print(f"   Warnings: {result1.warnings}")
    else:
        print(f"❌ FAILED: {result1.error}")
    
    # Test case 2: Mixed quote styles
    print("\n📝 Testing: Mixed quote styles")
    text2 = '''
    name: 'John'
    age: 30
    city: "New York"
    '''
    print(f"   Input: {text2}")
    
    result2 = parser.parse(text2)
    if result2.success:
        print(f"✅ SUCCESS: {result2.data}")
        if result2.warnings:
            print(f"   Warnings: {result2.warnings}")
    else:
        print(f"❌ FAILED: {result2.error}")

def test_llm_output_parsing():
    """Test parsing LLM output with markdown"""
    print("\n🧪 Testing LLM Output Parsing...")
    
    from parser import StructuredOutputParser
    parser = StructuredOutputParser()
    
    # Test case 1: JSON with markdown
    print("\n📝 Testing: JSON with markdown")
    text1 = '''
    Here's the user data:
    
    ```json
    {
        "name": "John",
        "age": 30,
        "skills": ["Python", "JavaScript"]
    }
    ```
    
    The data includes user information.
    '''
    print(f"   Input: {text1[:50]}...")
    
    result1 = parser.parse_json(text1)
    if result1.success:
        print(f"✅ SUCCESS: {result1.data}")
        if result1.warnings:
            print(f"   Warnings: {result1.warnings}")
    else:
        print(f"❌ FAILED: {result1.error}")
    
    # Test case 2: YAML with markdown
    print("\n📝 Testing: YAML with markdown")
    text2 = '''
    Here's the configuration:
    
    ```yaml
    database:
      host: localhost
      port: 5432
      name: myapp
    ```
    
    This configuration should work.
    '''
    print(f"   Input: {text2[:50]}...")
    
    result2 = parser.parse_yaml(text2)
    if result2.success:
        print(f"✅ SUCCESS: {result2.data}")
        if result2.warnings:
            print(f"   Warnings: {result2.warnings}")
    else:
        print(f"❌ FAILED: {result2.error}")

def main():
    """Run all specific fix tests"""
    print("🚀 Testing Specific Parsing Fixes...")
    print("=" * 60)
    
    try:
        test_specific_json_fixes()
        test_specific_yaml_fixes()
        test_llm_output_parsing()
        
        print("\n" + "=" * 60)
        print("🎉 All specific fix tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
