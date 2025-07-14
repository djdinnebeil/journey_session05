"""
Vercel Function Entry Point

This file makes the FastAPI app available as a Vercel function.
It imports the main FastAPI app from the modular API structure.
"""

# Import with fallback for both local and Vercel environments
try:
    from .main import app
except ImportError:
    # Fallback for local development
    from api.main import app

# Export the app for Vercel
__all__ = ["app"] 