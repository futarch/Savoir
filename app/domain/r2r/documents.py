import logging
from typing import Dict, Any, List, Optional
from .client import r2r_client
from .errors import handle_r2r_error, R2RError

log = logging.getLogger(__name__)

@handle_r2r_error
async def handle_create_document(
    raw_text: str
) -> Dict[str, Any]:
    """Create a new document in R2R.
    
    Args:
        raw_text: Document content
        
    Returns:
        Created document info
    """
    if not raw_text:
        raise R2RError("Document content is required")
        
    response = await r2r_client.create_document(raw_text)
    
    if not response.get("success"):
        error = response.get("error")
        if error:
            raise R2RError(error)
        raise R2RError("Failed to create document")
        
    document_id = response.get("data", {}).get("id")
    if not document_id:
        raise R2RError("No document ID in response")
        
    return {
        "success": True,
        "document_id": document_id,
        "raw_text": raw_text
    }

@handle_r2r_error
async def handle_add_document_to_collection(
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