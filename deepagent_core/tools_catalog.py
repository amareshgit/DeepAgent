"""Tools Catalog for DeepAgent

Implements all tools demonstrated across Notebooks 1 & 2:
- Tavily Web Search (Notebook 1)
- Custom @tool functions (Notebook 2): add_numbers, multiply_numbers, evaluate_expression
- Dynamic custom tool registration
"""
import os
import math
from typing import Literal, Optional, List, Dict, Any, Callable
from langchain_core.tools import tool, BaseTool
from tavily import TavilyClient


@tool
def add_numbers(a: int, b: int) -> int:
    """Add two integers together. Useful for basic math operations."""
    return a + b


@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together. Returns the product."""
    return a * b


@tool
def evaluate_expression(expression: str) -> str:
    """Safely evaluates a mathematical expression (e.g., 'sqrt(144) + 15 * 3' or 'cos(pi/3)').
    Allowed functions: sin, cos, tan, sqrt, log, log10, exp, pow, abs, round, pi, e.
    """
    safe_dict = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "pow": math.pow,
        "abs": abs,
        "round": round,
        "pi": math.pi,
        "e": math.e,
    }
    try:
        # Strip potential dangerous characters
        cleaned = expression.replace("__", "").replace("import", "").replace("lambda", "")
        # Evaluate within restricted scope
        res = eval(cleaned, {"__builtins__": {}}, safe_dict)
        return f"Result of '{expression}' = {res}"
    except Exception as exc:
        return f"Error evaluating expression '{expression}': {exc}"


def get_web_search_tool(api_key: Optional[str] = None):
    """Factory for creating Tavily web_search tool as demonstrated in Notebook 1."""
    key = api_key or os.getenv("TAVILY_API_KEY")
    if not key:
        return None

    try:
        tavily_client = TavilyClient(api_key=key)

        @tool
        def web_search(
            query: str,
            max_results: int = 5,
            topic: Literal["general", "sports", "news", "finance"] = "general",
            include_raw_content: bool = False,
        ) -> str:
            """Run a web search using Tavily to retrieve current, up-to-date web information and facts."""
            try:
                res = tavily_client.search(
                    query,
                    max_results=max_results,
                    include_raw_content=include_raw_content,
                    topic=topic,
                )
                results = res.get("results", [])
                if not results:
                    return f"No web search results found for: {query}"
                formatted = []
                for item in results:
                    title = item.get("title", "No Title")
                    url = item.get("url", "")
                    content = item.get("content", "")
                    formatted.append(f"### [{title}]({url})\n{content}\n")
                return "\n".join(formatted)
            except Exception as exc:
                return f"Tavily search error for '{query}': {exc}"

        return web_search
    except Exception:
        return None


def get_all_tools(
    enable_web_search: bool = True,
    enable_math_tools: bool = True,
    tavily_api_key: Optional[str] = None,
    custom_tools: Optional[List[BaseTool]] = None,
) -> List[Any]:
    """Assemble all selected tools for the DeepAgent."""
    tools: List[Any] = []

    if enable_math_tools:
        tools.extend([add_numbers, multiply_numbers, evaluate_expression])

    if enable_web_search:
        search_tool = get_web_search_tool(tavily_api_key)
        if search_tool:
            tools.append(search_tool)

    if custom_tools:
        tools.extend(custom_tools)

    return tools
