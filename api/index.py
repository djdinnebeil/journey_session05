"""
Vercel Function Entry Point

This file makes the FastAPI app available as a Vercel serverless function.
It handles the import and initialization properly for the serverless environment.
"""

import os
import sys
from pathlib import Path

# Ensure proper path setup for Vercel
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    # Import the FastAPI app
    from main import app
    
    # Export for Vercel
    __all__ = ["app"]
    
except Exception as e:
    # Fallback app for debugging
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/")
    async def error_handler():
        return JSONResponse(
            status_code=500,
            content={
                "error": "Import failed",
                "details": str(e),
                "message": "Check Vercel logs for more details"
            }
        )
    
    @app.get("/health")
    async def health_check():
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "python_path": sys.path,
                "current_dir": str(current_dir),
                "files_in_dir": os.listdir(current_dir) if os.path.exists(current_dir) else []
            }
        ) 