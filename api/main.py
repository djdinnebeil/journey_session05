"""
Main FastAPI Application

This is the main FastAPI application that orchestrates all the API endpoints
and handles the LangGraph agent functionality.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging to show backend activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path for local development
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import with fallback for both local and Vercel environments
try:
    from .chat import handle_chat, ChatRequest, ChatResponse
    from .tools import TOOL_DESCRIPTIONS
    from .agent import initialize_global_agent, get_global_agent
except ImportError:
    # Fallback for local development
    from api.chat import handle_chat, ChatRequest, ChatResponse
    from api.tools import TOOL_DESCRIPTIONS
    from api.agent import initialize_global_agent, get_global_agent


# Create FastAPI app
app = FastAPI(
    title="LangGraph Agent API",
    description="A LangGraph agent with multiple tools deployed on Vercel",
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

# Serve static files (adjusted for Vercel deployment)
try:
    # For Vercel, the public directory structure might be different
    import os
    static_dir = "public" if os.path.exists("public") else "../public"
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
except (RuntimeError, OSError):
    # In case public directory doesn't exist or isn't accessible
    print("Warning: Could not mount static files directory")


@app.on_event("startup")
async def startup_event():
    """Initialize the agent when the app starts (if API key is in environment)"""
    logger.info("🤖 Initializing LangGraph agent...")
    print("🤖 Initializing LangGraph agent...")
    initialize_global_agent()
    logger.info("✅ Agent initialized successfully!")
    print("✅ Agent initialized successfully!")


@app.get("/")
async def root():
    """Serve the frontend HTML"""
    try:
        # Try different paths for Vercel deployment
        html_paths = ["public/index.html", "../public/index.html"]
        for path in html_paths:
            if os.path.exists(path):
                return FileResponse(path)
        # If no HTML file found, return JSON response
        return {"message": "LangGraph Agent API is running!", "status": "healthy"}
    except FileNotFoundError:
        return {"message": "LangGraph Agent API is running!", "status": "healthy"}


@app.get("/api")
async def api_root():
    """API health check endpoint"""
    return {"message": "LangGraph Agent API is running!", "status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the LangGraph agent"""
    logger.info(f"💬 Received chat request: {request.message[:100]}...")
    print(f"💬 Incoming message: {request.message[:100]}...")
    response = await handle_chat(request)
    logger.info(f"🤖 Agent response: {response.response[:100]}...")
    print(f"🤖 Sending response: {response.response[:100]}...")
    return response


@app.get("/tools")
async def get_available_tools():
    """Get list of available tools"""
    return {"tools": TOOL_DESCRIPTIONS}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    global_agent = get_global_agent()
    return {
        "status": "healthy",
        "model_initialized": global_agent is not None,
        "graph_compiled": global_agent is not None,
        "tools_available": len(TOOL_DESCRIPTIONS),
        "environment_api_key": bool(os.getenv("OPENAI_API_KEY"))
    }


# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 