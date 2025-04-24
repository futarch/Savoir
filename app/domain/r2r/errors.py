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
    log.error(f"R2R error: {error_msg}")
    return R2RResponse(success=False, error=error_msg).to_dict()

def handle_r2r_error(func):
    """
    Decorator for handling R2R errors.
    
    This decorator will:
    1. Pass through R2RError exceptions
    2. Wrap other exceptions in R2RError
    3. Log all errors with detailed information
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Log the function call
            func_name = func.__name__
            log.info(f"Calling R2R function: {func_name} with args: {args}, kwargs: {kwargs}")
            
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Check for error in the result
            if isinstance(result, dict) and not result.get("success", True):
                error_msg = result.get("error", "Unknown error")
                log.error(f"Error in {func_name}: {error_msg}")
                if error_msg:
                    raise R2RError(error_msg)
                else:
                    raise R2RError("Unknown error")
            
            # Log successful result
            log.info(f"R2R function {func_name} completed successfully")
            return result
            
        except R2RError as e:
            # Log the R2RError with details
            log.error(f"R2R error in {func.__name__}: {str(e)}")
            raise
            
        except Exception as e:
            # Log the exception with details
            import traceback
            error_msg = str(e) if str(e) else "Unknown error"
            log.error(f"Unexpected error in {func.__name__}: {error_msg}")
            log.error(f"Traceback: {traceback.format_exc()}")
            raise R2RError(error_msg) from e
            
    return wrapper 