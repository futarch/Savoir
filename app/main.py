from dotenv import load_dotenv
load_dotenv()

import logging
from typing import Optional
from typing_extensions import Annotated  
from fastapi import FastAPI, Query, HTTPException, Depends, Request, Response  
from app.domain import (
    send_whatsapp_message,
    respond_and_send_message,
    transcribe_audio,
    authenticate_user_by_phone_number,
    process_assistant_message
)
from app.schema import Payload, Message, Audio, User  
import os
from urllib.parse import unquote

# Constants
VERIFICATION_MODE = "subscribe"
ERROR_MESSAGES = {
    "verification_failed": "Webhook verification failed",
    "unauthorized": "Unauthorized access",
    "invalid_payload": "Invalid webhook payload",
    "processing_error": "Error processing webhook"
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
VERIFICATION_TOKEN = os.getenv('WHATSAPP_VERIFICATION_TOKEN')
if not VERIFICATION_TOKEN:
    raise ValueError("WHATSAPP_VERIFICATION_TOKEN environment variable is not set")

log = logging.getLogger(__name__)

app = FastAPI(
    title="Savoir WhatsApp Webhook",
    version="0.1.0"
)

# ===== Health Check Endpoints =====

@app.get("/health")
def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "healthy"}

# ===== Webhook Verification =====

@app.get("/webhook")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
) -> Response:
    """
    Verify the WhatsApp webhook.
    
    Args:
        mode: The verification mode (must be "subscribe")
        token: The verification token to check
        challenge: The challenge string to return if verification succeeds
    """
    try:
        token = unquote(token).strip()
        verification_token = VERIFICATION_TOKEN.strip()
        
        if mode != VERIFICATION_MODE or not token or token != verification_token:
            log.error(ERROR_MESSAGES["verification_failed"])
            raise HTTPException(status_code=403, detail=ERROR_MESSAGES["verification_failed"])
            
        return Response(content=challenge, media_type="text/plain")
            
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error in webhook verification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== Message Processing Dependencies =====

def parse_message(payload: Payload) -> Optional[Message]:  
    """
    Extract the first message from a WhatsApp webhook payload.
    
    Args:
        payload: The webhook payload containing message data
    """
    if not payload.entry[0].changes[0].value.messages:  
        return None  
    return payload.entry[0].changes[0].value.messages[0]

def get_current_user(message: Annotated[Message, Depends(parse_message)]) -> Optional[User]:  
    """
    Authenticate user based on phone number.
    
    Args:
        message: The WhatsApp message containing the sender's phone number
    """
    if not message:  
        return None  
    return authenticate_user_by_phone_number(message.from_)

def parse_audio_file(message: Annotated[Message, Depends(parse_message)]) -> Optional[Audio]:  
    """
    Extract audio data from a message.
    
    Args:
        message: The WhatsApp message
    """
    if message and message.type == "audio":  
        return message.audio  
    return None  

def message_extractor(  
        message: Annotated[Message, Depends(parse_message)],  
        audio: Annotated[Audio, Depends(parse_audio_file)],  
) -> Optional[str]:  
    """
    Extract text content from message or audio.
    
    Args:
        message: The WhatsApp message
        audio: The audio data if the message is an audio message
    """
    if audio:  
        return transcribe_audio(audio)  
    if message and message.text:  
        return message.text.body  
    return None

# ===== Webhook Processing =====

@app.post("/webhook")
async def process_webhook(request: Request) -> dict[str, str]:
    """
    Process incoming WhatsApp webhook messages.
    
    This endpoint handles both text and audio messages from WhatsApp.
    It authenticates the user, extracts the message content, and processes it.
    """
    try:
        body = await request.json()
        log.info(f"Received webhook payload: {body}")
        
        try:
            payload = Payload(**body)
            message = parse_message(payload)
            
            if message:
                user_phone = message.from_
                user_message = message.text.body if message.text else None
                
                if user_message:
                    user = authenticate_user_by_phone_number(user_phone)
                    if not user:
                        log.error(ERROR_MESSAGES["unauthorized"])
                        raise HTTPException(status_code=401, detail=ERROR_MESSAGES["unauthorized"])
                    
                    await respond_and_send_message(user_message, user)
            
        except Exception as e:
            log.warning(f"{ERROR_MESSAGES['invalid_payload']}: {str(e)}")
            if hasattr(e, 'errors'):  # If it's a Pydantic validation error
                for error in e.errors():
                    log.warning(f"Validation error: {error}")
                    log.warning(f"  - Location: {error.get('loc', [])}")
                    log.warning(f"  - Message: {error.get('msg', '')}")
                    log.warning(f"  - Type: {error.get('type', '')}")
        
        return {"status": "success"}
        
    except Exception as e:
        log.error(f"{ERROR_MESSAGES['processing_error']}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
