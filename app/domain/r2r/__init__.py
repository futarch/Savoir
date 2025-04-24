"""
R2R (Retrieval) module initialization.

This module provides functionality for interacting with the R2R API,
including collection management, document operations, and search capabilities.
"""

from .handlers import (
    handle_create_collection,
    handle_create_document,
    handle_add_document_to_collection,
    handle_search,
    handle_rag
)
from .collections import handle_list_user_collections

__all__ = [
    'handle_create_collection',
    'handle_list_user_collections',
    'handle_create_document',
    'handle_add_document_to_collection',
    'handle_search',
    'handle_rag'
] 