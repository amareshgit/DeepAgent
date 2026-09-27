"""DeepAgent Intelligence Studio - Comprehensive Streamlit Conversational AI App

Integrates all capabilities and notebooks from DeepAgent:
- Notebook 1: Basic Deep Agent & Tavily Web Search
- Notebook 2: Custom @tool Math & Dynamic Tools
- Notebook 3: FilesystemBackend, StoreBackend (cross-thread persistence), StateBackend
- Notebook 4: Context Engineering, AGENTS.md Memory, and Subagent Swarm Delegation
- Skills System: Python, LangGraph, AWS, Technical Writing
- Live Workspace Notes & Files Explorer
"""
import os
import json
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

import streamlit as st
from dotenv import load_dotenv

# Load workspace .env
load_dotenv()

from deepagent_core.agent_factory import (
    create_configured_agent,
    get_available_models,
    DEFAULT_SYSTEM_PROMPTS,
)
from deepagent_core.backends_manager import BackendManager, BackendType
from deepagent_core.skills_manager import SkillsCatalog
from deepagent_core.memory_manager import MemoryManager, DEFAULT_MEMORY_FILE
from deepagent_core.demos import NOTEBOOK_DEMOS
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

# Set Page Config
st.set_page_config(
    page_title="DeepAgent Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load Custom CSS
css_file = os.path.join(os.path.dirname(__file__), "assets", "custom.css")
if os.path.exists(css_file):
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Text & Stream Helpers
# -----------------------------------------------------------------------------
def extract_text(content: Any) -> str:
    """Robust extractor for message content across various LangChain formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text" and "text" in item:
                    texts.append(str(item["text"]))
                elif "content" in item:
                    texts.append(str(item["content"]))
                elif "text" in item:
                    texts.append(str(item["text"]))
            else:
                texts.append(str(item))
        return "\n".join(texts)
    elif content is None:
        return ""
    return str(content)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "backend_manager" not in st.session_state:
    st.session_state.backend_manager = BackendManager()

if "memory_manager" not in st.session_state:
    st.session_state.memory_manager = MemoryManager()

if "skills_catalog" not in st.session_state:
    st.session_state.skills_catalog = SkillsCatalog()

if "checkpointer" not in st.session_state:
    st.session_state.checkpointer = MemorySaver()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "threads" not in st.session_state:
    # Maps thread_id -> list of message dicts
    st.session_state.threads = {st.session_state.thread_id: []}

if "custom_tools" not in st.session_state:
    st.session_state.custom_tools = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# -----------------------------------------------------------------------------
# Sidebar: Engine, Backends, Capabilities, Memory & Skills
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
            <span style="font-size: 1.8rem;">⚡</span>
            <div>
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #f8fafc;">DeepAgent Control</h3>
                <span style="font-size: 0.75rem; color: #94a3b8;">Autonomous Reasoning Stack</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # 1. Model & Engine Configuration
    st.markdown("<div class='sidebar-section-title'>🤖 1. LLM Model & Provider</div>", unsafe_allow_html=True)
    all_models = get_available_models()
    provider_options = list(all_models.keys())

    # Default to Groq if key exists, else OpenAI
    default_provider_idx = 0
    if os.getenv("GROQ_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        default_provider_idx = 1

    selected_provider = st.selectbox(
        "Provider",
        options=provider_options,
        index=default_provider_idx,
        help="Select model provider (Groq for ultra-fast, OpenAI for reasoning, Ollama for local)",
    )

    models_for_provider = all_models[selected_provider]
    selected_model = st.selectbox(
        "Model Name",
        options=models_for_provider,
        index=0,
        help="Choose specific LLM model identifier",
    )

    # API Key check & override
    env_key_name = {
        "OpenAI": "OPENAI_API_KEY",
        "Groq": "GROQ_API_KEY",
        "Google GenAI": "GOOGLE_API_KEY",
    }.get(selected_provider)

    has_env_key = bool(env_key_name and os.getenv(env_key_name))
    key_placeholder = f"Detected in .env ({env_key_name})" if has_env_key else f"Enter {selected_provider} API Key"

    custom_api_key = st.text_input(
        f"{selected_provider} Key (Optional override)",
        value="",
        placeholder=key_placeholder,
        type="password",
    )
    effective_api_key = custom_api_key if custom_api_key.strip() else (os.getenv(env_key_name) if env_key_name else None)

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)

    st.markdown("---")

    # 2. Pluggable Storage Backend (Notebook 3)
    st.markdown("<div class='sidebar-section-title'>💾 2. Pluggable Backend (Notebook 3)</div>", unsafe_allow_html=True)
    backend_choices = [
        BackendType.FILESYSTEM,
        BackendType.STORE,
        BackendType.STATE,
    ]
    selected_backend = st.selectbox(
        "Active Storage Backend",
        options=backend_choices,
        index=0,
        format_func=lambda x: x.value,
        help=(
            "FilesystemBackend: Edits local disk files in workspace\n"
            "StoreBackend: LangGraph InMemoryStore across threads\n"
            "StateBackend: Ephemeral execution memory"
        ),
    )

    st.markdown("---")

    # 3. Tools & Capabilities (Notebook 1 & 2)
    st.markdown("<div class='sidebar-section-title'>🛠️ 3. Tools & Capabilities (NB 1 & 2)</div>", unsafe_allow_html=True)
    tavily_detected = bool(os.getenv("TAVILY_API_KEY"))
    enable_web_search = st.checkbox(
        "🔍 Tavily Web Search (NB 1)",
        value=tavily_detected,
        help="Live web research & source citation",
    )
    if enable_web_search and not tavily_detected:
        tavily_key_input = st.text_input("Tavily API Key", type="password")
    else:
        tavily_key_input = os.getenv("TAVILY_API_KEY")

    enable_math_tools = st.checkbox(
        "🔢 Math Tools (add_numbers, multiply) (NB 2)",
        value=True,
        help="add_numbers, multiply_numbers, evaluate_expression",
    )

    with st.expander("➕ Add Custom @tool Function (NB 2)"):
        custom_tool_name = st.text_input("Tool Name", value="reverse_string")
        custom_tool_desc = st.text_input("Description", value="Reverses an input string")
        custom_tool_code = st.text_area(
            "Python Code",
            value="def reverse_string(text: str) -> str:\n    '''Reverses the given text string.'''\n    return text[::-1]",
            height=100,
        )
        if st.button("Register Custom Tool"):
            try:
                local_scope = {}
                exec(custom_tool_code, globals(), local_scope)
                func = local_scope.get(custom_tool_name)
                if func and callable(func):
                    decorated_tool = tool(func)
                    st.session_state.custom_tools.append(decorated_tool)
                    st.success(f"Registered tool: {custom_tool_name}")
                else:
                    st.error(f"Function {custom_tool_name} not found in provided code.")
            except Exception as e:
                st.error(f"Error registering tool: {e}")

    st.markdown("---")

    # 4. Context Engineering & Memory (Notebook 4 & AGENTS.md)
    st.markdown("<div class='sidebar-section-title'>🧠 4. Context & Memory (NB 4)</div>", unsafe_allow_html=True)
    system_prompt_type = st.selectbox(
        "Persona / System Prompt",
        options=list(DEFAULT_SYSTEM_PROMPTS.keys()),
        index=0,
    )
    if system_prompt_type == "Custom":
        active_system_prompt = st.text_area("Custom System Prompt", value="Act as a helpful Deep Agent.", height=80)
    else:
        active_system_prompt = DEFAULT_SYSTEM_PROMPTS[system_prompt_type]

    load_memory_toggle = st.checkbox(
        "Load AGENTS.md Memory",
        value=True,
        help="Loads deepagentsdemo/projects/AGENTS.md into <agent_memory> tags",
    )

    # 5. Skills Subsystem (deepagentsdemo/skills)
    st.markdown("<div class='sidebar-section-title'>📚 5. Domain Skills Catalog</div>", unsafe_allow_html=True)
    all_skill_names = st.session_state.skills_catalog.get_skill_names()
    selected_skills = st.multiselect(
        "Active Skills",
        options=all_skill_names,
        default=all_skill_names,
        help="Select which skills from deepagentsdemo/skills to inject",
    )

    st.markdown("---")

    # 6. Subagent Swarm Delegation (Notebook 4 & SubAgentMiddleware)
    st.markdown("<div class='sidebar-section-title'>🤖 6. Subagents Swarm (NB 4)</div>", unsafe_allow_html=True)
    enable_subagents = st.checkbox("Enable Subagent Delegation", value=True)
    sub_researcher = st.checkbox("🔬 research_specialist", value=True, disabled=not enable_subagents)
    sub_math = st.checkbox("📐 math_specialist", value=True, disabled=not enable_subagents)
    sub_python = st.checkbox("🐍 python_specialist", value=True, disabled=not enable_subagents)
    sub_langgraph = st.checkbox("🕸️ langgraph_specialist", value=True, disabled=not enable_subagents)

    subagents_config = {
        "researcher": sub_researcher,
        "math": sub_math,
        "python": sub_python,
        "langgraph": sub_langgraph,
    }

    st.markdown("---")

    # 7. Session & Thread Management
    st.markdown("<div class='sidebar-section-title'>🧵 7. Session & Threads</div>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.caption(f"Current Thread: `{st.session_state.thread_id[:8]}...`")
    with col_t2:
        if st.button("➕ New", help="Start a new conversation thread"):
            new_id = str(uuid.uuid4())
            st.session_state.thread_id = new_id
            st.session_state.threads[new_id] = []
            st.rerun()

    existing_threads = list(st.session_state.threads.keys())
    if len(existing_threads) > 1:
        selected_thread = st.selectbox(
            "Switch Thread",
            options=existing_threads,
            index=existing_threads.index(st.session_state.thread_id),
            format_func=lambda x: f"Thread {x[:8]} ({len(st.session_state.threads[x])} msgs)",
        )
        if selected_thread != st.session_state.thread_id:
            st.session_state.thread_id = selected_thread
            st.rerun()

    if st.button("🗑️ Clear Current Thread", use_container_width=True):
        st.session_state.threads[st.session_state.thread_id] = []
        st.rerun()


# -----------------------------------------------------------------------------
# Agent Compilation / Instantiation
# -----------------------------------------------------------------------------
current_messages = st.session_state.threads[st.session_state.thread_id]

try:
    agent, store = create_configured_agent(
        provider=selected_provider,
        model_name=selected_model,
        temperature=temperature,
        api_key=effective_api_key,
        system_prompt=active_system_prompt,
        backend_type=selected_backend,
        backend_manager=st.session_state.backend_manager,
        enable_web_search=enable_web_search,
        enable_math_tools=enable_math_tools,
        tavily_api_key=tavily_key_input,
        load_memory=load_memory_toggle,
        memory_path=DEFAULT_MEMORY_FILE,
        selected_skills=selected_skills,
        enable_subagents=enable_subagents,
        subagents_config=subagents_config,
        checkpointer=st.session_state.checkpointer,
    )
except Exception as exc:
    st.error(f"Agent Initialization Error: {exc}")
    agent = None


# -----------------------------------------------------------------------------
# Header Display & Dynamic Stat Pills
# -----------------------------------------------------------------------------
backend_short_name = {
    BackendType.FILESYSTEM: "FilesystemBackend (Disk)",
    BackendType.STORE: "StoreBackend (Shared Store)",
    BackendType.STATE: "StateBackend (Ephemeral)",
}.get(selected_backend, "Backend")

st.markdown(
    f"""
    <div class="deepagent-header">
        <div class="header-title-container">
            <div class="header-brand">
                <span class="header-icon">⚡</span>
                <div>
                    <h1 class="header-title">DeepAgent Intelligence Studio</h1>
                    <div class="header-subtitle">Autonomous Multi-Step Reasoning, Pluggable Backends & Subagent Swarms</div>
                </div>
            </div>
        </div>
        <div class="status-pill-container">
            <span class="stat-pill pill-cyan">🤖 Model: <strong>{selected_provider} ({selected_model})</strong></span>
            <span class="stat-pill pill-purple">💾 Storage: <strong>{backend_short_name}</strong></span>
            <span class="stat-pill pill-emerald">🧠 Memory: <strong>{'AGENTS.md Active' if load_memory_toggle else 'Off'}</strong></span>
            <span class="stat-pill pill-amber">📚 Skills: <strong>{len(selected_skills)} Active</strong></span>
            <span class="stat-pill pill-cyan">🤖 Subagents: <strong>{'Enabled' if enable_subagents else 'Disabled'}</strong></span>
            <span class="stat-pill pill-purple">🧵 Thread: <code>{st.session_state.thread_id[:8]}...</code></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Tabs Layout
# -----------------------------------------------------------------------------
tab_chat, tab_demos, tab_memory, tab_skills, tab_files, tab_arch = st.tabs([
    "💬 Agent Chat",
    "🧪 Notebook Lab & Demos",
    "🧠 Context & Memory Hub",
    "📚 Domain Skills Catalog",
    "📁 Files & Notes Explorer",
    "⚙️ Architecture & Inspector",
])


# =============================================================================
# TAB 1: Conversational Chatbot
# =============================================================================
with tab_chat:
    # Quick starter chips if conversation is empty
    if len(current_messages) == 0:
        st.markdown("##### 🚀 Quick Starters (From Notebooks 1-4):")
        cols = st.columns(3)
        starters = [
            ("🔍 Web Research (NB 1)", "What is a Deep Agent and what makes it distinct from standard ReAct agents? Search the web."),
            ("🔢 Math Tool Test (NB 2)", "Use add_numbers to calculate 25 + 17, then multiply the result by 4."),
            ("📁 Create Note (NB 3)", "Create a file at /deepagentsdemo/notes/todo.txt with tasks for building a deep agent app."),
            ("💾 StoreBackend Test (NB 3)", "Create a file at /notes/experiment.txt with content 'Testing cross-thread memory.'"),
            ("🧠 Ingest AGENTS.md (NB 4)", "Explain our project architecture and MemoryMiddleware based on our loaded AGENTS.md memory."),
            ("🤖 Subagent Delegation (NB 4)", "Delegate math calculation of (450 * 12) + 85 to math_specialist and ask research_specialist about LangGraph."),
        ]
        for idx, (label, prompt_text) in enumerate(starters):
            with cols[idx % 3]:
                if st.button(label, key=f"starter_{idx}", use_container_width=True):
                    st.session_state.pending_prompt = prompt_text
                    st.rerun()

    # Display Chat History
    for msg in current_messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        steps = msg.get("steps", [])

        with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "⚡"):
            if role == "assistant" and steps:
                with st.expander(f"🔍 Reasoning & Tool Invocations ({len(steps)} steps)", expanded=False):
                    for step in steps:
                        st_type = step.get("type")
                        if st_type == "tool_call":
                            is_sub = step.get("name") == "task"
                            if is_sub:
                                s_type = step.get("args", {}).get("subagent_type", "subagent")
                                s_desc = step.get("args", {}).get("description", "")
                                st.markdown(
                                    f"<div class='subagent-call-box'>🤖 <strong>Delegated to Subagent:</strong> <code>{s_type}</code><br/>"
                                    f"<em>Task:</em> {s_desc}</div>",
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.markdown(
                                    f"<div class='tool-call-box'>🛠️ <strong>Tool Call:</strong> <code>{step.get('name')}</code><br/>"
                                    f"<strong>Args:</strong> <code>{json.dumps(step.get('args', {}))}</code></div>",
                                    unsafe_allow_html=True,
                                )
                        elif st_type == "tool_result":
                            res_text = str(step.get("content", ""))
                            if len(res_text) > 400:
                                res_text = res_text[:400] + "... (truncated)"
                            st.caption(f"📄 Result from `{step.get('name', 'tool')}`:")
                            st.code(res_text, language="text")

            st.markdown(content)

    # Chat Input Box
    user_input = st.chat_input("Ask DeepAgent anything, run tools, or delegate tasks...")

    # Determine prompt to run
    prompt_to_run = None
    if st.session_state.pending_prompt:
        prompt_to_run = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
    elif user_input:
        prompt_to_run = user_input

    if prompt_to_run:
        # Append User Message
        current_messages.append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt_to_run)

        # Assistant Execution with streaming & step tracking
        with st.chat_message("assistant", avatar="⚡"):
            status_container = st.status("🧠 DeepAgent thinking & decomposing task...", expanded=True)
            intermediate_steps: List[Dict[str, Any]] = []
            final_text_chunks: List[str] = []
            response_placeholder = st.empty()

            config = {"configurable": {"thread_id": st.session_state.thread_id}}

            try:
                if agent is None:
                    raise RuntimeError("Agent is not compiled. Please verify API keys and settings in sidebar.")

                stream_iter = agent.stream(
                    {"messages": [{"role": "user", "content": prompt_to_run}]},
                    config=config,
                    stream_mode="updates",
                )

                for chunk in stream_iter:
                    for node_name, node_val in chunk.items():
                        if isinstance(node_val, dict) and "messages" in node_val:
                            for m in node_val["messages"]:
                                # 1. Check for tool calls
                                if hasattr(m, "tool_calls") and m.tool_calls:
                                    for tc in m.tool_calls:
                                        tc_name = tc.get("name", "tool")
                                        tc_args = tc.get("args", {})
                                        intermediate_steps.append({
                                            "type": "tool_call",
                                            "name": tc_name,
                                            "args": tc_args,
                                        })
                                        if tc_name == "task":
                                            sub_type = tc_args.get("subagent_type", "subagent")
                                            sub_desc = tc_args.get("description", "")
                                            status_container.markdown(
                                                f"🤖 **Delegating to Subagent:** `{sub_type}` — *{sub_desc}*"
                                            )
                                        else:
                                            status_container.markdown(
                                                f"🛠️ **Executing Tool:** `{tc_name}` with args: `{json.dumps(tc_args)}`"
                                            )

                                # 2. Check for tool outputs
                                elif m.__class__.__name__ == "ToolMessage" or getattr(m, "type", "") == "tool":
                                    t_name = getattr(m, "name", "tool")
                                    t_content = extract_text(getattr(m, "content", ""))
                                    intermediate_steps.append({
                                        "type": "tool_result",
                                        "name": t_name,
                                        "content": t_content,
                                    })
                                    status_container.markdown(
                                        f"📄 **Tool Result received from** `{t_name}` ({len(t_content)} chars)"
                                    )

                                # 3. Assistant final text
                                elif hasattr(m, "content") and m.content:
                                    extracted = extract_text(m.content)
                                    if extracted.strip():
                                        final_text_chunks.append(extracted)
                                        response_placeholder.markdown(extracted)

                status_container.update(
                    label=f"✅ DeepAgent finished execution ({len(intermediate_steps)} tool steps)",
                    state="complete",
                    expanded=False,
                )

                final_answer = final_text_chunks[-1] if final_text_chunks else "Completed task."
                current_messages.append({
                    "role": "assistant",
                    "content": final_answer,
                    "steps": intermediate_steps,
                    "timestamp": datetime.now().isoformat(),
                })

            except Exception as exc:
                status_container.update(label="❌ Execution Error", state="error", expanded=True)
                st.error(f"Error during agent execution: {exc}")
                current_messages.append({
                    "role": "assistant",
                    "content": f"**Execution Error**: {exc}",
                    "steps": intermediate_steps,
                    "timestamp": datetime.now().isoformat(),
                })


