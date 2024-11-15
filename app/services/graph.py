# app/services/graph.py

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from app.utils.tools import (
    create_tool_node_with_fallback,
    part_3_safe_tools,
    part_3_sensitive_tools,
    sensitive_tool_names,
    fetch_customer_relate_information
)
from app.services.assistant import Assistant, part_3_assistant_runnable
from app.models.state import State

def create_graph():
    """Create processing graph with tool routing"""
    
    # Initialize graph
    builder = StateGraph(State)

    def welcome(state: State):
        """Welcome message node"""
        return {
            "messages": [
                ("assistant", """Welcome to the Shopping Assistant! 
                I can help you:
                - Search for products
                - Manage your shopping cart
                - Track orders
                - Provide recommendations
                
                How can I assist you today?""")
            ]
        }

    def user_info(state: State):
        return {"user_info": fetch_customer_relate_information.invoke({})}

    # Add nodes
    builder.add_node("welcome", welcome)
    builder.add_node("fetch_user_info", user_info)
    builder.add_node("assistant", Assistant(part_3_assistant_runnable))
    builder.add_node("safe_tools", create_tool_node_with_fallback(part_3_safe_tools))
    builder.add_node("sensitive_tools", create_tool_node_with_fallback(part_3_sensitive_tools))

    # Update edges to include welcome
    builder.add_edge(START, "welcome")
    builder.add_edge("welcome", "fetch_user_info")
    builder.add_edge("fetch_user_info", "assistant")

    def route_tools(state: State):
        next_node = tools_condition(state)
        # If no tools are invoked or next_node is None, return END
        if next_node == END:
            return END
        ai_message = state["messages"][-1]
        # Check if tool_calls exist in the last message
        if not getattr(ai_message, 'tool_calls', None):
            return END  # No tool calls, end the conversation
        # This assumes single tool calls
        first_tool_call = ai_message.tool_calls[0]
        if first_tool_call["name"] in sensitive_tool_names:
            return "sensitive_tools"
        return "safe_tools"

    # Add edges with routing
    builder.add_conditional_edges(
        "assistant",
        route_tools,
        ["safe_tools", "sensitive_tools", END]
    )
    builder.add_edge("safe_tools", "assistant")
    builder.add_edge("sensitive_tools", "assistant")

    # Setup memory and compile
    memory = MemorySaver()
    return builder.compile(
        checkpointer=memory,
        interrupt_before=["sensitive_tools"]
    )
