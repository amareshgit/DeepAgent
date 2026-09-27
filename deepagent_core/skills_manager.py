"""Skills Manager for DeepAgent

Discovers, parses, and provides access to domain skills in deepagentsdemo/skills:
- python: Modern Python 3.11-3.13, typing, async, Pydantic, testing
- langgraph: StateGraph, cyclic flows, multi-agent supervisors, checkpointers
- aws: Boto3, Lambda, DynamoDB, Bedrock, IAM, CDK
- technical-writing: Diátaxis framework, ADRs, documentation standards
"""
import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class SkillInfo:
    def __init__(
        self,
        name: str,
        path: str,
        description: str = "",
        version: str = "1.0.0",
        tags: Optional[List[str]] = None,
        skill_md: str = "",
        instructions_md: str = "",
        examples_md: str = "",
    ):
        self.name = name
        self.path = path
        self.description = description
        self.version = version
        self.tags = tags or []
        self.skill_md = skill_md
        self.instructions_md = instructions_md
        self.examples_md = examples_md

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "version": self.version,
            "tags": self.tags,
            "has_skill_md": bool(self.skill_md),
            "has_instructions": bool(self.instructions_md),
            "has_examples": bool(self.examples_md),
        }


class SkillsCatalog:
    def __init__(self, base_skills_dir: str = "deepagentsdemo/skills"):
        self.base_skills_dir = base_skills_dir
        self.skills: Dict[str, SkillInfo] = {}
        self.reload()

    def reload(self):
        """Scan skills directory and parse all available skill definitions."""
        self.skills.clear()
        if not os.path.exists(self.base_skills_dir):
            return

        for item in sorted(os.listdir(self.base_skills_dir)):
            item_path = os.path.join(self.base_skills_dir, item)
            if not os.path.isdir(item_path):
                continue

            skill_md_path = os.path.join(item_path, "SKILL.md")
            inst_path = os.path.join(item_path, "instructions.md")
            ex_path = os.path.join(item_path, "examples.md")

            skill_md_content = ""
            instructions_content = ""
            examples_content = ""
            desc = ""
            version = "1.0.0"
            tags = []
            name = item

            if os.path.exists(skill_md_path):
                try:
                    with open(skill_md_path, "r", encoding="utf-8") as f:
                        skill_md_content = f.read()

                    # Parse YAML frontmatter if present
                    if skill_md_content.startswith("---"):
                        parts = skill_md_content.split("---", 2)
                        if len(parts) >= 3:
                            fm_text = parts[1]
                            parsed_fm = yaml.safe_load(fm_text) or {}
                            name = parsed_fm.get("name", item)
                            desc = parsed_fm.get("description", "")
                            version = parsed_fm.get("version", "1.0.0")
                            tags = parsed_fm.get("tags", [])
                except Exception:
                    pass

            if os.path.exists(inst_path):
                try:
                    with open(inst_path, "r", encoding="utf-8") as f:
                        instructions_content = f.read()
                except Exception:
                    pass

            if os.path.exists(ex_path):
                try:
                    with open(ex_path, "r", encoding="utf-8") as f:
                        examples_content = f.read()
                except Exception:
                    pass

            self.skills[name] = SkillInfo(
                name=name,
                path=item_path,
                description=desc or f"Skill for {name}",
                version=str(version),
                tags=tags,
                skill_md=skill_md_content,
                instructions_md=instructions_content,
                examples_md=examples_content,
            )

    def get_skill_names(self) -> List[str]:
        return list(self.skills.keys())

    def get_skill(self, name: str) -> Optional[SkillInfo]:
        return self.skills.get(name)

    def get_skill_paths(self, selected_names: Optional[List[str]] = None) -> List[str]:
        """Return the POSIX paths for selected skills, or all if None."""
        if selected_names is None:
            return [skill.path for skill in self.skills.values()]
        return [self.skills[name].path for name in selected_names if name in self.skills]
