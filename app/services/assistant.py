# app/services/assistant.py
import os
from datetime import datetime
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.utils.tools import part_3_safe_tools, part_3_sensitive_tools
from app.models.state import State
from langchain_core.runnables import RunnableConfig

# Initialize LLM
llm = ChatOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://chatapi.littlewheat.com/v1/",
    model="gpt-3.5-turbo-0125",
    temperature=0.7,
    verbose=True
)

# Assistant prompt template
assistant_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""
    You are a helpful customer support assistant. 
    When showing search results:
    1. ALWAYS start with "I found X items matching your search:"
    2. List EVERY product in numbered format
    3. Use consistent formatting for each product:
    ```
    N. [Product Name]
       - Description: [Description]
       - Price: $[Price]
       - Stock: [Inventory] units available
    ```
    4. After listing all items, add a comparison section:
       - Price comparison
       - Feature comparison
       - Best value recommendation
    
    Shopping cart management is also available. You can add and remove products.
    Order tracking and history are available. 
    You can provide recommendations based on preferences.
    
    Current user: {user_info}
    Current time: {time}
    """),
    ("placeholder", "{messages}")
]).partial(time=datetime.now)

# Create assistant runnable with tools
part_3_assistant_runnable = (
    assistant_prompt 
    | llm.bind_tools(tools=part_3_safe_tools + part_3_sensitive_tools)
)

class Assistant:
    def __init__(self, runnable):
        self.runnable = runnable
        
    def __call__(self, state: State, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content or
                isinstance(result.content, list) and 
                not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}