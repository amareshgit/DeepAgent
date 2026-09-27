# Python Skill — Production Examples

This document provides ready-to-use, production-grade patterns demonstrating the Python directives.

---

## Example 1: Concurrent Asynchronous Task Pipeline with TaskGroup

Demonstrates structured concurrency (`asyncio.TaskGroup`), rate limiting with `asyncio.Semaphore`, timeouts, and graceful error aggregation.

```python
"""Concurrent processing pipeline demonstrating modern Python async patterns."""

import asyncio
import logging
from dataclasses import dataclass
from typing import Final

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MAX_CONCURRENT_WORKERS: Final[int] = 3
TIMEOUT_SECONDS: Final[float] = 5.0


@dataclass(frozen=True, slots=True)
class WorkItem:
    item_id: str
    payload: str


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    item_id: str
    success: bool
    data: str | None = None
    error: str | None = None


class WorkPipeline:
    def __init__(self, concurrency_limit: int = MAX_CONCURRENT_WORKERS) -> None:
        self._semaphore = asyncio.Semaphore(concurrency_limit)

    async def _execute_single(self, item: WorkItem) -> ProcessingResult:
        async with self._semaphore:
            logger.info("Starting processing item: %s", item.item_id)
            try:
                # Simulate async network/compute work with timeout
                async with asyncio.timeout(TIMEOUT_SECONDS):
                    await asyncio.sleep(0.5)  # non-blocking wait
                    if "bad" in item.payload.lower():
                        raise ValueError(f"Invalid item content in {item.item_id}")
                    return ProcessingResult(
                        item_id=item.item_id,
                        success=True,
                        data=f"Transformed: {item.payload.upper()}",
                    )
            except TimeoutError:
                logger.error("Processing timed out for %s", item.item_id)
                return ProcessingResult(item_id=item.item_id, success=False, error="Timeout")
            except Exception as exc:
                logger.exception("Unexpected error processing %s: %s", item.item_id, exc)
                return ProcessingResult(item_id=item.item_id, success=False, error=str(exc))

    async def run(self, items: list[WorkItem]) -> list[ProcessingResult]:
        results: list[ProcessingResult] = []
        # Structured concurrency guarantees all tasks complete or cancel cleanly
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(self._execute_single(item)) for item in items]

        for t in tasks:
            results.append(t.result())
        return results


# Usage Demonstration
async def main() -> None:
    work_items = [
        WorkItem("job-1", "dataset alpha"),
        WorkItem("job-2", "dataset bad payload"),
        WorkItem("job-3", "dataset gamma"),
    ]
    pipeline = WorkPipeline(concurrency_limit=2)
    results = await pipeline.run(work_items)
    for res in results:
        print(f"[{res.item_id}] Success={res.success} | Data={res.data} | Error={res.error}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Example 2: Pydantic v2 Data Validation with Discriminated Unions

Demonstrates clean domain modeling, field validators, computed fields, and discriminated unions.

```python
"""Pydantic v2 data models for enterprise API payloads."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    event_id: str = Field(..., min_length=4, max_length=64, description="Unique event UUID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FileUploadEvent(BaseEvent):
    event_type: Literal["file_upload"] = "file_upload"
    filename: str = Field(..., min_length=1)
    file_size_bytes: int = Field(..., gt=0, le=500_000_000)  # Max 500MB

    @field_validator("filename")
    @classmethod
    def validate_extension(cls, value: str) -> str:
        allowed = {".csv", ".parquet", ".json", ".pdf"}
        if not any(value.lower().endswith(ext) for ext in allowed):
            raise ValueError(f"File must have one of following extensions: {allowed}")
        return value

    @computed_field
    @property
    def size_mb(self) -> float:
        return round(self.file_size_bytes / (1024 * 1024), 2)


class AlertTriggerEvent(BaseEvent):
    event_type: Literal["alert_trigger"] = "alert_trigger"
    severity: Priority
    message: str = Field(..., min_length=5, max_length=500)


# Discriminated Union for polymorphic deserialization
AnyAppEvent = Annotated[
    Union[FileUploadEvent, AlertTriggerEvent],
    Field(discriminator="event_type"),
]


# Usage Demonstration
if __name__ == "__main__":
    raw_payload = {
        "event_type": "file_upload",
        "event_id": "evt-90123",
        "filename": "quarterly_report.parquet",
        "file_size_bytes": 10_485_760,
    }
    # Adapts correctly to FileUploadEvent based on event_type tag
    event = AnyAppEvent.model_validate(raw_payload)
    print(f"Loaded: {type(event).__name__}")
    print(f"File: {event.filename}, Size MB: {event.size_mb}")
```

---

## Example 3: Context Manager for Safe Resource Lifecycle

Demonstrates both generator-based (`@contextmanager`) and class-based (`__enter__` / `__exit__`) context management with automatic rollback on exception.

```python
"""Deterministic resource management and atomic execution context."""

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
import tempfile


@contextmanager
def temporary_working_dir(prefix: str = "agent_run_") -> Generator[Path, None, None]:
    """Create an isolated temporary directory and guarantee cleanup on exit."""
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield temp_dir
    finally:
        # Recursively delete files and folder
        if temp_dir.exists():
            for child in sorted(temp_dir.glob("**/*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            temp_dir.rmdir()


# Class-based atomic file writer (prevents partially written files)
class AtomicFileWriter:
    def __init__(self, target_path: Path, encoding: str = "utf-8") -> None:
        self._target_path = target_path
        self._encoding = encoding
        self._temp_path = target_path.with_suffix(f"{target_path.suffix}.tmp")
        self._file_handle = None

    def __enter__(self):
        self._file_handle = self._temp_path.open("w", encoding=self._encoding)
        return self._file_handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_handle:
            self._file_handle.close()
        if exc_type is not None:
            # An error occurred; clean up the temp file without touching target
            if self._temp_path.exists():
                self._temp_path.unlink()
            return False  # Propagate exception
        # Success: atomically rename temp file to target
        self._temp_path.replace(self._target_path)
        return True
```

---

## Example 4: Parameterized Unit Testing Suite with Pytest

Demonstrates clean, deterministic tests with mock fixtures and error validation.

```python
"""Pytest suite demonstrating fixtures, parameterization, and mocking."""

import pytest
from unittest.mock import MagicMock


def calculate_discount(price: float, rate: float) -> float:
    if price < 0 or rate < 0 or rate > 1:
        raise ValueError("Invalid price or discount rate")
    return round(price * (1.0 - rate), 2)


@pytest.fixture
def mock_audit_logger():
    mock = MagicMock()
    mock.log_transaction.return_value = True
    return mock


@pytest.mark.parametrize(
    ("price", "rate", "expected"),
    [
        (100.0, 0.1, 90.0),
        (50.0, 0.0, 50.0),
        (200.0, 0.25, 150.0),
        (99.99, 0.5, 50.0),
    ],
)
def test_calculate_discount_valid(price: float, rate: float, expected: float) -> None:
    assert calculate_discount(price, rate) == expected


@pytest.mark.parametrize(
    ("price", "rate"),
    [
        (-10.0, 0.1),
        (100.0, -0.05),
        (100.0, 1.25),
    ],
)
def test_calculate_discount_invalid_raises_value_error(price: float, rate: float) -> None:
    with pytest.raises(ValueError, match="Invalid price or discount rate"):
        calculate_discount(price, rate)
```
