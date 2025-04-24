"""
R2R documents module.

This module provides functionality for managing documents in R2R,
including creating documents and adding them to collections.
"""

import logging
from typing import Dict, Any, List, Optional
from .client import r2r_client
from .errors import handle_r2r_error, R2RError, create_success_response

log = logging.getLogger(__name__)

@handle_r2r_error
async def handle_create_document(
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new document in R2R.
    
    Args:
        content: The document content
        metadata: Optional metadata for the document
        
    Returns:
        Dictionary containing the created document details
    """
    try:
        response = await r2r_client.create_document(content, metadata)
        
        if not response.get("success"):
            error = response.get("error", "Failed to create document")
            raise R2RError(error)
            
        return create_success_response(response.get("data"))
        
    except Exception as e:
        log.error(f"Error creating document: {str(e)}")
        raise R2RError(f"Error creating document: {str(e)}")

@handle_r2r_error
async def handle_add_document_to_collection(
    document_id: str,
    collection_id: str
) -> Dict[str, Any]:
    """
    Add a document to a collection in R2R.
    
    Args:
        document_id: ID of the document to add
        collection_id: ID of the collection to add the document to
        
    Returns:
        Dictionary containing the operation result
    """
    try:
        response = await r2r_client.add_document_to_collection(document_id, collection_id)
        
        if not response.get("success"):
            error = response.get("error", "Failed to add document to collection")
            raise R2RError(error)
            
        return create_success_response(response.get("data"))
        
    except Exception as e:
        log.error(f"Error adding document to collection: {str(e)}")
        raise R2RError(f"Error adding document to collection: {str(e)}")

@handle_r2r_error
async def handle_add_document_to_collections(
    document_id: str,
    collection_ids: List[str]
) -> Dict[str, Any]:
    """Add a document to one or more collections.
    
    Args:
        document_id: ID of document to add
        collection_ids: IDs of collections to add to
        
    Returns:
        Operation result
    """
    if not document_id:
        raise R2RError("Document ID is required")
    if not collection_ids:
        raise R2RError("Collection IDs are required")
        
    # Add document to each collection
    for collection_id in collection_ids:
        response = await r2r_client.add_document_to_collection(collection_id, document_id)
        if not response.get("success"):
            error = response.get("error")
            if error:
                raise R2RError(error)
            raise R2RError("Failed to add document to collection")
        
    return {
        "success": True,
        "document_id": document_id,
        "collection_ids": collection_ids
    } 