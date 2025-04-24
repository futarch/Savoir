import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the update_assistant function
from app.domain.openai.assistant import update_assistant

# Run the update_assistant function
if __name__ == "__main__":
    try:
        print("Starting assistant update process...")
        updated_assistant = update_assistant()
        print(f"Successfully updated assistant with ID: {updated_assistant.id}")
    except Exception as e:
        print(f"Failed to update assistant: {str(e)}") 