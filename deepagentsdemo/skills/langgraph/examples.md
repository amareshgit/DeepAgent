# LangGraph Skill — Production Examples

This document provides complete, tested patterns for building robust stateful workflows with LangGraph.

---

## Example 1: Robust ReAct Tool-Calling Agent from Scratch

Demonstrates `StateGraph`, `Annotated[list, add_messages]`, dynamic tool binding, and safe loop routing.

```python
"""Complete ReAct Agent implemented with LangGraph StateGraph."""

from typing import Annotated, Literal
from typing_extensions import TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


# 1. Tool Definitions
@tool
def search_docs(query: str) -> str:
    """Search project documentation for a given topic."""
    # Simulated search result
    knowledge = {
        "memory": "MemoryMiddleware loads AGENTS.md directly into system prompt tags.",
        "backends": "FilesystemBackend maps agent file operations to disk root_dir.",
    }
    for key, val in knowledge.items():
        if key in query.lower():
            return f"Found documentation: {val}"
    return "No direct documentation match found."


tools = [search_docs]
tools_by_name = {t.name: t for t in tools}

# 2. State Definition
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# 3. Node Functions
def call_model(state: AgentState) -> dict[str, list[AnyMessage]]:
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)
    response = model.invoke(state["messages"])
    return {"messages": [response]}


def execute_tools(state: AgentState) -> dict[str, list[AnyMessage]]:
    last_msg = state["messages"][-1]
    tool_outputs: list[AnyMessage] = []

    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        for call in last_msg.tool_calls:
            t = tools_by_name.get(call["name"])
            try:
                if t is None:
                    raise KeyError(f"Tool {call['name']} not found")
                output = t.invoke(call["args"])
                tool_outputs.append(
                    ToolMessage(content=str(output), tool_call_id=call["id"])
                )
            except Exception as err:
                tool_outputs.append(
                    ToolMessage(
                        content=f"Error executing tool: {err}",
                        tool_call_id=call["id"],
                        status="error",
                    )
                )
    return {"messages": tool_outputs}


# 4. Routing Predicate
def should_continue(state: AgentState) -> Literal["tools", "end"]:
    last_msg = state["messages"][-1]
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return "tools"
    return "end"


# 5. Graph Assembly
builder = StateGraph(AgentState)
builder.add_node("agent", call_model)
builder.add_node("tools", execute_tools)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
builder.add_edge("tools", "agent")

checkpointer = MemorySaver()
app = builder.compile(checkpointer=checkpointer)

# Execution
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread-react-1"}, "recursion_limit": 10}
    response = app.invoke(
        {"messages": [HumanMessage(content="How does memory work in Deep Agents?")]},
        config=config,
    )
    print("Final Agent Answer:")
    print(response["messages"][-1].content)
```

---

## Example 2: Multi-Agent Supervisor Pattern

Demonstrates hierarchical routing where a central supervisor analyzes progress and delegates work to specialized subagent nodes.

