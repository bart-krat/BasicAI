"""
State Management for Agent Framework

This module provides state management for agents to persist information
across interactions and handle complex tasks that exceed context windows.

Comprehensive Pydantic validation enforced throughout.
"""

import json
import os
import pickle
from typing import Any, Dict, List, Optional, Union, Type, Generic, TypeVar
from pathlib import Path
from datetime import datetime
import asyncio
import hashlib

# Required Pydantic imports
from pydantic import BaseModel, Field, validator, ValidationError
from enum import Enum

class StateEntry(BaseModel):
    """A single state entry with comprehensive Pydantic validation"""
    key: str = Field(..., min_length=1, max_length=200, description="State key")
    value: Any = Field(..., description="State value")
    timestamp: datetime = Field(default_factory=datetime.now, description="Entry timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Entry metadata")
    
    @validator('key')
    def validate_key(cls, v):
        """Validate state key"""
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError("State key must contain only alphanumeric characters, underscores, hyphens, and dots")
        return v.lower().strip()
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata"""
        if not isinstance(v, dict):
            raise ValueError("Metadata must be a dictionary")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        validate_assignment = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateEntry':
        """Create from dictionary"""
        return cls(**data)

class StateSchema(BaseModel):
    """Pydantic-based state schema definition"""
    required_keys: List[str] = Field(default_factory=list, description="Required state keys")
    key_types: Dict[str, Any] = Field(default_factory=dict, description="Expected types for keys")
    validation_rules: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Custom validation rules")
    
    @validator('required_keys')
    def validate_required_keys(cls, v):
        """Validate required keys"""
        return [key.lower().strip() for key in v if key.strip()]
    
    def validate_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate state against schema"""
        errors = []
        warnings = []
        
        # Check required keys
        missing_keys = [key for key in self.required_keys if key not in state]
        if missing_keys:
            errors.append(f"Missing required keys: {missing_keys}")
        
        # Validate each key's type and rules
        for key, value in state.items():
            if key in self.key_types:
                expected_type = self.key_types[key].get('type')
                if expected_type and not self._check_type(value, expected_type):
                    warnings.append(f"Key '{key}' expected {expected_type}, got {type(value).__name__}")
            
            # Apply custom validation rules
            if key in self.validation_rules:
                rule_result = self._apply_validation_rule(key, value, self.validation_rules[key])
                if not rule_result['valid']:
                    errors.append(f"Validation failed for '{key}': {rule_result['error']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_map = {
            'string': str,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'datetime': datetime
        }
        return isinstance(value, type_map.get(expected_type, type(None)))
    
    def _apply_validation_rule(self, key: str, value: Any, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom validation rule"""
        try:
            if 'min_length' in rule and isinstance(value, str):
                if len(value) < rule['min_length']:
                    return {'valid': False, 'error': f"Minimum length {rule['min_length']} required"}
            
            if 'max_length' in rule and isinstance(value, str):
                if len(value) > rule['max_length']:
                    return {'valid': False, 'error': f"Maximum length {rule['max_length']} exceeded"}
            
            if 'min_value' in rule and isinstance(value, (int, float)):
                if value < rule['min_value']:
                    return {'valid': False, 'error': f"Minimum value {rule['min_value']} required"}
            
            if 'max_value' in rule and isinstance(value, (int, float)):
                if value > rule['max_value']:
                    return {'valid': False, 'error': f"Maximum value {rule['max_value']} exceeded"}
            
            return {'valid': True, 'error': None}
        except Exception as e:
            return {'valid': False, 'error': f"Validation error: {str(e)}"}

class StateManager(BaseModel):
    """
    State management for agents with comprehensive Pydantic validation
    
    Provides:
    - In-memory state storage with validation
    - File-based persistence
    - Session management
    - Comprehensive key-value operations
    - Required Pydantic validation
    """
    
    session_id: str = Field(..., description="Unique session identifier")
    state_dir: Path = Field(..., description="Directory for persistent storage")
    auto_save: bool = Field(default=True, description="Auto-save to disk")
    max_memory_entries: int = Field(default=1000, ge=1, le=10000, description="Maximum memory entries")
    state_schema: Optional[StateSchema] = Field(None, description="State validation schema")
    _state: Dict[str, StateEntry] = Field(default_factory=dict, exclude=True)
    _state_file: Path = Field(exclude=True)
    _lock: Optional[asyncio.Lock] = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True  # Allow Path and asyncio.Lock
    
    def __init__(self, 
                 session_id: Optional[str] = None,
                 state_dir: Optional[str] = None,
                 auto_save: bool = True,
                 max_memory_entries: int = 1000,
                 state_schema: Optional[StateSchema] = None,
                 **kwargs):
        """
        Initialize state manager with Pydantic validation
        
        Args:
            session_id: Unique session identifier (auto-generated if None)
            state_dir: Directory for persistent storage (default: ./agent_state)
            auto_save: Whether to automatically save to disk
            max_memory_entries: Maximum entries to keep in memory
            state_schema: Optional state validation schema
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = self._generate_session_id()
        
        # Setup state directory
        state_path = Path(state_dir or "./agent_state")
        state_path.mkdir(exist_ok=True)
        
        # Initialize Pydantic model
        super().__init__(
            session_id=session_id,
            state_dir=state_path,
            auto_save=auto_save,
            max_memory_entries=max_memory_entries,
            state_schema=state_schema,
            **kwargs
        )
        
        # Initialize private attributes
        self._state = {}
        self._state_file = self.state_dir / f"state_{self.session_id}.json"
        self._lock = asyncio.Lock()
        
        # Load existing state if available
        self._load_state()
        
        print(f"📋 StateManager initialized with Pydantic validation")
        if self.state_schema:
            print(f"📋 State schema validation enabled")

    def define(self, state_schema: Dict[str, Any]) -> None:
        """
        Define the complete state schema at initialization
        
        Args:
            state_schema: Dictionary defining all state variables and their initial values
        """
        for key, value in state_schema.items():
            entry = StateEntry(
                key=key,
                value=value,
                timestamp=datetime.now(),
                metadata={"defined_at_init": True}
            )
            self._state[key] = entry
        
        print(f"📋 Defined {len(state_schema)} state variables")
        
        # Save the defined state
        if self.auto_save:
            asyncio.create_task(self._save_state())
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _load_state(self):
        """Load state from disk"""
        if self._state_file.exists():
            try:
                with open(self._state_file, 'r') as f:
                    data = json.load(f)
                    for entry_data in data.get('entries', []):
                        entry = StateEntry.from_dict(entry_data)
                        self._state[entry.key] = entry
                print(f"📁 Loaded {len(self._state)} state entries from {self._state_file}")
            except Exception as e:
                print(f"⚠️ Failed to load state: {e}")
    
    async def _save_state(self):
        """Save state to disk"""
        if not self.auto_save:
            return
            
        async with self._lock:
            try:
                data = {
                    'session_id': self.session_id,
                    'last_saved': datetime.now().isoformat(),
                    'entries': [entry.to_dict() for entry in self._state.values()]
                }
                
                # Write to temporary file first, then rename (atomic operation)
                temp_file = self._state_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                temp_file.rename(self._state_file)
                print(f"💾 Saved {len(self._state)} state entries to {self._state_file}")
                
            except Exception as e:
                print(f"⚠️ Failed to save state: {e}")
    
    # Core state operations
    async def set(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Set a state value with comprehensive Pydantic validation
        
        Args:
            key: State key
            value: State value
            metadata: Optional metadata
            
        Returns:
            True if successful, False if validation failed
        """
        try:
            # Create state entry with Pydantic validation
            entry = StateEntry(
                key=key,
                value=value,
                metadata=metadata or {}
            )
            
            # Validate against state schema if provided
            if self.state_schema:
                temp_state = {**await self.get_all(), key: value}
                validation_result = self.state_schema.validate_state(temp_state)
                
                if not validation_result['valid']:
                    print(f"❌ State validation failed for key '{key}': {validation_result['errors']}")
                    return False
                
                if validation_result['warnings']:
                    print(f"⚠️ State validation warnings for key '{key}': {validation_result['warnings']}")
            
            # Store validated entry
            async with self._lock:
                self._state[key] = entry
                
                # Limit memory usage
                if len(self._state) > self.max_memory_entries:
                    sorted_entries = sorted(self._state.items(), key=lambda x: x[1].timestamp)
                    for old_key, _ in sorted_entries[:len(self._state) - self.max_memory_entries]:
                        del self._state[old_key]
            
            if self.auto_save:
                await self._save_state()
            
            return True
            
        except ValidationError as e:
            print(f"❌ Pydantic validation failed for key '{key}': {e}")
            return False
        except Exception as e:
            print(f"❌ Error setting state for key '{key}': {e}")
            return False
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get a state value
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        async with self._lock:
            entry = self._state.get(key)
            return entry.value if entry else default
    
    async def has(self, key: str) -> bool:
        """Check if key exists in state"""
        async with self._lock:
            return key in self._state
    
    async def delete(self, key: str) -> bool:
        """
        Delete a state value
        
        Args:
            key: State key
            
        Returns:
            True if key was deleted, False if not found
        """
        async with self._lock:
            if key in self._state:
                del self._state[key]
                if self.auto_save:
                    await self._save_state()
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all state"""
        async with self._lock:
            self._state.clear()
            if self.auto_save:
                await self._save_state()
    
    # Advanced operations
    async def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple state values at once
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        async with self._lock:
            for key, value in updates.items():
                entry = StateEntry(
                    key=key,
                    value=value,
                    timestamp=datetime.now()
                )
                self._state[key] = entry
        
        if self.auto_save:
            await self._save_state()
    
    async def get_all(self) -> Dict[str, Any]:
        """Get all state values as a dictionary"""
        async with self._lock:
            return {key: entry.value for key, entry in self._state.items()}
    
    async def keys(self) -> List[str]:
        """Get all state keys"""
        async with self._lock:
            return list(self._state.keys())
    
    async def search(self, pattern: str) -> Dict[str, Any]:
        """
        Search for keys matching a pattern
        
        Args:
            pattern: Pattern to search for (simple substring match)
            
        Returns:
            Dictionary of matching key-value pairs
        """
        async with self._lock:
            matches = {}
            for key, entry in self._state.items():
                if pattern.lower() in key.lower():
                    matches[key] = entry.value
            return matches
    
    # Context management
    async def get_context(self, max_entries: int = 10) -> str:
        """
        Get recent state as context string for LLM
        
        Args:
            max_entries: Maximum number of recent entries to include
            
        Returns:
            Formatted context string
        """
        async with self._lock:
            # Sort by timestamp, get most recent
            sorted_entries = sorted(
                self._state.items(), 
                key=lambda x: x[1].timestamp, 
                reverse=True
            )[:max_entries]
            
            if not sorted_entries:
                return "No previous context available."
            
            context_lines = ["Previous context:"]
            for key, entry in sorted_entries:
                timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                value_str = str(entry.value)[:200]  # Truncate long values
                context_lines.append(f"- {key}: {value_str} ({timestamp})")
            
            return "\n".join(context_lines)
    
    # File operations
    async def save_to_file(self, filepath: str) -> None:
        """Save state to a specific file"""
        async with self._lock:
            data = {
                'session_id': self.session_id,
                'saved_at': datetime.now().isoformat(),
                'entries': [entry.to_dict() for entry in self._state.values()]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
    
    async def load_from_file(self, filepath: str) -> None:
        """Load state from a specific file"""
        async with self._lock:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self._state.clear()
                for entry_data in data.get('entries', []):
                    entry = StateEntry.from_dict(entry_data)
                    self._state[entry.key] = entry
    
    # Utility methods
    def get_info(self) -> Dict[str, Any]:
        """Get information about the state manager"""
        return {
            'session_id': self.session_id,
            'state_dir': str(self.state_dir),
            'total_entries': len(self._state),
            'auto_save': self.auto_save,
            'max_memory_entries': self.max_memory_entries,
            'state_file': str(self._state_file),
            'pydantic_enforced': True,
            'validation_enabled': self.state_schema is not None,
            'schema_required_keys': self.state_schema.required_keys if self.state_schema else []
        }
    
    async def cleanup_old_entries(self, days: int = 7) -> int:
        """
        Remove entries older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of entries removed
        """
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        
        async with self._lock:
            old_keys = []
            for key, entry in self._state.items():
                if entry.timestamp < cutoff_date:
                    old_keys.append(key)
            
            for key in old_keys:
                del self._state[key]
            
            if old_keys and self.auto_save:
                await self._save_state()
            
            return len(old_keys)

# Convenience functions
def create_state_manager(session_id: Optional[str] = None, 
                        state_dir: Optional[str] = None,
                        state_schema: Optional[StateSchema] = None) -> StateManager:
    """Create a new state manager instance with Pydantic validation"""
    return StateManager(
        session_id=session_id, 
        state_dir=state_dir,
        state_schema=state_schema
    )

def get_or_create_state_manager(session_id: str, 
                               state_dir: Optional[str] = None,
                               state_schema: Optional[StateSchema] = None) -> StateManager:
    """Get existing state manager or create new one with Pydantic validation"""
    return StateManager(
        session_id=session_id, 
        state_dir=state_dir,
        state_schema=state_schema
    )

# Example usage
async def example_usage():
    """Example of how to use the state management with Pydantic validation"""
    
    # Create state schema
    schema = StateSchema(
        required_keys=["user_name", "task_progress"],
        key_types={
            "user_name": {"type": "string"},
            "task_progress": {"type": "object"},
            "last_query": {"type": "string"}
        },
        validation_rules={
            "user_name": {"min_length": 1, "max_length": 50},
            "task_progress": {"min_value": 0, "max_value": 100}
        }
    )
    
    # Create state manager with schema
    state = create_state_manager(
        session_id="example_session",
        state_schema=schema
    )
    
    # Basic operations with validation
    success1 = await state.set("user_name", "Alice")
    success2 = await state.set("task_progress", {"step": 1, "total": 5})
    success3 = await state.set("last_query", "What is machine learning?")
    
    print(f"Set operations: {success1}, {success2}, {success3}")
    
    # Get values
    name = await state.get("user_name")
    progress = await state.get("task_progress")
    print(f"User: {name}, Progress: {progress}")
    
    # Update multiple values
    await state.update({
        "task_progress": {"step": 2, "total": 5},
        "last_query": "Explain neural networks"
    })
    
    # Get context for LLM
    context = await state.get_context(max_entries=5)
    print(f"Context: {context}")
    
    # Search
    results = await state.search("task")
    print(f"Task-related entries: {results}")
    
    # Get info
    info = state.get_info()
    print(f"State info: {info}")
    
    # Example of validation failure
    print("\nTesting validation:")
    invalid_result = await state.set("user_name", "")  # Empty string should fail
    print(f"Invalid set result: {invalid_result}")
    
    # Example of custom validation
    class CustomStateSchema(StateSchema):
        @validator('required_keys')
        def validate_required_keys(cls, v):
            if len(v) > 10:
                raise ValueError("Too many required keys")
            return v
    
    custom_schema = CustomStateSchema(
        required_keys=["user_name", "task_progress", "last_query"]
    )
    
    custom_state = create_state_manager(
        session_id="custom_session",
        state_schema=custom_schema
    )
    
    print(f"Custom state manager created with {len(custom_schema.required_keys)} required keys")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
