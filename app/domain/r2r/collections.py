"""
R2R collections module.

This module provides functionality for managing collections in R2R,
including creating, listing, and managing collections.
"""

from asyncio import TimeoutError
import asyncio
import logging
from typing import Dict, Any, Optional, List
from .client import r2r_client
from .utils import wait_for_collection_ready
from .errors import handle_r2r_error, R2RError, create_success_response
import time
import json

log = logging.getLogger(__name__)

@handle_r2r_error
async def handle_create_collection(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new collection in R2R.
    
    Args:
        name: Name of the collection
        description: Optional description of the collection
        
    Returns:
        Dictionary containing the created collection details
    """
    try:
        response = await r2r_client.create_collection(name, description)
        
        if not response.get("success"):
            raise R2RError(response.get("error", "Failed to create collection"))
            
        return create_success_response(response.get("data"))
        
    except Exception as e:
        log.error(f"Error creating collection: {str(e)}")
        raise R2RError(f"Error creating collection: {str(e)}")

@handle_r2r_error
async def handle_list_user_collections(offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    List collections for the current user.
    
    Args:
        offset: Number of collections to skip
        limit: Maximum number of collections to return
        
    Returns:
        Dictionary containing the list of collections
    """
    try:
        response = await r2r_client.collections(offset=offset, limit=limit)
        
        if not response.get("success"):
            raise R2RError(response.get("error", "Failed to list collections"))
            
        return create_success_response(response.get("data"))
        
    except Exception as e:
        log.error(f"Error listing collections: {str(e)}")
        raise R2RError(f"Error listing collections: {str(e)}") 