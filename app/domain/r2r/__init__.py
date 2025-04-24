"""
R2R (Retrieval) module initialization.

This module provides functionality for interacting with the R2R API,
including collection management, document operations, and search capabilities.
"""

from .search import handle_search_with_names, handle_rag_with_names
from .collections import handle_create_collection, handle_list_user_collections
from .documents import handle_create_document, handle_add_document_to_collection
from .client import r2r_client

__all__ = [
    'handle_create_collection',
    'handle_list_user_collections',
    'handle_create_document',
    'handle_add_document_to_collection',
    'handle_search_with_names',
    'handle_rag_with_names',
    'r2r_client'
] 