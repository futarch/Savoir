import os
import logging
from dotenv import load_dotenv
from .assistant import update_assistant

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Load environment variables from root .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
log.info(f"Loading environment from: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)  # override=True to ensure we use root .env values

def main():
    try:
        log.info("Starting assistant update process...")
        
        # Update the assistant with the latest instructions and tools
        updated_assistant = update_assistant()
        
        log.info(f"Successfully updated assistant with ID: {updated_assistant.id}")
        
    except Exception as e:
        log.error(f"Failed to update assistant: {str(e)}")

if __name__ == "__main__":
    main() 