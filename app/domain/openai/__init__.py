"""
OpenAI module initialization.

This module provides functionality for interacting with the OpenAI API,
including assistant creation, message handling, and tool execution.
"""

from .assistant import run
from .tools import tools, function_handlers

__all__ = ['run', 'tools', 'function_handlers'] 