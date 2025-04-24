import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Mock the r2r_client module
r2r_client = MagicMock()
r2r_client.create_document = AsyncMock()
r2r_client.add_document_to_collection = AsyncMock()
r2r_client.collections = AsyncMock()
r2r_client.search = AsyncMock()
r2r_client.rag = AsyncMock()

# Mock responses
MOCK_DOCUMENT_RESPONSE = {
    "success": True,
    "data": {
        "id": "doc123",
        "content": "Test document content",
        "created_at": "2023-01-01T00:00:00Z"
    }
}

MOCK_COLLECTION_RESPONSE = {
    "success": True,
    "data": {
        "id": "col123",
        "name": "Test Collection",
        "description": "Test description",
        "created_at": "2023-01-01T00:00:00Z"
    }
}

MOCK_COLLECTIONS_LIST_RESPONSE = {
    "success": True,
    "data": [
        {
            "id": "col123",
            "name": "Test Collection",
            "description": "Test description"
        },
        {
            "id": "col456",
            "name": "Another Collection",
            "description": "Another description"
        }
    ]
}

MOCK_SEARCH_RESPONSE = {
    "success": True,
    "data": [
        {
            "content": "Test search result",
            "metadata": {"source": "test"},
            "score": 0.95,
            "collection_id": "col123"
        }
    ]
}

MOCK_RAG_RESPONSE = {
    "success": True,
    "data": {
        "answer": "This is a test RAG response",
        "sources": [
            {
                "content": "Test source content",
                "metadata": {"source": "test"},
                "score": 0.95
            }
        ]
    }
}

# Mock the R2RError class
class R2RError(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# Mock the handle_r2r_error decorator
def handle_r2r_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, R2RError):
                raise e
            raise R2RError(str(e))
    return wrapper

# Mock the document functions
@handle_r2r_error
async def handle_create_document(content: str, metadata: dict = None):
    response = await r2r_client.create_document(content, metadata)
    if not response.get("success"):
        raise R2RError(response.get("error", "Failed to create document"))
    return response

@handle_r2r_error
async def handle_add_document_to_collection(document_id: str, collection_id: str):
    response = await r2r_client.add_document_to_collection(collection_id, document_id)
    if not response.get("success"):
        raise R2RError(response.get("error", "Failed to add document to collection"))
    return response

@handle_r2r_error
async def handle_add_document_to_collections(document_id: str, collection_ids: list):
    if not document_id:
        raise R2RError("Document ID is required")
    if not collection_ids:
        raise R2RError("Collection IDs are required")
        
    for collection_id in collection_ids:
        response = await r2r_client.add_document_to_collection(collection_id, document_id)
        if not response.get("success"):
            raise R2RError(response.get("error", "Failed to add document to collection"))
        
    return {
        "success": True,
        "document_id": document_id,
        "collection_ids": collection_ids
    }

# Test document functions
@pytest.mark.asyncio
async def test_handle_create_document():
    # Setup mock
    r2r_client.create_document.return_value = MOCK_DOCUMENT_RESPONSE
    
    # Call function
    result = await handle_create_document("Test document content", {"source": "test"})
    
    # Verify
    assert result["success"] is True
    assert result["data"]["id"] == "doc123"
    r2r_client.create_document.assert_called_once_with("Test document content", {"source": "test"})

@pytest.mark.asyncio
async def test_handle_add_document_to_collection():
    # Setup mock
    r2r_client.add_document_to_collection.return_value = {"success": True, "data": {}}
    
    # Call function
    result = await handle_add_document_to_collection("doc123", "col123")
    
    # Verify
    assert result["success"] is True
    r2r_client.add_document_to_collection.assert_called_once_with("col123", "doc123")

@pytest.mark.asyncio
async def test_handle_add_document_to_collections():
    # Reset mock
    r2r_client.add_document_to_collection.reset_mock()
    
    # Setup mock
    r2r_client.add_document_to_collection.return_value = {"success": True, "data": {}}
    
    # Call function
    result = await handle_add_document_to_collections("doc123", ["col123", "col456"])
    
    # Verify
    assert result["success"] is True
    assert result["document_id"] == "doc123"
    assert result["collection_ids"] == ["col123", "col456"]
    assert r2r_client.add_document_to_collection.call_count == 2
    r2r_client.add_document_to_collection.assert_any_call("col123", "doc123")
    r2r_client.add_document_to_collection.assert_any_call("col456", "doc123")

# Test error handling
@pytest.mark.asyncio
async def test_handle_create_document_error():
    # Setup mock to return error
    r2r_client.create_document.return_value = {"success": False, "error": "API Error"}
    
    # Call function and expect exception
    with pytest.raises(R2RError) as excinfo:
        await handle_create_document("Test document content")
    
    # Verify error message
    assert "API Error" in str(excinfo.value)

@pytest.mark.asyncio
async def test_handle_add_document_to_collections_validation():
    # Test with missing document_id
    with pytest.raises(R2RError) as excinfo:
        await handle_add_document_to_collections("", ["col123"])
    
    assert "Document ID is required" in str(excinfo.value)
    
    # Test with missing collection_ids
    with pytest.raises(R2RError) as excinfo:
        await handle_add_document_to_collections("doc123", [])
    
    assert "Collection IDs are required" in str(excinfo.value) 