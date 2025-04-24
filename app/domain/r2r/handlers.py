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
    log.info(f"Creating collection: {name} with description: {description}")
    
    try:
        response = await r2r_client.create_collection(name, description)
        log.info(f"Collection creation response: {response}")
        
        if not response or "results" not in response:
            log.error(f"Invalid response format from R2R API: {response}")
            raise R2RError("Invalid response format from R2R API")
            
        collection_data = response["results"]
        if not collection_data or "id" not in collection_data:
            log.error(f"No collection ID in response: {collection_data}")
            raise R2RError("No collection ID in response")
            
        log.info(f"Successfully created collection with ID: {collection_data['id']}")
        return {
            "success": True,
            "data": {
                "collection_id": collection_data["id"],
                "name": collection_data["name"],
                "description": collection_data.get("description"),
                "status": collection_data.get("graph_cluster_status", "unknown")
            }
        }
    except Exception as e:
        log.error(f"Failed to create collection: {str(e)}")
        raise R2RError(f"Failed to create collection: {str(e)}")

@handle_r2r_error
async def handle_create_document(raw_text: str, collection_id: str) -> Dict[str, Any]:
    """Handle document creation.
    
    Args:
        raw_text: The text content to be uploaded
        collection_id: ID of the collection to add the document to
        
    Returns:
        Dict containing success status and document info
    """
    try:
        log.info(f"Creating document with content length: {len(raw_text)} for collection: {collection_id}")
        
        # Ensure raw_text is not empty
        if not raw_text or not raw_text.strip():
            log.error("Empty raw_text provided")
            raise R2RError("Document content cannot be empty")
            
        # Ensure collection_id is provided
        if not collection_id:
            log.error("No collection_id provided")
            raise R2RError("Collection ID is required")
            
        # Create the document
        response = await r2r_client.create_document(raw_text)
        
        if not response:
            log.error("No response received from R2R API")
            raise R2RError("Failed to create document: No response received")
            
        if not isinstance(response, dict):
            log.error(f"Invalid response format: {response}")
            raise R2RError("Failed to create document: Invalid response format")
            
        # Check for error in response
        if "error" in response:
            error = response.get("error", "Unknown error")
            log.error(f"Error creating document: {error}")
            raise R2RError(f"Failed to create document: {error}")
            
        # Check for document_id in response
        if "document_id" not in response:
            log.error(f"No document_id in response: {response}")
            raise R2RError("Failed to create document: No document ID in response")
            
        document_id = response["document_id"]
        log.info(f"Successfully created document with ID: {document_id}")
        
        # Add document to collection
        add_response = await r2r_client.add_document_to_collection(collection_id, document_id)
        if not add_response or "error" in add_response:
            error = add_response.get("error", "Unknown error") if add_response else "No response"
            log.error(f"Error adding document to collection: {error}")
            raise R2RError(f"Failed to add document to collection: {error}")
            
        log.info(f"Successfully added document {document_id} to collection {collection_id}")
        
        return {
            "success": True,
            "data": {
                "document_id": document_id,
                "collection_id": collection_id
            }
        }
        
    except Exception as e:
        log.error(f"Error creating document: {str(e)}")
        raise R2RError(f"Failed to create document: {str(e)}")

@handle_r2r_error
async def handle_add_document_to_collection(document_id: str, collection_id: str) -> Dict[str, Any]:
    """Handle adding document to collection.
    
    Args:
        document_id: ID of document to add
        collection_id: ID of collection to add the document to
        
    Returns:
        Operation result
    """
    if not document_id:
        raise R2RError("Document ID is required")
    if not collection_id:
        raise R2RError("Collection ID is required")
        
    log.info(f"Adding document {document_id} to collection: {collection_id}")
    
    response = await r2r_client.add_document_to_collection(collection_id, document_id)
    log.info(f"Add document response: {response}")
    
    if not response or "results" not in response:
        log.error(f"Invalid response format from R2R API: {response}")
        raise R2RError(f"Invalid response format when adding to collection {collection_id}")
    
    log.info(f"Successfully added document {document_id} to collection: {collection_id}")
    return {
        "success": True,
        "data": {
            "document_id": document_id,
            "collection_id": collection_id,
            "message": response.get("results", {}).get("message", "Document successfully assigned to the collection")
        }
    }

@handle_r2r_error
async def handle_list_user_collections(offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """Handle listing collections.
    
    Args:
        offset: Number of objects to skip (default: 0)
        limit: Maximum number of objects to return (default: 100, max: 1000)
        
    Returns:
        Dict containing collections data in OpenAI API format
    """
    log.info(f"Listing user collections with offset={offset}, limit={limit}")
    response = await r2r_client.collections(offset=offset, limit=limit)
    log.info(f"List collections response: {response}")
    
    # Check if the response has the expected format
    if not response or "results" not in response:
        log.error(f"Invalid response format from R2R API: {response}")
        raise R2RError("Invalid response format from R2R API")
        
    collections = response["results"]
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
                        "total_entries": response.get("total_entries", len(collections))
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

@handle_r2r_error
async def handle_search(
    query: str,
    collection_id: Optional[str] = None,
    max_chunks: Optional[int] = None,
    semantic: Optional[bool] = None
) -> Dict[str, Any]:
    """Handle search operation."""
    log.info(f"Searching with query: {query}, collection_id: {collection_id}, max_chunks: {max_chunks}, semantic: {semantic}")
    response = await r2r_client.search(
        query,
        collection_id=collection_id,
        max_chunks=max_chunks,
        semantic=semantic
    )
    log.info(f"Search response: {response}")
    
    if not response or "results" not in response:
        log.error(f"Invalid response format from R2R API: {response}")
        raise R2RError("Invalid response format from R2R API")
        
    log.info(f"Successfully completed search with {len(response['results'].get('chunks', []))} chunks")
    return {
        "success": True,
        "data": response["results"]
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
    log.info(f"RAG with query: {query}, collection_id: {collection_id}, max_chunks: {max_chunks}, model: {model}, temperature: {temperature}")
    response = await r2r_client.rag(
        query,
        collection_id=collection_id,
        max_chunks=max_chunks,
        model=model,
        temperature=temperature
    )
    log.info(f"RAG response: {response}")
    
    if not response or "results" not in response:
        log.error(f"Invalid response format from R2R API: {response}")
        raise R2RError("Invalid response format from R2R API")
        
    log.info(f"Successfully completed RAG operation")
    return {
        "success": True,
        "data": response["results"]
    } 