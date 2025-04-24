import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Mock the error classes and functions
class R2RError(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class SearchError(R2RError):
    """Error during search operations"""
    pass

class DocumentError(R2RError):
    """Error during document operations"""
    pass

class CollectionError(R2RError):
    """Error during collection operations"""
    pass

class ConversationError(R2RError):
    """Error during conversation operations"""
    pass

class R2RResponse:
    """Generic response wrapper for R2R operations"""
    def __init__(self, success: bool, data: dict = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self) -> dict:
        """Convert response to dictionary format"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error
        }

def create_success_response(data: dict = None) -> dict:
    """Create a success response"""
    return {
        "success": True,
        "data": data
    }

def create_error_response(error: Exception | str) -> dict:
    """Create an error response"""
    error_message = str(error) if isinstance(error, Exception) else error
    return {
        "success": False,
        "data": None,
        "error": error_message
    }

def handle_r2r_error(func):
    """Decorator to handle R2R errors"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, R2RError):
                raise e
            raise R2RError(str(e))
    return wrapper

def test_r2r_error():
    # Test basic error
    error = R2RError("Test error")
    assert str(error) == "Test error"
    assert error.status_code is None
    
    # Test error with status code
    error = R2RError("Test error", status_code=400)
    assert str(error) == "Test error"
    assert error.status_code == 400

def test_specific_errors():
    # Test SearchError
    error = SearchError("Search error")
    assert isinstance(error, R2RError)
    assert str(error) == "Search error"
    
    # Test DocumentError
    error = DocumentError("Document error")
    assert isinstance(error, R2RError)
    assert str(error) == "Document error"
    
    # Test CollectionError
    error = CollectionError("Collection error")
    assert isinstance(error, R2RError)
    assert str(error) == "Collection error"
    
    # Test ConversationError
    error = ConversationError("Conversation error")
    assert isinstance(error, R2RError)
    assert str(error) == "Conversation error"

def test_r2r_response():
    # Test success response
    response = R2RResponse(True, data={"test": "data"})
    assert response.success is True
    assert response.data == {"test": "data"}
    assert response.error is None
    
    # Test error response
    response = R2RResponse(False, error="Test error")
    assert response.success is False
    assert response.data is None
    assert response.error == "Test error"
    
    # Test to_dict method
    response_dict = response.to_dict()
    assert response_dict["success"] is False
    assert response_dict["data"] is None
    assert response_dict["error"] == "Test error"

def test_create_success_response():
    # Test with data
    response = create_success_response({"test": "data"})
    assert response["success"] is True
    assert response["data"] == {"test": "data"}
    assert "error" not in response
    
    # Test without data
    response = create_success_response()
    assert response["success"] is True
    assert response["data"] is None
    assert "error" not in response

def test_create_error_response():
    # Test with string error
    response = create_error_response("Test error")
    assert response["success"] is False
    assert response["data"] is None
    assert response["error"] == "Test error"
    
    # Test with exception error
    response = create_error_response(R2RError("Test exception"))
    assert response["success"] is False
    assert response["data"] is None
    assert response["error"] == "Test exception"

@pytest.mark.asyncio
async def test_handle_r2r_error_decorator_success():
    # Define a test function
    @handle_r2r_error
    async def test_function():
        return {"result": "success"}
    
    # Call the function
    result = await test_function()
    
    # Verify the result
    assert result == {"result": "success"}

@pytest.mark.asyncio
async def test_handle_r2r_error_decorator_exception():
    # Define a test function that raises an exception
    @handle_r2r_error
    async def test_function():
        raise R2RError("Test error")
    
    # Call the function and expect exception
    with pytest.raises(R2RError) as excinfo:
        await test_function()
    
    # Verify the error message
    assert str(excinfo.value) == "Test error"

@pytest.mark.asyncio
async def test_handle_r2r_error_decorator_with_args():
    # Define a test function with arguments
    @handle_r2r_error
    async def test_function(arg1, arg2):
        return {"arg1": arg1, "arg2": arg2}
    
    # Call the function with arguments
    result = await test_function("value1", "value2")
    
    # Verify the result
    assert result == {"arg1": "value1", "arg2": "value2"} 