import os
import json
import logging
import tempfile
from pathlib import Path
from typing import BinaryIO
from openai import OpenAI
from dotenv import load_dotenv
from app.schema import User, Audio

# Load environment variables
load_dotenv()

log = logging.getLogger(__name__)

# OpenAI configuration
llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def authenticate_user_by_phone_number(phone_number: str) -> User:
    """
    Since we're not implementing multi-user yet, this function will create a default user
    for any incoming phone number.
    """
    log.info(f"Authenticating user with phone number: {phone_number}")
    user = User(
        id="1",  # Default user ID as string
        phone=phone_number
    )
    log.info(f"Created default user: id={user.id} phone='{user.phone}'")
    return user

def download_file_from_facebook(file_id: str, file_type: str, mime_type: str) -> str | None:
    """
    Download a file from Facebook's servers using the file ID.
    
    Args:
        file_id (str): The ID of the file to download
        file_type (str): The type of file (e.g., 'audio', 'image')
        mime_type (str): The MIME type of the file
        
    Returns:
        str | None: The path to the downloaded file, or None if download failed
    """
    try:
        # Get the access token from environment variables
        access_token = os.getenv('WHATSAPP_API_KEY')
        if not access_token:
            log.error("WHATSAPP_API_KEY environment variable is not set")
            return None
            
        # Construct the URL to get the file URL
        url = f"https://graph.facebook.com/v22.0/{file_id}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        # Make the request to get the file URL
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            log.error(f"Failed to get file URL: {response.text}")
            return None
            
        # Extract the file URL from the response
        file_data = response.json()
        file_url = file_data.get('url')
        if not file_url:
            log.error("File URL not found in response")
            return None
            
        # Download the file
        file_response = requests.get(file_url, headers=headers)
        if file_response.status_code != 200:
            log.error(f"Failed to download file: {file_response.text}")
            return None
            
        # Create a temporary file to store the downloaded content
        temp_dir = tempfile.gettempdir()
        file_extension = mime_type.split('/')[-1]
        temp_file_path = Path(temp_dir) / f"{file_id}.{file_extension}"
        
        with open(temp_file_path, 'wb') as f:
            f.write(file_response.content)
            
        log.info(f"Successfully downloaded file to {temp_file_path}")
        return str(temp_file_path)
        
    except Exception as e:
        log.error(f"Error downloading file: {str(e)}")
        return None

def transcribe_audio_file(audio_file: BinaryIO) -> str:
    """
    Transcribe an audio file using OpenAI's Whisper model.
    
    Args:
        audio_file (BinaryIO): The audio file to transcribe
        
    Returns:
        str: The transcribed text
    """
    try:
        # Transcribe the audio file using OpenAI's Whisper model
        response = llm.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        
        return response.text
        
    except Exception as e:
        log.error(f"Error transcribing audio: {str(e)}")
        raise

def transcribe_audio(audio: Audio) -> str:
    """
    Transcribe an audio message received via WhatsApp.
    
    Args:
        audio (Audio): The audio object containing the file ID and MIME type
        
    Returns:
        str: The transcribed text
    """
    try:
        # Download the audio file from Facebook
        file_path = download_file_from_facebook(
            file_id=audio.file_id,
            file_type='audio',
            mime_type=audio.mime_type
        )
        
        if not file_path:
            raise Exception("Failed to download audio file")
            
        # Open the audio file and transcribe it
        with open(file_path, 'rb') as audio_file:
            transcription = transcribe_audio_file(audio_file)
            
        # Clean up the temporary file
        try:
            os.remove(file_path)
        except:
            pass
            
        return transcription
        
    except Exception as e:
        log.error(f"Error transcribing audio: {str(e)}")
        raise 