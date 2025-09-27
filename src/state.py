"""
State Management for Agent Framework

This module provides state management for agents to persist information
across interactions and handle complex tasks that exceed context windows.
"""

import json
import os
import pickle
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
import asyncio
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class StateEntry:
    """A single state entry with metadata"""
    key: str
    value: Any
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'key': self.key,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateEntry':
        """Create from dictionary"""
        return cls(
            key=data['key'],
            value=data['value'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata')
        )

class StateManager:
    """
    State management for agents
    
    Provides:
    - In-memory state storage
    - File-based persistence
    - Session management
    - Simple key-value operations
    """
    
    def __init__(self, 
                 session_id: Optional[str] = None,
                 state_dir: Optional[str] = None,
                 auto_save: bool = True,
                 max_memory_entries: int = 1000):
        """
        Initialize state manager
        
        Args:
            session_id: Unique session identifier (auto-generated if None)
            state_dir: Directory for persistent storage (default: ./agent_state)
            auto_save: Whether to automatically save to disk
            max_memory_entries: Maximum entries to keep in memory
        """
        self.state_dir = Path(state_dir or "./agent_state")
        self.state_dir.mkdir(exist_ok=True)
        
        self.session_id = session_id or self._generate_session_id()
        self.auto_save = auto_save
        self.max_memory_entries = max_memory_entries
        
        # In-memory state storage
        self._state: Dict[str, StateEntry] = {}
        self._state_file = self.state_dir / f"state_{self.session_id}.json"
        self._lock = asyncio.Lock()
        
        # Load existing state if available
        self._load_state()

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
    async def set(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Set a state value
        
        Args:
            key: State key
            value: State value (must be JSON serializable)
            metadata: Optional metadata
        """
        async with self._lock:
            entry = StateEntry(
                key=key,
                value=value,
                timestamp=datetime.now(),
                metadata=metadata
            )
            self._state[key] = entry
            
            # Limit memory usage
            if len(self._state) > self.max_memory_entries:
                # Remove oldest entries
                sorted_entries = sorted(self._state.items(), key=lambda x: x[1].timestamp)
                for old_key, _ in sorted_entries[:len(self._state) - self.max_memory_entries]:
                    del self._state[old_key]
        
        if self.auto_save:
            await self._save_state()
    
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
        """Get information about the state"""
        return {
            'session_id': self.session_id,
            'state_dir': str(self.state_dir),
            'total_entries': len(self._state),
            'auto_save': self.auto_save,
            'state_file': str(self._state_file)
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
async def create_state_manager(session_id: Optional[str] = None, 
                              state_dir: Optional[str] = None) -> StateManager:
    """Create a new state manager instance"""
    return StateManager(session_id=session_id, state_dir=state_dir)

async def get_or_create_state_manager(session_id: str, 
                                     state_dir: Optional[str] = None) -> StateManager:
    """Get existing state manager or create new one"""
    return StateManager(session_id=session_id, state_dir=state_dir)

# Example usage
async def example_usage():
    """Example of how to use the state management"""
    
    # Create state manager
    state = await create_state_manager(session_id="example_session")
    
    # Basic operations
    await state.set("user_name", "Alice")
    await state.set("task_progress", {"step": 1, "total": 5})
    await state.set("last_query", "What is machine learning?")
    
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

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
