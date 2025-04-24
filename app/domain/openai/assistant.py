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

# Load environment variables from root .env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
log.info(f"Loading environment from: {env_path}")
load_dotenv(dotenv_path=env_path, override=True)  # override=True to ensure we use root .env values

# Initialize OpenAI clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get assistant ID from environment variable or create new assistant
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
log.info(f"Loaded OPENAI_ASSISTANT_ID from env: {ASSISTANT_ID}")

def get_or_create_assistant():
    """Get existing assistant or create a new one if it doesn't exist."""
    global ASSISTANT_ID
    
    try:
        if ASSISTANT_ID:
            log.info(f"Attempting to retrieve assistant with ID: {ASSISTANT_ID}")
            # Try to retrieve the existing assistant
            assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
            log.info(f"Retrieved existing assistant: {ASSISTANT_ID}")
            return assistant
            
        # Create new assistant if none exists
        log.info("No assistant ID found, creating new assistant")
        assistant = client.beta.assistants.create(
            name="Savoir",
            instructions=INSTRUCTIONS,
            tools=tools,
            model="gpt-4.1",
        )
        
        # Store the assistant ID
        ASSISTANT_ID = assistant.id
        log.info(f"Created new assistant with ID: {ASSISTANT_ID}")
        
        # Update root .env file with the new assistant ID
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
        log.info(f"Writing new assistant ID to: {env_path}")
        with open(env_path, 'a') as f:
            f.write(f'\nOPENAI_ASSISTANT_ID={ASSISTANT_ID}\n')
            
        return assistant
        
    except Exception as e:
        log.error(f"Error getting/creating assistant: {str(e)}")
        raise

# Initialize the assistant
assistant = get_or_create_assistant()

# Store user threads
user_threads = {}

def update_assistant():
    """Update the existing assistant with the latest instructions and tools from the files.
    
    Returns:
        Updated assistant info
    """
    global assistant
    
    try:
        # Import the latest instructions and tools
        from .instructions import INSTRUCTIONS
        from .tools import tools
        
        # Update the assistant with the latest instructions and tools
        log.info(f"Updating assistant: {ASSISTANT_ID}")
        updated_assistant = client.beta.assistants.update(
            assistant_id=ASSISTANT_ID,
            instructions=INSTRUCTIONS,
            tools=tools
        )
        
        # Update the global assistant object
        assistant = updated_assistant
        
        log.info(f"Successfully updated assistant with ID: {ASSISTANT_ID}")
        return assistant
        
    except Exception as e:
        log.error(f"Error updating assistant: {str(e)}")
        raise

async def get_or_create_thread(user_id: str):
    """Get existing thread for user or create a new one"""
    try:
        if user_id in user_threads:
            return {"success": True, "thread_id": user_threads[user_id]}
            
        thread = await async_client.beta.threads.create()
        user_threads[user_id] = thread.id
        return {"success": True, "thread_id": thread.id}
    except Exception as e:
        log.error(f"Error getting/creating thread: {str(e)}")
        return {"success": False, "error": str(e)}

async def add_message_to_thread(thread_id: str, content: str):
    """Add a message to a thread"""
    try:
        message = await async_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )
        return {"success": True, "message_id": message.id}
    except Exception as e:
        log.error(f"Error adding message to thread: {str(e)}")
        return {"success": False, "error": str(e)}

async def run_assistant(thread_id: str):
    """Run the assistant on a thread"""
    try:
        run = await async_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        return {"success": True, "run_id": run.id}
    except Exception as e:
        log.error(f"Error running assistant: {str(e)}")
        return {"success": False, "error": str(e)}

async def get_run_status(thread_id: str, run_id: str):
    """Get the status of a run"""
    try:
        run = await async_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        return {"success": True, "status": run.status, "run": run}
    except Exception as e:
        log.error(f"Error getting run status: {str(e)}")
        return {"success": False, "error": str(e)}

async def get_thread_messages(thread_id: str):
    """Get messages from a thread."""
    try:
        messages = await async_client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )
        
        if not messages.data:
            log.error("No messages found in thread")
            return {"success": False, "error": "No messages found"}
            
        latest_message = messages.data[0]
        log.info(f"Got latest message: {latest_message.id}")
        
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

async def handle_tool_calls(thread_id: str, run_id: str):
    """Handle tool calls from the assistant"""
    try:
        run = await async_client.beta.threads.runs.retrieve(
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
        await async_client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )
        
        return {"success": True, "status": "tool_outputs_submitted"}
        
    except Exception as e:
        log.error(f"Error handling tool calls: {str(e)}")
        return {"success": False, "error": str(e)}

