import logging
from typing import List, Dict, Any, Optional
from .client import r2r_client
from .errors import create_success_response, SearchError, handle_r2r_error

log = logging.getLogger(__name__)

async def _get_collection_id(collection_name: Optional[str]) -> Optional[str]:
    """
    Get collection ID from a collection name.
    
    Args:
        collection_name: Name of the collection to find
        
    Returns:
        Collection ID if found, None otherwise
    """
    if not collection_name:
        return None
        
    try:
        collections = await r2r_client.collections()
        if not collections.get("success"):
            return None
            
        for collection in collections.get("data", []):
            if collection.get("name") == collection_name:
                return str(collection.get("id"))
                
        log.warning(f"Collection name '{collection_name}' not found")
        return None
    except Exception as e:
        log.error(f"Error getting collection ID: {str(e)}")
        return None

def _format_search_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format search results into a standard structure.
    
    Args:
        results: List of raw search results
        
    Returns:
        List of formatted results with standardized fields
    """
    return [{
        "content": result.get("content", ""),
        "metadata": result.get("metadata", {}),
        "score": result.get("score", 0.0),
        "collection_id": result.get("collection_id", ""),
        "document_id": result.get("document_id", "")
    } for result in results if isinstance(result, dict)]

@handle_r2r_error
async def handle_search_with_names(
    query: str, 
    collection_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search for relevant chunks in collections using collection names.
    
    Args:
        query: The search query string
        collection_names: Optional list of collection names to search in
        
    Returns:
        Dictionary containing search results and success status
    """
    if not query or not query.strip():
        raise SearchError("Search query cannot be empty")
        
    try:
        collection_id = await _get_collection_id(collection_names[0] if collection_names else None)
        log.info(f"Performing search with query: '{query}', collection_id: {collection_id}")
        
        search_results = await r2r_client.search(query)
        if not search_results.get("success"):
            raise SearchError(search_results.get("error", "Search failed"))
        
        results = search_results.get("data", {}).get("results", [])
        formatted_results = _format_search_results(results)
        
        log.info(f"Search completed successfully, found {len(formatted_results)} results")
        return create_success_response({"results": formatted_results})
        
    except Exception as e:
        log.error(f"Search error: {str(e)}")
        raise SearchError(f"Search error: {str(e)}")

@handle_r2r_error
async def handle_rag_with_names(
    query: str, 
    collection_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Perform Retrieval-Augmented Generation (RAG) using collection names.
    
    Args:
        query: The query string for RAG
        collection_names: Optional list of collection names to search in
        
    Returns:
        Dictionary containing RAG response and success status
    """
    try:
        collection_id = await _get_collection_id(collection_names[0] if collection_names else None)
        log.info(f"Performing RAG with query: '{query}', collection_id: {collection_id}")
        
        rag_results = await r2r_client.rag(query, collection_id)
        if not rag_results.get("success"):
            raise SearchError(rag_results.get("error", "RAG failed"))
        
        data = rag_results.get("data", {})
        response_data = {
            "answer": data.get("answer", ""),
            "context": data.get("context", [])
        }
        
        log.info(f"RAG completed successfully with {len(response_data['context'])} sources")
        return create_success_response(response_data)
        
    except Exception as e:
        log.error(f"RAG error: {str(e)}")
        raise SearchError(f"RAG error: {str(e)}") 