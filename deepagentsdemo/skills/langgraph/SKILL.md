---
name: langgraph
description: State graph orchestration skill for building reliable agentic workflows, multi-agent systems, human-in-the-loop cycles, memory checkpointers, and cyclic control flows using LangGraph.
version: 1.0.0
tags:
  - langgraph
  - agents
  - stategraph
  - multi-agent
  - checkpointing
  - hitl
  - streaming
---

# LangGraph Skill

## Purpose & Scope
This skill provides the **Deep Agent** with deep expertise in designing, building, debugging, and optimizing stateful, cyclic agent workflows using **LangGraph**.

Unlike simple sequential chains or DAGs, LangGraph enables cyclical execution graphs, fine-grained state management with reducer functions, long-term persistence across threads, human-in-the-loop approvals, and multi-agent coordination. When a user is building autonomous agents, multi-turn reasoning loops, or complex tool-use supervisors, this skill provides the definitive guidance.

---

## Core Capabilities

1. **StateGraph Architecture & Schema Modeling**:
   - Defining typed state structures with `TypedDict` or Pydantic `BaseModel`.
   - Managing state channels with reducers (e.g., `Annotated[list[AnyMessage], add_messages]`, custom update dictionaries, or overwriting channels).
   - Clean separation of input schemas, internal state, and output schemas.

2. **Graph Topology & Control Flow**:
   - Nodes as discrete, testable Python functions returning partial state updates.
   - Deterministic and conditional edges (`add_edge`, `add_conditional_edges`) with clear routing predicates.
   - Special control flow tokens: `START`, `END`, and self-referential cycles (loops).
   - Loop guardrails: recursion limits (`recursion_limit`) and cycle circuit breakers.

3. **Multi-Agent Systems & Coordination**:
   - **Supervisor / Hierarchical Pattern**: Orchestrator node determines which worker agent handles the task and synthesizes outcomes.
   - **Network / Collaboration Pattern**: Agents communicate by publishing messages to a shared conversation channel.
   - **Subgraphs**: Encapsulating isolated child graphs within a parent graph to keep state channels modular.

4. **Persistence & Time Travel**:
   - Attaching checkpointers (`MemorySaver`, `SqliteSaver`, `PostgresSaver`).
   - Thread isolation (`configurable: {"thread_id": "..."}`) for persistent multi-turn conversations.
   - State history inspection (`get_state`, `get_state_history`) and time-travel rollbacks/edits (`update_state`).

5. **Human-in-the-Loop (HITL)**:
   - Dynamic interrupts using the modern `interrupt()` function.
   - Static breakpoint triggers (`interrupt_before`, `interrupt_after`).
   - Resuming graph execution with human review feedback via `Command(resume=...)`.

6. **Streaming & Observability**:
   - Streaming intermediate node states via `graph.stream()`, `stream_mode="values"`, `"updates"`, or `"messages"`.
   - Native integration with LangSmith for distributed trace inspection.

---

## When to Use This Skill (Triggers)

Activate this skill when the user query involves:
- Designing or implementing a `StateGraph`, `MessageGraph`, or custom agent loop.
- Implementing a ReAct agent, tool-calling loop, or self-correcting code generation agent.
- Structuring multi-agent architectures (supervisor, worker teams, agent delegation).
- Adding persistence, cross-session memory, checkpointers (`MemorySaver`, `SqliteSaver`).
- Integrating Human-in-the-Loop (HITL) approval steps or state rewinds.
- Debugging infinite recursion, state channel race conditions, or graph compilation errors.

---

## Associated References
- Detailed directives: [`instructions.md`](./instructions.md)
- Production graph examples: [`examples.md`](./examples.md)