```python
"""Multi-agent supervisor pattern using LangGraph."""

from typing import Annotated, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


# Routing Decision Schema
class RouterSchema(BaseModel):
    next_worker: Literal["researcher", "coder", "FINISH"] = Field(
        description="The next worker to execute or FINISH if the user request is satisfied."
    )
    task_instructions: str = Field(
        description="Specific instructions for the delegated worker."
    )


class MultiAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    next_worker: str
    delegated_task: str


# Supervisor Node
def supervisor_node(state: MultiAgentState) -> dict[str, str]:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(RouterSchema)

    system_prompt = (
        "You are the supervisor coordinating a researcher and a coder. "
        "Review the conversation history and select the next worker or FINISH."
    )
    prompt = [("system", system_prompt)] + list(state["messages"])
    decision = structured_llm.invoke(prompt)

    return {
        "next_worker": decision.next_worker,
        "delegated_task": decision.task_instructions,
    }


# Worker 1: Researcher
def researcher_node(state: MultiAgentState) -> dict[str, list[AnyMessage]]:
    task = state["delegated_task"]
    # Simulated researcher output
    report = f"[Researcher]: Found architecture specifications for: {task}."
    return {"messages": [HumanMessage(content=report, name="researcher")]}


# Worker 2: Coder
def coder_node(state: MultiAgentState) -> dict[str, list[AnyMessage]]:
    task = state["delegated_task"]
    # Simulated coder output
    code = f"[Coder]: Implemented clean solution for: {task}."
    return {"messages": [HumanMessage(content=code, name="coder")]}


# Routing Condition
def route_next(state: MultiAgentState) -> str:
    if state["next_worker"] == "FINISH":
        return END
    return state["next_worker"]


# Graph Assembly
graph_builder = StateGraph(MultiAgentState)
graph_builder.add_node("supervisor", supervisor_node)
graph_builder.add_node("researcher", researcher_node)
graph_builder.add_node("coder", coder_node)

graph_builder.add_edge(START, "supervisor")
graph_builder.add_conditional_edges(
    "supervisor",
    route_next,
    {"researcher": "researcher", "coder": "coder", END: END},
)
# Workers always report back to supervisor
graph_builder.add_edge("researcher", "supervisor")
graph_builder.add_edge("coder", "supervisor")

orchestrator = graph_builder.compile()
```

---

## Example 3: Human-in-the-Loop with `interrupt()` and Resume

Demonstrates pausing graph execution for sensitive tool approval (e.g. database schema change or AWS resource deletion) and resuming state safely.

```python
"""Human-in-the-Loop graph with dynamic interrupt() and state resumption."""

from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class DeploymentState(TypedDict):
    target_environment: str
    action: str
    approved: bool | None
    execution_status: str


def plan_deployment(state: DeploymentState) -> dict[str, str]:
    return {"action": f"Deploying build v2.4 to {state['target_environment']}"}


def human_approval_gate(state: DeploymentState) -> dict[str, bool]:
    # Pauses the graph and exposes details to the caller
    human_response = interrupt({
        "question": f"Approval required to execute: {state['action']}",
        "environment": state["target_environment"],
    })
    # Resumed via Command(resume={"approved": True/False})
    is_approved = bool(human_response.get("approved", False))
    return {"approved": is_approved}


def execute_or_cancel(state: DeploymentState) -> dict[str, str]:
    if state.get("approved"):
        return {"execution_status": "SUCCESS: Deployment completed successfully."}
    return {"execution_status": "CANCELLED: Human operator rejected the deployment."}


builder = StateGraph(DeploymentState)
builder.add_node("plan", plan_deployment)
builder.add_node("approval_gate", human_approval_gate)
builder.add_node("executor", execute_or_cancel)

builder.add_edge(START, "plan")
builder.add_edge("plan", "approval_gate")
builder.add_edge("approval_gate", "executor")
builder.add_edge("executor", END)

checkpointer = MemorySaver()
app = builder.compile(checkpointer=checkpointer)

# Demonstration of Pause & Resume Flow
if __name__ == "__main__":
    thread_config = {"configurable": {"thread_id": "deploy-prod-001"}}

    # 1. Run until human gate (interrupt fires)
    print("--- Step 1: Initiating Deployment ---")
    state_step_1 = app.invoke({"target_environment": "production"}, config=thread_config)
    
    # Check interrupt payload
    current_snapshot = app.get_state(thread_config)
    print("Graph paused at:", current_snapshot.next)
    print("Interrupt payload:", current_snapshot.tasks[0].interrupts[0].value)

    # 2. Resume execution with human approval
    print("\n--- Step 2: Operator Approves Deployment ---")
    state_step_2 = app.invoke(
        Command(resume={"approved": True}),
        config=thread_config,
    )
    print("Result:", state_step_2["execution_status"])
```
