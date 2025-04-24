"""
Domain package initialization.

This package provides domain-specific functionality for the application,
including WhatsApp integration, OpenAI assistant, and R2R retrieval.
"""
from .whatsapp import send_whatsapp_message, respond_and_send_message, transcribe_audio, authenticate_user_by_phone_number
from .openai.tools import tools, function_handlers
from .openai.assistant import run as run_assistant

async def process_assistant_message(message: str, user_id: str) -> str:
    """
    Process a message through the OpenAI assistant.
    
    Args:
        message: The message to process
        user_id: The ID of the user sending the message
        
    Returns:
        The assistant's response
    """
    return await run_assistant(message, user_id)

__all__ = [
    'send_whatsapp_message',
    'respond_and_send_message',
    'transcribe_audio',
    'authenticate_user_by_phone_number',
    'tools',
    'function_handlers',
    'run_assistant',
    'process_assistant_message'
]