# =============================================================================
# TAB 2: Notebook Lab & Ready-to-Run Demos
# =============================================================================
with tab_demos:
    st.markdown("### 🧪 DeepAgent Notebook Scenarios & Interactive Labs")
    st.caption("One-click execution of the core experiments and capabilities demonstrated across all 4 notebooks.")

    demo_cols = st.columns(2)
    for idx, demo in enumerate(NOTEBOOK_DEMOS):
        with demo_cols[idx % 2]:
            st.markdown(
                f"""
                <div class="demo-card">
                    <span class="demo-card-badge">{demo['badge']}</span>
                    <div class="demo-card-title">{demo['icon']} {demo['title']}</div>
                    <div class="demo-card-desc">{demo['description']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                if st.button(f"▶️ Run in Chat", key=f"run_demo_{demo['id']}", use_container_width=True):
                    st.session_state.pending_prompt = demo["prompt"]
                    st.rerun()
            with col_b2:
                with st.popover("Inspect Prompt"):
                    st.markdown(f"**Prompt:**\n\n```\n{demo['prompt']}\n```")
                    st.markdown(f"**Recommended Backend:** `{demo['recommended_backend']}`")
                    st.markdown(f"**Tools:** `{', '.join(demo['recommended_tools'])}`")

    st.markdown("---")
    st.markdown("### 🌐 Live StoreBackend Cross-Thread Verification (Notebook 3 Cell 6-8)")
    st.info(
        "In Notebook 3, `StoreBackend` backed by `InMemoryStore` is proven by writing a file on **Thread 1**, "
        "and reading that exact file back on **Thread 2**—something `StateBackend` cannot do!"
    )

    col_st1, col_st2 = st.columns(2)
    with col_st1:
        st.markdown("#### 1. Write on Thread 1")
        test_file_path = st.text_input("Store File Path", value="/notes/todo.txt")
        test_file_content = st.text_area(
            "File Content to Write",
            value="1. Record video\n2. Edit video\n3. Upload video\n4. Review DeepAgent analytics",
            height=100,
        )
        if st.button("🚀 Write to StoreBackend (Thread 1)", key="btn_store_write"):
            with st.spinner("Writing file to StoreBackend on Thread 1..."):
                try:
                    # Create dedicated StoreBackend agent
                    store_agent, _ = create_configured_agent(
                        provider=selected_provider,
                        model_name=selected_model,
                        backend_type=BackendType.STORE,
                        backend_manager=st.session_state.backend_manager,
                        checkpointer=st.session_state.checkpointer,
                        api_key=effective_api_key,
                    )
                    t1_id = f"thread-demo-1-{uuid.uuid4().hex[:6]}"
                    cfg1 = {"configurable": {"thread_id": t1_id}}
                    p1 = f"Create a file at {test_file_path} with exactly this content:\n{test_file_content}\nThen tell me you have done it."
                    r1 = store_agent.invoke({"messages": [{"role": "user", "content": p1}]}, config=cfg1)
                    st.success("✅ File successfully written to StoreBackend on Thread 1!")
                    st.markdown(f"**Thread 1 Reply:**\n{extract_text(r1['messages'][-1].content)}")
                except Exception as e:
                    st.error(f"Store write error: {e}")

    with col_st2:
        st.markdown("#### 2. Read Back on Thread 2 (Different Session)")
        read_path_input = st.text_input("Read Back Path", value="/notes/todo.txt")
        if st.button("📖 Read Back from StoreBackend (Thread 2)", key="btn_store_read"):
            with st.spinner("Reading back file from StoreBackend on Thread 2..."):
                try:
                    store_agent, _ = create_configured_agent(
                        provider=selected_provider,
                        model_name=selected_model,
                        backend_type=BackendType.STORE,
                        backend_manager=st.session_state.backend_manager,
                        checkpointer=st.session_state.checkpointer,
                        api_key=effective_api_key,
                    )
                    t2_id = f"thread-demo-2-{uuid.uuid4().hex[:6]}"
                    cfg2 = {"configurable": {"thread_id": t2_id}}
                    p2 = f"Read {read_path_input} back to me verbatim."
                    r2 = store_agent.invoke({"messages": [{"role": "user", "content": p2}]}, config=cfg2)
                    st.success("🎉 Cross-thread persistence confirmed! Read back on Thread 2:")
                    st.code(extract_text(r2["messages"][-1].content), language="markdown")
                except Exception as e:
                    st.error(f"Store read error: {e}")


# =============================================================================
# TAB 3: Context Engineering & Persistent Memory Hub (AGENTS.md)
# =============================================================================
with tab_memory:
    st.markdown("### 🧠 Context Engineering & Persistent Memory (`AGENTS.md`)")
    st.markdown(
        "As explained in **Notebook 4** and `deepagentsdemo/projects/AGENTS.md`, "
        "Deep Agents use `MemoryMiddleware` to inject persistent workspace context, architecture guidelines, "
        "and operational conventions directly into `<agent_memory>` tags in the system prompt."
    )

    mem_stats = st.session_state.memory_manager.get_memory_stats()
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Memory File", DEFAULT_MEMORY_FILE)
    col_m2.metric("Status", "Found & Loaded" if mem_stats["exists"] else "Missing")
    col_m3.metric("Size", f"{mem_stats['size_bytes']} bytes ({mem_stats['lines']} lines)")

    st.markdown("---")

    col_edit1, col_edit2 = st.columns([3, 2])
    with col_edit1:
        st.markdown("#### 📝 Live `AGENTS.md` Memory Editor")
        current_mem_text = st.session_state.memory_manager.read_memory()
        edited_mem = st.text_area(
            "Edit AGENTS.md directly",
            value=current_mem_text,
            height=450,
            key="agents_md_editor",
        )
        if st.button("💾 Save Changes to AGENTS.md", type="primary"):
            ok = st.session_state.memory_manager.write_memory(edited_mem)
            if ok:
                st.success("Successfully updated AGENTS.md! Future agent turns will reflect new memory rules.")
            else:
                st.error("Failed to write to AGENTS.md.")

    with col_edit2:
        st.markdown("#### 📋 Memory Update Protocol")
        st.markdown(
            """
            > **From AGENTS.md Section 6:**
            - **Do update memory**:
              - When user specifies lasting project conventions, coding standards, or domain rules.
              - When new reusable tools, workflows, or subagent profiles are added.
              - When resolving tricky bugs with specific architectural patterns.
            - **Do NOT update memory**:
              - For transient info (*"I will be back in 10 minutes"*).
              - For secrets, tokens, or API credentials.
            - **Autonomous Updates**:
              - The DeepAgent can autonomously update memory during execution using its `edit_file` or `write_file` tools!
            """
        )
        st.markdown("#### 👁️ Active System Prompt Preview")
        st.info(active_system_prompt)


# =============================================================================
# TAB 4: Domain Skills Catalog
# =============================================================================
with tab_skills:
    st.markdown("### 📚 Domain Skills Catalog (`deepagentsdemo/skills`)")
    st.markdown(
        "Deep Agents dynamically load domain skills to ground their reasoning and tool usage. "
        "Each skill includes frontmatter (`SKILL.md`), specific rules (`instructions.md`), and reference implementations (`examples.md`)."
    )

    skill_names = st.session_state.skills_catalog.get_skill_names()
    if not skill_names:
        st.warning("No skills discovered in `deepagentsdemo/skills`.")
    else:
        chosen_skill = st.selectbox("Select Skill to Inspect", options=skill_names, index=0)
        skill_obj = st.session_state.skills_catalog.get_skill(chosen_skill)

        if skill_obj:
            st.markdown(f"#### 📖 Skill: `{skill_obj.name}` (v{skill_obj.version})")
            st.markdown(f"*{skill_obj.description}*")
            if skill_obj.tags:
                tag_badges = " ".join([f"`{t}`" for t in skill_obj.tags])
                st.markdown(f"**Tags:** {tag_badges}")

            st.markdown("---")
            skill_sub_tabs = st.tabs(["📄 SKILL.md", "📋 instructions.md", "💡 examples.md"])
            with skill_sub_tabs[0]:
                st.markdown(skill_obj.skill_md if skill_obj.skill_md else "*No SKILL.md found.*")
            with skill_sub_tabs[1]:
                st.markdown(skill_obj.instructions_md if skill_obj.instructions_md else "*No instructions.md found.*")
            with skill_sub_tabs[2]:
                st.markdown(skill_obj.examples_md if skill_obj.examples_md else "*No examples.md found.*")


# =============================================================================
# TAB 5: Files & Notes Explorer (Live Workspace)
# =============================================================================
with tab_files:
    st.markdown("### 📁 Files & Notes Workspace Explorer")
    st.markdown(
        "Inspect notes created by the agent (such as `deepagentsdemo/notes/todo.txt` from Notebook 3), "
        "read disk files, or create new notes."
    )

    notes_dir = "deepagentsdemo/notes"
    os.makedirs(notes_dir, exist_ok=True)
    notes_files = [f for f in os.listdir(notes_dir) if not f.startswith(".")]

    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        st.markdown("#### 📂 Notes in `deepagentsdemo/notes/`")
        if not notes_files:
            st.caption("No notes currently in folder.")
        for nf in notes_files:
            p = os.path.join(notes_dir, nf)
            sz = os.path.getsize(p)
            st.markdown(f"- 📄 **{nf}** ({sz} bytes)")

        st.markdown("---")
        st.markdown("#### ➕ Create New Note")
        new_note_name = st.text_input("Note Filename", value="agent_summary.txt")
        new_note_body = st.text_area("Note Content", value="DeepAgent multi-step execution notes.", height=120)
        if st.button("Create Note"):
            target_path = os.path.join(notes_dir, new_note_name)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(new_note_body)
            st.success(f"Created {target_path}")
            st.rerun()

    with col_f2:
        st.markdown("#### 🔍 File Viewer")
        if notes_files:
            selected_note_view = st.selectbox("Select file to view", options=notes_files)
            full_path = os.path.join(notes_dir, selected_note_view)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    file_text = f.read()
                st.code(file_text, language="markdown")
            except Exception as e:
                st.error(f"Error reading file: {e}")
        else:
            st.info("Create a note or have the DeepAgent write `/deepagentsdemo/notes/todo.txt`.")


# =============================================================================
# TAB 6: Architecture & Inspector
# =============================================================================
with tab_arch:
    st.markdown("### ⚙️ DeepAgent Architecture & Graph Inspector")
    st.markdown(
        """
        Deep Agents is a modular framework built on **LangGraph** with a multi-layered middleware architecture:
        """
    )

    st.code(
        """
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
        """,
        language="text",
    )

    st.markdown("---")
    col_a1, col_a2 = st.columns(2)

    with col_a1:
        st.markdown("#### 🛠️ Active Tools in DeepAgent")
        if agent and hasattr(agent, "nodes") and "tools" in agent.nodes:
            t_node = agent.nodes["tools"]
            tools_list = list(getattr(t_node.bound, "tools_by_name", {}).keys())
            for t in tools_list:
                st.markdown(f"- 🔧 `{t}`")
        else:
            st.caption("Tools node information available once agent compiles.")

    with col_a2:
        st.markdown("#### 🤖 Configured Subagents Swarm")
        if enable_subagents:
            sub_dict = {
                "research_specialist": "Performs deep web research & source verification via Tavily",
                "math_specialist": "Calculates math equations, arithmetic & evaluation",
                "python_specialist": "Writes and refactors modern Python code & tests",
                "langgraph_specialist": "Designs LangGraph StateGraphs and cyclic workflows",
            }
            for s_name, s_role in sub_dict.items():
                is_active = subagents_config.get(s_name.split("_")[0], False)
                status_icon = "🟢" if is_active else "⚪"
                st.markdown(f"- {status_icon} **`{s_name}`**: *{s_role}*")
        else:
            st.caption("Subagents are currently disabled in sidebar.")
