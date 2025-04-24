from openai import OpenAI, AsyncOpenAI
import os
import json
import asyncio
import logging
from dotenv import load_dotenv, find_dotenv
from .tools import tools, function_handlers
from .instructions import INSTRUCTIONS, NOTES
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class OpenAIAssistant:
    """Class to manage OpenAI Assistant API interactions."""
    
    def __init__(self, api_key=None, assistant_id=None):
        """Initialize the OpenAI Assistant client.
        
        Args:
            api_key: OpenAI API key. If None, will be loaded from environment.
            assistant_id: OpenAI Assistant ID. If None, will be loaded from environment or created.
        """
        # Load environment variables from root .env
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
        log.info(f"Loading environment from: {env_path}")
        load_dotenv(dotenv_path=env_path, override=True)
        
        # Initialize OpenAI clients
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        
        # Get or create assistant
        self.assistant_id = assistant_id or os.getenv("OPENAI_ASSISTANT_ID")
        self.assistant = self._get_or_create_assistant()
        
        # Store user threads
        self.user_threads = {}
    
    def _get_or_create_assistant(self):
        """Get existing assistant or create a new one if it doesn't exist."""
        try:
            if self.assistant_id:
                log.info(f"Retrieving assistant with ID: {self.assistant_id}")
                # Try to retrieve the existing assistant
                assistant = self.client.beta.assistants.retrieve(self.assistant_id)
                return assistant
                
            # Create new assistant if none exists
            log.info("No assistant ID found, creating new assistant")
            assistant = self.client.beta.assistants.create(
                name="Savoir",
                instructions=INSTRUCTIONS,
                tools=tools,
                model="gpt-4.1",
            )
            
            # Store the assistant ID
            self.assistant_id = assistant.id
            log.info(f"Created new assistant with ID: {self.assistant_id}")
            
            # Update root .env file with the new assistant ID
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
            with open(env_path, 'a') as f:
                f.write(f'\nOPENAI_ASSISTANT_ID={self.assistant_id}\n')
                
            return assistant
            
        except Exception as e:
            log.error(f"Error getting/creating assistant: {str(e)}")
            raise
    
    def update_assistant(self):
        """Update the existing assistant with the latest instructions and tools from the files.
        
        Returns:
            Updated assistant info
        """
        try:
            # Import the latest instructions and tools
            from .instructions import INSTRUCTIONS
            from .tools import tools
            
            # Update the assistant with the latest instructions and tools
            log.info(f"Updating assistant: {self.assistant_id}")
            updated_assistant = self.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                instructions=INSTRUCTIONS,
                tools=tools
            )
            
            # Update the assistant object
            self.assistant = updated_assistant
            
            log.info(f"Successfully updated assistant with ID: {self.assistant_id}")
            return self.assistant
            
        except Exception as e:
            log.error(f"Error updating assistant: {str(e)}")
            raise
    
    async def get_or_create_thread(self, user_id: str):
        """Get existing thread for user or create a new one"""
        try:
            if user_id in self.user_threads:
                return {"success": True, "thread_id": self.user_threads[user_id]}
                
            thread = await self.async_client.beta.threads.create()
            self.user_threads[user_id] = thread.id
            return {"success": True, "thread_id": thread.id}
        except Exception as e:
            log.error(f"Error getting/creating thread: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def add_message_to_thread(self, thread_id: str, content: str):
        """Add a message to a thread"""
        try:
            message = await self.async_client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=content
            )
            return {"success": True, "message_id": message.id}
        except Exception as e:
            log.error(f"Error adding message to thread: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_assistant(self, thread_id: str):
        """Run the assistant on a thread"""
        try:
            run = await self.async_client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
            return {"success": True, "run_id": run.id}
        except Exception as e:
            log.error(f"Error running assistant: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_run_status(self, thread_id: str, run_id: str):
        """Get the status of a run"""
        try:
            run = await self.async_client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            return {"success": True, "status": run.status, "run": run}
        except Exception as e:
            log.error(f"Error getting run status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_thread_messages(self, thread_id: str):
        """Get messages from a thread."""
        try:
            messages = await self.async_client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=1
            )
            
            if not messages.data:
                log.error("No messages found in thread")
                return {"success": False, "error": "No messages found"}
                
            latest_message = messages.data[0]
            
            # Extract the message content
            message_content = ""
            for content in latest_message.content:
                if content.type == "text":
                    message_content = content.text.value
                    break
                    
            return {
                "success": True,
                "last_message": message_content,
                "message_id": latest_message.id
            }
            
        except Exception as e:
            log.error(f"Error getting thread messages: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def handle_tool_calls(self, thread_id: str, run_id: str):
        """Handle tool calls from the assistant"""
        try:
            run = await self.async_client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if not run.required_action:
                return {"success": True, "status": "no_action_required"}
                
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                log.info(f"Executing function {function_name} with args {function_args}")
                
                # Call the appropriate function handler
                if function_name in function_handlers:
                    function_handler = function_handlers[function_name]
                    # Handle both async and sync functions
                    if asyncio.iscoroutinefunction(function_handler):
                        function_result = await function_handler(**function_args)
                    else:
                        function_result = function_handler(**function_args)
                    
                    log.info(f"Function {function_name} returned: {function_result}")
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(function_result)
                    })
                else:
                    log.error(f"Unknown function {function_name}")
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"error": f"Unknown function {function_name}"})
                    })
            
            # Submit the tool outputs
            await self.async_client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            
            return {"success": True, "status": "tool_outputs_submitted"}
            
        except Exception as e:
            log.error(f"Error handling tool calls: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def has_active_run(self, thread_id: str):
        """Check if there is an active run for the thread"""
        try:
            runs = await self.async_client.beta.threads.runs.list(
                thread_id=thread_id,
                limit=1,
                order="desc"
            )
            if runs.data:
                latest_run = runs.data[0]
                # Check for any status that indicates the run is still active
                if latest_run.status in ["in_progress", "queued", "requires_action"]:
                    return True
            return False
        except Exception as e:
            log.error(f"Error checking for active runs: {str(e)}")
            return False
    
    def _create_error_response(self, message="I'm sorry, I encountered an error processing your request. Please try again later."):
        """Create a standardized error response in OpenAI API format."""
        return {
            "id": "assistant-error",
            "object": "chat.completion",
            "created": int(time.time()),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": message
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    
    def _create_busy_response(self):
        """Create a response indicating the assistant is busy."""
        return {
            "id": "assistant-busy",
            "object": "chat.completion",
            "created": int(time.time()),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "I'm still processing your previous request. Please wait a moment before sending another message."
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    
    def _create_success_response(self, thread_id, content):
        """Create a successful response in OpenAI API format."""
        return {
            "id": f"assistant-{thread_id}",
            "object": "chat.completion",
            "created": int(time.time()),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    
    async def _process_run(self, thread_id, run_id):
        """Process a run and wait for completion."""
        max_iterations = 30  # Maximum number of iterations (30 * 2 seconds = 60 seconds)
        iteration = 0
        
        while iteration < max_iterations:
            status_result = await self.get_run_status(thread_id, run_id)
            if not status_result["success"]:
                return False, "Failed to get run status"
                
            status = status_result["status"]
            
            if status == "completed":
                return True, None
            elif status == "failed":
                return False, "Run failed"
            elif status == "requires_action":
                # Handle tool calls
                tool_result = await self.handle_tool_calls(thread_id, run_id)
                if not tool_result["success"]:
                    return False, "Failed to handle tool calls"
                
            # Wait before checking again
            await asyncio.sleep(2)
            iteration += 1
            
        if iteration >= max_iterations:
            return False, "Run timed out"
    
    async def run(self, user_message: str, user_id: str, thread_id: str = None):
        """Main function to handle user messages and run the assistant"""
        try:
            log.info(f"Processing message for user {user_id}")
            
            # Get or create thread for user
            thread_result = await self.get_or_create_thread(user_id)
            if not thread_result["success"]:
                return self._create_error_response()
            thread_id = thread_result["thread_id"]
            
            # Check for active runs
            if await self.has_active_run(thread_id):
                return self._create_busy_response()

            # Add the message to the thread
            msg_result = await self.add_message_to_thread(thread_id, user_message)
            if not msg_result["success"]:
                return self._create_error_response()
            
            # Run the assistant
            run_result = await self.run_assistant(thread_id)
            if not run_result["success"]:
                return self._create_error_response()
                
            # Process the run
            success, error_message = await self._process_run(thread_id, run_result["run_id"])
            if not success:
                return self._create_error_response(error_message or "Run failed")
                
            # Get the messages from the thread
            messages_result = await self.get_thread_messages(thread_id)
            if not messages_result["success"]:
                return self._create_error_response()
                
            # Return the assistant's response
            return self._create_success_response(
                thread_id, 
                messages_result.get("last_message", "")
            )
            
        except Exception as e:
            log.error(f"Error in run function: {str(e)}")
            return self._create_error_response()

# Create a singleton instance
assistant = OpenAIAssistant()

# For backward compatibility
get_or_create_assistant = assistant._get_or_create_assistant
update_assistant = assistant.update_assistant
get_or_create_thread = assistant.get_or_create_thread
add_message_to_thread = assistant.add_message_to_thread
run_assistant = assistant.run_assistant
get_run_status = assistant.get_run_status
get_thread_messages = assistant.get_thread_messages
handle_tool_calls = assistant.handle_tool_calls
has_active_run = assistant.has_active_run
run = assistant.run