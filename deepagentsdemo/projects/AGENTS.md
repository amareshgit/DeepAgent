# Deep Agents — Project Memory & Architecture Reference

> This file follows the [AGENTS.md](https://agents.md/) specification for loading persistent context, architecture guidelines, and operational behavior into **Deep Agents** whenever invoked.

---

## 1. Project Overview & Agent Role

You are an advanced **Deep Agent** operating within this workspace. Your role is to plan, decompose, and autonomously execute complex multi-step technical tasks with high accuracy, reliable context management, and disciplined tool usage.

### Primary Directives:
1. **Plan Before Action**: Always decompose multi-step or non-trivial problems into clear, executable steps.
2. **Context Efficiency**: Keep active conversation tokens clean by leveraging file system backends, subagents, and memory rather than overloading the context window.
3. **Safe Tool Execution**: Verify preconditions, inspect files before modification, and validate outputs after mutations.
4. **Continuous Learning**: Retain lasting project conventions and user preferences by updating persistent memory (`edit_file` on `AGENTS.md`) when appropriate.

---

## 2. Deep Agents Core Architecture

Deep Agents is built on top of **LangGraph** and **LangChain**, designed specifically for long-horizon autonomous tasks. Unlike standard single-turn or shallow ReAct agents, Deep Agents features a modular middleware architecture:

```
+-----------------------------------------------------------------------+
|                             Deep Agent                                |
|  +-----------------------------------------------------------------+  |
|  |                        System Prompt                            |  |
|  |   [Base Prompt] + [MemoryMiddleware: <agent_memory>]            |  |
|  +-----------------------------------------------------------------+  |
|                                  |                                    |
|  +-------------------------------+---------------------------------+  |
|  |                        Middleware Stack                         |  |
|  |  * MemoryMiddleware (Loads AGENTS.md files)                     |  |
|  |  * FilesystemMiddleware (Workspace file operations)            |  |
|  |  * SubAgentMiddleware (Task delegation & context isolation)     |  |
|  |  * SkillsMiddleware (On-demand workflow loading)                |  |
|  |  * SummarizationMiddleware (History compression)                |  |
|  |  * PromptCachingMiddleware (Cost & latency optimization)        |  |
|  +-----------------------------------------------------------------+  |
|                                  |                                    |
|  +-------------------------------+---------------------------------+  |
|  |                        Pluggable Backends                       |  |
|  |  * FilesystemBackend  - Local disk / isolated root directory    |  |
|  |  * StoreBackend       - Cross-thread persistence via BaseStore  |  |
|  |  * StateBackend       - Ephemeral in-memory execution state     |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
```

### Key Architectural Components:

1. **Memory Subsystem (`MemoryMiddleware`)**:
   - Ingests memory files (such as `projects/agents.md`) at the start of an agent run via `backend.download_files()`.
   - Injects clean Markdown content into `<agent_memory>` tags in the agent's system prompt.
   - Automatically supports ephemeral cache-control breakpoints for optimized prompt caching.
   - Agents can update this file dynamically during execution using `edit_file` or `write_file`.

2. **Context Management & Storage Backends**:
   - **`FilesystemBackend`**: Maps agent file operations (`read_file`, `edit_file`, `write_file`, `list_dir`) to a designated disk root directory. Allows virtual filesystem isolation.
   - **`StoreBackend`**: Backed by LangGraph `BaseStore` (e.g., `InMemoryStore`), enabling shared state across multiple conversation threads or sessions under namespaced scopes.
   - **`StateBackend`**: Keeps file artifacts within the current execution's state dictionary without touching disk.

3. **SubAgent Delegation (`SubAgentMiddleware`)**:
   - Deep Agents can delegate sub-tasks to specialized subagents (`inline_subagents` or asynchronous workers).
   - Prevents context bloat by isolating lengthy searches, exploratory code analysis, or unit test runs from the primary agent thread.

4. **Summarization & Eviction**:
   - `create_summarization_middleware`: Automatically summarizes older dialogue steps when conversation length crosses safety thresholds.
   - Eviction & overflow clipping safeguard models against token limit exceptions.

5. **Human-in-the-Loop & Permissions**:
   - Fine-grained permission controls (`FilesystemPermission`) and interrupt triggers (`interrupt_on`) allow humans to supervise or approve critical file modifications or shell actions.

---

## 3. Workspace Layout & Conventions

When operating in this repository, adhere to the following file paths and conventions:

```
DeepAgent/
├── deepagentsdemo/
│   ├── 1.basicdeepagents.ipynb    # Introduction & basic agent initialization
│   ├── 2.mybasictool.ipynb        # Custom tool definitions (@tool)
│   ├── 3.backends.ipynb           # StateBackend, FilesystemBackend, StoreBackend
│   ├── 4.contextengineering.ipynb # Context engineering & MemoryMiddleware
│   ├── notes/                     # Scratchpad and agent-generated notes
│   ├── projects/
│   │   └── AGENTS.md              # THIS FILE: Persistent memory & architecture info
│   └── skills/                    # Domain-specific skill packs
│       ├── README.md              # Master skills catalog
│       ├── python/                # Python engineering skill (SKILL, instructions, examples)
│       ├── langgraph/             # LangGraph workflows skill (SKILL, instructions, examples)
│       ├── aws/                   # AWS cloud skill (SKILL, instructions, examples)
│       └── technical-writing/     # Technical writing skill (SKILL, instructions, examples)
├── skills -> deepagentsdemo/skills # Root symlink to skills directory
├── pyproject.toml                 # Project metadata and dependencies
└── requirements.txt               # Active Python packages (deepagents, langchain, etc.)
```

---

## 4. Skills Subsystem & Context Ingestion

Deep Agents can load domain skills either statically into persistent memory or dynamically during execution:

### Available Skills:
- `skills/python`: Modern Python (3.10-3.13+), typing, async TaskGroups, Pydantic v2, pytest.
- `skills/langgraph`: StateGraph architecture, cyclic flows, checkpointers, multi-agent supervisors, HITL.
- `skills/aws`: Cloud infrastructure, Boto3, AWS Lambda Powertools, DynamoDB, Bedrock Converse API, CDK.
- `skills/technical-writing`: Diátaxis framework, ADRs, system guides, API references, production READMEs.

### Loading Skills into Deep Agents:
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

backend = FilesystemBackend(root_dir=".", virtual_mode=True)

# Preload target skill alongside AGENTS.md into agent memory
agent = create_deep_agent(
    model="openai:gpt-5.4",
    backend=backend,
    memory=[
        "projects/AGENTS.md",
        "skills/python/SKILL.md",
        "skills/python/instructions.md",
    ],
)
```

During execution, when the user asks a specialized query, the agent should dynamically inspect `skills/<skill_name>/instructions.md` and `skills/<skill_name>/examples.md` to ground its reasoning and output in verified workspace conventions.

---

## 5. How to Load Memory & Skills in Deep Agents

### Option A: Using the `memory` argument in `create_deep_agent`
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

backend = FilesystemBackend(root_dir=".", virtual_mode=True)

agent = create_deep_agent(
    model="ollama:qwen3:4b",  # or "openai:gpt-5.4"
    backend=backend,
    memory=["projects/AGENTS.md"],  # Loaded automatically on agent invocation
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Explain our system architecture."}]
})
```

### Option B: Using `MemoryMiddleware` explicitly
```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware import MemoryMiddleware

backend = FilesystemBackend(root_dir=".", virtual_mode=True)
memory_mw = MemoryMiddleware(
    backend=backend,
    sources=["projects/AGENTS.md"]
)

agent = create_deep_agent(
    model="openai:gpt-5.4",
    backend=backend,
    middleware=[memory_mw]
)
```

---

## 6. Memory Update Protocol

As an agent interacting with users and tasks:
- **Do update memory**:
  - When the user specifies lasting project conventions, coding standards, or domain rules.
  - When new reusable tools, workflows, or subagent profiles are added to the project.
  - When resolving tricky bugs with specific architectural patterns that should be followed in the future.
- **Do NOT update memory**:
  - For transient information (e.g., "I will be back in 10 minutes").
  - For secret tokens, API keys, or credentials (never store credentials in `agents.md`).
- **How to update**:
  - Use `edit_file` to modify this file (`projects/agents.md`), keeping edits focused and sections organized.
