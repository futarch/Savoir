# Standard library imports
import os
import logging
import json
import aiohttp
from typing import Dict, Any, List, Optional

# Third-party imports
from dotenv import load_dotenv
from .errors import R2RError

# Load environment variables
load_dotenv()

log = logging.getLogger(__name__)

# Get API key from environment
API_KEY = os.getenv("R2R_API_KEY")
if not API_KEY:
    raise ValueError("R2R_API_KEY environment variable is not set")

# Base URL for the API
BASE_URL = "https://api.sciphi.ai/v3"
TIMEOUT = 30

class Documents:
    """Documents API client."""
    
    def __init__(self, client):
        self.client = client
        
    async def create(self, raw_text: str) -> Dict[str, Any]:
        """Create a new document.
        
        Args:
            raw_text: The text content to be uploaded
            
        Returns:
            Created document info
        """
        # Create form data
        data = aiohttp.FormData()
        data.add_field('raw_text', raw_text)
        
        response = await self.client._make_request(
            "POST",
            "/documents",
            data=data
        )
        
        return response

class R2RClient:
    """Client for interacting with the R2R API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("R2R_API_KEY")
        if not self.api_key:
            raise ValueError("R2R_API_KEY environment variable is not set")
        
        self.base_url = base_url or "https://api.sciphi.ai/v3"
        self._session = None
        self.documents = Documents(self)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(headers={
                "Authorization": f"Bearer {self.api_key}"
            })
        return self._session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the R2R API."""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with await session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError:
                    if response.status >= 400:
                        return {"success": False, "error": response_text}
                    raise R2RError(f"Invalid JSON response: {response_text}")
                
                # For successful responses, return the data as is
                if response.status < 400:
                    return response_data
                
                # For error responses, format them consistently
                error_msg = response_data.get("message", response_data.get("error", "Unknown error"))
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search(
        self,
        query: str,
        collection_id: Optional[str] = None,
        max_chunks: Optional[int] = 5,
        semantic: Optional[bool] = False
    ) -> Dict[str, Any]:
        """Perform a search query."""
        data = aiohttp.FormData()
        data.add_field('query', query)
        data.add_field('max_chunks', str(max_chunks))
        data.add_field('semantic', str(semantic).lower())
        if collection_id:
            data.add_field('collection_id', collection_id)
            
        return await self._make_request(
            "POST",
            "/search",
            data=data
        )
    
    async def collections(self, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """List all collections."""
        params = {
            "offset": offset,
            "limit": min(limit, 1000)
        }
        
        return await self._make_request("GET", "/collections", params=params)
    
    async def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new collection."""
        data = aiohttp.FormData()
        data.add_field('name', name)
        if description:
            data.add_field('description', description)
            
        return await self._make_request(
            "POST",
            "/collections",
            data=data
        )
    
    async def create_document(self, raw_text: str) -> Dict[str, Any]:
        """Create a new document."""
        return await self.documents.create(raw_text=raw_text)
    
    async def add_document_to_collection(self, collection_id: str, document_id: str) -> Dict[str, Any]:
        """Add a document to a collection."""
        return await self._make_request(
            "POST",
            f"/collections/{collection_id}/documents/{document_id}",
            data=aiohttp.FormData()
        )
    
    async def rag(
        self,
        query: str,
        collection_id: Optional[str] = None,
        max_chunks: Optional[int] = 8,
        model: Optional[str] = "gpt-4",
        temperature: Optional[float] = 0.7
    ) -> Dict[str, Any]:
        """Perform RAG operation."""
        data = aiohttp.FormData()
        data.add_field('query', query)
        data.add_field('max_chunks', str(max_chunks))
        data.add_field('model', model)
        data.add_field('temperature', str(temperature))
        if collection_id:
            data.add_field('collection_id', collection_id)
            
        return await self._make_request(
            "POST",
            "/rag",
            data=data
        )

    async def close(self):
        """Close the client session."""
        if self._session:
            await self._session.close()
            self._session = None

# Create a global client instance
r2r_client = R2RClient()

# Log the API key (first 10 chars only) for verification
log.info(f"R2R API key set: {API_KEY[:10]}...")

# Verify the key was set
if not r2r_client.api_key:
    log.error("Failed to set R2R API key on client")
    raise ValueError("Failed to set R2R API key on client")
else:
    log.info(f"R2R API key successfully set on client: {r2r_client.api_key[:10]}...")  # Only log first 10 chars 