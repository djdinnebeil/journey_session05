"""
Chat API Endpoint

This module contains the chat endpoint for the LangGraph agent.
It handles incoming chat requests and returns agent responses.
"""

from fastapi import HTTPException
from pydantic import BaseModel
from typing import List

# Import with fallback for both local and Vercel environments
try:
    from .agent import create_agent, run_agent, get_global_agent
except ImportError:
    # Fallback for local development
    from api.agent import create_agent, run_agent, get_global_agent


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    openai_api_key: str = None  # Optional API key from frontend


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    tool_calls: List[str] = []


async def handle_chat(request: ChatRequest) -> ChatResponse:
    """
    Handle a chat request with the LangGraph agent.
    
    Args:
        request: ChatRequest containing message and optional API key
        
    Returns:
        ChatResponse with agent response and tool calls
        
    Raises:
        HTTPException: If API key is missing or agent execution fails
    """
    try:
        # Use the provided API key or fall back to global initialization
        if request.openai_api_key:
            # Initialize agent with the provided API key for this request
            current_agent = create_agent(request.openai_api_key)
        elif get_global_agent():
            # Use the globally initialized agent
            current_agent = get_global_agent()
        else:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key is required. Either provide it in the request or set OPENAI_API_KEY environment variable."
            )
        
        # Run the agent with the message
        result = await run_agent(current_agent, request.message)
        
        return ChatResponse(
            response=result["response"],
            tool_calls=result["tool_calls"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing request: {str(e)}"
        ) 