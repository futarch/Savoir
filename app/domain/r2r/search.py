import logging
from typing import List, Dict, Any, Optional
from .client import r2r_client
from .errors import create_success_response, create_error_response, SearchError, handle_r2r_error, R2RError
from .utils import make_request, format_response
from .handlers import handle_search, handle_rag

log = logging.getLogger(__name__)

async def _convert_collection_names_to_ids(collection_names: List[str]) -> Optional[List[str]]:
    """
    Convert collection names to their corresponding IDs.
    
    This function queries the R2R API to get all collections and matches the provided
    collection names to their corresponding IDs. If a collection name is not found,
    it logs a warning and continues with the next name.
    
    Args:
        collection_names: List of collection names to convert
        
    Returns:
        List of collection IDs or None if no collection names provided
        
    Raises:
        Exception: If there's an error accessing the collections API
    """
    if not collection_names:
        return None
        
    try:
        collections = await r2r_client.collections()
        if not collections.get("success"):
            error = collections.get("error", "Failed to list collections")
            raise R2RError(error)
            
        collection_ids = []
        
        for collection_name in collection_names:
            found = False
            for collection in collections.get("data", []):
                if collection.get("name") == collection_name:
                    collection_ids.append(str(collection.get("id")))
                    found = True
                    break
            
            if not found:
                log.warning(f"Collection name '{collection_name}' not found")
                
        return collection_ids if collection_ids else None
    except Exception as e:
        log.error(f"Error converting collection names to IDs: {str(e)}")
        raise

def _extract_results_from_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract and format search results from various possible API response formats.
    
    This function handles different response structures that might come from the R2R API,
    including chunk search results, graph search results, and vector search results.
    It standardizes the format of each result to include content, metadata, score,
    and document identifiers.
    
    Args:
        response: The API response dictionary containing search results
        
    Returns:
        List of formatted results, each containing:
            - content: The text content of the result
            - metadata: Additional metadata about the result
            - score: Relevance score of the result
            - collection_id: ID of the collection containing the result
            - document_id: ID of the source document
    """
    formatted_results = []
    
    # Check all possible result locations in the response
    result_keys = [
        "chunk_search_results",
        "graph_search_results",
        "results",
        "search_results",
        "vector_search_results"
    ]
    
    for key in result_keys:
        results = response.get(key, [])
        if not results or not isinstance(results, list):
            continue
            
        for result in results:
            if isinstance(result, dict):
                formatted_result = {
                    "content": result.get("content", ""),
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", 0.0),
                    "collection_id": result.get("collection_id", ""),
                    "document_id": result.get("document_id", "")
                }
                formatted_results.append(formatted_result)
            else:
                # Handle object format
                formatted_result = {
                    "content": getattr(result, "content", ""),
                    "metadata": getattr(result, "metadata", {}),
                    "score": getattr(result, "score", 0.0),
                    "collection_id": getattr(result, "collection_id", ""),
                    "document_id": getattr(result, "document_id", "")
                }
                formatted_results.append(formatted_result)
    
    return formatted_results

@handle_r2r_error
async def handle_search_with_names(
    query: str, 
    collection_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search for relevant chunks in collections using collection names.
    
    This function performs a search across specified collections to find
    the most relevant chunks of text matching the query. It supports filtering
    by collection names.
    
    Args:
        query: The search query string
        collection_names: Optional list of collection names to search in
        
    Returns:
        A dictionary containing:
            - success: Boolean indicating if the operation was successful
            - data: Dictionary containing the search results
            - error: Error message if the operation failed
        
    Raises:
        SearchError: If the search operation fails
    """
    if not query or not query.strip():
        raise SearchError("Search query cannot be empty")
        
    try:
        # Convert collection names to IDs if provided
        collection_ids = await _convert_collection_names_to_ids(collection_names)
        
        log.info(f"Performing search with query: '{query}', collection_names: {collection_names}")
        
        # Use the handler function with the first collection ID if available
        collection_id = collection_ids[0] if collection_ids else None
        
        # Perform the search using the handler function
        search_results = await r2r_client.search(query)
        
        if not search_results.get("success"):
            error = search_results.get("error", "Search failed")
            raise SearchError(error)
        
        # Format the results
        results = search_results.get("data", {}).get("results", [])
        
        log.info(f"Search completed successfully, found {len(results)} results")
        return {
            "success": True,
            "data": {
                "results": results
            }
        }
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
    
    This function combines semantic search with language model generation to provide
    context-aware responses. It first retrieves relevant chunks from the collections,
    then uses them as context for the language model to generate a response.
    
    Args:
        query: The query string for RAG
        collection_names: Optional list of collection names to search in
        
    Returns:
        A dictionary containing:
            - success: Boolean indicating if the operation was successful
            - data: Dictionary containing the RAG response
            - error: Error message if the operation failed
    """
    try:
        # Convert collection names to IDs if provided
        collection_ids = await _convert_collection_names_to_ids(collection_names)
        collection_id = collection_ids[0] if collection_ids else None
        
        log.info(f"Performing RAG with query: '{query}', collection_names: {collection_names}")
        
        # Perform RAG using the client
        rag_results = await r2r_client.rag(query, collection_id)
        
        if not rag_results.get("success"):
            error = rag_results.get("error", "RAG failed")
            raise SearchError(error)
        
        # Format the results
        data = rag_results.get("data", {})
        answer = data.get("answer", "")
        context = data.get("context", [])
        
        log.info(f"RAG completed successfully with {len(context)} sources")
        return {
            "success": True,
            "data": {
                "answer": answer,
                "context": context
            }
        }
    except Exception as e:
        log.error(f"RAG error: {str(e)}")
        raise SearchError(f"RAG error: {str(e)}") 