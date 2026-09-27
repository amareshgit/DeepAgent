---
name: python
description: Expert Python engineering skill for modern Python (3.10-3.13+), type hinting, clean architecture, async programming, idiomatic design patterns, testing with pytest, and performance optimization.
version: 1.0.0
tags:
  - python
  - typing
  - asyncio
  - pydantic
  - pytest
  - clean-code
  - performance
---

# Python Skill

## Purpose & Scope
This skill equips the **Deep Agent** with production-grade Python engineering expertise. It provides the behavioral principles, coding conventions, architectural heuristics, and concrete patterns necessary to write robust, maintainable, high-performance, and idiomatic Python code.

Whenever a user task involves writing new Python code, reviewing or refactoring existing modules, resolving complex bugs, writing asynchronous routines, structuring packages, or authoring comprehensive test suites, this skill governs the agent's output.

---

## Core Capabilities

1. **Modern Idiomatic Syntax**:
   - Modern syntax features (Python 3.10 through 3.13+): structural pattern matching (`match/case`), union syntax (`X | Y`), exception groups (`except*`), positional-only parameters, and walrus operator (`:=`).
   - Standard library modernizations: `pathlib.Path`, `dataclasses`, `enum.StrEnum`, `zoneinfo`.

2. **Strict Typing & Data Validation**:
   - Type annotations across all function signatures, class attributes, and complex collections using `typing` and standard generics (PEP 585/604).
   - Domain modeling and serialization using **Pydantic v2** (`BaseModel`, `Field`, `model_validator`, `field_validator`, `TypeAdapter`).
   - Protocols (`typing.Protocol`) for structural subtyping and decoupling implementations from interfaces.

3. **Concurrency & Asynchronous I/O**:
   - Structured concurrency with `asyncio.TaskGroup` (Python 3.11+).
   - Non-blocking I/O patterns, async context managers, async iterators, and graceful cancellation.
   - Offloading CPU-bound tasks to `concurrent.futures.ProcessPoolExecutor` and blocking I/O to `asyncio.to_thread`.

4. **Resilient Error Handling & Resource Management**:
   - Explicit custom exception hierarchies deriving from `Exception`.
   - Exception chaining (`raise CustomError(...) from err`) preserving original tracebacks.
   - Deterministic resource cleanup with context managers (`@contextmanager`, `__enter__`/`__exit__`, `contextlib.AsyncExitStack`).

5. **Testing & Quality Assurance**:
   - Comprehensive unit and integration testing with **pytest**.
   - Parameterized testing (`@pytest.mark.parametrize`), scoped fixtures (`fixture(scope=...)`), monkeypatching, and `pytest-asyncio`.
   - Linting, formatting, and typing alignment with `ruff` and `mypy`.

---

## When to Use This Skill (Triggers)

Activate this skill when the user query involves:
- Writing or refactoring Python scripts, modules, or backend services.
- Designing data models, request/response validation, or config parsing with Pydantic.
- Debugging Python runtime issues, memory leaks, event loop deadlocks, or exception handling.
- Developing asynchronous pipelines, API clients, or background task queues.
- Authoring unit or integration tests using `pytest`.
- Configuring packaging, virtual environments, dependencies, or modern tooling (`uv`, `pyproject.toml`).

---

## Associated References
- Detailed directives: [`instructions.md`](./instructions.md)
- Production code examples: [`examples.md`](./examples.md)
