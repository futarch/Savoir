import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
import json

# Mock the R2RClient class
class R2RClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or "test_api_key"
        self.base_url = base_url or "https://test.api.com"
        
    async def _make_request(self, method: str, endpoint: str, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.api_key}'
        url = f"{self.base_url}{endpoint}"
        
        session = await aiohttp.ClientSession().__aenter__()
        try:
            response = await session.request(method, url, headers=headers, **kwargs)
            return await response.json()
        finally:
            await session.__aexit__(None, None, None)
        
    async def create_document(self, content: str, metadata: dict = None):
        return await self._make_request(
            "POST",
            "/documents",
            json={"content": content, "metadata": metadata}
        )
        
    async def add_document_to_collection(self, collection_id: str, document_id: str):
        return await self._make_request(
            "POST",
            f"/collections/{collection_id}/documents/{document_id}"
        )
        
    async def collections(self, offset: int = 0, limit: int = 100):
        return await self._make_request(
            "GET",
            "/collections",
            params={"offset": offset, "limit": limit}
        )
        
    async def create_collection(self, name: str, description: str = ""):
        return await self._make_request(
            "POST",
            "/collections",
            json={"name": name, "description": description}
        )
        
    async def search(self, query: str, collection_id: str = None, max_chunks: int = 5, semantic: bool = False):
        return await self._make_request(
            "POST",
            "/search",
            json={
                "query": query,
                "collection_id": collection_id,
                "max_chunks": max_chunks,
                "semantic": semantic
            }
        )
        
    async def rag(self, query: str, collection_id: str = None, max_chunks: int = 8, model: str = "gpt-4", temperature: float = 0.7):
        return await self._make_request(
            "POST",
            "/rag",
            json={
                "query": query,
                "collection_id": collection_id,
                "max_chunks": max_chunks,
                "model": model,
                "temperature": temperature
            }
        )

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

@pytest.fixture
def r2r_client():
    return R2RClient(api_key='test_api_key', base_url='https://test.api.com')

@pytest.mark.asyncio
async def test_make_request(r2r_client):
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = MOCK_DOCUMENT_RESPONSE
    mock_response.__aenter__.return_value = mock_response
    
    # Setup mock session
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.request.return_value = mock_response
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        # Call function
        result = await r2r_client._make_request("GET", "/test")
        
        # Verify
        assert result == MOCK_DOCUMENT_RESPONSE
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "GET"  # method
        assert call_args[0][1] == "https://test.api.com/test"  # url
        assert call_args[1]['headers']['Authorization'] == 'Bearer test_api_key'

@pytest.mark.asyncio
async def test_create_document(r2r_client):
    with patch.object(r2r_client, '_make_request') as mock_make_request:
        # Setup mock
        mock_make_request.return_value = MOCK_DOCUMENT_RESPONSE
        
        # Call function
        result = await r2r_client.create_document("Test document content")
        
        # Verify
        assert result == MOCK_DOCUMENT_RESPONSE
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[1] == "/documents"

@pytest.mark.asyncio
async def test_add_document_to_collection(r2r_client):
    with patch.object(r2r_client, '_make_request') as mock_make_request:
        # Setup mock
        mock_make_request.return_value = {"success": True, "data": {}}
        
        # Call function
        result = await r2r_client.add_document_to_collection("col123", "doc123")
        
        # Verify
        assert result == {"success": True, "data": {}}
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[1] == "/collections/col123/documents/doc123"

@pytest.mark.asyncio
async def test_collections(r2r_client):
    with patch.object(r2r_client, '_make_request') as mock_make_request:
        # Setup mock
        mock_make_request.return_value = MOCK_COLLECTIONS_LIST_RESPONSE
        
        # Call function
        result = await r2r_client.collections(offset=0, limit=10)
        
        # Verify
        assert result == MOCK_COLLECTIONS_LIST_RESPONSE
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[0]
        assert call_args[0] == "GET"
        assert call_args[1] == "/collections"
        assert mock_make_request.call_args[1]['params'] == {"offset": 0, "limit": 10}

@pytest.mark.asyncio
async def test_create_collection(r2r_client):
    with patch.object(r2r_client, '_make_request') as mock_make_request:
        # Setup mock
        mock_make_request.return_value = MOCK_COLLECTION_RESPONSE
        
        # Call function
        result = await r2r_client.create_collection("Test Collection", "Test description")
        
        # Verify
        assert result == MOCK_COLLECTION_RESPONSE
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[1] == "/collections"
        assert mock_make_request.call_args[1]['json'] == {
            "name": "Test Collection",
            "description": "Test description"
        }

@pytest.mark.asyncio
async def test_search(r2r_client):
    with patch.object(r2r_client, '_make_request') as mock_make_request:
        # Setup mock
        mock_make_request.return_value = MOCK_SEARCH_RESPONSE
        
        # Call function
        result = await r2r_client.search("test query", collection_id="col123", max_chunks=5, semantic=True)
        
        # Verify
        assert result == MOCK_SEARCH_RESPONSE
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[1] == "/search"
        assert mock_make_request.call_args[1]['json'] == {
            "query": "test query",
            "collection_id": "col123",
            "max_chunks": 5,
            "semantic": True
        }

@pytest.mark.asyncio
async def test_rag(r2r_client):
    with patch.object(r2r_client, '_make_request') as mock_make_request:
        # Setup mock
        mock_make_request.return_value = MOCK_RAG_RESPONSE
        
        # Call function
        result = await r2r_client.rag(
            "test query", 
            collection_id="col123", 
            max_chunks=8, 
            model="gpt-4", 
            temperature=0.7
        )
        
        # Verify
        assert result == MOCK_RAG_RESPONSE
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args[0]
        assert call_args[0] == "POST"
        assert call_args[1] == "/rag"
        assert mock_make_request.call_args[1]['json'] == {
            "query": "test query",
            "collection_id": "col123",
            "max_chunks": 8,
            "model": "gpt-4",
            "temperature": 0.7
        }

@pytest.mark.asyncio
async def test_error_handling(r2r_client):
    with patch.object(r2r_client, '_make_request') as mock_make_request:
        # Setup mock to raise exception
        mock_make_request.side_effect = aiohttp.ClientError("API Error")
        
        # Call function and expect exception
        with pytest.raises(Exception) as excinfo:
            await r2r_client.search("test query")
        
        # Verify error message
        assert "API Error" in str(excinfo.value) 