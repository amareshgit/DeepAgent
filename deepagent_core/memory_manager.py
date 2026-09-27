"""Memory Manager for DeepAgent

Handles persistent project memory as described in:
- deepagentsdemo/projects/AGENTS.md
- 4.contextengineering.ipynb

Provides capabilities to view, edit, inspect, and supply memory paths
to create_deep_agent(memory=[...]).
"""
import os
from pathlib import Path
from typing import List, Optional, Dict, Any


DEFAULT_MEMORY_FILE = "deepagentsdemo/projects/AGENTS.md"


class MemoryManager:
    def __init__(self, primary_memory_path: str = DEFAULT_MEMORY_FILE):
        self.primary_memory_path = primary_memory_path

    def get_primary_path(self) -> str:
        return self.primary_memory_path

    def memory_exists(self) -> bool:
        return os.path.exists(self.primary_memory_path)

    def read_memory(self, path: Optional[str] = None) -> str:
        target = path or self.primary_memory_path
        if not os.path.exists(target):
            return f"Memory file not found at: {target}"
        try:
            with open(target, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as exc:
            return f"Error reading memory file: {exc}"

    def write_memory(self, content: str, path: Optional[str] = None) -> bool:
        target = path or self.primary_memory_path
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception:
            return False

    def get_memory_stats(self, path: Optional[str] = None) -> Dict[str, Any]:
        target = path or self.primary_memory_path
        if not os.path.exists(target):
            return {"exists": False, "size_bytes": 0, "lines": 0, "path": target}
        try:
            size = os.path.getsize(target)
            with open(target, "r", encoding="utf-8") as f:
                lines = len(f.readlines())
            return {
                "exists": True,
                "size_bytes": size,
                "lines": lines,
                "path": target,
            }
        except Exception:
            return {"exists": False, "size_bytes": 0, "lines": 0, "path": target}
