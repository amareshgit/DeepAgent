# Deep Agent Skills Catalog

This directory contains specialized, modular skill packs designed to be loaded by **Deep Agents** either statically (via memory/context configuration) or dynamically on-demand during task planning and execution.

Each skill follows a standard three-file architecture:
1. **`SKILL.md`**: Defines the skill's identity, metadata, purpose, core capabilities, activation triggers, and cross-references.
2. **`instructions.md`**: Provides deep behavioral guidelines, engineering directives, design patterns, anti-patterns, and quality benchmarks for the agent.
3. **`examples.md`**: Contains comprehensive, production-ready code implementations, configurations, and reference patterns that the agent can draw from when answering or generating solutions.

---

## Available Skills

| Skill | Directory | Primary Capabilities | Triggers & Keywords |
|---|---|---|---|
| **Python** | [`python/`](./python/) | Modern Python (3.10-3.13+), typing, async/await, Pydantic v2, clean architecture, pytest | `python`, `asyncio`, `typing`, `pydantic`, `pytest`, `pep8`, `concurrency` |
| **LangGraph** | [`langgraph/`](./langgraph/) | StateGraph design, cyclic agent workflows, checkpointing, multi-agent supervisors, HITL | `langgraph`, `stategraph`, `agent`, `workflow`, `checkpoint`, `interrupt`, `supervisor` |
| **AWS** | [`aws/`](./aws/) | Cloud architecture, Boto3 SDK, Serverless (Lambda, API Gateway), DynamoDB, S3, Bedrock AI, CDK | `aws`, `boto3`, `lambda`, `s3`, `dynamodb`, `bedrock`, `iam`, `cdk`, `cloud` |
| **Technical Writing** | [`technical-writing/`](./technical-writing/) | Technical documentation, Diátaxis framework, ADRs, API docs, system guides, READMEs | `documentation`, `technical writing`, `readme`, `adr`, `api docs`, `guide`, `rfc` |

---

## Skill Directory Structure

```text
skills/
├── README.md                          # This catalog
├── python/
│   ├── SKILL.md                       # Identity, capabilities & triggers
│   ├── instructions.md                # Agent execution instructions & standards
│   └── examples.md                    # Working code patterns & pytest suites
├── langgraph/
│   ├── SKILL.md                       # Graph architecture & lifecycle
│   ├── instructions.md                # StateGraph rules, reducers & HITL protocol
│   └── examples.md                    # ReAct, multi-agent & checkpointing implementations
├── aws/
│   ├── SKILL.md                       # Cloud services & security boundaries
│   ├── instructions.md                # Boto3 patterns, least privilege & Bedrock rules
│   └── examples.md                    # Lambda powertools, Boto3 client, Bedrock Converse, CDK
└── technical-writing/
    ├── SKILL.md                       # Documentation taxonomy & objectives
    ├── instructions.md                # Diátaxis framework, tone & structuring rules
    └── examples.md                    # Production README, ADR, API guide, and tutorial
```

---

## How Deep Agents Load & Use Skills

### 1. Preloading via Memory
When initializing a specialized agent session, pass the target skill files directly into the `memory` parameter:

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

backend = FilesystemBackend(root_dir=".", virtual_mode=True)

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

### 2. On-Demand Dynamic Retrieval
When operating with full workspace access, a Deep Agent should:
1. Identify when a user request aligns with a specific domain (e.g., AWS deployment, LangGraph cyclic graph design, Python refactoring, or writing an ADR).
2. Read the appropriate `skills/<skill_name>/SKILL.md` to confirm scope and guidelines.
3. Consult `instructions.md` and `examples.md` before generating code or architecture documents to ensure strict adherence to workspace standards.
