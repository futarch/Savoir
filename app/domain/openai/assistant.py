from openai import OpenAI, AsyncOpenAI
import os, json, asyncio, logging
from dotenv import load_dotenv
from .tools import tools, function_handlers
from .instructions import INSTRUCTIONS

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class OpenAIAssistant:
    def __init__(self, api_key=None, assistant_id=None):
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
        load_dotenv(dotenv_path=env_path, override=True)
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.assistant_id = assistant_id or os.getenv("OPENAI_ASSISTANT_ID")
        self.assistant = self._get_or_create_assistant()
        self.user_threads = {}
    
    def _get_or_create_assistant(self):
        try:
            if self.assistant_id:
                log.info(f"Retrieving assistant with ID: {self.assistant_id}")
                return self.client.beta.assistants.retrieve(self.assistant_id)
                
            log.info("No assistant ID found, creating new assistant")
            assistant = self.client.beta.assistants.create(
                name="Savoir",
                instructions=INSTRUCTIONS,
                tools=tools,
                model="gpt-4.1",
            )
            
            self.assistant_id = assistant.id
            log.info(f"Created new assistant with ID: {self.assistant_id}")
            
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
            with open(env_path, 'a') as f:
                f.write(f'\nOPENAI_ASSISTANT_ID={self.assistant_id}\n')
                
            return assistant
            
        except Exception as e:
            log.error(f"Error getting/creating assistant: {str(e)}")
            raise
    
    def update_assistant(self):
        try:
            from .instructions import INSTRUCTIONS
            from .tools import tools
            
            log.info(f"Updating assistant: {self.assistant_id}")
            self.assistant = self.client.beta.assistants.update(
                assistant_id=self.assistant_id,
                instructions=INSTRUCTIONS,
                tools=tools
            )
            
            log.info(f"Successfully updated assistant with ID: {self.assistant_id}")
            return self.assistant
            
        except Exception as e:
            log.error(f"Error updating assistant: {str(e)}")
            raise
    
    async def get_or_create_thread(self, user_id: str):
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
            message_content = next(
                (content.text.value for content in latest_message.content if content.type == "text"),
                None
            )
            
            return {
                "success": True,
                "last_message": message_content,
                "message_id": latest_message.id
            }
            
        except Exception as e:
            log.error(f"Error getting thread messages: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def handle_tool_calls(self, thread_id: str, run_id: str):
        try:
            run = await this.async_client.beta.threads.runs.retrieve(
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
                
                if function_name in function_handlers:
                    function_handler = function_handlers[function_name]
                    function_result = await function_handler(**function_args) if asyncio.iscoroutinefunction(function_handler) else function_handler(**function_args)
                    
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
            
            await this.async_client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
            
            return {"success": True, "status": "tool_outputs_submitted"}
            
        except Exception as e:
            log.error(f"Error handling tool calls: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def has_active_run(self, thread_id: str):
        try:
            runs = await this.async_client.beta.threads.runs.list(
                thread_id=thread_id,
                limit=1,
                order="desc"
            )
            if runs.data:
                latest_run = runs.data[0]
                return latest_run.status in ["queued", "in_progress"]
            return False
        except Exception as e:
            log.error(f"Error checking active run: {str(e)}")
            return False
    
    def _create_error_response(self, message="I'm sorry, I encountered an error processing your request. Please try again later."):
        return {
            "error": message,
            "choices": [{
                "message": {
                    "content": message
                }
            }]
        }
    
    def _create_busy_response(self):
        return {
            "error": "The assistant is currently busy processing another request. Please try again in a few moments.",
            "choices": [{
                "message": {
                    "content": "I'm currently busy processing another request. Please try again in a few moments."
                }
            }]
        }
    
    def _create_success_response(self, thread_id, content):
        return {
            "id": thread_id,
            "choices": [{
                "message": {
                    "content": content
                }
            }]
        }
    
    async def _process_run(self, thread_id, run_id):
        max_retries = 10
        retry_delay = 1
        
        for _ in range(max_retries):
            run_status = await this.get_run_status(thread_id, run_id)
            
            if not run_status["success"]:
                return this._create_error_response()
                
            status = run_status["status"]
            
            if status == "completed":
                messages = await this.get_thread_messages(thread_id)
                if messages["success"]:
                    return this._create_success_response(thread_id, messages["last_message"])
                return this._create_error_response()
                
            elif status == "requires_action":
                tool_result = await this.handle_tool_calls(thread_id, run_id)
                if not tool_result["success"]:
                    return this._create_error_response()
                    
            elif status in ["failed", "cancelled", "expired"]:
                return this._create_error_response()
                
            await asyncio.sleep(retry_delay)
            
        return this._create_error_response("The request timed out. Please try again.")
    
    async def run(self, user_message: str, user_id: str, thread_id: str = None):
        try:
            if await this.has_active_run(thread_id):
                return this._create_busy_response()
                
            thread_result = await this.get_or_create_thread(user_id)
            if not thread_result["success"]:
                return this._create_error_response()
                
            thread_id = thread_result["thread_id"]
            
            message_result = await this.add_message_to_thread(thread_id, user_message)
            if not message_result["success"]:
                return this._create_error_response()
                
            run_result = await this.run_assistant(thread_id)
            if not run_result["success"]:
                return this._create_error_response()
                
            return await this._process_run(thread_id, run_result["run_id"])
            
        except Exception as e:
            log.error(f"Error in run: {str(e)}")
            return this._create_error_response()

assistant = OpenAIAssistant()