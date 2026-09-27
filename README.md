# ⚡ DeepAgent Intelligence Studio

An advanced, conversational AI chatbot and multi-agent development studio built on top of **Deep Agents**, **LangGraph**, and **Streamlit**.

This application implements and unifies all concepts, features, tools, and backends explained across the notebooks in `deepagentsdemo/`:
- **`1.basicdeepagents.ipynb`**: Autonomous planning, multi-step task decomposition, and live web research using **Tavily**.
- **`2.mybasictool.ipynb`**: Custom `@tool` functions (`add_numbers`, `multiply_numbers`, `evaluate_expression`) and dynamic tool registration.
- **`3.backends.ipynb`**: Pluggable storage and execution backends:
  - `FilesystemBackend`: Modifies local workspace disk files in `virtual_mode`.
  - `StoreBackend`: Cross-thread persistent file sharing backed by LangGraph `InMemoryStore`.
  - `StateBackend`: Ephemeral in-memory execution state.
- **`4.contextengineering.ipynb` & `4-subagents.ipynb`**:
  - Context engineering with persistent project memory via `MemoryMiddleware` and [AGENTS.md](file:///Users/amareshpandey/Projects/Amaresh-AI/DeepAgent/deepagentsdemo/projects/AGENTS.md).
  - Domain skills catalog injection (`python`, `langgraph`, `aws`, `technical-writing`).
  - Subagent swarm delegation (`task` tool) with specialized subagents (`research_specialist`, `math_specialist`, `python_specialist`, `langgraph_specialist`).

---

## 🚀 Quick Start

### 1. Environment & Dependencies

Install dependencies using `uv`:

```bash
uv sync
```

Make sure your `.env` contains your preferred LLM provider keys:
- `OPENAI_API_KEY`
- `GROQ_API_KEY` (Supports ultra-fast inference with `openai/gpt-oss-120b`)
- `TAVILY_API_KEY` (For live web search)
- `GOOGLE_API_KEY` (For Gemini models)

### 2. Launching the Streamlit App

Run the Streamlit app locally:

```bash
./.venv/bin/streamlit run app.py
```

The app will start at `http://localhost:8501`.

---

## 🌟 Application Features & Tabs

### 1. 💬 Agent Chat (Conversational Interface)
- Multi-turn conversation with memory using LangGraph `MemorySaver` checkpointer and unique session/thread IDs.
- Real-time step-by-step reasoning & tool execution streaming (shows `model` thinking -> `tools` calls with args -> tool execution outputs -> subagent delegations -> final response).
- Quick starter prompt chips for instant experimentation.
- Session switcher: create new chats, switch between previous session threads, clear current chat, and export chat logs.

### 2. 🧪 Notebook Lab & Interactive Demos
- One-click execution of the core experiments from all 4 notebooks:
  - **Notebook 1**: Basic Deep Agent with Tavily Web Search
  - **Notebook 2**: Custom `@tool` math executions
  - **Notebook 3A**: FilesystemBackend file creation on disk (`/deepagentsdemo/notes/todo.txt`)
  - **Notebook 3B**: StoreBackend cross-thread persistence verification (Thread 1 write -> Thread 2 read back verbatim)
  - **Notebook 4A**: Context Engineering with `AGENTS.md` memory injection
  - **Notebook 4B**: Subagent Swarm Delegation
- Dedicated interactive widget to test cross-thread `StoreBackend` persistence!

### 3. 🧠 Context & Memory Hub (`AGENTS.md`)
- Ingests `deepagentsdemo/projects/AGENTS.md` into `<agent_memory>` tags in the system prompt.
- Live in-app editor to inspect or modify `AGENTS.md`.
- Memory Update Protocol reference guide.

### 4. 📚 Domain Skills Catalog
- Interactive browser for domain skills in `deepagentsdemo/skills/`:
  - 🐍 `skills/python`: Modern Python 3.11-3.13, typing, async, Pydantic, testing
  - 🕸️ `skills/langgraph`: StateGraph, cyclic flows, multi-agent supervisors, checkpointers
  - ☁️ `skills/aws`: Boto3, Lambda, DynamoDB, Bedrock, IAM, CDK
  - 📝 `skills/technical-writing`: Diátaxis framework, ADRs, documentation standards
- Tabbed viewer for `SKILL.md`, `instructions.md`, and `examples.md`.

### 5. 📁 Files & Notes Explorer (Live Workspace)
- Live file manager for `deepagentsdemo/notes/` and workspace files.
- Inspect note files created by the Deep Agent (like `notes/todo.txt`).
- Create, edit, and view notes in real-time.

### 6. ⚙️ Architecture & Inspector
- Complete architectural diagram of DeepAgent (middleware stack, pluggable backends, LangGraph StateGraph).
- Active tools inspector.
- Configured subagent swarm status.

---

## 📂 Project Structure

```
DeepAgent/
├── app.py                      # Main Streamlit Application
├── deepagent_core/             # Core Backend Modules
│   ├── __init__.py
│   ├── agent_factory.py        # DeepAgent builder (models, backends, memory, skills, tools, subagents)
│   ├── tools_catalog.py        # Tavily search, math tools, filesystem tools, dynamic tool generator
│   ├── skills_manager.py       # Catalog scanner, parser, viewer for deepagentsdemo/skills
│   ├── memory_manager.py       # AGENTS.md loader, editor, and memory context inspector
│   ├── backends_manager.py     # Backend state management (Filesystem, StoreBackend, StateBackend)
│   └── demos.py                # Ready-to-run demo scenarios from Notebooks 1, 2, 3, 4
├── assets/
│   └── custom.css              # Custom styling, dark mode, glassmorphism, responsive pills
├── deepagentsdemo/             # Notebooks, skills, and project notes
│   ├── 1.basicdeepagents.ipynb
│   ├── 2.mybasictool.ipynb
│   ├── 3.backends.ipynb
│   ├── 4.contextengineering.ipynb
│   ├── notes/                  # Agent workspace notes (todo.txt)
│   ├── projects/               # AGENTS.md persistent memory
│   └── skills/                 # Domain skills (python, langgraph, aws, technical-writing)
├── pyproject.toml
└── requirements.txt
```
