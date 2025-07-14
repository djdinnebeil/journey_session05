"""
Main FastAPI Application

This is the main FastAPI application optimized for Vercel serverless deployment.
It handles the LangGraph agent functionality with proper error handling.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Global agent instance
_global_agent = None

# Create FastAPI app
app = FastAPI(
    title="LangGraph Agent API",
    description="A FastAPI application with LangGraph agent integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    api_key: Optional[str] = None
    openai_api_key: Optional[str] = None  # Frontend compatibility

class ChatResponse(BaseModel):
    response: str
    tool_calls: list[str] = []

def initialize_agent_if_needed():
    """Lazy initialization of the agent"""
    global _global_agent
    if _global_agent is None:
        try:
            # Import dependencies here for lazy loading
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage
            from langgraph.graph import StateGraph, END
            from langgraph.graph.message import add_messages
            from langgraph.prebuilt import ToolNode
            from typing import TypedDict, Annotated
            
            # Import tools with fallback
            try:
                from tools import AVAILABLE_TOOLS
            except ImportError:
                from .tools import AVAILABLE_TOOLS
            
            # Agent State
            class AgentState(TypedDict):
                messages: Annotated[list, add_messages]
            
            # Create the graph
            workflow = StateGraph(AgentState)
            
            def call_model(state: AgentState):
                """Call the language model with tools"""
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    # For demo purposes, return a mock response
                    return {
                        "messages": [
                            HumanMessage(content="I need an OpenAI API key to function properly. Please provide one in your request or set the OPENAI_API_KEY environment variable.")
                        ]
                    }
                
                model = ChatOpenAI(
                    api_key=api_key,
                    model="gpt-3.5-turbo",
                    temperature=0.7
                ).bind_tools(AVAILABLE_TOOLS)
                
                response = model.invoke(state["messages"])
                return {"messages": [response]}
            
            def should_continue(state: AgentState):
                """Check if we should continue with tool calls"""
                messages = state["messages"]
                last_message = messages[-1]
                if last_message.tool_calls:
                    return "tools"
                return END
            
            # Define the nodes
            workflow.add_node("agent", call_model)
            workflow.add_node("tools", ToolNode(AVAILABLE_TOOLS))
            
            # Set entry point
            workflow.set_entry_point("agent")
            
            # Add conditional edges
            workflow.add_conditional_edges("agent", should_continue)
            workflow.add_edge("tools", "agent")
            
            # Compile the graph
            _global_agent = workflow.compile()
            logger.info("✅ Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            _global_agent = None
    
    return _global_agent

@app.get("/")
async def root():
    """Serve the frontend HTML"""
    try:
        # Try to serve the HTML file
        html_path = "public/index.html"
        if os.path.exists(html_path):
            return FileResponse(html_path)
        
        # Try alternative path for Vercel
        alt_path = "../public/index.html"
        if os.path.exists(alt_path):
            return FileResponse(alt_path)
        
        # Fallback to JSON response
        return JSONResponse({
            "message": "LangGraph Agent API is running!",
            "status": "healthy",
            "endpoints": {
                "chat": "/chat",
                "health": "/health",
                "docs": "/docs"
            }
        })
    except Exception as e:
        return JSONResponse({
            "message": "LangGraph Agent API is running!",
            "status": "healthy",
            "note": f"Frontend file not found: {e}"
        })

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        agent = initialize_agent_if_needed()
        return JSONResponse({
            "status": "healthy",
            "agent_initialized": agent is not None,
            "environment_api_key": bool(os.getenv("OPENAI_API_KEY")),
            "python_version": sys.version,
            "tools_available": True
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "agent_initialized": False
        })

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the LangGraph agent"""
    try:
        logger.info(f"💬 Received message: {request.message[:100]}...")
        
        # Check for API key (handle both field names)
        api_key = request.api_key or request.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            return ChatResponse(
                response="I need an OpenAI API key to function. Please provide one in your request or set the OPENAI_API_KEY environment variable.",
                tool_calls=[]
            )
        
        # Set the API key temporarily if provided in request
        if api_key and api_key != os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = api_key
            logger.info("🔑 Using API key from request")
        
        # Initialize agent
        agent = initialize_agent_if_needed()
        if not agent:
            return ChatResponse(
                response="Sorry, I'm having trouble initializing. Please check the logs.",
                tool_calls=[]
            )
        
        # Import here for lazy loading
        from langchain_core.messages import HumanMessage
        
        # Run the agent
        result = agent.invoke({
            "messages": [HumanMessage(content=request.message)]
        })
        
        # Extract response and tool calls
        messages = result["messages"]
        final_message = messages[-1]
        
        tool_calls = []
        for msg in messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_calls.extend([tc["name"] for tc in msg.tool_calls])
        
        response = final_message.content if hasattr(final_message, 'content') else str(final_message)
        
        logger.info(f"🤖 Response generated successfully")
        
        return ChatResponse(
            response=response,
            tool_calls=list(set(tool_calls))  # Remove duplicates
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def get_available_tools():
    """Get list of available tools"""
    try:
        # Import tools with fallback
        try:
            from tools import TOOL_DESCRIPTIONS
        except ImportError:
            from .tools import TOOL_DESCRIPTIONS
        return {"tools": TOOL_DESCRIPTIONS}
    except Exception as e:
        return {"tools": [], "error": str(e)}

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 