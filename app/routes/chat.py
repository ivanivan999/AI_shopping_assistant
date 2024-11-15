# app/routes/chat.py
from flask import Blueprint, jsonify, request, render_template, session
from app.services import create_graph
from langchain_core.messages import ToolMessage, AIMessage
import uuid, logging, json
from config import ChatConfig
from datetime import datetime


bp = Blueprint('chat', __name__)

logger = logging.getLogger(__name__)

@bp.route('/', methods=['GET'])
def chat_page():
    session['chat_id'] = str(uuid.uuid4())
    return render_template('chat.html')

@bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '').strip()
        if not data or 'message' not in data:
            return jsonify({
                "status": "error",
                "message": "No message provided"
            }), 400

        chat_id = session.get('chat_id', str(uuid.uuid4()))
        session['chat_id'] = chat_id

        config = ChatConfig.from_request(
            user_id=data.get('user_id'),
            thread_id=chat_id
        )
        
        graph = create_graph()
        # Send welcome message on first message
        if not session.get('welcomed'):
            initial_result = graph.invoke(
                {},
                config,
                stream_mode="values"
            )
            session['welcomed'] = True
            formatted_messages = []
            if initial_result and "messages" in initial_result:
                formatted_messages.append({
                    "role": "assistant",
                    "content": initial_result["messages"][0][1],
                    "timestamp": datetime.now().isoformat()
                })
                
        # Handle pending tool approval
        pending_tool = session.get('pending_tool')
        if pending_tool and message.lower() == 'y':
            # result = graph.invoke(None, config)
            print("1")
            print(pending_tool)
            result = graph.invoke(
                {
                    "messages": [
                        AIMessage(
                            content="",
                            tool_calls=[{
                                "id": pending_tool["id"],
                                "name": pending_tool["name"],
                                "args": pending_tool["arguments"]
                            }]
                        ),
                        # Add corresponding tool response message
                        ToolMessage(
                            content="",
                            tool_call_id=pending_tool["id"]
                        )
                    ]
                },
                config,
                interrupt_before=["sensitive_tools"]
            )
            session.pop('pending_tool', None)
            return handle_tool_result(result)

        events = graph.stream(
            {"messages": ("user", data.get('message'))},
            config,
            stream_mode="values"
        )

        return handle_chat_response(events, graph, config)
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
        

def handle_tool_result(result: dict) -> dict:
    """Handle the result of a tool execution"""
    formatted_messages = []
    
    if isinstance(result, dict) and "messages" in result:
        for msg in result["messages"]:
            if hasattr(msg, 'content'):
                formatted_messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                })
    
    return jsonify({
        "status": "success",
        "messages": formatted_messages
    })

def handle_chat_response(events, graph, config) -> dict:
    """Handle regular chat messages and format response"""
    formatted_messages = []
    
    # Process stream events
    for event in events:
        if event.get("messages"):
            msg = event["messages"][-1]
            if hasattr(msg, 'content'):
                formatted_messages.append({
                    "role": "assistant" if hasattr(msg, 'tool_calls') else "tool",
                    "content": msg.content,
                    "timestamp": datetime.now().isoformat()
                })
    
    # Check for pending tools
    snapshot = graph.get_state(config)
    if snapshot.next:
        state_values = snapshot.values
        if state_values and "messages" in state_values:
            last_message = state_values["messages"][-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                tool_call = last_message.tool_calls[0]
                # print(tool_call)
                session['pending_tool'] = {
                    'name': tool_call["name"],
                    'arguments': tool_call["args"],
                    'id': tool_call["id"]
                }
                
                # Add approval request
                formatted_messages.append({
                    "role": "assistant",
                    "content": f"Would you like me to {tool_call['name']} with these parameters? Type 'y' to approve.",
                    "timestamp": datetime.now().isoformat()
                })
    
    return jsonify({
        "status": "success",
        "messages": formatted_messages
    })