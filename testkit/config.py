"""配置模型与读写"""
import os
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel


class RepoConfig(BaseModel):
    url: str
    type: str  # skill | agent | script | knowledge | template | project


class Config(BaseModel):
    workspace: Path = Path.home() / ".testkit" / "ecosystem"
    repos: dict[str, RepoConfig] = {}
    sources: dict = {}
    hooks: dict = {}

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        return cls(**data)

    def to_file(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.safe_dump(self.model_dump(), f, default_flow_style=False, allow_unicode=True)


DEFAULT_CONFIG = Config(
    repos={
        "skills":    RepoConfig(url="https://github.com/Huanannan93/test-skills.git",    type="skill"),
        "agents":    RepoConfig(url="https://github.com/Huanannan93/test-agents.git",    type="agent"),
        "scripts":   RepoConfig(url="https://github.com/Huanannan93/test-scripts.git",   type="script"),
        "knowledge": RepoConfig(url="https://github.com/Huanannan93/test-knowledge.git", type="knowledge"),
        "templates": RepoConfig(url="https://github.com/Huanannan93/test-templates.git", type="template"),
        "projects":  RepoConfig(url="https://github.com/Huanannan93/test-projects.git",  type="project"),
    }
)


def config_path() -> Path:
    return Path.home() / ".testkit" / "config.yml"


CONFIG_PATH = config_path()
