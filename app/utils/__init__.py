# app/utils/__init__.py

from .tools import (
    create_tool_node_with_fallback,
    handle_tool_error,
    part_3_safe_tools,
    part_3_sensitive_tools,
    sensitive_tool_names
)

from .database import get_db

def _print_event(event: dict, _printed: set, max_length: int = 1500) -> None:
    """Print event content if not already printed"""
    if event.get("messages"):
        content = event["messages"][-1].content
        if content not in _printed:
            if len(content) > max_length:
                content = content[:max_length] + "..."
            print(content)
            _printed.add(content)

__all__ = [
    # Tool utilities
    'create_tool_node_with_fallback',
    'handle_tool_error',
    'part_3_safe_tools',
    'part_3_sensitive_tools',
    'sensitive_tool_names',
    
    # Database utilities
    'get_db',
    
    # Event handling
    '_print_event'
]