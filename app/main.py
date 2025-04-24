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

# Constants and Configuration
VERIFICATION_MODE = "subscribe"
VERIFICATION_TOKEN = os.getenv('WHATSAPP_VERIFICATION_TOKEN')
if not VERIFICATION_TOKEN:
    raise ValueError("WHATSAPP_VERIFICATION_TOKEN environment variable is not set")

ERROR_MESSAGES = {
    "verification_failed": "Webhook verification failed",
    "unauthorized": "Unauthorized access",
    "invalid_payload": "Invalid webhook payload",
    "processing_error": "Error processing webhook"
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('whatsapp.log'), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

app = FastAPI(title="Savoir WhatsApp Webhook", version="0.1.0")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}

@app.get("/webhook")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge")
) -> Response:
    try:
        token = unquote(token).strip()
        if mode != VERIFICATION_MODE or not token or token != VERIFICATION_TOKEN.strip():
            raise HTTPException(status_code=403, detail=ERROR_MESSAGES["verification_failed"])
        return Response(content=challenge, media_type="text/plain")
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error in webhook verification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def parse_message(payload: Payload) -> Optional[Message]:  
    return payload.entry[0].changes[0].value.messages[0] if payload.entry[0].changes[0].value.messages else None

def get_current_user(message: Annotated[Message, Depends(parse_message)]) -> Optional[User]:  
    return authenticate_user_by_phone_number(message.from_) if message else None

def parse_audio_file(message: Annotated[Message, Depends(parse_message)]) -> Optional[Audio]:  
    return message.audio if message and message.type == "audio" else None

def message_extractor(  
    message: Annotated[Message, Depends(parse_message)],  
    audio: Annotated[Audio, Depends(parse_audio_file)],  
) -> Optional[str]:  
    if audio:
        return transcribe_audio(audio)
    return message.text.body if message and message.text else None

@app.post("/webhook")
async def process_webhook(request: Request) -> dict[str, str]:
    try:
        body = await request.json()
        log.info(f"Received webhook payload: {body}")
        
        try:
            payload = Payload(**body)
            message = parse_message(payload)
            
            if message and message.text:
                user = authenticate_user_by_phone_number(message.from_)
                if not user:
                    raise HTTPException(status_code=401, detail=ERROR_MESSAGES["unauthorized"])
                await respond_and_send_message(message.text.body, user)
            
        except Exception as e:
            log.warning(f"{ERROR_MESSAGES['invalid_payload']}: {str(e)}")
            if hasattr(e, 'errors'):
                for error in e.errors():
                    log.warning(f"Validation error: {error.get('msg', '')} at {error.get('loc', [])}")
        
        return {"status": "success"}
        
    except Exception as e:
        log.error(f"{ERROR_MESSAGES['processing_error']}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
