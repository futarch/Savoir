"""
Domain package initialization.

This package provides domain-specific functionality for the application,
including WhatsApp integration, OpenAI assistant, and R2R retrieval.
"""
from .whatsapp import send_whatsapp_message, respond_and_send_message, transcribe_audio, authenticate_user_by_phone_number
from .openai.tools import tools, function_handlers
from .openai.assistant import assistant
from .r2r import (
    handle_create_collection,
    handle_list_user_collections,
    handle_create_document,
    handle_add_document_to_collection,
    handle_search_with_names,
    handle_rag_with_names,
    r2r_client
)

async def process_assistant_message(message: str, user_id: str) -> str:
    """
    Process a message through the OpenAI assistant.
    
    Args:
        message: The message to process
        user_id: The ID of the user sending the message
        
    Returns:
        The assistant's response
    """
    return await assistant.run(message, user_id)

__all__ = [
    # WhatsApp functionality
    'send_whatsapp_message',
    'respond_and_send_message',
    'transcribe_audio',
    'authenticate_user_by_phone_number',
    
    # OpenAI functionality
    'tools',
    'function_handlers',
    'assistant',
    'process_assistant_message',
    
    # R2R functionality
    'handle_create_collection',
    'handle_list_user_collections',
    'handle_create_document',
    'handle_add_document_to_collection',
    'handle_search_with_names',
    'handle_rag_with_names',
    'r2r_client'
]