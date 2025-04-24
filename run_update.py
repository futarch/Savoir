#!/usr/bin/env python3

import os, sys, logging
from dotenv import load_dotenv
from app.domain.openai.assistant import assistant

# Add current directory to Python path and configure logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'), override=True)

def main():
    try:
        log.info("Starting assistant update process...")
        updated_assistant = assistant.update_assistant()
        log.info(f"Successfully updated assistant with ID: {updated_assistant.id}")
        return updated_assistant
    except Exception as e:
        log.error(f"Failed to update assistant: {str(e)}")
        raise

if __name__ == "__main__":
    main() 