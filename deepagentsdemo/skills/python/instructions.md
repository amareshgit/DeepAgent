# Python Skill — Agent Instructions & Guidelines

When acting as a Python engineer or generating Python code, adhere strictly to the following architectural, syntactical, and quality standards.

---

## 1. Syntax & Language Version Baseline

1. **Target Python 3.10+ (Prefer 3.11–3.13)**:
   - Use `int | str` instead of `Union[int, str]`.
   - Use `list[str]`, `dict[str, int]`, `set[Path]` instead of importing `List`, `Dict`, `Set` from `typing`.
   - Use `Path.read_text(encoding="utf-8")` and `Path.write_text(..., encoding="utf-8")` rather than raw `open(...)` calls for simple file operations.
2. **Type Annotations**:
   - Every public function and method MUST have complete argument and return type annotations.
   - For functions that return nothing, use `-> None`.
   - Use `typing.Self` for methods returning instances of their class (builders, fluent interfaces).
   - Use `collections.abc.Sequence`, `collections.abc.Mapping`, or `collections.abc.Iterable` for function arguments to allow maximum caller flexibility, but return concrete types (`list`, `dict`).
3. **Data Modeling**:
   - For simple immutable data bags without validation: Use `@dataclass(frozen=True, slots=True)`.
   - For domain models requiring validation, serialization, coercion, or schema generation: Use **Pydantic v2** (`pydantic.BaseModel`).
   - Use `StrEnum` or `IntEnum` for distinct categorical values.

---

## 2. Asynchronous Programming Guidelines

1. **Structured Concurrency**:
   - Prefer `asyncio.TaskGroup` (Python 3.11+) over `asyncio.gather()` whenever managing groups of tasks. If one fails, the remaining tasks are automatically cancelled, preventing dangling operations.
   - Set timeouts with `asyncio.timeout(seconds)` context manager rather than `asyncio.wait_for`.
2. **Never Block the Event Loop**:
   - Never call `time.sleep()`, synchronous `requests.get()`, or long CPU loops inside async routines.
   - Wrap legacy blocking I/O calls in `await asyncio.to_thread(blocking_function, *args, **kwargs)`.
3. **Resource Lifecycle**:
   - Always close sessions, connections, and pools inside `async with` blocks or `try...finally`.

---

## 3. Error Handling & Defense-in-Depth

1. **Specific Catching**:
   - Never use bare `except:` or catch generic `Exception` unless you are at the outermost boundaries of an application (e.g., top-level CLI or server worker loop) and re-logging with full traceback.
2. **Exception Chaining**:
   - When catching an internal library exception and translating it into a domain-specific error, always use `raise MyDomainError("Contextual message") from err`.
3. **Custom Exceptions**:
   - Define a domain base exception:
     ```python
     class DomainError(Exception):
         """Base exception for the application domain."""

     class ResourceNotFoundError(DomainError):
         """Raised when an entity is missing."""
     ```

---

## 4. Code Organization & Clean Architecture

1. **Separation of Concerns**:
   - Keep data access, business domain logic, and presentation/CLI/API layers cleanly separated.
   - Favor dependency injection over global variables or hardcoded singletons.
2. **Protocols & Interfaces**:
   - Define behavior using `typing.Protocol` to keep code loosely coupled and easily testable without monkeypatching concrete classes.
3. **Documentation**:
   - Follow Google-style or PEP 257 docstrings for all non-trivial functions and classes:
     ```python
     def process_payload(data: dict[str, Any], *, dry_run: bool = False) -> Result:
         """Process and validate incoming event payload.

         Args:
             data: Raw dictionary received from incoming webhook.
             dry_run: When True, performs validation without mutating state.

         Returns:
             Result object containing status and computed metrics.

         Raises:
             ValidationError: If payload schema fails validation.
         """
     ```

---

## 5. Testing Discipline with pytest

1. **Pytest Idioms**:
   - Use plain `assert` statements; never use `unittest.TestCase` assertions (`self.assertEqual`).
   - Isolate test state using fixtures with explicit scopes (`@pytest.fixture`).
   - Parameterize test variations using `@pytest.mark.parametrize`.
2. **Mocking**:
   - Mock external network calls, file system mutations, and cloud services using `unittest.mock.patch` or `monkeypatch`.
   - Prefer verifying side-effects over fragile implementation detail assertions.

---

## 6. Output Checklist for the Deep Agent

Before outputting Python code to the user:
- [ ] Is Python version targeted to modern standards (PEP 585/604)?
- [ ] Are all functions fully type-annotated?
- [ ] Are file operations explicitly specifying `encoding="utf-8"`?
- [ ] Are exceptions handled gracefully with proper chaining?
- [ ] Is asynchronous code free of event-loop blocking operations?
- [ ] Are resources managed deterministically with context managers?
- [ ] Is a corresponding test or usage example provided?
