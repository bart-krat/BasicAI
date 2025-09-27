"""
Robust JSON and YAML Parsers for LLM Output

This module provides robust parsing utilities for extracting structured data
from LLM responses with comprehensive error handling and validation.
"""

import json
import yaml
import re
from typing import Any, Dict, List, Optional, Union, Type, Callable
from dataclasses import dataclass
from enum import Enum
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParseError(Exception):
    """Custom exception for parsing errors"""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

@dataclass
class ParseResult:
    """Result of parsing operation"""
    data: Any
    success: bool
    error: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

class JSONParser:
    """Robust JSON parser with error handling, validation, and auto-fixing"""
    
    def __init__(self, strict: bool = True, validate_schema: bool = False, auto_fix: bool = True):
        """
        Initialize JSON parser
        
        Args:
            strict: Whether to use strict JSON parsing
            validate_schema: Whether to validate against a schema
            auto_fix: Whether to attempt automatic fixes for common errors
        """
        self.strict = strict
        self.validate_schema = validate_schema
        self.auto_fix = auto_fix
    
    def parse(self, text: str, schema: Optional[Dict] = None) -> ParseResult:
        """
        Parse JSON from text with comprehensive error handling and auto-fixing
        
        Args:
            text: Text containing JSON
            schema: Optional JSON schema for validation
            
        Returns:
            ParseResult with parsed data and status
        """
        try:
            # Clean the text first
            cleaned_text = self._clean_json_text(text)
            
            # Try to parse JSON
            try:
                if self.strict:
                    data = json.loads(cleaned_text)
                else:
                    data = json.loads(cleaned_text, strict=False)
            except json.JSONDecodeError as e:
                # If auto-fix is enabled, try to fix common errors
                if self.auto_fix:
                    fixed_result = self._attempt_auto_fix(cleaned_text, str(e))
                    if fixed_result.success:
                        data = fixed_result.data
                        warnings = fixed_result.warnings + ["JSON was auto-fixed"]
                    else:
                        return ParseResult(
                            data=None,
                            success=False,
                            error=f"JSON decode error: {str(e)}. Auto-fix failed: {fixed_result.error}"
                        )
                else:
                    return ParseResult(
                        data=None,
                        success=False,
                        error=f"JSON decode error: {str(e)}"
                    )
            
            # Validate against schema if provided
            if schema and self.validate_schema:
                validation_result = self._validate_schema(data, schema)
                if not validation_result.success:
                    return ParseResult(
                        data=None,
                        success=False,
                        error=f"Schema validation failed: {validation_result.error}",
                        warnings=validation_result.warnings
                    )
            
            return ParseResult(
                data=data,
                success=True,
                warnings=self._get_warnings(data)
            )
            
        except Exception as e:
            return ParseResult(
                data=None,
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    def _clean_json_text(self, text: str) -> str:
        """Clean and extract JSON from text"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*$', '', text)
        
        # Find JSON object or array
        json_patterns = [
            r'\{.*\}',  # JSON object
            r'\[.*\]',  # JSON array
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                return matches[0]
        
        return text.strip()
    
    def _validate_schema(self, data: Any, schema: Dict) -> ParseResult:
        """Validate data against JSON schema"""
        try:
            # Basic schema validation (you can enhance this)
            if 'type' in schema:
                expected_type = schema['type']
                if expected_type == 'object' and not isinstance(data, dict):
                    return ParseResult(
                        data=None,
                        success=False,
                        error=f"Expected object, got {type(data).__name__}"
                    )
                elif expected_type == 'array' and not isinstance(data, list):
                    return ParseResult(
                        data=None,
                        success=False,
                        error=f"Expected array, got {type(data).__name__}"
                    )
            
            return ParseResult(data=data, success=True)
            
        except Exception as e:
            return ParseResult(
                data=None,
                success=False,
                error=f"Schema validation error: {str(e)}"
            )
    
    def _get_warnings(self, data: Any) -> List[str]:
        """Generate warnings for parsed data"""
        warnings = []
        
        if isinstance(data, dict):
            if not data:
                warnings.append("Empty JSON object")
            elif len(data) > 100:
                warnings.append("Large JSON object detected")
        
        elif isinstance(data, list):
            if not data:
                warnings.append("Empty JSON array")
            elif len(data) > 1000:
                warnings.append("Large JSON array detected")
        
        return warnings
    
    def _attempt_auto_fix(self, text: str, error_msg: str) -> ParseResult:
        """
        Attempt to automatically fix common JSON errors
        
        Args:
            text: The JSON text to fix
            error_msg: The original error message
            
        Returns:
            ParseResult with fixed data or error
        """
        warnings = []
        fixed_text = text
        
        try:
            # Apply fixes in order of priority
            original_text = fixed_text
            
            # Fix 1: Remove JavaScript-style comments first
            fixed_text = self._remove_comments(fixed_text)
            if fixed_text != original_text:
                warnings.append("Removed JavaScript-style comments")
                original_text = fixed_text
            
            # Fix 2: Fix single quotes to double quotes
            fixed_text = self._fix_single_quotes(fixed_text)
            if fixed_text != original_text:
                warnings.append("Fixed single quotes to double quotes")
                original_text = fixed_text
            
            # Fix 3: Fix unquoted keys
            fixed_text = self._fix_unquoted_keys(fixed_text)
            if fixed_text != original_text:
                warnings.append("Fixed unquoted keys")
                original_text = fixed_text
            
            # Fix 4: Fix unquoted string values
            fixed_text = self._fix_unquoted_strings(fixed_text)
            if fixed_text != original_text:
                warnings.append("Fixed unquoted string values")
                original_text = fixed_text
            
            # Fix 5: Fix trailing commas
            fixed_text = self._fix_trailing_commas(fixed_text)
            if fixed_text != original_text:
                warnings.append("Fixed trailing commas")
                original_text = fixed_text
            
            # Fix 6: Fix missing brackets/braces (do this last)
            fixed_text = self._fix_missing_brackets(fixed_text)
            if fixed_text != original_text:
                warnings.append("Fixed missing brackets/braces")
            
            # Try to parse the fixed text
            data = json.loads(fixed_text)
            
            return ParseResult(
                data=data,
                success=True,
                warnings=warnings
            )
            
        except json.JSONDecodeError as e:
            # If still failing, try a more aggressive approach
            try:
                # Try to extract and fix the JSON more aggressively
                fixed_text = self._aggressive_json_fix(text)
                data = json.loads(fixed_text)
                
                return ParseResult(
                    data=data,
                    success=True,
                    warnings=warnings + ["Applied aggressive JSON fix"]
                )
            except:
                return ParseResult(
                    data=None,
                    success=False,
                    error=f"Auto-fix failed: {str(e)}"
                )
        except Exception as e:
            return ParseResult(
                data=None,
                success=False,
                error=f"Auto-fix error: {str(e)}"
            )
    
    def _fix_missing_brackets(self, text: str) -> str:
        """Fix missing closing brackets and braces"""
        # Count opening and closing brackets
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        
        # Add missing closing braces
        missing_braces = open_braces - close_braces
        if missing_braces > 0:
            text += '}' * missing_braces
        
        # Add missing closing brackets
        missing_brackets = open_brackets - close_brackets
        if missing_brackets > 0:
            text += ']' * missing_brackets
        
        return text
    
    def _fix_array_brackets(self, text: str) -> str:
        """Fix missing array brackets more intelligently"""
        # Find arrays that are missing closing brackets
        # Look for patterns like: "key": ["item1", "item2"
        array_pattern = r'(\w+":\s*\[[^]]*)(?![^[]*\])'
        
        def fix_array(match):
            array_start = match.group(1)
            # Count opening and closing brackets in this array
            open_count = array_start.count('[')
            close_count = array_start.count(']')
            missing = open_count - close_count
            if missing > 0:
                return array_start + ']' * missing
            return array_start
        
        text = re.sub(array_pattern, fix_array, text)
        return text
    
    def _fix_trailing_commas(self, text: str) -> str:
        """Fix trailing commas in JSON"""
        # Remove trailing commas before closing brackets/braces
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        return text
    
    def _aggressive_json_fix(self, text: str) -> str:
        """More aggressive JSON fixing for complex cases"""
        # Remove all comments first
        text = self._remove_comments(text)
        
        # Fix common patterns
        text = re.sub(r'(\w+):', r'"\1":', text)  # Quote unquoted keys
        text = re.sub(r"'([^']*)':", r'"\1":', text)  # Fix single quote keys
        text = re.sub(r":\s*'([^']*)'", r': "\1"', text)  # Fix single quote values
        text = re.sub(r',(\s*[}\]])', r'\1', text)  # Remove trailing commas
        
        # Fix array brackets specifically
        text = self._fix_array_brackets(text)
        
        # Fix missing brackets more intelligently
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        
        # Add missing closing braces
        missing_braces = open_braces - close_braces
        if missing_braces > 0:
            text += '}' * missing_braces
        
        # Add missing closing brackets
        missing_brackets = open_brackets - close_brackets
        if missing_brackets > 0:
            text += ']' * missing_brackets
        
        return text
    
    def _fix_unquoted_keys(self, text: str) -> str:
        """Fix unquoted keys in JSON objects"""
        # Find unquoted keys and quote them
        text = re.sub(r'(\w+):', r'"\1":', text)
        return text
    
    def _fix_single_quotes(self, text: str) -> str:
        """Fix single quotes to double quotes"""
        # Replace single quotes with double quotes, but be careful with apostrophes
        text = re.sub(r"'([^']*)':", r'"\1":', text)  # Keys
        text = re.sub(r":\s*'([^']*)'", r': "\1"', text)  # Values
        return text
    
    def _fix_unquoted_strings(self, text: str) -> str:
        """Fix unquoted string values"""
        # This is more complex - look for patterns like: "key": value
        # where value should be quoted if it's a string
        def quote_string_values(match):
            key = match.group(1)
            value = match.group(2).strip()
            
            # If value looks like a string (not number, boolean, null, or already quoted)
            if not re.match(r'^(true|false|null|\d+\.?\d*|".*")$', value):
                return f'"{key}": "{value}"'
            else:
                return f'"{key}": {value}'
        
        text = re.sub(r'"(\w+)":\s*([^,}\]]+)', quote_string_values, text)
        return text
    
    def _remove_comments(self, text: str) -> str:
        """Remove JavaScript-style comments"""
        # Remove single-line comments
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        # Remove multi-line comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        return text

class YAMLParser:
    """Robust YAML parser with error handling, validation, and auto-fixing"""
    
    def __init__(self, safe_load: bool = True, validate_schema: bool = False, auto_fix: bool = True):
        """
        Initialize YAML parser
        
        Args:
            safe_load: Whether to use safe YAML loading
            validate_schema: Whether to validate against a schema
            auto_fix: Whether to attempt automatic fixes for common errors
        """
        self.safe_load = safe_load
        self.validate_schema = validate_schema
        self.auto_fix = auto_fix
    
    def parse(self, text: str, schema: Optional[Dict] = None) -> ParseResult:
        """
        Parse YAML from text with comprehensive error handling
        
        Args:
            text: Text containing YAML
            schema: Optional schema for validation
            
        Returns:
            ParseResult with parsed data and status
        """
        try:
            # Clean the text first
            cleaned_text = self._clean_yaml_text(text)
            
            # Parse YAML
            if self.safe_load:
                data = yaml.safe_load(cleaned_text)
            else:
                data = yaml.load(cleaned_text, Loader=yaml.FullLoader)
            
            # Validate against schema if provided
            if schema and self.validate_schema:
                validation_result = self._validate_schema(data, schema)
                if not validation_result.success:
                    return ParseResult(
                        data=None,
                        success=False,
                        error=f"Schema validation failed: {validation_result.error}",
                        warnings=validation_result.warnings
                    )
            
            return ParseResult(
                data=data,
                success=True,
                warnings=self._get_warnings(data)
            )
            
        except yaml.YAMLError as e:
            # If auto-fix is enabled, try to fix common YAML errors
            if self.auto_fix:
                fixed_result = self._attempt_yaml_auto_fix(cleaned_text, str(e))
                if fixed_result.success:
                    return ParseResult(
                        data=fixed_result.data,
                        success=True,
                        warnings=fixed_result.warnings + ["YAML was auto-fixed"]
                    )
                else:
                    return ParseResult(
                        data=None,
                        success=False,
                        error=f"YAML parse error: {str(e)}. Auto-fix failed: {fixed_result.error}"
                    )
            else:
                return ParseResult(
                    data=None,
                    success=False,
                    error=f"YAML parse error: {str(e)}"
                )
        except Exception as e:
            return ParseResult(
                data=None,
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    def _clean_yaml_text(self, text: str) -> str:
        """Clean and extract YAML from text"""
        # Remove markdown code blocks
        text = re.sub(r'```yaml\s*', '', text)
        text = re.sub(r'```\s*$', '', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _validate_schema(self, data: Any, schema: Dict) -> ParseResult:
        """Validate data against schema"""
        try:
            # Basic schema validation
            if 'type' in schema:
                expected_type = schema['type']
                if expected_type == 'object' and not isinstance(data, dict):
                    return ParseResult(
                        data=None,
                        success=False,
                        error=f"Expected object, got {type(data).__name__}"
                    )
                elif expected_type == 'array' and not isinstance(data, list):
                    return ParseResult(
                        data=None,
                        success=False,
                        error=f"Expected array, got {type(data).__name__}"
                    )
            
            return ParseResult(data=data, success=True)
            
        except Exception as e:
            return ParseResult(
                data=None,
                success=False,
                error=f"Schema validation error: {str(e)}"
            )
    
    def _get_warnings(self, data: Any) -> List[str]:
        """Generate warnings for parsed data"""
        warnings = []
        
        if isinstance(data, dict):
            if not data:
                warnings.append("Empty YAML object")
            elif len(data) > 100:
                warnings.append("Large YAML object detected")
        
        elif isinstance(data, list):
            if not data:
                warnings.append("Empty YAML array")
            elif len(data) > 1000:
                warnings.append("Large YAML array detected")
        
        return warnings
    
    def _attempt_yaml_auto_fix(self, text: str, error_msg: str) -> ParseResult:
        """
        Attempt to automatically fix common YAML errors
        
        Args:
            text: The YAML text to fix
            error_msg: The original error message
            
        Returns:
            ParseResult with fixed data or error
        """
        warnings = []
        fixed_text = text
        
        try:
            # Apply all fixes in sequence
            original_text = fixed_text
            
            # Fix 1: Fix quote issues first
            fixed_text = self._fix_yaml_quotes(fixed_text)
            if fixed_text != original_text:
                warnings.append("Fixed quote issues")
                original_text = fixed_text
            
            # Fix 2: Add missing colons
            fixed_text = self._fix_missing_colons(fixed_text)
            if fixed_text != original_text:
                warnings.append("Fixed missing colons")
                original_text = fixed_text
            
            # Fix 3: Fix structure issues
            fixed_text = self._fix_yaml_structure(fixed_text)
            if fixed_text != original_text:
                warnings.append("Fixed YAML structure")
                original_text = fixed_text
            
            # Fix 4: Fix inconsistent indentation
            fixed_text = self._fix_yaml_indentation_properly(fixed_text)
            if fixed_text != original_text:
                warnings.append("Fixed inconsistent indentation")
            
            # Debug: Print the final fixed text
            print(f"DEBUG: Final fixed text: {repr(fixed_text)}")
            
            # Try to parse the fixed text
            if self.safe_load:
                data = yaml.safe_load(fixed_text)
            else:
                data = yaml.load(fixed_text, Loader=yaml.FullLoader)
            
            print(f"DEBUG: Successfully parsed: {data}")
            
            return ParseResult(
                data=data,
                success=True,
                warnings=warnings
            )
            
        except yaml.YAMLError as e:
            print(f"DEBUG: YAML parse error after fixes: {str(e)}")
            print(f"DEBUG: Fixed text that failed: {repr(fixed_text)}")
            return ParseResult(
                data=None,
                success=False,
                error=f"YAML auto-fix failed: {str(e)}"
            )
        except Exception as e:
            print(f"DEBUG: Unexpected error in auto-fix: {str(e)}")
            return ParseResult(
                data=None,
                success=False,
                error=f"YAML auto-fix error: {str(e)}"
            )
    
    def _fix_yaml_indentation(self, text: str) -> str:
        """Fix inconsistent YAML indentation"""
        lines = text.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip():  # Skip empty lines
                # Normalize indentation to 2 spaces
                indent_level = len(line) - len(line.lstrip())
                if indent_level > 0:
                    # Convert to 2-space indentation
                    normalized_indent = '  ' * (indent_level // 2)
                    fixed_lines.append(normalized_indent + line.lstrip())
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_yaml_structure(self, text: str) -> str:
        """Fix YAML structure issues"""
        lines = text.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if line.strip():
                # Check if this line has a colon
                if ':' in line and not line.strip().endswith(':'):
                    # This is a key-value pair
                    fixed_lines.append(line)
                elif ':' in line and line.strip().endswith(':'):
                    # This is a key with no value, add a default
                    fixed_lines.append(line.rstrip(':') + ': null')
                else:
                    # This might be a value without a key, try to fix
                    if i > 0 and ':' in lines[i-1]:
                        # Previous line had a colon, this might be a continuation
                        fixed_lines.append('  ' + line.strip())
                    else:
                        fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_missing_colons(self, text: str) -> str:
        """Fix missing colons in YAML"""
        # Add colons after keys that don't have them
        text = re.sub(r'^(\s*\w+)(\s+)(?!:)', r'\1:', text, flags=re.MULTILINE)
        return text
    
    def _fix_yaml_quotes(self, text: str) -> str:
        """Fix quote issues in YAML"""
        # Fix single quotes to double quotes for consistency
        text = re.sub(r"'([^']*)'", r'"\1"', text)
        return text
    
    def _fix_yaml_indentation_properly(self, text: str) -> str:
        """Fix YAML indentation more properly"""
        lines = text.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip():
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                
                # Normalize to 2-space indentation
                if leading_spaces > 0:
                    # Convert to proper 2-space indentation
                    indent_level = leading_spaces // 2
                    normalized_indent = '  ' * indent_level
                    fixed_lines.append(normalized_indent + line.lstrip())
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

class StructuredOutputParser:
    """Unified parser for structured LLM output"""
    
    def __init__(self):
        """Initialize the structured output parser"""
        self.json_parser = JSONParser()
        self.yaml_parser = YAMLParser()
    
    def parse_json(self, text: str, schema: Optional[Dict] = None) -> ParseResult:
        """Parse JSON from text"""
        return self.json_parser.parse(text, schema)
    
    def parse_yaml(self, text: str, schema: Optional[Dict] = None) -> ParseResult:
        """Parse YAML from text"""
        return self.yaml_parser.parse(text, schema)
    
    def auto_parse(self, text: str, preferred_format: str = "json") -> ParseResult:
        """
        Automatically detect and parse structured data
        
        Args:
            text: Text containing structured data
            preferred_format: Preferred format if both are detected
            
        Returns:
            ParseResult with parsed data
        """
        # Try JSON first if preferred
        if preferred_format.lower() == "json":
            json_result = self.parse_json(text)
            if json_result.success:
                return json_result
            
            yaml_result = self.parse_yaml(text)
            if yaml_result.success:
                return yaml_result
        
        # Try YAML first if preferred
        else:
            yaml_result = self.parse_yaml(text)
            if yaml_result.success:
                return yaml_result
            
            json_result = self.parse_json(text)
            if json_result.success:
                return json_result
        
        # If neither worked, try to extract and parse more aggressively
        try:
            # Try to extract JSON from markdown
            json_text = self._extract_json_from_text(text)
            if json_text:
                json_result = self.parse_json(json_text)
                if json_result.success:
                    return json_result
            
            # Try to extract YAML from markdown
            yaml_text = self._extract_yaml_from_text(text)
            if yaml_text:
                yaml_result = self.parse_yaml(yaml_text)
                if yaml_result.success:
                    return yaml_result
        except:
            pass
        
        # If still nothing worked, return the last error
        return ParseResult(
            data=None,
            success=False,
            error="Could not parse as JSON or YAML"
        )
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from text with markdown"""
        # Look for JSON in markdown code blocks
        json_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_yaml_from_text(self, text: str) -> str:
        """Extract YAML from text with markdown"""
        # Look for YAML in markdown code blocks
        yaml_patterns = [
            r'```yaml\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```'
        ]
        
        for pattern in yaml_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                return matches[0]
        
        return None
    
    def extract_structured_data(self, text: str, format_hint: Optional[str] = None) -> ParseResult:
        """
        Extract structured data from text with format detection
        
        Args:
            text: Text containing structured data
            format_hint: Hint about the format (json, yaml, auto)
            
        Returns:
            ParseResult with parsed data
        """
        if format_hint:
            if format_hint.lower() == "json":
                return self.parse_json(text)
            elif format_hint.lower() == "yaml":
                return self.parse_yaml(text)
        
        # Auto-detect format
        return self.auto_parse(text)

# Utility functions
def validate_json_schema(data: Any, schema: Dict) -> bool:
    """Validate data against JSON schema"""
    try:
        # Basic validation (can be enhanced with jsonschema library)
        if 'type' in schema:
            expected_type = schema['type']
            if expected_type == 'object' and not isinstance(data, dict):
                return False
            elif expected_type == 'array' and not isinstance(data, list):
                return False
        return True
    except:
        return False

def format_parse_error(error: str, text: str) -> str:
    """Format parse error with context"""
    return f"Parse Error: {error}\nText: {text[:100]}..."

def extract_json_from_text(text: str) -> Optional[str]:
    """Extract JSON string from text"""
    json_patterns = [
        r'```json\s*(.*?)\s*```',
        r'\{.*\}',
        r'\[.*\]'
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0]
    
    return None

def extract_yaml_from_text(text: str) -> Optional[str]:
    """Extract YAML string from text"""
    yaml_patterns = [
        r'```yaml\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```'
    ]
    
    for pattern in yaml_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0]
    
    return None

# Example usage and testing
if __name__ == "__main__":
    # Test JSON parsing
    json_text = '''
    ```json
    {
        "name": "John Doe",
        "age": 30,
        "skills": ["Python", "JavaScript", "SQL"]
    }
    ```
    '''
    
    parser = StructuredOutputParser()
    result = parser.parse_json(json_text)
    
    if result.success:
        print("✅ JSON parsed successfully:")
        print(json.dumps(result.data, indent=2))
    else:
        print(f"❌ JSON parse failed: {result.error}")
    
    # Test YAML parsing
    yaml_text = '''
    ```yaml
    name: Jane Doe
    age: 25
    skills:
      - Python
      - Machine Learning
      - Data Science
    ```
    '''
    
    result = parser.parse_yaml(yaml_text)
    
    if result.success:
        print("✅ YAML parsed successfully:")
        print(yaml.dump(result.data, default_flow_style=False))
    else:
        print(f"❌ YAML parse failed: {result.error}")