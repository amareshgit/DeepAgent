# LangGraph Skill — Agent Instructions & Guidelines

When architecting, writing, or debugging graphs in **LangGraph**, adhere strictly to the following engineering directives and best practices.

---

## 1. Graph State Design & Reducers

1. **Explicit Typing**:
   - Always define graph state as a `typing.TypedDict` or Pydantic `BaseModel`.
   - If using `add_messages` to append chat turns, always annotate the channel:
     ```python
     from typing import Annotated
     from typing_extensions import TypedDict
     from langchain_core.messages import AnyMessage
     from langgraph.graph.message import add_messages

     class AgentState(TypedDict):
         messages: Annotated[list[AnyMessage], add_messages]
         current_step: int
         final_output: str | None
     ```
2. **Channel Reducer Semantics**:
   - Understand the difference between default overwriting and annotated reducers:
     - **Default (no reducer)**: Returning `{"field": new_value}` replaces the old value completely.
     - **Annotated reducer (e.g. `add_messages` or `operator.add`)**: Returning `{"messages": [new_msg]}` merges or appends according to the reducer logic (and deduplicates messages by ID).
3. **Immutability & Partial Updates**:
   - Nodes must return a dictionary containing **only the keys being updated**.
   - Do NOT mutate the incoming `state` dict directly in-place. Always return a new dictionary with modified values.

---

## 2. Node Function Design

1. **Single Responsibility**:
   - Each node should perform one logical task (e.g., calling the model, executing a batch of tools, formatting an artifact, validating output).
2. **Deterministic Inputs/Outputs**:
   - Nodes receive `(state: AgentState, config: RunnableConfig | None = None)` and return `dict[str, Any]` or `Command`.
3. **Error Containment**:
   - Tool execution nodes should catch tool execution failures and write the error message back into a `ToolMessage(content="Error: ...", status="error")` instead of letting an unhandled exception abort the entire graph.

---

## 3. Edge Routing & Cyclic Flow Control

1. **Explicit Routing Functions**:
   - Use `add_conditional_edges(source_node, routing_func, path_map)` where `path_map` maps possible return strings to target nodes or `END`:
     ```python
     def should_continue(state: AgentState) -> Literal["tools", "end"]:
         last_message = state["messages"][-1]
         if last_message.tool_calls:
             return "tools"
         return "end"

     builder.add_conditional_edges(
         "agent",
         should_continue,
         {"tools": "tools", "end": END}
     )
     ```
2. **Recursion Guardrails**:
   - When invoking or compiling graphs with cycles, always set a recursion limit:
     ```python
     app = builder.compile(checkpointer=checkpointer)
     app.invoke(input_data, config={"recursion_limit": 25})
     ```
   - Track iteration count inside the state to prevent infinite tool loops when models repeat identical failing arguments.

---

## 4. Multi-Agent Topologies

1. **Supervisor vs Swarm**:
   - **Supervisor**: A central router LLM evaluates current progress and delegates to specialized worker nodes (`researcher`, `coder`, `reviewer`). Each worker finishes its subtask and routes back to the supervisor.
   - **Subgraphs**: When a worker has its own internal iterative loop, encapsulate it as a compiled subgraph node in the parent graph. This keeps the parent state clean and avoids namespace collisions.
2. **Handoff Protocols**:
   - Standardize handoff messages using clear prompt instructions or tool calls (`transfer_to_coder(task=...)`).

---

## 5. Persistence, Threads & Human-in-the-Loop (HITL)

1. **Thread Identification**:
   - Always supply `{"configurable": {"thread_id": "<unique_id>"}}` when persistent checkpointers are used.
2. **Modern `interrupt()` Pattern**:
   - When human approval or input is required, use LangGraph's dynamic `interrupt()` inside the node:
     ```python
     from langgraph.types import interrupt

     def human_approval_node(state: AgentState) -> dict[str, Any]:
         approval = interrupt({
             "question": "Do you approve deleting the database?",
             "details": state["pending_action"]
         })
         if not approval.get("approved"):
             return {"status": "rejected"}
         return {"status": "approved"}
     ```
   - Resume using `app.invoke(Command(resume={"approved": True}), config=config)`.

---

## 6. Output Checklist for the Deep Agent

Before delivering LangGraph code to the user:
- [ ] Are state channels explicitly typed with appropriate reducers?
- [ ] Do nodes return partial update dicts without mutating state in-place?
- [ ] Are conditional edge return values mapped via path dictionaries or typed literals?
- [ ] Is there an explicit termination condition reaching `END`?
- [ ] Are recursion limits and tool error handling in place?
- [ ] If persistence is required, is a checkpointer attached and `thread_id` configured?
