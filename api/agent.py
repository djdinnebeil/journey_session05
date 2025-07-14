"""
LangGraph Agent

This module contains the LangGraph agent initialization and execution logic.
It handles the creation and compilation of the agent graph with tools.
"""

import os
from typing import TypedDict, Annotated

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Import with fallback for both local and Vercel environments
try:
    from .tools import AVAILABLE_TOOLS
except ImportError:
    # Fallback for local development
    from api.tools import AVAILABLE_TOOLS


class AgentState(TypedDict):
    """State structure for the LangGraph agent."""
    messages: Annotated[list, add_messages]


def create_agent(api_key: str = None):
    """
    Create and compile a LangGraph agent with the provided API key.
    
    Args:
        api_key: OpenAI API key. If None, will try to get from environment.
        
    Returns:
        Compiled LangGraph agent ready for execution.
        
    Raises:
        ValueError: If no API key is provided and none found in environment.
    """
    # Get API key from parameter or environment variables
    openai_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key is required")
    
    # Initialize model with the provided API key
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)
    model = model.bind_tools(AVAILABLE_TOOLS)
    
    # Create tool node
    tool_node = ToolNode(AVAILABLE_TOOLS)
    
    # Define the agent node that calls the model
    def call_model(state):
        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages": [response]}
    
    # Build and compile the LangGraph
    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("action", tool_node)
    
    def decide_next(state):
        return "action" if state["messages"][-1].tool_calls else END
    
    graph.add_conditional_edges("agent", decide_next, {"action": "action", END: END})
    graph.add_edge("action", "agent")
    graph.set_entry_point("agent")
    
    return graph.compile()


async def run_agent(agent, message: str):
    """
    Run the agent with a given message and return the response.
    
    Args:
        agent: Compiled LangGraph agent
        message: User message to process
        
    Returns:
        Dictionary with 'response' and 'tool_calls' keys
    """
    # Prepare input for the agent
    inputs = {"messages": [HumanMessage(content=message)]}
    
    # Stream through the graph and collect responses
    tool_calls_made = []
    final_response = ""
    
    async for chunk in agent.astream(inputs, stream_mode="updates"):
        for node, values in chunk.items():
            if node == "action" and values.get("messages"):
                # Track tool calls
                for msg in values["messages"]:
                    if hasattr(msg, 'name'):
                        tool_calls_made.append(msg.name)
            elif node == "agent" and values.get("messages"):
                # Get the final response
                last_message = values["messages"][-1]
                if hasattr(last_message, 'content') and last_message.content:
                    final_response = last_message.content
    
    # If no final response was captured, get it from the last message
    if not final_response:
        final_state = agent.invoke(inputs)
        if final_state.get("messages"):
            final_response = final_state["messages"][-1].content
    
    return {
        "response": final_response or "I apologize, but I couldn't generate a response.",
        "tool_calls": tool_calls_made
    }


# Global agent instance (initialized at startup if API key is available)
_global_agent = None


def initialize_global_agent():
    """Initialize the global agent if an API key is available in environment."""
    global _global_agent
    try:
        if os.getenv("OPENAI_API_KEY"):
            _global_agent = create_agent()
            print("LangGraph agent initialized successfully with environment API key")
            return True
        else:
            print("No environment API key found - will require API key from requests")
            return False
    except Exception as e:
        print(f"Failed to initialize global agent: {e}")
        return False


def get_global_agent():
    """Get the global agent instance."""
    return _global_agent 