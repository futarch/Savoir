"""Error handling utilities for R2R (Retrieval) operations.

This module provides standardized error handling and response formatting for R2R operations.
It includes utility functions for creating consistent success and error responses,
as well as custom exceptions for specific error cases.
"""

import logging
from typing import TypeVar, Dict, Any, Union, Optional, Generic
from functools import wraps

log = logging.getLogger(__name__)

T = TypeVar('T')

class R2RError(Exception):
    """Base class for R2R errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
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

class R2RResponse(Generic[T]):
    """Generic response wrapper for R2R operations"""
    def __init__(self, success: bool, data: Optional[T] = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error
        }

def create_success_response(data: Any = None) -> Dict[str, Any]:
    """Create a success response"""
    return R2RResponse(success=True, data=data).to_dict()

def create_error_response(error: Union[Exception, str]) -> Dict[str, Any]:
    """Create an error response"""
    error_msg = str(error)
    return R2RResponse(success=False, error=error_msg).to_dict()

def handle_r2r_error(func):
    """
    Decorator for handling R2R errors.
    
    This decorator will:
    1. Pass through R2RError exceptions
    2. Wrap other exceptions in R2RError
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Check for error in the result
            if isinstance(result, dict) and not result.get("success", True):
                error_msg = result.get("error", "Unknown error")
                if error_msg:
                    raise R2RError(error_msg)
                else:
                    raise R2RError("Unknown error")
            
            return result
            
        except R2RError as e:
            # Pass through R2RError
            raise
            
        except Exception as e:
            # Wrap other exceptions in R2RError
            raise R2RError(str(e))
            
    return wrapper 