"""
LangGraph Agent Tools

This module contains all the tool definitions for the LangGraph agent.
Each tool is decorated with @tool and provides specific functionality.
"""

import random
import requests
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """Returns a dummy weather report for a given city."""
    return f"The weather in {city} is sunny with a temperature of 22°C (72°F). Perfect day to go outside!"


@tool
def wiki_search(query: str) -> str:
    """Searches Wikipedia for a summary of the given query."""
    try:
        response = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("extract", "No summary available.")
        else:
            return f"Wiki search failed with status code: {response.status_code}"
    except Exception as e:
        return f"Wiki search failed: {str(e)}"


@tool
def fun_fact(topic: str) -> str:
    """Returns a fun fact about the given topic."""
    facts = {
        "pizza": "Did you know that pizza was invented in Naples, Italy, and the first pizzeria opened in 1830?",
        "ocean": "Did you know that we have explored less than 5% of our oceans?",
        "space": "Did you know that a day on Venus is longer than its year?",
        "cats": "Did you know that cats have 32 muscles in each ear?",
        "default": f"Did you know that {topic} has a fascinating history filled with interesting discoveries?"
    }
    return facts.get(topic.lower(), facts["default"])


@tool
def random_color(colors: list[str]) -> str:
    """Randomly selects a color from a given list of strings."""
    if not colors:
        return "No colors provided to choose from."
    
    selected = random.choice(colors)
    return f"I randomly selected: {selected} from the list {colors}"


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