async def has_active_run(thread_id: str):
    """Check if there is an active run for the thread"""
    try:
        runs = await async_client.beta.threads.runs.list(
            thread_id=thread_id,
            limit=1,
            order="desc"
        )
        if runs.data:
            latest_run = runs.data[0]
            log.info(f"Latest run status: {latest_run.status}")
            # Check for any status that indicates the run is still active
            if latest_run.status in ["in_progress", "queued", "requires_action"]:
                return True
        return False
    except Exception as e:
        log.error(f"Error checking for active runs: {str(e)}")
        return False

async def run(user_message: str, user_id: str, thread_id: str = None):
    """Main function to handle user messages and run the assistant"""
    try:
        log.info(f"Processing message for user {user_id}: {user_message}")
        
        # Get or create thread for user
        thread_result = await get_or_create_thread(user_id)
        if not thread_result["success"]:
            log.error(f"Failed to get/create thread: {thread_result.get('error')}")
            return {
                "id": "assistant-error",
                "object": "chat.completion",
                "created": int(time.time()),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I'm sorry, I encountered an error processing your request. Please try again later."
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
        thread_id = thread_result["thread_id"]
        log.info(f"Using thread ID: {thread_id}")
        
        # Check for active runs
        if await has_active_run(thread_id):
            log.warning("Active run detected, waiting before processing new message")
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

        # Add the message to the thread
        msg_result = await add_message_to_thread(thread_id, user_message)
        if not msg_result["success"]:
            log.error(f"Failed to add message to thread: {msg_result.get('error')}")
            return {
                "id": "assistant-error",
                "object": "chat.completion",
                "created": int(time.time()),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I'm sorry, I encountered an error processing your request. Please try again later."
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
        log.info(f"Added message to thread: {msg_result.get('message_id')}")
        
        # Run the assistant
        run_result = await run_assistant(thread_id)
        if not run_result["success"]:
            log.error(f"Failed to run assistant: {run_result.get('error')}")
            return {
                "id": "assistant-error",
                "object": "chat.completion",
                "created": int(time.time()),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I'm sorry, I encountered an error processing your request. Please try again later."
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
        log.info(f"Started assistant run: {run_result.get('run_id')}")
            
        # Wait for the run to complete
        run_id = run_result["run_id"]
        max_iterations = 30  # Maximum number of iterations (30 * 2 seconds = 60 seconds)
        iteration = 0
        
        while iteration < max_iterations:
            status_result = await get_run_status(thread_id, run_id)
            if not status_result["success"]:
                log.error(f"Failed to get run status: {status_result.get('error')}")
                return {
                    "id": "assistant-error",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "I'm sorry, I encountered an error processing your request. Please try again later."
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
                
            status = status_result["status"]
            log.info(f"Run status: {status}")
            
            if status == "completed":
                break
            elif status == "failed":
                return {
                    "id": "assistant-error",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "I'm sorry, I encountered an error processing your request. Please try again later."
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
            elif status == "requires_action":
                # Handle tool calls
                tool_result = await handle_tool_calls(thread_id, run_id)
                if not tool_result["success"]:
                    log.error(f"Failed to handle tool calls: {tool_result.get('error')}")
                    return {
                        "id": "assistant-error",
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "content": "I'm sorry, I encountered an error processing your request. Please try again later."
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
                
            # Wait before checking again
            await asyncio.sleep(2)
            iteration += 1
            
        if iteration >= max_iterations:
            log.error(f"Run timed out after {max_iterations * 2} seconds")
            return {
                "id": "assistant-error",
                "object": "chat.completion",
                "created": int(time.time()),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I'm sorry, your request timed out. Please try again later."
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
            
        # Get the messages from the thread
        messages_result = await get_thread_messages(thread_id)
        if not messages_result["success"]:
            log.error(f"Failed to get thread messages: {messages_result.get('error')}")
            return {
                "id": "assistant-error",
                "object": "chat.completion",
                "created": int(time.time()),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I'm sorry, I encountered an error processing your request. Please try again later."
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
            
        # Return the assistant's response in OpenAI API format
        return {
            "id": f"assistant-{thread_id}",
            "object": "chat.completion",
            "created": int(time.time()),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": messages_result.get("last_message", "")
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
        
    except Exception as e:
        log.error(f"Error in run function: {str(e)}")
        return {
            "id": "assistant-error",
            "object": "chat.completion",
            "created": int(time.time()),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "I'm sorry, I encountered an error processing your request. Please try again later."
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