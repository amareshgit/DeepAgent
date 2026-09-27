"""Agent Factory for DeepAgent

Assembles and compiles the full DeepAgent graph with:
- Multi-provider chat models (OpenAI, Groq, Ollama, Google GenAI)
- Pluggable backends (FilesystemBackend, StoreBackend, StateBackend)
- Dynamic tools (Tavily search, Math tools, Custom tools)
- Persistent project memory (AGENTS.md)
- Domain skills (Python, LangGraph, AWS, Technical Writing)
- Subagent delegation swarm (researcher, math, python, langgraph)
- Multi-turn conversational checkpointer (MemorySaver)
"""
import os
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from .backends_manager import BackendManager, BackendType
from .tools_catalog import get_all_tools, add_numbers, multiply_numbers, evaluate_expression, get_web_search_tool
from .skills_manager import SkillsCatalog
from .memory_manager import DEFAULT_MEMORY_FILE


DEFAULT_SYSTEM_PROMPTS = {
    "Autonomous Researcher": (
        "You are an expert autonomous Deep Agent and research scientist. "
        "Decompose multi-step questions, synthesize citations, and verify data. "
        "When appropriate, leverage subagents for focused deep research, file operations, "
        "or mathematical computation."
    ),
    "Deep Software Architect": (
        "You are a Principal Software Architect specializing in AI agent frameworks, "
        "LangGraph, modern Python, and distributed systems. Follow best practices, "
        "refer to loaded domain skills, and provide clean, production-grade code."
    ),
    "Full-Stack Agent Coordinator": (
        "You are a versatile Deep Agent swarm coordinator. Plan tasks step by step, "
        "delegate domain sub-tasks to specialized subagents using the task tool, and "
        "manage project state cleanly through your filesystem and persistent memory."
    ),
    "Custom": ""
}


def get_available_models() -> Dict[str, List[str]]:
    """Return catalog of supported model providers and models."""
    return {
        "OpenAI": [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4.1-mini",
            "o3-mini",
        ],
        "Groq": [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
        ],
        "Ollama (Local)": [
            "qwen3:4b",
            "llama3.2",
            "llama3",
            "mistral",
            "deepseek-r1",
        ],
        "Google GenAI": [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.1-pro-preview",
            "gemini-flash-latest",
            "gemini-pro-latest",
        ],
    }


def build_subagents(
    enable_researcher: bool = True,
    enable_math: bool = True,
    enable_python: bool = True,
    enable_langgraph: bool = True,
    tavily_api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Assemble subagents for delegation via the task tool."""
    subagents = []

    if enable_researcher:
        search_tool = get_web_search_tool(tavily_api_key)
        subagents.append({
            "name": "research_specialist",
            "description": "Performs deep web research, verifies facts, and retrieves live web data via Tavily",
            "system_prompt": "You are a research specialist. Search the web thoroughly, corroborate facts, and cite sources.",
            "tools": [search_tool] if search_tool else [],
        })

    if enable_math:
        subagents.append({
            "name": "math_specialist",
            "description": "Performs precision calculations, arithmetic evaluation, and mathematical analysis",
            "system_prompt": "You are a math computation specialist. Solve calculations step by step using your tools.",
            "tools": [add_numbers, multiply_numbers, evaluate_expression],
        })

    if enable_python:
        subagents.append({
            "name": "python_specialist",
            "description": "Writes, reviews, and refactors modern Python (3.11-3.13), async code, and Pydantic schemas",
            "system_prompt": "You are a senior Python engineer adhering to clean architecture, typing, and modern standards.",
            "skills": ["deepagentsdemo/skills/python"] if os.path.exists("deepagentsdemo/skills/python") else [],
        })

    if enable_langgraph:
        subagents.append({
            "name": "langgraph_specialist",
            "description": "Architects StateGraph workflows, cyclic flows, multi-agent supervisors, and memory checkpointers",
            "system_prompt": "You are a LangGraph specialist. Design modular state graphs and resilient multi-agent patterns.",
            "skills": ["deepagentsdemo/skills/langgraph"] if os.path.exists("deepagentsdemo/skills/langgraph") else [],
        })

    return subagents


def create_configured_agent(
    provider: str = "OpenAI",
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.2,
    api_key: Optional[str] = None,
    system_prompt: str = "You are a Deep Agent.",
    backend_type: BackendType = BackendType.FILESYSTEM,
    backend_manager: Optional[BackendManager] = None,
    enable_web_search: bool = True,
    enable_math_tools: bool = True,
    tavily_api_key: Optional[str] = None,
    load_memory: bool = True,
    memory_path: str = DEFAULT_MEMORY_FILE,
    selected_skills: Optional[List[str]] = None,
    enable_subagents: bool = True,
    subagents_config: Optional[Dict[str, bool]] = None,
    checkpointer: Optional[MemorySaver] = None,
) -> Tuple[Any, Optional[Any]]:
    """Builds and returns (compiled_agent, backend_store)."""
    # 1. Resolve API key & environment
    if api_key:
        if provider == "OpenAI":
            os.environ["OPENAI_API_KEY"] = api_key
        elif provider == "Groq":
            os.environ["GROQ_API_KEY"] = api_key
        elif provider == "Google GenAI":
            os.environ["GOOGLE_API_KEY"] = api_key

    # 2. Initialize chat model
    provider_map = {
        "OpenAI": "openai",
        "Groq": "groq",
        "Ollama (Local)": "ollama",
        "Google GenAI": "google_genai",
    }
    model_provider = provider_map.get(provider, "openai")

    try:
        model = init_chat_model(
            model=model_name,
            model_provider=model_provider,
            temperature=temperature,
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to initialize chat model {model_name} ({provider}): {exc}")

    # 3. Setup Backend
    bm = backend_manager or BackendManager()
    backend, store = bm.get_backend(backend_type)

    # 4. Setup Tools
    tools = get_all_tools(
        enable_web_search=enable_web_search,
        enable_math_tools=enable_math_tools,
        tavily_api_key=tavily_api_key,
    )

    # 5. Setup Skills
    skills_paths: List[str] = []
    if selected_skills:
        catalog = SkillsCatalog()
        skills_paths = catalog.get_skill_paths(selected_skills)
    elif selected_skills is None:
        # Default load all skills if directory exists
        if os.path.exists("deepagentsdemo/skills"):
            skills_paths = ["deepagentsdemo/skills"]

    # 6. Setup Memory
    memory_paths: List[str] = []
    if load_memory and os.path.exists(memory_path):
        memory_paths = [memory_path]

    # 7. Setup Subagents
    subagents_list = []
    if enable_subagents:
        cfg = subagents_config or {
            "researcher": enable_web_search,
            "math": enable_math_tools,
            "python": True,
            "langgraph": True,
        }
        subagents_list = build_subagents(
            enable_researcher=cfg.get("researcher", False),
            enable_math=cfg.get("math", False),
            enable_python=cfg.get("python", False),
            enable_langgraph=cfg.get("langgraph", False),
            tavily_api_key=tavily_api_key,
        )

    # 8. Checkpointer
    cp = checkpointer if checkpointer is not None else MemorySaver()

    # 9. Create DeepAgent
    agent = create_deep_agent(
        model=model,
        tools=tools if tools else None,
        system_prompt=system_prompt,
        subagents=subagents_list if subagents_list else None,
        skills=skills_paths if skills_paths else None,
        memory=memory_paths if memory_paths else None,
        backend=backend,
        checkpointer=cp,
        store=store,
    )

    return agent, store
