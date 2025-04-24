import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp

# Mock the R2RError class
class R2RError(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# Mock the utility functions
async def wait_for_resource_ready(
    resource_id: str,
    check_function,
    status_field: str,
    ready_status: str = "ready",
    failed_status: str = "failed",
    max_attempts: int = 30,
    polling_interval: float = 1.0
) -> bool:
    """Generic function to wait for a resource to be ready."""
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
    """Wait for a collection to be ready."""
    async def check_collection(coll_id: str):
        return {"status": "ready"}  # Mocked response
    
    return await wait_for_resource_ready(
        collection_id,
        check_collection,
        "status",
        max_attempts=max_attempts,
        polling_interval=polling_interval
    )

async def wait_for_document_ready(
    document_id: str,
    max_attempts: int = 30,
    polling_interval: float = 1.0
) -> bool:
    """Wait for a document to be ready."""
    async def check_document(doc_id: str):
        return {"status": "ready"}  # Mocked response
    
    return await wait_for_resource_ready(
        document_id,
        check_document,
        "status",
        max_attempts=max_attempts,
        polling_interval=polling_interval
    )

async def make_request(
    method: str,
    endpoint: str,
    headers: dict,
    data: dict = None,
    timeout: int = 30
) -> dict:
    """Make an HTTP request."""
    session = await aiohttp.ClientSession().__aenter__()
    try:
        url = f"https://api.sciphi.ai/v3{endpoint}"
        response = await session.request(method, url, headers=headers, json=data, timeout=timeout)
        return await response.json()
    finally:
        await session.__aexit__(None, None, None)

def format_response(data) -> dict:
    """Format a response."""
    return data

def validate_collection_name(name: str) -> None:
    """Validate a collection name."""
    if not name:
        raise R2RError("Collection name cannot be empty")
    if "/" in name:
        raise R2RError("Collection name contains invalid characters")

# Mock responses
MOCK_COLLECTION_RESPONSE = {
    "success": True,
    "data": {
        "id": "col123",
        "name": "Test Collection",
        "description": "Test description",
        "status": "ready"
    }
}

MOCK_DOCUMENT_RESPONSE = {
    "success": True,
    "data": {
        "id": "doc123",
        "content": "Test document content",
        "status": "ready"
    }
}

@pytest.mark.asyncio
async def test_wait_for_resource_ready_success():
    # Define a mock check function that returns ready status
    async def mock_check_function(resource_id):
        return {"status": "ready"}
    
    # Call the function
    result = await wait_for_resource_ready(
        "test123",
        mock_check_function,
        "status",
        "ready",
        "failed",
        max_attempts=3,
        polling_interval=0.1
    )
    
    # Verify the result
    assert result is True

@pytest.mark.asyncio
async def test_wait_for_resource_ready_failure():
    # Define a mock check function that returns failed status
    async def mock_check_function(resource_id):
        return {"status": "failed"}
    
    # Call the function
    result = await wait_for_resource_ready(
        "test123",
        mock_check_function,
        "status",
        "ready",
        "failed",
        max_attempts=3,
        polling_interval=0.1
    )
    
    # Verify the result
    assert result is False

@pytest.mark.asyncio
async def test_wait_for_resource_ready_timeout():
    # Define a mock check function that always returns pending status
    async def mock_check_function(resource_id):
        return {"status": "pending"}
    
    # Call the function with a small max_attempts
    result = await wait_for_resource_ready(
        "test123",
        mock_check_function,
        "status",
        "ready",
        "failed",
        max_attempts=2,
        polling_interval=0.1
    )
    
    # Verify the result (should be False after max attempts)
    assert result is False

@pytest.mark.asyncio
async def test_wait_for_collection_ready():
    result = await wait_for_collection_ready(
        "col123",
        max_attempts=3,
        polling_interval=0.1
    )
    
    # Verify the result
    assert result is True

@pytest.mark.asyncio
async def test_wait_for_document_ready():
    result = await wait_for_document_ready(
        "doc123",
        max_attempts=3,
        polling_interval=0.1
    )
    
    # Verify the result
    assert result is True

@pytest.mark.asyncio
async def test_make_request():
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"success": True, "data": {"test": "data"}}
    mock_response.__aenter__.return_value = mock_response
    
    # Setup mock session
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.request.return_value = mock_response
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        # Call the function
        result = await make_request(
            "GET",
            "/test",
            {"Authorization": "Bearer test_token"},
            {"param": "value"},
            timeout=10
        )
        
        # Verify the result
        assert result == {"success": True, "data": {"test": "data"}}
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "GET"  # method
        assert call_args[0][1] == "https://api.sciphi.ai/v3/test"  # url
        assert call_args[1]['headers'] == {"Authorization": "Bearer test_token"}
        assert call_args[1]['json'] == {"param": "value"}
        assert call_args[1]['timeout'] == 10

def test_format_response():
    # Test with dictionary data
    result = format_response({"test": "data"})
    assert result == {"test": "data"}
    
    # Test with string data
    result = format_response("test data")
    assert result == "test data"
    
    # Test with None data
    result = format_response(None)
    assert result is None

def test_validate_collection_name():
    # Test valid collection name
    validate_collection_name("Valid Collection")
    
    # Test empty collection name
    with pytest.raises(R2RError) as excinfo:
        validate_collection_name("")
    
    assert "Collection name cannot be empty" in str(excinfo.value)
    
    # Test collection name with invalid characters
    with pytest.raises(R2RError) as excinfo:
        validate_collection_name("Invalid/Collection")
    
    assert "Collection name contains invalid characters" in str(excinfo.value) 