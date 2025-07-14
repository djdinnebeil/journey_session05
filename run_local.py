#!/usr/bin/env python3
"""
Local Development Runner for LangGraph Agent API

This script runs the FastAPI application locally for development and testing.
It handles the import paths correctly and starts the uvicorn server.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path for proper imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def main():
    """Run the FastAPI application locally."""
    # Import here to ensure path is set up first
    import uvicorn
    
    print("🚀 Starting LangGraph Agent API locally...")
    print("📱 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🔧 Health check: http://localhost:8000/health")
    print("💬 Chat endpoint: http://localhost:8000/chat")
    print("\n" + "="*50)
    
    # Check for OpenAI API key
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key found in environment")
    else:
        print("⚠️  No OpenAI API key found in environment")
        print("   You can provide it via requests or set OPENAI_API_KEY")
    
    print("="*50 + "\n")
    print("📋 Backend output will appear below:")
    print("   - Tool calls will be logged with [TOOL] prefix")
    print("   - Agent reasoning will be visible")
    print("   - HTTP requests will be logged")
    print("-" * 50)
    
    # Run the application using import string for proper reload and logging
    uvicorn.run(
        "api.main:app",  # Import string instead of app object
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info",  # Show all info logs
        access_log=True,  # Show HTTP access logs
        use_colors=True,  # Colorful output
    )

if __name__ == "__main__":
    main() 