import asyncio
from asyncio import TimeoutError
from typing import Optional, Union, Any, Callable, Awaitable, Dict
from .client import r2r_client
import aiohttp
import logging
from .errors import R2RError, handle_r2r_error

log = logging.getLogger(__name__)

# Common constants
TIMEOUT = 30
BASE_URL = "https://api.sciphi.ai/v3"

async def wait_for_resource_ready(
    resource_id: str,
    check_function: Callable[[str], Awaitable[Any]],
    status_field: str,
    ready_status: str = "ready",
    failed_status: str = "failed",
    max_attempts: int = 30,
    polling_interval: float = 1.0
) -> bool:
    """
    Generic function to wait for a resource to be ready.
    
    Args:
        resource_id: The ID of the resource to check
        check_function: Async function that retrieves the resource
        status_field: The field name that contains the status
        ready_status: The status value that indicates the resource is ready
        failed_status: The status value that indicates the resource has failed
        max_attempts: Maximum number of polling attempts
        polling_interval: Time between polling attempts in seconds
        
    Returns:
        bool: True if the resource is ready, False otherwise
    """
    for attempt in range(max_attempts):
        resource = await check_function(resource_id)
        
        # Handle both dictionary and object responses
        status = resource.get(status_field) if isinstance(resource, dict) else getattr(resource, status_field, None)
        
        if status == ready_status:
            return True
        elif status == failed_status:
            return False
            
        await asyncio.sleep(polling_interval)
    
    return False

async def wait_for_collection_ready(
    collection_id: str,
    max_attempts: int = 30,
    polling_interval: float = 1.0
) -> bool:
    """
    Wait for a collection to be ready.
    
    Args:
        collection_id: The ID of the collection to check
        max_attempts: Maximum number of polling attempts
        polling_interval: Time between polling attempts in seconds
        
    Returns:
        bool: True if the collection is ready, False otherwise
    """
    async def check_collection(coll_id: str) -> Any:
        collections = await r2r_client.collections()
        for collection in collections.get("data", []):
            if isinstance(collection, dict):
                if str(collection.get("id")) == coll_id:
                    return collection
            else:
                if str(collection.id) == coll_id:
                    return collection
        return None
        
    return await wait_for_resource_ready(
        resource_id=collection_id,
        check_function=check_collection,
        status_field="graph_cluster_status",
        max_attempts=max_attempts,
        polling_interval=polling_interval
    )

async def wait_for_document_ready(
    document_id: str,
    max_attempts: int = 30,
    polling_interval: float = 1.0
) -> bool:
    """
    Wait for a document to be ready.
    
    Args:
        document_id: The ID of the document to check
        max_attempts: Maximum number of polling attempts
        polling_interval: Time between polling attempts in seconds
        
    Returns:
        bool: True if the document is ready, False otherwise
    """
    async def check_document(doc_id: str) -> Any:
        return await r2r_client.documents.get(doc_id)
        
    return await wait_for_resource_ready(
        resource_id=document_id,
        check_function=check_document,
        status_field="ingestion_status",
        ready_status="completed",
        max_attempts=max_attempts,
        polling_interval=polling_interval
    )

async def make_request(
    method: str,
    endpoint: str,
    headers: Dict[str, str],
    data: Optional[Dict[str, Any]] = None,
    timeout: int = TIMEOUT
) -> Dict[str, Any]:
    """Make an HTTP request to the R2R API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint
        headers: Request headers
        data: Request body data
        timeout: Request timeout in seconds
        
    Returns:
        API response as dictionary
        
    Raises:
        R2RError: If the request fails
    """
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{BASE_URL}/{endpoint.lstrip('/')}"
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=timeout
            ) as response:
                response_data = await response.json()
                
                if not response.ok:
                    error_msg = response_data.get("error", "Unknown error")
                    raise R2RError(error_msg, status_code=response.status)
                    
                return response_data
                
        except aiohttp.ClientError as e:
            raise R2RError(f"Request failed: {str(e)}")
        except Exception as e:
            raise R2RError(f"Unexpected error: {str(e)}")

def format_response(data: Any) -> Dict[str, Any]:
    """Format API response data.
    
    Args:
        data: Response data to format
        
    Returns:
        Formatted response dictionary
    """
    if isinstance(data, dict):
        return data
    return {"data": data}

def validate_collection_name(name: str) -> None:
    """Validate collection name.
    
    Args:
        name: Collection name to validate
        
    Raises:
        R2RError: If name is invalid
    """
    if not name or not isinstance(name, str):
        raise R2RError("Collection name must be a non-empty string")
    if len(name) > 100:
        raise R2RError("Collection name must be less than 100 characters") 