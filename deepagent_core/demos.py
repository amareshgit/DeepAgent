"""Notebook Demos & Quick-Start Presets for DeepAgent

Provides ready-to-run scenarios inspired directly by the 4 notebooks in deepagentsdemo:
- Notebook 1: Basic Deep Agent & Tavily Web Search
- Notebook 2: Custom @tool Math Invocations
- Notebook 3: FilesystemBackend vs StoreBackend vs StateBackend
- Notebook 4: Context Engineering, Memory (AGENTS.md), and Subagent Delegation Swarm
"""
from typing import Dict, Any, List

NOTEBOOK_DEMOS: List[Dict[str, Any]] = [
    {
        "id": "nb1_basic",
        "title": "Notebook 1: Deep Agent & Tavily Research",
        "badge": "1.basicdeepagents.ipynb",
        "icon": "🚀",
        "description": "Demonstrates autonomous planning, web search via Tavily, and multi-step reasoning.",
        "prompt": "What is a Deep Agent, and how does its planning capability and subagent architecture differ from standard LangChain ReAct agents?",
        "recommended_tools": ["web_search"],
        "recommended_backend": "FilesystemBackend (Local Disk / Workspace)",
    },
    {
        "id": "nb2_tools",
        "title": "Notebook 2: Custom @tool Execution",
        "badge": "2.mybasictool.ipynb",
        "icon": "🔢",
        "description": "Tests custom tool calling with add_numbers, multiply_numbers, and mathematical evaluation.",
        "prompt": "Use the add_numbers tool to calculate 25 + 17, then multiply that result by 3 using multiply_numbers.",
        "recommended_tools": ["add_numbers", "multiply_numbers"],
        "recommended_backend": "StateBackend (Ephemeral State)",
    },
    {
        "id": "nb3_fs",
        "title": "Notebook 3A: FilesystemBackend File Operations",
        "badge": "3.backends.ipynb",
        "icon": "📁",
        "description": "Creates or updates /deepagentsdemo/notes/todo.txt on the local workspace disk.",
        "prompt": "Create a file at /deepagentsdemo/notes/todo.txt with exactly this content:\n1. Record video\n2. Edit video\n3. Upload video\n4. Review analytics\nThen verify by reading it back.",
        "recommended_tools": ["write_file", "read_file"],
        "recommended_backend": "FilesystemBackend (Local Disk / Workspace)",
    },
    {
        "id": "nb3_store",
        "title": "Notebook 3B: StoreBackend Cross-Thread Persistence",
        "badge": "3.backends.ipynb",
        "icon": "💾",
        "description": "Tests cross-thread storage using LangGraph InMemoryStore across isolated sessions.",
        "prompt": "Create a file at /notes/cross_thread_demo.txt with content 'DeepAgent StoreBackend persists state across multiple threads!'. Then confirm it was stored.",
        "recommended_tools": ["write_file"],
        "recommended_backend": "StoreBackend (LangGraph InMemoryStore / Cross-Thread)",
    },
    {
        "id": "nb4_context",
        "title": "Notebook 4A: Context Engineering & AGENTS.md Memory",
        "badge": "4.contextengineering.ipynb",
        "icon": "🧠",
        "description": "Leverages persistent memory from projects/AGENTS.md to reason about workspace architecture.",
        "prompt": "Based on our project memory in AGENTS.md and loaded skills, explain the Deep Agents core architecture, the role of MemoryMiddleware, and the workspace conventions.",
        "recommended_tools": ["read_file"],
        "recommended_backend": "FilesystemBackend (Local Disk / Workspace)",
    },
    {
        "id": "nb4_subagents",
        "title": "Notebook 4B: Subagent Swarm Delegation",
        "badge": "4-subagents.ipynb",
        "icon": "🤖",
        "description": "Delegates distinct tasks to specialized subagents (researcher, math, python, langgraph) via the task tool.",
        "prompt": "I need two tasks completed:\n1. Delegate to the math_specialist to calculate the square root of 65536 plus 45.\n2. Delegate to the research_specialist to summarize the primary capabilities of Deep Agents.\nSynthesize their results cleanly.",
        "recommended_tools": ["task", "add_numbers", "web_search"],
        "recommended_backend": "FilesystemBackend (Local Disk / Workspace)",
    },
]
