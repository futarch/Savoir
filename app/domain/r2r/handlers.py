import logging
from typing import Dict, Any, List, Optional
from .client import r2r_client
from .errors import handle_r2r_error, R2RError
import time
import json

log = logging.getLogger(__name__)

@handle_r2r_error
async def handle_create_collection(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Handle creating a new collection."""
    if not name:
        raise R2RError("Collection name is required")
        
    response = await r2r_client.create_collection(name, description)
    
    if not response or "error" in response:
        error = response.get("error", "Unknown error") if response else "No response"
        raise R2RError(f"Failed to create collection: {error}")
        
    return {
        "success": True,
        "data": response
    }

@handle_r2r_error
async def handle_create_document(raw_text: str) -> Dict[str, Any]:
    """Handle document creation."""
    if not raw_text or not raw_text.strip():
        raise R2RError("Document content cannot be empty")
        
    response = await r2r_client.create_document(raw_text)
    
    if not response or "error" in response:
        error = response.get("error", "Unknown error") if response else "No response"
        raise R2RError(f"Failed to create document: {error}")
        
    return {
        "success": True,
        "data": response
    }

@handle_r2r_error
async def handle_add_document_to_collection(document_id: str, collection_id: str) -> Dict[str, Any]:
    """Handle adding document to collection."""
    if not document_id:
        raise R2RError("Document ID is required")
    if not collection_id:
        raise R2RError("Collection ID is required")
        
    response = await r2r_client.add_document_to_collection(collection_id, document_id)
    
    if not response or "error" in response:
        error = response.get("error", "Unknown error") if response else "No response"
        raise R2RError(f"Failed to add document to collection: {error}")
        
    return {
        "success": True,
        "data": response
    }

@handle_r2r_error
async def handle_list_user_collections(offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """Handle listing collections."""
    response = await r2r_client.collections(offset=offset, limit=limit)
    
    if not response or "error" in response:
        error = response.get("error", "Unknown error") if response else "No response"
        raise R2RError(f"Failed to list collections: {error}")
        
    return {
        "success": True,
        "data": response
    }

@handle_r2r_error
async def handle_search(
    query: str,
    collection_id: Optional[str] = None,
    max_chunks: Optional[int] = None,
    semantic: Optional[bool] = None
) -> Dict[str, Any]:
    """Handle search operation."""
    if not query:
        raise R2RError("Search query is required")
        
    response = await r2r_client.search(
        query,
        collection_id=collection_id,
        max_chunks=max_chunks,
        semantic=semantic
    )
    
    if not response or "error" in response:
        error = response.get("error", "Unknown error") if response else "No response"
        raise R2RError(f"Failed to perform search: {error}")
        
    return {
        "success": True,
        "data": response
    }

@handle_r2r_error
async def handle_rag(
    query: str,
    collection_id: Optional[str] = None,
    max_chunks: Optional[int] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> Dict[str, Any]:
    """Handle RAG operation."""
    if not query:
        raise R2RError("Query is required")
        
    response = await r2r_client.rag(
        query,
        collection_id=collection_id,
        max_chunks=max_chunks,
        model=model,
        temperature=temperature
    )
    
    if not response or "error" in response:
        error = response.get("error", "Unknown error") if response else "No response"
        raise R2RError(f"Failed to perform RAG: {error}")
        
    return {
        "success": True,
        "data": response
    } 