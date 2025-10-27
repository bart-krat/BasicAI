"""
Test script for YAML fix
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from parser import YAMLParser

def test_yaml_mixed_quotes():
    """Test YAML with mixed quote styles"""
    print("🧪 Testing YAML Mixed Quote Styles...")
    
    parser = YAMLParser(auto_fix=True)
    
    # Test case that was failing
    text = '''
    name: 'John'
    age: 30
    city: "New York"
    '''
    
    print(f"Input: {text}")
    
    result = parser.parse(text)
    
    if result.success:
        print(f"✅ SUCCESS: {result.data}")
        if result.warnings:
            print(f"Warnings: {result.warnings}")
    else:
        print(f"❌ FAILED: {result.error}")
        
        # Try to debug the issue
        print("\n🔍 Debugging:")
        print("Original text:")
        print(repr(text))
        
        # Try the fixes manually
        parser_debug = YAMLParser(auto_fix=True)
        
        # Test each fix step
        print("\nStep 1 - Quote fix:")
        step1 = parser_debug._fix_yaml_quotes(text)
        print(repr(step1))
        
        print("\nStep 2 - Missing colons:")
        step2 = parser_debug._fix_missing_colons(step1)
        print(repr(step2))
        
        print("\nStep 3 - Structure fix:")
        step3 = parser_debug._fix_yaml_structure(step2)
        print(repr(step3))
        
        print("\nStep 4 - Indentation fix:")
        step4 = parser_debug._fix_yaml_indentation_properly(step3)
        print(repr(step4))
        
        # Try parsing the final result
        try:
            import yaml
            final_result = yaml.safe_load(step4)
            print(f"\n✅ Manual fix SUCCESS: {final_result}")
        except Exception as e:
            print(f"\n❌ Manual fix FAILED: {e}")

def test_yaml_indentation():
    """Test YAML with inconsistent indentation"""
    print("\n🧪 Testing YAML Indentation...")
    
    parser = YAMLParser(auto_fix=True)
    
    # Test case that was failing
    text = '''
    name: John
    age: 30
      city: New York
    '''
    
    print(f"Input: {text}")
    
    result = parser.parse(text)
    
    if result.success:
        print(f"✅ SUCCESS: {result.data}")
        if result.warnings:
            print(f"Warnings: {result.warnings}")
    else:
        print(f"❌ FAILED: {result.error}")

def main():
    """Run YAML fix tests"""
    print("🚀 Testing YAML Fixes...")
    print("=" * 50)
    
    try:
        test_yaml_mixed_quotes()
        test_yaml_indentation()
        
        print("\n" + "=" * 50)
        print("🎉 YAML fix tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
