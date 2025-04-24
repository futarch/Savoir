import os, logging, aiohttp, ssl
from dotenv import load_dotenv
from ..openai.assistant import assistant
from app.schema import User

# Load environment variables
load_dotenv()

log = logging.getLogger(__name__)

# WhatsApp API configuration
WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')

async def send_whatsapp_message(to, message):
    """Send a message via WhatsApp API"""
    log.info(f"Sending WhatsApp message to {to}")
    url = f"https://graph.facebook.com/v22.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_API_KEY}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp", "preview_url": False, "recipient_type": "individual",
        "to": to, "type": "text", "text": {"body": message}
    }

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        async with session.post(url, headers=headers, json=data) as response:
            response_data = await response.json()
            if response.status == 200:
                log.info(f"Successfully sent message to {to}")
                return response_data
            log.error(f"Failed to send message. Status: {response.status}, Response: {response_data}")
            raise Exception(f"Failed to send message: {response_data}")

async def respond_and_send_message(user_message: str, user: User, thread_id: str = None):   
    """Process a user message and send a response via WhatsApp"""
    try:
        log.info(f"Processing message for user {user.phone}: {user_message}")
        response = await assistant.run(user_message=user_message, user_id=str(user.id), thread_id=thread_id)
        
        if isinstance(response, dict):
            if "error" in response:
                content = "I'm sorry, I encountered an error processing your request. Please try again later."
            elif "choices" in response and response["choices"]:
                content = response["choices"][0]["message"].get("content", "No response generated").strip()
                thread_id = response.get("id", thread_id)
            else:
                content = "I'm sorry, I couldn't process your request at this time."
        else:
            content = "I'm sorry, I couldn't process your request at this time."
        
        await send_whatsapp_message(user.phone, content)
        log.info(f"Successfully completed message processing for user {user.phone}")
        
        return {"success": True, "response": content, "thread_id": thread_id}
    except Exception as e:
        log.error(f"Error in respond_and_send_message: {str(e)}")
        return {"success": False, "error": str(e)} 