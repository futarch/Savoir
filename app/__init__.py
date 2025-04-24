"""
Application package initialization.

This package provides the main application functionality,
including FastAPI routes and domain-specific operations.
"""
from app.main import app

__version__ = "0.1.0"
__author__ = "Savoir Team"

# Import commonly used components
from app.domain import (
    send_whatsapp_message,
    respond_and_send_message,
    transcribe_audio,
    authenticate_user_by_phone_number,
    process_assistant_message
)

__all__ = [
    "app",
    "send_whatsapp_message",
    "respond_and_send_message",
    "transcribe_audio",
    "authenticate_user_by_phone_number",
    "process_assistant_message",
    "__version__",
    "__author__"
] 