from asyncio import TimeoutError
import asyncio
import logging
from typing import Dict, Any, Optional
from .client import r2r_client
from .utils import wait_for_collection_ready
from .errors import handle_r2r_error, R2RError
import time
import json

log = logging.getLogger(__name__)

@handle_r2r_error
async def handle_create_collection(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Handle the create_collection function call"""
    log.info(f"Creating collection with name: {name}, description: {description}")
    
    # Create collection
    collection_result = await r2r_client.create_collection(name=name, description=description)
    log.info(f"Collection result: {collection_result}")
    
    if not collection_result.get("success"):
        error = collection_result.get("error")
        if error:
            raise R2RError(error)
        raise R2RError("Failed to create collection")
        
    collection_id = collection_result.get("data", {}).get("id")
    if not collection_id:
        raise R2RError("No collection ID in response")
        
    # Wait for collection to be ready
    is_ready = await wait_for_collection_ready(collection_id)
    if not is_ready:
        raise R2RError("Collection creation timed out")
        
    return {
        "success": True,
        "collection_id": collection_id,
        "name": name,
        "description": description
    }

@handle_r2r_error
async def handle_list_user_collections(offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """Handle the list_user_collections function call
    
    Args:
        offset: Number of objects to skip (default: 0)
        limit: Maximum number of objects to return (default: 100, max: 1000)
        
    Returns:
        Dict containing collections data in OpenAI API format
    """
    # Use the R2R client's built-in method to list collections
    collections_result = await r2r_client.collections(offset=offset, limit=limit)
    
    if not collections_result or "results" not in collections_result:
        log.error(f"Invalid response format from R2R API: {collections_result}")
        raise R2RError("Invalid response format from R2R API")
    
    collections = collections_result["results"]
    if not isinstance(collections, list):
        log.error(f"Collections is not a list: {collections}")
        raise R2RError("Invalid collections format")
    
    # Format the collections for the response
    formatted_collections = []
    for collection in collections:
        formatted_collections.append({
            "id": collection.get("id"),
            "name": collection.get("name"),
            "description": collection.get("description"),
            "created_at": collection.get("created_at"),
            "updated_at": collection.get("updated_at"),
            "document_count": collection.get("document_count", 0),
            "user_count": collection.get("user_count", 0),
            "owner_id": collection.get("owner_id"),
            "graph_cluster_status": collection.get("graph_cluster_status"),
            "graph_sync_status": collection.get("graph_sync_status")
        })
    
    log.info(f"Successfully retrieved {len(collections)} collections")
    
    # Return data in OpenAI API format
    return {
        "id": "r2r-collections-response",
        "object": "r2r.collections",
        "created": int(time.time()),
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "collections": formatted_collections,
                        "total_entries": collections_result.get("total_entries", len(collections))
                    })
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    } 