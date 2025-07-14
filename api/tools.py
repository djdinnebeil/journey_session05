"""
LangGraph Agent Tools

This module contains all the tool definitions for the LangGraph agent.
Each tool is decorated with @tool and provides specific functionality.
"""

import random
import requests
from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """Returns a dummy weather report for a given city."""
    return f"The weather in {city} is sunny."


@tool
def wiki_search(query: str) -> str:
    """Searches Wikipedia for a summary of the given query."""
    try:
        response = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        )
        data = response.json()
        return data.get("extract", "No summary available.")
    except Exception as e:
        return f"Wiki search failed: {e}"


@tool
def fun_fact(topic: str) -> str:
    """Returns a fun fact about the given topic."""
    return f"Did you know that {topic} has a fascinating history?"


@tool
def random_color(colors: list[str]) -> str:
    """Randomly selects a color from a given list of strings."""
    print(f"[TOOL] Choosing from: {colors}")
    return random.choice(colors) if colors else "No colors provided."


# Export all tools
AVAILABLE_TOOLS = [get_weather, wiki_search, fun_fact, random_color]

# Tool descriptions for API documentation
TOOL_DESCRIPTIONS = [
    {
        "name": "get_weather",
        "description": "Returns a dummy weather report for a given city"
    },
    {
        "name": "wiki_search", 
        "description": "Searches Wikipedia for a summary of the given query"
    },
    {
        "name": "fun_fact",
        "description": "Returns a fun fact about the given topic"
    },
    {
        "name": "random_color",
        "description": "Randomly selects a color from a given list of strings"
    }
] 