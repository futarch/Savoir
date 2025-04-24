from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, validator


class WhatsAppBaseModel(BaseModel):
    """Base model for all WhatsApp webhook related models with common configuration."""
    model_config = ConfigDict(extra='allow')


class Profile(WhatsAppBaseModel):
    """User profile information."""
    name: str


class Contact(WhatsAppBaseModel):
    """Contact information for a WhatsApp user."""
    profile: Profile
    wa_id: str = Field(..., description="WhatsApp ID of the contact")


class Text(WhatsAppBaseModel):
    """Text message content."""
    body: str = Field(..., min_length=1)


class Audio(WhatsAppBaseModel):
    """Audio message content."""
    mime_type: str = Field(..., pattern=r'^audio/.*$')
    sha256: str = Field(..., min_length=64, max_length=64)
    id: str
    voice: bool


class Message(WhatsAppBaseModel):
    """Message received from WhatsApp."""
    model_config = ConfigDict(populate_by_name=True, extra='allow')
    from_: str = Field(..., alias="from", description="Sender's WhatsApp ID")
    id: str
    timestamp: str
    text: Optional[Text] = None
    audio: Optional[Audio] = None
    type: str = Field(..., pattern=r'^(text|audio)$')


class Metadata(WhatsAppBaseModel):
    """Metadata about the WhatsApp Business Account."""
    display_phone_number: str
    phone_number_id: str
    
    @validator('display_phone_number')
    def validate_phone_number(cls, v):
        """Ensure phone number contains only digits."""
        digits = ''.join(filter(str.isdigit, v))
        if not (1 <= len(digits) <= 15):
            raise ValueError("Phone number must have between 1 and 15 digits")
        return digits


class Value(WhatsAppBaseModel):
    """Value object containing the webhook payload."""
    messaging_product: str = Field(..., pattern=r'^whatsapp$')
    metadata: Metadata
    contacts: Optional[List[Contact]] = None
    messages: Optional[List[Message]] = None


class Change(WhatsAppBaseModel):
    """Change notification from WhatsApp."""
    value: Value
    field: str = Field(..., pattern=r'^messages$')
    statuses: Optional[List[Dict[str, Any]]] = None


class Entry(WhatsAppBaseModel):
    """Entry in the webhook payload."""
    id: str
    changes: List[Change]


class Payload(WhatsAppBaseModel):
    """Root webhook payload from WhatsApp."""
    object: str = Field(..., pattern=r'^whatsapp_business_account$')
    entry: List[Entry]


class User(WhatsAppBaseModel):
    """User information for internal use."""
    id: str
    phone: str
    
    @validator('phone')
    def validate_phone_number(cls, v):
        """Ensure phone number contains only digits."""
        digits = ''.join(filter(str.isdigit, v))
        if not (1 <= len(digits) <= 15):
            raise ValueError("Phone number must have between 1 and 15 digits")
        return digits


class UserMessage(WhatsAppBaseModel):
    """Internal representation of a user message."""
    user: User
    message: Optional[str] = None
    audio: Optional[Audio] = None