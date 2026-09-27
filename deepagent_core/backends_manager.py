"""Backends Manager for DeepAgent

Implements all 3 storage and execution backends explained in Notebook 3 (3.backends.ipynb):
1. FilesystemBackend: Local disk workspace operations, virtual mode
2. StoreBackend: Cross-thread persistent file storage backed by InMemoryStore
3. StateBackend: In-memory ephemeral execution state
"""
from enum import Enum
from typing import Tuple, Any, Optional, Dict
from deepagents.backends import FilesystemBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore


class BackendType(str, Enum):
    FILESYSTEM = "FilesystemBackend (Local Disk / Workspace)"
    STORE = "StoreBackend (LangGraph InMemoryStore / Cross-Thread)"
    STATE = "StateBackend (Ephemeral State)"


class BackendManager:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = workspace_root
        self.in_memory_store = InMemoryStore()

    def get_backend(
        self,
        backend_type: BackendType,
        custom_root: Optional[str] = None,
    ) -> Tuple[Any, Optional[InMemoryStore]]:
        """Instantiate backend and return (backend_instance, store_instance).

        When StoreBackend is used, store must also be passed to create_deep_agent.
        """
        root = custom_root or self.workspace_root

        if backend_type == BackendType.FILESYSTEM:
            backend = FilesystemBackend(root_dir=root, virtual_mode=True)
            return backend, None

        elif backend_type == BackendType.STORE:
            # Matches Notebook 3: static namespace for local dev
            backend = StoreBackend(
                namespace=lambda rt: ("demo-user",),
            )
            return backend, self.in_memory_store

        elif backend_type == BackendType.STATE:
            backend = StateBackend()
            return backend, None

        else:
            backend = FilesystemBackend(root_dir=root, virtual_mode=True)
            return backend, None

    def reset_store(self):
        """Clears the in-memory store."""
        self.in_memory_store = InMemoryStore()
