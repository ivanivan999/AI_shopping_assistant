# app/utils/tools.py

from langchain_core.tools import Tool
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from langchain_core.runnables import RunnableLambda

from typing import List, Dict, Any
from app.models.product import search_products,search_products_with_recommendations
from app.models.cart import add_product_to_cartitems, remove_product_from_cartitems
from app.models.order import fetch_customer_relate_information

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


# "Read"-only tools (such as retrievers) don't need a user confirmation to use
part_3_safe_tools = [
    # TavilySearchResults(max_results=1),
    fetch_customer_relate_information,
    search_products,
    search_products_with_recommendations
]

# These tools all change the user's reservations.
# The user has the right to control what decisions are made
part_3_sensitive_tools = [
    add_product_to_cartitems,
    remove_product_from_cartitems,
]
sensitive_tool_names = {t.name for t in part_3_sensitive_tools}
